import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

def simplify_polylines(polylines: list[FloatArray], threshold: float) -> list[FloatArray]: ...
def closest_points_on_polyline(query_points: FloatArray, polyline: FloatArray) -> FloatArray: ...
