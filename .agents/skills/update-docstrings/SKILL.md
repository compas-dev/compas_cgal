---
name: update-docstrings
description: Modernize compas_cgal docstrings while preserving Python, nanobind, CGAL, and plugin behavior.
---

# Update compas_cgal docstrings

Apply the repository-wide rules in `AGENTS.md`, especially **Nanobind Boundary**, **Documentation and Public API**, and **Tests and Validation**.

## Requirements

- Use MkDocs-compatible NumPy-style docstrings with Markdown.
- Omit parameter types already present in signatures and keep canonical Python types in `Returns` sections.
- Document required array shape, dtype, and layout when they are part of the native contract; do not imply that annotations enforce them.
- Document ownership or copying when returned arrays or native containers make it observable.
- Omit `Returns` for functions returning `None` and remove empty sections.
- Replace Sphinx roles, directives, citations, and math syntax in touched docstrings with Markdown equivalents.
- Keep examples executable and do not change runtime behavior.
- Leave a blank line before the closing quotes of multiline docstrings.

## Validation

Run focused doctests where applicable, Ruff on touched Python files, relevant MkDocs builds, and `git diff --check`.
