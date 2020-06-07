import os

import numpy as np
import compas
from compas.datastructures import Mesh
from compas.datastructures import mesh_quads_to_triangles
from compas_cgal._cgal import meshing

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '..', 'images', 'cgal_remesh.png')


def main(v, f):
    V = np.asarray(v, dtype=np.float64)
    F = np.asarray(f, dtype=np.int32)

    # meshing.refine(V, F)
    # meshing.fair(V, F)
    # meshing.triangulate(V, F)
    result = meshing.remesh(V, F, 0.3, 10)
    return result


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas_plotters import MeshPlotter

    m = Mesh.from_obj(compas.get('faces.obj'))
    mesh_quads_to_triangles(m)

    v, f = m.to_vertices_and_faces()

    result = main(v, f)

    mesh = Mesh.from_vertices_and_faces(result.vertices, result.faces)

    plotter = MeshPlotter(mesh, figsize=(8, 5))
    plotter.draw_vertices(radius=0.01)
    plotter.draw_faces()
    plotter.show()
