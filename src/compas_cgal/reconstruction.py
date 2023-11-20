from __future__ import annotations
import numpy as np
from compas_cgal._cgal import reconstruction


def poisson_surface_reconstruction(points, normals):
    P = np.asarray(points, dtype=np.float64)
    N = np.asarray(normals, dtype=np.float64)
    return reconstruction.poisson_surface_reconstruction(P, N)
