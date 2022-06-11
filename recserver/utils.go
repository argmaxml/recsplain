package main

import (
	"log"
	"math/rand"
	"os"

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
