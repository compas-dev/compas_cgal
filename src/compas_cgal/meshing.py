import numpy as np
from compas.datastructures import Mesh
from compas.plugins import plugin

from compas_cgal import _meshing
from compas_cgal import _types_std  # noqa: F401

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
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to create a dual from.
    angle_radians : double, optional
        Angle limit in radians for boundary vertices to remove.
    length_factor : double, optional
        Length factor for remeshing.
    number_of_iterations : int, optional
        Number of remeshing iterations.
    scale_factor : double, optional
        Scale factor for inner vertices.
    fixed_vertices : list[int], optional
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
    fixed_vertices = np.asarray(fixed_vertices, dtype=np.int32, order="C")
    return _meshing.pmp_trimesh_remesh_dual(V, F, fixed_vertices, length_factor, number_of_iterations, angle_radians, scale_factor)


def project_mesh_on_mesh(
    mesh_source: VerticesFaces,
    mesh_target: VerticesFaces,
) -> VerticesFaces:
    """Project mesh_source vertices onto mesh_target surface.

    Parameters
    ----------
    mesh_source : :attr:`compas_cgal.types.VerticesFaces`
        Mesh that is projected onto the target mesh.
    mesh_target : :attr:`compas_cgal.types.VerticesFaces`
        Mesh that is projected onto.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFaces`
        The projected mesh (vertices on mesh_source surface, original faces).

    """
    V_source, F_source = mesh_source.to_vertices_and_faces()
    V_source = project_points_on_mesh(V_source, mesh_target)
    return Mesh.from_vertices_and_faces(V_source, F_source)


def pull_mesh_on_mesh(
    mesh_source: VerticesFaces,
    mesh_target: VerticesFaces,
) -> VerticesFaces:
    """Pull mesh_source vertices onto mesh_target surface using mesh_source normals.

    Parameters
    ----------
    mesh_source : :attr:`compas_cgal.types.VerticesFaces`
        Mesh that is projected onto the target mesh.
    mesh_target : :attr:`compas_cgal.types.VerticesFaces`
        Mesh that is projected onto.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFaces`
        The projected mesh (vertices on mesh_source surface, original faces).

    """
    V_source, F_source = mesh_source.to_vertices_and_faces()
    N_source = []
    for v in mesh_source.vertices():
        N_source.append(mesh_source.vertex_normal(v))

    V_source = pull_points_on_mesh(V_source, N_source, mesh_target)
    return Mesh.from_vertices_and_faces(V_source, F_source)


def project_points_on_mesh(
    points: list[list[float]],
    mesh: VerticesFaces,
) -> list[list[float]]:
    """Project points onto a mesh by closest perpendicular distance.

    Parameters
    ----------
    points : list[list[float]]
        The points to project.
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        Mesh that the points are projected onto.

    Returns
    -------
    list[list[float]]
        The projected points (vertices on the mesh surface).

    """
    V_target, F_target = mesh.to_vertices_and_faces(triangulated=True)
    numpy_V_source = np.asarray(points, dtype=np.float64, order="C")
    numpy_V_target = np.asarray(V_target, dtype=np.float64, order="C")
    numpy_F_target = np.asarray(F_target, dtype=np.int32, order="C")
    _meshing.pmp_project(numpy_V_target, numpy_F_target, numpy_V_source)

    return numpy_V_source


def pull_points_on_mesh(points: list[list[float]], normals: list[list[float]], mesh: VerticesFaces) -> list[list[float]]:
    """Pull points onto a mesh surface using ray-mesh intersection along normal vectors.

    Parameters
    ----------
    points : list[list[float]]
        The points to pull.
    normals : list[list[float]]
        The normal vectors used for directing the projection.
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        Mesh that the points are pulled onto.

    Returns
    -------
    list[list[float]]
        The pulled points (vertices on the mesh surface).

    """

    V_target, F_target = mesh.to_vertices_and_faces(triangulated=True)
    numpy_V_source = np.asarray(points, dtype=np.float64, order="C")
    numpy_N_source = np.asarray(normals, dtype=np.float64, order="C")
    numpy_V_target = np.asarray(V_target, dtype=np.float64, order="C")
    numpy_F_target = np.asarray(F_target, dtype=np.int32, order="C")
    _meshing.pmp_pull(numpy_V_target, numpy_F_target, numpy_V_source, numpy_N_source)
    return numpy_V_source
