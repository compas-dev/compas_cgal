from typing import Iterable
from typing import Literal

import numpy as np
from compas.plugins import plugin

from compas_cgal import _booleans  # type: ignore

from .types import VerticesFaces
from .types import VerticesFacesEdgesNumpy
from .types import VerticesFacesNumpy
from .types import VerticesFacesSourceNumpy


def _boolean(
    A: VerticesFaces,
    B: VerticesFaces,
    operation: Literal["union", "difference", "intersection"],
) -> VerticesFacesNumpy:
    """Wrapper for all boolean operations.

    Parameters
    ----------
    A
        Mesh A.
    B
        Mesh B.
    operation
        The type of boolean operation.

    Returns
    -------
    VerticesFacesNumpy

    Raises
    ------
    NotImplementedError
        If the operation type is not supported.

    """
    VA, FA = A
    VB, FB = B
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)

    if operation == "union":
        result = _booleans.boolean_union(VA, FA, VB, FB)
    elif operation == "difference":
        result = _booleans.boolean_difference(VA, FA, VB, FB)
    elif operation == "intersection":
        result = _booleans.boolean_intersection(VA, FA, VB, FB)
    elif operation == "split":
        result = _booleans.split(VA, FA, VB, FB)
    else:
        raise NotImplementedError

    return result


@plugin(category="booleans", pluggable_name="boolean_union_mesh_mesh")
def boolean_union_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Boolean union of two meshes.

    Parameters
    ----------
    A
        Mesh A.
    B
        Mesh B.

    Returns
    -------
    VerticesFacesNumpy

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import boolean_union_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> C = boolean_union_mesh_mesh(A, B)
    >>> shape = Polyhedron(*C)

    """
    return _boolean(A, B, "union")


@plugin(category="booleans", pluggable_name="boolean_difference_mesh_mesh")
def boolean_difference_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Boolean difference of two meshes.

    Parameters
    ----------
    A
        Mesh A.
    B
        Mesh B.

    Returns
    -------
    VerticesFacesNumpy

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import boolean_difference_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> C = boolean_difference_mesh_mesh(A, B)
    >>> shape = Polyhedron(*C)

    """
    return _boolean(A, B, "difference")


@plugin(category="booleans", pluggable_name="boolean_intersection_mesh_mesh")
def boolean_intersection_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Boolean intersection of two meshes.

    Parameters
    ----------
    A
        Mesh A.
    B
        Mesh B.

    Returns
    -------
    VerticesFacesNumpy

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import boolean_intersection_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> C = boolean_intersection_mesh_mesh(A, B)
    >>> shape = Polyhedron(*C)

    """
    return _boolean(A, B, "intersection")


@plugin(category="booleans", pluggable_name="split_mesh_mesh")
def split_mesh_mesh(
    A: VerticesFaces,
    B: VerticesFaces,
) -> VerticesFacesNumpy:
    """Split one mesh with another.

    Parameters
    ----------
    A
        Mesh A.
    B
        Mesh B.

    Returns
    -------
    VerticesFacesNumpy

    Examples
    --------
    >>> from compas.geometry import Box, Sphere, Polyhedron
    >>> from compas_cgal.booleans import split_mesh_mesh

    >>> box = Box(1)
    >>> sphere = Sphere(0.5, point=[1, 1, 1])

    >>> A = box.to_vertices_and_faces(triangulated=True)
    >>> B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> V, F = split_mesh_mesh(A, B)
    >>> shape = Polyhedron(V.tolist(), F.tolist())

    """
    return _boolean(A, B, "split")  # type: ignore


split = split_mesh_mesh


def _boolean_with_edges(
    A: VerticesFaces,
    B: VerticesFaces,
    operation: Literal["union", "difference", "intersection"],
) -> VerticesFacesEdgesNumpy:
    VA, FA = A
    VB, FB = B
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)

    if operation == "union":
        return _booleans.boolean_union_with_edges(VA, FA, VB, FB)
    if operation == "difference":
        return _booleans.boolean_difference_with_edges(VA, FA, VB, FB)
    if operation == "intersection":
        return _booleans.boolean_intersection_with_edges(VA, FA, VB, FB)
    raise NotImplementedError(operation)


def boolean_union_mesh_mesh_with_edges(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesEdgesNumpy:
    """Boolean union returning (V, F, E) where E lists vertex-index pairs of intersection-curve edges.

    The edges are the corefinement intersection curve in the output mesh and can be
    used to recover clean polygonal outlines / face groupings without remeshing.
    See CGAL discussion #8711.
    """
    return _boolean_with_edges(A, B, "union")


def boolean_difference_mesh_mesh_with_edges(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesEdgesNumpy:
    """Boolean difference returning (V, F, E). See `boolean_union_mesh_mesh_with_edges`."""
    return _boolean_with_edges(A, B, "difference")


def boolean_intersection_mesh_mesh_with_edges(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesEdgesNumpy:
    """Boolean intersection returning (V, F, E). See `boolean_union_mesh_mesh_with_edges`."""
    return _boolean_with_edges(A, B, "intersection")


def _concat_meshes(meshes: Iterable[VerticesFaces]) -> VerticesFacesNumpy:
    Vs: list[np.ndarray] = []
    Fs: list[np.ndarray] = []
    offset = 0
    for V, F in meshes:
        V = np.asarray(V, dtype=np.float64)
        F = np.asarray(F, dtype=np.int32)
        Vs.append(V)
        Fs.append(F + offset)
        offset += V.shape[0]
    if not Vs:
        return np.zeros((0, 3), dtype=np.float64), np.zeros((0, 3), dtype=np.int32)
    return np.vstack(Vs), np.vstack(Fs)


def _boolean_with_face_source(
    A: VerticesFaces,
    B: VerticesFaces,
    operation: Literal["union", "difference", "intersection"],
) -> VerticesFacesSourceNumpy:
    VA, FA = A
    VB, FB = B
    VA = np.asarray(VA, dtype=np.float64)
    FA = np.asarray(FA, dtype=np.int32)
    VB = np.asarray(VB, dtype=np.float64)
    FB = np.asarray(FB, dtype=np.int32)

    if operation == "union":
        return _booleans.boolean_union_with_face_source(VA, FA, VB, FB)
    if operation == "difference":
        return _booleans.boolean_difference_with_face_source(VA, FA, VB, FB)
    if operation == "intersection":
        return _booleans.boolean_intersection_with_face_source(VA, FA, VB, FB)
    raise NotImplementedError(operation)


def boolean_union_mesh_mesh_with_face_source(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesSourceNumpy:
    """Boolean union returning (V, F, S) where S[i] = [mesh_id, face_id] of the input face that produced output face i.

    `mesh_id` is 0 for A and 1 for B; `face_id` is the original face index into FA / FB.
    Tracking is done through a CGAL corefinement visitor so face splits during the
    boolean are correctly propagated to all sub-faces.
    """
    return _boolean_with_face_source(A, B, "union")


def boolean_difference_mesh_mesh_with_face_source(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesSourceNumpy:
    """Boolean difference returning (V, F, S). See `boolean_union_mesh_mesh_with_face_source`."""
    return _boolean_with_face_source(A, B, "difference")


def boolean_intersection_mesh_mesh_with_face_source(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesSourceNumpy:
    """Boolean intersection returning (V, F, S). See `boolean_union_mesh_mesh_with_face_source`."""
    return _boolean_with_face_source(A, B, "intersection")


_OP_CODES = {"union": 0, "difference": 1, "intersection": 2, "xor": 3}


def boolean_chain(
    meshes: Iterable[VerticesFaces],
    operations: Iterable[Literal["union", "difference", "intersection", "xor"]],
    exact: bool = True,
) -> VerticesFacesNumpy:
    """Run a chain of boolean operations entirely in C++ without round-tripping intermediates.

    Computes ``result = meshes[0]; result = result OP_i meshes[i+1]`` for each
    operation in order. The full collection of input meshes is sent to C++ in a
    single call; intermediate meshes never leave C++; only the final ``(V, F)``
    is returned to Python. Between successive corefinements the intermediate
    mesh is passed through ``autorefine_and_remove_self_intersections`` so that
    near-degenerate geometry introduced by EPICK's approximate constructions
    does not break the next operation.

    Parameters
    ----------
    meshes : iterable of (V, F)
        Triangle meshes. Length must be ``len(operations) + 1``.
    operations : iterable of {"union", "difference", "intersection", "xor"}
        Per-step operation. ``"difference"`` is ``result - meshes[i+1]``.
        ``"xor"`` is the symmetric difference.

    Returns
    -------
    (V, F) : VerticesFacesNumpy
        The final mesh.

    Notes
    -----
    With ``exact=True`` (default) the chain runs in CGAL's
    ``Exact_predicates_exact_constructions_kernel`` (EPECK). Constructions
    are lazy-exact: there are no rounding artifacts on cut boundaries, so
    no snap rounding is needed and the chain handles geometrically
    degenerate input — e.g., three cylinders meeting at the origin —
    without any shifts. ``xor`` is implemented as ``(A−B) ∪ (B−A)`` and is
    fully reliable on overlapping inputs because EPECK keeps the shared
    boundary curve exact.

    With ``exact=False`` the chain uses
    ``Exact_predicates_inexact_constructions_kernel`` (EPICK) and applies
    CGAL 6.1's autorefine + iterative snap rounding between steps. This is
    faster but ``xor`` on partially-overlapping inputs may return an empty
    mesh because snap rounding collapses the shared boundary.
    """
    Vs: list[np.ndarray] = []
    Fs: list[np.ndarray] = []
    v_counts: list[int] = []
    f_counts: list[int] = []
    for V, F in meshes:
        V = np.asarray(V, dtype=np.float64)
        F = np.asarray(F, dtype=np.int32)
        Vs.append(V)
        Fs.append(F)
        v_counts.append(int(V.shape[0]))
        f_counts.append(int(F.shape[0]))

    op_codes: list[int] = []
    for op in operations:
        if op not in _OP_CODES:
            raise ValueError(f"unknown operation {op!r}; must be one of {sorted(_OP_CODES)}")
        op_codes.append(_OP_CODES[op])

    if len(op_codes) + 1 != len(Vs):
        raise ValueError("len(operations) must equal len(meshes) - 1")

    # Concatenate all meshes into single V and F arrays. Face indices stay
    # mesh-local; the per-mesh row counts tell C++ where each mesh starts.
    # This is the entire Python -> C++ marshalling for the chain.
    V_flat = np.vstack(Vs) if Vs else np.zeros((0, 3), dtype=np.float64)
    F_flat = np.vstack(Fs) if Fs else np.zeros((0, 3), dtype=np.int32)

    if exact:
        return _booleans.boolean_chain_exact(V_flat, F_flat, v_counts, f_counts, op_codes)
    return _booleans.boolean_chain(V_flat, F_flat, v_counts, f_counts, op_codes)


def boolean_chain_with_face_source(
    meshes: Iterable[VerticesFaces],
    operations: Iterable[Literal["union", "difference", "intersection"]],
    exact: bool = True,
) -> VerticesFacesSourceNumpy:
    """Boolean chain that also tracks, for every output face, which input mesh
    and which input face produced it. Returns ``(V, F, S)`` where ``S[i] =
    [mesh_id, face_id]``. ``mesh_id`` is the position of the source mesh in
    ``meshes`` and ``face_id`` is its row in that mesh's input face array.

    Tracking is done via a CGAL corefinement visitor that propagates per-face
    tags through subface creations and face copies — the technique used in
    the Cockroach project for CGAL face-color tracking through booleans.

    With ``exact=True`` (default) the chain runs on EPECK Surface_meshes,
    so the visitor works directly on geometrically degenerate input — no
    cylinder offsets needed.

    With ``exact=False`` the chain uses EPICK without snap rounding (because
    the visitor's property maps cannot survive the soup conversion that
    snap rounding requires). The chain may then trip CGAL's "Non-handled
    triple intersection" precondition on inputs that share an axis or
    vertex; geometrically perturb the inputs to break the degeneracy.

    ``"xor"`` is not supported here.
    """
    Vs: list[np.ndarray] = []
    Fs: list[np.ndarray] = []
    v_counts: list[int] = []
    f_counts: list[int] = []
    for V, F in meshes:
        V = np.asarray(V, dtype=np.float64)
        F = np.asarray(F, dtype=np.int32)
        Vs.append(V)
        Fs.append(F)
        v_counts.append(int(V.shape[0]))
        f_counts.append(int(F.shape[0]))

    op_codes: list[int] = []
    for op in operations:
        if op == "xor":
            raise ValueError("xor is not supported by boolean_chain_with_face_source")
        if op not in _OP_CODES:
            raise ValueError(f"unknown operation {op!r}; must be one of union/difference/intersection")
        op_codes.append(_OP_CODES[op])

    if len(op_codes) + 1 != len(Vs):
        raise ValueError("len(operations) must equal len(meshes) - 1")

    V_flat = np.vstack(Vs) if Vs else np.zeros((0, 3), dtype=np.float64)
    F_flat = np.vstack(Fs) if Fs else np.zeros((0, 3), dtype=np.int32)

    if exact:
        return _booleans.boolean_chain_with_face_source_exact(V_flat, F_flat, v_counts, f_counts, op_codes)
    return _booleans.boolean_chain_with_face_source(V_flat, F_flat, v_counts, f_counts, op_codes)


def split_by_source(
    V: np.ndarray,
    F: np.ndarray,
    S: np.ndarray,
) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """Split a face-source-tagged boolean result into one mesh per source.

    Given ``(V, F, S)`` from :func:`boolean_chain_with_face_source`, returns a
    dict mapping each ``mesh_id`` present in ``S[:, 0]`` to its own
    ``(V_sub, F_sub)`` pair. ``V_sub`` contains only the vertices referenced
    by that submesh's faces and ``F_sub`` is reindexed accordingly.

    Note: vertices on the boundary between two source regions are duplicated
    across the resulting submeshes (each submesh gets its own copy), so the
    submeshes are no longer connected at cut boundaries. The original ``(V,
    F, S)`` remains the canonical output — use this helper only when a
    per-source mesh layout is convenient (e.g. assigning a single colour or
    material to a viewer scene object).
    """
    V = np.asarray(V)
    F = np.asarray(F)
    S = np.asarray(S)

    out: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for mesh_id in np.unique(S[:, 0]):
        face_mask = S[:, 0] == mesh_id
        F_sub = F[face_mask]
        used = np.unique(F_sub.reshape(-1))
        remap = np.full(V.shape[0], -1, dtype=np.int64)
        remap[used] = np.arange(used.shape[0])
        out[int(mesh_id)] = (V[used], remap[F_sub].astype(F.dtype))
    return out


def boolean_difference_mesh_meshes(A: VerticesFaces, Bs: Iterable[VerticesFaces]) -> VerticesFacesNumpy:
    """Subtract many meshes from A in a single corefinement.

    Sequential `A = A - B_i` chains accumulate subdivision and round-off, which can
    crash CGAL's corefinement on long sequences (see CGAL issue #9282). Merging the
    cutters into one disjoint operand and doing a single difference avoids that.

    The cutters in `Bs` should not overlap each other; if they do, merge them first
    via `boolean_union_mesh_mesh` and pass the union as a single operand.
    """
    B = _concat_meshes(Bs)
    return _boolean(A, B, "difference")
