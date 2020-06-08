from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np
from compas.datastructures import Mesh
from compas_cgal._cgal import meshing


__all__ = [
    'remesh'
]


def remesh(A, target_edge_length, number_of_iterations=10):
    """Wrapper for all boolean operations.

    Parameters
    ----------
    A : tuple of vertices and faces
        The mesh to remesh.
    target_edge_length : float
        The target edge length.
    number_of_iterations : int, optional
        Number of remeshing iterations.
        Default is ``10``.

    Returns
    -------
    list
        The vertices and faces of the new mesh.

    """
    V, F = A
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    result = meshing.remesh(V, F, target_edge_length, number_of_iterations)
    return result.vertices, result.faces


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
