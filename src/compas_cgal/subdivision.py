import numpy as np
from compas_cgal._cgal import subdivision


def catmull_clark(mesh, k=1):
    """Subdivide a mesh withe the Catmull Clark scheme.

    Parameters
    ----------
    mesh : tuple[Sequence[[float, float, float] | :class:`compas.geometry.Point`], Sequence[[int, int, int]]]
        The mesh to remesh.
    k : int, optional
        The number of subdivision steps.

    Returns
    -------
    NDArray[(Any, 3), np.float64]
        The vertices of the subdivided mesh.
    NDArray[(Any, 4), np.int32]
        The faces of the subdivided mesh.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return subdivision.subd_catmullclark(V, F, k)
