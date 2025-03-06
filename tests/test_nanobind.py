import numpy as np
from compas_cgal.compas_cgal_ext import scale_matrix, create_matrix, add


def test_add_binding():
    """Test adding two numbers using C++ binding."""
    result = add(1, 2)
    assert result == 3


def test_scale_matrix_binding():
    """Test scaling a matrix using C++ binding."""
    # Create test matrix with exact values
    input_matrix = np.array(
        [[1.1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]],
        dtype=np.float64,
        order="C",  # C-style, row-major order to match Eigen::RowMajor
    )

    expected = np.array([[2.2, 4.4, 6.6], [8.8, 11.0, 13.2], [15.4, 17.6, 19.8]])

    # Make copy for testing since scale_matrix modifies in-place
    test_matrix = input_matrix.copy()
    scale_matrix(test_matrix)  # Function modifies array in-place

    # Test in-place modification with exact values
    np.testing.assert_array_almost_equal(test_matrix, expected)


def test_create_matrix_binding():
    """Test creating a matrix using C++ binding."""
    result = create_matrix()

    # Test exact values
    expected = np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]])

    # Test shape and type
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.float64
    assert result.flags["C_CONTIGUOUS"]  # Check row-major order
    assert result.shape == (3, 3)

    # Test exact values
    np.testing.assert_array_almost_equal(result, expected)
