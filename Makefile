PYTHON_VERSION = ""
PYTHON = python$(PYTHON_VERSION)

.PHONY: selfupdate
selfupdate:
	hack/selfupdate.sh

.PHONY: fix-template-comments
fix-template-comments:
	hack/template_notice.py fix

.PHONY: venv
venv:
	if command -v uv; then \
		uv venv --python=$(PYTHON) --clear; \
		uv pip install -r requirements-test.txt; \
	else \
		if command -v virtualenv; then \
			virtualenv --python=$(PYTHON) --clear .venv; \
		else \
			$(PYTHON) -m venv --clear .venv; \
		fi; \
		.venv/bin/pip install -r requirements-test.txt; \
	fi

.PHONY: test
test:
	.venv/bin/pytest -vv
