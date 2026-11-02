import numpy as np
from numpy.typing import NDArray

from ._types_std import VectorRowMatrixXd

def intersection_mesh_mesh(
    vertices_a: NDArray[np.float64],
    faces_a: NDArray[np.int32],
    vertices_b: NDArray[np.float64],
    faces_b: NDArray[np.int32],
) -> VectorRowMatrixXd: ...
