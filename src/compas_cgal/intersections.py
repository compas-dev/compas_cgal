import numpy as np
from compas_cgal._cgal import intersections
from compas.plugins import plugin


@plugin(category='intersections')
def intersection_mesh_mesh(A, B):
    """Compute the intersection of tow meshes.

    Parameters
    ----------
    A : tuple[Sequence[[float, float, float] | :class:`compas.geometry.Point`], Sequence[[int, int, int]]]
        Mesh A.
    B : tuple[Sequence[[float, float, float] | :class:`compas.geometry.Point`], Sequence[[int, int, int]]]
        Mesh B.

    Returns
    -------
    list[NDArray[(Any, 3), np.float64]]
        A list of intersection polylines, with each polyline an array of points.

    """
    VA, FA = A
    VB, FB = B
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)

    pointsets = intersections.intersection_mesh_mesh(VA, FA, VB, FB)

    return pointsets
