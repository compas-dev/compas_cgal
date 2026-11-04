import gc
from pathlib import Path

import numpy as np
import pytest

from compas_cgal import measure
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
