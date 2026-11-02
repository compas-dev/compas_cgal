import numpy as np
from numpy.typing import NDArray

from ._types_std import VectorRowMatrixXd

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int32]
Mesh = tuple[FloatArray, IntArray]

def delaunay_triangulation(vertices: FloatArray) -> IntArray: ...
def constrained_delaunay_triangulation(
    boundary_vertices: FloatArray,
    internal_vertices: FloatArray,
    holes: VectorRowMatrixXd,
    curves: VectorRowMatrixXd,
    is_conforming: bool = False,
) -> Mesh: ...
def refined_delaunay_mesh(
    boundary_vertices: FloatArray,
    internal_vertices: FloatArray,
    holes: VectorRowMatrixXd,
    curves: VectorRowMatrixXd,
    min_angle: float = 0.0,
    max_length: float = 0.0,
    is_optimized: bool = True,
) -> Mesh: ...
