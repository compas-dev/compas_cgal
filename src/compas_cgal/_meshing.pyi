from collections.abc import Sequence
from typing import Any
from typing import SupportsIndex

import numpy as np
from numpy.typing import NDArray

from ._types_std import VectorInt
from ._types_std import VectorVectorInt

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int32]
IntegerArray = NDArray[np.integer[Any]]
Mesh = tuple[FloatArray, IntArray]

def pmp_trimesh_remesh(
    vertices_a: FloatArray,
    faces_a: IntArray,
    target_edge_length: float,
    number_of_iterations: int = 10,
    do_project: bool = True,
    protect_boundary: bool = False,
    protect_sharp_edges_angle_deg: float = 0.0,
    keep_points: FloatArray = ...,
) -> Mesh: ...
def pmp_trimesh_remesh_dual(
    vertices_a: FloatArray,
    faces_a: IntArray,
    fixed_vertices: IntegerArray | Sequence[SupportsIndex] | VectorInt,
    length_factor: float = 1,
    number_of_iterations: int = 10,
    angle_radians: float = 0.9,
    scale_factor: float = 1.0,
) -> tuple[FloatArray, IntArray, FloatArray, VectorVectorInt]: ...
def pmp_pull(vertices_a: FloatArray, faces_a: IntArray, vertices_b: FloatArray, normals_b: FloatArray) -> None: ...
def pmp_project(vertices_a: FloatArray, faces_a: IntArray, vertices_b: FloatArray) -> None: ...
