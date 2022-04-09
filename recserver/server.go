package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/sbinet/npyio"
	"gonum.org/v1/gonum/mat"
)

type Schema struct {
	Filters  []Filter  `json:"filters"`
	Encoders []Encoder `json:"encoders"`
}

type Filter struct {
	Field  string   `json:"field"`
	Values []string `json:"values"`
}

type Encoder struct {
	Field  string   `json:"field"`
	Values []string `json:"values"`
	Type   string   `json:"type"`
	Npy    string   `json:"npy"`
	Weight float64  `json:"weight"`
}

func read_schema(schema_file string) string {
	jsonFile, err := os.Open(schema_file)
	if err != nil {
		fmt.Println(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)

	var schema Schema

	json.Unmarshal(byteValue, &schema)

	ret := ""
	for i := 0; i < len(schema.Filters); i++ {
		ret += fmt.Sprintf("Filter: %s\n", schema.Filters[i].Field)
	}
	return ret
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

func main() {
	app := fiber.New()

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
	app.Get("/:fname", func(c *fiber.Ctx) error {
		msg := read_schema(c.Params("fname") + ".json")
		return c.SendString(msg)
	})

	log.Fatal(app.Listen(":3000"))
}
