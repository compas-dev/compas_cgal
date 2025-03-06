import pytest
import numpy as np
from compas.datastructures import Mesh
from compas_cgal import remesh


@pytest.fixture
def sample_mesh():
    """Create a simple cube mesh for testing."""
    vertices = [
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
    ]
    faces = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],  # top, bottom
        [0, 1, 5, 4],
        [2, 3, 7, 6],  # front, back
        [0, 3, 7, 4],
        [1, 2, 6, 5],  # left, right
    ]
    return Mesh.from_vertices_and_faces(vertices, faces)


def test_remesh(sample_mesh):
    """Test the remeshing functionality."""
    # Convert mesh to arrays
    vertices, faces = sample_mesh.to_vertices_and_faces()
    vertices = np.asarray(vertices, dtype=np.float64, order="C")
    faces = np.asarray(faces, dtype=np.int32, order="C")

    # Test parameters
    target_edge_length = 0.5
    num_iterations = 10

    # Run remeshing
    remeshed_vertices, remeshed_faces = remesh(
        vertices, faces, target_edge_length, num_iterations
    )

    # Verify output types and shapes
    assert isinstance(remeshed_vertices, np.ndarray)
    assert isinstance(remeshed_faces, np.ndarray)
    assert remeshed_vertices.dtype == np.float64
    assert remeshed_faces.dtype == np.int32
    assert remeshed_vertices.flags["C_CONTIGUOUS"]  # Check row-major order
    assert remeshed_faces.flags["C_CONTIGUOUS"]
    assert remeshed_vertices.shape[1] == 3  # 3D points
    assert remeshed_faces.shape[1] >= 3  # At least triangular faces

    # Verify mesh is valid
    remeshed_mesh = Mesh.from_vertices_and_faces(remeshed_vertices, remeshed_faces)
    assert remeshed_mesh.is_valid()
