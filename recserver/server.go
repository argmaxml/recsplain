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
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/template/html"
	"github.com/sbinet/npyio"
	"gonum.org/v1/gonum/mat"
)

type Schema struct {
	IdCol    string    `json:"id_col"`
	Metric   string    `json:"metric"`
	Filters  []Filter  `json:"filters"`
	Encoders []Encoder `json:"encoders"`
	Sources  []Source  `json:"sources"`
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

func itertools_product(a ...[]string) [][]string {
	c := 1
	for _, a := range a {
		c *= len(a)
	}
	if c == 0 {
		return nil
	}
	p := make([][]string, c)
	b := make([]string, c*len(a))
	n := make([]int, len(a))
	s := 0
	for i := range p {
		e := s + len(a)
		pi := b[s:e]
		p[i] = pi
		s = e
		for j, n := range n {
			pi[j] = a[j][n]
		}
		for j := len(n) - 1; j >= 0; j-- {
			n[j]++
			if n[j] < len(a[j]) {
				break
			}
			n[j] = 0
		}
	}
	return p
}

func zip(a []string, b []string) map[string]string {
	c := make(map[string]string)
	for i := 0; i < len(a); i++ {
		c[a[i]] = b[i]
	}
	return c
}

func read_schema(schema_file string) (Schema, [][]string) {
	jsonFile, err := os.Open(schema_file)
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)

	var schema Schema

	json.Unmarshal(byteValue, &schema)

	values := make([][]string, len(schema.Filters))
	for i := 0; i < len(schema.Filters); i++ {
		values[i] = schema.Filters[i].Values
	}
	partitions := itertools_product(values...)
	return schema, partitions
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

func read_npy(npy string) *mat.Dense {
	f, err := os.Open(npy)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	r, err := npyio.NewReader(f)
	if err != nil {
		log.Fatal(err)
	}

	shape := r.Header.Descr.Shape
	raw := make([]float64, shape[0]*shape[1])

	err = r.Read(&raw)
	if err != nil {
		log.Fatal(err)
	}

	m := mat.NewDense(shape[0], shape[1], raw)
	return m
}

func index_of(a []string, x string) int {
	for i, n := range a {
		if n == x {
			return i
		}
	}
	return -1
}

func encode(schema Schema, embeddings map[string]*mat.Dense, query map[string]string) []float32 {
	encoded := make([]float64, 0)
	// Concatenate all components to a single vector
	for i := 0; i < len(schema.Encoders); i++ {
		val, found := query[schema.Encoders[i].Field]
		if !found {
			val = schema.Encoders[i].Default
		}
		emb_matrix := embeddings[schema.Encoders[i].Field]
		row_index := index_of(schema.Encoders[i].Values, val)
		if row_index == -1 { // not found, use default
			row_index = index_of(schema.Encoders[i].Values, schema.Encoders[i].Default)
		}
		_, emb_size := emb_matrix.Dims()
		raw_vector := make([]float64, emb_size)
		if row_index > -1 {
			raw_vector = mat.Row(nil, row_index, emb_matrix)
			for j := 0; j < emb_size; j++ {
				raw_vector[j] *= schema.Encoders[i].Weight
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

func partition_number(schema Schema, partition_map map[string]int, query map[string]string) int {

	filters := make([]string, len(schema.Filters))
	for i := 0; i < len(schema.Filters); i++ {
		val, found := query[schema.Filters[i].Field]
		if !found {
			val = schema.Filters[i].Default
		}
		filters[i] = val
	}
	partition_key := strings.Join(filters, "~")
	partition_idx := partition_map[partition_key]
	return partition_idx
}

func componentwise_distance(schema Schema, embeddings map[string]*mat.Dense, v1 []float32, v2 []float32) (float32, map[string]float32) {
	breakdown := make(map[string]float32)
	var total_distance float32
	total_distance = 0
	vector_size := 0
	for field, emb_matrix := range embeddings {
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

// func start_server(indices []faiss.IndexImpl, embeddings map[string]*mat.Dense, partitions [][]string, partition_map map[string]int, schema Schema, index_labels []string) {
func start_server(partitioned_records map[int][]Record, indices []faiss.Index, embeddings map[string]*mat.Dense, partitions [][]string, partition_map map[string]int, schema Schema, index_labels []string) {
	app := fiber.New(fiber.Config{
		Views: html.New("./views", ".html"),
	})

	// GET /api/register
	app.Get("/npy/*", func(c *fiber.Ctx) error {
		m := read_npy(c.Params("*") + ".npy")
		msg := fmt.Sprintf("data = %v\n", mat.Formatted(m, mat.Prefix("       ")))
		return c.SendString(msg)
	})

	app.Get("/partitions", func(c *fiber.Ctx) error {
		ret := make([]PartitionMeta, len(partitions))
		for i, partition := range partitions {
			ret[i].Name = partition
			ret[i].Count = int(indices[i].Ntotal())
			ret[i].Trained = indices[i].IsTrained()
		}
		return c.JSON(ret)
	})

	app.Get("/labels", func(c *fiber.Ctx) error {
		return c.JSON(index_labels)
	})

	app.Post("/encode", func(c *fiber.Ctx) error {
		// Get raw body from POST request
		var query map[string]string
		json.Unmarshal(c.Body(), &query)
		// if err := c.BodyParser(&query); err != nil {
		// 	return err
		// }
		encoded := encode(schema, embeddings, query)
		return c.JSON(encoded)
	})

	app.Post("/query/:k?", func(c *fiber.Ctx) error {
		var query map[string]string
		json.Unmarshal(c.Body(), &query)

		encoded := encode(schema, embeddings, query)
		partition_idx := partition_number(schema, partition_map, query)
		k, err := strconv.Atoi(c.Params("k"))
		if err != nil {
			k = 2
		}
		distances, ids, err := indices[partition_idx].Search(encoded, int64(k))
		if err != nil {
			log.Fatal(err)
		}
		retrieved := make([]Explanation, 0)
		for i, id := range ids {
			if id == -1 {
				continue
			}
			next_result := Explanation{
				Label:    index_labels[int(id)],
				Distance: distances[i],
			}
			if partitioned_records != nil {
				var reconstructed []float32
				reconstructed = nil
				//TODO: Have a more intelligent way of looking up the original record (currently, linear search)
				for _, record := range partitioned_records[partition_idx] {
					if record.Id == int(id) {
						reconstructed = encode(schema, embeddings, record.Values)
						break
					}
				}
				if reconstructed != nil {
					total_distance, breakdown := componentwise_distance(schema, embeddings, encoded, reconstructed)
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
		for _, e := range schema.Filters {
			fields = append(fields, e.Field)
		}
		for _, e := range schema.Encoders {
			fields = append(fields, e.Field)
		}
		return c.Render("index", fiber.Map{
			"Headline": "Recsplain",
			"Fields":   fields,
		})
	})

	log.Fatal(app.Listen(":3000"))
}

func read_partitioned_csv(schema Schema, partition_map map[string]int, filename string) (map[int][]Record, []string, error) {

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
		return nil, nil, err
	}

	header := raw_data[0]
	id_num := index_of(header, schema.IdCol)
	if id_num == -1 {
		return nil, nil, errors.New("Id column not found")
	}
	data := raw_data[1:]

	label2id := make(map[string]int)
	partition2records := make(map[int][]Record)
	for _, row := range data {
		id, found := label2id[row[id_num]]
		if !found {
			id = len(label2id)
			label2id[row[id_num]] = id
		}
		query := zip(header, row)
		partition_idx := partition_number(schema, partition_map, query)
		partition2records[partition_idx] = append(partition2records[partition_idx], Record{
			Label:     row[id_num],
			Id:        id,
			Values:    query,
			Partition: partition_idx,
		})

	}
	//TODO: Do we need index_labels ? can we use the label2id instead?
	index_labels := make([]string, len(label2id))
	for lbl, id := range label2id {
		index_labels[id] = lbl
	}
	return partition2records, index_labels, nil
}

func index_partitions(schema Schema, indices []faiss.Index, dim int, embeddings map[string]*mat.Dense, records map[int][]Record) {
	var wg sync.WaitGroup
	for partition_idx, partitioned_records := range records {
		wg.Add(1)
		go func(i int, recs []Record) {
			defer wg.Done()
			if strings.ToLower(schema.Metric) == "ip" {
				// indices[i], _ = faiss.NewIndexFlatIP(dim)
				indices[i], _ = faiss.IndexFactory(dim, "IVF10,Flat", faiss.MetricInnerProduct)
			}
			if strings.ToLower(schema.Metric) == "l2" {
				// indices[i], _ = faiss.NewIndexFlatL2(dim)
				indices[i], _ = faiss.IndexFactory(dim, "IVF10,Flat", faiss.MetricL2)
			}
			if strings.ToLower(schema.Metric) == "l1" {
				// indices[i], _ = faiss.NewIndexFlatL1(dim)
				indices[i], _ = faiss.IndexFactory(dim, "IVF10,Flat", faiss.MetricL1)
			}
			xb := make([]float32, dim*len(recs))
			ids := make([]int64, len(recs))
			for i, record := range recs {
				encoded := encode(schema, embeddings, record.Values)
				for j, v := range encoded {
					xb[i*dim+j] = v
					ids[i] = int64(record.Id)
				}
			}
			indices[i].Train(xb)
			fmt.Println("IsTrained(", i, ") =", indices[i].IsTrained())
			indices[i].AddWithIDs(xb, ids)
			fmt.Println("IsTrained(", i, ") =", indices[i].IsTrained())
		}(partition_idx, partitioned_records)
	}
	wg.Wait()
}

func main() {
	base_dir := "."
	if len(os.Args) > 1 {
		base_dir = os.Args[1]
	}

	embeddings := make(map[string]*mat.Dense)
	// values:= make(map[string][]string)
	schema, partitions := read_schema(base_dir + "/schema.json")
	dim := 0
	for i := 0; i < len(schema.Encoders); i++ {
		embeddings[schema.Encoders[i].Field] = read_npy(schema.Encoders[i].Npy)
		_, emb_size := embeddings[schema.Encoders[i].Field].Dims()
		dim += emb_size
	}
	partition_map := make(map[string]int)
	// indices := make([]faiss.IndexImpl, len(partitions))
	indices := make([]faiss.Index, len(partitions))
	for i := 0; i < len(partitions); i++ {
		key := strings.Join(partitions[i], "~")
		partition_map[key] = i
	}
	var partitioned_records map[int][]Record

	LOAD_INDEX := false
	var index_labels []string
	if LOAD_INDEX {
		index_labels = read_index_labels(base_dir + "/index_labels.json")
		for i := 0; i < len(partitions); i++ {
			ind, err := faiss.ReadIndex(base_dir+"/"+strconv.Itoa(i), 0)
			indices[i] = *ind
			if err != nil {
				log.Fatal(err)
			}
		}
		partitioned_records = nil
	} else {
		var err error

		found_item_source := false
		for _, src := range schema.Sources {
			if strings.ToLower(src.Record) == "items" {
				if src.Type == "csv" {
					partitioned_records, index_labels, err = read_partitioned_csv(schema, partition_map, src.Path)
					if err != nil {
						log.Fatal(err)
					}
					found_item_source = true
				}
			}
		}
		if !found_item_source {
			log.Fatal("No item source found")
		}

		index_partitions(schema, indices, dim, embeddings, partitioned_records)
	}

	start_server(partitioned_records, indices, embeddings, partitions, partition_map, schema, index_labels)
}
