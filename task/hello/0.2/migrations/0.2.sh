#!/usr/bin/env bash

set -euo pipefail

declare -r pipeline_file=${1:?missing pipeline file}

echo "Applying migration to pipeline ${pipeline_file}"

# Let's fail shellcheck and therefore the ./hack/valiate-migration.sh script for testing purposes
# Unquoted variable (SC2086)
#echo $pipeline_file

if ! yq -e '.spec.tasks[] | select(.name == "hello").params[] | select(.name == "pipelinerun-name")' "$pipeline_file" >/dev/null; then
  echo "Adding pipelinerun-name parameter to the hello task"
  yq -i "(.spec.tasks[] | select(.name == \"hello\")).params += [{\"name\": \"pipelinerun-name\", \"value\": \"\$(context.pipelineRun.name)\"}]" "$pipeline_file"
else
    echo "pipelinerun-name parameter already exists in hello task. No changes needed."
fi
