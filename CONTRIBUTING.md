# Contributing

## Understanding the repository

* [`{{cookiecutter.repo_root}}/`]({{cookiecutter.repo_root}}/)
  * This is the core of the repo. Here we define all the files that we want
    to share across Konflux Task repositories.
* [`{{cookiecutter.repo_root}}/SHARED-CI.md`]({{cookiecutter.repo_root}}/SHARED-CI.md)
  * Documents (almost) everything that someone who [onboards](README.md#-onboarding)
    their repo to the shared CI might want to know. Gets copied to their repo during
    the onboarding.
* [`cookiecutter.json`](cookiecutter.json)
  * This is where we configure how templates should get rendered when someone onboards
  * `"repo_root": "."`
    * A trick to get around a [Cookiecutter] limitation. Normally, Cookiecutter
      will not apply templates to the repository root. Templates have to be under
      a `{{cookiecutter.<some_variable>}}` directory. But, by setting that variable
      to `.`, we trick Cookiecutter into applying the templates to the repo root.
  * `"_copy_without_render": ["*"]`
    * Cookiecutter uses Jinja templating to render the templates. Jinja's `{{` braces
      would clash both with Bash syntax and with GitHub workflow syntax. We disable
      all rendering so that we don't have to bother with that.
  * You may have noticed that we kind of work around the entirety of Cookiecutter
    by configuring it this way. Why use it at all then? Single reason: so that
    those who onboard can get automated updates using [`cruft`][cruft] (if you'd
    like to know more, see [docs/why-cruft.md](docs/why-cruft.md)).
* [`.github/`](.github/)
  * Your standard `.github` directory for workflows and related resources
  * Most of the files are copy-pasted from `{{cookiecutter.repo_root}}/`
    * Because we want to test the behavior of the shared workflows in this repo itself
  * Note: the copy-pasted ones will have a `# <TEMPLATED FILE!>` comment
* [`.github/workflows/check-generated-content.yaml`](.github/workflows/check-generated-content.yaml)
  * A workflow specific to this repo, not included in the Cookiecutter template
  * Uses [`hack/template_notice.py`](hack/template_notice.py) to verify that all
    the files in `{{cookiecutter.repo_root}}/` have a `# <TEMPLATED FILE!>` comment
  * Uses [`hack/selfupdate.sh`](hack/selfupdate.sh) to verify that all the files
    in `{{cookiecutter.repo_root}}/` are copied to the actual repo root
* [`hack/`](hack/)
  * Scripts for `.github` workflows and for local development
  * Most of them are copy-pasted from `{{cookiecutter.repo_root}}/`
    * Because the workflows expect them to be in `./hack/`
  * Note: the copy-pasted ones will have a `# <TEMPLATED FILE!>` comment
* [`task/`](task/)
  * Example Tekton Tasks that don't do anything useful
  * Their purpose is to:
    * Make it possible to test the behavior of the shared workflows and scripts
      directly in this repo
    * Provide an example of the repository structure that the workflows and scripts
      expect
* [`tests/`](tests/)
  * Tests for the scripts in `hack/`

## Typical development workflow

1. Edit/add some files inside `{{cookiecutter.repo_root}}/`
2. Run `hack/template_notice.py fix` to add the `# <TEMPLATED FILE!>` comments
3. Run `hack/selfupdate.sh` to copy the changes to the repo root
4. Edit/add some files in the `task/` directory to test your changes
5. If possible, add automated tests for your changes
6. Open a PR
7. Get it reviewed and merged 🎉

## Testing

Set up Python virtualenv for tests written in Python:

```bash
# Python scripts should support python>=3.11, test with 3.11
make PYTHON_VERSION=3.11 venv
```

* If you don't have Python 3.11 installed, testing with your current python should be fine

  ```bash
  make venv
  ```

Run tests:

```bash
make test
```

[Cookiecutter]: https://cookiecutter.readthedocs.io/en/stable/
[cruft]: https://cruft.github.io/cruft
