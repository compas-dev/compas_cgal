# Development Environment

The canonical development environment is managed by uv and recorded in
`uv.lock`.

```bash
uv sync --frozen --group dev
```

Run commands without activating the environment:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

The compatibility facade used by existing shared actions remains available as
`uv run invoke test`, `uv run invoke docs`, and `uv run invoke check`. Direct
tool commands above define the repository contract.

The dependency groups in `pyproject.toml` replace the former Conda environment
and requirements files. The `dev`, `docs`, and `viz` groups retain their
development, documentation, and visualization dependencies respectively.

The native extensions require a C++20 compiler. CMake, Ninja, nanobind, and the
Python build backend come from the lock. Rebuild after editing C++ with
`uv sync --reinstall-package compas-cgal`.
