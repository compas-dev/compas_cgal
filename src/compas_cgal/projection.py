import numpy as np
from compas.datastructures import Mesh

from compas_cgal import _meshing  # type: ignore
from compas_cgal import _types_std  # noqa: F401  # type: ignore

from .types import VerticesFaces


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
