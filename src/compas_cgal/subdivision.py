from compas.typing import VerticesFaces

from compas_cgal import _subdivision
from compas_cgal import _types_std  # noqa: F401

from ._mesh import as_native_mesh
from ._mesh import as_native_polygon_mesh
from ._mesh import validate_native_mesh
from .types import VerticesFacesNumpy
from .types import VerticesQuadsNumpy

__all__ = ["mesh_subdivide_catmull_clark", "mesh_subdivide_loop", "mesh_subdivide_sqrt3"]


def mesh_subdivide_catmull_clark(mesh: VerticesFaces, k: int = 1) -> VerticesQuadsNumpy:
    """Subdivide a mesh with the Catmull Clark scheme.

    Parameters
    ----------
    mesh
        The mesh to remesh.
    k
        The number of subdivision steps.

    Returns
    -------
    VerticesQuadsNumpy
        Vertex coordinates and quadrilateral faces of the subdivided mesh.

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas.geometry import Box
    >>> from compas_cgal.subdivision import mesh_subdivide_catmull_clark

    >>> box = Box(1)
    >>> mesh = box.to_polygonal_surface().to_vertices_and_faces()

    >>> result = mesh_subdivide_catmull_clark(mesh, k=3)
    >>> subdivided = Mesh.from_vertices_and_faces(*result)

    """
    V, F = as_native_polygon_mesh(mesh, "mesh")
    vertices, faces = _subdivision.subd_catmullclark(V, F, k)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise RuntimeError("CGAL Catmull-Clark subdivision result vertices should have shape (N, 3).")
    if faces.ndim != 2 or faces.shape[1] != 4:
        raise RuntimeError("CGAL Catmull-Clark subdivision result faces should have shape (M, 4).")
    if faces.size and (faces.min() < 0 or faces.max() >= len(vertices)):
        raise RuntimeError("CGAL Catmull-Clark subdivision result contains an out-of-range face index.")
    return vertices, faces


def mesh_subdivide_loop(mesh: VerticesFaces, k: int = 1) -> VerticesFacesNumpy:
    """Subdivide a mesh with the Loop scheme.

    Parameters
    ----------
    mesh
        The mesh to remesh.
    k
        The number of subdivision steps.

    Returns
    -------
    VerticesFacesNumpy

    """
    V, F = as_native_mesh(mesh, "mesh")
    return validate_native_mesh(_subdivision.subd_loop(V, F, k), "Loop subdivision")


def mesh_subdivide_sqrt3(mesh: VerticesFaces, k: int = 1) -> VerticesFacesNumpy:
    """Subdivide a mesh with the Sqrt3 scheme.

    Parameters
    ----------
    mesh
        The mesh to remesh.
    k
        The number of subdivision steps.

    Returns
    -------
    VerticesFacesNumpy

    """
    V, F = as_native_mesh(mesh, "mesh")
    return validate_native_mesh(_subdivision.subd_sqrt3(V, F, k), "Sqrt3 subdivision")
