from __future__ import annotations
from .types import VerticesFaces
from .types import VerticesFacesNumpy
import numpy as np
from compas_cgal._cgal import subdivision


def catmull_clark(mesh: VerticesFaces, k=1) -> VerticesFacesNumpy:
    """Subdivide a mesh withe the Catmull Clark scheme.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to remesh.
    k : int, optional
        The number of subdivision steps.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    Examples
    --------
    >>> from compas.geometry import Box, Polyhedron
    >>> from compas_cgal.subdivision import catmull_clark

    >>> box = Box(1)
    >>> mesh = box.to_vertices_and_faces()

    >>> result = catmull_clark(mesh, k=3)
    >>> shape = Polyhedron(*result)

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return subdivision.subd_catmullclark(V, F, k)
