from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np
from compas.datastructures import Mesh
from compas_cgal._cgal import booleans
from compas_cgal._cgal import meshing


__all__ = [
    'boolean_union',
    'boolean_difference',
    'boolean_intersection'
]


def _boolean(A, B, operation, remesh=True):
    """Wrapper for all boolean operations.

    Parameters
    ----------
    A : tuple of vertices and faces
        Mesh A.
    B : tuple of vertices and faces
        Mesh B.
    operation : {'union', 'difference', 'intersection'}
        The type of boolean operation.
    remesh : bool, optional
        Remesh if ``True``.
        Default is ``True``.

    Returns
    -------
    list
        The vertices of the boolean mesh,
        and the faces of the boolean mesh,
        as a list of two numpy arrays.

    Raises
    ------
    NotImplementedError
        If the operation type is not supported.

    Notes
    -----
    * COMPAS meshes should be able to shadow (vertices, faces) tuples.
    * Provide remeshing options
    * Add remeshing on the C++ side (avoid needles traffic).
    * Provide optional out parameter.
    * Remeshing only protects sharp features in the boolean.
    * Remeshing should protect the intersection edges.
    * Result should be a list of vertices and faces.

    """
    VA, FA = A
    VB, FB = B
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)

    if operation == 'union':
        result = booleans.boolean_union(VA, FA, VB, FB)
    elif operation == 'difference':
        result = booleans.boolean_difference(VA, FA, VB, FB)
    elif operation == 'intersection':
        result = booleans.boolean_intersection(VA, FA, VB, FB)
    else:
        raise NotImplementedError

    if remesh:
        V = result.vertices
        F = result.faces
        result = meshing.remesh(V, F, 0.1, 10)

    return result.vertices, result.faces


def boolean_union(A, B, remesh=True):
    return _boolean(A, B, 'union', remesh=remesh)


def boolean_difference(A, B, remesh=True):
    return _boolean(A, B, 'difference', remesh=remesh)


def boolean_intersection(A, B, remesh=True):
    return _boolean(A, B, 'intersection', remesh=remesh)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
