import numpy as np
from typing import Optional
from compas.plugins import plugin
from compas.datastructures import Mesh

from compas_cgal import _meshing
from compas_cgal import _types_std  # noqa: F401

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
    return _meshing.remesh(V, F, target_edge_length, number_of_iterations, do_project)


def mesh_project(
    mesh_source: VerticesFaces,
    mesh_target: VerticesFaces,
    use_normals: bool = True,
) -> VerticesFaces:
    """Project mesh_target vertices onto mesh_source surface.

    Parameters
    ----------
    mesh_source : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to project onto (target surface).
    mesh_target : :attr:`compas_cgal.types.VerticesFaces`
        The mesh whose vertices will be projected (source points).
    use_normals : bool, optional
        Whether to use normals for ray-based projection. If False, closest point projection is used.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFaces`
        The projected mesh (vertices on mesh_source surface, original faces).

    """
    V_source, F_source = mesh_source.to_vertices_and_faces()
    V_target, F_target = mesh_target.to_vertices_and_faces(triangulated=True)

    # Convert inputs to numpy arrays
    numpy_V_source = np.asarray(V_source, dtype=np.float64, order="C")

    numpy_V_target = np.asarray(V_target, dtype=np.float64, order="C")
    numpy_F_target = np.asarray(F_target, dtype=np.int32, order="C")

    # Handle normals calculation
    if use_normals:
        # Pre-allocate numpy array for normals with correct size
        numpy_N_source = np.zeros((mesh_source.number_of_vertices(), 3), dtype=np.float64)

        # Fill the array with vertex normals
        for i, vertex_key in enumerate(mesh_source.vertices()):
            normal = -mesh_source.vertex_normal(vertex_key)
            numpy_N_source[i, 0] = normal.x
            numpy_N_source[i, 1] = normal.y
            numpy_N_source[i, 2] = normal.z
    else:
        # Don't use normals - create empty array
        numpy_N_source = np.zeros((0, 0), dtype=np.float64)

    # Call the C++ function
    _meshing.project(numpy_V_target, numpy_F_target, numpy_V_source, numpy_N_source)

    return Mesh.from_vertices_and_faces(numpy_V_source, F_source)


def mesh_dual(
    mesh: VerticesFaces,
    angle_radians: float = 0.0,
    circumcenter: bool = True,
    scale_factor: float = 1.0,
) -> tuple[np.ndarray, list[list[int]]]:
    """Create a dual mesh from a triangular mesh with variable-length faces.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to create a dual from.
    angle_radians : double, optional
        Angle limit in radians for boundary vertices to remove.
    circumcenter : bool, optional
        Whether to use the circumcenter of the triangle instead of the centroid.
    scale_factor : double, optional
        Scale factor for inner vertices.

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

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    vertices, var_faces = _meshing.dual(V, F, angle_radians, circumcenter, scale_factor)
    return vertices, var_faces
