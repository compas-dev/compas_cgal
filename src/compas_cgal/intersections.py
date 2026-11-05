from __future__ import annotations

from typing import TYPE_CHECKING

from compas_cgal import _intersections  # type: ignore
from compas_cgal import _types_std  # type: ignore

from ._mesh import as_native_mesh
from ._mesh import validate_polylines
from .types import PolylinesNumpy

if TYPE_CHECKING:
    from compas._typing import TriangleMeshInput


def intersection_mesh_mesh(
    A: TriangleMeshInput,
    B: TriangleMeshInput,
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
    >>> from compas.geometry import Box, Native, Polyline, Sphere, UVGrid, intersection_mesh_mesh  # doctest: +SKIP

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.tessellate(Native()).to_vertices_and_triangles()
    >>> B = sphere.tessellate(UVGrid(32, 32)).to_vertices_and_triangles()

    >>> result = intersection_mesh_mesh(A, B)
    >>> polylines = [Polyline(points) for points in result]

    """
    VA, FA = as_native_mesh(A, "A")
    VB, FB = as_native_mesh(B, "B")

    pointsets: _types_std.VectorRowMatrixXd = _intersections.intersection_mesh_mesh(VA, FA, VB, FB)

    return validate_polylines(pointsets, "mesh intersection")
