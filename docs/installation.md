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

Then use any one of the following package managers.

### Using conda

```bash
conda env create -f environment.yml
conda activate cgal-dev
```

The environment installs CMake, COMPAS, the development and documentation requirements, and builds `compas_cgal` itself.

### Using uv

[uv](https://docs.astral.sh/uv/) sets up an isolated environment in `.venv`.

```bash
uv venv --python 3.12
uv pip install -r requirements.txt -r requirements-dev.txt -r requirements-viz.txt
uv pip install -e . --no-build-isolation
```

Activate the environment with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux.

### Using pixi

[pixi](https://pixi.sh/) resolves the conda and PyPI dependencies from the `[tool.pixi]` tables in `pyproject.toml`,
locked in `pixi.lock`, and builds the package in editable mode.

```bash
pixi install
pixi run test
```

Other tasks are `pixi run lint` and `pixi run format-check`, and `pixi shell` opens an activated shell.
The manifest is solved for `linux-64` and `osx-arm64` only, on Windows use conda or uv.

## Dev Install

To contribute, see [the developer guide](devguide.md).

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
