from compas.geometry import Box
from compas_cgal.skeletonization import mesh_skeleton


def test_mesh_skeleton():
    """Test mesh skeletonization with a simple box."""
    # Create test box mesh
    box = Box.from_width_height_depth(2.0, 2.0, 2.0)
    mesh = box.to_vertices_and_faces(triangulated=True)

    # Get skeleton
    edges = mesh_skeleton(mesh)

    # Basic validation
    assert isinstance(edges, list)
    assert len(edges) > 0
    assert isinstance(edges[0], tuple)
    assert len(edges[0]) == 2
    assert len(edges[0][0]) == 3  # 3D points
