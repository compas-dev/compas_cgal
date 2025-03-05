import numpy as np
from compas.datastructures import Mesh
from compas_cgal import remesh
from compas.geometry import scale_vector
from compas.geometry import Translation
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Vector
from pathlib import Path
import math
from line_profiler import profile
from compas_viewer import Viewer


@profile  # Add this decorator
def meshing_remesh_binding(mesh: Mesh, target_edge_length: float, num_iterations: int):
    """Profile the remeshing workflow including data loading, preprocessing and remeshing."""

    vertices, faces = mesh.to_vertices_and_faces()

    # Convert to numpy arrays with row-major order (C-style)
    vertices = np.asarray(vertices, dtype=np.float64, order="C")
    faces = np.asarray(faces, dtype=np.int32, order="C")

    # C++ remeshing
    remeshed_vertices, remeshed_faces = remesh(
        vertices, faces, target_edge_length, num_iterations
    )

    mesh = Mesh.from_vertices_and_faces(remeshed_vertices, remeshed_faces)

    return mesh


if __name__ == "__main__":
    # test_remesh()

    FILE = Path(__file__).parent.parent / "data" / "Bunny.ply"

    # Load and preprocess
    bunny = Mesh.from_ply(FILE)
    bunny.remove_unused_vertices()

    # Transform
    vector = scale_vector(bunny.centroid(), -1)
    T = Translation.from_vector(vector)
    S = Scale.from_factors([100, 100, 100])
    R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))
    bunny.transform(R * S * T)

    remeshed_mesh = meshing_remesh_binding(bunny, 0.5, 10)

    # ==============================================================================
    # Visualize
    # ==============================================================================

    viewer = Viewer()

    viewer.renderer.camera.target = [0, 0, 0]
    viewer.renderer.camera.position = [0, -25, 10]

    viewer.scene.add(
        bunny.transformed(Translation.from_vector([-10, 0, 0])), show_points=False
    )
    viewer.scene.add(
        remeshed_mesh.transformed(Translation.from_vector([+10, 0, 0])),
        show_points=False,
    )

    viewer.show()
