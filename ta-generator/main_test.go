package main

import (
	"bytes"
	"errors"
	"flag"
	"os"
	"path"
	"testing"

	"github.com/google/go-cmp/cmp"
)

var update = flag.Bool("update", false, "rewrite the golden ta.yaml files with the generated output")

func TestGolden(t *testing.T) {
	dirs, err := os.ReadDir("golden")
	if err != nil {
		t.Fatal(err)
	}

	resolveImage = func() string {
		return "quay.io/konflux-ci/build-trusted-artifacts:latest@sha256:resolved"
	}

	for _, dir := range dirs {
		t.Run(dir.Name(), func(t *testing.T) {
			task, err := loadTask(path.Join("golden", dir.Name(), "base.yaml"))
			if errors.Is(err, os.ErrNotExist) {
				task, err = loadTask(path.Join("golden", dir.Name(), "kustomization.yaml"))
			}
			if err != nil {
				t.Fatal(err)
			}

			recipe, err := readRecipe(path.Join("golden", dir.Name(), "recipe.yaml"))
			if err != nil {
				t.Fatal(err)
			}

			image = "" // force resolve
			if dir.Name() == "git-clone" {
				// use existing, simulates image being set from main from the parsed Task Step
				image = "quay.io/konflux-ci/build-trusted-artifacts:latest@sha256:existing"
			}

			if err := perform(task, recipe); err != nil {
				t.Fatal(err)
			}

			got := bytes.Buffer{}
			if err := writeTask(task, &got); err != nil {
				t.Fatal(err)
			}

			golden := path.Join("golden", dir.Name(), "ta.yaml")

			if *update {
				if err := os.WriteFile(golden, got.Bytes(), 0644); err != nil {
					t.Fatal(err)
				}
				return
			}

			// The golden ta.yaml files are compared byte for byte. They must match
			// exactly what the generator produces. Run `go test -update` to regenerate them.
			expected, err := os.ReadFile(golden)
			if err != nil {
				t.Fatal(err)
			}

			if diff := cmp.Diff(string(expected), got.String()); diff != "" {
				t.Errorf("%s diff (-expected +got):\n%s", dir.Name(), diff)
			}
		})
	}
}
