import numpy as np
from compas.plugins import plugin
from compas_cgal._cgal import booleans


__all__ = [
    'boolean_union',
    'boolean_difference',
    'boolean_intersection'
]


def _boolean(A, B, operation):
    """Wrapper for all boolean operations.

    Parameters
    ----------
    A : tuple of vertices and faces
        Mesh A.
    B : tuple of vertices and faces
        Mesh B.
    operation : {'union', 'difference', 'intersection'}
        The type of boolean operation.

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

    return result


@plugin(category='booleans', pluggable_name='boolean_union_mesh_mesh')
def boolean_union(A, B):
    return _boolean(A, B, 'union')


@plugin(category='booleans', pluggable_name='boolean_difference_mesh_mesh')
def boolean_difference(A, B):
    return _boolean(A, B, 'difference')


@plugin(category='booleans', pluggable_name='boolean_intersection_mesh_mesh')
def boolean_intersection(A, B):
    return _boolean(A, B, 'intersection')
