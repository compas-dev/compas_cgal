from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

def isolines(
    vertices: NDArray[np.float64],
    faces: NDArray[np.int32],
    scalars: NDArray[np.float64],
    isovalues: Sequence[float],
    refine: int = 0,
) -> list[NDArray[np.float64]]: ...
