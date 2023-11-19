from __future__ import annotations
from .types import VerticesFaces
from .types import VerticesFacesNumpy
import numpy as np
from compas_cgal._cgal import meshing
from compas.plugins import plugin


@plugin(category="trimesh", pluggable_name="trimesh_remesh")
def mesh_remesh(
    mesh: VerticesFaces,
    target_edge_length: float,
    number_of_iterations: int = 10,
    do_project: bool = True,
) -> VerticesFacesNumpy:
    """Remeshing of a triangle mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to remesh.
    target_edge_length : float
        The target edge length.
    number_of_iterations : int, optional
        Number of remeshing iterations.
    do_project : bool, optional
        If True, reproject vertices onto the input surface when they are created or displaced.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    Notes
    -----
    This remeshing function only constrains the edges on the boundary of the mesh.
    Protecting specific features or edges is not implemented yet.

    Examples
    --------
    >>> from compas.geometry import Sphere, Polyhedron
    >>> from compas_cgal.meshing import mesh_remesh

    >>> sphere = Sphere(0.5, point=[1, 1, 1])
    >>> mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> V, F = mesh_remesh(mesh, 1.0)
    >>> shape = Polyhedron(V.tolist(), F.tolist())

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return meshing.remesh(V, F, target_edge_length, number_of_iterations)
