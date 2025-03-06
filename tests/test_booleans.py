import pytest
import numpy as np

from compas.geometry import Box, Sphere
from compas.datastructures import Mesh

from compas_cgal.booleans import (
    boolean_union_mesh_mesh,
    boolean_difference_mesh_mesh,
    boolean_intersection_mesh_mesh,
    split_mesh_mesh,
)


@pytest.fixture
def box_sphere_meshes():
    """Create test box and sphere meshes."""
    box = Box.from_width_height_depth(2.0, 2.0, 2.0)
    sphere = Sphere(1.0, point=[1, 1, 1])

    box_mesh = box.to_vertices_and_faces(triangulated=True)
    sphere_mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    return box_mesh, sphere_mesh


def test_boolean_union(box_sphere_meshes):
    """Test boolean union operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = boolean_union_mesh_mesh(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3  # 3D points
    assert faces.shape[1] == 3  # Triangle faces
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify topology
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()
    assert mesh.euler() == 2  # Valid closed manifold


def test_boolean_difference(box_sphere_meshes):
    """Test boolean difference operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = boolean_difference_mesh_mesh(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3
    assert faces.shape[1] == 3
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify topology
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()
    assert mesh.euler() == 2  # Valid closed manifold


def test_boolean_intersection(box_sphere_meshes):
    """Test boolean intersection operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = boolean_intersection_mesh_mesh(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3
    assert faces.shape[1] == 3
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify topology
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()
    assert mesh.euler() == 2  # Valid closed manifold


def test_split(box_sphere_meshes):
    """Test mesh split operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = split_mesh_mesh(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3
    assert faces.shape[1] == 3
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify components
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()

    # Split should create at least 2 connected vertex groups
    components = list(mesh.connected_vertices())
    print(components)
    assert len(components) >= 2
