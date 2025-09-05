# check-kustomize-build-workflow-base task

Testing task based on example hello task. It's purpose is to verify that the github
workflow "check-kustomize-build" and the associated scripts "verify-manifests.sh" and
"build-manifests.sh" work as expected. 

It works together with task "check-kustomize-build-workflow-modified", which modifies this
task using kustomize. If the modified version task manifest (the yaml file) is not part of the PR,
the github workflow check fails.

## Workspaces
|name|description|optional|
|---|---|---|
|source|Workspace with the source code (at subpath /source)|false|
