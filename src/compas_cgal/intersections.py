from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np
from compas_cgal._cgal import intersections


__all__ = [
    'intersection_mesh_mesh'
]


def intersection_mesh_mesh(A, B):
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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
