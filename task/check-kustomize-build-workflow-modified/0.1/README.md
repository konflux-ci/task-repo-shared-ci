# check-kustomize-build-workflow-modified task

Testing task that modifies "check-kustomize-build-workflow" task. It's purpose is to verify that the github
workflow "check-kustomize-build" and the associated scripts "verify-manifests.sh" and
"build-manifests.sh" work as expected. 

If this modified task manifest (the yaml file) is not part of the PR, the github workflow check fails.

## Workspaces
|name|description|optional|
|---|---|---|
|source|Workspace with the source code (at subpath /source)|false|
