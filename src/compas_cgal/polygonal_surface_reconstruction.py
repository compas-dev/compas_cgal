from typing import Union

import numpy as np
from compas.geometry import Point
from compas.geometry import Vector

from compas_cgal.cgal import polygonal_surface_reconstruction

from .types import FloatNx3


def polygonal_surface_reconstruction_ransac(
    points: Union[list[Point], FloatNx3],
    normals: Union[list[Vector], FloatNx3],
):
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

    """

    P = np.asarray(points, dtype=np.float64)
    N = np.asarray(normals, dtype=np.float64)
    return polygonal_surface_reconstruction.polygonal_surface_reconstruction_ransac(P, N)
