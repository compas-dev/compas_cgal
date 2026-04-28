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

## Using uv

[uv](https://docs.astral.sh/uv/) can be used to set up an isolated environment and build `compas_cgal` from source.

```bash
uv venv --python 3.12
uv pip install -r requirements.txt -r requirements-dev.txt -r requirements-viz.txt
uv pip install -e . --no-build-isolation
```

Activate the environment with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux.

The editable install triggers a native CMake/CGAL build via `scikit-build-core` and `nanobind`, which can take several minutes on the first run.

## Dev Install

See [the developer guide](devguide.md).

## Building the documentation

Install the docs toolchain once:

```bash
pip install -r requirements-docs.txt
```

Build the site (always works, no network/socket needed):

```bash
mkdocs build
```

Output is written to `./site/`. Open `site/index.html` directly, or serve it locally:

```bash
mkdocs serve -a 127.0.0.1:49500
```

A high port like `49500` avoids the Windows reserved-port ranges (Hyper-V/WSL2) that cause `PermissionError: [WinError 10013]` on the default port 8000.

CI deploys via `mkdocs gh-deploy --force` on every push to `main` (`.github/workflows/docs.yml`).
