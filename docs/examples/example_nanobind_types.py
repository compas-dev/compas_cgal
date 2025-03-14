from compas_cgal.compas_cgal_ext import scale_matrix, create_matrix, add
import numpy as np
from line_profiler import profile


@profile
def add_binding(a: int = 1, b: int = 2) -> int:
    """Add two numbers in C++."""
    result = add(a, b)
    return result


@profile
def scale_matrix_binding(mat: np.ndarray) -> None:
    """Scale a NumPy matrix in-place using C++ and transfer to Python."""
    mat.flags.writeable = True
    scale_matrix(mat)
    return mat


@profile
def create_matrix_binding() -> np.ndarray:
    """Create a NumPy matrix in C++ and transfer to Python."""
    mat: np.ndarray = create_matrix()
    return mat


m = np.array(
    [[1.1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]],
    dtype=np.float64,
    order="C",  # C-style, row-major order to match Eigen::RowMajor
)

print("Sum of 1 and 2 is:\n", add_binding(1, 2), "\n")
print("Input matrix:\n", m)
print("Scaled matrix:\n", scale_matrix_binding(m), "\n")
print("Created matrix:\n", create_matrix_binding(), "\n")
