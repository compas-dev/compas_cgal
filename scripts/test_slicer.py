import os
import numpy as np
from compas_cgal._cgal import slicer


def main(mesh, planes):
    V, F = mesh.to_vertices_and_faces()
    points, normals = zip(*planes)
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    P = np.array(points, dtype=np.float64)
    N = np.array(normals, dtype=np.float64)
    return slicer.slice_mesh(V, F, P, N)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import math
    import compas

    from compas.utilities import print_profile
    from compas.utilities import rgb_to_hex
    from compas.geometry import scale_vector
    from compas.geometry import Point
    from compas.geometry import Vector
    from compas.geometry import Plane
    from compas.geometry import Box
    from compas.geometry import Polygon
    from compas.geometry import Polyline
    from compas.geometry import Rotation
    from compas.geometry import Translation
    from compas.geometry import Scale
    from compas.datastructures import Mesh
    from compas.datastructures import mesh_quads_to_triangles
    from compas_viewers.objectviewer import ObjectViewer

    # main = print_profile(main)

    point = Point(0, 0, 0)
    normal = Vector(1, 0, 0)
    # R = Rotation.from_axis_and_angle(Vector(0, 1, 0), math.radians(60))
    # normal.transform(R)
    planes = []
    for i in range(2):
        plane = Plane(Point(-0.15 * i, 0, 0), normal)
        planes.append(plane)

    mesh = Mesh.from_ply(compas.get('bunny.ply'))
    vector = scale_vector(mesh.centroid(), -1)

    T = Translation.from_vector(vector)
    S = Scale.from_factors([100, 100, 100])
    R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))

    mesh.transform_numpy(R * S * T)

    # currently this only returns one polyline
    # because otherwise a segmentation fault occurs
    result = main(mesh, planes)

    polylines = []
    for points in [result]:
        points = [Point(*point) for point in points]  # otherwise Polygon throws an error
        polyline = Polyline(points)
        polylines.append(polyline)

    viewer = ObjectViewer()

    # viewer.add(mesh, settings={'color': '#cccccc'})

    for polyline in polylines:
        viewer.add(polyline, settings={'color': '#0000ff'})

    viewer.update()
    viewer.show()
