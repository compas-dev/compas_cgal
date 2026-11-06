import numpy as np
from compas.datastructures import Mesh
from compas.typing import Float64Array
from compas.typing import PointsLike

from compas_cgal import _meshing
from compas_cgal import _types_std  # noqa: F401

from ._mesh import as_native_mesh

__all__ = ["project_mesh_on_mesh", "project_points_on_mesh", "pull_mesh_on_mesh", "pull_points_on_mesh"]


def project_mesh_on_mesh(
    mesh_source: Mesh,
    mesh_target: Mesh,
) -> Mesh:
    """Project mesh_source vertices onto mesh_target surface.

    Parameters
    ----------
    mesh_source
        Mesh that is projected onto the target mesh.
    mesh_target
        Mesh that is projected onto.

    Returns
    -------
    Mesh
        The projected mesh (vertices on mesh_source surface, original faces).

    """
    V_source, F_source = mesh_source.to_vertices_and_faces()
    V_source = project_points_on_mesh(V_source, mesh_target)
    return Mesh.from_vertices_and_faces(V_source, F_source)


def pull_mesh_on_mesh(
    mesh_source: Mesh,
    mesh_target: Mesh,
) -> Mesh:
    """Pull mesh_source vertices onto mesh_target surface using mesh_source normals.

    Parameters
    ----------
    mesh_source
        Mesh that is projected onto the target mesh.
    mesh_target
        Mesh that is projected onto.

    Returns
    -------
    Mesh
        The projected mesh (vertices on mesh_source surface, original faces).

    """
    V_source, F_source = mesh_source.to_vertices_and_faces()
    N_source = []
    for v in mesh_source.vertices():
        N_source.append(mesh_source.vertex_normal(v))

    V_source = pull_points_on_mesh(V_source, N_source, mesh_target)
    return Mesh.from_vertices_and_faces(V_source, F_source)


def project_points_on_mesh(
    points: PointsLike,
    mesh: Mesh,
) -> Float64Array:
    """Project points onto a mesh by closest perpendicular distance.

    Parameters
    ----------
    points
        The points to project.
    mesh
        Mesh that the points are projected onto.

    Returns
    -------
    numpy.ndarray
        The projected point coordinates.

    """
    triangle_mesh = mesh.triangulated(None)
    target = triangle_mesh.to_vertices_and_faces()
    numpy_V_source = np.ascontiguousarray(points, dtype=np.float64)
    if numpy_V_source.ndim != 2 or numpy_V_source.shape[1] != 3:
        raise ValueError("points should have shape (N, 3).")
    numpy_V_target, numpy_F_target = as_native_mesh(target, "mesh")
    _meshing.pmp_project(numpy_V_target, numpy_F_target, numpy_V_source)

    return numpy_V_source


def pull_points_on_mesh(points: PointsLike, normals: PointsLike, mesh: Mesh) -> Float64Array:
    """Pull points onto a mesh surface using ray-mesh intersection along normal vectors.

    Parameters
    ----------
    points
        The points to pull.
    normals
        The normal vectors used for directing the projection.
    mesh
        Mesh that the points are pulled onto.

    Returns
    -------
    numpy.ndarray
        The pulled point coordinates.

    """

    triangle_mesh = mesh.triangulated()
    target = triangle_mesh.to_vertices_and_faces()
    numpy_V_source = np.ascontiguousarray(points, dtype=np.float64)
    numpy_N_source = np.ascontiguousarray(normals, dtype=np.float64)
    if numpy_V_source.ndim != 2 or numpy_V_source.shape[1] != 3:
        raise ValueError("points should have shape (N, 3).")
    if numpy_N_source.shape != numpy_V_source.shape:
        raise ValueError("normals should have the same shape as points.")
    numpy_V_target, numpy_F_target = as_native_mesh(target, "mesh")
    _meshing.pmp_pull(numpy_V_target, numpy_F_target, numpy_V_source, numpy_N_source)
    return numpy_V_source
