from compas.geometry import Box
from compas_cgal import area, volume, centroid, VectorDouble
from compas.geometry import Point
from compas.datastructures import Mesh
import numpy as np
from line_profiler import profile


@profile
def area_binding(mesh: Mesh) -> float:
    """Compute the surface area of a mesh."""
    # Convert to numpy arrays with row-major order (C-style)
    v, f = mesh.to_vertices_and_faces()
    v_numpy = np.asarray(v, dtype=np.float64, order="C")
    f_numpy = np.asarray(f, dtype=np.int32, order="C")

    # Compute area by calling the C++ function
    return area(v_numpy, f_numpy)


@profile
def volume_binding(mesh: Mesh) -> float:
    """Compute the volume of a closed mesh."""
    # Convert to numpy arrays with row-major order (C-style)
    v, f = mesh.to_vertices_and_faces()
    v_numpy = np.asarray(v, dtype=np.float64, order="C")
    f_numpy = np.asarray(f, dtype=np.int32, order="C")

    # Compute volume by calling the C++ function
    return volume(v_numpy, f_numpy)


@profile
def centroid_binding(mesh: Mesh) -> Point:
    """Compute the centroid (center of mass) of a mesh."""
    # Convert to numpy arrays with row-major order (C-style)
    v, f = mesh.to_vertices_and_faces()
    v_numpy = np.asarray(v, dtype=np.float64, order="C")
    f_numpy = np.asarray(f, dtype=np.int32, order="C")

    # Compute centroid by calling the C++ function
    vector_of_double: VectorDouble = centroid(v_numpy, f_numpy)

    # Convert centroid to a COMPAS Point
    point = Point(*vector_of_double)
    return point


if __name__ == "__main__":
    # Create a unit box mesh
    box = Box(1)
    v, f = box.to_vertices_and_faces()
    mesh = Mesh.from_vertices_and_faces(v, f)
    mesh.quads_to_triangles()

    # Test the bindings
    print("Area:", area_binding(mesh))
    print("Volume:", volume_binding(mesh))
    print("Centroid:", centroid_binding(mesh))
