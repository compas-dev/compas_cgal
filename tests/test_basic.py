"""Basic tests for COMPAS CGAL functionality."""

from compas_cgal import scale_matrix, create_matrix, add
import numpy as np


def test_add():
    """Test the add function from COMPAS CGAL."""
    result = add(1, 2)
    print(f"Adding 1 + 2 = {result}")
    assert result == 3
    return result


def test_matrix_operations():
    """Test matrix operations using COMPAS CGAL's C++ bindings."""
    # Create a NumPy array in row-major order to match Eigen::RowMajor
    mat = np.array(
        [[1.1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]],
        dtype=np.float64,
        order="C",  # C-style, row-major order to match Eigen::RowMajor
    )
    mat.flags.writeable = True  # Ensure the array is writeable
    
    print("Original matrix:")
    print(mat)

    # Scale the matrix in-place
    scale_matrix(mat)
    print("\nMatrix after scaling:")
    print(mat)

    # Get a new matrix from C++
    returned_matrix = create_matrix()
    print("\nMatrix created by C++:")
    print(returned_matrix)
    
    # Verify the returned matrix is row-major ordered
    assert isinstance(returned_matrix, np.ndarray)
    assert returned_matrix.flags['C_CONTIGUOUS']  # Verify row-major order
    return mat, returned_matrix


if __name__ == "__main__":
    print("Running add test...")
    test_add()
    
    print("\nRunning matrix operations test...")
    test_matrix_operations()
