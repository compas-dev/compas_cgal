from compas.datastructures import Mesh

from compas.geometry import scale_vector
from compas.geometry import Translation
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Vector
from compas.geometry import transform_points_numpy
from pathlib import Path
import math
from line_profiler import profile
from compas_viewer import Viewer
from compas_cgal.meshing import mesh_remesh


@profile
def main():
    """Remesh a bunny mesh that is loaded from .ply file."""

    FILE = Path(__file__).parent.parent.parent / "data" / "Bunny.ply"
    bunny = Mesh.from_ply(FILE)
    bunny.remove_unused_vertices()

    centroid = bunny.vertex_point(0)

    vector = scale_vector(centroid, -1)

    T = Translation.from_vector(vector)
    S = Scale.from_factors([100, 100, 100])
    R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))

    bunny.transform(R * S * T)
    V0, F0 = bunny.to_vertices_and_faces()
    V1 = transform_points_numpy(V0, R * S * T)

    V1, F1 = mesh_remesh((V0, F0), 0.3, 10)
    V1 = transform_points_numpy(V1, Translation.from_vector([20, 0, 0]))
    mesh = Mesh.from_vertices_and_faces(V1, F1)

    return bunny, mesh


bunny, mesh = main()


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(width=1600, height=900)

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -25, 10]

viewer.scene.add(bunny, show_points=False)
viewer.scene.add(mesh, show_points=False)

viewer.show()
