package main

import (
	"encoding/csv"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"os"
	"strconv"
	"strings"
	"sync"

	"github.com/DataIntelligenceCrew/go-faiss"
	"github.com/bluele/gcache"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/template/html"
	"gonum.org/v1/gonum/mat"
)

type Schema struct {
	IdCol        string    `json:"id_col"`
	Metric       string    `json:"metric"`
	IndexFactory string    `json:"index_factory"`
	Filters      []Filter  `json:"filters"`
	Encoders     []Encoder `json:"encoders"`
	Sources      []Source  `json:"sources"`
	Dim          int       `json:"dim"`
	Embeddings   map[string]*mat.Dense
	Partitions   [][]string
	PartitionMap map[string]int
}

type Filter struct {
	Field   string   `json:"field"`
	Values  []string `json:"values"`
	Default string   `json:"default"`
}

type Encoder struct {
	Field   string   `json:"field"`
	Values  []string `json:"values"`
	Default string   `json:"default"`
	Type    string   `json:"type"`
	Npy     string   `json:"npy"`
	Weight  float64  `json:"weight"`
}

type Source struct {
	Record string `json:"record"`
	Type   string `json:"type"`
	Path   string `json:"path"`
	Query  string `json:"query"`
}

type Explanation struct {
	Label     string             `json:"label"`
	Distance  float32            `json:"distance"`
	Breakdown map[string]float32 `json:"breakdown"`
}

type ItemLookup struct {
	id2label        []string
	label2id        map[string]int
	label2partition map[string]int
}

type Record struct {
	Id        int
	Label     string
	Partition int
	Values    map[string]string
}

type PartitionMeta struct {
	Name    []string `json:"name"`
	Count   int      `json:"count"`
	Trained bool     `json:"trained"`
}

func read_index_labels(in_file string) []string {
	jsonFile, err := os.Open(in_file)
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)

	var index_labels []string

	json.Unmarshal(byteValue, &index_labels)
	return index_labels
}

func (schema Schema) encode(query map[string]string) []float32 {
	encoded := make([]float64, 0)
	// Concatenate all components to a single vector
	for i := 0; i < len(schema.Encoders); i++ {
		var raw_vector []float64
		encoder_type := strings.ToLower(schema.Encoders[i].Type)
		val, found := query[schema.Encoders[i].Field]
		if !found {
			val = schema.Encoders[i].Default
		}
		if contains([]string{"numeric", "num", "scalar"}, encoder_type) {
			fval, err := strconv.ParseFloat(val, 64)
			if err != nil {
				fval = 0
			}
			raw_vector = []float64{fval * schema.Encoders[i].Weight}
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
					raw_vector[j] *= schema.Encoders[i].Weight
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

func (schema Schema) partition_number(query map[string]string) int {

	filters := make([]string, len(schema.Filters))
	for i := 0; i < len(schema.Filters); i++ {
		val, found := query[schema.Filters[i].Field]
		if !found {
			val = schema.Filters[i].Default
		}
		filters[i] = val
	}
	partition_key := strings.Join(filters, "~")
	partition_idx := schema.PartitionMap[partition_key]
	return partition_idx
}

func (schema Schema) componentwise_distance(v1 []float32, v2 []float32) (float32, map[string]float32) {
	breakdown := make(map[string]float32)
	var total_distance float32
	total_distance = 0
	vector_size := 0
	for field, emb_matrix := range schema.Embeddings {
		_, emb_size := emb_matrix.Dims()
		breakdown[field] = 0
		for i := 0; i < emb_size; i++ {
			if strings.ToLower(schema.Metric) == "l1" {
				if v1[i] > v2[i] {
					breakdown[field] += (v1[i] - v2[i])
				} else {
					breakdown[field] += (v2[i] - v1[i])
				}
			}
			if strings.ToLower(schema.Metric) == "l2" {
				breakdown[field] += (v1[i] - v2[i]) * (v1[i] - v2[i])
			}
			//TODO: Support InnerProduct
			total_distance += breakdown[field]
		}
		if strings.ToLower(schema.Metric) == "l2" {
			breakdown[field] = float32(math.Sqrt(float64(breakdown[field])))
		}
		breakdown[field] /= float32(emb_size)
		vector_size += emb_size

	}
	if strings.ToLower(schema.Metric) == "l2" {
		total_distance = float32(math.Sqrt(float64(total_distance)))
	}
	total_distance /= float32(vector_size)
	return total_distance, breakdown
}

func (schema Schema) reconstruct(partitioned_records map[int][]Record, id int64, partition_idx int) []float32 {
	var reconstructed []float32
	reconstructed = nil
	//TODO: Have a more intelligent way of looking up the original record (currently, linear search)
	for _, record := range partitioned_records[partition_idx] {
		if record.Id == int(id) {
			reconstructed = schema.encode(record.Values)
			break
		}
	}
	return reconstructed
}

func faiss_index_from_cache(cache gcache.Cache, index int) faiss.Index {
	faiss_interface, _ := cache.Get(index)
	return faiss_interface.(faiss.Index)
}

func start_server(schema Schema, partitioned_records map[int][]Record, indices gcache.Cache, item_lookup ItemLookup) {
	app := fiber.New(fiber.Config{
		Views: html.New("./views", ".html"),
	})

	var faiss_index faiss.Index
	// GET /api/register
	app.Get("/npy/*", func(c *fiber.Ctx) error {
		m := read_npy(c.Params("*") + ".npy")
		msg := fmt.Sprintf("data = %v\n", mat.Formatted(m, mat.Prefix("       ")))
		return c.SendString(msg)
	})

	app.Get("/partitions", func(c *fiber.Ctx) error {
		ret := make([]PartitionMeta, len(schema.Partitions))
		for i, partition := range schema.Partitions {
			ret[i].Name = partition
			//TODO: fix
			// ret[i].Count = int(indices[i].Ntotal())
			// ret[i].Trained = indices[i].IsTrained()
		}
		return c.JSON(ret)
	})

	app.Get("/labels", func(c *fiber.Ctx) error {
		return c.JSON(item_lookup.id2label)
	})

	app.Get("/reload_items", func(c *fiber.Ctx) error {
		partitioned_records, item_lookup, _ = schema.pull_item_data()
		os.RemoveAll("indices")
		schema.index_partitions(partitioned_records)
		return c.SendString("{\"Status\": \"OK\"}")
	})

	app.Get("/reload_users", func(c *fiber.Ctx) error {
		//TODO: Reload users
		return c.SendString("{\"Status\": \"OK\"}")
	})

	app.Post("/encode", func(c *fiber.Ctx) error {
		var query map[string]string
		json.Unmarshal(c.Body(), &query)
		encoded := schema.encode(query)
		return c.JSON(encoded)
	})

	app.Post("/query/:k?", func(c *fiber.Ctx) error {
		var query map[string]string
		json.Unmarshal(c.Body(), &query)

		encoded := schema.encode(query)
		partition_idx := schema.partition_number(query)
		k, err := strconv.Atoi(c.Params("k"))
		if err != nil {
			k = 2
		}
		//TODO: Resolve code duplication (1)
		faiss_index = faiss_index_from_cache(indices, partition_idx)
		distances, ids, err := faiss_index.Search(encoded, int64(k))
		if err != nil {
			log.Fatal(err)
		}
		retrieved := make([]Explanation, 0)
		for i, id := range ids {
			if id == -1 {
				continue
			}
			next_result := Explanation{
				Label:    item_lookup.id2label[int(id)],
				Distance: distances[i],
			}
			if partitioned_records != nil {
				reconstructed := schema.reconstruct(partitioned_records, id, partition_idx)
				if reconstructed != nil {
					total_distance, breakdown := schema.componentwise_distance(encoded, reconstructed)
					next_result.Distance = total_distance
					next_result.Breakdown = breakdown
				}
			}
			retrieved = append(retrieved, next_result)
		}
		return c.JSON(retrieved)
	})

	app.Post("/item_query", func(c *fiber.Ctx) error {
		payload := struct {
			K       string            `json:"k"`
			ItemId  string            `json:"id"`
			Filters map[string]string `json:"filters"`
		}{}

		if err := c.BodyParser(&payload); err != nil {
			return err
		}
		k, err := strconv.Atoi(payload.K)
		if err != nil {
			k = 2
		}
		id := int64(item_lookup.label2id[payload.ItemId])
		partition_idx := schema.partition_number(payload.Filters)
		encoded := schema.reconstruct(partitioned_records, id, partition_idx)
		if encoded == nil {
			return c.SendString("{\"Status\": \"Not Found\"}")
		}
		//TODO: Resolve code duplication (2)
		faiss_index = faiss_index_from_cache(indices, partition_idx)
		distances, ids, err := faiss_index.Search(encoded, int64(k))
		if err != nil {
			log.Fatal(err)
		}
		retrieved := make([]Explanation, 0)
		for i, id := range ids {
			if id == -1 {
				continue
			}
			next_result := Explanation{
				Label:    item_lookup.id2label[int(id)],
				Distance: distances[i],
			}
			if partitioned_records != nil {
				reconstructed := schema.reconstruct(partitioned_records, id, partition_idx)
				if reconstructed != nil {
					total_distance, breakdown := schema.componentwise_distance(encoded, reconstructed)
					next_result.Distance = total_distance
					next_result.Breakdown = breakdown
				}
			}
			retrieved = append(retrieved, next_result)
		}
		return c.JSON(retrieved)
	})

	app.Post("/user_query/:k?", func(c *fiber.Ctx) error {
		payload := struct {
			K       string            `json:"k"`
			UserId  string            `json:"id"`
			History []string          `json:"history"`
			Filters map[string]string `json:"filters"`
		}{}

		if err := c.BodyParser(&payload); err != nil {
			return err
		}
		partition_idx := schema.partition_number(payload.Filters)
		k, err := strconv.Atoi(payload.K)
		if err != nil {
			k = 2
		}
		item_vecs := make([][]float32, 1)
		item_vecs[0] = make([]float32, schema.Dim) // zero_vector
		for _, item_id := range payload.History {
			id := int64(item_lookup.label2id[item_id])
			if id == -1 {
				continue
			}
			reconstructed := schema.reconstruct(partitioned_records, id, partition_idx)
			if reconstructed == nil {
				continue
			}
			item_vecs = append(item_vecs, reconstructed)
		}
		//TODO: Account for cold start
		user_vec := make([]float32, schema.Dim)
		for _, item_vec := range item_vecs {
			for i := range user_vec {
				user_vec[i] += item_vec[i] / float32(len(item_vecs))
			}
		}

		//TODO: Resolve code duplication (3)
		faiss_index = faiss_index_from_cache(indices, partition_idx)
		distances, ids, err := faiss_index.Search(user_vec, int64(k))
		if err != nil {
			log.Fatal(err)
		}
		retrieved := make([]Explanation, 0)
		for i, id := range ids {
			if id == -1 {
				continue
			}
			next_result := Explanation{
				Label:    item_lookup.id2label[int(id)],
				Distance: distances[i],
			}
			if partitioned_records != nil {
				reconstructed := schema.reconstruct(partitioned_records, id, partition_idx)
				if reconstructed != nil {
					total_distance, breakdown := schema.componentwise_distance(user_vec, reconstructed)
					next_result.Distance = total_distance
					next_result.Breakdown = breakdown
				}
			}
			retrieved = append(retrieved, next_result)
		}
		return c.JSON(retrieved)
	})

	app.Get("/", func(c *fiber.Ctx) error {
		fields := make([]string, 0)
		filters := make([]string, 0)
		for _, e := range schema.Filters {
			fields = append(fields, e.Field)
			filters = append(filters, e.Field)
		}
		for _, e := range schema.Encoders {
			fields = append(fields, e.Field)
		}
		return c.Render("index", fiber.Map{
			"Headline": "Recsplain API",
			"Fields":   fields,
			"Filters":  filters,
		})
	})

	log.Fatal(app.Listen(":3000"))
}

func (schema Schema) read_partitioned_csv(filename string) (map[int][]Record, ItemLookup, error) {

	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	// reader.Comma = '\t'
	reader.FieldsPerRecord = -1
	raw_data, err := reader.ReadAll()
	if err != nil {
		return nil, ItemLookup{}, err
	}

	header := raw_data[0]
	id_num := index_of(header, schema.IdCol)
	if id_num == -1 {
		return nil, ItemLookup{}, errors.New("id column not found")
	}
	data := raw_data[1:]

	label2id := make(map[string]int)
	label2partition := make(map[string]int)
	partition2records := make(map[int][]Record)
	for _, row := range data {
		id, found := label2id[row[id_num]]
		if !found {
			id = len(label2id)
			label2id[row[id_num]] = id
		}
		query := zip(header, row)
		partition_idx := schema.partition_number(query)
		label2partition[row[id_num]] = partition_idx
		partition2records[partition_idx] = append(partition2records[partition_idx], Record{
			Label:     row[id_num],
			Id:        id,
			Values:    query,
			Partition: partition_idx,
		})

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
	// os.Mkdir("partitions", os.ModePerm)
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
			// partition_dir := fmt.Sprintf("partitions/%d", i)
			// os.Mkdir(partition_dir, os.ModePerm)
			defer wg.Done()
			// index_type := "IDMap,LSH"
			// index_type := "IDMap,ITQ,LSHt"
			// n_clusters := 128
			// if len(recs) < n_clusters {
			// 	n_clusters = len(recs)
			// }
			var faiss_index faiss.Index
			// https://github.com/facebookresearch/faiss/wiki/The-index-factory
			// index_type := fmt.Sprintf("IVF%d,Flat", n_clusters)
			if strings.ToLower(schema.Metric) == "ip" {
				faiss_index, _ = faiss.IndexFactory(schema.Dim, schema.IndexFactory, faiss.MetricInnerProduct)
			}
			if strings.ToLower(schema.Metric) == "l2" {
				faiss_index, _ = faiss.IndexFactory(schema.Dim, schema.IndexFactory, faiss.MetricL2)
			}
			if strings.ToLower(schema.Metric) == "l1" {
				faiss_index, _ = faiss.IndexFactory(schema.Dim, schema.IndexFactory, faiss.MetricL1)
			}
			xb := make([]float32, schema.Dim*len(partitioned_records))
			ids := make([]int64, len(partitioned_records))
			for i, record := range partitioned_records {
				encoded := schema.encode(record.Values)
				// go write_npy(fmt.Sprintf("%s/%d", partition_dir, record.Id), encoded)
				for j, v := range encoded {
					xb[i*schema.Dim+j] = v
					ids[i] = int64(record.Id)
				}
			}
			faiss_index.Train(xb)
			faiss_index.AddWithIDs(xb, ids)
			faiss_index.Train(xb)
			faiss.WriteIndex(faiss_index, fmt.Sprintf("indices/%d", partition_idx))
			faiss_index.Delete()

		}(partition_idx, partitioned_records)
	}
	wg.Wait()
}

func (schema Schema) pull_item_data() (map[int][]Record, ItemLookup, error) {
	var item_lookup ItemLookup
	var partitioned_records map[int][]Record
	var err error
	found_item_source := false
	for _, src := range schema.Sources {
		if strings.ToLower(src.Record) == "items" {
			if src.Type == "csv" {
				partitioned_records, item_lookup, err = schema.read_partitioned_csv(src.Path)
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

func read_schema(schema_file string) Schema {
	jsonFile, err := os.Open(schema_file)
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)

	var schema Schema
	json.Unmarshal(byteValue, &schema)
	if schema.IndexFactory == "" {
		schema.IndexFactory = "IDMap,LSH"
	}
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

	return schema
}

func main() {
	base_dir := "."
	if len(os.Args) > 1 {
		base_dir = os.Args[1]
	}

	schema := read_schema(base_dir + "/schema.json")

	indices := gcache.New(32).
		LFU().
		LoaderFunc(func(key interface{}) (interface{}, error) {
			ind, err := faiss.ReadIndex(fmt.Sprintf("%s/indices/%d", base_dir, key), 0)
			return *ind, err
		}).
		EvictedFunc(func(key, value interface{}) {
			value.(faiss.Index).Delete()
		}).
		Build()

	// indices := make([]faiss.IndexImpl, len(partitions))
	// indices := make([]faiss.Index, len(partitions))

	var partitioned_records map[int][]Record

	//TODO: Read from CLI
	var item_lookup ItemLookup
	var err error
	partitioned_records, item_lookup, err = schema.pull_item_data()
	if err != nil {
		log.Fatal(err)
	}

	schema.index_partitions(partitioned_records)

	start_server(schema, partitioned_records, indices, item_lookup)
}
