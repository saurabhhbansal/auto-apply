"""Shared fixtures.

The convention the suite follows: tests drive the tools as commands over a throwaway
run folder and assert on the files that come back, never reaching into a tool's
internals. `config.py` is the exception, being a block of numbers whose shape is the
thing worth asserting.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

PDFLATEX = shutil.which("pdflatex")


def pytest_runtest_setup(item):
    """Skip pdflatex-dependent tests when there is no TeX installed.

    The suite has to stay runnable on a machine without TinyTeX, while still
    covering the compile where it matters.
    """
    if "needs_pdflatex" in item.keywords and PDFLATEX is None:
        pytest.skip("pdflatex is not on PATH (install TinyTeX; see docs/calibration.md)")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def config_module():
    """tools/config.py, imported by path — tools/ is not a package."""
    spec = importlib.util.spec_from_file_location(
        "auto_apply_config", REPO_ROOT / "tools" / "config.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def probe():
    """tests/calibration/probe.py.

    Imported for its Jinja2 environment and synthetic data, so the template-facing
    tests drive the template through one place.

    It stays the probe's own copy of that configuration now that tools/render.py
    exists, rather than being read from there: calibration isolates the template, so
    a bug in render.py must not be able to move a Page-budget constant. The two are
    held together by the template itself — a mismatch in the delimiters would leave
    one of them unable to render it at all.
    """
    calibration_dir = REPO_ROOT / "tests" / "calibration"
    spec = importlib.util.spec_from_file_location(
        "calibration_probe", calibration_dir / "probe.py"
    )
    module = importlib.util.module_from_spec(spec)
    # Must be in sys.modules *before* exec: @dataclass resolves annotations via
    # sys.modules[cls.__module__], and probe.py defines a dataclass.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _isolate_probe_output(request, tmp_path, monkeypatch):
    """Point the probe's compile output at tmp_path for every test that uses it.

    Without this the tests share tests/calibration/out/ and inherit each other's
    .aux files, which quietly changes what pdflatex emits — a build over an
    existing .aux is not the same build as a fresh one, so the byte-identical-PDF
    check passes or fails depending on what ran before it.
    """
    if "probe" not in request.fixturenames:
        return
    monkeypatch.setattr(request.getfixturevalue("probe"), "OUT_DIR", tmp_path)
