import os
import numpy as np
from compas_cgal._cgal import slicer

HERE = os.path.dirname(__file__)


def main(mesh, plane):
    V, F = mesh.to_vertices_and_faces()
    point, normal = plane
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    P = np.array([point], dtype=np.float64)
    N = np.array([normal], dtype=np.float64)
    result = slicer.slice_mesh(V, F, P, N)
    print(result)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    from compas.utilities import print_profile
    from compas.utilities import rgb_to_hex
    from compas.geometry import Point
    from compas.geometry import Vector
    from compas.geometry import Plane
    from compas.geometry import Box
    from compas.datastructures import Mesh
    from compas.datastructures import mesh_quads_to_triangles

    main = print_profile(main)

    O = Point(0, 0, 0)
    Z = Vector(0, 0, 1)
    XY = Plane(O, Z)

    box = Box.from_width_height_depth(1, 1, 1)
    box = Mesh.from_shape(box)
    mesh_quads_to_triangles(box)

    main(box, XY)
