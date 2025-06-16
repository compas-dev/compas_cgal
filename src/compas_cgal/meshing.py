import numpy as np
from compas.plugins import plugin

from compas_cgal import _meshing

from .types import VerticesFaces
from .types import VerticesFacesNumpy


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
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return _meshing.remesh(V, F, target_edge_length, number_of_iterations)


def mesh_remesh_dual(
    mesh: VerticesFaces,
    target_edge_length: float,
    number_of_iterations: int = 10,
    angle_radians: float = 0.0,
    circumcenter: bool = True,
) -> tuple[np.ndarray, list[list[int]]]:
    """Create a dual mesh from a triangular mesh with variable-length faces.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to create a dual from.
    target_edge_length : float
        The target edge length for primal mesh remeshing before dual creation.
    number_of_iterations : int, optional
        Number of remeshing iterations for the primal mesh.
    angle_radians : double, optional
        Angle limit in radians for boundary vertices to remove.
    circumcenter : bool, optional
        Whether to use the circumcenter of the triangle instead of the centroid.

    Returns
    -------
    tuple
        A tuple containing:
        - Dual mesh vertices as an Nx3 numpy array.
        - Variable-length faces as a list of lists of vertex indices.

    Notes
    -----
    This dual mesh implementation includes proper boundary handling by:
    1. Creating vertices at face centroids of the primal mesh
    2. Creating additional vertices at boundary edge midpoints
    3. Creating proper connections for boundary edges

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas_cgal.meshing import mesh_remesh_dual

    >>> # Create a simple quad mesh
    >>> mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], [[0, 1, 2, 3]])
    >>> vertices, faces = mesh.to_vertices_and_faces()

    >>> # Create its dual mesh with variable-length faces
    >>> V, F = mesh_remesh_dual((vertices, faces), 0.1)
    >>> dual_mesh = Mesh.from_vertices_and_faces(V, [])
    >>> # Add the variable-length faces to the mesh
    >>> for face in F:
    ...     dual_mesh.add_face(face)

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    vertices, var_faces = _meshing.remesh_dual(V, F, target_edge_length, number_of_iterations, angle_radians, circumcenter)
    return vertices, var_faces
