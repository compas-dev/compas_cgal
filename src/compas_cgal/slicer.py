from collections.abc import Sequence

import numpy as np
from compas.geometry import Plane
from compas.geometry import Tessellation

from compas_cgal import _slicer  # type: ignore
from compas_cgal import _types_std  # noqa: F401  # type: ignore

from ._tessellation import as_native_tessellation
from .types import PolylinesNumpy


def slice_mesh_planes(mesh: Tessellation, planes: Sequence[Plane]) -> PolylinesNumpy:
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
    >>> mesh = sphere.tessellate(UVGrid(32, 32))

    >>> planes = [Plane([0, 0, z], [0, 0, 1.0]) for z in linspace(0.1, 1.9, 19)]

    >>> result = trimesh_slice(mesh, planes)
    >>> polylines = [Polyline(points) for points in result]

    """
    points, normals = zip(*planes)
    V, F = as_native_tessellation(mesh)
    P = np.array(points, dtype=np.float64, order="C")
    N = np.array(normals, dtype=np.float64, order="C")

    pointsets = _slicer.slice_mesh(V, F, P, N)
    return pointsets
