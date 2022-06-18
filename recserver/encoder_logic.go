package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"math"
	"os"
	"strconv"
	"strings"
	"sync"

	"github.com/DataIntelligenceCrew/go-faiss"
	"github.com/bluele/gcache"
	"gonum.org/v1/gonum/mat"
)

func (schema Schema) read_partitioned_csv(filename string, variants []Variant) (map[int][]Record, ItemLookup, error) {
	header, data, err := read_csv(filename)
	if err != nil {
		return nil, ItemLookup{}, err
	}
	id_num := index_of(header, schema.IdCol)
	if id_num == -1 {
		return nil, ItemLookup{}, errors.New("id column not found")
	}

	label2id := make(map[string]int)
	label2partition := make(map[string]int)
	partition2records := make(map[int][]Record)
	for _, variant := range variants {
		for _, row := range data {
			vid := variant.Name + "~" + row[id_num]
			id, found := label2id[vid]
			if !found {
				id = len(label2id)
				label2id[vid] = id
			}
			query := zip(header, row)

			partition_idx := schema.partition_number(query, variant.Name)
			label2partition[vid] = partition_idx
			partition2records[partition_idx] = append(partition2records[partition_idx], Record{
				Label:     row[id_num],
				Id:        id,
				Values:    row,
				Fields:    header,
				Partition: partition_idx,
			})
		}

	}
	id2label := make([]string, len(label2id))
	for lbl, id := range label2id {
		id2label[id] = lbl
	}
	// Build lookups
	item_lookup := ItemLookup{
		label2id:        label2id,
		id2label:        id2label,
		label2partition: label2partition,
	}
	item_lookup.id2label = id2label
	return partition2records, item_lookup, nil
}

func (schema Schema) index_partitions(records map[int][]Record) {
	os.Mkdir("indices", os.ModePerm)
	var wg sync.WaitGroup
	for partition_idx, partitioned_records := range records {
		if len(partitioned_records) < 10 {
			continue
		}
		if _, err := os.Stat(fmt.Sprintf("indices/%d", partition_idx)); !os.IsNotExist(err) {
			continue
		}

		wg.Add(1)
		go func(partition_idx int, partitioned_records []Record) {
			defer wg.Done()
			var faiss_index faiss.Index
			// https://github.com/facebookresearch/faiss/wiki/The-index-factory
			index_factory := schema.IndexFactory
			if schema.IndexFactory == "" { //auto compute
				n_clusters := 128
				if len(partitioned_records) < n_clusters {
					n_clusters = len(partitioned_records)
				}
				index_factory = fmt.Sprintf("IVF%d,Flat", n_clusters)
			}
			if strings.ToLower(schema.Metric) == "ip" {
				faiss_index, _ = faiss.IndexFactory(schema.Dim, index_factory, faiss.MetricInnerProduct)
			}
			if strings.ToLower(schema.Metric) == "l2" {
				faiss_index, _ = faiss.IndexFactory(schema.Dim, index_factory, faiss.MetricL2)
			}
			if strings.ToLower(schema.Metric) == "l1" {
				faiss_index, _ = faiss.IndexFactory(schema.Dim, index_factory, faiss.MetricL1)
			}
			xb := make([]float32, schema.Dim*len(partitioned_records))
			ids := make([]int64, len(partitioned_records))
			for i, record := range partitioned_records {
				encoded := schema.encode(zip(record.Fields, record.Values))
				for j, v := range encoded {
					xb[i*schema.Dim+j] = v
					ids[i] = int64(record.Id)
				}
			}
			// fmt.Printf("Start-%d\n", partition_idx)
			faiss_index.Train(xb)
			faiss_index.AddWithIDs(xb, ids)
			faiss_index.Train(xb)
			faiss.WriteIndex(faiss_index, fmt.Sprintf("indices/%d", partition_idx))
			faiss_index.Delete()
			// fmt.Printf("Done-%d\n", partition_idx)

		}(partition_idx, partitioned_records)
	}
	wg.Wait()
}

func (schema Schema) pull_item_data(variants []Variant) (map[int][]Record, ItemLookup, error) {
	var item_lookup ItemLookup
	var partitioned_records map[int][]Record
	var err error
	found_item_source := false
	for _, src := range schema.Sources {
		if strings.ToLower(src.Record) == "items" {
			if src.Type == "csv" {
				partitioned_records, item_lookup, err = schema.read_partitioned_csv(src.Path, variants)
				if err != nil {
					return nil, ItemLookup{}, err
				}
				found_item_source = true
			}
		}
	}
	if !found_item_source {
		return nil, ItemLookup{}, errors.New("no item source found")
	}
	return partitioned_records, item_lookup, err
}

func (schema Schema) pull_user_data() (map[string][]string, error) {
	var user_data map[string][]string
	var err error
	found_user_source := false
	for _, src := range schema.Sources {
		if strings.ToLower(src.Record) == "users" {
			if src.Type == "csv" {
				user_data, err = schema.read_user_csv(src.Path, src.Query)
				if err != nil {
					return nil, err
				}
				found_user_source = true
			}
		}
	}
	if !found_user_source {
		return nil, errors.New("no user source found")
	}
	return user_data, err
}

func (schema Schema) read_user_csv(filename string, history_col string) (map[string][]string, error) {

	header, data, err := read_csv(filename)
	if err != nil {
		fmt.Println(err.Error())
	}
	id_num := index_of(header, schema.IdCol)
	if id_num == -1 {
		return nil, errors.New("id column not found")
	}

	history_num := index_of(header, history_col)
	if id_num == -1 {
		return nil, errors.New("history column not found")
	}

	user_data := make(map[string][]string)
	for _, row := range data {
		user_id := row[id_num]
		user_data[user_id] = strings.Split(row[history_num], ",")
	}

	return user_data, nil
}

func read_schema(schema_file string, variants_file string) (Schema, []Variant, error) {
	schema_json_file, err := os.Open(schema_file)
	if err != nil {
		fmt.Println(err)
		return Schema{}, nil, err
	}
	defer schema_json_file.Close()
	schema_byte_value, _ := ioutil.ReadAll(schema_json_file)
	var schema Schema
	json.Unmarshal(schema_byte_value, &schema)

	variants_json_file, err := os.Open(variants_file)
	var variants []Variant
	if err == nil {
		defer variants_json_file.Close()
		variants_byte_value, _ := ioutil.ReadAll(variants_json_file)
		json.Unmarshal(variants_byte_value, &variants)
	} else {
		fmt.Println("Variant file not found, using default 100 percent split")
		variants := make([]Variant, 1)
		variants[0] = Variant{
			Name:       "",
			Percentage: 100,
			Weights:    make(map[string]float64),
		}
	}

	if schema.WeightOverride == nil {
		schema.WeightOverride = make([]WeightOverride, 0)
	}
	variants_vals := make([]string, len(variants))
	for i, variant := range variants {
		variants_vals[i] = variant.Name
	}
	variant_filter := make([]Filter, 1)
	variant_filter[0] = Filter{
		Field:   "variant",
		Default: "",
		Values:  variants_vals,
	}
	schema.Filters = append(variant_filter, schema.Filters...)

	embeddings := make(map[string]*mat.Dense)
	dim := 0
	for i := 0; i < len(schema.Encoders); i++ {
		encoder_type := strings.ToLower(schema.Encoders[i].Type)
		if contains([]string{"np", "numpy", "npy"}, encoder_type) {
			embeddings[schema.Encoders[i].Field] = read_npy(schema.Encoders[i].Npy)
			_, emb_size := embeddings[schema.Encoders[i].Field].Dims()
			dim += emb_size
		}
		if contains([]string{"numeric", "num", "scalar"}, encoder_type) {
			dim += 1
		}
	}
	schema.Dim = dim
	schema.Embeddings = embeddings

	//Add weight overloading
	varianted_weights := make([]WeightOverride, 0)
	for _, variant := range variants {
		for encoder_field, encoder_weight := range variant.Weights {
			varianted_weights = append(varianted_weights, WeightOverride{
				FilterField:   "variant",
				FilterValue:   variant.Name,
				EncoderField:  encoder_field,
				EncoderWeight: encoder_weight,
			})
		}
	}
	schema.WeightOverride = append(schema.WeightOverride, varianted_weights...)

	values := make([][]string, len(schema.Filters))
	for i := 0; i < len(schema.Filters); i++ {
		values[i] = schema.Filters[i].Values
	}
	partitions := itertools_product(values...)

	schema.Partitions = partitions

	partition_map := make(map[string]int)
	for i := 0; i < len(partitions); i++ {
		key := strings.Join(partitions[i], "~")
		partition_map[key] = i
	}
	schema.PartitionMap = partition_map
	return schema, variants, nil
}

func (schema Schema) encode(query map[string]string) []float32 {
	encoded := make([]float64, 0)
	encoder_weights := make([]float64, len(schema.Encoders))
	for i := 0; i < len(schema.Encoders); i++ {
		encoder_weights[i] = schema.Encoders[i].Weight
	}
	// Concatenate all components to a single vector
	for i := 0; i < len(schema.Encoders); i++ {
		var raw_vector []float64
		encoder_type := strings.ToLower(schema.Encoders[i].Type)
		val, found := query[schema.Encoders[i].Field]
		if !found {
			val = schema.Encoders[i].Default
		}
		// Override weight if specified
		for j := 0; j < len(schema.Filters); j++ {
			for _, weight_override := range schema.WeightOverride {
				if weight_override.EncoderField == schema.Encoders[i].Field && weight_override.FilterField == schema.Filters[j].Field && weight_override.FilterValue == query[schema.Filters[j].Field] {
					encoder_weights[i] = weight_override.EncoderWeight
				}
			}
		}
		if contains([]string{"numeric", "num", "scalar"}, encoder_type) {
			fval, err := strconv.ParseFloat(val, 64)
			if err != nil {
				fval = 0
			}
			raw_vector = []float64{fval * encoder_weights[i]}
		} else {
			emb_matrix := schema.Embeddings[schema.Encoders[i].Field]
			row_index := index_of(schema.Encoders[i].Values, val)
			if row_index == -1 { // not found, use default
				row_index = index_of(schema.Encoders[i].Values, schema.Encoders[i].Default)
			}
			_, emb_size := emb_matrix.Dims()
			raw_vector = make([]float64, emb_size)
			if row_index > -1 {
				raw_vector = mat.Row(nil, row_index, emb_matrix)
				for j := 0; j < emb_size; j++ {
					raw_vector[j] *= encoder_weights[i]
				}
			}
		}
		encoded = append(encoded, raw_vector...)
	}
	// Convert to float32
	encoded32 := make([]float32, len(encoded))
	for i, f64 := range encoded {
		encoded32[i] = float32(f64)
	}

	return encoded32
}

func (schema Schema) partition_number(query map[string]string, variant string) int {

	filters := make([]string, len(schema.Filters))
	for i := 1; i < len(schema.Filters); i++ {
		val, found := query[schema.Filters[i].Field]
		if !found {
			val = schema.Filters[i].Default
		}
		filters[i] = val
	}
	filters[0] = variant
	partition_key := strings.Join(filters, "~")
	partition_idx := schema.PartitionMap[partition_key]
	return partition_idx
}

func (schema Schema) componentwise_distance(v1 []float32, v2 []float32) (float32, map[string]float32) {
	breakdown := make(map[string]float32)
	var total_distance float32
	total_distance = 0
	offset := 0
	for _, encoder := range schema.Encoders {
		if contains([]string{"np", "numpy", "npy"}, strings.ToLower(encoder.Type)) {
			emb_matrix := schema.Embeddings[encoder.Field]
			_, emb_size := emb_matrix.Dims()
			breakdown[encoder.Field] = 0
			for i := 0; i < emb_size; i++ {
				if strings.ToLower(schema.Metric) == "l1" {
					if v1[offset+i] > v2[offset+i] {
						breakdown[encoder.Field] += (v1[offset+i] - v2[offset+i])
					} else {
						breakdown[encoder.Field] += (v2[offset+i] - v1[offset+i])
					}
				}
				if strings.ToLower(schema.Metric) == "l2" {
					breakdown[encoder.Field] += (v1[offset+i] - v2[offset+i]) * (v1[offset+i] - v2[offset+i])
				}
				//TODO: Support InnerProduct
				total_distance += breakdown[encoder.Field]
			}
			if strings.ToLower(schema.Metric) == "l2" {
				breakdown[encoder.Field] = float32(math.Sqrt(float64(breakdown[encoder.Field])))
			}
			breakdown[encoder.Field] /= float32(emb_size)
			offset += emb_size
		} else { //numeric field
			if v1[offset] > v2[offset] {
				breakdown[encoder.Field] += (v1[offset] - v2[offset])
			} else {
				breakdown[encoder.Field] += (v2[offset] - v1[offset])
			}
			offset += 1
		}

	}
	if strings.ToLower(schema.Metric) == "l2" {
		total_distance = float32(math.Sqrt(float64(total_distance)))
	}
	total_distance /= float32(schema.Dim)
	return total_distance, breakdown
}

func (schema Schema) reconstruct(partitioned_records map[int][]Record, id int64, partition_idx int) []float32 {
	var reconstructed []float32
	reconstructed = nil
	//TODO: Have a more intelligent way of looking up the original record (currently, linear search)
	for _, record := range partitioned_records[partition_idx] {
		if record.Id == int(id) {
			reconstructed = schema.encode(zip(record.Fields, record.Values))
			break
		}
	}
	return reconstructed
}

func faiss_index_from_cache(cache gcache.Cache, index int) faiss.Index {
	faiss_interface, _ := cache.Get(index)
	return faiss_interface.(faiss.Index)
}

func random_variant(variants []Variant) string {
	weights := make([]float64, len(variants))
	names := make([]string, len(variants))
	for i := 0; i < len(variants); i++ {
		weights[i] = variants[i].Percentage
		names[i] = variants[i].Name
	}
	retval := random_by_weights(names, weights)
	if retval == "default" {
		return ""
	}
	return retval
}
