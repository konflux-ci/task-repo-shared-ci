# Migration from 0.1 to 0.2

The parameter `pipelinerun-name` was added.
This change will be added to build pipeline definition file automatically by script migrations/0.2.sh when MintMaker runs [pipeline-migration-tool](https://github.com/konflux-ci/pipeline-migration-tool). 

If that should fail for any reason, please follow these steps:
- Search for the task named `hello` in your pipeline definition file
- Add new param called `pipelinerun-name` with the value `$(context.pipelineRun.name)`
