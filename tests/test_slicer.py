from compas.geometry import Box, Plane, Point, Vector, Polyline
from compas_cgal.slicer import slice_mesh


def test_mesh_slice():
    """Test mesh slicing with a simple box."""
    # Create test box mesh
    box = Box.from_width_height_depth(2.0, 2.0, 2.0)
    mesh = box.to_vertices_and_faces(triangulated=True)

    # Create one horizontal slicing plane
    point = Point(0, 0, 0)
    normal = Vector(0, 0, 1)
    plane = Plane(point, normal)

    # Get intersection curves
    slicer_polylines = slice_mesh(mesh, [plane])

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
