"""Tests for COMPAS CGAL meshing functionality."""

import pytest
import numpy as np
from compas.datastructures import Mesh
from compas_cgal.meshing import mesh_remesh


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
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    mesh.quads_to_triangles()
    return mesh


def test_remesh(sample_mesh):
    """Test the remeshing functionality."""
    # Get mesh data
    V, F = sample_mesh.to_vertices_and_faces()

    # Test parameters
    target_edge_length = 0.5
    num_iterations = 10

    # Run remeshing
    V_new, F_new = mesh_remesh((V, F), target_edge_length, num_iterations)

    # Verify output types and shapes
    assert isinstance(V_new, np.ndarray)
    assert isinstance(F_new, np.ndarray)
    assert V_new.dtype == np.float64
    assert F_new.dtype == np.int32
    assert V_new.flags["C_CONTIGUOUS"]  # Check row-major order
    assert F_new.flags["C_CONTIGUOUS"]
    assert V_new.shape[1] == 3  # 3D points
    assert F_new.shape[1] == 3  # Triangular faces

    # Verify mesh is valid
    remeshed_mesh = Mesh.from_vertices_and_faces(V_new, F_new)
    assert remeshed_mesh.is_valid()
