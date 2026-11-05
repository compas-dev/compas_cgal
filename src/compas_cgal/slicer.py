from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import numpy as np

from compas_cgal import _slicer  # type: ignore
from compas_cgal import _types_std  # noqa: F401  # type: ignore

from ._mesh import as_native_mesh
from ._mesh import validate_polylines
from .types import PolylinesNumpy

if TYPE_CHECKING:
    from compas._typing import TriangleMeshInput
    from compas.geometry._typing import PlaneType


def slice_mesh_planes(mesh: TriangleMeshInput, planes: Sequence[PlaneType]) -> PolylinesNumpy:
    """Slice a mesh by a list of planes.

    Parameters
    ----------
    mesh
        The mesh to slice.
    planes
        The slicing planes.

    Returns
    -------
    PolylinesNumpy
        A list of slice polylines, with each polyline an array of points.

    Examples
    --------
    >>> from compas.geometry import Plane, Polyline, Sphere, UVGrid, trimesh_slice  # doctest: +SKIP
    >>> from compas.itertools import linspace

    >>> sphere = Sphere(1.0, point=[0, 0, 1.0])
    >>> mesh = sphere.tessellate(UVGrid(32, 32)).to_vertices_and_triangles()

    >>> planes = [Plane([0, 0, z], [0, 0, 1.0]) for z in linspace(0.1, 1.9, 19)]

    >>> result = trimesh_slice(mesh, planes)
    >>> polylines = [Polyline(points) for points in result]

    """
    if len(planes) == 0:
        return []

    points, normals = zip(*planes)
    V, F = as_native_mesh(mesh, "mesh")
    P = np.ascontiguousarray(points, dtype=np.float64)
    N = np.ascontiguousarray(normals, dtype=np.float64)
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError("Plane points should have shape (N, 3).")
    if N.ndim != 2 or N.shape[1] != 3:
        raise ValueError("Plane normals should have shape (N, 3).")
    if not np.isfinite(P).all() or not np.isfinite(N).all():
        raise ValueError("Plane points and normals should be finite.")
    if np.any(np.linalg.norm(N, axis=1) == 0):
        raise ValueError("Plane normals should be nonzero.")

    pointsets = _slicer.slice_mesh(V, F, P, N)
    return validate_polylines(pointsets, "mesh slicing")
