import numpy as np
from compas_cgal._cgal import booleans
from compas_cgal._cgal import meshing


def boolean(A, B, operation='union', remesh=True):
    VA, FA = A.to_vertices_and_faces()
    VB, FB = B.to_vertices_and_faces()
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)
    if operation == 'union':
        result = booleans.boolean_union(VA, FA, VB, FB)
    elif operation == 'difference':
        result = booleans.boolean_difference(VA, FA, VB, FB)
        if remesh:
            V = result.vertices
            F = result.faces
            result = meshing.remesh(V, F, 0.1, 10)
    elif operation == 'intersection':
        result = booleans.boolean_intersection(VA, FA, VB, FB)
    else:
        raise NotImplementedError
    mesh = Mesh.from_vertices_and_faces(result.vertices, result.faces)
    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas.geometry import Point
    from compas.geometry import Vector
    from compas.geometry import Plane
    from compas.geometry import Box
    from compas.geometry import Sphere
    from compas.datastructures import Mesh
    from compas.datastructures import mesh_quads_to_triangles
    from compas.datastructures import mesh_subdivide_quad
    from compas_viewers.multimeshviewer import MultiMeshViewer
    from compas_viewers.multimeshviewer import MeshObject

    R = 1.4

    O = Point(0, 0, 0)
    X = Vector(1, 0, 0)
    Y = Vector(0, 1, 0)
    Z = Vector(0, 0, 1)
    YZ = Plane(O, X)
    ZX = Plane(O, Y)
    XY = Plane(O, Z)

    box = Box.from_width_height_depth(2 * R, 2 * R, 2 * R)
    box = Mesh.from_shape(box)
    box = mesh_subdivide_quad(box, k=1)
    mesh_quads_to_triangles(box)

    sphere = Sphere(O, 1.25 * R)
    sphere = Mesh.from_shape(sphere, u=50, v=50)
    mesh_quads_to_triangles(sphere)

    mesh = boolean(box, sphere, 'difference')

    meshes = []
    meshes.append(MeshObject(mesh, color='#cccccc'))

    viewer = MultiMeshViewer()
    viewer.meshes = meshes

    viewer.show()
