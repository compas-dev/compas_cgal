"""Closed-form ground truth for the exact polyhedral geodesic backend.

Validating an exactness oracle against the implementation it replaces proves
agreement, not correctness. These fixtures anchor
:func:`compas_cgal.geodesics.exact_geodesic_distances` on surfaces whose
multi-source geodesic distance is known in closed form -- and, decisively, known
*for the polyhedron*, not merely for the smooth surface the polyhedron
approximates. On a boundary-aligned mesh the two coincide, so the residual left
for the test to absorb is floating-point arithmetic alone (measured at 1.6 ulp of
the fixture scale, see ``MMP_ARITHMETIC_RTOL``) rather than a discretization
budget that would have to be loosened to millimetres.

Derivations
-----------

**1. Revolved straight generator -- cylinder, cone frustum, flat annulus.**
Revolve the segment ``(rho0, z0) -> (rho1, z1)`` about the z axis; let ``L`` be
its length and ``t`` arc length along it. Mesh it as a structured
``n_theta x n_t`` grid whose vertices lie on the generator lines, with every grid
edge present, and seed every vertex of the two rims (``t = 0`` and ``t = L``).
Then at every vertex::

    d(v) = min(t(v), L - t(v))

holds *exactly on the polyhedron*. Lower bound: the surface is developable, so it
unrolls isometrically into the plane with ``t`` mapping to a coordinate of unit
gradient -- the axial coordinate for the cylinder, the polar radius for the cone
and the annulus -- hence ``t`` is 1-Lipschitz on the surface and any path from
``v`` to a source ``q`` has length ``>= |t(v) - t(q)| >= min(t, L - t)``, because
``t(q)`` is 0 or ``L``. Upper bound: the chain of grid edges along ``v``'s own
generator to the nearer rim has length exactly ``min(t, L - t)``. The argument
uses neither a regular cross-section polygon nor a uniform ``t`` spacing.

``rho0 == rho1`` is the open cylinder (``t`` = axial distance to the nearer end
ring); ``z0 == z1`` is the flat annulus (``t = r - a``, so ``d = min(r - a,
b - r)``); otherwise a cone frustum (``t`` = slant distance). *Validity:
unconditional.* The apex-wrapping caveat that governs cone point-to-point
geodesics never binds, because the whole rim is a source and angular offset zero
is therefore always available.

**2. Flat convex plate -- the genuinely two-dimensional case.** A planar convex
polygon carries the euclidean metric, so for *any* triangulation of it and *any*
source set, ``d(v) = min_s ||v - s||`` exactly. Interior vertices may be jittered
freely: the domain and its convexity are fixed by the boundary vertices alone.
With every boundary vertex seeded on a *structured* grid this collapses to
``min(x, w - x, y, h - y)``, because each interior vertex shares its row and its
column with a boundary vertex and the nearest source lands exactly on the
perpendicular foot.

**3. Open cylinder, sparse rim sources -- the unrolled prism.** The triangulated
prism has zero angle defect at every interior vertex, so it unrolls isometrically
to a flat rectangle and ``d(v) = min_s sqrt(du^2 + dt^2)`` with ``du`` the
circumferential gap reduced modulo the unrolled width. That width is
``n_theta * chord``, **not** ``2 * pi * R``: substituting the smooth
circumference injects an error of 0.20 / 0.022 / 0.0032 mm at ``n_theta`` = 16 /
48 / 128 on an R=10 mm cylinder -- thirteen orders of magnitude above the
arithmetic floor, and a silent one.

**4. Cone frustum, sparse rim sources -- REJECTED as a gate.** The frustum
unrolls to an annular sector of radii ``[s0, s1]``, and the unrolled chord is the
geodesic only while it stays outside radius ``s0``; where it would cross the hole
the true path bends around the inner rim and the chord is a strict lower bound
only. Measured on a 48x16 frustum (rho 6 -> 14 over dz 30) with a single rim
source: 102 of 816 vertices are in the crossing regime, where the chord
understates by up to 0.51 mm. The formula is also ill-conditioned as the frustum
approaches a cylinder -- ``s0 = rho0 / sin(alpha)`` diverges and the chord form
loses digits to cancellation (residual 2.0e-12 mm at ``sin(alpha) = 0.067``
against 3.6e-14 mm at 0.258). Both failure modes are why this file gates the
frustum through form (1), which is unconditional and well conditioned, and keeps
the sector form only as a *negative* pin: see
:func:`test_cone_sector_form_fails_inside_the_hole_crossing_regime`.

Why every fixture is boundary-aligned
-------------------------------------
Seeding vertices rather than the boundary curve costs a source-sampling term:
midway between two boundary vertices a distance ``d`` from the rim, the nearest
*vertex* is ``sqrt(d^2 + (h/2)^2)`` away. Measured on a cylinder whose rings are
staggered by half a step, that term is first order -- max error 0.371 / 0.186 /
0.093 / 0.046 mm as the chord halves from 3.90 to 0.49 mm, an observed order of
1.00. Boundary-aligned meshes drive it to *exactly* zero, which is what makes an
arithmetic-scale tolerance defensible here. Any fixture added to this file must
keep that alignment or it stops being an anchor.

What these fixtures cannot do alone
-----------------------------------
On the full-rim fixtures the closed-form distance is realised by a chain of mesh
edges, so Dijkstra over the edge graph reproduces it exactly (measured excess
0.000 %) and the test cannot tell an exact geodesic solver from a graph
shortest-path one. The sparse-source and jittered fixtures close that hole --
graph excess of 4.9 % to 12.7 % median, up to 41.4 % -- and
:func:`test_fixtures_discriminate_against_graph_shortest_paths` pins it so the
suite cannot be silently reduced to the gameable half.
"""

import heapq

import numpy as np
import pytest

from compas_cgal.geodesics import exact_geodesic_distances

# The backend under test, isolated so it can be re-pointed in one line.
BACKEND = exact_geodesic_distances

# Dimensionless. Applied to each fixture's stated conditioning scale to obtain an
# absolute tolerance in mm. Derivation: the closed forms below are exact on the
# polyhedron, so the whole residual is float64 arithmetic. Measured against
# Kirsanov MMP on aligned frusta, the relative residual is 1.1e-16 at 112
# vertices and 5.7e-16 at 14 016 (1.6 ulp of the fixture scale), growing as
# n_vert^0.33 -- so ~10 ulp is a fair ceiling at 1e6 vertices. 1e-11 is ~4.5e4
# ulp: four orders of headroom for a different exact algorithm's rounding (CGAL
# runs Xin-Wang, not MMP), while still eight orders below the smallest
# fixture-level error mode this file rejects (source sampling at h/2 ~ 0.4 mm)
# and nine below a graph-metrication imposter (>= 4.9 %).
MMP_ARITHMETIC_RTOL = 1e-11

# mm. Distance reported at a seeded vertex. The backend documents exactly 0.0;
# this admits one ulp of a 100 mm fixture rather than pinning bit equality.
SOURCE_DISTANCE_ATOL_MM = 1e-13

# Dimensionless, relative. Minimum median excess of edge-graph Dijkstra over the
# closed form that a fixture must exhibit to count as discriminating. Measured
# 4.9 % (jittered plate, 1 source) to 12.7 % (prism, 2 rim sources); pinned at
# 2 % for ~2.5x headroom against mesh-density changes.
GRAPH_IMPOSTER_MIN_MEDIAN_EXCESS = 0.02

# Dimensionless, relative. Ceiling on the same statistic for the boundary-aligned
# full-rim fixtures, whose geodesics *are* edge chains: measured exactly 0.000 %.
# Pinned so the negative result stays visible instead of being assumed.
GRAPH_ALIGNED_MAX_MEDIAN_EXCESS = 1e-9

# Multiples of the mean edge length. The relative-excess statistic is taken only
# over vertices at least this far from a source; nearer than a few edges the
# graph and continuous paths coincide and the ratio is dominated by quantisation.
GRAPH_EXCESS_MIN_DISTANCE_EDGES = 3.0

# mm. Minimum by which the unrolled-sector chord must understate the true
# frustum geodesic inside the hole-crossing regime, on the pinned 48x16 fixture.
# Measured maximum 0.509 mm; pinned at 0.05 mm for 10x headroom.
CONE_HOLE_CROSSING_MIN_DEVIATION_MM = 0.05

# mm. Slack allowed on the one-sided claim that the unrolled chord never exceeds
# the true frustum geodesic. Measured worst violation -6.7e-14 mm, i.e. rounding.
CONE_LOWER_BOUND_SLACK_MM = 1e-12

# Fraction of the grid spacing by which interior plate vertices are displaced to
# destroy row/column alignment. Below 0.5 the triangulation stays valid.
PLATE_JITTER_FRACTION = 0.35


# --------------------------------------------------------------------------- #
# mesh builders (numpy only)
# --------------------------------------------------------------------------- #


def revolved_strip(rho0, z0, rho1, z1, n_theta, n_t, stagger=0.0):
    """Build the surface swept by revolving a straight generator about +z.

    Covers the whole developable family in one builder: equal radii give an open
    cylinder, equal heights a flat annulus, anything else a cone frustum.

    Args:
        rho0: Radius at the first rim (mm).
        z0: Height of the first rim (mm).
        rho1: Radius at the second rim (mm).
        z1: Height of the second rim (mm).
        n_theta: Number of vertices around the circumference.
        n_t: Number of quad rows along the generator.
        stagger: Fraction of the circumferential step by which ring ``j`` is
            rotated, as ``j * stagger``. Zero keeps the generators straight and
            edge-aligned, which the closed form requires.

    Returns:
        Tuple of vertices ``(n, 3)``, triangles ``(m, 3)``, rim source indices,
        per-vertex generator arc length ``t``, and the generator length ``L``.
    """
    length = float(np.hypot(rho1 - rho0, z1 - z0))
    t = np.linspace(0.0, length, n_t + 1)
    frac = t / length
    rho = rho0 + frac * (rho1 - rho0)
    z = z0 + frac * (z1 - z0)
    dtheta = 2.0 * np.pi / n_theta
    ring = np.arange(n_theta)

    vertices = np.empty(((n_t + 1) * n_theta, 3), dtype=np.float64)
    for j in range(n_t + 1):
        theta = (ring + j * stagger) * dtheta
        block = slice(j * n_theta, (j + 1) * n_theta)
        vertices[block, 0] = rho[j] * np.cos(theta)
        vertices[block, 1] = rho[j] * np.sin(theta)
        vertices[block, 2] = z[j]

    faces = []
    for j in range(n_t):
        for k in range(n_theta):
            a = j * n_theta + k
            b = j * n_theta + (k + 1) % n_theta
            c = (j + 1) * n_theta + (k + 1) % n_theta
            d = (j + 1) * n_theta + k
            faces.append((a, b, c))
            faces.append((a, c, d))

    sources = np.concatenate([np.arange(n_theta), np.arange(n_t * n_theta, (n_t + 1) * n_theta)]).astype(np.int32)
    return (
        vertices,
        np.asarray(faces, dtype=np.int32),
        sources,
        np.repeat(t, n_theta),
        length,
    )


def cone_fan(rho, dz, n_rings, n_theta):
    """Build a cone or disc as a fan from a single apex vertex.

    Unlike :func:`revolved_strip` this puts a genuine curvature singularity --
    an apex with angle defect ``2*pi - Theta`` -- inside the domain, which is
    where an MMP-style solver has to split windows rather than propagate them.

    Args:
        rho: Rim radius (mm).
        dz: Apex-to-rim height (mm); zero gives a flat disc.
        n_rings: Number of rings between apex and rim.
        n_theta: Number of vertices per ring.

    Returns:
        Tuple of vertices ``(n, 3)``, triangles ``(m, 3)``, rim source indices,
        per-vertex slant distance from the apex, and the apex-to-rim slant
        length ``L``.
    """
    length = float(np.hypot(rho, dz))
    vertices = [(0.0, 0.0, 0.0)]
    slant = [0.0]
    for j in range(1, n_rings + 1):
        frac = j / n_rings
        for k in range(n_theta):
            theta = 2.0 * np.pi * k / n_theta
            vertices.append((frac * rho * np.cos(theta), frac * rho * np.sin(theta), frac * dz))
            slant.append(frac * length)

    faces = [(0, 1 + k, 1 + (k + 1) % n_theta) for k in range(n_theta)]
    for j in range(1, n_rings):
        base0 = 1 + (j - 1) * n_theta
        base1 = 1 + j * n_theta
        for k in range(n_theta):
            a = base0 + k
            b = base0 + (k + 1) % n_theta
            c = base1 + (k + 1) % n_theta
            d = base1 + k
            faces.append((a, b, c))
            faces.append((a, c, d))

    vertices = np.asarray(vertices, dtype=np.float64)
    sources = np.arange(1 + (n_rings - 1) * n_theta, vertices.shape[0]).astype(np.int32)
    return (
        vertices,
        np.asarray(faces, dtype=np.int32),
        sources,
        np.asarray(slant, dtype=np.float64),
        length,
    )


def flat_plate(width, height, nx, ny, jitter=0.0, seed=0):
    """Build a rectangular plate in the plane ``z = 0``.

    Boundary vertices always stay on the rectangle, so the domain -- and its
    convexity, on which the euclidean closed form rests -- is independent of the
    jitter applied to interior vertices.

    Args:
        width: Plate extent along x (mm).
        height: Plate extent along y (mm).
        nx: Number of cells along x.
        ny: Number of cells along y.
        jitter: Interior displacement as a fraction of the cell size.
        seed: Seed for the jitter, so fixtures stay deterministic.

    Returns:
        Tuple of vertices ``(n, 3)``, triangles ``(m, 3)``, and the boundary
        vertex indices.
    """
    xs = np.linspace(0.0, width, nx + 1)
    ys = np.linspace(0.0, height, ny + 1)
    grid_x, grid_y = np.meshgrid(xs, ys, indexing="ij")
    vertices = np.stack([grid_x.ravel(), grid_y.ravel(), np.zeros(grid_x.size)], axis=1)
    index = np.arange(vertices.shape[0]).reshape(nx + 1, ny + 1)

    if jitter > 0.0:
        rng = np.random.default_rng(seed)
        interior = index[1:-1, 1:-1].ravel()
        vertices[interior, 0] += rng.uniform(-jitter * width / nx, jitter * width / nx, interior.size)
        vertices[interior, 1] += rng.uniform(-jitter * height / ny, jitter * height / ny, interior.size)

    faces = []
    for a in range(nx):
        for b in range(ny):
            v00, v10 = index[a, b], index[a + 1, b]
            v11, v01 = index[a + 1, b + 1], index[a, b + 1]
            # Alternating diagonals keep the triangulation from biasing one
            # direction, which a metrication-based imposter would exploit.
            if (a + b) % 2 == 0:
                faces.append((v00, v10, v11))
                faces.append((v00, v11, v01))
            else:
                faces.append((v00, v10, v01))
                faces.append((v10, v11, v01))

    boundary = np.unique(np.concatenate([index[0, :], index[-1, :], index[:, 0], index[:, -1]])).astype(np.int32)
    return vertices, np.asarray(faces, dtype=np.int32), boundary


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def distances(vertices, faces, sources):
    """Call the backend under test with plain-python source indices.

    Args:
        vertices: Vertex array ``(n, 3)``.
        faces: Triangle array ``(m, 3)``.
        sources: Source vertex indices.

    Returns:
        Per-vertex geodesic distance as a float64 array ``(n,)``.
    """
    result = BACKEND((vertices, faces), [int(i) for i in np.asarray(sources).ravel()])
    return np.asarray(result, dtype=np.float64).ravel()


def assert_matches(actual, expected, scale, label):
    """Assert a field matches its closed form within the arithmetic tolerance.

    Args:
        actual: Distances from the backend under test (mm).
        expected: Closed-form distances (mm).
        scale: The fixture's conditioning scale (mm) -- the largest length the
            reference formula's arithmetic passes through.
        label: Fixture name, reported on failure.
    """
    error = np.abs(np.asarray(actual) - np.asarray(expected))
    atol = MMP_ARITHMETIC_RTOL * scale
    worst = int(np.argmax(error))
    assert error.max() <= atol, (
        f"{label}: max |backend - closed form| = {error.max():.3e} mm exceeds "
        f"{atol:.3e} mm (rtol {MMP_ARITHMETIC_RTOL:g} x scale {scale:.4f} mm); "
        f"worst at vertex {worst}: {actual[worst]:.12f} vs {expected[worst]:.12f}"
    )


def euclidean_to_nearest_source(vertices, sources):
    """Euclidean distance from every vertex to its nearest source vertex.

    On a flat convex domain this *is* the geodesic distance.

    Args:
        vertices: Vertex array ``(n, 3)``.
        sources: Source vertex indices.

    Returns:
        Per-vertex distance ``(n,)`` in mm.
    """
    seeds = vertices[np.asarray(sources)]
    return np.linalg.norm(vertices[:, None, :] - seeds[None, :, :], axis=2).min(axis=1)


def mean_edge_length(vertices, faces):
    """Mean length of the mesh edges, used to scale distance floors.

    Args:
        vertices: Vertex array ``(n, 3)``.
        faces: Triangle array ``(m, 3)``.

    Returns:
        Mean edge length in mm.
    """
    lengths = [np.linalg.norm(vertices[f[i]] - vertices[f[(i + 1) % 3]]) for f in faces for i in range(3)]
    return float(np.mean(lengths))


def edge_graph_distances(vertices, faces, sources):
    """Dijkstra over the mesh edge graph -- the graph shortest-path imposter.

    Present only so the fixtures can prove they discriminate: a solver that
    walks edges instead of unfolding faces must fail them.

    Args:
        vertices: Vertex array ``(n, 3)``.
        faces: Triangle array ``(m, 3)``.
        sources: Source vertex indices.

    Returns:
        Per-vertex edge-graph distance ``(n,)`` in mm.
    """
    adjacency = {}
    for f in faces:
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            weight = float(np.linalg.norm(vertices[a] - vertices[b]))
            adjacency.setdefault(int(a), []).append((int(b), weight))
            adjacency.setdefault(int(b), []).append((int(a), weight))

    best = np.full(vertices.shape[0], np.inf)
    queue = []
    for s in np.asarray(sources).ravel():
        best[int(s)] = 0.0
        heapq.heappush(queue, (0.0, int(s)))
    while queue:
        cost, node = heapq.heappop(queue)
        if cost > best[node]:
            continue
        for neighbour, weight in adjacency.get(node, ()):
            candidate = cost + weight
            if candidate < best[neighbour]:
                best[neighbour] = candidate
                heapq.heappush(queue, (candidate, neighbour))
    return best


def graph_median_excess(vertices, faces, sources, reference):
    """Median relative excess of the edge-graph field over the closed form.

    Args:
        vertices: Vertex array ``(n, 3)``.
        faces: Triangle array ``(m, 3)``.
        sources: Source vertex indices.
        reference: Closed-form distances ``(n,)`` in mm.

    Returns:
        Median of ``(graph - reference) / reference`` over vertices far enough
        from a source for the ratio to be meaningful.
    """
    graph = edge_graph_distances(vertices, faces, sources)
    floor = GRAPH_EXCESS_MIN_DISTANCE_EDGES * mean_edge_length(vertices, faces)
    far = reference >= floor
    assert far.any(), "fixture has no vertex far enough from a source to compare"
    return float(np.median((graph[far] - reference[far]) / reference[far]))


def rotated(vertices):
    """Apply a fixed rigid motion, under which intrinsic distance is invariant.

    Args:
        vertices: Vertex array ``(n, 3)``.

    Returns:
        Transformed vertex array ``(n, 3)``.
    """
    axis = np.array([1.0, -2.0, 3.0])
    axis = axis / np.linalg.norm(axis)
    angle = 0.7
    cross = np.array(
        [
            [0.0, -axis[2], axis[1]],
            [axis[2], 0.0, -axis[0]],
            [-axis[1], axis[0], 0.0],
        ]
    )
    rotation = np.eye(3) * np.cos(angle) + np.sin(angle) * cross + (1.0 - np.cos(angle)) * np.outer(axis, axis)
    return vertices @ rotation.T + np.array([37.0, -11.0, 5.0])


# --------------------------------------------------------------------------- #
# the developable family: d = min(t, L - t) from both rims
# --------------------------------------------------------------------------- #

REVOLVED_FIXTURES = {
    "open_cylinder": (10.0, 0.0, 10.0, 40.0),
    "cone_frustum": (6.0, 0.0, 14.0, 30.0),
    "shallow_frustum": (4.0, 0.0, 20.0, 6.0),
    "flat_annulus": (5.0, 0.0, 18.0, 0.0),
    "steep_frustum": (2.0, 0.0, 20.0, 40.0),
}


@pytest.mark.parametrize("name", sorted(REVOLVED_FIXTURES))
@pytest.mark.parametrize("resolution", [(24, 10), (64, 30)])
def test_revolved_generator_full_rim_matches_closed_form(name, resolution):
    """Distance from both rims is the generator arc length to the nearer one.

    One statement covers the cylinder (axial), the flat annulus (radial) and the
    cone frustum (slant), because all three are the same developable surface up
    to the generator's inclination.
    """
    n_theta, n_t = resolution
    vertices, faces, sources, t, length = revolved_strip(*REVOLVED_FIXTURES[name], n_theta, n_t)
    assert_matches(
        distances(vertices, faces, sources),
        np.minimum(t, length - t),
        length,
        f"{name} {n_theta}x{n_t}",
    )


def test_revolved_generator_closed_form_is_invariant_under_rigid_motion():
    """Geodesic distance is intrinsic, so placing the frustum elsewhere is free."""
    vertices, faces, sources, t, length = revolved_strip(6.0, 0.0, 14.0, 30.0, 48, 20)
    assert_matches(
        distances(rotated(vertices), faces, sources),
        np.minimum(t, length - t),
        length,
        "frustum under rigid motion",
    )


@pytest.mark.parametrize(
    "rho, dz",
    [(20.0, 0.0), (20.0, 15.0), (8.0, 40.0)],
    ids=["flat_disc", "blunt_cone", "sharp_cone"],
)
def test_cone_fan_with_apex_matches_slant_distance(rho, dz):
    """The apex's angle defect does not perturb the rim-distance closed form.

    ``sharp_cone`` carries a defect of 5.05 rad, so this exercises window
    splitting at a cone point rather than plain propagation.
    """
    vertices, faces, sources, slant, length = cone_fan(rho, dz, 12, 48)
    assert_matches(
        distances(vertices, faces, sources),
        length - slant,
        length,
        f"cone fan rho={rho} dz={dz}",
    )


# --------------------------------------------------------------------------- #
# flat convex plate: d = min_s ||v - s||
# --------------------------------------------------------------------------- #


def test_flat_plate_full_boundary_matches_distance_to_the_boundary_curve():
    """On a boundary-aligned grid, vertex sources reproduce the continuous form.

    Every interior vertex shares a row and a column with a boundary vertex, so
    the nearest source sits exactly on the perpendicular foot and the vertex
    source-sampling term is zero rather than small.
    """
    width, height = 40.0, 30.0
    vertices, faces, boundary = flat_plate(width, height, 24, 18)
    x, y = vertices[:, 0], vertices[:, 1]
    assert_matches(
        distances(vertices, faces, boundary),
        np.minimum.reduce([x, width - x, y, height - y]),
        float(np.hypot(width, height)),
        "plate, full boundary",
    )


@pytest.mark.parametrize("jitter", [0.0, PLATE_JITTER_FRACTION], ids=["grid", "jittered"])
@pytest.mark.parametrize("n_sources", [1, 3, None], ids=["one", "three", "all"])
def test_flat_plate_matches_euclidean_distance_to_nearest_source(jitter, n_sources):
    """A flat convex polygon carries the euclidean metric, whatever the mesh.

    Sparse sources make the geodesics cross triangles obliquely instead of
    running along edges, which is what turns this from a plausibility check into
    a test only an unfolding solver can pass.
    """
    width, height = 40.0, 30.0
    vertices, faces, boundary = flat_plate(width, height, 24, 18, jitter=jitter, seed=11)
    if n_sources is None:
        sources = boundary
    else:
        sources = boundary[:: max(1, len(boundary) // n_sources)][:n_sources]
    assert_matches(
        distances(vertices, faces, sources),
        euclidean_to_nearest_source(vertices, sources),
        float(np.hypot(width, height)),
        f"plate jitter={jitter} sources={len(sources)}",
    )


# --------------------------------------------------------------------------- #
# open cylinder, sparse rim sources: the unrolled prism, with wrap-around
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("n_sources", [1, 2, 5], ids=["one", "two", "five"])
def test_open_cylinder_sparse_sources_match_the_unrolled_prism(n_sources):
    """The prism is intrinsically flat, so it unrolls to a rectangle exactly.

    The unrolled width is ``n_theta * chord``; using ``2 * pi * R`` instead is
    wrong by 0.022 mm here, which this tolerance rejects by eleven orders of
    magnitude.
    """
    radius, length, n_theta, n_t = 10.0, 40.0, 48, 20
    vertices, faces, rim, t, _ = revolved_strip(radius, 0.0, radius, length, n_theta, n_t)
    chord = 2.0 * radius * np.sin(np.pi / n_theta)
    width = n_theta * chord
    circumferential = np.tile(np.arange(n_theta), n_t + 1) * chord

    sources = rim[:: max(1, len(rim) // n_sources)][:n_sources]
    gap = np.abs(circumferential[:, None] - circumferential[None, sources])
    gap = np.minimum(gap, width - gap)
    axial = np.abs(t[:, None] - t[None, sources])
    reference = np.sqrt(gap**2 + axial**2).min(axis=1)

    assert_matches(
        distances(vertices, faces, sources),
        reference,
        float(np.hypot(width, length)),
        f"prism, {n_sources} rim sources",
    )


# --------------------------------------------------------------------------- #
# the rejected formula, pinned as a negative result
# --------------------------------------------------------------------------- #


def _frustum_sector_reference(rho0, rho1, dz, n_theta, n_t):
    """Unrolled-sector chord distance on a frustum, with its validity mask.

    Args:
        rho0: Radius at the near rim (mm).
        rho1: Radius at the far rim (mm).
        dz: Height between rims (mm).
        n_theta: Vertices around the circumference.
        n_t: Quad rows along the generator.

    Returns:
        Tuple of vertices, faces, the single rim source, the chord distances,
        and a boolean mask that is True where the chord stays outside the
        sector's hole and the formula is therefore the geodesic.
    """
    vertices, faces, rim, t, length = revolved_strip(rho0, 0.0, rho1, dz, n_theta, n_t)
    sin_alpha = (rho1 - rho0) / length
    inner_slant = rho0 / sin_alpha
    slant = inner_slant + t
    facet_angle = 2.0 * np.arcsin(sin_alpha * np.sin(np.pi / n_theta))
    total_angle = n_theta * facet_angle
    azimuth = np.tile(np.arange(n_theta), n_t + 1) * facet_angle

    sources = rim[:1]
    delta = np.abs(azimuth[:, None] - azimuth[None, sources])
    delta = np.minimum(delta, total_angle - delta)
    here, there = slant[:, None], slant[None, sources]
    chord_sq = here**2 + there**2 - 2.0 * here * there * np.cos(delta)
    chord = np.sqrt(np.maximum(chord_sq, 0.0))
    # Radius of closest approach of the chord to the apex, when the foot of the
    # perpendicular falls between the endpoints; otherwise an endpoint is closest.
    foot_between = (here**2 + chord_sq >= there**2) & (there**2 + chord_sq >= here**2)
    closest = np.where(
        foot_between & (chord > 0.0),
        here * there * np.sin(delta) / np.where(chord > 0.0, chord, 1.0),
        np.minimum(here, there),
    )
    nearest = chord.argmin(axis=1)
    rows = np.arange(chord.shape[0])
    return (
        vertices,
        faces,
        sources,
        chord[rows, nearest],
        closest[rows, nearest] >= inner_slant,
        slant.max(),
    )


def test_cone_sector_form_holds_outside_the_hole_crossing_regime():
    """Where the unrolled chord clears the inner rim it is the exact geodesic."""
    vertices, faces, sources, chord, valid, scale = _frustum_sector_reference(6.0, 14.0, 30.0, 48, 16)
    assert valid.sum() > 0, "fixture degenerated: nothing outside the hole regime"
    field = distances(vertices, faces, sources)
    assert_matches(field[valid], chord[valid], scale, "frustum sector, valid regime")


def test_cone_sector_form_fails_inside_the_hole_crossing_regime():
    """Inside it the chord is only a lower bound -- which is why it is not a gate.

    Pinned as a negative result: the sector form must not be promoted to an
    unconditional frustum oracle, because the true path bends around the inner
    rim and is measurably longer.
    """
    vertices, faces, sources, chord, valid, _ = _frustum_sector_reference(6.0, 14.0, 30.0, 48, 16)
    crossing = ~valid
    assert crossing.sum() > 0, "fixture degenerated: nothing inside the hole regime"
    deviation = distances(vertices, faces, sources)[crossing] - chord[crossing]
    assert deviation.min() >= -CONE_LOWER_BOUND_SLACK_MM, f"the unrolled chord is meant to be a lower bound, but the backend fell {-deviation.min():.3e} mm below it"
    assert deviation.max() >= CONE_HOLE_CROSSING_MIN_DEVIATION_MM, (
        "the hole-crossing regime is supposed to be materially wrong; it "
        f"deviates by only {deviation.max():.3e} mm, so this fixture no longer "
        "demonstrates why the sector form is rejected"
    )


# --------------------------------------------------------------------------- #
# fixture quality
# --------------------------------------------------------------------------- #


def test_seeded_vertices_report_zero_distance():
    """Every source is at distance zero from itself, on all three surface kinds."""
    for vertices, faces, sources in (
        revolved_strip(6.0, 0.0, 14.0, 30.0, 32, 12)[:3],
        cone_fan(20.0, 15.0, 8, 32)[:3],
        flat_plate(40.0, 30.0, 16, 12)[:3],
    ):
        field = distances(vertices, faces, sources)
        assert np.abs(field[np.asarray(sources)]).max() <= SOURCE_DISTANCE_ATOL_MM
        assert np.all(field >= 0.0)
        assert np.all(np.isfinite(field))


def test_fixtures_discriminate_against_graph_shortest_paths():
    """The sparse and jittered fixtures reject an edge-walking solver.

    Without this, a Dijkstra-over-edges implementation would pass the aligned
    half of this file unchanged.
    """
    plate_v, plate_f, plate_b = flat_plate(40.0, 30.0, 24, 18, jitter=PLATE_JITTER_FRACTION, seed=11)
    corner = plate_b[:1]
    excess = graph_median_excess(plate_v, plate_f, corner, euclidean_to_nearest_source(plate_v, corner))
    assert excess >= GRAPH_IMPOSTER_MIN_MEDIAN_EXCESS, f"jittered plate no longer discriminates: graph excess {excess:.4%}"

    radius, length, n_theta, n_t = 10.0, 40.0, 48, 20
    prism_v, prism_f, rim, t, _ = revolved_strip(radius, 0.0, radius, length, n_theta, n_t)
    chord = 2.0 * radius * np.sin(np.pi / n_theta)
    width = n_theta * chord
    circumferential = np.tile(np.arange(n_theta), n_t + 1) * chord
    sources = rim[:2]
    gap = np.abs(circumferential[:, None] - circumferential[None, sources])
    gap = np.minimum(gap, width - gap)
    axial = np.abs(t[:, None] - t[None, sources])
    reference = np.sqrt(gap**2 + axial**2).min(axis=1)
    excess = graph_median_excess(prism_v, prism_f, sources, reference)
    assert excess >= GRAPH_IMPOSTER_MIN_MEDIAN_EXCESS, f"sparse-source prism no longer discriminates: graph excess {excess:.4%}"


def test_full_rim_fixtures_are_edge_realisable_and_so_insufficient_alone():
    """Pin the known blind spot: full-rim geodesics here *are* edge chains.

    Measured excess is exactly zero, so these fixtures cannot separate an exact
    solver from a graph one. They are kept for their unconditional closed form,
    and :func:`test_fixtures_discriminate_against_graph_shortest_paths` supplies
    the discrimination they lack. Reducing this file to the full-rim half would
    silently remove the correctness content.
    """
    vertices, faces, sources, t, length = revolved_strip(10.0, 0.0, 10.0, 40.0, 32, 16)
    excess = graph_median_excess(vertices, faces, sources, np.minimum(t, length - t))
    assert excess <= GRAPH_ALIGNED_MAX_MEDIAN_EXCESS, (
        f"full-rim cylinder now shows {excess:.4%} graph excess; the blind spot documented here has changed and the note above needs re-measuring"
    )
