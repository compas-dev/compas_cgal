import numpy as np
from compas_cgal._cgal import meshing
from compas.plugins import plugin


@plugin(category='trimesh', pluggable_name='trimesh_remesh')
def remesh(mesh, target_edge_length, number_of_iterations=10, do_project=True):
    """Remeshing of a triangle mesh.

    Parameters
    ----------
    mesh : tuple of vertices and faces
        The mesh to remesh.
    target_edge_length : float
        The target edge length.
    number_of_iterations : int, optional
        Number of remeshing iterations.
        Default is ``10``.
    do_project : bool, optional
        Reproject vertices onto the input surface when they are created or displaced.
        Default is ``True``.

    Returns
    -------
    list
        The vertices and faces of the new mesh.

    Notes
    -----
    This remeshing function only constrains the edges on the boundary of the mesh.
    To protect specific features or edges, please use :func:`remesh_constrained`.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return meshing.remesh(V, F, target_edge_length, number_of_iterations)


def remesh_constrained(mesh, target_edge_length, protected_edges, number_of_iterations=10, do_project=True):
    """Remeshing of a triangle mesh.

    Parameters
    ----------
    mesh : tuple of vertices and faces
        The mesh to remesh.
    target_edge_length : float
        The target edge length.
    protected_edges : list
        A list of vertex pairs that identify protected edges of the mesh.
    number_of_iterations : int, optional
        Number of remeshing iterations.
        Default is ``10``.
    do_project : bool, optional
        Reproject vertices onto the input surface when they are created or displaced.
        Default is ``True``.

    Returns
    -------
    list
        The vertices and faces of the new mesh.

    """
    raise NotImplementedError
