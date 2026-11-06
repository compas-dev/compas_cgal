import numpy as np
from numpy.typing import NDArray

from ._types_std import VectorRowMatrixXd

def slice_mesh(
    vertices: NDArray[np.float64],
    faces: NDArray[np.int32],
    points: NDArray[np.float64],
    normals: NDArray[np.float64],
) -> VectorRowMatrixXd: ...
