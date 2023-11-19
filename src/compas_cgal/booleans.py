from __future__ import annotations
from typing import Literal
from .types import VerticesFaces
from .types import VerticesFacesNumpy

import numpy as np
from compas.plugins import plugin
from compas_cgal._cgal import booleans


def _boolean(
    A: VerticesFaces,
    B: VerticesFaces,
    operation: Literal["union", "difference", "intersection"],
) -> VerticesFacesNumpy:
    """Wrapper for all boolean operations.

    Parameters
    ----------
    A : VerticesFaces
        Mesh A.
    B : VerticesFaces
        Mesh B.
    operation : Literal['union', 'difference', 'intersection']
        The type of boolean operation.

    Returns
    -------
    VerticesFacesNumpy

    Raises
    ------
    NotImplementedError
        If the operation type is not supported.

    """
    VA, FA = A
    VB, FB = B
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)

    if operation == "union":
        result = booleans.boolean_union(VA, FA, VB, FB)
    elif operation == "difference":
        result = booleans.boolean_difference(VA, FA, VB, FB)
    elif operation == "intersection":
        result = booleans.boolean_intersection(VA, FA, VB, FB)
    elif operation == "split":
        result = booleans.split(VA, FA, VB, FB)
    else:
        raise NotImplementedError

    return result


@plugin(category="booleans", pluggable_name="boolean_union_mesh_mesh")
def boolean_union_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Boolean union of two meshes.

    Parameters
    ----------
    A : :attr:`compas_cgal.types.VerticesFaces`
        Mesh A.
    B : :attr:`compas_cgal.types.VerticesFaces`
        Mesh B.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import boolean_union_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> C = boolean_union_mesh_mesh(A, B)
    >>> shape = Polyhedron(*C)

    """
    return _boolean(A, B, "union")


@plugin(category="booleans", pluggable_name="boolean_difference_mesh_mesh")
def boolean_difference_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Boolean difference of two meshes.

    Parameters
    ----------
    A : :attr:`compas_cgal.types.VerticesFaces`
        Mesh A.
    B : :attr:`compas_cgal.types.VerticesFaces`
        Mesh B.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import boolean_difference_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> C = boolean_difference_mesh_mesh(A, B)
    >>> shape = Polyhedron(*C)

    """
    return _boolean(A, B, "difference")


@plugin(category="booleans", pluggable_name="boolean_intersection_mesh_mesh")
def boolean_intersection_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Boolean intersection of two meshes.

    Parameters
    ----------
    A : :attr:`compas_cgal.types.VerticesFaces`
        Mesh A.
    B : :attr:`compas_cgal.types.VerticesFaces`
        Mesh B.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import boolean_intersection_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> C = boolean_intersection_mesh_mesh(A, B)
    >>> shape = Polyhedron(*C)

    """
    return _boolean(A, B, "intersection")


@plugin(category="booleans", pluggable_name="split_mesh_mesh")
def split_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Split one mesh with another.

    Parameters
    ----------
    A : :attr:`compas_cgal.types.VerticesFaces`
        Mesh A.
    B : :attr:`compas_cgal.types.VerticesFaces`
        Mesh B.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import split_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> V, F = split_mesh_mesh(A, B)
    >>> shape = Polyhedron(V.tolist(), F.tolist())

    """
    return _boolean(A, B, "split")


split = split_mesh_mesh
