# Installation

## Stable

Stable releases of :mod:`compas_cgal` can be installed via ``conda-forge``.

```bash
conda create -n cgal -c conda-forge compas_cgal
```

Several examples use the COMPAS Viewer for visualisation.
To install `compas_viewer` in the same environment

```bash
conda activate cgal
conda install compas_viewer
```

## From source

Building from source compiles the native CGAL extensions with CMake, `scikit-build-core` and `nanobind`.
The first build can take several minutes. A C++ compiler is required, see the
[compiler requirements](devguide/compiler.md). Clone the repository first:

```bash
git clone https://github.com/compas-dev/compas_cgal.git
cd compas_cgal
```

Use [uv](https://docs.astral.sh/uv/) to reproduce the locked development
environment in `.venv`:

[uv](https://docs.astral.sh/uv/) sets up an isolated environment in `.venv`.

```bash
uv sync --frozen --group dev
```

The editable native extension is built by the sync. Rebuild it after C++ changes
with `uv sync --reinstall-package compas-cgal`. CMake, Ninja, nanobind, and the
Python build backend are locked development dependencies. A platform C++20
compiler remains an explicit system prerequisite.

Direct tool commands are authoritative. Existing contributor and shared-action
workflows may continue to use the thin Invoke facade during migration:

```bash
uv run invoke test
uv run invoke docs
uv run invoke check
```

These commands do not hide native provisioning: the initial build and every C++
rebuild still use the explicit `uv sync` commands above.

The dependency groups in `pyproject.toml` are the single dependency source of
truth. Until the compatible COMPAS 3 release is available from PyPI, uv resolves
the exact coordinated COMPAS candidate recorded in `[tool.uv.sources]`. A clean
checkout therefore remains reproducible without depending on a sibling
repository. For coordinated local development, use an uncommitted uv override
rather than changing the canonical lock.

## Dev Install

To contribute, see [the developer guide](devguide.md).

## Building the documentation

Install the docs toolchain once:

```bash
uv sync --frozen --group docs
```

Build the site (always works, no network/socket needed):

```bash
uv run mkdocs build --strict
```

Output is written to `./site/`. Open `site/index.html` directly, or serve it locally:

```bash
uv run mkdocs serve -a 127.0.0.1:49500
```

A high port like `49500` avoids the Windows reserved-port ranges (Hyper-V/WSL2) that cause `PermissionError: [WinError 10013]` on the default port 8000.

Pull requests build the documentation in strict mode. Versioned deployment is a
release step and uses the already validated source revision.
