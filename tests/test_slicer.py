import numpy as np
import pytest

from compas.geometry import Box, Plane, Point, Vector, Polyline
from compas.geometry import trimesh_slice


def test_mesh_slice():
    """Test mesh slicing with a simple box."""
    # Create test box mesh
    box = Box.from_width_height_depth(2.0, 2.0, 2.0)
    mesh = box.to_tessellation().to_vertices_and_triangles()

    # Create one horizontal slicing plane
    point = Point(0, 0, 0)
    normal = Vector(0, 0, 1)
    plane = Plane(point, normal)

    # Get intersection curves
    slicer_polylines = trimesh_slice(mesh, [plane])

    # Convert edges to polylines
    polylines = []
    for polyline in slicer_polylines:
        points = []
        for point in polyline:
            points.append(Point(*point))
        polylines.append(Polyline(points))

    # Basic validation
    assert isinstance(polylines, list)
    assert len(polylines) > 0  # Box intersected by middle plane should give edges
    assert len(polylines[0]) == 9
    assert len(polylines[0][0]) == 3  # 3D points


def test_mesh_slice_accepts_tuple_plane():
    """The plugin accepts the structural plane representation from COMPAS."""
    mesh = Box.from_width_height_depth(2.0, 2.0, 2.0).to_tessellation().to_vertices_and_triangles()

    result = trimesh_slice(mesh, [([0, 0, 0], [0, 0, 1])])

    assert result
    assert len(result[0][0]) == 3


def test_mesh_slice_accepts_empty_planes_without_native_call(monkeypatch):
    mesh = Box.from_width_height_depth(2.0, 2.0, 2.0).to_tessellation().to_vertices_and_triangles()

    def fail(*args):
        raise AssertionError("native slicer should not be called")

    monkeypatch.setattr("compas_cgal.slicer._slicer.slice_mesh", fail)
    assert trimesh_slice(mesh, []) == []


def test_mesh_slice_rejects_zero_normal():
    mesh = Box.from_width_height_depth(2.0, 2.0, 2.0).to_tessellation().to_vertices_and_triangles()

    with pytest.raises(ValueError, match="nonzero"):
        trimesh_slice(mesh, [([0, 0, 0], [0, 0, 0])])


def test_mesh_slice_rejects_invalid_native_result_shape(monkeypatch):
    mesh = Box.from_width_height_depth(2.0, 2.0, 2.0).to_tessellation().to_vertices_and_triangles()
    monkeypatch.setattr(
        "compas_cgal.slicer._slicer.slice_mesh",
        lambda *args: [np.empty((0, 2), dtype=np.float64)],
    )

    with pytest.raises(RuntimeError, match="mesh slicing result"):
        trimesh_slice(mesh, [([0, 0, 0], [0, 0, 1])])
