"""Tests for mesh remeshing functionality in COMPAS CGAL."""

import numpy as np
from compas.datastructures import Mesh
from compas_cgal import remesh
from compas_viewer.viewer import Viewer
from pathlib import Path
from compas.geometry import scale_vector
from compas.geometry import Translation
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Vector
import math
import time


def print_time(step_name, start_time):
    """Helper function to print execution time of a step."""
    duration = time.time() - start_time
    print(f"Time for {step_name}: {duration:.3f} seconds")
    return time.time()


def test_remesh():
    """Test mesh remeshing functionality.

    This function tests the remeshing of a triangle mesh with target edge length
    and specified number of iterations.
    """

    FILE = Path(__file__).parent.parent / "data" / "Bunny.ply"

    # ==============================================================================
    # Get the bunny and construct a mesh
    # ==============================================================================

    start_time = time.time()
    bunny = Mesh.from_ply(FILE)
    start_time = print_time("Loading PLY file", start_time)

    bunny.remove_unused_vertices()
    start_time = print_time("Removing unused vertices", start_time)

    # ==============================================================================
    # Move the bunny to the origin and rotate it upright.
    # ==============================================================================

    vector = scale_vector(bunny.centroid(), -1)
    T = Translation.from_vector(vector)
    S = Scale.from_factors([100, 100, 100])
    R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))
    bunny.transform(R * S * T)
    start_time = print_time("Transforming mesh", start_time)

    vertices, faces = bunny.to_vertices_and_faces()
    start_time = print_time("Converting to vertices and faces", start_time)

    print("\nMesh statistics:")
    print(f"Number of vertices: {len(vertices)}")
    print(f"Number of faces: {len(faces)}")

    # Convert to numpy arrays with row-major order (C-style)
    vertices = np.asarray(vertices, dtype=np.float64, order="C")
    faces = np.asarray(faces, dtype=np.int32, order="C")
    start_time = print_time("Converting to NumPy arrays", start_time)

    # Test remeshing
    target_edge_length = 0.5
    num_iterations = 10
    print(
        f"\nRemeshing with target edge length {target_edge_length} and {num_iterations} iterations..."
    )

    # C++ remeshing
    start_time = time.time()
    remeshed_vertices, remeshed_faces = remesh(
        vertices, faces, target_edge_length, num_iterations
    )
    start_time = print_time("C++ remeshing operation", start_time)

    # Convert back to COMPAS mesh
    mesh = Mesh.from_vertices_and_faces(remeshed_vertices, remeshed_faces)
    start_time = print_time("Converting back to COMPAS mesh", start_time)

    print("\nRemeshed mesh statistics:")
    print(f"Number of vertices: {len(remeshed_vertices)}")
    print(f"Number of faces: {len(remeshed_faces)}")

    # Verify the output arrays are row-major ordered
    assert isinstance(remeshed_vertices, np.ndarray)
    assert isinstance(remeshed_faces, np.ndarray)
    assert remeshed_vertices.flags[
        "C_CONTIGUOUS"
    ], "Remeshed vertices should be row-major (C-contiguous)"
    assert remeshed_faces.flags[
        "C_CONTIGUOUS"
    ], "Remeshed faces should be row-major (C-contiguous)"

    # Visualization
    start_time = time.time()
    viewer = Viewer()
    viewer.scene.add(bunny.transformed(Translation.from_vector([-10, 0, 0])))
    viewer.scene.add(mesh.transformed(Translation.from_vector([10, 0, 0])))
    start_time = print_time("Setting up visualization", start_time)
    
    viewer.show()
    return remeshed_vertices, remeshed_faces


if __name__ == "__main__":
    print("Running mesh remesh test...")
    test_remesh()
