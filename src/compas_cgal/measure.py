import numpy as np
from compas.geometry import Point
from compas.plugins import plugin

from compas_cgal import _measure
from compas_cgal import _types_std

from .types import VerticesFaces


def mesh_area(mesh: VerticesFaces) -> float:
    """Compute the area of a triangle mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh.

    Returns
    -------
    float
        The area of the mesh.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return _measure.area(V, F)


@plugin(category="trimesh", pluggable_name="trimesh_volume")
def mesh_volume(mesh: VerticesFaces) -> float:
    """Compute the volume of a closed triangle mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
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
    >>> mesh = box.to_vertices_and_faces(triangulated=True)

    >>> mesh_volume(mesh)
    1.0

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return _measure.volume(V, F)


def mesh_centroid(mesh: VerticesFaces) -> list[float]:
    """Compute the centroid of a the volume of a closed triangle mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh.

    Returns
    -------
    list
        The centroid of the mesh.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    vector_of_double: _types_std.VectorDouble = _measure.centroid(V, F)
    point = Point(*vector_of_double)
    return point
