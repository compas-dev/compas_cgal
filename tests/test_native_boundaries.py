import ast
import gc
import importlib
from pathlib import Path

import numpy as np
import pytest

from compas_cgal import measure
from compas_cgal import meshing
from compas_cgal import polylines
from compas_cgal import straight_skeleton_2
from compas_cgal import _intersections
from compas_cgal import _measure
from compas_cgal import _meshing
from compas_cgal import _straight_skeleton_2
from compas_cgal import _types_std
from compas_cgal.booleans import boolean_difference_mesh_mesh
from compas_cgal.booleans import boolean_intersection_mesh_mesh
from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.booleans import boolean_union_mesh_mesh_with_edges
from compas_cgal.booleans import boolean_union_mesh_mesh_with_face_source
from compas_cgal.booleans import split_mesh_mesh
from compas_cgal.intersections import intersection_mesh_mesh
from compas_cgal.slicer import slice_mesh_planes
from compas_cgal.subdivision import mesh_subdivide_loop


NATIVE_MODULES = (
    "_booleans",
    "_geodesics",
    "_intersections",
    "_isolines",
    "_measure",
    "_meshing",
    "_polylines",
    "_reconstruction",
    "_skeletonization",
    "_slicer",
    "_straight_skeleton_2",
    "_subdivision",
    "_triangulation",
    "_types_std",
)


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
def test_remesh_inputs_are_normalized_without_mutation(monkeypatch, vertices, faces):
    vertices_before = np.asarray(vertices).copy()
    faces_before = np.asarray(faces).copy()
    captured = {}

    def remesh(native_vertices, native_faces, *args):
        captured["vertices"] = native_vertices
        captured["faces"] = native_faces
        return native_vertices, native_faces

    monkeypatch.setattr(meshing._meshing, "pmp_trimesh_remesh", remesh)

    result_vertices, result_faces = meshing.trimesh_remesh((vertices, faces), 0.5)

    assert captured["vertices"].dtype == np.float64
    assert captured["faces"].dtype == np.int32
    assert captured["vertices"].flags.c_contiguous
    assert captured["faces"].flags.c_contiguous
    assert result_vertices.shape[1] == 3
    assert result_faces.shape[1] == 3
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


def test_native_stub_exports_match_runtime_extensions():
    package = Path(__file__).parents[1] / "src" / "compas_cgal"

    for module_name in NATIVE_MODULES:
        module = importlib.import_module(f"compas_cgal.{module_name}")
        runtime_exports = {name for name in dir(module) if not name.startswith("_") and callable(getattr(module, name))}
        tree = ast.parse((package / f"{module_name}.pyi").read_text())
        stub_exports = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_")}

        assert stub_exports == runtime_exports, module_name


def test_measured_native_container_contracts():
    vertices = np.asarray([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
    faces = np.asarray([[0, 1, 2]], dtype=np.int32)
    centroid = _measure.centroid(vertices, faces)

    assert isinstance(centroid, _types_std.VectorDouble)
    assert all(isinstance(coordinate, float) for coordinate in centroid)

    boundary = np.asarray([[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0]], dtype=np.float64)
    skeleton_vertices, skeleton_types, skeleton_edges, skeleton_face_indices = _straight_skeleton_2.create_interior_straight_skeleton(boundary)

    assert isinstance(skeleton_vertices, np.ndarray)
    assert isinstance(skeleton_types, list)
    assert isinstance(skeleton_edges, np.ndarray)
    assert isinstance(skeleton_face_indices, list)
    assert skeleton_vertices.dtype == np.float64
    assert skeleton_edges.dtype == np.int32


def test_native_vector_stubs_describe_sequence_behavior():
    values = _types_std.VectorInt([1, 2, 3])

    assert not isinstance(values, list)
    assert list(values) == [1, 2, 3]
    assert isinstance(values[1:], _types_std.VectorInt)
    values[1:] = [4, 5]
    values.append(6)
    assert list(values) == [1, 4, 5, 6]


def test_native_dual_accepts_measured_fixed_vertex_containers():
    vertices = np.asarray(
        [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]],
        dtype=np.float64,
    )
    faces = np.asarray(
        [[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6], [0, 5, 1], [0, 4, 5], [2, 7, 3], [2, 6, 7], [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2]],
        dtype=np.int32,
    )

    containers = (
        [0, 2],
        (0, 2),
        range(0, 3, 2),
        [np.int32(0), np.int64(2)],
        np.asarray([0, 2], dtype=np.int8),
        np.asarray([0, 2], dtype=np.int16),
        np.asarray([0, 2], dtype=np.int32),
        np.asarray([0, 2], dtype=np.int64),
        np.asarray([0, 2], dtype=np.uint8),
        np.asarray([0, 2], dtype=np.uint32),
        np.asarray([0, 2], dtype=np.uint64),
        _types_std.VectorInt([0, 2]),
    )
    for fixed_vertices in containers:
        result = _meshing.pmp_trimesh_remesh_dual(vertices, faces, fixed_vertices, 1.0, 1, 0.9, 1.0)

        assert result[0].shape[1] == 3
        assert result[1].shape[1] == 3


@pytest.mark.parametrize(
    "fixed_vertices",
    [
        np.asarray([False, True], dtype=np.bool_),
        np.asarray([0.0, 2.0], dtype=np.float32),
        [0.0, 2.0],
    ],
)
def test_native_dual_rejects_noninteger_fixed_vertex_containers(fixed_vertices):
    vertices = np.asarray([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
    faces = np.asarray([[0, 1, 2]], dtype=np.int32)

    with pytest.raises(TypeError):
        _meshing.pmp_trimesh_remesh_dual(vertices, faces, fixed_vertices, 1.0, 1, 0.9, 1.0)


def test_dual_fixed_vertices_are_normalized_for_native_abi(monkeypatch):
    captured = {}

    def dual(vertices, faces, fixed_vertices, *args):
        captured["vertices"] = vertices
        captured["faces"] = faces
        captured["fixed_vertices"] = fixed_vertices
        return vertices, faces, vertices, [[0, 1, 2]]

    monkeypatch.setattr(meshing._meshing, "pmp_trimesh_remesh_dual", dual)
    mesh = ([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])

    containers = (
        [0, 2],
        (0, 2),
        range(0, 3, 2),
        np.asarray([0, 2], dtype=np.int32),
        np.asarray([0, 2], dtype=np.int64),
    )
    for fixed_vertices in containers:
        meshing.trimesh_dual(mesh, fixed_vertices=fixed_vertices)

        assert captured["vertices"].dtype == np.float64
        assert captured["faces"].dtype == np.int32
        assert captured["fixed_vertices"].dtype == np.int32
        assert captured["fixed_vertices"].flags.c_contiguous


def test_native_intersection_result_is_list_of_float_arrays():
    vertices_a = np.asarray(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
        dtype=np.float64,
    )
    vertices_b = vertices_a + np.asarray([0.25, 0.25, 0.25])
    faces = np.asarray([[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]], dtype=np.int32)

    polylines = _intersections.intersection_mesh_mesh(vertices_a, faces, vertices_b, faces)

    assert isinstance(polylines, _types_std.VectorRowMatrixXd)
    assert polylines
    assert all(isinstance(polyline, np.ndarray) for polyline in polylines)
    assert all(polyline.dtype == np.float64 for polyline in polylines)


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
    assert set(module_names) == set(NATIVE_MODULES)
    assert not [name for name in module_names if not (package / f"{name}.pyi").is_file()]
