"""Shared array conversion at native triangle-mesh boundaries."""

import operator

import numpy as np
from compas.typing import Float64Array
from compas.typing import Int32Array
from compas.typing import VerticesFaces

from .types import PolylinesNumpy
from .types import VerticesFacesNumpy


def as_native_mesh(mesh: VerticesFaces, name: str) -> VerticesFacesNumpy:
    """Convert structural mesh buffers to the representation required by CGAL."""
    vertices, faces = _as_native_mesh(mesh, name)
    if faces.shape[1] != 3:
        raise ValueError(f"{name} faces should have shape (M, 3).")
    return vertices, faces


def as_native_polygon_mesh(mesh: VerticesFaces, name: str) -> tuple[Float64Array, Int32Array]:
    """Convert fixed-width polygon buffers to the representation required by CGAL."""
    vertices, faces = _as_native_mesh(mesh, name)
    if faces.shape[1] < 3:
        raise ValueError(f"{name} faces should contain at least three indices.")
    return vertices, faces


def _as_native_mesh(mesh: VerticesFaces, name: str) -> tuple[Float64Array, Int32Array]:
    try:
        vertices, faces = mesh
    except (TypeError, ValueError):
        raise TypeError(f"{name} should be a (vertices, faces) pair.")

    vertices = np.ascontiguousarray(vertices, dtype=np.float64)
    faces = as_native_indices(faces, f"{name} faces", dimensions=2)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError(f"{name} vertices should have shape (N, 3).")
    if not np.isfinite(vertices).all():
        raise ValueError(f"{name} vertices should be finite.")
    if faces.size:
        minimum = faces.min()
        maximum = faces.max()
        if minimum < 0 or maximum >= len(vertices):
            raise IndexError(f"{name} face index is out of range.")
    return vertices, faces


def as_native_indices(values: object, name: str, dimensions: int) -> Int32Array:
    """Normalize non-boolean `SupportsIndex` values for a native call."""
    try:
        array = np.asarray(values)
    except ValueError as error:
        raise ValueError(f"{name} should be a regular {dimensions}-dimensional index array.") from error
    if array.ndim != dimensions:
        raise ValueError(f"{name} should be a {dimensions}-dimensional index array.")

    indices = []
    for value in array.flat:
        if isinstance(value, (bool, np.bool_)):
            raise TypeError(f"{name} should contain non-boolean integer indices.")
        try:
            indices.append(operator.index(value))
        except TypeError as error:
            raise TypeError(f"{name} should contain values implementing SupportsIndex.") from error

    info = np.iinfo(np.int32)
    if any(index < info.min or index > info.max for index in indices):
        raise OverflowError(f"{name} exceed the index range supported by CGAL.")
    return np.asarray(indices, dtype=np.int32).reshape(array.shape)


def validate_native_mesh(result: VerticesFacesNumpy, operation: str) -> VerticesFacesNumpy:
    """Check the shape of a native triangle-mesh result."""
    vertices, faces = result
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise RuntimeError(f"CGAL {operation} result vertices should have shape (N, 3).")
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise RuntimeError(f"CGAL {operation} result faces should have shape (M, 3).")
    if faces.size and (faces.min() < 0 or faces.max() >= len(vertices)):
        raise RuntimeError(f"CGAL {operation} result contains an out-of-range face index.")
    return vertices, faces


def validate_polylines(result: PolylinesNumpy, operation: str) -> PolylinesNumpy:
    """Check the shape of native polyline results."""
    for points in result:
        if points.ndim != 2 or points.shape[1] != 3:
            raise RuntimeError(f"CGAL {operation} result polylines should have shape (N, 3).")
    return result
