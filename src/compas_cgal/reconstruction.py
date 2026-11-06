import numpy as np
from compas.typing import PointsLike

from compas_cgal import _reconstruction

from ._mesh import validate_native_mesh
from .types import FloatNx3
from .types import IntNx3

__all__ = [
    "pointset_normal_estimation",
    "pointset_outlier_removal",
    "pointset_reduction",
    "pointset_smoothing",
    "poisson_surface_reconstruction",
]


def _as_pointset(points: PointsLike, name: str) -> FloatNx3:
    """Convert a structural point set to a native `(N, 3)` array."""
    array = np.ascontiguousarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"{name} should have shape (N, 3).")
    return array


def _validate_pointset(result: FloatNx3, operation: str, expected_rows: int | None = None) -> FloatNx3:
    """Check the shape and optional cardinality of a native point-set result."""
    if result.ndim != 2 or result.shape[1] != 3:
        raise RuntimeError(f"CGAL {operation} result should have shape (N, 3).")
    if expected_rows is not None and len(result) != expected_rows:
        raise RuntimeError(f"CGAL {operation} result should contain {expected_rows} points, got {len(result)}.")
    return result


def poisson_surface_reconstruction(
    points: PointsLike,
    normals: PointsLike,
    sm_angle: float = 20.0,
    sm_radius: float = 30.0,
    sm_distance: float = 0.375,
) -> tuple[FloatNx3, IntNx3]:
    """Reconstruct a surface from a point cloud using the Poisson surface reconstruction algorithm.

    Parameters
    ----------
    points
        The points of the point cloud as an `(N, 3)` array-like object.
    normals
        The normals of the point cloud as an `(N, 3)` array-like object.
    sm_angle : float, optional
        Surface meshing angle bound in degrees.
        Controls the minimum angle of triangles in the output mesh.
        Default is 20.0.
    sm_radius : float, optional
        Surface meshing radius bound as a factor of average spacing.
        Controls the size of triangles relative to the point cloud density.
        Larger values result in coarser meshes with fewer vertices.
        Default is 30.0.
    sm_distance : float, optional
        Surface meshing approximation error bound as a factor of average spacing.
        Controls how closely the mesh approximates the implicit surface.
        Larger values result in coarser meshes with fewer vertices that may deviate more from the original point cloud.
        Default is 0.375.

    Returns
    -------
    tuple[numpy.ndarray]
        The vertices and faces of the reconstructed surface.

    Raises
    ------
    ValueError
        If points or normals are not 3D
        If number of points and normals don't match
        If less than 3 points are provided
        If points are not well-distributed for reconstruction
    RuntimeError
        If the reconstruction algorithm fails

    Notes
    -----
    The Poisson surface reconstruction algorithm requires:
    1. A sufficiently dense point cloud
    2. Well-oriented normals
    3. Points distributed across a meaningful surface

    The surface meshing parameters (sm_angle, sm_radius, sm_distance) control the quality and
    density of the output mesh. Increasing sm_radius and sm_distance will typically result in
    fewer mesh vertices, which can help filter out vertices that don't belong to the original
    point cloud, but may also reduce detail.

    Examples
    --------
    >>> points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    >>> normals = [[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]]
    >>> V, F = poisson_surface_reconstruction(points, normals)
    >>> # Use larger sm_radius and sm_distance to reduce mesh complexity
    >>> V, F = poisson_surface_reconstruction(points, normals, sm_radius=50.0, sm_distance=0.5)
    """
    P = _as_pointset(points, "points")
    N = _as_pointset(normals, "normals")

    if P.shape[0] != N.shape[0]:
        raise ValueError("Number of points and normals must match")
    if len(P) < 3:
        raise ValueError("At least 3 points are required")

    # Ensure normals are unit vectors
    norms = np.linalg.norm(N, axis=1)
    if not np.allclose(norms, 1.0):
        N = N / norms[:, np.newaxis]

    try:
        result = _reconstruction.poisson_surface_reconstruction(P, N, sm_angle, sm_radius, sm_distance)
        return validate_native_mesh(result, "Poisson reconstruction")
    except RuntimeError as e:
        raise RuntimeError(f"Poisson surface reconstruction failed: {str(e)}")


def pointset_outlier_removal(
    points: PointsLike,
    nnnbrs: int = 10,
    radius: float = 1.0,
) -> FloatNx3:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points
        The points of the point cloud as an `(N, 3)` array-like object.
    nnnbrs
        The number of nearest neighbors to consider for each point.
    radius
        The radius of the sphere to consider for each point as a multiplication factor of the average point spacing.

    Returns
    -------
    numpy.ndarray
        The points of the point cloud without outliers.

    """
    P = _as_pointset(points, "points")
    result = _reconstruction.pointset_outlier_removal(P, nnnbrs, radius)
    return _validate_pointset(result, "point-set outlier removal")


def pointset_reduction(
    points: PointsLike,
    spacing: float = 2,
) -> FloatNx3:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points
        The points of the point cloud as an `(N, 3)` array-like object.
    spacing
        The cell size.

    Returns
    -------
    numpy.ndarray
        The vectors of the point cloud.

    """
    P = _as_pointset(points, "points")
    result = _reconstruction.pointset_reduction(P, spacing)
    return _validate_pointset(result, "point-set reduction")


def pointset_smoothing(
    points: PointsLike,
    neighbors: int = 8,
    iterations: int = 1,
) -> FloatNx3:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points
        The points of the point cloud as an `(N, 3)` array-like object.
    neighbors
        The number of nearest neighbors to consider for each point.

    Returns
    -------
    numpy.ndarray
        The vectors of the point cloud.

    """
    P = _as_pointset(points, "points")
    result = _reconstruction.pointset_smoothing(P, neighbors, iterations)
    return _validate_pointset(result, "point-set smoothing", expected_rows=len(P))


def pointset_normal_estimation(
    points: PointsLike,
    neighbors: int = 8,
    erase: bool = False,
) -> tuple[FloatNx3, FloatNx3]:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points
        The points of the point cloud as an `(N, 3)` array-like object.
    neighbors
        The number of nearest neighbors to consider for each point.
    erase
        Erase points that are not oriented properly.

    Returns
    -------
    numpy.ndarray
        The vectors of the point cloud.

    """
    P = _as_pointset(points, "points")
    result = _reconstruction.pointset_normal_estimation(P, neighbors, erase)
    if len(result) != 2:
        raise RuntimeError("CGAL point-set normal estimation should return points and normals.")
    result_points, result_normals = result
    result_points = _validate_pointset(result_points, "point-set normal estimation points")
    result_normals = _validate_pointset(result_normals, "point-set normal estimation normals", expected_rows=len(result_points))
    return result_points, result_normals
