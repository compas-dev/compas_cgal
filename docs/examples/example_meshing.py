import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Translation
from compas.geometry import Vector
from compas.geometry import scale_vector
from compas.geometry import transform_points_numpy
from compas_viewer import Viewer

from compas_cgal.meshing import mesh_remesh, mesh_remesh_dual
from compas_cgal import _types_std  # noqa: F401

def main():
    """Remesh a bunny mesh that is loaded from .ply file."""

    FILE = Path(__file__).parent.parent.parent / "data" / "Bunny.ply"
    
    bunny = Mesh.from_ply(FILE)
    #bunny = Mesh.from_meshgrid(1,10,1,10)
    bunny.quads_to_triangles()
    bunny.remove_unused_vertices()

    centroid = bunny.vertex_point(0)

    vector = scale_vector(centroid, -1)

    T = Translation.from_vector(vector)
    S = Scale.from_factors([100, 100, 100])
    R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))

    # bunny.transform(R * S * T)
    V0, F0 = bunny.to_vertices_and_faces()
    V1 = transform_points_numpy(V0, R * S * T)


    edge_length = 0.005
    iterations = 10
    V1, F1 = mesh_remesh((V0, F0), edge_length, iterations)
    V1 = transform_points_numpy(V1, Translation.from_vector([0.15, 0, 0]))
    mesh = Mesh.from_vertices_and_faces(V1, F1)
    

    V1, F1 = mesh_remesh_dual((V0, F0), edge_length, iterations, 3.14, True)
    V1 = transform_points_numpy(V1, Translation.from_vector([0.3, 0, 0]))
    dual = Mesh.from_vertices_and_faces(V1, F1)

    return bunny, mesh, dual


bunny, mesh, dual = main()


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(width=1600, height=900)

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -0.25, 0.10]

viewer.scene.add(bunny, show_points=False)
viewer.scene.add(mesh, show_points=False)
viewer.scene.add(dual, show_points=True)

viewer.show()
