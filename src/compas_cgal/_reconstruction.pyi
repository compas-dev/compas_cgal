import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int32]

def poisson_surface_reconstruction(
    points: FloatArray,
    normals: FloatArray,
    sm_angle: float = 20.0,
    sm_radius: float = 30.0,
    sm_distance: float = 0.375,
) -> tuple[FloatArray, IntArray]: ...
def pointset_outlier_removal(points: FloatArray, num_neighbors: int, radius: float) -> FloatArray: ...
def pointset_reduction(points: FloatArray, spacing: float = 2.0) -> FloatArray: ...
def pointset_smoothing(points: FloatArray, num_neighbors: int = 8, num_iterations: int = 1) -> FloatArray: ...
def pointset_normal_estimation(points: FloatArray, num_neighbors: int = 8, erase_unoriented: bool = True) -> tuple[FloatArray, FloatArray]: ...
