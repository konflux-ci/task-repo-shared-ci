# check-task-migration-test task

The purpose of this task is to test [`.github/workflows/check-task-migration.yaml`](.github/workflows/check-task-migration.yaml)
workflow and the associated [`hack/validate-migration.sh`](hack/validate-migration.sh) script.

To test:
1. uncomment the code in [`task/check-task-migration-test/0.2/migrations/0.2.sh`](task/check-task-migration-test/0.2/migrations/0.2.sh).
This should cause the failure [`hack/validate-migration.sh`](hack/validate-migration.sh), in the ShellCheck phase.

2. Remove the [`task/check-task-migration-test/0.2/MIGRATION.md`](task/check-task-migration-test/0.2/MIGRATION.md) file. This should cause a following failure in the "Check MIGRATION.md" stage of the [`.github/workflows/check-task-migration.yaml`](.github/workflows/check-task-migration.yaml) workflow:
```
Missing file task/check-task-migration-test/0.2/MIGRATION.md
```

## Workspaces
|name|description|optional|
|---|---|---|
|source|Workspace with the source code (at subpath /source)|false|
