import numpy as np
from compas_cgal._cgal import measuring
from compas.plugins import plugin


@plugin(category='trimesh', pluggable_name='trimesh_volume')
def voluming(mesh):
    """Compute the volume of a closed triangle mesh.

    Parameters
    ----------
    mesh : tuple of vertices and faces
        The mesh.

    Returns
    -------
    float
        The volume of the mesh.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return measuring.voluming(V, F)
