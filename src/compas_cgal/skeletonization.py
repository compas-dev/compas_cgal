from __future__ import annotations
from .types import VerticesFaces
from .types import PolylinesNumpy
import numpy as np
from compas_cgal._cgal import skeletonization


def mesh_skeleton(mesh: VerticesFaces) -> PolylinesNumpy:
    """Compute the skeleton of a closed triangle mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to skeletonize.

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        The skeleton of the mesh.

    """
    V, F = mesh
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return skeletonization.mesh_skeleton(V, F)
