import numpy as np
from numpy.typing import NDArray

from ._types_std import VectorDouble
from ._types_std import VectorVectorInt

def mesh_skeleton(vertices: NDArray[np.float64], faces: NDArray[np.int32]) -> tuple[VectorDouble, VectorDouble, VectorVectorInt, VectorVectorInt]: ...
