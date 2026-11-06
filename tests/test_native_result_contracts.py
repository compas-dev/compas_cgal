import numpy as np
import pytest

from compas_cgal import geodesics
from compas_cgal import polylines
from compas_cgal import reconstruction
from compas_cgal import skeletonization
from compas_cgal import straight_skeleton_2


MESH = (
    [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
    [[0, 1, 2]],
)


@pytest.mark.parametrize("shape", [(2,), (3, 2), (1, 2)])
def test_heat_geodesic_rejects_wrong_native_cardinality(monkeypatch, shape):
    monkeypatch.setattr(geodesics, "_heat_geodesic_distances", lambda *args: np.zeros(shape, dtype=np.float64))

    with pytest.raises(RuntimeError, match="one value per mesh vertex"):
        geodesics.heat_geodesic_distances(MESH, [0])


def test_exact_geodesic_rejects_mismatched_native_vectors(monkeypatch):
    result = (np.zeros((3, 1), dtype=np.float64), np.zeros((2, 1), dtype=np.int32))
    monkeypatch.setattr(geodesics, "_exact_geodesic_distances", lambda *args: result)

    with pytest.raises(RuntimeError, match="nearest sources"):
        geodesics.exact_geodesic_distances(MESH, [0], return_sources=True)


def test_geodesic_split_rejects_unpaired_native_mesh_lists(monkeypatch):
    vertices = [np.asarray(MESH[0], dtype=np.float64)]
    monkeypatch.setattr(geodesics, "_geodesic_isolines_split", lambda *args: (vertices, []))

    with pytest.raises(RuntimeError, match="1 vertex arrays and 0 face arrays"):
        geodesics.geodesic_isolines_split(MESH, [0], [0.5])


@pytest.mark.parametrize("operation", ["pointset_outlier_removal", "pointset_reduction", "pointset_smoothing"])
def test_pointset_operations_reject_malformed_native_result(monkeypatch, operation):
    result = np.empty((2, 2), dtype=np.float64)
    monkeypatch.setattr(reconstruction._reconstruction, operation, lambda *args: result)

    with pytest.raises(RuntimeError, match="result should have shape"):
        getattr(reconstruction, operation)([[0, 0, 0], [1, 0, 0]])


def test_pointset_smoothing_rejects_wrong_native_cardinality(monkeypatch):
    result = np.empty((1, 3), dtype=np.float64)
    monkeypatch.setattr(reconstruction._reconstruction, "pointset_smoothing", lambda *args: result)

    with pytest.raises(RuntimeError, match="should contain 2 points"):
        reconstruction.pointset_smoothing([[0, 0, 0], [1, 0, 0]])


def test_normal_estimation_rejects_unpaired_native_pointsets(monkeypatch):
    points = np.empty((2, 3), dtype=np.float64)
    normals = np.empty((1, 3), dtype=np.float64)
    monkeypatch.setattr(reconstruction._reconstruction, "pointset_normal_estimation", lambda *args: (points, normals))

    with pytest.raises(RuntimeError, match="should contain 2 points"):
        reconstruction.pointset_normal_estimation([[0, 0, 0], [1, 0, 0]])


def test_poisson_reconstruction_rejects_malformed_native_mesh(monkeypatch):
    result = (np.empty((2, 2), dtype=np.float64), np.empty((0, 3), dtype=np.int32))
    monkeypatch.setattr(reconstruction._reconstruction, "poisson_surface_reconstruction", lambda *args: result)
    points = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    normals = [[0, 0, 1], [0, 0, 1], [0, 0, 1]]

    with pytest.raises(RuntimeError, match="Poisson surface reconstruction failed"):
        reconstruction.poisson_surface_reconstruction(points, normals)


def test_polyline_simplification_rejects_unpaired_native_results(monkeypatch):
    monkeypatch.setattr(polylines, "_simplify", lambda *args: [])

    with pytest.raises(RuntimeError, match="0 polylines for 1 inputs"):
        polylines.simplify_polyline([[0, 0], [1, 0]], 0.1)


def test_polyline_simplification_rejects_wrong_native_dimension(monkeypatch):
    result = [np.empty((1, 3), dtype=np.float64)]
    monkeypatch.setattr(polylines, "_simplify", lambda *args: result)

    with pytest.raises(RuntimeError, match=r"shape \(N, 2\)"):
        polylines.simplify_polyline([[0, 0], [1, 0]], 0.1)


def test_closest_points_rejects_wrong_native_cardinality(monkeypatch):
    monkeypatch.setattr(polylines, "_closest_points", lambda *args: np.empty((1, 2), dtype=np.float64))

    with pytest.raises(RuntimeError, match="should contain 2 points"):
        polylines.closest_points_on_polyline([[0, 1], [1, 1]], [[0, 0], [1, 0]])


@pytest.mark.parametrize(
    "result, message",
    [
        ((np.empty((2, 3)), [0], np.empty((0, 2), dtype=np.int32), []), "2 points and 1 point indices"),
        ((np.empty((0, 3)), [], np.empty((2, 2), dtype=np.int32), [0]), "2 edges and 1 edge types"),
    ],
)
def test_straight_skeleton_rejects_unpaired_native_vectors(monkeypatch, result, message):
    monkeypatch.setattr(straight_skeleton_2._straight_skeleton_2, "create_interior_straight_skeleton", lambda *args: result)

    with pytest.raises(RuntimeError, match=message):
        straight_skeleton_2.interior_straight_skeleton([[0, 0, 0], [1, 0, 0], [0, 1, 0]], as_graph=False)


@pytest.mark.parametrize(
    "result",
    [
        ([0.0, 0.0, 0.0], [], [[]], [[]]),
        ([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [], [[]]),
    ],
)
def test_skeletonization_rejects_unpaired_native_vectors(monkeypatch, result):
    monkeypatch.setattr(skeletonization._skeletonization, "mesh_skeleton", lambda *args: result)

    with pytest.raises(RuntimeError, match="CGAL mesh skeletonization"):
        skeletonization.mesh_skeleton(MESH)
