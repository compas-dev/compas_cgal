from compas.datastructures import Mesh

# from compas_cgal import remesh
from compas.geometry import scale_vector
from compas.geometry import Translation
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Vector
from pathlib import Path
import math
from line_profiler import profile
from compas_viewer import Viewer
from compas_cgal.meshing import mesh_remesh


@profile
def main():
    """Resmesh a bunny mesh that is loaded from .ply file."""

    FILE = Path(__file__).parent.parent / "data" / "Bunny.ply"

    # ==============================================================================
    # Get the bunny and construct a mesh
    # ==============================================================================

    bunny = Mesh.from_ply(FILE)

    bunny.remove_unused_vertices()

    # ==============================================================================
    # Move the bunny to the origin and rotate it upright.
    # ==============================================================================

    centroid = bunny.centroid()
    vector = scale_vector(centroid, -1)

    T = Translation.from_vector(vector)
    S = Scale.from_factors([100, 100, 100])
    R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))

    bunny.transform(R * S * T)

    # ==============================================================================
    # Remesh
    # ==============================================================================

    V, F = mesh_remesh(bunny.to_vertices_and_faces(), 0.3, 10)
    mesh = Mesh.from_vertices_and_faces(V, F)

    return bunny, mesh


if __name__ == "__main__":
    bunny, mesh = main()

    # ==============================================================================
    # Visualize
    # ==============================================================================

    viewer = Viewer(width=1600, height=900)

    viewer.renderer.camera.target = [0, 0, 0]
    viewer.renderer.camera.position = [0, -25, 10]

    viewer.scene.add(
        bunny.transformed(Translation.from_vector([-10, 0, 0])), show_points=False
    )
    viewer.scene.add(
        mesh.transformed(Translation.from_vector([+10, 0, 0])), show_points=False
    )

    viewer.show()
