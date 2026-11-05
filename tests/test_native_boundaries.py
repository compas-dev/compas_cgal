import gc
from pathlib import Path

import numpy as np
import pytest
from compas.geometry import Tessellation

from compas_cgal import measure
from compas_cgal import polylines
from compas_cgal import straight_skeleton_2
from compas_cgal._tessellation import as_native_tessellation
from compas_cgal._tessellation import from_native_tessellation
from compas_cgal.booleans import boolean_difference_mesh_mesh
from compas_cgal.booleans import boolean_intersection_mesh_mesh
from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.booleans import boolean_union_mesh_mesh_with_edges
from compas_cgal.booleans import boolean_union_mesh_mesh_with_face_source
from compas_cgal.booleans import split_mesh_mesh
from compas_cgal.intersections import intersection_mesh_mesh
from compas_cgal.slicer import slice_mesh_planes
from compas_cgal.subdivision import mesh_subdivide_loop


def coordinate_inputs():
    values = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    c_float64 = np.asarray(values, dtype=np.float64)
    c_float32 = np.asarray(values, dtype=np.float32)
    f_float64 = np.asfortranarray(c_float64)
    sliced_float64 = np.asarray([[0, 0, 0, 9], [1, 0, 0, 9], [0, 1, 0, 9]], dtype=np.float64)[:, :3]
    readonly_float64 = c_float64.copy()
    readonly_float64.flags.writeable = False
    return [values, tuple(map(tuple, values)), c_float32, c_float64, f_float64, sliced_float64, readonly_float64]


def index_inputs():
    values = [[0, 1, 2], [2, 1, 0]]
    c_int64 = np.asarray(values, dtype=np.int64)
    c_int32 = np.asarray(values, dtype=np.int32)
    f_int32 = np.asfortranarray(c_int32)
    sliced_int32 = np.asarray([[0, 1, 2, 9], [2, 1, 0, 9]], dtype=np.int32)[:, :3]
    readonly_int32 = c_int32.copy()
    readonly_int32.flags.writeable = False
    return [values, tuple(map(tuple, values)), c_int64, c_int32, f_int32, sliced_int32, readonly_int32]


def polygon_inputs():
    values = [[0, 0, 0], [4, 0, 0], [4, 4, 0], [0, 4, 0]]
    c_float64 = np.asarray(values, dtype=np.float64)
    c_float32 = np.asarray(values, dtype=np.float32)
    f_float64 = np.asfortranarray(c_float64)
    sliced_float64 = np.asarray([[0, 0, 0, 9], [4, 0, 0, 9], [4, 4, 0, 9], [0, 4, 0, 9]], dtype=np.float64)[:, :3]
    readonly_float64 = c_float64.copy()
    readonly_float64.flags.writeable = False
    return [values, tuple(map(tuple, values)), c_float32, c_float64, f_float64, sliced_float64, readonly_float64]


def boolean_coordinate_inputs():
    values = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    c_float64 = np.asarray(values, dtype=np.float64)
    c_float32 = np.asarray(values, dtype=np.float32)
    f_float64 = np.asfortranarray(c_float64)
    sliced_float64 = np.asarray([[*point, 9] for point in values], dtype=np.float64)[:, :3]
    readonly_float64 = c_float64.copy()
    readonly_float64.flags.writeable = False
    return [values, tuple(map(tuple, values)), c_float32, c_float64, f_float64, sliced_float64, readonly_float64]


def boolean_index_inputs():
    values = [[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]]
    c_int64 = np.asarray(values, dtype=np.int64)
    c_int32 = np.asarray(values, dtype=np.int32)
    f_int32 = np.asfortranarray(c_int32)
    sliced_int32 = np.asarray([[*face, 9] for face in values], dtype=np.int32)[:, :3]
    readonly_int32 = c_int32.copy()
    readonly_int32.flags.writeable = False
    return [values, tuple(map(tuple, values)), c_int64, c_int32, f_int32, sliced_int32, readonly_int32]


class HugeVertices(np.ndarray):
    """Small array reporting a vertex count beyond the CGAL index range."""

    def __len__(self):
        return np.iinfo(np.int32).max + 2

    def __iter__(self):
        for index in range(self.shape[0]):
            yield np.asarray(np.ndarray.__getitem__(self, index))


def test_python_wrapper_normalizes_mesh_arrays_at_native_boundary(monkeypatch):
    captured = {}

    def area(vertices, faces):
        captured["vertices"] = vertices
        captured["faces"] = faces
        return 0.5

    monkeypatch.setattr(measure._measure, "area", area)

    result = measure.mesh_area(([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]]))

    assert result == 0.5
    assert captured["vertices"].dtype == np.float64
    assert captured["faces"].dtype == np.int32
    assert captured["vertices"].flags.c_contiguous
    assert captured["faces"].flags.c_contiguous


def test_tessellation_boundary_normalizes_without_mutation():
    vertices = np.asfortranarray(np.asarray([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32))
    triangles = np.asfortranarray(np.asarray([[0, 1, 2]], dtype=np.int64))
    vertices_before = vertices.copy()
    triangles_before = triangles.copy()

    native_vertices, native_triangles = as_native_tessellation(Tessellation(vertices, triangles))

    assert native_vertices.dtype == np.float64
    assert native_triangles.dtype == np.int32
    assert native_vertices.flags.c_contiguous
    assert native_triangles.flags.c_contiguous
    np.testing.assert_array_equal(vertices, vertices_before)
    np.testing.assert_array_equal(triangles, triangles_before)


def test_native_tessellation_retains_compatible_buffers():
    vertices = np.asarray([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64, order="C")
    triangles = np.asarray([[0, 1, 2]], dtype=np.int32, order="C")

    tessellation = from_native_tessellation(vertices, triangles)

    assert tessellation.vertices is vertices
    assert tessellation.triangles is triangles


def test_tessellation_boundary_rejects_indices_outside_native_range():
    vertices = np.asarray([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64).view(HugeVertices)
    triangles = [[0, 1, np.iinfo(np.int32).max + 1]]

    with pytest.raises(OverflowError, match="Triangle indices"):
        as_native_tessellation(Tessellation(vertices, triangles))


@pytest.mark.parametrize("vertices", coordinate_inputs())
@pytest.mark.parametrize("faces", index_inputs())
def test_public_mesh_inputs_are_normalized_without_mutation(monkeypatch, vertices, faces):
    vertices_before = np.asarray(vertices).copy()
    faces_before = np.asarray(faces).copy()
    captured = {}

    def area(native_vertices, native_faces):
        captured["vertices"] = native_vertices
        captured["faces"] = native_faces
        return 0.5

    monkeypatch.setattr(measure._measure, "area", area)

    assert measure.mesh_area((vertices, faces)) == 0.5
    assert captured["vertices"].dtype == np.float64
    assert captured["faces"].dtype == np.int32
    assert captured["vertices"].flags.c_contiguous
    assert captured["faces"].flags.c_contiguous
    np.testing.assert_array_equal(vertices, vertices_before)
    np.testing.assert_array_equal(faces, faces_before)


@pytest.mark.parametrize("vertices, faces", list(zip(boolean_coordinate_inputs(), boolean_index_inputs())))
@pytest.mark.parametrize("operation", ["union", "difference", "intersection", "split", "edges", "source"])
def test_boolean_inputs_are_normalized_without_mutation(monkeypatch, vertices, faces, operation):
    vertices_before = np.asarray(vertices).copy()
    faces_before = np.asarray(faces).copy()
    captured = []

    def boolean(*arrays):
        captured.extend(arrays)
        result = (np.empty((0, 3), dtype=np.float64), np.empty((0, 3), dtype=np.int32))
        if operation in {"edges", "source"}:
            return (*result, np.empty((0, 2), dtype=np.int32))
        return result

    if operation in {"union", "difference", "intersection"}:
        monkeypatch.setattr(f"compas_cgal.booleans._booleans.boolean_{operation}", boolean)
        functions = {
            "union": boolean_union_mesh_mesh,
            "difference": boolean_difference_mesh_mesh,
            "intersection": boolean_intersection_mesh_mesh,
        }
        functions[operation]((vertices, faces), (vertices, faces))
    elif operation == "edges":
        monkeypatch.setattr("compas_cgal.booleans._booleans.boolean_union_with_edges", boolean)
        boolean_union_mesh_mesh_with_edges((vertices, faces), (vertices, faces))
    elif operation == "source":
        monkeypatch.setattr("compas_cgal.booleans._booleans.boolean_union_with_face_source", boolean)
        boolean_union_mesh_mesh_with_face_source((vertices, faces), (vertices, faces))
    else:
        monkeypatch.setattr("compas_cgal.booleans._booleans.split", boolean)
        split_mesh_mesh((vertices, faces), (vertices, faces))

    for native_vertices, native_faces in zip(captured[::2], captured[1::2]):
        assert native_vertices.dtype == np.float64
        assert native_faces.dtype == np.int32
        assert native_vertices.flags.c_contiguous
        assert native_faces.flags.c_contiguous
    np.testing.assert_array_equal(vertices, vertices_before)
    np.testing.assert_array_equal(faces, faces_before)


@pytest.mark.parametrize("vertices, faces", list(zip(boolean_coordinate_inputs(), boolean_index_inputs())))
@pytest.mark.parametrize("operation", ["intersection", "slice"])
def test_polyline_mesh_inputs_are_normalized_without_mutation(monkeypatch, vertices, faces, operation):
    vertices_before = np.asarray(vertices).copy()
    faces_before = np.asarray(faces).copy()
    captured = []

    if operation == "intersection":

        def native(*arrays):
            captured.extend(arrays)
            return [np.empty((0, 3), dtype=np.float64)]

        monkeypatch.setattr("compas_cgal.intersections._intersections.intersection_mesh_mesh", native)
        intersection_mesh_mesh((vertices, faces), (vertices, faces))
    else:

        def native(native_vertices, native_faces, points, normals):
            captured.extend([native_vertices, native_faces])
            assert points.dtype == np.float64
            assert normals.dtype == np.float64
            assert points.flags.c_contiguous
            assert normals.flags.c_contiguous
            return [np.empty((0, 3), dtype=np.float64)]

        monkeypatch.setattr("compas_cgal.slicer._slicer.slice_mesh", native)
        slice_mesh_planes((vertices, faces), [([0, 0, 0], [0, 0, 1])])

    for native_vertices, native_faces in zip(captured[::2], captured[1::2]):
        assert native_vertices.dtype == np.float64
        assert native_faces.dtype == np.int32
        assert native_vertices.flags.c_contiguous
        assert native_faces.flags.c_contiguous
    np.testing.assert_array_equal(vertices, vertices_before)
    np.testing.assert_array_equal(faces, faces_before)


@pytest.mark.parametrize("points", coordinate_inputs())
@pytest.mark.parametrize("operation", ["simplify", "closest"])
def test_polyline_inputs_are_normalized_without_mutation(monkeypatch, points, operation):
    points_before = np.asarray(points).copy()
    captured = []

    if operation == "simplify":

        def simplify(arrays, threshold):
            captured.extend(arrays)
            return arrays

        monkeypatch.setattr(polylines, "_simplify", simplify)
        polylines.simplify_polylines((points,), 0.1)
    else:

        def closest(query_points, polyline):
            captured.extend([query_points, polyline])
            return query_points

        monkeypatch.setattr(polylines, "_closest_points", closest)
        polylines.closest_points_on_polyline(points, points)

    for array in captured:
        assert array.dtype == np.float64
        assert array.flags.c_contiguous
    np.testing.assert_array_equal(points, points_before)


@pytest.mark.parametrize("boundary", polygon_inputs())
def test_straight_skeleton_holes_are_normalized_without_mutation(monkeypatch, boundary):
    hole = np.asarray([[1, 1, 0], [1, 2, 0], [2, 2, 0], [2, 1, 0]], dtype=np.float32)
    hole = np.asfortranarray(hole)
    boundary_before = np.asarray(boundary).copy()
    hole_before = hole.copy()
    captured = {}

    def skeleton(native_boundary, native_holes):
        captured["boundary"] = native_boundary
        captured["holes"] = native_holes
        return (
            np.empty((0, 3), dtype=np.float64),
            np.empty((0,), dtype=np.int32),
            np.empty((0, 2), dtype=np.int32),
            np.empty((0,), dtype=np.int32),
        )

    monkeypatch.setattr(straight_skeleton_2._straight_skeleton_2, "create_interior_straight_skeleton_with_holes", skeleton)
    straight_skeleton_2.interior_straight_skeleton_with_holes(boundary, [hole], as_graph=False)

    assert captured["boundary"].dtype == np.float64
    assert captured["boundary"].flags.c_contiguous
    assert captured["holes"][0].dtype == np.float64
    assert captured["holes"][0].flags.c_contiguous
    np.testing.assert_array_equal(boundary, boundary_before)
    np.testing.assert_array_equal(hole, hole_before)


def test_native_array_results_remain_valid_after_collection():
    mesh = (
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]],
    )

    vertices, faces = mesh_subdivide_loop(mesh)
    expected_vertices = vertices.copy()
    expected_faces = faces.copy()

    gc.collect()

    np.testing.assert_array_equal(vertices, expected_vertices)
    np.testing.assert_array_equal(faces, expected_faces)
    assert vertices.dtype == np.float64
    assert faces.dtype == np.int32
    assert vertices.flags.c_contiguous
    assert faces.flags.c_contiguous


def test_all_native_modules_have_stubs_and_package_is_typed():
    package = Path(__file__).parents[1] / "src" / "compas_cgal"
    cmake = (Path(__file__).parents[1] / "CMakeLists.txt").read_text()

    module_names = []
    for line in cmake.splitlines():
        line = line.strip()
        if line.startswith("add_nanobind_module("):
            module_names.append(line.removeprefix("add_nanobind_module(").split(maxsplit=1)[0])

    assert (package / "py.typed").is_file()
    assert module_names
    assert not [name for name in module_names if not (package / f"{name}.pyi").is_file()]
