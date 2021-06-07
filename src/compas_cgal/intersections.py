import numpy as np
from compas_cgal._cgal import intersections
from compas.plugins import plugin

from compas_cgal.types import VerticesFaces
from compas_cgal.types import ListOfPolylinesNumpy


__all__ = [
    'intersection_mesh_mesh'
]


@plugin(category='intersections')
def intersection_mesh_mesh(A: VerticesFaces, B: VerticesFaces) -> ListOfPolylinesNumpy:
    """Compute the intersection of tow meshes.

    Parameters
    ----------
    A : tuple of vertices and faces
        Mesh A.
    B : tuple of vertices and faces
        Mesh B.

    Returns
    -------
    list of arrays of points
        The intersection polylines as arrays of points.

    """
    VA, FA = A
    VB, FB = B
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)

    pointsets = intersections.intersection_mesh_mesh(VA, FA, VB, FB)

    return pointsets
