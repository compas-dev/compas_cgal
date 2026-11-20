"""Closest point and signed distance to a triangle mesh using CGAL."""

from typing import Optional
from typing import Tuple

import numpy as np
from numpy.typing import NDArray

from compas_cgal._distance import MeshDistance as _MeshDistance
from compas_cgal.types import VerticesFaces

__all__ = ["MeshDistance"]


class MeshDistance:
    """Closest point and signed distance queries on a triangle mesh.

    Use this class to query many points against the same mesh. The search
    tree (CGAL ``AABB_tree``) is built once in the constructor and reused by
    every call. Queries run on several threads and release the GIL; the
    result does not depend on the number of threads.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        A manifold triangle mesh without degenerate faces.
        For :meth:`signed_distance` it has to be closed, free of self-intersections,
        and its faces wound counter-clockwise seen from outside.

    Raises
    ------
    ValueError
        If the faces are not triangles, refer to a vertex that does not exist,
        or do not form a manifold mesh.

    Examples
    --------
    >>> from compas.geometry import Box
    >>> from compas_cgal.distance import MeshDistance
    >>> box = Box(2)
    >>> mesh = box.to_vertices_and_faces(triangulated=True)
    >>> solver = MeshDistance(mesh)  # the tree is built here
    >>> distances, points, faces, gradients = solver.signed_distance([[0, 0, 0], [3, 0, 0]])
    >>> distances
    array([-1.,  2.])

    """

    def __init__(self, mesh: VerticesFaces) -> None:
        V, F = mesh
        V = np.asarray(V, dtype=np.float64, order="C")
        F = np.asarray(F, dtype=np.int32, order="C")
        self._solver = _MeshDistance(V, F)

    @property
    def is_closed(self) -> bool:
        """Whether the mesh is closed, as :meth:`signed_distance` requires."""
        return self._solver.is_closed

    def closest(self, points, num_threads: Optional[int] = None) -> Tuple[NDArray, NDArray]:
        """Find the closest point on the mesh for each query point.

        Parameters
        ----------
        points : array-like
            The query points, as an Nx3 array.
        num_threads : int, optional
            The number of threads to run the queries on.
            By default, all hardware threads.

        Returns
        -------
        closest_points : NDArray
            The closest points on the mesh. Shape is (N, 3).
        faces : NDArray
            The index of a face each closest point lies on, as ``int32``. Shape is (N,).

        Raises
        ------
        ValueError
            If the points are not an Nx3 array, or the number of threads is negative.

        """
        P = np.asarray(points, dtype=np.float64, order="C")
        return self._solver.closest(P, num_threads or 0)

    def signed_distance(self, points, num_threads: Optional[int] = None) -> Tuple[NDArray, NDArray, NDArray, NDArray]:
        """Compute the signed distance to the mesh for each query point.

        The side is decided by CGAL ``Side_of_triangle_mesh`` with exact
        predicates, independently of the closest point: a query is inside,
        outside, or on the mesh, and the distance is exactly zero only in
        the last case or where the closest point coincides with the query
        in ``float64``.

        Parameters
        ----------
        points : array-like
            The query points, as an Nx3 array.
        num_threads : int, optional
            The number of threads to run the queries on.
            By default, all hardware threads.

        Returns
        -------
        distances : NDArray
            The distance to the mesh, negative inside. Shape is (N,).
        closest_points : NDArray
            The closest points on the mesh. Shape is (N, 3).
        faces : NDArray
            The index of a face each closest point lies on, as ``int32``.
            For a query on the mesh, the lowest index among the faces it lies on.
            Shape is (N,).
        gradients : NDArray
            The gradient of the signed distance: the unit vector from the
            closest point to the query, reversed inside. For a query on the
            mesh, the angle-weighted pseudonormal of the face, edge or vertex
            it lies on. Shape is (N, 3).

        Raises
        ------
        ValueError
            If the mesh is not closed, the points are not an Nx3 array,
            or the number of threads is negative.

        """
        P = np.asarray(points, dtype=np.float64, order="C")
        return self._solver.signed_distance(P, num_threads or 0)
