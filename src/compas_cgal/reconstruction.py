from typing import Tuple
from typing import Union

import numpy as np
from compas.geometry import Point
from compas.geometry import Vector

from compas_cgal.compas_cgal_ext import reconstruction

from .types import FloatNx3
from .types import IntNx3


def poisson_surface_reconstruction(
    points: Union[list[Point], FloatNx3],
    normals: Union[list[Vector], FloatNx3],
) -> Tuple[FloatNx3, IntNx3]:
    """Reconstruct a surface from a point cloud using the Poisson surface reconstruction algorithm.

    Parameters
    ----------
    points : list of :class:`compas.geometry.Point` or :class:`numpy.ndarray`
        The points of the point cloud.
    normals : list of :class:`compas.geometry.Vector` or :class:`numpy.ndarray`
        The normals of the point cloud.

    Returns
    -------
    tuple of :class:`numpy.ndarray`
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
    """
    # Convert input to numpy arrays with proper type and memory layout
    P = np.asarray(points, dtype=np.float64, order="C")
    N = np.asarray(normals, dtype=np.float64, order="C")

    # Input validation
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError("Points must be an Nx3 array")
    if N.ndim != 2 or N.shape[1] != 3:
        raise ValueError("Normals must be an Nx3 array")
    if P.shape[0] != N.shape[0]:
        raise ValueError("Number of points and normals must match")
    if len(P) < 3:
        raise ValueError("At least 3 points are required")

    # Ensure normals are unit vectors
    norms = np.linalg.norm(N, axis=1)
    if not np.allclose(norms, 1.0):
        N = N / norms[:, np.newaxis]

    try:
        return reconstruction.poisson_surface_reconstruction(P, N)
    except RuntimeError as e:
        raise RuntimeError(f"Poisson surface reconstruction failed: {str(e)}")


def pointset_outlier_removal(
    points: Union[list[Point], FloatNx3],
    nnnbrs: int = 10,
    radius: float = 1.0,
) -> FloatNx3:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points : list of :class:`compas.geometry.Point` or :class:`numpy.ndarray`
        The points of the point cloud.
    nnnbrs : int, optional
        The number of nearest neighbors to consider for each point.
    radius : float, optional
        The radius of the sphere to consider for each point as a multiplication factor of the average point spacing.

    Returns
    -------
    :class:`numpy.ndarray`
        The points of the point cloud without outliers.

    """
    P = np.asarray(points, dtype=np.float64, order="C")
    return reconstruction.pointset_outlier_removal(P, nnnbrs, radius)


def pointset_reduction(
    points: Union[list[Point], FloatNx3],
    spacing: float = 2,
) -> FloatNx3:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points : list of :class:`compas.geometry.Point` or :class:`numpy.ndarray`
        The points of the point cloud.
    spacing : int, optional
        The cell size.

    Returns
    -------
    :class:`numpy.ndarray`
        The vectors of the point cloud.

    """
    P = np.asarray(points, dtype=np.float64, order="C")
    return reconstruction.pointset_reduction(P, spacing)


def pointset_smoothing(
    points: Union[list[Point], FloatNx3],
    neighbors: int = 8,
    iterations: int = 1,
) -> FloatNx3:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points : list of :class:`compas.geometry.Point` or :class:`numpy.ndarray`
        The points of the point cloud.
    neighbors : int, optional
        The number of nearest neighbors to consider for each point.

    Returns
    -------
    :class:`numpy.ndarray`
        The vectors of the point cloud.

    """
    P = np.asarray(points, dtype=np.float64, order="C")
    return reconstruction.pointset_smoothing(P, neighbors, iterations)


def pointset_normal_estimation(
    points: Union[list[Point], FloatNx3],
    neighbors: int = 8,
    erase: bool = False,
) -> Tuple[FloatNx3, FloatNx3]:
    """Remove outliers from a point cloud using the point set outlier removal algorithm.

    Parameters
    ----------
    points : list of :class:`compas.geometry.Point` or :class:`numpy.ndarray`
        The points of the point cloud.
    neighbors : int, optional
        The number of nearest neighbors to consider for each point.
    erase : bool, optional
        Erase points that are not oriented properly.

    Returns
    -------
    :class:`numpy.ndarray`
        The vectors of the point cloud.

    """
    P = np.asarray(points, dtype=np.float64, order="C")
    return reconstruction.pointset_normal_estimation(P, neighbors, erase)
