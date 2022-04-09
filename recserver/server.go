package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"

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

func read_npy(npy string) string {
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
	return fmt.Sprintf("data = %v\n", mat.Formatted(m, mat.Prefix("       ")))
}

func encode(schema Schema, query map[string]string) *mat.Dense {
	return nil
}

func main() {
	app := fiber.New(fiber.Config{
		Views: html.New("./views", ".html"),
	})
	// embeddings:= make(map[string]*mat.Dense)
	// values:= make(map[string]*mat.Dense)
	schema, partitions := read_schema("schema.json")
	// GET /api/register
	app.Get("/npy/*", func(c *fiber.Ctx) error {
		msg := read_npy(c.Params("*") + ".npy")
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

	// GET /john
	app.Get("/partitions", func(c *fiber.Ctx) error {
		ret := make([]string, len(partitions))
		for i, partition := range partitions {
			ret[i] = fmt.Sprintf("%s", partition)
		}
		return c.JSON(ret)
	})

	app.Post("/encode", func(c *fiber.Ctx) error {
		// Get raw body from POST request
		c.Body() // user=john
		var query map[string]string

		if err := c.BodyParser(&query); err != nil {
			return err
		}
		ret := encode(schema, query)
		return c.JSON(ret)
	})

	app.Get("/", func(c *fiber.Ctx) error {
		// Render index template
		return c.Render("index", fiber.Map{
			"Headline": "Recsplain",
		})
	})

	log.Fatal(app.Listen(":3000"))
}
