import numpy as np

from compas_cgal import _subdivision  # type: ignore
from compas_cgal import _types_std  # noqa: F401 # type: ignore

from .types import VerticesFaces
from .types import VerticesFacesNumpy


def mesh_subdivide_catmull_clark(mesh: VerticesFaces, k=1) -> VerticesFacesNumpy:
    """Subdivide a mesh with the Catmull Clark scheme.

    Parameters
    ----------
    mesh
        The mesh to remesh.
    k
        The number of subdivision steps.

    Returns
    -------
    VerticesFacesNumpy

    Examples
    --------
    >>> from compas.geometry import Box, Polyhedron
    >>> from compas_cgal.subdivision import mesh_subdivide_catmull_clark

    >>> box = Box(1)
    >>> mesh = box.to_vertices_and_faces()

    >>> result = mesh_subdivide_catmull_clark(mesh, k=3)
    >>> shape = Polyhedron(*result)

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return _subdivision.subd_catmullclark(V, F, k)


def mesh_subdivide_loop(mesh: VerticesFaces, k=1) -> VerticesFacesNumpy:
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
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return _subdivision.subd_loop(V, F, k)


def mesh_subdivide_sqrt3(mesh: VerticesFaces, k=1) -> VerticesFacesNumpy:
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
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return _subdivision.subd_sqrt3(V, F, k)
