# 🏗️ Shared CI for Konflux Task repos

This repo provides the shared scripts and CI workflows crucial for developing
Konflux Tasks.

To include the shared CI in your repo, see the [onboarding](#-onboarding) steps.

For further post-onboarding information, see the [SHARED-CI.md](./SHARED-CI.md)
doc in this repo or the copy brought in by the onboarding process to your own repo.

## 🚀 Onboarding

Pre-requisites:

- Install [`cruft`][cruft]

> [!TIP]
> If you have [`uv`][uv] installed, you can run `uvx cruft` and don't need
> to install `cruft` itself.

Process:

1. Check that the onboarding process will not destroy your local changes

   ```bash
   git status --short .github/ hack/ SHARED-CI.md
   ```

   This command will print all the files the process could affect.
   Commit any changes that you don't want to lose.

2. Run the `cruft create` command

   ```bash
   cruft create https://github.com/konflux-ci/task-repo-shared-ci --no-input --overwrite-if-exists
   ```

3. Restore the files that got deleted in the process

   ```bash
   git diff --diff-filter=D --name-only -- .github/ hack/ | xargs git checkout --
   ```

4. If you use [Renovate], create/update your renovate.json using the
   [`hack/renovate-ignore-shared-ci.sh`](hack/renovate-ignore-shared-ci.sh) script:

   ```bash
   hack/renovate-ignore-shared-ci.sh
   ```

5. Commit the files brought in during the onboarding

   ```bash
   git add .cruft.json renovate.json .github/ hack/ SHARED-CI.md
   git commit
   ```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 Why use [cruft]

What we need to share:

- `.github/workflows/*` files
- scripts used for `.github/workflows/*` **and** for local development

### Options considered

#### GitHub actions

Maintain a set of GitHub actions that task repos can reuse.

❌ Problems:

- Each repo still needs its own workflow files referencing the actions
- The repos don't get locally runnable scripts
  - [nektos/act] could help to some extent, but it brings more complexity

#### Git submodule

Include the workflow files and scripts as a git submodule.

❌ Problems:

- It's not possible to run workflows from git submodules ([github#10892])

#### Reusable workflows

Maintain a set of [reusable workflows] that task repos can call.

❌ Problems:

- Same as the [GitHub actions](#github-actions) approach

#### GitHub template repo

Create a [template repo], generate task repos from the template.
For existing repos, they would have to copy-paste the files directly.

❌ Problems:

- The shared files get copied once and then never updated
- No good way to evolve functionality over time, introduce new checks etc.

#### cruft

Create a [cookiecutter] template, include the template in task repos, use [cruft]
to keep it up to date.

✅ What works:

- Task repos include the workflow files and scripts from the template directly
- The repos get a solid mechanism for keeping the shared CI up to date
- It's straightforward to test CI changes directly in the target repo

❔ What may not:

- To some extent, it's possible to patch the shared files and have the patches
  respected during updates
  - Task repo maintainers may decide not to contribute to the shared templates and
    overly rely on local patches (we don't want that)
  - Making local patches increases the chance of merge conflicts during the update
    (which may be good, because it discourages the above)

[cruft]: https://cruft.github.io/cruft
[nektos/act]: https://github.com/nektos/act
[github#10892]: https://github.com/orgs/community/discussions/10892
[reusable workflows]: https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows#calling-a-reusable-workflow
[template repo]: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository
[cookiecutter]: https://cookiecutter.readthedocs.io/en/stable/
[uv]: https://docs.astral.sh/uv/
[Renovate]: https://docs.renovatebot.com/
