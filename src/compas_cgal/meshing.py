from __future__ import annotations

import numpy as np
from compas.typing import IndicesLike
from compas.typing import VerticesFaces

from compas_cgal import _meshing
from compas_cgal import _types_std  # noqa: F401

from ._mesh import as_native_mesh
from ._mesh import validate_native_mesh
from .types import DualMeshNumpy
from .types import VerticesFacesNumpy

__all__ = ["trimesh_dual", "trimesh_remesh"]


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
    target_edge_length
        The target edge length.
    number_of_iterations
        Number of remeshing iterations.
    do_project
        If True, reproject vertices onto the input surface when they are created or displaced.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        Native vertex and triangle arrays of the remeshed geometry.

    Examples
    --------
    >>> from compas.geometry import Sphere
    >>> from compas_cgal.meshing import trimesh_remesh
    >>> mesh = Sphere(0.5).to_tessellation(nu=32, nv=32).to_vertices_and_triangles()
    >>> vertices, triangles = trimesh_remesh(mesh, 0.1)

    """
    V, F = as_native_mesh(mesh, "mesh")
    result = _meshing.pmp_trimesh_remesh(
        V,
        F,
        target_edge_length,
        number_of_iterations,
        do_project,
        False,
        0.0,
        np.empty((0, 3), dtype=np.float64),
    )
    return validate_native_mesh(result, "remeshing")


def trimesh_dual(
    mesh: VerticesFaces,
    length_factor: float = 1.0,
    number_of_iterations: int = 10,
    angle_radians: float = 0.9,
    scale_factor: float = 1.0,
    fixed_vertices: IndicesLike = (),
) -> DualMeshNumpy:
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
        Vertex indices to keep fixed during remeshing.

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
    V, F = as_native_mesh(mesh, "mesh")
    fixed_vertices_array = np.ascontiguousarray(fixed_vertices, dtype=np.int32)
    if fixed_vertices_array.ndim != 1:
        raise ValueError("fixed_vertices should be a one-dimensional sequence of indices.")
    if fixed_vertices_array.size and (fixed_vertices_array.min() < 0 or fixed_vertices_array.max() >= len(V)):
        raise IndexError("fixed_vertices contains an out-of-range vertex index.")
    vertices, faces, dual_vertices, dual_faces = _meshing.pmp_trimesh_remesh_dual(
        V,
        F,
        fixed_vertices_array,
        length_factor,
        number_of_iterations,
        angle_radians,
        scale_factor,
    )
    validate_native_mesh((vertices, faces), "dual remeshing")
    if dual_vertices.ndim != 2 or dual_vertices.shape[1] != 3:
        raise RuntimeError("CGAL dual result vertices should have shape (N, 3).")
    for face in dual_faces:
        if any(index < 0 or index >= len(dual_vertices) for index in face):
            raise RuntimeError("CGAL dual result contains an out-of-range face index.")
    return vertices, faces, dual_vertices, dual_faces
