import subprocess
import sys

import pytest
import numpy as np

from compas.geometry import Sphere
from compas.datastructures import Mesh
from compas_cgal.geodesics import heat_geodesic_distances
from compas_cgal.isolines import isolines
from compas_cgal.isolines import isolines_with_indices


@pytest.fixture
def sphere_mesh_with_distances():
    """Create a test sphere mesh with geodesic distances as vertex attribute."""
    sphere = Sphere(1.0, point=[0, 0, 0])
    V, F = sphere.to_vertices_and_faces(u=16, v=16, triangulated=True)
    mesh = Mesh.from_vertices_and_faces(V, F)

    # Compute geodesic distances from vertex 0
    distances = heat_geodesic_distances((V, F), [0])

    # Store distances as vertex attribute
    for key, d in zip(mesh.vertices(), distances):
        mesh.vertex_attribute(key, "distance", float(d))

    return mesh


def test_isolines_with_n(sphere_mesh_with_distances):
    """Test isoline extraction with n evenly spaced isovalues."""
    mesh = sphere_mesh_with_distances

    polylines = isolines(mesh, "distance", n=5)

    # Should return list of polylines
    assert isinstance(polylines, list)
    assert len(polylines) > 0

    # Each polyline should be a valid Nx3 array
    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.ndim == 2
        assert pts.shape[1] == 3  # 3D points
        assert pts.shape[0] >= 2  # At least 2 points


def test_isolines_with_explicit_isovalues(sphere_mesh_with_distances):
    """Test isoline extraction with explicit isovalue list."""
    mesh = sphere_mesh_with_distances

    # Get distance range to pick valid isovalues
    distances = list(mesh.vertices_attribute("distance"))
    mid_val = (min(distances) + max(distances)) / 2

    polylines = isolines(mesh, "distance", isovalues=[mid_val])

    assert isinstance(polylines, list)
    assert len(polylines) > 0

    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.shape[1] == 3


def test_isolines_validation_neither_provided(sphere_mesh_with_distances):
    """Test that ValueError is raised when neither isovalues nor n is provided."""
    mesh = sphere_mesh_with_distances

    with pytest.raises(ValueError, match="Either 'isovalues' or 'n' must be provided"):
        isolines(mesh, "distance")


def test_isolines_validation_both_provided(sphere_mesh_with_distances):
    """Test that ValueError is raised when both isovalues and n are provided."""
    mesh = sphere_mesh_with_distances

    with pytest.raises(ValueError, match="Provide exactly one of 'isovalues' or 'n'"):
        isolines(mesh, "distance", isovalues=[1.0], n=5)


def test_isolines_empty_result(sphere_mesh_with_distances):
    """Test isolines with isovalue outside scalar range returns empty list."""
    mesh = sphere_mesh_with_distances

    # Use isovalue way outside the distance range
    polylines = isolines(mesh, "distance", isovalues=[1000.0])

    assert isinstance(polylines, list)
    assert len(polylines) == 0


def test_isolines_with_smoothing(sphere_mesh_with_distances):
    """Test isoline extraction with smoothing enabled."""
    mesh = sphere_mesh_with_distances

    polylines = isolines(mesh, "distance", n=3, smoothing=2)

    assert isinstance(polylines, list)
    assert len(polylines) > 0

    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.shape[1] == 3


def test_isolines_with_resample_int(sphere_mesh_with_distances):
    """Test isoline extraction with integer resampling factor."""
    mesh = sphere_mesh_with_distances

    polylines_no_resample = isolines(mesh, "distance", n=3, resample=False)
    polylines_resample = isolines(mesh, "distance", n=3, resample=4)

    # Resampled polylines should generally have more points
    if len(polylines_no_resample) > 0 and len(polylines_resample) > 0:
        total_pts_no_resample = sum(len(pl) for pl in polylines_no_resample)
        total_pts_resample = sum(len(pl) for pl in polylines_resample)
        assert total_pts_resample >= total_pts_no_resample


def test_isolines_resample_disabled(sphere_mesh_with_distances):
    """Test isoline extraction with resampling disabled."""
    mesh = sphere_mesh_with_distances

    polylines = isolines(mesh, "distance", n=3, resample=False)

    assert isinstance(polylines, list)
    # Result should still be valid polylines
    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.shape[1] == 3


# ---------------------------------------------------------------------------
# isolines_with_indices: many isovalues on one mesh
# ---------------------------------------------------------------------------


def _canonical(polylines):
    """Polylines as a sorted list, each closed one started at its smallest point.

    Where a closed polyline starts, the direction a polyline runs in, and the order of the
    polylines of one isovalue carry no geometry; the points do, and they are kept bit for bit.
    """
    result = []
    for points in polylines:
        points = np.asarray(points)
        if np.array_equal(points[0], points[-1]):
            ring = points[:-1]
            start = min(range(len(ring)), key=lambda i: tuple(ring[i]))
            ring = np.roll(ring, -start, axis=0)
            if tuple(ring[-1]) < tuple(ring[1]):
                ring = np.concatenate([ring[:1], ring[:0:-1]])
            points = np.concatenate([ring, ring[:1]])
        elif tuple(points[-1]) < tuple(points[0]):
            points = points[::-1]
        result.append(points)
    return sorted(result, key=lambda points: points.tobytes())


def _assert_same_polylines(batch, single):
    batch, single = _canonical(batch), _canonical(single)
    assert len(batch) == len(single)
    for a, b in zip(batch, single):
        assert np.array_equal(a, b)


def _arrays(mesh, name):
    V, F = mesh.to_vertices_and_faces()
    return (V, F), np.asarray(mesh.vertices_attribute(name), dtype=np.float64)


@pytest.fixture
def grid_mesh_with_x():
    """An open 6 x 6 grid of triangles whose scalar is x: whole columns of vertices sit on integer isovalues."""
    mesh = Mesh.from_meshgrid(dx=6, nx=6)
    mesh.quads_to_triangles()
    for key in mesh.vertices():
        mesh.vertex_attribute(key, "x", float(mesh.vertex_attribute(key, "x")))
    return mesh


def test_isolines_with_indices_are_the_isolines_of_each_isovalue(sphere_mesh_with_distances):
    mesh = sphere_mesh_with_distances
    vf, scalars = _arrays(mesh, "distance")
    smin, smax = float(scalars.min()), float(scalars.max())
    isovalues = np.linspace(smin, smax, 9)[1:-1].tolist()

    polylines, indices = isolines_with_indices(vf, scalars, isovalues)

    assert len(polylines) == len(indices) > 0
    for i, isovalue in enumerate(isovalues):
        batch = [pl for pl, k in zip(polylines, indices) if k == i]
        single = isolines(mesh, "distance", isovalues=[isovalue], resample=False)
        assert len(single) > 0
        _assert_same_polylines(batch, single)


def test_isolines_with_indices_through_vertices_and_on_an_open_mesh(grid_mesh_with_x):
    mesh = grid_mesh_with_x
    vf, scalars = _arrays(mesh, "x")
    # 2.0 and 3.0 run along columns of vertices, 2.5 crosses the edges between them.
    isovalues = [2.0, 2.5, 3.0]

    polylines, indices = isolines_with_indices(vf, scalars, isovalues)

    for i, isovalue in enumerate(isovalues):
        batch = [pl for pl, k in zip(polylines, indices) if k == i]
        single = isolines(mesh, "x", isovalues=[isovalue], resample=False)
        assert len(single) > 0
        _assert_same_polylines(batch, single)
        assert all(np.all(pl[:, 0] == isovalue) for pl in batch)


def test_isolines_with_indices_index_the_isovalues_as_given(sphere_mesh_with_distances):
    vf, scalars = _arrays(sphere_mesh_with_distances, "distance")
    smin, smax = float(scalars.min()), float(scalars.max())
    low, mid, high = np.linspace(smin, smax, 5)[1:-1].tolist()
    # Unsorted, with a repeated isovalue and one that crosses nothing.
    isovalues = [high, low, smax + 1.0, mid, low]

    polylines, indices = isolines_with_indices(vf, scalars, isovalues)

    assert isinstance(indices, np.ndarray)
    assert indices.dtype == np.int32
    assert indices.shape == (len(polylines),)
    assert np.all(np.diff(indices) >= 0)
    assert set(indices.tolist()) == {0, 1, 3, 4}
    for i, isovalue in enumerate(isovalues):
        batch = [pl for pl, k in zip(polylines, indices) if k == i]
        _assert_same_polylines(batch, isolines_with_indices(vf, scalars, [isovalue])[0])


def test_isolines_with_indices_need_one_scalar_per_vertex(sphere_mesh_with_distances):
    vf, scalars = _arrays(sphere_mesh_with_distances, "distance")

    with pytest.raises(ValueError, match="scalar"):
        isolines_with_indices(vf, scalars[:-1], [1.0])


def test_isolines_module_works_when_imported_alone():
    """The bound list types have to be loaded by the module itself, not by an earlier import."""
    code = (
        "from compas_cgal.isolines import isolines_with_indices\n"
        "V = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]\n"
        "polylines, indices = isolines_with_indices((V, [[0, 1, 2]]), [0.0, 1.0, 1.0], [0.5])\n"
        "assert len(polylines) == 1 and indices.tolist() == [0]\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
