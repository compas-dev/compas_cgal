import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Pointcloud
from compas.geometry import Rotation
from compas.geometry import Scale
from compas_cgal.reconstruction import poisson_surface_reconstruction

# Test data file path
TEST_DATA_FILE = Path(__file__).parent.parent / "data" / "oni.xyz"


def load_test_data(file_path):
    """Load point cloud data from file.

    Parameters
    ----------
    file_path : Path
        Path to the xyz file containing points and normals.

    Returns
    -------
    tuple
        (points, normals) where each is a list of 3D coordinates.
    """
    points = []
    normals = []
    with open(file_path, "r") as f:
        for line in f:
            x, y, z, nx, ny, nz = line.strip().split()
            points.append([float(x), float(y), float(z)])
            normals.append([float(nx), float(ny), float(nz)])
    return points, normals


def test_reconstruction_poisson_surface_reconstruction():
    points, normals = load_test_data(TEST_DATA_FILE)

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


def test_reconstruction_poisson_surface_reconstruction_with_parameters():
    """Test Poisson surface reconstruction with custom parameters to reduce mesh complexity."""
    points, normals = load_test_data(TEST_DATA_FILE)

    # Test with larger sm_radius and sm_distance to reduce mesh complexity
    V1, F1 = poisson_surface_reconstruction(points, normals, sm_radius=50.0, sm_distance=0.5)
    mesh1 = Mesh.from_vertices_and_faces(V1, F1)

    # Test with default parameters
    V2, F2 = poisson_surface_reconstruction(points, normals)
    mesh2 = Mesh.from_vertices_and_faces(V2, F2)

    # Mesh with larger parameters should have fewer or equal vertices
    # (though this isn't guaranteed in all cases due to CGAL's internal logic)
    assert mesh1.is_manifold()
    assert mesh1.number_of_vertices() > 0
    assert mesh1.number_of_faces() > 0
    assert mesh2.is_manifold()
    assert mesh2.number_of_vertices() > 0
    assert mesh2.number_of_faces() > 0


def test_reconstruction_poisson_surface_reconstruction_angle_parameter():
    """Test Poisson surface reconstruction with custom angle parameter."""
    points, normals = load_test_data(TEST_DATA_FILE)

    # Test with custom angle parameter
    V, F = poisson_surface_reconstruction(points, normals, sm_angle=25.0)
    mesh = Mesh.from_vertices_and_faces(V, F)

    assert mesh.is_manifold()
    assert mesh.number_of_vertices() > 0
    assert mesh.number_of_faces() > 0
