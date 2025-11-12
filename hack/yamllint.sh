#!/bin/bash
set -o errexit -o nounset -o pipefail

mapfile -t shared_yaml_files < <(
    git grep --files-with-matches '^# <TEMPLATED FILE!>' | grep -E '\.ya?ml'
)

ignore_disable_comment() {
    sed -i 's/^# yamllint disable-file/# dont disable file/' "${shared_yaml_files[@]}"
}

undo_ignore_disable_comment() {
    sed -i 's/^# dont disable file/# yamllint disable-file/' "${shared_yaml_files[@]}"
}

ignore_disable_comment
trap undo_ignore_disable_comment EXIT

yamllint "$@"
