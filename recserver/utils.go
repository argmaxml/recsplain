package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/sbinet/npyio"
	"gonum.org/v1/gonum/mat"
)

func random_by_weights(values []string, weights []float64) string {
	if len(values) != len(weights) || len(values) == 0 {
		return ""
	}
	total := 0.0
	for _, w := range weights {
		total += w
	}
	r := rand.Float64() * total
	for i, w := range weights {
		r -= w
		if r <= 0 {
			return values[i]
		}
	}
	return values[len(values)-1]
}

func itertools_product[T any](a ...[]T) [][]T {
	c := 1
	for _, a := range a {
		c *= len(a)
	}
	if c == 0 {
		return nil
	}
	p := make([][]T, c)
	b := make([]T, c*len(a))
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

func zip[K comparable, V any](a []K, b []V) map[K]V {
	c := make(map[K]V)
	for i := 0; i < len(a); i++ {
		c[a[i]] = b[i]
	}
	return c
}

func index_of[T comparable](a []T, x T) int {
	for i, n := range a {
		if n == x {
			return i
		}
	}
	return -1
}

func contains[T comparable](a []T, x T) bool {
	return index_of(a, x) != -1
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

func write_npy(npy string, m []float32) error {
	f, err := os.Create(npy)
	if err != nil {
		return err
	}
	defer f.Close()

	err = npyio.Write(f, m)
	if err != nil {
		return err
	}
	return nil
}

func download_file(url string, filename string) error {
	// Create the file
	out, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer out.Close()

	// Get the data
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Write the body to file
	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return err
	}

	return nil
}

func read_csv(filename string) ([]string, [][]string, error) {
	if strings.HasPrefix(filename, "http") {
		dfilename := filename[strings.LastIndex(filename, "/")+1:]
		err := download_file(filename, dfilename)
		if err != nil {
			return nil, nil, err
		}
		filename = dfilename
	}
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
	data := raw_data[1:]
	return header, data, nil
}

func poll_endpoint(url string, seconds int64) {
	if seconds <= 0 {
		return
	}
	time.Sleep(time.Second * time.Duration(seconds))
	ticker := time.NewTicker(time.Second * time.Duration(seconds))
	for t := range ticker.C {
		resp, _ := http.Get(url)
		fmt.Println("Polling ", url, " at ", t, " status: ", resp.Status)
	}
}
