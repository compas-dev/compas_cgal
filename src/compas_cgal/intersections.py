from __future__ import annotations

from compas.typing import VerticesFaces

from compas_cgal import _intersections
from compas_cgal import _types_std  # noqa: F401

from ._mesh import as_native_mesh
from ._mesh import validate_polylines
from .types import PolylinesNumpy

__all__ = ["intersection_mesh_mesh"]


def intersection_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> PolylinesNumpy:
    """Compute the intersection of two triangle meshes.

    Parameters
    ----------
    A
        Mesh A.
    B
        Mesh B.

    Returns
    -------
    PolylinesNumpy
        A list of intersection polylines, with each polyline an array of points.

    Examples
    --------
    >>> from compas.geometry import Box, Frame, Polyline, Sphere, intersection_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, frame=Frame(point=[1, 1, 1]))

    >>> A = box.to_tessellation().to_vertices_and_triangles()
    >>> B = sphere.to_tessellation(nu=32, nv=32).to_vertices_and_triangles()

    >>> result = intersection_mesh_mesh(A, B)
    >>> polylines = [Polyline(points) for points in result]

    """
    VA, FA = as_native_mesh(A, "A")
    VB, FB = as_native_mesh(B, "B")

    pointsets = _intersections.intersection_mesh_mesh(VA, FA, VB, FB)

    return validate_polylines(pointsets, "mesh intersection")
