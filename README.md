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
   [`hack/renovate-ignore-shared-ci.sh`](hack/renovate-ignore-shared-ci.sh) script
   (see [why](./SHARED-CI.md#conflicts-with-renovate)):

   ```bash
   hack/renovate-ignore-shared-ci.sh
   ```

5. Commit the files brought in during the onboarding

   ```bash
   git add .cruft.json renovate.json .github/ hack/ SHARED-CI.md
   git commit
   ```

Optional, but recommended: to receive periodic updates for the shared CI, set up
the [Shared CI Updater requirements](./SHARED-CI.md#updater-requirements).

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

[cruft]: https://cruft.github.io/cruft
[uv]: https://docs.astral.sh/uv/
[Renovate]: https://docs.renovatebot.com/
