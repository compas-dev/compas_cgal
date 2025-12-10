"""Geodesic distance computation using CGAL heat method."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from compas_cgal import _types_std  # noqa: F401  # Load vector type bindings
from compas_cgal._geodesics import heat_geodesic_distances as _heat_geodesic_distances
from compas_cgal._geodesics import HeatGeodesicSolver as _HeatGeodesicSolver

if TYPE_CHECKING:
    from compas.datastructures import Mesh

__all__ = ["heat_geodesic_distances", "HeatGeodesicSolver"]


def heat_geodesic_distances(mesh: Mesh, sources: list[int]) -> NDArray:
    """Compute geodesic distances from source vertices using CGAL heat method.

    Uses CGAL's Heat_method_3 with intrinsic Delaunay triangulation for
    accurate geodesic distance computation.

    Parameters
    ----------
    mesh : Mesh
        A compas mesh (must be triangulated).
    sources : list[int]
        Source vertex indices.

    Returns
    -------
    NDArray
        Geodesic distances from the nearest source to each vertex.
        Shape is (n_vertices,).

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas_cgal.geodesics import heat_geodesic_distances
    >>> mesh = Mesh.from_obj('model.obj')
    >>> distances = heat_geodesic_distances(mesh, [0])  # distances from vertex 0

    """
    V, F = mesh.to_vertices_and_faces()
    vertices = np.asarray(V, dtype=np.float64)
    faces = np.asarray(F, dtype=np.int32)

    result = _heat_geodesic_distances(vertices, faces, sources)

    # Return as 1D array
    return result.flatten()


class HeatGeodesicSolver:
    """Precomputed heat method solver for repeated geodesic queries.

    Use this class when computing geodesic distances from multiple
    different sources on the same mesh. The expensive precomputation
    is done once in the constructor, and solve() can be called many
    times efficiently.

    Parameters
    ----------
    mesh : Mesh
        A compas mesh (must be triangulated).

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas_cgal.geodesics import HeatGeodesicSolver
    >>> mesh = Mesh.from_obj('model.obj')
    >>> solver = HeatGeodesicSolver(mesh)  # precomputation happens here
    >>> d0 = solver.solve([0])  # distances from vertex 0
    >>> d1 = solver.solve([1])  # distances from vertex 1 (fast, reuses precomputation)

    """

    def __init__(self, mesh: Mesh) -> None:
        V, F = mesh.to_vertices_and_faces()
        vertices = np.asarray(V, dtype=np.float64)
        faces = np.asarray(F, dtype=np.int32)
        self._solver = _HeatGeodesicSolver(vertices, faces)

    def solve(self, sources: list[int]) -> NDArray:
        """Compute geodesic distances from source vertices.

        Parameters
        ----------
        sources : list[int]
            Source vertex indices.

        Returns
        -------
        NDArray
            Geodesic distances from the nearest source to each vertex.
            Shape is (n_vertices,).

        """
        result = self._solver.solve(sources)
        return result.flatten()

    @property
    def num_vertices(self) -> int:
        """Number of vertices in the mesh."""
        return self._solver.num_vertices
