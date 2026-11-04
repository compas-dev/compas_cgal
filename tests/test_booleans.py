import pytest
import numpy as np

from compas.geometry import Box, Frame, Native, Sphere, UGrid, UVGrid
from compas.geometry import boolean_difference_mesh_mesh as core_boolean_difference
from compas.geometry import boolean_intersection_mesh_mesh as core_boolean_intersection
from compas.geometry import boolean_union_mesh_mesh as core_boolean_union
from compas.datastructures import Mesh

from compas_cgal.booleans import (
    boolean_chain,
    boolean_chain_with_face_source,
    boolean_difference_mesh_mesh,
    boolean_difference_mesh_mesh_with_edges,
    boolean_difference_mesh_mesh_with_face_source,
    boolean_difference_mesh_meshes,
    boolean_intersection_mesh_mesh,
    boolean_intersection_mesh_mesh_with_edges,
    boolean_intersection_mesh_mesh_with_face_source,
    boolean_union_mesh_mesh_with_edges,
    boolean_union_mesh_mesh_with_face_source,
    boolean_union_mesh_mesh,
    split_mesh_mesh,
)


@pytest.fixture
def box_sphere_meshes():
    """Create test box and sphere meshes."""
    box = Box.from_width_height_depth(2.0, 2.0, 2.0)
    sphere = Sphere(1.0, frame=Frame([1, 1, 1], [1, 0, 0], [0, 1, 0]))

    box_mesh = box.tessellate(Native()).to_vertices_and_triangles()
    sphere_mesh = sphere.tessellate(UVGrid(32, 32)).to_vertices_and_triangles()

    return box_mesh, sphere_mesh


def test_boolean_union(box_sphere_meshes):
    """Test boolean union operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = core_boolean_union(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3  # 3D points
    assert faces.shape[1] == 3  # Triangle faces
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify topology
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()
    assert mesh.euler() == 2  # Valid closed manifold


def test_boolean_difference(box_sphere_meshes):
    """Test boolean difference operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = core_boolean_difference(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3
    assert faces.shape[1] == 3
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify topology
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()
    assert mesh.euler() == 2  # Valid closed manifold


def test_boolean_intersection(box_sphere_meshes):
    """Test boolean intersection operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = core_boolean_intersection(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3
    assert faces.shape[1] == 3
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify topology
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()
    assert mesh.euler() == 2  # Valid closed manifold


def _tetrahedron():
    return (
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]],
    )


@pytest.mark.parametrize(
    ("function", "native_name"),
    [
        (boolean_union_mesh_mesh, "boolean_union"),
        (boolean_difference_mesh_mesh, "boolean_difference"),
        (boolean_intersection_mesh_mesh, "boolean_intersection"),
    ],
)
@pytest.mark.parametrize(
    ("invalid", "error", "message"),
    [
        (([[0, 0]], [[0, 0, 0]]), ValueError, r"shape \(N, 3\)"),
        (([[0, 0, float("nan")]], [[0, 0, 0]]), ValueError, "finite"),
        (([[0, 0, 0]], [[0, 0]]), ValueError, r"shape \(M, 3\)"),
        (([[0, 0, 0]], np.asarray([[0, 0, 2**32]], dtype=np.int64)), OverflowError, "range supported by CGAL"),
        (([[0, 0, 0]], [[-1, 0, 0]]), IndexError, "out of range"),
        (([[0, 0, 0]], [[0, 0, 1]]), IndexError, "out of range"),
    ],
)
def test_direct_boolean_rejects_unsafe_native_buffers(monkeypatch, function, native_name, invalid, error, message):
    def fail_if_called(*args):
        raise AssertionError("native boolean should not be called")

    monkeypatch.setattr(f"compas_cgal.booleans._booleans.{native_name}", fail_if_called)

    with pytest.raises(error, match=message):
        function(invalid, _tetrahedron())


def test_direct_boolean_leaves_topology_validation_to_cgal(monkeypatch):
    captured = []

    def boolean(*arrays):
        captured.extend(arrays)
        return np.empty((0, 3), dtype=np.float64), np.empty((0, 3), dtype=np.int32)

    monkeypatch.setattr("compas_cgal.booleans._booleans.boolean_union", boolean)
    open_triangle = ([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])

    vertices, faces = boolean_union_mesh_mesh(open_triangle, open_triangle)

    assert len(captured) == 4
    assert vertices.shape == (0, 3)
    assert faces.shape == (0, 3)


@pytest.mark.parametrize(
    "result",
    [
        (np.empty((0, 2), dtype=np.float64), np.empty((0, 3), dtype=np.int32)),
        (np.empty((0, 3), dtype=np.float64), np.empty((0, 4), dtype=np.int32)),
    ],
)
def test_direct_boolean_rejects_invalid_native_result_shape(monkeypatch, result):
    monkeypatch.setattr("compas_cgal.booleans._booleans.boolean_union", lambda *args: result)

    with pytest.raises(RuntimeError, match="CGAL Boolean result"):
        boolean_union_mesh_mesh(_tetrahedron(), _tetrahedron())


def test_direct_boolean_propagates_native_failure(monkeypatch):
    def fail(*args):
        raise RuntimeError("CGAL Boolean union failed.")

    monkeypatch.setattr("compas_cgal.booleans._booleans.boolean_union", fail)

    with pytest.raises(RuntimeError, match="CGAL Boolean union failed"):
        boolean_union_mesh_mesh(_tetrahedron(), _tetrahedron())


def test_split(box_sphere_meshes):
    """Test mesh split operation."""
    mesh_a, mesh_b = box_sphere_meshes
    vertices, faces = split_mesh_mesh(mesh_a, mesh_b)

    assert isinstance(vertices, np.ndarray)
    assert isinstance(faces, np.ndarray)
    assert vertices.shape[1] == 3
    assert faces.shape[1] == 3
    assert len(vertices) > 0
    assert len(faces) > 0

    # Create mesh to verify components
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    assert mesh.is_valid()

    # Split should create at least 2 connected vertex groups
    components = list(mesh.connected_vertices())
    print(components)
    assert len(components) >= 2


@pytest.mark.parametrize(
    "fn",
    [
        boolean_union_mesh_mesh_with_edges,
        boolean_difference_mesh_mesh_with_edges,
        boolean_intersection_mesh_mesh_with_edges,
    ],
)
def test_boolean_with_edges(box_sphere_meshes, fn):
    """Edge-tracking variants return (V, F, E) with valid intersection edges."""
    mesh_a, mesh_b = box_sphere_meshes
    V, F, E = fn(mesh_a, mesh_b)

    assert V.shape[1] == 3 and F.shape[1] == 3 and E.shape[1] == 2
    assert len(V) > 0 and len(F) > 0 and len(E) > 0
    # All edge indices must reference valid vertices in V.
    assert E.min() >= 0
    assert E.max() < len(V)


def test_boolean_difference_mesh_meshes(box_sphere_meshes):
    """Consolidate-then-subtract returns the same shape as a single difference."""
    box, sphere = box_sphere_meshes

    V_single, F_single = boolean_difference_mesh_mesh(box, sphere)
    V_multi, F_multi = boolean_difference_mesh_meshes(box, [sphere])

    # Single-cutter case must match the single-mesh API.
    assert V_multi.shape == V_single.shape
    assert F_multi.shape == F_single.shape

    # With a second cutter at the opposite corner, the result has more cuts.
    sphere_b = (np.asarray(sphere[0]) - np.array([2.0, 2.0, 2.0]), np.asarray(sphere[1]))
    V_two, F_two = boolean_difference_mesh_meshes(box, [sphere, sphere_b])
    assert len(V_two) > len(V_single)


@pytest.mark.parametrize(
    "fn",
    [
        boolean_union_mesh_mesh_with_face_source,
        boolean_difference_mesh_mesh_with_face_source,
        boolean_intersection_mesh_mesh_with_face_source,
    ],
)
def test_boolean_with_face_source(box_sphere_meshes, fn):
    """Face-source variants tag every output face with [mesh_id, face_id]."""
    A, B = box_sphere_meshes
    V, F, S = fn(A, B)

    assert S.shape == (F.shape[0], 2)
    mesh_ids, face_ids = S[:, 0], S[:, 1]

    # Every output face is tagged.
    assert (mesh_ids != -1).all()
    # mesh_id is 0 (A) or 1 (B); face_id is within that mesh's range.
    n_a, n_b = len(A[1]), len(B[1])
    assert ((mesh_ids != 0) | ((face_ids >= 0) & (face_ids < n_a))).all()
    assert ((mesh_ids != 1) | ((face_ids >= 0) & (face_ids < n_b))).all()
    # Both inputs contribute when the operands overlap.
    assert (mesh_ids == 0).any()
    assert (mesh_ids == 1).any()


def test_boolean_chain_single_step(box_sphere_meshes):
    """A single-step chain produces a valid closed manifold of the same kind
    as the dedicated single-call API. The exact vertex/face counts may differ
    because boolean_chain runs autorefine + snap rounding on the result, which
    folds near-coincident vertices."""
    from compas.datastructures import Mesh as ComMesh

    A, B = box_sphere_meshes
    V, F = boolean_chain([A, B], ["difference"])
    assert V.shape[1] == 3 and F.shape[1] == 3
    assert V.shape[0] > 0 and F.shape[0] > 0
    mesh = ComMesh.from_vertices_and_faces(V, F)
    assert mesh.is_valid()
    assert mesh.euler() == 2


def test_boolean_chain_xor_self_is_empty(box_sphere_meshes):
    """A xor A = empty mesh."""
    A, _ = box_sphere_meshes
    V, F = boolean_chain([A, A], ["xor"])
    assert V.shape == (0, 3) and F.shape == (0, 3)


def test_boolean_chain_validation(box_sphere_meshes):
    A, B = box_sphere_meshes
    with pytest.raises(ValueError):
        boolean_chain([A, B], ["nope"])  # unknown op
    with pytest.raises(ValueError):
        boolean_chain([A, B, A], ["difference"])  # mismatched lengths


def test_boolean_chain_with_face_source():
    """Three-mesh chain: cube - sphere - cylinder. Every output face must be
    tagged with one of {0, 1, 2}."""
    from compas.geometry import Box, Cylinder, Frame, Sphere

    cube = Box(2).tessellate(Native()).to_vertices_and_triangles()
    sphere = Sphere(0.8, frame=Frame([1, 1, 1], [1, 0, 0], [0, 1, 0])).tessellate(UVGrid(32, 32)).to_vertices_and_triangles()
    cyl = Cylinder(0.4, 4.0, Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])).tessellate(UGrid(32)).to_vertices_and_triangles()

    V, F, S = boolean_chain_with_face_source(
        [cube, sphere, cyl],
        ["difference", "difference"],
    )
    assert S.shape == (F.shape[0], 2)
    mids = S[:, 0]
    assert (mids != -1).all()
    # All three input meshes contribute (each survives in some part of the result).
    assert (mids == 0).any()
    assert (mids == 1).any()
    assert (mids == 2).any()


def test_boolean_chain_with_face_source_xor_rejected(box_sphere_meshes):
    A, B = box_sphere_meshes
    with pytest.raises(ValueError):
        boolean_chain_with_face_source([A, B], ["xor"])


def test_boolean_chain_drilled_rounded_cube():
    """Reproduces the example_boolean_difference_mesh_meshes.py CSG case
    that previously crashed with "Non-handled triple intersection" — now
    runs end-to-end thanks to autorefine_triangle_soup + snap rounding."""
    from compas.geometry import Box, Cylinder, Frame, Sphere

    cube = Box(2).tessellate(Native()).to_vertices_and_triangles()
    sphere = Sphere(1.3).tessellate(UVGrid(64, 64)).to_vertices_and_triangles()

    def cyl(axis, r=0.6):
        if axis == "x":
            frame = Frame([0, 0, 0], [0, 1, 0], [0, 0, 1])
        elif axis == "y":
            frame = Frame([0, 0, 0], [0, 0, 1], [1, 0, 0])
        else:
            frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
        return Cylinder(r, 4.0, frame).tessellate(UGrid(48)).to_vertices_and_triangles()

    V, F = boolean_chain(
        [cube, sphere, cyl("x"), cyl("y"), cyl("z")],
        ["intersection", "difference", "difference", "difference"],
    )
    assert V.shape[0] > 0
    assert F.shape[0] > 0
    assert F.shape[1] == 3


def test_boolean_with_face_source_disjoint(box_sphere_meshes):
    """When B is far away, A - B equals A and every face came from A."""
    box, sphere = box_sphere_meshes
    far_sphere = (np.asarray(sphere[0]) + np.array([100.0, 100.0, 100.0]), np.asarray(sphere[1]))

    V, F, S = boolean_difference_mesh_mesh_with_face_source(box, far_sphere)
    assert (S[:, 0] == 0).all()
    # face_ids should be a permutation of [0, n_a) since no faces were cut.
    assert sorted(S[:, 1].tolist()) == list(range(len(box[1])))
