from compas.geometry import Box
from compas_cgal.skeletonization import mesh_skeleton, mesh_skeleton_with_mapping


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


def test_mesh_skeleton_with_mapping():
    """Test mesh skeletonization with vertex mapping."""
    # Create test box mesh
    box = Box.from_width_height_depth(2.0, 2.0, 2.0)
    mesh = box.to_vertices_and_faces(triangulated=True)
    vertices, faces = mesh

    # Get skeleton with mapping
    edges, vertex_indices = mesh_skeleton_with_mapping(mesh)

    # Basic validation of edges
    assert isinstance(edges, list)
    assert len(edges) > 0
    assert isinstance(edges[0], tuple)
    assert len(edges[0]) == 2
    assert len(edges[0][0]) == 3  # 3D points

    # Validate vertex indices
    assert isinstance(vertex_indices, list)
    assert len(vertex_indices) == len(edges)

    # Each edge should have vertex indices for start and end
    for indices in vertex_indices:
        assert isinstance(indices, tuple)
        assert len(indices) == 2
        start_indices, end_indices = indices

        # Each skeleton vertex maps to one or more original vertices
        assert isinstance(start_indices, list)
        assert isinstance(end_indices, list)

        # Indices should be valid
        num_vertices = len(vertices)
        for idx in start_indices:
            assert 0 <= idx < num_vertices
        for idx in end_indices:
            assert 0 <= idx < num_vertices
