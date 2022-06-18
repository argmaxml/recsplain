package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/DataIntelligenceCrew/go-faiss"
	"github.com/bluele/gcache"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/template/html"
	"gonum.org/v1/gonum/mat"
)

const port = 8088

func start_server(schema Schema, variants []Variant, indices gcache.Cache, item_lookup ItemLookup, partitioned_records map[int][]Record, user_data map[string][]string) {
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
		partitioned_records, item_lookup, _ = schema.pull_item_data(variants)
		os.RemoveAll("indices")
		schema.index_partitions(partitioned_records)
		return c.SendString("{\"Status\": \"OK\"}")
	})

	app.Get("/reload_users", func(c *fiber.Ctx) error {
		var err error
		if user_data == nil {
			return c.SendString("User history not available in sources list")
		}
		user_data, err = schema.pull_user_data()
		if err != nil {
			return c.SendString(err.Error())
		}
		return c.SendString("{\"Status\": \"OK\"}")
	})

	app.Post("/encode", func(c *fiber.Ctx) error {
		var query map[string]string
		json.Unmarshal(c.Body(), &query)
		encoded := schema.encode(query)
		return c.JSON(encoded)
	})

	app.Post("/item_query/:k?", func(c *fiber.Ctx) error {
		payload := struct {
			ItemId  string            `json:"id"`
			Query   map[string]string `json:"query"`
			Explain bool              `json:"explain"`
			Variant string            `json:"variant"`
		}{}

		if err := c.BodyParser(&payload); err != nil {
			return err
		}
		k, err := strconv.Atoi(c.Params("k"))
		if err != nil {
			k = 2
		}
		var partition_idx int
		var encoded []float32
		var variant string
		if payload.Variant == "" {
			variant = random_variant(variants)
		} else {
			variant = payload.Variant
		}
		if payload.ItemId != "" {
			id := int64(item_lookup.label2id[variant+"~"+payload.ItemId])
			partition_idx = item_lookup.label2partition[variant+"~"+payload.ItemId]
			encoded = schema.reconstruct(partitioned_records, id, partition_idx)
			if encoded == nil {
				return c.SendString("{\"Status\": \"Not Found\"}")
			}
		} else {
			partition_idx = schema.partition_number(payload.Query, variant)
			encoded = schema.encode(payload.Query)
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
				Label:    strings.SplitN(item_lookup.id2label[int(id)], "~", 2)[1],
				Distance: distances[i],
			}
			if (payload.Explain) && (partitioned_records != nil) {
				reconstructed := schema.reconstruct(partitioned_records, id, partition_idx)
				if reconstructed != nil {
					total_distance, breakdown := schema.componentwise_distance(encoded, reconstructed)
					next_result.Distance = total_distance
					next_result.Breakdown = breakdown
				}
			}
			retrieved = append(retrieved, next_result)
		}
		if variant == "" {
			variant = "default"
		}
		retval := QueryRetVal{
			Explanations: retrieved,
			Variant:      variant,
		}
		return c.JSON(retval)
	})

	app.Post("/user_query/:k?", func(c *fiber.Ctx) error {
		payload := struct {
			UserId  string            `json:"id"`
			History []string          `json:"history"`
			Filters map[string]string `json:"filters"`
			Explain bool              `json:"explain"`
			Variant string            `json:"variant"`
		}{}

		if err := c.BodyParser(&payload); err != nil {
			return err
		}
		var variant string
		if payload.Variant == "" {
			variant = random_variant(variants)
		} else {
			variant = payload.Variant
		}
		partition_idx := schema.partition_number(payload.Filters, variant)
		k, err := strconv.Atoi(c.Params("k"))
		if err != nil {
			k = 2
		}
		item_vecs := make([][]float32, 1)
		item_vecs[0] = make([]float32, schema.Dim) // zero_vector

		if payload.UserId != "" {
			//Override user history from the id, if provided
			if user_data == nil {
				return c.SendString("User history not available in sources list")
			}
			payload.History = user_data[payload.UserId]
		}

		for _, item_id := range payload.History {
			id := int64(item_lookup.label2id[variant+"~"+item_id])
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

		//TODO: Resolve code duplication (2)
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
				Label:    strings.SplitN(item_lookup.id2label[int(id)], "~", 2)[1],
				Distance: distances[i],
			}
			if (payload.Explain) && (partitioned_records != nil) {
				reconstructed := schema.reconstruct(partitioned_records, id, partition_idx)
				if reconstructed != nil {
					total_distance, breakdown := schema.componentwise_distance(user_vec, reconstructed)
					next_result.Distance = total_distance
					next_result.Breakdown = breakdown
				}
			}
			retrieved = append(retrieved, next_result)
		}
		if variant == "" {
			variant = "default"
		}
		retval := QueryRetVal{
			Explanations: retrieved,
			Variant:      variant,
		}
		return c.JSON(retval)
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

	log.Fatal(app.Listen(fmt.Sprintf(":%d", port)))
}

func main() {
	base_dir := "."
	if len(os.Args) > 1 {
		base_dir = os.Args[1]
	}

	schema, variants, err := read_schema(base_dir+"/schema.json", base_dir+"/variants.json")
	if err != nil {
		fmt.Println(err)
	}

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
	var user_data map[string][]string

	//TODO: Read from CLI
	item_lookup := ItemLookup{
		id2label:        make([]string, 0),
		label2id:        make(map[string]int),
		label2partition: make(map[string]int),
	}
	partitioned_records, item_lookup, err = schema.pull_item_data(variants)
	if err != nil {
		log.Fatal(err)
	}
	user_data, err = schema.pull_user_data()
	if err != nil {
		log.Println(err)
	}

	schema.index_partitions(partitioned_records)

	// Poll for changes:
	for _, src := range schema.Sources {
		if src.RefreshRate > 0 {
			//This is probably a bad idea, but it works for now
			go poll_endpoint(fmt.Sprintf("http://localhost:%d/reload_"+src.Record, port), src.RefreshRate)
		}
	}

	start_server(schema, variants, indices, item_lookup, partitioned_records, user_data)
}
