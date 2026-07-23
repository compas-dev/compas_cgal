"""Tests for COMPAS CGAL meshing functionality."""

import pytest
import numpy as np
from compas.datastructures import Mesh
from compas_cgal.meshing import trimesh_remesh, trimesh_dual


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
    V_new, F_new = trimesh_remesh((V, F), target_edge_length, num_iterations)

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


@pytest.fixture
def square_with_hole():
    """Annular layer: square outer boundary, square hole in the middle.

    Tests boundary preservation on a topology with TWO loops (outer + hole).
    """
    outer = [[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [4.0, 4.0, 0.0], [0.0, 4.0, 0.0]]
    inner = [[1.0, 1.0, 0.0], [3.0, 1.0, 0.0], [3.0, 3.0, 0.0], [1.0, 3.0, 0.0]]
    V = np.asarray(outer + inner, dtype=np.float64)
    # Fan-triangulate the annulus: connect each outer corner to two inner
    # corners. 8 triangles total.
    F = np.asarray(
        [
            [0, 1, 5],
            [0, 5, 4],
            [1, 2, 6],
            [1, 6, 5],
            [2, 3, 7],
            [2, 7, 6],
            [3, 0, 4],
            [3, 4, 7],
        ],
        dtype=np.int32,
    )
    return V, F


def _corner_set(V, atol=1e-6):
    return {tuple(np.round(p / atol).astype(int)) for p in V}


def test_remesh_default_subdivides_boundary(square_with_hole):
    """Without protect_boundary the boundary IS subdivided (default CGAL behaviour)."""
    V, F = square_with_hole
    V_new, F_new = trimesh_remesh((V, F), target_edge_length=0.5, number_of_iterations=5)
    # Boundary subdivision adds vertices on outer + inner loops.
    assert V_new.shape[0] > V.shape[0], f"default mode should add boundary verts; got {V_new.shape[0]} <= {V.shape[0]}"


def test_remesh_protect_boundary_keeps_corners(square_with_hole):
    """With protect_boundary=True every original corner survives verbatim."""
    V, F = square_with_hole
    V_new, F_new = trimesh_remesh(
        (V, F),
        target_edge_length=0.5,
        number_of_iterations=5,
        protect_boundary=True,
    )
    new_corners = _corner_set(V_new)
    orig_corners = _corner_set(V)
    missing = orig_corners - new_corners
    assert not missing, f"protect_boundary lost original corners: {missing}"


def test_remesh_protect_boundary_keeps_boundary_vertex_count(square_with_hole):
    """protect_boundary=True must not insert NEW vertices along the boundary loops.

    Bounds the boundary-vertex count to the original 8 (4 outer + 4 inner).
    """
    V, F = square_with_hole
    V_new, F_new = trimesh_remesh(
        (V, F),
        target_edge_length=0.5,
        number_of_iterations=5,
        protect_boundary=True,
    )
    # Count vertices that lie on the original boundary segments. The 8
    # original corners are all collinear with the outer/inner square edges.
    # Any remeshed vertex on a boundary edge can be detected by checking
    # if its half-edge has no twin in the new mesh.
    he_set = set()
    for face in F_new:
        for k in range(3):
            i, j = int(face[k]), int(face[(k + 1) % 3])
            he_set.add((i, j))
    boundary_verts = set()
    for i, j in he_set:
        if (j, i) not in he_set:
            boundary_verts.add(i)
            boundary_verts.add(j)
    # Original boundary had 8 verts (4 outer + 4 inner); protect_boundary
    # forbids splitting boundary edges so count must stay exactly 8.
    assert len(boundary_verts) == 8, f"protect_boundary=True must keep 8 boundary verts; got {len(boundary_verts)}"


def test_remesh_protect_sharp_edges_default_disabled():
    """protect_sharp_edges_angle_deg=0.0 (default) must not affect output."""
    # Two co-planar triangles sharing an interior edge — no sharp dihedral.
    V = np.asarray([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float64)
    F = np.asarray([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
    V_a, F_a = trimesh_remesh((V, F), 0.3, number_of_iterations=5)
    V_b, F_b = trimesh_remesh((V, F), 0.3, number_of_iterations=5, protect_sharp_edges_angle_deg=0.0)
    np.testing.assert_array_equal(V_a.shape, V_b.shape)
    np.testing.assert_array_equal(F_a.shape, F_b.shape)


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
