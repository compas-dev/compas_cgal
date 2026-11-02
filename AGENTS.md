# COMPAS CGAL Agent Guide

## Scope and Principles

These instructions apply to the entire repository.

- Keep `compas_cgal` focused on CGAL integration through nanobind extension modules and small Python adapters.
- Follow the current contracts in the neighboring COMPAS source repository.
- Preserve unrelated working-tree changes and keep patches focused.
- Treat Python wrappers, nanobind bindings, type stubs, tests, and documentation as one public contract.
- Prefer the simplest implementation that preserves runtime behavior. Avoid speculative compatibility layers.

## Python and Typing

- Support Python 3.12 and newer, as declared in `pyproject.toml`.
- Use modern Python syntax, PEP 604 unions, built-in generics, and `Self` where appropriate.
- Annotate the values accepted by the runtime API. Do not add conversions or validation merely to satisfy a type checker.
- Use COMPAS structural aliases at public boundaries and precise NumPy types at the nanobind boundary.
- Prefer precise protocols, aliases, and overloads over broad `Any` or casts.
- Use `TYPE_CHECKING` for imports used only by annotations.
- Keep `src/compas_cgal/py.typed` and all native-module `.pyi` files packaged.
- Update a native stub whenever a nanobind function name, argument, default, return value, class, property, or overload changes.

## Nanobind Boundary

- Before changing a wrapper annotation, inspect the corresponding C++ binding and conversion path.
- Preserve accepted dtypes, dimensions, memory layout, ownership, indexing, orientation, defaults, exception behavior, and returned container types.
- Do not assume that a NumPy annotation enforces a shape. Document and test required shapes such as `N x 2`, `N x 3`, and triangular faces separately.
- Verify that returned arrays own their memory or keep their C++ owner alive.
- Keep native type-registration ordering explicit. Do not remove `_types_std` imports without verifying the affected converters.
- Test conversion failures at the Python boundary. Avoid sending malformed data into CGAL when it could trigger assertions or undefined behavior.

## Plugins

- Register plugins through the `compas.plugins` package entry points in `pyproject.toml`. Do not use legacy `__all_plugins__` discovery.
- Keep modules under `compas_cgal.plugins` lightweight. They must not import a nanobind extension during plugin discovery.
- Import public implementations inside plugin functions so native modules load only when an operation is invoked.
- Match the current COMPAS extension-point name, category, signature, and return contract. Use `pluggable_name` only when the local function name differs.
- Keep backend-specific operations as ordinary public functions when no COMPAS extension point exists.

## Documentation and Public API

- Define explicit `__all__` lists for direct public package modules.
- Write MkDocs/mkdocstrings-compatible NumPy-style docstrings using Markdown.
- Omit parameter types already present in signatures. Keep canonical Python types in `Returns` sections.
- Use backticks and Markdown links rather than Sphinx roles or directives.
- Except for single-line docstrings, leave a blank line before closing quotes.

## Tests and Validation

- Build or rebuild the editable nanobind extensions before tests that exercise native code.
- Run the smallest relevant tests first, then broaden validation in proportion to risk.
- For typing changes, run Pyright against the built package and Ruff on touched Python files.
- For plugin changes, test discovery from installed distribution metadata and verify that discovery does not import native extension modules.
- For native-boundary changes, test dtype, shape, contiguity, ownership, and exception behavior as applicable.
- Always run `git diff --check`.
