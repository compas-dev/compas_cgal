import numpy as np
from compas.geometry import Polyhedron
from compas.datastructures import Mesh
from compas_cgal._cgal import subdivision
from compas_view2.app import App

mesh = Mesh.from_meshgrid(dx=10, nx=10)

V, F = mesh.to_vertices_and_faces()
V, F = subdivision.subd_catmullclark(np.asarray(V, dtype=np.float64), F, 2)

shape = Polyhedron(V, F)

viewer = App()
viewer.add(shape)
viewer.show()
