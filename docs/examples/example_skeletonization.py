import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Polyline
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Translation
from compas_cgal.skeletonization import mesh_skeleton
from line_profiler import profile

from compas_viewer import Viewer


@profile
def main():
    # Load and transform mesh
    input_file = Path(__file__).parent.parent.parent / "data" / "elephant.off"

    # Create transformation sequence
    rotation_x = Rotation.from_axis_and_angle([1, 0, 0], math.radians(60))
    rotation_y = Rotation.from_axis_and_angle([0, 1, 0], math.radians(5))
    rotation = rotation_y * rotation_x
    scale = Scale.from_factors([5, 5, 5])
    translation = Translation.from_vector([0, 0, 2])
    
    # Apply transformations to mesh
    mesh = Mesh.from_off(input_file).transformed(translation * rotation * scale)
    mesh = mesh.subdivided("loop")

    # Convert mesh to vertices and faces
    vertices, faces = mesh.to_vertices_and_faces()

    # Generate skeleton edges
    skeleton_edges = mesh_skeleton((vertices, faces))

    # Convert skeleton edges to polylines
    polylines = []
    for start_point, end_point in skeleton_edges:
        polyline = Polyline([start_point, end_point])
        polylines.append(polyline)

    return mesh, polylines


if __name__ == "__main__":
    mesh, polylines = main()

    # Set up viewer
    viewer = Viewer(width=1600, height=900)
    viewer.renderer.camera.target = [0, 0, 1.5]
    viewer.renderer.camera.position = [-5, -5, 1.5]
    
    # Add mesh to scene
    viewer.scene.add(mesh, opacity=0.5, show_points=False)

    # Add skeleton polylines to scene
    for polyline in polylines:
        viewer.scene.add(polyline, linewidth=5, show_points=True)

    viewer.show()
