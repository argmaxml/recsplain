package main

import "gonum.org/v1/gonum/mat"

type Schema struct {
	IdCol          string    `json:"id_col"`
	Metric         string    `json:"metric"`
	IndexFactory   string    `json:"index_factory"`
	Filters        []Filter  `json:"filters"`
	Encoders       []Encoder `json:"encoders"`
	Sources        []Source  `json:"sources"`
	Dim            int       `json:"dim"`
	Embeddings     map[string]*mat.Dense
	NumItems       int
	Partitions     [][]string
	PartitionMap   map[string]int
	WeightOverride []WeightOverride `json:"weight_override"`
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

type WeightOverride struct {
	FilterField   string  `json:"filter_field"`
	EncoderField  string  `json:"encoder_field"`
	FilterValue   string  `json:"filter_value"`
	EncoderWeight float64 `json:"encoder_weight"`
}

type Source struct {
	Record      string `json:"record"`
	Type        string `json:"type"`
	Path        string `json:"path"`
	Query       string `json:"query"`
	RefreshRate int64  `json:"refresh_rate"`
}

type Explanation struct {
	Label     string             `json:"label"`
	Distance  float32            `json:"distance"`
	Breakdown map[string]float32 `json:"breakdown"`
}

type QueryRetVal struct {
	Explanations []Explanation `json:"explanations"`
	Variant      string        `json:"variant"`
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
	Values    []string
	Fields    []string
}

type PartitionMeta struct {
	Name    []string `json:"name"`
	Count   int      `json:"count"`
	Trained bool     `json:"trained"`
}

type Variant struct {
	Name       string             `json:"name"`
	Percentage float64            `json:"percentage"`
	Weights    map[string]float64 `json:"weights"`
}
