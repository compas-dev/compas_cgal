"""Shared array conversion at native triangle-mesh boundaries."""

import numpy as np

from .types import PolylinesNumpy
from .types import VerticesFaces
from .types import VerticesFacesNumpy


def as_native_mesh(mesh: VerticesFaces, name: str) -> VerticesFacesNumpy:
    """Convert structural mesh buffers to the representation required by CGAL."""
    try:
        vertices, faces = mesh
    except (TypeError, ValueError):
        raise TypeError(f"{name} should be a (vertices, triangles) pair.")

    vertices = np.ascontiguousarray(vertices, dtype=np.float64)
    faces = np.ascontiguousarray(faces, dtype=np.int64)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError(f"{name} vertices should have shape (N, 3).")
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError(f"{name} faces should have shape (M, 3).")
    if not np.isfinite(vertices).all():
        raise ValueError(f"{name} vertices should be finite.")
    if faces.size:
        minimum = faces.min()
        maximum = faces.max()
        info = np.iinfo(np.int32)
        if minimum < info.min or maximum > info.max:
            raise OverflowError(f"{name} face indices exceed the range supported by CGAL.")
        if minimum < 0 or maximum >= len(vertices):
            raise IndexError(f"{name} face index is out of range.")
    return vertices, np.ascontiguousarray(faces, dtype=np.int32)


def validate_native_mesh(result: VerticesFacesNumpy, operation: str) -> VerticesFacesNumpy:
    """Check the shape of a native triangle-mesh result."""
    vertices, faces = result
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise RuntimeError(f"CGAL {operation} result vertices should have shape (N, 3).")
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise RuntimeError(f"CGAL {operation} result faces should have shape (M, 3).")
    return vertices, faces


def validate_polylines(result: PolylinesNumpy, operation: str) -> PolylinesNumpy:
    """Check the shape of native polyline results."""
    for points in result:
        if points.ndim != 2 or points.shape[1] != 3:
            raise RuntimeError(f"CGAL {operation} result polylines should have shape (N, 3).")
    return result
