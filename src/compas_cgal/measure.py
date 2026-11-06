from compas.typing import VerticesFaces

from compas_cgal import _measure
from compas_cgal import _types_std  # noqa: F401

from ._mesh import as_native_mesh

__all__ = ["mesh_area", "mesh_centroid", "mesh_volume"]


def mesh_area(mesh: VerticesFaces) -> float:
    """Compute the area of a triangle mesh.

    Parameters
    ----------
    mesh
        The mesh.

    Returns
    -------
    float
        The area of the mesh.

    """
    V, F = as_native_mesh(mesh, "mesh")
    return _measure.area(V, F)


def mesh_volume(mesh: VerticesFaces) -> float:
    """Compute the volume of a closed triangle mesh.

    Parameters
    ----------
    mesh
        The mesh.

    Returns
    -------
    float
        The volume of the mesh.

    Examples
    --------
    >>> from compas.geometry import Box
    >>> from compas_cgal.measure import mesh_volume

    >>> box = Box(1)
    >>> mesh = box.to_tessellation().to_vertices_and_triangles()

    >>> mesh_volume(mesh)
    1.0

    """
    V, F = as_native_mesh(mesh, "mesh")
    return _measure.volume(V, F)


def mesh_centroid(mesh: VerticesFaces) -> list[float]:
    """Compute the centroid of the volume of a closed triangle mesh.

    Parameters
    ----------
    mesh
        The mesh.

    Returns
    -------
    list[float]
        The centroid of the mesh.

    """
    V, F = as_native_mesh(mesh, "mesh")
    return list(_measure.centroid(V, F))
