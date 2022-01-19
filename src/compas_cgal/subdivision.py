import numpy as np
from compas_cgal._cgal import subdivision


def catmull_clark(mesh, k=1):
    """Subdivide a mesh withe the Catmull Clark scheme.

    Parameters
    ----------
    mesh : tuple[sequence[[float, float, float] | :class:`compas.geometry.Point`], sequence[[int, int, int]]]
        The mesh to remesh.
    k : int, optional
        The number of subdivision steps.

    Returns
    -------
    (V, 3) np.array[float]
        The vertices of the subdivided mesh.
    (F, 4) np.array[int]
        The faces of the subdivided mesh.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return subdivision.subd_catmullclark(V, F, k)
