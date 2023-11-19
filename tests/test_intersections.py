from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import Polyline


from compas_cgal.intersections import intersection_mesh_mesh


def test_intersections():
    A = Sphere(1.0).to_vertices_and_faces(u=50, v=50, triangulated=True)
    B = Sphere(1.0, point=[1, 0, 0]).to_vertices_and_faces(
        u=50, v=50, triangulated=True
    )

    polylines = []
    pointsets = intersection_mesh_mesh(A, B)
    for points in pointsets:
        points = [
            Point(*point) for point in points
        ]  # otherwise Polygon throws an error
        polyline = Polyline(points)
        polylines.append(polyline)

    print(pointsets)


if __name__ == "__main__":
    test_intersections()
