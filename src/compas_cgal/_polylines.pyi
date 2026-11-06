import numpy as np
from numpy.typing import NDArray

from ._types_std import VectorRowMatrixXd

FloatArray = NDArray[np.float64]

def simplify_polylines(polylines: list[FloatArray], threshold: float) -> VectorRowMatrixXd: ...
def closest_points_on_polyline(query_points: FloatArray, polyline: FloatArray) -> FloatArray: ...
