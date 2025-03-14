import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Pointcloud
from compas.geometry import Rotation
from compas.geometry import Scale
from compas_cgal.reconstruction import poisson_surface_reconstruction


def test_reconstruction_poisson_surface_reconstruction():
    FILE = Path(__file__).parent.parent / "data" / "oni.xyz"

    points = []
    normals = []
    with open(FILE, "r") as f:
        for line in f:
            x, y, z, nx, ny, nz = line.strip().split()
            points.append([float(x), float(y), float(z)])
            normals.append([float(nx), float(ny), float(nz)])

    V, F = poisson_surface_reconstruction(points, normals)
    mesh = Mesh.from_vertices_and_faces(V, F)

    R = Rotation.from_axis_and_angle([1, 0, 0], math.radians(90))
    S = Scale.from_factors([5, 5, 5])
    T = R * S

    c = Pointcloud(V)
    c.transform(T)
    mesh.transform(T)

    assert mesh.is_manifold()
    assert mesh.number_of_vertices() > 0
    assert mesh.number_of_faces() > 0
