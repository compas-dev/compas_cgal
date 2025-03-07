import numpy as np

from compas.geometry import Box
from compas_cgal.subdivision import mesh_subdivide_catmull_clark
from compas_cgal.subdivision import mesh_subdivide_loop
from compas_cgal.subdivision import mesh_subdivide_sqrt3


def test_subdivision_methods():
    """Test all three subdivision methods on a simple box mesh."""
    # Create test box
    box = Box.from_diagonal(([0, 0, 0], [1, 1, 1]))

    # Test Catmull-Clark on quad mesh
    V1, F1 = box.to_vertices_and_faces(triangulated=False)
    V1_subd, F1_subd = mesh_subdivide_catmull_clark((V1, F1), k=1)
    assert isinstance(V1_subd, np.ndarray)
    assert isinstance(F1_subd, np.ndarray)
    assert V1_subd.shape[1] == 3  # Check vertex dimension
    assert len(F1_subd) > len(F1)  # Should have more faces after subdivision

    # Test Loop on triangle mesh
    V2, F2 = box.to_vertices_and_faces(triangulated=True)
    V2_subd, F2_subd = mesh_subdivide_loop((V2, F2), k=1)
    assert isinstance(V2_subd, np.ndarray)
    assert isinstance(F2_subd, np.ndarray)
    assert V2_subd.shape[1] == 3  # Check vertex dimension
    assert len(F2_subd) > len(F2)  # Should have more faces after subdivision

    # Test Sqrt3 on triangle mesh
    V3, F3 = box.to_vertices_and_faces(triangulated=True)
    V3_subd, F3_subd = mesh_subdivide_sqrt3((V3, F3), k=1)
    assert isinstance(V3_subd, np.ndarray)
    assert isinstance(F3_subd, np.ndarray)
    assert V3_subd.shape[1] == 3  # Check vertex dimension
    assert len(F3_subd) > len(F3)  # Should have more faces after subdivision
