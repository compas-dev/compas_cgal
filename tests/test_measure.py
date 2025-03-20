"""Tests for COMPAS CGAL measure functionality."""

import pytest
from compas.geometry import Box
from compas.datastructures import Mesh
from compas_cgal.measure import mesh_area, mesh_volume, mesh_centroid


def test_area():
    """Test area computation with a unit cube."""
    box = Box.from_width_height_depth(1, 1, 1)
    mesh = Mesh.from_vertices_and_faces(*box.to_vertices_and_faces())
    mesh.quads_to_triangles()
    V, F = mesh.to_vertices_and_faces()

    # Unit cube has 6 faces, each 1x1 = total area of 6
    assert pytest.approx(mesh_area((V, F))) == 6.0


def test_volume():
    """Test volume computation with a unit cube."""
    box = Box.from_width_height_depth(1, 1, 1)
    mesh = Mesh.from_vertices_and_faces(*box.to_vertices_and_faces())
    mesh.quads_to_triangles()
    V, F = mesh.to_vertices_and_faces()

    # Unit cube has volume of 1
    assert pytest.approx(mesh_volume((V, F))) == 1.0


def test_centroid():
    """Test centroid computation with a unit cube."""
    box = Box.from_width_height_depth(1, 1, 1)
    mesh = Mesh.from_vertices_and_faces(*box.to_vertices_and_faces())
    mesh.quads_to_triangles()
    V, F = mesh.to_vertices_and_faces()

    # Centroid should be at origin (0,0,0)
    result = mesh_centroid((V, F))
    assert pytest.approx(result) == [0.0, 0.0, 0.0]
