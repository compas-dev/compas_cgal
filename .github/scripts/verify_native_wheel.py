"""Verify that a COMPAS CGAL wheel contains every typed native module."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile

NATIVE_MODULES = (
    "_booleans",
    "_geodesics",
    "_intersections",
    "_isolines",
    "_measure",
    "_meshing",
    "_polylines",
    "_reconstruction",
    "_skeletonization",
    "_slicer",
    "_straight_skeleton_2",
    "_subdivision",
    "_triangulation",
    "_types_std",
)


def verify_wheel(wheel: Path) -> None:
    """Verify typed-package files and native extensions in ``wheel``."""
    with ZipFile(wheel) as archive:
        names = set(archive.namelist())

    required = {"compas_cgal/py.typed"}
    required.update(f"compas_cgal/{module}.pyi" for module in NATIVE_MODULES)
    missing = sorted(required.difference(names))
    if missing:
        raise SystemExit(f"{wheel} is missing typed-package files: {missing}")

    missing_extensions = []
    for module in NATIVE_MODULES:
        prefix = f"compas_cgal/{module}."
        if not any(name.startswith(prefix) and name.endswith((".so", ".pyd")) for name in names):
            missing_extensions.append(module)
    if missing_extensions:
        raise SystemExit(f"{wheel} is missing native extensions: {missing_extensions}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheels", nargs="+", type=Path)
    args = parser.parse_args()
    for wheel in args.wheels:
        verify_wheel(wheel)


if __name__ == "__main__":
    main()
