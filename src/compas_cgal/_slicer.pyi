import numpy as np
from numpy.typing import NDArray

def slice_mesh(
    vertices: NDArray[np.float64],
    faces: NDArray[np.int32],
    points: NDArray[np.float64],
    normals: NDArray[np.float64],
) -> list[NDArray[np.float64]]: ...
