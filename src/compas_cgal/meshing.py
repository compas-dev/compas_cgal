import numpy as np
from compas.plugins import plugin

from compas_cgal import _meshing  # type: ignore
from compas_cgal import _types_std  # noqa: F401  # type: ignore

from .types import VerticesFaces
from .types import VerticesFacesNumpy


@plugin(category="trimesh", pluggable_name="trimesh_remesh")
def trimesh_remesh(
    mesh: VerticesFaces,
    target_edge_length: float,
    number_of_iterations: int = 10,
    do_project: bool = True,
) -> VerticesFacesNumpy:
    """Remeshing of a triangle mesh.

    Parameters
    ----------
    mesh
        The mesh to remesh.
    target_edge_length : float
        The target edge length.
    number_of_iterations : int, optional
        Number of remeshing iterations.
    do_project : bool, optional
        If True, reproject vertices onto the input surface when they are created or displaced.

    Returns
    -------
    VerticesFacesNumpy

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
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return _meshing.pmp_trimesh_remesh(V, F, target_edge_length, number_of_iterations, do_project)


def trimesh_dual(
    mesh: VerticesFaces,
    length_factor: float = 1.0,
    number_of_iterations: int = 10,
    angle_radians: float = 0.9,
    scale_factor: float = 1.0,
    fixed_vertices: list[int] = [],
) -> tuple[np.ndarray, list[list[int]]]:
    """Create a dual mesh from a triangular mesh with variable-length faces.

    Parameters
    ----------
    mesh
        The mesh to create a dual from.
    angle_radians
        Angle limit in radians for boundary vertices to remove.
    length_factor
        Length factor for remeshing.
    number_of_iterations
        Number of remeshing iterations.
    scale_factor
        Scale factor for inner vertices.
    fixed_vertices
        List of vertex indices to keep fixed during remeshing.

    Returns
    -------
    tuple
        A tuple containing:

        - Remeshed mesh vertices as an Nx3 numpy array.
        - Remeshed mesh faces as an Mx3 numpy array.
        - Dual mesh vertices as an Nx3 numpy array.
        - Variable-length faces as a list of lists of vertex indices.

    Notes
    -----
    This dual mesh implementation includes proper boundary handling by:
    1. Creating vertices at face centroids of the primal mesh
    2. Creating additional vertices at boundary edge midpoints
    3. Creating proper connections for boundary edges

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    fixed_vertices = np.asarray(fixed_vertices, dtype=np.int32, order="C")  # type: ignore
    return _meshing.pmp_trimesh_remesh_dual(V, F, fixed_vertices, length_factor, number_of_iterations, angle_radians, scale_factor)
