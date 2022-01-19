import numpy as np
from compas_cgal._cgal import slicer
from compas.plugins import plugin


@plugin(category='trimesh', pluggable_name='trimesh_slice')
def slice_mesh(mesh, planes):
    """Slice a mesh by a list of planes.

    Parameters
    ----------
    mesh : tuple[sequence[[float, float, float] | :class:`compas.geometry.Point`], sequence[[int, int, int]]]
        The mesh to slice.
    planes : list[[point, normal] | :class:`compas.geometry.Plane`]
        The slicing planes.

    Returns
    -------
    list[np.array[np.array[float]]]
        A list of slice polylines, with each polyline an array of points.

    """
    vertices, faces = mesh
    points, normals = zip(*planes)
    V = np.asarray(vertices, dtype=np.float64)
    F = np.asarray(faces, dtype=np.int32)
    P = np.array(points, dtype=np.float64)
    N = np.array(normals, dtype=np.float64)

    pointsets = slicer.slice_mesh(V, F, P, N)
    return pointsets
