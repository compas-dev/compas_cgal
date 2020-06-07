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

    from compas.geometry import scale_vector
    from compas.geometry import Point
    from compas.geometry import Vector
    from compas.geometry import Plane
    from compas.geometry import Polyline
    from compas.geometry import Rotation
    from compas.geometry import Translation
    from compas.geometry import Scale
    from compas.datastructures import Mesh
    from compas_viewers.objectviewer import ObjectViewer

    normal = Vector(1, 0, 0)
    planes = []
    for i in range(2):
        plane = Plane(Point(-0.15 * i, 0, 0), normal)
        planes.append(plane)

    mesh = Mesh.from_ply(compas.get('bunny.ply'))
    vector = scale_vector(mesh.centroid(), -1)

    T = Translation.from_vector(vector)
    S = Scale.from_factors([100, 100, 100])
    R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))

    mesh.transform(R * S * T)

    result = main(mesh, planes)

    polylines = []
    for points in result:
        points = [Point(*point) for point in points]  # otherwise Polygon throws an error
        polyline = Polyline(points)
        polylines.append(polyline)

    viewer = ObjectViewer()
    viewer.view.use_shaders = False

    for polyline in polylines:
        viewer.add(polyline, settings={'color': '#0000ff'})

    viewer.update()
    viewer.show()
