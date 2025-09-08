#!/bin/bash
shopt -s nullglob
set -euo pipefail

# <TEMPLATED FILE!>
# This file comes from the templates at https://github.com/konflux-ci/task-repo-shared-ci.
# Please consider sending a PR upstream instead of editing the file directly.
# See the SHARED-CI.md document in this repo for more details.

echo ">>> Applying and validating Tekton Tasks"

for task_folder in task/*/; do
  if [ -d "$task_folder" ]; then
    task_name="$(basename "$task_folder")"
    echo ">>> Validating Task: $task_name"
    
    (
      cd "$task_folder"
      for version in */; do
        if [ -d "$version" ]; then
          kubectl apply -f "$version/$task_name.yaml" --dry-run=server
        fi
      done
    )
  fi
done

echo ">>> All tasks validated successfully."
