from compas.geometry import Tessellation

from compas_cgal import _intersections  # type: ignore
from compas_cgal import _types_std  # type: ignore

from ._tessellation import as_native_tessellation
from .types import PolylinesNumpy


def intersection_mesh_mesh(
    A: Tessellation,
    B: Tessellation,
) -> PolylinesNumpy:
    """Compute the intersection of two triangle tessellations.

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

    >>> A = box.tessellate(Native())
    >>> B = sphere.tessellate(UVGrid(32, 32))

    >>> result = intersection_mesh_mesh(A, B)
    >>> polylines = [Polyline(points) for points in result]

    """
    VA, FA = as_native_tessellation(A)
    VB, FB = as_native_tessellation(B)

    pointsets: _types_std.VectorRowMatrixXd = _intersections.intersection_mesh_mesh(VA, FA, VB, FB)

    return pointsets
