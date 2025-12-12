"""Geodesic distance computation using CGAL heat method."""

from typing import List

import numpy as np
from numpy.typing import NDArray

from compas_cgal import _types_std  # noqa: F401  # Load vector type bindings
from compas_cgal._geodesics import geodesic_isolines as _geodesic_isolines
from compas_cgal._geodesics import geodesic_isolines_split as _geodesic_isolines_split
from compas_cgal._geodesics import heat_geodesic_distances as _heat_geodesic_distances
from compas_cgal._geodesics import HeatGeodesicSolver as _HeatGeodesicSolver
from compas_cgal.types import PolylinesNumpy
from compas_cgal.types import VerticesFaces
from compas_cgal.types import VerticesFacesNumpy

__all__ = ["heat_geodesic_distances", "HeatGeodesicSolver", "geodesic_isolines_split", "geodesic_isolines"]


def heat_geodesic_distances(mesh: VerticesFaces, sources: List[int]) -> NDArray:
    """Compute geodesic distances from source vertices using CGAL heat method.

    Uses CGAL's Heat_method_3 with intrinsic Delaunay triangulation for
    accurate geodesic distance computation.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        A triangulated mesh as a tuple of vertices and faces.
    sources : List[int]
        Source vertex indices.

    Returns
    -------
    NDArray
        Geodesic distances from the nearest source to each vertex.
        Shape is (n_vertices,).

    Examples
    --------
    >>> from compas.geometry import Box
    >>> from compas_cgal.geodesics import heat_geodesic_distances
    >>> box = Box(1)
    >>> mesh = box.to_vertices_and_faces(triangulated=True)
    >>> distances = heat_geodesic_distances(mesh, [0])  # distances from vertex 0

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")

    result = _heat_geodesic_distances(V, F, sources)
    return result.flatten()


class HeatGeodesicSolver:
    """Precomputed heat method solver for repeated geodesic queries.

    Use this class when computing geodesic distances from multiple
    different sources on the same mesh. The expensive precomputation
    is done once in the constructor, and solve() can be called many
    times efficiently.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        A triangulated mesh as a tuple of vertices and faces.

    Examples
    --------
    >>> from compas.geometry import Sphere
    >>> from compas_cgal.geodesics import HeatGeodesicSolver
    >>> sphere = Sphere(1.0)
    >>> mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)
    >>> solver = HeatGeodesicSolver(mesh)  # precomputation happens here
    >>> d0 = solver.solve([0])  # distances from vertex 0
    >>> d1 = solver.solve([1])  # distances from vertex 1 (fast, reuses precomputation)

    """

    def __init__(self, mesh: VerticesFaces) -> None:
        V, F = mesh
        V = np.asarray(V, dtype=np.float64, order="C")
        F = np.asarray(F, dtype=np.int32, order="C")
        self._solver = _HeatGeodesicSolver(V, F)

    def solve(self, sources: List[int]) -> NDArray:
        """Compute geodesic distances from source vertices.

        Parameters
        ----------
        sources : List[int]
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


def geodesic_isolines_split(
    mesh: VerticesFaces,
    sources: List[int],
    isovalues: List[float],
) -> List[VerticesFacesNumpy]:
    """Split mesh into components along geodesic isolines.

    Computes geodesic distances from sources, refines the mesh along
    specified isovalue thresholds, and splits into connected components.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        A triangulated mesh as a tuple of vertices and faces.
    sources : List[int]
        Source vertex indices for geodesic distance computation.
    isovalues : List[float]
        Isovalue thresholds for splitting. The mesh will be refined
        along curves where the geodesic distance equals each isovalue,
        then split into connected components.

    Returns
    -------
    List[:attr:`compas_cgal.types.VerticesFacesNumpy`]
        List of mesh components as (vertices, faces) tuples.

    Examples
    --------
    >>> from compas.geometry import Sphere
    >>> from compas_cgal.geodesics import geodesic_isolines_split
    >>> sphere = Sphere(1.0)
    >>> mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)
    >>> components = geodesic_isolines_split(mesh, [0], [0.5, 1.0, 1.5])
    >>> len(components)  # Number of mesh strips

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")

    vertices_list, faces_list = _geodesic_isolines_split(V, F, sources, isovalues)
    return list(zip(vertices_list, faces_list))


def geodesic_isolines(
    mesh: VerticesFaces,
    sources: List[int],
    isovalues: List[float],
) -> PolylinesNumpy:
    """Extract isoline polylines from geodesic distance field.

    Computes geodesic distances and extracts polylines along specified isovalues.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        A triangulated mesh as a tuple of vertices and faces.
    sources : List[int]
        Source vertex indices for geodesic distance computation.
    isovalues : List[float]
        Isovalue thresholds for isoline extraction.

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        List of polyline segments as Nx3 arrays of points.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")

    return list(_geodesic_isolines(V, F, sources, isovalues))
