from __future__ import annotations

from typing import Any
from typing import Union

import numpy as np
from compas.geometry import Point
from compas.geometry import Vector
from nptyping import Float
from nptyping import NDArray
from nptyping import Shape

from compas_cgal._cgal import polygonal_surface_reconstruction


def polygonal_surface_reconstruction_ransac(
    points: Union[list[Point], NDArray[Shape["Any, 3"], Float]],
    normals: Union[list[Vector], NDArray[Shape["Any, 3"], Float]],
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
