import numpy as np
import compas
from compas.datastructures import Mesh
from compas.datastructures import mesh_quads_to_triangles
from compas_cgal._cgal import meshing


def main(v, f):
    V = np.asarray(v, dtype=np.float64)
    F = np.asarray(f, dtype=np.int32)

    # meshing.refine(V, F)
    # meshing.fair(V, F)
    # meshing.triangulate(V, F)
    meshing.remesh(V, F, 0.5, 10)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas.utilities import print_profile

    m = Mesh.from_obj(compas.get('faces.obj'))
    mesh_quads_to_triangles(m)

    v, f = m.to_vertices_and_faces()

    main = print_profile(main)

    main(v, f)
