import compas
from compas_cgal.meshing import remesh
from compas.datastructures import Mesh

from compas_view2.app import App


mesh = Mesh.from_obj(compas.get('tubemesh.obj'))
mesh.quads_to_triangles()

# ==============================================================================
# Remesh
# ==============================================================================

length = sum([mesh.edge_length(*edge) for edge in mesh.edges()]) / mesh.number_of_edges()

V, F = remesh(mesh.to_vertices_and_faces(), 0.5 * length)

mesh = Mesh.from_vertices_and_faces(V, F)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = App()

viewer.add(mesh, facecolor=(0.7, 0.7, 0.7))

viewer.run()
