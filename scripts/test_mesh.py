import numpy as np
import compas
from compas.datastructures import Mesh
from compas_cgal._cgal import mesh

m = Mesh.from_obj(compas.get('faces.obj'))

v, f = m.to_vertices_and_faces()

V = np.asarray(v, dtype=np.float64)
F = np.asarray(f, dtype=np.int32)

mesh.mesh_test(V, F)
