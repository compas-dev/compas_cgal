"""Tests for the signed distance to a closed triangle mesh, against a box in closed form."""

import threading
import time

import numpy as np
import pytest

from compas_cgal.distance import MeshDistance

# A box that is neither centred nor dyadic, so that every coordinate rounds.
BOX_CENTRE = np.array([0.3, -0.2, 0.1])
BOX_HALF = np.array([0.7, 0.45, 1.1])
BOX_LOW = BOX_CENTRE - BOX_HALF
BOX_HIGH = BOX_CENTRE + BOX_HALF

QUERY_COUNT = 20000
QUERY_SEED = 0
# Half width of the cube the random queries are drawn from, around the box centre.
QUERY_REACH = 2.5

# Largest difference between the binding and the closed form, for a distance or a coordinate
# of a closest point. Both sides are a few dozen float64 operations on numbers no larger than
# COORDINATE_SCALE, each rounding by at most half a unit in the last place: 16 of them bound
# the difference (measured: 4.4e-16 on the distances, 5.6e-16 on the closest points, 9.0e-16 on
# the gradients).
COORDINATE_SCALE = 4.0
ROUNDING_TOLERANCE = 16 * np.finfo(np.float64).eps * COORDINATE_SCALE
# Smallest gap between the two nearest sides for an interior query to count as off the
# medial axis, where the closest side and so the gradient are not unique.
MEDIAL_MARGIN = 1e-6
# Queries of the call that must leave the GIL free: on one thread they take a few hundred
# milliseconds (measured: 0.4 s), against the 5 ms after which CPython hands the GIL over.
GIL_QUERY_COUNT = 400000
# Pause between two notes of the watching thread, seconds.
GIL_TICK = 0.001


def box_mesh():
    """The box as 8 vertices and 12 outward-wound triangles."""
    corners = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)])
    vertices = np.where(corners == 1, BOX_HIGH, BOX_LOW)
    faces = np.array(
        [
            [0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1],
            [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3],
        ],
        dtype=np.int32,
    )  # fmt: skip
    return vertices, faces


def box_signed_distance(points):
    """Closed form: negative inside, zero on the surface."""
    q = np.maximum(BOX_LOW - points, points - BOX_HIGH)
    return np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(q.max(axis=1), 0.0)


def random_queries():
    rng = np.random.default_rng(QUERY_SEED)
    return BOX_CENTRE + rng.uniform(-QUERY_REACH, QUERY_REACH, (QUERY_COUNT, 3))


def surface_points(bound_axes):
    """Points exactly on the box: `bound_axes` coordinates on a side, the others strictly inside.

    One bound axis gives points on a face, two on an edge, three the corners. Returns the points
    and, per point and axis, -1, 0 or +1: the side the coordinate sits on.
    """
    rng = np.random.default_rng(QUERY_SEED + bound_axes)
    count = 400
    points = BOX_CENTRE + rng.uniform(-0.9, 0.9, (count, 3)) * BOX_HALF
    sides = np.zeros((count, 3))
    for i in range(count):
        for axis in rng.permutation(3)[:bound_axes]:
            sides[i, axis] = rng.choice((-1.0, 1.0))
            points[i, axis] = BOX_HIGH[axis] if sides[i, axis] > 0 else BOX_LOW[axis]
    return points, sides


def on_triangle(point, triangle):
    """Whether `point` lies on `triangle`, to the rounding tolerance."""
    a, b, c = triangle
    normal = np.cross(b - a, c - a)
    normal /= np.linalg.norm(normal)
    if abs(np.dot(point - a, normal)) > ROUNDING_TOLERANCE:
        return False
    for start, end in ((a, b), (b, c), (c, a)):
        if np.dot(np.cross(end - start, point - start), normal) < -ROUNDING_TOLERANCE:
            return False
    return True


def test_distance_and_closest_point_equal_the_closed_form():
    queries = random_queries()
    distances, closest, _, _ = MeshDistance(box_mesh()).signed_distance(queries)

    assert distances.shape == (QUERY_COUNT,)
    assert closest.shape == (QUERY_COUNT, 3)
    assert np.abs(distances - box_signed_distance(queries)).max() <= ROUNDING_TOLERANCE

    # Outside the box the closest point is the query clamped into it.
    outside = box_signed_distance(queries) > 0
    assert outside.sum() > QUERY_COUNT // 2
    clamped = np.clip(queries[outside], BOX_LOW, BOX_HIGH)
    assert np.abs(closest[outside] - clamped).max() <= ROUNDING_TOLERANCE


def test_sign_is_negative_inside_and_positive_outside():
    queries = random_queries()
    distances, _, _, _ = MeshDistance(box_mesh()).signed_distance(queries)
    inside = np.all((queries > BOX_LOW) & (queries < BOX_HIGH), axis=1)

    assert inside.sum() > 100
    assert np.all(distances[inside] < 0)
    assert np.all(distances[~inside] > 0)


@pytest.mark.parametrize("bound_axes", [1, 2, 3])
def test_a_point_on_the_mesh_is_at_distance_zero(bound_axes):
    points, _ = surface_points(bound_axes)
    distances, closest, _, _ = MeshDistance(box_mesh()).signed_distance(points)

    assert np.all(distances == 0.0)
    assert np.array_equal(closest, points)


@pytest.mark.parametrize("bound_axes", [1, 2, 3])
def test_sign_is_right_one_rounding_step_off_the_mesh(bound_axes):
    points, sides = surface_points(bound_axes)
    solver = MeshDistance(box_mesh())
    on_side = sides != 0

    outward = np.where(on_side, np.nextafter(points, points + sides), points)
    assert np.all(solver.signed_distance(outward)[0] > 0)

    inward = np.where(on_side, np.nextafter(points, points - sides), points)
    assert np.all(solver.signed_distance(inward)[0] < 0)


def test_face_is_one_the_closest_point_lies_on():
    queries = random_queries()[:2000]
    vertices, faces = box_mesh()
    _, closest, face_indices, _ = MeshDistance((vertices, faces)).signed_distance(queries)

    assert face_indices.shape == (2000,)
    assert face_indices.dtype == np.int32
    assert face_indices.min() >= 0 and face_indices.max() < len(faces)
    for point, face in zip(closest, face_indices):
        assert on_triangle(point, vertices[faces[face]])


def test_gradient_is_the_unit_direction_away_from_the_closest_point():
    queries = random_queries()
    distances, closest, _, gradients = MeshDistance(box_mesh()).signed_distance(queries)

    assert np.abs(np.linalg.norm(gradients, axis=1) - 1.0).max() <= ROUNDING_TOLERANCE

    # Outside: away from the clamped point. Inside: the outward normal of the nearest side.
    q = np.maximum(BOX_LOW - queries, queries - BOX_HIGH)
    outside = q.max(axis=1) > 0
    clamped = np.clip(queries[outside], BOX_LOW, BOX_HIGH)
    expected = (queries[outside] - clamped) / np.linalg.norm(queries[outside] - clamped, axis=1)[:, None]
    assert np.abs(gradients[outside] - expected).max() <= ROUNDING_TOLERANCE

    ordered = np.sort(q, axis=1)
    off_medial_axis = ~outside & (ordered[:, 2] - ordered[:, 1] > MEDIAL_MARGIN)
    assert off_medial_axis.sum() > 100
    nearest = q[off_medial_axis].argmax(axis=1)
    expected = np.zeros((off_medial_axis.sum(), 3))
    rows = np.arange(len(nearest))
    expected[rows, nearest] = np.sign(queries[off_medial_axis][rows, nearest] - BOX_CENTRE[nearest])
    assert np.abs(gradients[off_medial_axis] - expected).max() <= ROUNDING_TOLERANCE


@pytest.mark.parametrize("bound_axes", [1, 2, 3])
def test_gradient_on_the_mesh_is_the_pseudonormal_of_the_feature(bound_axes):
    """On a face its normal, on an edge the mean of its two faces', at a corner all three's."""
    points, sides = surface_points(bound_axes)
    _, _, _, gradients = MeshDistance(box_mesh()).signed_distance(points)

    expected = sides / np.linalg.norm(sides, axis=1)[:, None]
    assert np.abs(gradients - expected).max() <= ROUNDING_TOLERANCE


def test_gradient_on_a_diagonal_of_a_side_is_the_normal_of_that_side():
    """The two triangles of one side share an edge, and its pseudonormal is their normal."""
    vertices, faces = box_mesh()
    # Faces 0 and 1 share the diagonal from vertex 0 to vertex 3, on the side x = low.
    midpoint = 0.5 * (vertices[0] + vertices[3])
    distances, _, _, gradients = MeshDistance((vertices, faces)).signed_distance(midpoint[None, :])

    assert abs(distances[0]) <= ROUNDING_TOLERANCE
    assert np.abs(gradients[0] - np.array([-1.0, 0.0, 0.0])).max() <= ROUNDING_TOLERANCE


def test_closest_agrees_with_signed_distance():
    queries = random_queries()
    solver = MeshDistance(box_mesh())
    _, closest, face_indices, _ = solver.signed_distance(queries)
    points, faces = solver.closest(queries)

    assert np.array_equal(points, closest)
    assert np.array_equal(faces, face_indices)


def test_two_builds_answer_bit_for_bit_the_same():
    queries = np.concatenate([random_queries()] + [surface_points(n)[0] for n in (1, 2, 3)])
    first = MeshDistance(box_mesh()).signed_distance(queries)
    second = MeshDistance(box_mesh()).signed_distance(queries)

    for a, b in zip(first, second):
        assert np.array_equal(a, b)


def test_closest_works_on_an_open_mesh_and_signed_distance_refuses_it():
    vertices, faces = box_mesh()
    solver = MeshDistance((vertices, faces[:-1]))
    queries = random_queries()[:100]

    points, face_indices = solver.closest(queries)
    assert points.shape == (100, 3)
    assert face_indices.max() < len(faces) - 1
    with pytest.raises(ValueError, match="closed"):
        solver.signed_distance(queries)


def box_with_a_vertex_on_an_edge(flat):
    """The box with a ninth vertex midway along the edge from vertex 0 to vertex 2.

    The side below the edge is cut at the new vertex. The side beside it is cut there too, or,
    when `flat`, left whole with the triangle (0, 2, 8) filling the gap: three corners on one
    line. Either way the mesh is closed, manifold and wound outwards.
    """
    vertices, faces = box_mesh()
    vertices = np.concatenate([vertices, 0.5 * (vertices[[0]] + vertices[[2]])])
    cut = []
    for face in faces.tolist():
        if face == [0, 2, 6]:
            cut += [[0, 8, 6], [8, 2, 6]]
        elif face == [0, 3, 2]:
            cut += [[0, 3, 2], [0, 2, 8]] if flat else [[0, 3, 8], [8, 3, 2]]
        else:
            cut.append(face)
    return vertices, np.array(cut, dtype=np.int32)


def test_a_face_without_area_is_refused():
    """A face with its corners on one line has no normal, so no gradient for a query on it."""
    queries = random_queries()[:2000]
    distances, _, _, gradients = MeshDistance(box_with_a_vertex_on_an_edge(flat=False)).signed_distance(queries)
    assert np.abs(distances - box_signed_distance(queries)).max() <= ROUNDING_TOLERANCE
    assert np.isfinite(gradients).all()

    with pytest.raises(ValueError, match="degenerate"):
        MeshDistance(box_with_a_vertex_on_an_edge(flat=True))


def test_a_face_without_area_is_refused_where_rounding_hides_it():
    """The corners d, 2d and 4d lie on one line exactly, and their cross product in floats is not zero."""
    step = np.array([0.1, 0.2, 0.3])
    # A tetrahedron on d, 4d and two points off their line, with 2d as a fifth vertex on that edge.
    vertices = np.array([step, 4 * step, [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], 2 * step])
    # The edges from d are d and 3d, and 3d is not a float: it rounds, coordinate by coordinate.
    assert np.any(np.cross(vertices[4] - vertices[0], vertices[1] - vertices[0]) != 0.0)

    # The face on one side of the edge is cut at the fifth vertex; (0, 1, 4) fills the gap.
    faces = np.array([[0, 2, 1], [0, 4, 3], [4, 1, 3], [0, 1, 4], [0, 3, 2], [1, 2, 3]], dtype=np.int32)
    if np.linalg.det(vertices[1:4] - vertices[0]) < 0:
        faces = faces[:, ::-1]

    with pytest.raises(ValueError, match="face 3 is degenerate"):
        MeshDistance((vertices, faces))


def test_faces_between_two_vertices_at_one_place_are_refused():
    vertices, faces = box_mesh()
    vertices[1] = vertices[0]

    with pytest.raises(ValueError, match="degenerate"):
        MeshDistance((vertices, faces))


def test_a_face_that_names_a_missing_vertex_is_refused():
    vertices, faces = box_mesh()
    broken = faces.copy()
    broken[0, 0] = len(vertices)

    with pytest.raises(ValueError, match="vertex"):
        MeshDistance((vertices, broken))


def test_queries_that_are_not_points_in_space_are_refused():
    solver = MeshDistance(box_mesh())

    with pytest.raises(ValueError, match="3"):
        solver.signed_distance(np.zeros((5, 2)))


@pytest.mark.parametrize("num_threads", [None, 2, 7])
def test_the_number_of_threads_does_not_change_the_answer(num_threads):
    queries = np.concatenate([random_queries()] + [surface_points(n)[0] for n in (1, 2, 3)])
    solver = MeshDistance(box_mesh())

    one = solver.signed_distance(queries, num_threads=1)
    many = solver.signed_distance(queries, num_threads=num_threads)
    for a, b in zip(one, many):
        assert np.array_equal(a, b)

    one = solver.closest(queries, num_threads=1)
    many = solver.closest(queries, num_threads=num_threads)
    for a, b in zip(one, many):
        assert np.array_equal(a, b)


def test_a_negative_number_of_threads_is_refused():
    solver = MeshDistance(box_mesh())

    with pytest.raises(ValueError, match="thread"):
        solver.signed_distance(random_queries()[:10], num_threads=-1)
    with pytest.raises(ValueError, match="thread"):
        solver.closest(random_queries()[:10], num_threads=-1)


def test_queries_release_the_gil():
    """Another Python thread runs while a query is answered, not only after it."""
    solver = MeshDistance(box_mesh())
    rng = np.random.default_rng(QUERY_SEED)
    queries = BOX_CENTRE + rng.uniform(-QUERY_REACH, QUERY_REACH, (GIL_QUERY_COUNT, 3))
    ticks = []
    started, stop = threading.Event(), threading.Event()

    def watch():
        started.set()
        while not stop.is_set():
            ticks.append(time.perf_counter())
            time.sleep(GIL_TICK)

    watcher = threading.Thread(target=watch)
    watcher.start()
    started.wait()
    begin = time.perf_counter()
    solver.signed_distance(queries, num_threads=1)
    end = time.perf_counter()
    stop.set()
    watcher.join()

    # With the GIL held the watcher wakes only once the call has returned: late in the interval.
    first_half = [t for t in ticks if begin < t < 0.5 * (begin + end)]
    assert len(first_half) > 0
