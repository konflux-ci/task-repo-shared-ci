#!/usr/bin/env python3
"""Integration tests for hack/check-compute-resources.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest
import yaml


def _write(path: Path, files: dict[str, str]) -> None:
    for fp, content in files.items():
        p = path / fp
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


def _cr(
    mem_req: str | None = "256Mi",
    mem_lim: str | None = "256Mi",
    cpu_req: str | None = "100m",
    cpu_lim: str | None = None,
) -> dict:
    cr: dict = {"limits": {}, "requests": {}}
    if mem_lim:
        cr["limits"]["memory"] = mem_lim
    if cpu_lim:
        cr["limits"]["cpu"] = cpu_lim
    if cpu_req:
        cr["requests"]["cpu"] = cpu_req
    if mem_req:
        cr["requests"]["memory"] = mem_req
    return cr


def _step(name: str = "build", cr: dict | None = None, field: str = "computeResources") -> dict:
    s: dict = {"name": name, "image": "test:latest", "script": "echo hi"}
    if cr is not None:
        s[field] = cr
    return s


def _task(
    name: str = "hello",
    api: str = "tekton.dev/v1",
    steps: list[dict] | None = None,
    sidecars: list[dict] | None = None,
    step_template_cr: dict | None = None,
) -> str:
    field = "resources" if api.endswith("/v1beta1") else "computeResources"
    if steps is None:
        steps = [_step(cr=_cr(), field=field)]
    spec: dict = {"steps": steps}
    if step_template_cr is not None:
        spec["stepTemplate"] = {field: step_template_cr}
    if sidecars:
        spec["sidecars"] = sidecars
    doc = {"apiVersion": api, "kind": "Task", "metadata": {"name": name}, "spec": spec}
    return yaml.dump(doc, default_flow_style=False, sort_keys=False)


def _exc(entries: list[dict]) -> str:
    return yaml.dump({"exceptions": entries}, default_flow_style=False)


class _Repo:
    def __init__(self, path: Path):
        self.path = path
        self._git("init")
        (path / ".git" / "config").write_text(dedent("""\
            [user]
                name = Test
                email = t@t
            [commit]
                gpgsign = false
            [core]
                hooksPath = /dev/null
        """))
        self._git("branch", "-M", "main")
        self._git("commit", "--allow-empty", "-m", "init")

    def _git(self, *a: str) -> None:
        subprocess.run(["git", *a], cwd=self.path, capture_output=True, text=True, check=True)

    def add(self, files: dict[str, str]) -> None:
        _write(self.path, files)
        self._git("add", ".")
        self._git("commit", "-m", "add")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    src = Path(__file__).parent.parent / "hack" / "check-compute-resources.py"
    (tmp_path / "hack").mkdir()
    (tmp_path / "hack" / "check-compute-resources.py").write_text(src.read_text())
    return tmp_path


def _run(repo: Path, *, fail: bool = False) -> subprocess.CompletedProcess[str]:
    r = subprocess.run([sys.executable, "hack/check-compute-resources.py"], cwd=repo, capture_output=True, text=True)
    if not fail and r.returncode != 0:
        pytest.fail(f"unexpected failure:\nstdout: {r.stdout}\nstderr: {r.stderr}")
    return r


def _setup(repo: Path, files: dict[str, str]) -> None:
    _Repo(repo).add(files)


# --- compliant ---

def test_compliant(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task()})
    r = _run(repo)
    assert r.returncode == 0
    assert "All scanned task files satisfy computeResources rules." in r.stdout


def test_cpu_limit_equal(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step(cr=_cr(cpu_lim="100m"))])})
    assert _run(repo).returncode == 0


def test_sidecar_compliant(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(sidecars=[_step("logger", _cr())])})
    assert _run(repo).returncode == 0


def test_v1beta1(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(api="tekton.dev/v1beta1", steps=[_step(cr=_cr(), field="resources")])})
    assert _run(repo).returncode == 0


# --- missing resources ---

def test_missing_resources(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step()])})
    r = _run(repo, fail=True)
    assert "missing computeResources" in r.stderr


def test_sidecar_missing(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(sidecars=[_step("logger")])})
    r = _run(repo, fail=True)
    assert "sidecars 'logger': missing computeResources" in r.stderr


# --- memory ---

def test_memory_mismatch(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step(cr=_cr(mem_req="256Mi", mem_lim="512Mi"))])})
    r = _run(repo, fail=True)
    assert "memory request (256Mi) must equal memory limit (512Mi)" in r.stderr


def test_missing_memory_request(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step(cr=_cr(mem_req=None))])})
    r = _run(repo, fail=True)
    assert "missing memory request" in r.stderr


def test_missing_memory_limit(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step(cr=_cr(mem_lim=None))])})
    r = _run(repo, fail=True)
    assert "missing memory limit" in r.stderr


# --- cpu ---

def test_missing_cpu_request(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step(cr=_cr(cpu_req=None))])})
    r = _run(repo, fail=True)
    assert "missing cpu request" in r.stderr


def test_cpu_limit_mismatch(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step(cr=_cr(cpu_lim="500m"))])})
    r = _run(repo, fail=True)
    assert "cpu limit (500m) must equal cpu request (100m)" in r.stderr


# --- stepTemplate ---

def test_step_template_inherits(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(steps=[_step()], step_template_cr=_cr())})
    assert _run(repo).returncode == 0


def test_step_template_override(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(
        steps=[_step(cr=_cr(mem_req="256Mi", mem_lim="256Mi", cpu_req="100m"))],
        step_template_cr=_cr(mem_req="128Mi", mem_lim="999Mi", cpu_req="50m"),
    )})
    assert _run(repo).returncode == 0


def test_step_template_partial_merge(repo: Path) -> None:
    _setup(repo, {"task/hello/hello.yaml": _task(
        steps=[_step(cr=_cr(cpu_req=None))],
        step_template_cr={"requests": {"cpu": "100m"}},
    )})
    assert _run(repo).returncode == 0


# --- exceptions ---

def test_exception_skips_step(repo: Path) -> None:
    _setup(repo, {
        "task/hello/hello.yaml": _task(steps=[_step()]),
        ".github/.compute-resources-exceptions.yaml": _exc([{"path": "task/hello/hello.yaml", "steps": ["build"]}]),
    })
    assert _run(repo).returncode == 0


def test_exception_skips_sidecar(repo: Path) -> None:
    _setup(repo, {
        "task/hello/hello.yaml": _task(sidecars=[_step("logger")]),
        ".github/.compute-resources-exceptions.yaml": _exc([{"path": "task/hello/hello.yaml", "sidecars": ["logger"]}]),
    })
    assert _run(repo).returncode == 0


def test_stale_exception_missing_step(repo: Path) -> None:
    _setup(repo, {
        "task/hello/hello.yaml": _task(),
        ".github/.compute-resources-exceptions.yaml": _exc([{"path": "task/hello/hello.yaml", "steps": ["nonexistent"]}]),
    })
    assert "does not exist; remove it" in _run(repo, fail=True).stderr


def test_stale_exception_now_compliant(repo: Path) -> None:
    _setup(repo, {
        "task/hello/hello.yaml": _task(),
        ".github/.compute-resources-exceptions.yaml": _exc([{"path": "task/hello/hello.yaml", "steps": ["build"]}]),
    })
    assert "now compliant; remove it" in _run(repo, fail=True).stderr


def test_stale_exception_file_gone(repo: Path) -> None:
    _setup(repo, {
        "task/hello/hello.yaml": _task(),
        ".github/.compute-resources-exceptions.yaml": _exc([{"path": "task/gone/gone.yaml", "steps": ["x"]}]),
    })
    assert "not a scanned task file; remove it" in _run(repo, fail=True).stderr


def test_root_exceptions_fallback(repo: Path) -> None:
    _setup(repo, {
        "task/hello/hello.yaml": _task(steps=[_step()]),
        ".compute-resources-exceptions.yaml": _exc([{"path": "task/hello/hello.yaml", "steps": ["build"]}]),
    })
    assert _run(repo).returncode == 0


# --- non-task files ---

def test_skip_non_task_yaml(repo: Path) -> None:
    _setup(repo, {
        "task/hello/hello.yaml": _task(),
        "task/hello/tests/test-hello.yaml": "kind: Pipeline\n",
        "task/hello/kustomization.yaml": "resources: []\n",
    })
    assert _run(repo).returncode == 0


def test_empty_repo(repo: Path) -> None:
    _setup(repo, {"README.md": "# empty\n"})
    assert _run(repo).returncode == 0


def test_versioned_subdir(repo: Path) -> None:
    _setup(repo, {"task/hello/0.1/hello.yaml": _task()})
    assert _run(repo).returncode == 0
