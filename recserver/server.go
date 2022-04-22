package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/DataIntelligenceCrew/go-faiss"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/template/html"
	"github.com/sbinet/npyio"
	"gonum.org/v1/gonum/mat"
)

type Schema struct {
	Filters  []Filter  `json:"filters"`
	Encoders []Encoder `json:"encoders"`
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

func encode(schema Schema, partition_map map[string]int, embeddings map[string]*mat.Dense, query map[string]string) (int, []float64) {
	vectors := make([]*mat.Dense, len(schema.Encoders))
	encoded := make([]float64, 0)
	// Concatenate all components to a single vector
	for i := 0; i < len(schema.Encoders); i++ {
		val, found := query[schema.Encoders[i].Field]
		if !found {
			val = schema.Encoders[i].Default
		}
		emb_matrix := embeddings[schema.Encoders[i].Field]
		row_index := index_of(schema.Encoders[i].Values, val)
		if row_index == -1 {
			row_index = index_of(schema.Encoders[i].Values, schema.Encoders[i].Default)
		}
		_, emb_size := emb_matrix.Dims()
		raw_vector := mat.Row(nil, row_index, emb_matrix)
		for j := 0; j < emb_size; j++ {
			raw_vector[j] *= schema.Encoders[i].Weight
		}
		encoded = append(encoded, raw_vector...)
		vectors[i] = mat.NewDense(1, emb_size, raw_vector)

	}
	// Return partition number
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
	return partition_idx, encoded
}

func start_server(indices []faiss.IndexImpl, embeddings map[string]*mat.Dense, partitions [][]string, partition_map map[string]int, schema Schema, index_labels []string) {
	app := fiber.New(fiber.Config{
		Views: html.New("./views", ".html"),
	})

	// GET /api/register
	app.Get("/npy/*", func(c *fiber.Ctx) error {
		m := read_npy(c.Params("*") + ".npy")
		msg := fmt.Sprintf("data = %v\n", mat.Formatted(m, mat.Prefix("       ")))
		return c.SendString(msg)
	})

	// GET /flights/LAX-SFO
	app.Get("/flights/:from-:to", func(c *fiber.Ctx) error {
		msg := fmt.Sprintf("💸 From: %s, To: %s", c.Params("from"), c.Params("to"))
		return c.SendString(msg) // => 💸 From: LAX, To: SFO
	})

	// GET /dictionary.txt
	app.Get("/:file.:ext", func(c *fiber.Ctx) error {
		msg := fmt.Sprintf("📃 %s.%s", c.Params("file"), c.Params("ext"))
		return c.SendString(msg) // => 📃 dictionary.txt
	})

	// GET /john/75
	app.Get("/:name/:age/:gender?", func(c *fiber.Ctx) error {
		msg := fmt.Sprintf("👴 %s is %s years old", c.Params("name"), c.Params("age"))
		return c.SendString(msg) // => 👴 john is 75 years old
	})

	app.Get("/partitions", func(c *fiber.Ctx) error {
		ret := make([]string, len(partitions))
		for i, partition := range partitions {
			ret[i] = fmt.Sprintf("%s", partition)
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
		_, encoded := encode(schema, partition_map, embeddings, query)
		return c.JSON(encoded)
	})

	app.Post("/query/:k?", func(c *fiber.Ctx) error {
		var query map[string]string
		json.Unmarshal(c.Body(), &query)

		partition_idx, encoded := encode(schema, partition_map, embeddings, query)
		encoded32 := make([]float32, len(encoded))
		k, err := strconv.Atoi(c.Params("k"))
		if err != nil {
			k = 2
		}
		for i, f64 := range encoded {
			encoded32[i] = float32(f64)
		}
		_, ids, err := indices[partition_idx].Search(encoded32, int64(k))
		if err != nil {
			log.Fatal(err)
		}
		retrieved := make([]string, k)
		for i, id := range ids {
			//TODO: fix this out of bounds error
			// retrieved[i] = index_labels[int(id)]
			retrieved[i] = strconv.Itoa(int(id))
		}
		return c.JSON(retrieved)
	})

	app.Get("/", func(c *fiber.Ctx) error {
		// Render index template
		return c.Render("index", fiber.Map{
			"Headline": "Recsplain",
		})
	})

	log.Fatal(app.Listen(":3000"))
}

func main() {
	// base_dir := "/home/ugoren/TRecs/models/boom/"
	base_dir := "."
	if len(os.Args) > 1 {
		base_dir = os.Args[1]
	}
	index_labels := read_index_labels(base_dir + "/index_labels.json")
	embeddings := make(map[string]*mat.Dense)
	// values:= make(map[string][]string)
	schema, partitions := read_schema(base_dir + "/schema.json")
	for i := 0; i < len(schema.Encoders); i++ {
		embeddings[schema.Encoders[i].Field] = read_npy(schema.Encoders[i].Npy)
	}
	partition_map := make(map[string]int)
	indices := make([]faiss.IndexImpl, len(partitions))
	for i := 0; i < len(partitions); i++ {
		key := strings.Join(partitions[i], "~")
		partition_map[key] = i
		ind, err := faiss.ReadIndex(base_dir+"/"+strconv.Itoa(i), 0)
		indices[i] = *ind
		if err != nil {
			log.Fatal(err)
		}
	}
	start_server(indices, embeddings, partitions, partition_map, schema, index_labels)
}
