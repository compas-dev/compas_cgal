import os
import numpy as np
import compas

from compas.datastructures import Mesh
from compas.datastructures import mesh_quads_to_triangles

from compas_plotters import MeshPlotter

from compas_cgal._cgal import meshing


HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '..', 'images', 'cgal_remesh.png')

m = Mesh.from_obj(compas.get('faces.obj'))
mesh_quads_to_triangles(m)

vertices, faces = m.to_vertices_and_faces()

V = np.asarray(vertices, dtype=np.float64)
F = np.asarray(faces, dtype=np.int32)

result = meshing.remesh(V, F, 0.3, 10)

mesh = Mesh.from_vertices_and_faces(result.vertices, result.faces)

plotter = MeshPlotter(mesh, figsize=(8, 5))
plotter.draw_vertices(radius=0.01)
plotter.draw_faces()
plotter.show()
