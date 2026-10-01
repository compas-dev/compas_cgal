"""Geodesic distance computation using the heat method."""

from typing import List
from typing import Literal
from typing import Sequence
from typing import Tuple
from typing import Union
from typing import overload

import numpy as np
from compas.datastructures import Mesh
from numpy.typing import NDArray

from compas_cgal import _types_std  # noqa: F401  # Load vector type bindings
from compas_cgal._geodesics import ExactGeodesicSolver as _ExactGeodesicSolver
from compas_cgal._geodesics import HeatGeodesicSolver as _HeatGeodesicSolver
from compas_cgal._geodesics import exact_geodesic_distances as _exact_geodesic_distances
from compas_cgal._geodesics import exact_geodesic_distances_from_points as _exact_geodesic_distances_from_points
from compas_cgal._geodesics import geodesic_isolines as _geodesic_isolines
from compas_cgal._geodesics import geodesic_isolines_split as _geodesic_isolines_split
from compas_cgal._geodesics import heat_geodesic_distances as _heat_geodesic_distances
from compas_cgal.types import PolylinesNumpy
from compas_cgal.types import VerticesFaces
from compas_cgal.types import VerticesFacesNumpy

__all__ = [
    "heat_geodesic_distances",
    "HeatGeodesicSolver",
    "exact_geodesic_distances",
    "exact_geodesic_distances_from_points",
    "ExactGeodesicSolver",
    "geodesic_isolines_split",
    "geodesic_isolines",
]

MeshInput = Union[Mesh, VerticesFaces]
"""A triangulated mesh, accepted either as a :class:`compas.datastructures.Mesh`
or as a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces."""

PointsLike = Union[NDArray, Sequence[Sequence[float]]]
"""Source points, as an (S, 3) array or a sequence of XYZ triples such as a list of
:class:`compas.geometry.Point`."""


def _as_vertices_faces(mesh: MeshInput) -> Tuple[NDArray, NDArray]:
    """Coerce a mesh (compas ``Mesh`` or ``(V, F)`` tuple) to CGAL-ready arrays.

    Single marshalling seam for every geodesics entry point: vertices as a
    C-contiguous ``float64`` Nx3 array, faces as a C-contiguous ``int32`` Fx3
    array. The mesh must be triangulated.
    """
    if isinstance(mesh, Mesh):
        V, F = mesh.to_vertices_and_faces()
    else:
        V, F = mesh
    V = np.asarray(V, dtype=np.float64, order="C")
    F = np.asarray(F, dtype=np.int32, order="C")
    return V, F


@overload
def heat_geodesic_distances(mesh: Mesh, sources: List[int]) -> NDArray: ...
@overload
def heat_geodesic_distances(mesh: VerticesFaces, sources: List[int]) -> NDArray: ...
def heat_geodesic_distances(mesh: MeshInput, sources: List[int]) -> NDArray:
    """Compute geodesic distances from source vertices using the heat method.

    Heat method (Crane et al. 2017) with a Dirichlet-constrained Poisson step:
    the distance is exactly 0 at every source vertex and remains accurate for
    multi-vertex source sets (e.g. all boundary vertices of an open mesh).

    Parameters
    ----------
    mesh : :attr:`compas_cgal.geodesics.MeshInput`
        A triangulated mesh, either a :class:`compas.datastructures.Mesh`
        or a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces.
    sources : List[int]
        Source vertex indices (at least one; out-of-range indices are ignored).

    Returns
    -------
    NDArray
        Geodesic distances from the nearest source to each vertex.
        Shape is (n_vertices,).

    Raises
    ------
    ValueError
        If no valid source vertex index is given.
    RuntimeError
        If a connected component of the mesh contains no source vertex.

    Examples
    --------
    >>> from compas.geometry import Box
    >>> from compas_cgal.geodesics import heat_geodesic_distances
    >>> box = Box(1)
    >>> mesh = box.to_vertices_and_faces(triangulated=True)
    >>> distances = heat_geodesic_distances(mesh, [0])  # distances from vertex 0

    """
    V, F = _as_vertices_faces(mesh)
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
    mesh : :attr:`compas_cgal.geodesics.MeshInput`
        A triangulated mesh, either a :class:`compas.datastructures.Mesh`
        or a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces.

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

    @overload
    def __init__(self, mesh: Mesh) -> None: ...
    @overload
    def __init__(self, mesh: VerticesFaces) -> None: ...
    def __init__(self, mesh: MeshInput) -> None:
        V, F = _as_vertices_faces(mesh)
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


@overload
def geodesic_isolines_split(mesh: Mesh, sources: List[int], isovalues: List[float]) -> List[VerticesFacesNumpy]: ...
@overload
def geodesic_isolines_split(mesh: VerticesFaces, sources: List[int], isovalues: List[float]) -> List[VerticesFacesNumpy]: ...
def geodesic_isolines_split(mesh: MeshInput, sources: List[int], isovalues: List[float]) -> List[VerticesFacesNumpy]:
    """Split mesh into components along geodesic isolines.

    Computes geodesic distances from sources, refines the mesh along
    specified isovalue thresholds, and splits into connected components.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.geodesics.MeshInput`
        A triangulated mesh, either a :class:`compas.datastructures.Mesh`
        or a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces.
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
    V, F = _as_vertices_faces(mesh)
    vertices_list, faces_list = _geodesic_isolines_split(V, F, sources, isovalues)
    return list(zip(vertices_list, faces_list))


@overload
def geodesic_isolines(mesh: Mesh, sources: List[int], isovalues: List[float]) -> PolylinesNumpy: ...
@overload
def geodesic_isolines(mesh: VerticesFaces, sources: List[int], isovalues: List[float]) -> PolylinesNumpy: ...
def geodesic_isolines(mesh: MeshInput, sources: List[int], isovalues: List[float]) -> PolylinesNumpy:
    """Extract isoline polylines from geodesic distance field.

    Computes geodesic distances and extracts polylines along specified isovalues.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.geodesics.MeshInput`
        A triangulated mesh, either a :class:`compas.datastructures.Mesh`
        or a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces.
    sources : List[int]
        Source vertex indices for geodesic distance computation.
    isovalues : List[float]
        Isovalue thresholds for isoline extraction.

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        List of polyline segments as Nx3 arrays of points.

    """
    V, F = _as_vertices_faces(mesh)
    return list(_geodesic_isolines(V, F, sources, isovalues))


def _as_source_points(points: PointsLike) -> NDArray:
    """Coerce and validate source points to a C-contiguous float64 (S, 3) array.

    Single seam for every point-source entry point. An empty array is rejected here
    rather than in the binding: nanobind cannot bind a zero-row array to an
    ``Eigen::Ref``, so it would raise ``TypeError`` before the binding's own check.
    """
    P = np.asarray(points, dtype=np.float64, order="C")
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError(f"source points require shape (S, 3), got {P.shape}")
    if P.shape[0] == 0:
        raise ValueError("at least one source point is required")
    return P


@overload
def exact_geodesic_distances(mesh: MeshInput, sources: List[int], *, return_sources: Literal[False] = False) -> NDArray: ...
@overload
def exact_geodesic_distances(mesh: MeshInput, sources: List[int], *, return_sources: Literal[True]) -> Tuple[NDArray, NDArray]: ...
def exact_geodesic_distances(mesh: MeshInput, sources: List[int], *, return_sources: bool = False) -> Union[NDArray, Tuple[NDArray, NDArray]]:
    """Exact polyhedral geodesic distances from a set of source vertices.

    Computes the exact polyhedral geodesic (CGAL's `Surface_mesh_shortest_path`),
    evaluated in floating-point arithmetic: the algorithm is exact, its constructions
    are double precision. Distances are exactly 0 at every source vertex and the
    gradient magnitude is 1 by construction, which is what makes this backend usable
    as an accuracy reference for :func:`heat_geodesic_distances`.

    With ``return_sources=False`` the signature and return match
    :func:`heat_geodesic_distances` exactly, so the two backends are interchangeable
    at a call site.

    Cost differs sharply from the heat method even though the interfaces match. The
    heat method is two sparse solves; this is a whole-surface wavefront propagation,
    worst case O(n^2 log n) with sequence-tree memory. Measure before swapping one for
    the other on a large mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.geodesics.MeshInput`
        A triangulated mesh, either a :class:`compas.datastructures.Mesh`
        or a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces.
    sources : List[int]
        Source vertex indices (at least one; out-of-range indices are ignored and
        duplicates collapse).
    return_sources : bool, optional
        If True, also return which source each vertex's geodesic came from.

    Returns
    -------
    NDArray | Tuple[NDArray, NDArray]
        Geodesic distances from the nearest source to each vertex, shape (n_vertices,).
        If ``return_sources`` is True, additionally an int array of the same shape
        holding, for each vertex, the ORDINAL into ``sources`` of the nearest source,
        so that ``sources[ordinal]`` recovers the source vertex index.

    Raises
    ------
    ValueError
        If no valid source vertex index is given.
    RuntimeError
        If a connected component of the mesh contains no source.

    Examples
    --------
    >>> from compas.geometry import Box
    >>> from compas_cgal.geodesics import exact_geodesic_distances
    >>> box = Box(1)
    >>> mesh = box.to_vertices_and_faces(triangulated=True)
    >>> distances = exact_geodesic_distances(mesh, [0])

    """
    V, F = _as_vertices_faces(mesh)
    distances, nearest = _exact_geodesic_distances(V, F, sources)
    if return_sources:
        return distances.flatten(), nearest.flatten()
    return distances.flatten()


@overload
def exact_geodesic_distances_from_points(mesh: MeshInput, points: PointsLike, *, return_sources: Literal[False] = False) -> NDArray: ...
@overload
def exact_geodesic_distances_from_points(mesh: MeshInput, points: PointsLike, *, return_sources: Literal[True]) -> Tuple[NDArray, NDArray]: ...
def exact_geodesic_distances_from_points(mesh: MeshInput, points: PointsLike, *, return_sources: bool = False) -> Union[NDArray, Tuple[NDArray, NDArray]]:
    """Exact geodesic distances from source points located on the surface.

    Unlike vertex sources, a source point may sit anywhere on a face. This is the
    entry point to use when the sources are samples of a curve lying on the surface:
    seeding the samples themselves avoids the error incurred by substituting the
    nearest mesh vertex for each one, which is bounded below by the edge length.

    There is no heat-method counterpart. A heat source is an indicator on vertices,
    and a face-interior source cannot be expressed without splitting the mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.geodesics.MeshInput`
        A triangulated mesh, either a :class:`compas.datastructures.Mesh`
        or a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces.
    points : :attr:`compas_cgal.geodesics.PointsLike`
        Source points, e.g. a list of :class:`compas.geometry.Point`. Each is located on the surface, being
        projected to the closest point on the closest face. Callers that must bound
        that projection should compose with
        :func:`compas_cgal.projection.project_points_on_mesh`, which owns
        point-to-mesh proximity.

        Unlike vertex sources, duplicate points are **not** collapsed: doing so would
        require an equality test on coordinates, that is a positional tolerance, which
        this module does not own. A repeated point leaves the distance field unchanged
        and simply consumes an ordinal.
    return_sources : bool, optional
        If True, also return which source each vertex's geodesic came from.

    Returns
    -------
    NDArray | Tuple[NDArray, NDArray]
        Geodesic distances from the nearest source point to each vertex, shape
        (n_vertices,). If ``return_sources`` is True, additionally the ORDINAL into
        ``points`` of the nearest source, per vertex.

    Raises
    ------
    ValueError
        If ``points`` is empty, not (S, 3), or contains non-finite coordinates.
    RuntimeError
        If a connected component of the mesh contains no source.

    """
    V, F = _as_vertices_faces(mesh)
    P = _as_source_points(points)
    distances, nearest = _exact_geodesic_distances_from_points(V, F, P)
    if return_sources:
        return distances.flatten(), nearest.flatten()
    return distances.flatten()


class ExactGeodesicSolver:
    """Exact geodesic solver retaining one mesh across source sets.

    Use this when computing exact geodesics from several source sets on the same mesh.
    What is reused is narrower than for :class:`HeatGeodesicSolver`, and worth knowing:
    the CGAL mesh and its index maps are built once, and the AABB tree needed to locate
    source points is built on the first such query and never again. The wavefront
    propagation itself belongs to one source set and is redone per solve -- unlike the
    heat method's factorization, it is not reusable in principle.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.geodesics.MeshInput`
        A triangulated mesh, either a :class:`compas.datastructures.Mesh`
        or a :attr:`compas_cgal.types.VerticesFaces` tuple of vertices and faces.

    Examples
    --------
    >>> from compas.geometry import Sphere
    >>> from compas_cgal.geodesics import ExactGeodesicSolver
    >>> sphere = Sphere(1.0)
    >>> mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)
    >>> solver = ExactGeodesicSolver(mesh)
    >>> d0 = solver.solve([0])
    >>> d1 = solver.solve([1])

    """

    @overload
    def __init__(self, mesh: Mesh) -> None: ...
    @overload
    def __init__(self, mesh: VerticesFaces) -> None: ...
    def __init__(self, mesh: MeshInput) -> None:
        V, F = _as_vertices_faces(mesh)
        self._solver = _ExactGeodesicSolver(V, F)

    @overload
    def solve(self, sources: List[int], *, return_sources: Literal[False] = False) -> NDArray: ...
    @overload
    def solve(self, sources: List[int], *, return_sources: Literal[True]) -> Tuple[NDArray, NDArray]: ...
    def solve(self, sources: List[int], *, return_sources: bool = False) -> Union[NDArray, Tuple[NDArray, NDArray]]:
        """Exact geodesic distances from source vertices.

        Parameters
        ----------
        sources : List[int]
            Source vertex indices.
        return_sources : bool, optional
            If True, also return the ordinal into ``sources`` of the nearest source
            per vertex.

        Returns
        -------
        NDArray | Tuple[NDArray, NDArray]
            Distances of shape (n_vertices,), optionally with nearest-source ordinals.

        """
        distances, nearest = self._solver.solve(sources)
        if return_sources:
            return distances.flatten(), nearest.flatten()
        return distances.flatten()

    @overload
    def solve_from_points(self, points: PointsLike, *, return_sources: Literal[False] = False) -> NDArray: ...
    @overload
    def solve_from_points(self, points: PointsLike, *, return_sources: Literal[True]) -> Tuple[NDArray, NDArray]: ...
    def solve_from_points(self, points: PointsLike, *, return_sources: bool = False) -> Union[NDArray, Tuple[NDArray, NDArray]]:
        """Exact geodesic distances from source points located on the surface.

        Parameters
        ----------
        points : :attr:`compas_cgal.geodesics.PointsLike`
            Source points, e.g. a list of :class:`compas.geometry.Point`. Duplicates are
            not collapsed; see :func:`exact_geodesic_distances_from_points`.
        return_sources : bool, optional
            If True, also return the ordinal into ``points`` of the nearest source
            per vertex.

        Returns
        -------
        NDArray | Tuple[NDArray, NDArray]
            Distances of shape (n_vertices,), optionally with nearest-source ordinals.

        """
        P = _as_source_points(points)
        distances, nearest = self._solver.solve_from_points(P)
        if return_sources:
            return distances.flatten(), nearest.flatten()
        return distances.flatten()

    @property
    def num_vertices(self) -> int:
        """Number of vertices in the mesh."""
        return self._solver.num_vertices
