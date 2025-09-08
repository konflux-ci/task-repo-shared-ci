# hello task

The purpose of the 0.2 version of this task is to test [`.github/workflows/check-task-migration.yaml`](.github/workflows/check-task-migration.yaml)
workflow and the associated [`hack/validate-migration.sh`](hack/validate-migration.sh) script.

To test:
1. uncomment the code in [`task/hello/0.2/migrations/0.2.sh`](task/hello/0.2/migrations/0.2.sh).
This should cause the failure [`hack/validate-migration.sh`](hack/validate-migration.sh), in the ShellCheck phase.

2. Remove the [`task/hello/0.2/MIGRATION.md`](task/hello/0.2/MIGRATION.md) file. This should cause a following failure in the "Check MIGRATION.md" stage of the [`.github/workflows/check-task-migration.yaml`](.github/workflows/check-task-migration.yaml) workflow:
```
Missing file task/hello/0.2/MIGRATION.md
```

## Parameters
|name|description|default value|required|
|---|---|---|---|
|pipelinerun-name|The name of the pipelinerun||true|

## Workspaces
|name|description|optional|
|---|---|---|
|source|Workspace with the source code (at subpath /source)|false|
