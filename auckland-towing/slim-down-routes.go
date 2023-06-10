package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
)

type Route struct {
	Vendor     int         `json:"vendor"`
	Paths      [][]float64 `json:"path"`
	Timestamps []int       `json:"timestamps"`
}

func main() {
	paths, err := os.ReadFile("routes.json")
	if err != nil {
		panic(err)
	}
	var routes []Route
	var slimRoutes []Route
	if err := json.Unmarshal(paths, &routes); err != nil {
		panic(err)
	}
	longestTimestamp := 0
	for idx, route := range routes {
		if len(route.Paths) <= 10 {
			continue
		}
		// We want to keep the origin and end for accuracy but can trim the rest
		fmt.Printf("dealing with slice of len %d\n", len(route.Paths))
		for len(route.Paths) > 10 {
			min := 1
			max := len(route.Paths) - 1
			randomIdx := rand.Intn(max-min) + min
			route.Paths = removePaths(route.Paths, randomIdx)
			route.Timestamps = removeTimestamps(route.Timestamps, randomIdx)
		}
		for _, ts := range route.Timestamps {
			if ts > longestTimestamp {
				longestTimestamp = ts
			}
		}
		slimRoutes = append(slimRoutes, route)
		fmt.Printf("trimmed %d down to 10 paths\n", idx)
	}
	fmt.Printf("longest timestamp is %d", longestTimestamp)
	b, err := json.Marshal(slimRoutes)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile("routes-slim.json", b, 0644); err != nil {
		panic(err)
	}
}

func removePaths(slice [][]float64, s int) [][]float64 {
	return append(slice[:s], slice[s+1:]...)
}

func removeTimestamps(slice []int, s int) []int {
	return append(slice[:s], slice[s+1:]...)
}
