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
    FILE = Path(__file__).parent.parent.parent / "data" / "elephant.off"

    Rx = Rotation.from_axis_and_angle([1, 0, 0], math.radians(60))
    Ry = Rotation.from_axis_and_angle([0, 1, 0], math.radians(5))
    R = Ry * Rx
    S = Scale.from_factors([5, 5, 5])
    T = Translation.from_vector([0, 0, 2])
    mesh = Mesh.from_off(FILE).transformed(T * R * S)

    mesh = mesh.subdivided("loop")

    V, F = mesh.to_vertices_and_faces()

    # Get skeleton edges
    edges = mesh_skeleton((V, F))

    # Convert edges to polylines
    polylines = []
    for start, end in edges:
        polyline = Polyline([start, end])
        polylines.append(polyline)

    return mesh, polylines


if __name__ == "__main__":
    mesh, polylines = main()

    viewer = Viewer(width=1600, height=900)
    viewer.renderer.camera.target = [0, 0, 1.5]
    viewer.renderer.camera.position = [-5, -5, 1.5]
    viewer.scene.add(mesh, opacity=0.5, show_points=False)

    for polyline in polylines:
        viewer.scene.add(polyline, linewidth=5, show_points=True)

    viewer.show()
