#!/bin/bash
set -o errexit -o nounset -o pipefail

mapfile -t scripts < <(find hack/ .github/ '{{cookiecutter.repo_root}}/'  -name '*.sh')

if [ "${#scripts[@]}" -eq 0 ]; then
    echo "No shell scripts found."
    exit 0
fi

shellcheck --version
shellcheck "${scripts[@]}" "$@"
