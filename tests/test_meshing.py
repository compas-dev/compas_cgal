"""Tests for COMPAS CGAL meshing functionality."""

import pytest
import numpy as np
from compas.datastructures import Mesh
from compas.geometry import Tessellation, trimesh_remesh
from compas_cgal.meshing import trimesh_dual


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
        [0, 1, 2],
        [0, 2, 3],
        [4, 6, 5],
        [4, 7, 6],
        [0, 5, 1],
        [0, 4, 5],
        [2, 7, 3],
        [2, 6, 7],
        [0, 3, 7],
        [0, 7, 4],
        [1, 5, 6],
        [1, 6, 2],
    ]
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    return mesh


def test_remesh(sample_mesh):
    """Test the remeshing functionality."""
    # Get mesh data
    V, F = sample_mesh.to_vertices_and_faces()

    # Test parameters
    target_edge_length = 0.5
    num_iterations = 10

    # Run remeshing
    result = trimesh_remesh(Tessellation(V, F), target_edge_length, num_iterations)
    V_new, F_new = result.to_vertices_and_triangles()

    # Verify output types and shapes
    assert isinstance(result, Tessellation)
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


def test_remesh_rejects_vertex_face_tuple(sample_mesh):
    with pytest.raises(TypeError, match="Tessellation"):
        trimesh_remesh(sample_mesh.to_vertices_and_faces(), 0.5)


def test_dual(sample_mesh):
    """Test the dual functionality."""
    # Get mesh data
    V, F = sample_mesh.to_vertices_and_faces()

    # Test parameters
    length_factor = 1
    num_iterations = 10

    # Run remeshing
    V_new, F_new, V_dual, F_dual = trimesh_dual((V, F), length_factor, num_iterations)

    # Verify mesh is valid
    remeshed_mesh = Mesh.from_vertices_and_faces(V_new, F_new)
    assert remeshed_mesh.is_valid()

    # Verify dual mesh is valid
    dual_mesh = Mesh.from_vertices_and_faces(V_dual, F_dual)
    assert dual_mesh.is_valid()
