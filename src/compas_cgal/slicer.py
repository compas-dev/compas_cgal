import numpy as np
from compas_cgal._cgal import slicer
from compas.plugins import plugin


__all__ = [
    'slice_mesh'
]


@plugin(category='slicing')
def slice_mesh(mesh, planes):
    """Slice a mesh by a list of planes.

    Parameters
    ----------
    mesh : tuple of vertices and faces
        The mesh to slice.
    planes : list of (point, normal) tuples or compas.geometry.Plane
        The slicing planes.

    Returns
    -------
    list of arrays
        The points defining the slice polylines.

    """
    vertices, faces = mesh
    points, normals = zip(*planes)
    V = np.asarray(vertices, dtype=np.float64)
    F = np.asarray(faces, dtype=np.int32)
    P = np.array(points, dtype=np.float64)
    N = np.array(normals, dtype=np.float64)

    pointsets = slicer.slice_mesh(V, F, P, N)
    return pointsets
