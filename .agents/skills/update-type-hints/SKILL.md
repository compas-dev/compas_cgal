---
name: update-type-hints
description: Add, modernize, or review Python and nanobind type information in compas_cgal without changing native boundary behavior.
---

# Update compas_cgal type hints

Apply the repository-wide rules in `AGENTS.md`, especially **Python and Typing**, **Nanobind Boundary**, and **Tests and Validation**.

## Requirements

- Use Python 3.12 syntax, built-in generics, PEP 604 unions, and `Self` where appropriate.
- Inspect the corresponding C++ binding before changing a wrapper annotation.
- Model values accepted by the existing runtime API. Do not add conversions or validation merely to satisfy a type checker.
- Use COMPAS structural types at public boundaries and precise NumPy types for arrays crossing into nanobind.
- Update the matching `.pyi` file with every native signature change.
- Preserve dtype, dimensions, layout, ownership, defaults, return containers, indexing, orientation, and exception behavior.
- Prefer protocols, aliases, and overloads over broad `Any`, casts, or concrete runtime checks.
- Keep plugin registration modules free of native imports.

## Validation

Run focused Pyright and Ruff checks, relevant boundary tests against a built editable extension, and `git diff --check`. When native signatures change, also compare runtime signatures or generated stubs with the checked-in stubs.
