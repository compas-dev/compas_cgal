import pytest
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Polygon

from compas_cgal.straight_skeleton_2 import extrude

POINTS = [
    (-1.91, 3.59, 0.0),
    (-5.53, -5.22, 0.0),
    (-0.39, -1.98, 0.0),
    (2.98, -5.51, 0.0),
    (4.83, -2.02, 0.0),
    (9.70, -3.63, 0.0),
    (12.23, 1.25, 0.0),
    (3.42, 0.66, 0.0),
    (2.92, 4.03, 0.0),
]


def _zmax(mesh):
    return max(mesh.vertex_attribute(vertex, "z") for vertex in mesh.vertices())


def test_extrude_default_roof():
    """A default extrusion returns a closed, display-ready roof mesh and its outline."""
    mesh, lines = extrude(Polygon(POINTS))

    assert isinstance(mesh, Mesh)
    assert mesh.number_of_vertices() > 0
    assert mesh.is_valid()
    assert mesh.is_closed()
    assert _zmax(mesh) > 0.0

    # The mesh is triangulated so it renders correctly everywhere.
    assert mesh.is_trimesh()

    # The outline holds the true roof lines (eaves, hips and ridges).
    assert len(lines) > 0
    assert all(isinstance(line, Line) for line in lines)


def test_extrude_angle_controls_height():
    """A steeper taper angle produces a taller roof."""
    flat, _ = extrude(Polygon(POINTS), angles=30.0)
    steep, _ = extrude(Polygon(POINTS), angles=60.0)

    assert _zmax(steep) > _zmax(flat)


def test_extrude_maximum_height_truncates():
    """A maximum height caps the roof and keeps the mesh closed."""
    mesh, _ = extrude(Polygon(POINTS), maximum_height=1.5)

    assert mesh.is_closed()
    assert _zmax(mesh) == pytest.approx(1.5, abs=1e-6)


def test_extrude_with_hole():
    """A polygon with a hole (courtyard) extrudes into a closed hip-and-valley roof."""
    boundary = [(0, 0, 0), (12, 0, 0), (12, 9, 0), (0, 9, 0)]
    # Counter-clockwise hole is reversed automatically to the required orientation.
    hole = [(4, 3, 0), (8, 3, 0), (8, 6, 0), (4, 6, 0)]

    mesh, lines = extrude(boundary, holes=[hole])

    assert mesh.is_closed()
    assert mesh.is_valid()
    assert len(lines) > 0


def test_extrude_with_multiple_holes():
    """A polygon with several holes (courtyards) extrudes into a closed roof."""
    boundary = [(0, 0, 0), (14, 0, 0), (14, 9, 0), (0, 9, 0)]
    holes = [
        [(2.5, 3, 0), (5, 3, 0), (5, 6, 0), (2.5, 6, 0)],
        [(9, 3, 0), (11.5, 3, 0), (11.5, 6, 0), (9, 6, 0)],
    ]

    mesh, lines = extrude(boundary, holes=holes)

    assert mesh.is_closed()
    assert mesh.is_valid()
    assert len(lines) > 0


def test_extrude_weights_and_angles_are_exclusive():
    """Providing both weights and angles raises a clear error."""
    with pytest.raises(ValueError):
        extrude(Polygon(POINTS), weights=1.0, angles=45.0)
