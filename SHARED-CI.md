<!--
<TEMPLATED FILE!>
This file comes from the templates at https://github.com/konflux-ci/task-repo-shared-ci.
Please consider sending a PR upstream instead of editing the file directly.
-->

# 🤝 Shared CI setup for Konflux Task repos

Some of the CI scripts and workflows in this repo come from the [task-repo-shared-ci]
template repo.

All the files that come from the template repo have a `<TEMPLATED FILE!>` comment
near the top to help identify them.

## 🍏 Updating the shared CI

Use [`cruft`][cruft] to update the shared CI files to the latest template:

```bash
cruft update --skip-apply-ask --allow-untracked-files
```

Don't forget to commit the `.cruft.json` changes as well to track which
version of the templates you have.

> [!TIP]
> If you have [`uv`][uv] installed, you can run `uvx cruft` and don't need
> to install `cruft` itself.

Your repo also has an automated workflow that periodically checks for updates and
sends automated PRs. See [Shared CI Updater](#shared-ci-updater) for more details.

## 🔧 Making changes

You can edit the shared CI files if necessary, but please consider sending PRs
for the upstream [task-repo-shared-ci] templates to reduce drift and so that
others can benefit from the changes as well.

`cruft` *will* try to respect your custom patches during the update process, but
as you make more local changes you increase the chance of merge conflicts.

## 🌲 Expected repository structure

The shared scripts and workflows expect this repository to follow the
[Tekton Catalog structure][tekton-catalog-structure].

They also introduce new elements and conventions, such as the `${task_name}-oci-ta`
directories for [Trusted Artifacts](#trusted-artifacts) tasks.

For details on how the `tests` directory is used, see [Task Integration Tests](#task-integration-tests).

Putting it all together, the structure is as follows:

```text
task                                    👈 all tasks go here
├── hello                               👈 the name of a task
│   └── 0.1                             👈 a specific version of the task
│       ├── hello.yaml                  👈 ${task_name}.yaml
│       └── README.md
│       └── tests                       👈 Test directory
│           └── test-hello.yaml         👈 Test - A Pipeline named test-*.yaml
│           └── test-hello-2.yaml       👈 Test case 2
│           └── pre-apply-task-hook.sh  👈 Optional hook
└── hello-oci-ta                        👈 ${task_name}-oci-ta for Trusted Artifacts
    └── 0.1
        ├── hello-oci-ta.yaml
        ├── README.md
        └── recipe.yaml                 👈 triggers auto-generation of the task yaml
```

## ☑️ CI workflows

### Checkton

- script: [`hack/checkton-local.sh`](hack/checkton-local.sh)
  - Allows running checkton locally.
- workflow: [`.github/workflows/checkton.yaml`](.github/workflows/checkton.yaml)
  - Runs ShellCheck on scripts embedded in YAML files.

Checkton is used to lint shell scripts embedded in YAML files (primarily Tekton files). 
It does so by running ShellCheck. For more details, see the [checkton project](https://github.com/chmeliik/checkton)

### Kustomize Build

- script: [`hack/build-manifests.sh`](hack/build-manifests.sh)
  - Generates task manifest YAML files from Kustomize definitions (kustomize.yaml, patch.yaml)
- workflow: [`.github/workflows/check-kustomize-build.yaml`](.github/workflows/check-kustomize-build.yaml)
  - Checks if all task manifests are up to date (no rebuild required).

With Kustomize, Task manifests are generated and kept consistent across the
repository by composing base definitions (kustomize.yaml) with patches (patch.yaml).
This ensures that all Task YAML manifests are reproducible and remain in sync 
with their source definitions.

When authoring or modifying a Task, contributors should update the corresponding
Kustomize files and regenerate the manifests rather than editing the YAML directly.
Use [`hack/build-manifests.sh`](hack/build-manifests.sh) to regenerate the manifests.

### Trusted Artifacts

- script: [`hack/generate-ta-tasks.sh`](hack/generate-ta-tasks.sh)
  - Generates Trusted Artifacts variants of Tasks. See below for more details.
- workflow: [`.github/workflows/check-ta.yaml`](.github/workflows/check-ta.yaml)
  - Checks that the Trusted Artifacts variants are up to date with their base Tasks.

With Trusted Artifacts (TA), Tasks share files via the use of archives stored in
an image repository and not using attached storage (PersistentVolumeClaims). This
has performance and usability benefits. For more details, see
[ADR36](https://konflux-ci.dev/architecture/ADR/0036-trusted-artifacts.html).

When authoring a Task that needs to share or use files from another Task, the
task author can opt to include the Trusted Artifact variant, by convention in
the `${task_name}-oci-ta` directory. This is necessary for the Task to be usable
in Pipelines that make use of Trusted Artifacts.

To author a Trusted Artifacts variant of a Task, create the `${task_name}-oci-ta`
directory, define a [`recipe.yaml`][recipe.yaml] inside the directory and generate
the TA variant using the [`hack/generate-ta-tasks.sh`](hack/generate-ta-tasks.sh)
script. See the [trusted-artifacts generator] README for more details.

### Shared CI Updater

- workflow: [`.github/workflows/update-shared-ci.yaml`](.github/workflows/update-shared-ci.yaml)

Periodically (every Sunday, by default) checks for updates in the [task-repo-shared-ci]
templates and sends automated PRs.

You can also trigger it manually from the Actions tab of your repo.

> [!NOTE]
> If you've made custom edits to your shared CI files, then the update process
> can encounter merge conflicts. When that happens, the workflow will send the
> PR anyway but with the merge conflicts included. The PR will be in draft state
> and will include a caution note (like this one, but red) with instructions.
>
> If your repository uses Renovate for automated dependency updates, that may increase
> the chance of merge conflicts. See [Conflicts with Renovate](#conflicts-with-renovate)
> for the solution.

#### Required secrets

- `SHARED_CI_UPDATER_APP_ID` - the ID of the updater GitHub app
- `SHARED_CI_UPDATER_PRIVATE_KEY` - the private key for the updater GitHub app

These may already be set globally for your organization. If not, see the instructions
below.

#### Updater GitHub app

The update workflow uses the credentials of a GitHub app to create pull requests,
rather than the default [`GITHUB_TOKEN`][GITHUB_TOKEN]. There are two reasons:

1. PRs created using `GITHUB_TOKEN` cannot trigger `on: pull_request` or `on: push`
   workflows
2. It's not possible to grant `GITHUB_TOKEN` the permission to edit `.github/workflows/`
   files

Since the shared CI updater is *all about* workflows, it needs to use app credentials
to avoid those restrictions.

##### Set up the GitHub app

1. Go to your organization or user settings on GitHub
2. Go to `Developer settings` > `GitHub Apps`
3. Click `New GitHub App`.
4. Configure the app:
   - **GitHub App name**: e.g. `${org_name} shared CI updater`
   - **Homepage URL**: <https://github.com/konflux-ci/task-repo-shared-ci/blob/main/SHARED-CI.md#shared-ci-updater>
   - **Webhook**: uncheck the `☑️ Active` option
   - **Permissions**:
     - **Repository permissions**:
        - Contents: `Read and write`
        - Pull requests: `Read and write`
        - Workflows: `Read and write`

##### Set the required secrets

1. On the app's settings page, copy the App ID number and generate a private key
2. Go to your organization settings (to set the secrets org-wide)
   or your repository settings
3. Go to `Secrets and variables` > `Actions`
4. Create the secrets
   - `SHARED_CI_UPDATER_APP_ID`: the App ID number
   - `SHARED_CI_UPDATER_PRIVATE_KEY`: plaintext content of the private key

#### Conflicts with Renovate

If your repository uses [Renovate], you could frequently get merge conflicts
during the Shared CI updates, because your repository gets GitHub Actions updates
at a different rate than the upstream [task-repo-shared-ci] repository.

To avoid that, your repo gets the [`hack/renovate-ignore-shared-ci.sh`](hack/renovate-ignore-shared-ci.sh)
script. Run this script during the [onboarding process] to add all the Shared CI
workflows to the [`ignorePaths`][renovate-ignorepaths] in your `renovate.json`.
Afterwards, any time the updater workflow brings in a new workflow file, it will
run the script to automatically update `renovate.json`.

This ensures your Shared CI workflows follow the GitHub Actions versions defined
in the upstream reposistory and avoids unnecessary merge conflicts.

### Task Integration Tests

- workflow: [`.github/workflows/run-task-tests.yaml`](.github/workflows/run-task-tests.yaml)
- script: [`.github/scripts/test_tekton_tasks.sh`](.github/scripts/test_tekton_tasks.sh)

This workflow automatically runs integration tests for any Tekton Task that is changed in a pull request. It spins up a temporary Kubernetes (Kind) cluster, deploys Tekton, and then executes the tests defined for the modified task.

#### How to Add a Test

1. Create a `tests` directory inside the task's versioned folder.  

2. Inside the `tests` directory, create a test file named `test-*.yaml` (for example, `test-hello.yaml`).  
   - The script **automatically** discovers tests based on this naming convention.  

3. The file must define a Tekton `kind: Pipeline` object.  

4. The Pipeline must declare a workspace named exactly `tests-workspace`.  
   - The test script will **automatically** provide storage for this workspace when it runs the pipeline.  

5. Optionally, add a `pre-apply-task-hook.sh` to the `tests` directory.

#### Example Structure

```plaintext
task
└── hello
    └── 0.1
        ├── hello.yaml
        └── tests                         👈 Test directory
            └── test-hello.yaml           👈 Test - A Pipeline named test-*.yaml
            └── test-hello-2.yaml         👈 Test case 2
            └── pre-apply-task-hook.sh    👈 Optional hook
```

#### Using a `pre-apply-task-hook.sh`

In some cases, your Task may require certain Kubernetes resources, like **Secrets** or **ConfigMaps**, to exist in the namespace before the Task itself is applied to the cluster.

To handle this, you can create an optional shell script named `pre-apply-task-hook.sh` and place it inside the `tests` directory.

If this script exists, the test runner will execute it **after creating the test namespace but before applying the task**. 
This allows the hook to dynamically modify the task's definition before it is applied. For example, to lower/remove resource requests and limits for a constrained test environment.

The script receives two arguments:

- `$1`: The path to a temporary copy of the task's YAML file.  
- `$2`: The name of the temporary test namespace where the test will run.  


<details>
<summary><b>Click to see an example <code>pre-apply-task-hook.sh</code></b></summary>

This script removes comupteResources and creates a dummy docker config secret that a task might need for registry authentication.

```bash
#!/bin/bash

# This script is called before applying the task to set up required resources.
TASK_COPY="$1"
TEST_NS="$2"

# Remove computeResources - allows tasks with high resource requirements
# to run in a resource-constrained test environment (e.g., local Kind cluster)
echo "Removing computeResources for task: $1"
yq -i eval '.spec.steps[0].computeResources = {}' $1
yq -i eval '.spec.steps[1].computeResources = {}' $1

# Create a dummy docker config secret for registry authentication
echo '{"auths":{}}' | kubectl create secret generic dummy-secret \
  --from-file=.dockerconfigjson=/dev/stdin \
  --type=kubernetes.io/dockerconfigjson \
  -n "$TEST_NS" --dry-run=client -o yaml | kubectl apply -f - -n "$TEST_NS"

echo "Pre-requirements setup complete for namespace: $TEST_NS"

```
</details>  

### Tekton Security Task Lint

To enforce secure CI practices, we lint all Tekton Tasks on every pull request using the `task-lint.yaml` workflow.

#### Purpose

This check **disallows using `$(params.*)` variable substitution directly within a `script` block** of a Tekton Task.

Using `$(params.*)` directly in a script creates a security flaw. Tekton performs a raw text replacement of the parameter placeholder before the script is executed. This means if a parameter's value contains malicious shell commands, they will be run, leading to **arbitrary code execution**.

For more details and guidance on fixing the issue, see the [Tekton recommendations](https://github.com/tektoncd/catalog/blob/main/recommendations.md#dont-use-interpolation-in-scripts-or-string-arguments)

### Tekton Task Validation

To ensure all Tekton Tasks are well-formed and valid, a `Check Tekton Tasks` workflow is executed on every pull request. This workflow serves as a safeguard to block invalid tasks from being merged, so we don’t risk breaking users.

#### If the Check Fails

- Open the workflow logs in GitHub Actions
- Look at the `Apply all Tasks` step
- The logs will show which Task file failed and the exact error

> [!NOTE]  
> The `setup-tektoncd` step may occasionally fail due to GitHub API `rate limits` (see [tektoncd/actions#9](https://github.com/tektoncd/actions/issues/9)).  
> This is a known issue and not related to your changes.  
>  
> The current workaround is to `re-run the workflow`.


[task-repo-shared-ci]: https://github.com/konflux-ci/task-repo-shared-ci
[onboarding process]: https://github.com/konflux-ci/task-repo-shared-ci?tab=readme-ov-file#-onboarding
[cruft]: https://cruft.github.io/cruft
[uv]: https://docs.astral.sh/uv/
[recipe.yaml]: https://github.com/konflux-ci/build-definitions/tree/main/task-generator/trusted-artifacts#configuration-in-recipeyaml
[trusted-artifacts generator]: https://github.com/konflux-ci/build-definitions/tree/main/task-generator/trusted-artifacts
[GITHUB_TOKEN]: https://docs.github.com/en/actions/concepts/security/github_token
[tekton-catalog-structure]: https://github.com/tektoncd/catalog?tab=readme-ov-file#catalog-structure
[Renovate]: https://docs.renovatebot.com/
[renovate-ignorepaths]: https://docs.renovatebot.com/configuration-options/#ignorepaths
