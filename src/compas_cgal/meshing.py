import numpy as np
from compas_cgal._cgal import meshing
from compas.plugins import plugin


@plugin(category='trimesh', pluggable_name='trimesh_remesh')
def remesh(mesh, target_edge_length, number_of_iterations=10, do_project=True):
    """Remeshing of a triangle mesh.

    Parameters
    ----------
    mesh : tuple[sequence[[float, float, float] | :class:`compas.geometry.Point`], sequence[[int, int, int]]]
        The mesh to remesh.
    target_edge_length : float
        The target edge length.
    number_of_iterations : int, optional
        Number of remeshing iterations.
    do_project : bool, optional
        If True, reproject vertices onto the input surface when they are created or displaced.

    Returns
    -------
    (V, 3) np.array[float]
        The vertices of the remeshed mesh.
    (F, 3) np.array[int]
        The faces of the remeshed mesh.

    Notes
    -----
    This remeshing function only constrains the edges on the boundary of the mesh.
    Protecting specific features or edges is not implemented yet.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return meshing.remesh(V, F, target_edge_length, number_of_iterations)
