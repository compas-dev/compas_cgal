from compas.geometry import Sphere
from compas.datastructures import Mesh
from compas.geometry import Translation
from compas.geometry import transform_points_numpy
from compas_viewer import Viewer

from compas_cgal.meshing import mesh_remesh, mesh_dual

def main():
    """Remesh a mesh."""

    mesh = Mesh.from_shape(Sphere(1))
    mesh.quads_to_triangles()

    edge_length = 0.5
    iterations = 10
    x_translation = 2

    # Remesh
    V1, F1 = mesh_remesh(mesh.to_vertices_and_faces(), edge_length, iterations)
    V1 = transform_points_numpy(V1, Translation.from_vector([x_translation, 0, 0]))
    remeshed = Mesh.from_vertices_and_faces(V1, F1)
    
    # Dual
    V2, F2 = mesh_dual((V1, F1), 2.14, True)
    V2 = transform_points_numpy(V2, Translation.from_vector([x_translation, 0, 0]))
    dual = Mesh.from_vertices_and_faces(V2, F2)

    return mesh, remeshed, dual


mesh, remeshed, dual = main()


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(width=1600, height=900)

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -0.25, 0.10]

viewer.scene.add(mesh, show_points=False)
viewer.scene.add(remeshed, show_points=False)
viewer.scene.add(dual, show_points=True)

viewer.show()
