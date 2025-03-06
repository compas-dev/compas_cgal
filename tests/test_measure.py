"""Tests for COMPAS CGAL measure functionality."""

import pytest
import numpy as np
from compas.geometry import Box, Point
from compas.datastructures import Mesh
from compas_cgal import area, volume, centroid


def test_area_binding_unit_cube():
    """Test area computation with a unit cube."""
    # Create a unit cube mesh
    box = Box.from_width_height_depth(1, 1, 1)
    mesh = Mesh.from_vertices_and_faces(*box.to_vertices_and_faces())
    mesh.quads_to_triangles()

    # Convert to numpy arrays
    vertices = np.asarray(mesh.vertices_attributes("xyz"), dtype=np.float64, order="C")
    faces = np.asarray(
        [mesh.face_vertices(face) for face in mesh.faces()], dtype=np.int32, order="C"
    )

    # Unit cube has 6 faces, each 1x1 = total area of 6
    result = area(vertices, faces)
    assert pytest.approx(result) == 6.0


def test_volume_binding_unit_cube():
    """Test volume computation with a unit cube."""
    # Create a unit cube mesh
    box = Box.from_width_height_depth(1, 1, 1)
    mesh = Mesh.from_vertices_and_faces(*box.to_vertices_and_faces())
    mesh.quads_to_triangles()

    # Convert to numpy arrays
    vertices = np.asarray(mesh.vertices_attributes("xyz"), dtype=np.float64, order="C")
    faces = np.asarray(
        [mesh.face_vertices(face) for face in mesh.faces()], dtype=np.int32, order="C"
    )

    # Unit cube has volume of 1
    result = volume(vertices, faces)
    assert pytest.approx(result) == 1.0


def test_centroid_binding_unit_cube():
    """Test centroid computation with a unit cube."""
    # Create a unit cube mesh centered at origin
    box = Box.from_width_height_depth(1, 1, 1)
    mesh = Mesh.from_vertices_and_faces(*box.to_vertices_and_faces())
    mesh.quads_to_triangles()

    # Convert to numpy arrays
    v_numpy = np.asarray(mesh.vertices_attributes("xyz"), dtype=np.float64, order="C")
    f_numpy = np.asarray(
        [mesh.face_vertices(face) for face in mesh.faces()], dtype=np.int32, order="C"
    )

    # Compute centroid by calling the C++ function
    vector_of_double: VectorDouble = centroid(v_numpy, f_numpy)

    # Convert centroid to a COMPAS Point
    point = Point(*vector_of_double)
    assert pytest.approx(point) == Point(0.0, 0.0, 0.0)
