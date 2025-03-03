"""Tests for mesh remeshing functionality in COMPAS CGAL."""

from compas_viewer import viewer
import numpy as np
from compas.datastructures import Mesh
from compas_cgal import remesh
from compas_viewer.viewer import Viewer


def test_mesh_remesh():
    """Test mesh remeshing functionality.
    
    This function tests the remeshing of a triangle mesh with target edge length
    and specified number of iterations.
    """
    # Create a test mesh
    mesh = Mesh.from_polyhedron(20)
    vertices, faces = mesh.to_vertices_and_faces()
    
    print("Original mesh:")
    print(f"Number of vertices: {len(vertices)}")
    print(f"Number of faces: {len(faces)}")
    
    # Convert to numpy arrays with row-major order (C-style)
    vertices = np.asarray(vertices, dtype=np.float64, order='C')
    faces = np.asarray(faces, dtype=np.int32, order='C')
    
    # Test remeshing
    target_edge_length = 0.5
    num_iterations = 10
    print(f"\nRemeshing with target edge length {target_edge_length} and {num_iterations} iterations...")
    
    remeshed_vertices, remeshed_faces = remesh(
        vertices, faces, target_edge_length, num_iterations
    )

    # Verify the output arrays are row-major ordered
    assert isinstance(remeshed_vertices, np.ndarray)
    assert isinstance(remeshed_faces, np.ndarray)
    assert remeshed_vertices.flags['C_CONTIGUOUS'], "Remeshed vertices should be row-major (C-contiguous)"
    assert remeshed_faces.flags['C_CONTIGUOUS'], "Remeshed faces should be row-major (C-contiguous)"
    
    print("\nRemeshed mesh:")
    print(f"Number of vertices: {len(remeshed_vertices)}")
    print(f"Number of faces: {len(remeshed_faces)}")
    
    mesh = Mesh.from_vertices_and_faces(remeshed_vertices, remeshed_faces)
    viewer = Viewer()
    viewer.scene.add(mesh)
    viewer.show()
    return remeshed_vertices, remeshed_faces


if __name__ == "__main__":
    print("Running mesh remesh test...")
    test_mesh_remesh()