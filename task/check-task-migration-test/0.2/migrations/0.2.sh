#!/usr/bin/env bash

set -euo pipefail

declare -r pipeline_file=${1:?missing pipeline file}

echo "Applying migration to pipeline ${pipeline_file}"

# Let's fail shellcheck and therefore the ./hack/valiate-migration.sh script for testing purposes
# Unquoted variable (SC2086)
#echo $pipeline_file
