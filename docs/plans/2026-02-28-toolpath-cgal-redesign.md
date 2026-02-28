# Toolpath C++ Redesign: CGAL Kernel Types — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite `toolpath.cpp` to use CGAL kernel types (`Circle_2`, `Vector_2`, `Segment_2`, `Direction_2`) internally, eliminating ~900 lines of manual 2D geometry and the DP tangent solver.

**Architecture:** Hybrid — CGAL kernel types for all internal geometric computation; matrix serialization only at the Python boundary. Stay on `Epick`. A line is a degenerate arc. One code path, two output formats.

**Tech Stack:** C++20, CGAL 6.0.1 (Epick kernel), nanobind, Eigen, scikit-build-core

---

## Build & Test Commands

```bash
# Rebuild C++ extension after editing toolpath.cpp
pip install --no-build-isolation -ve .

# Run toolpath tests
pytest tests/test_toolpath.py -n auto -v

# Quick check single test
pytest tests/test_toolpath.py::test_name -v

# Format python
ruff check --fix src/compas_cgal/toolpath.py tests/test_toolpath.py && ruff format src/compas_cgal/toolpath.py tests/test_toolpath.py
```

## Key Files

- `src/toolpath.cpp` — the file being rewritten (1439 → ~450 lines)
- `src/toolpath.h` — header (unchanged, same public function signatures)
- `src/compas_cgal/toolpath.py` — Python bindings (unchanged)
- `tests/test_toolpath.py` — existing tests (unchanged, they ARE the contract)
- `src/compas.h` — shared CGAL typedefs (`compas::Kernel`, `compas::RowMatrixXd`)

## Design Reference

See design doc section above this plan for rationale on:
- Why the DP disappears (winding direction carries through kernel types)
- Why `_xy` functions are replaced by `TrochoidArc` methods
- The `TrochoidArc` / `ToolpathPrimitive` type design

---

### Task 1: Verify baseline

Confirm all existing tests pass before touching anything.

**Files:** None modified

**Step 1: Run existing tests**

Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: All 10 tests PASS

**Step 2: Record baseline**

Note the exact test count and any warnings for comparison after rewrite.

---

### Task 2: Write TrochoidArc struct and methods

Add the core type into the anonymous namespace of `toolpath.cpp`, alongside the existing code. Nothing is deleted yet — this is purely additive.

**Files:**
- Modify: `src/toolpath.cpp` — add after line 17 (after the existing typedefs, inside the anonymous namespace)

**Step 1: Add the TrochoidArc struct**

Add this after the existing `constexpr double PI` line, inside the first `namespace { }` block:

```cpp
typedef K::Vector_2 Vector_2;
typedef K::Segment_2 Segment_2;
typedef K::Circle_2 Circle_2;
typedef K::Direction_2 Direction_2;

struct TrochoidArc {
    Circle_2 circle;   // center + squared_radius; zero-radius = line
    Point_2  start;
    Point_2  end;
    bool     clockwise;

    bool is_line() const
    {
        return CGAL::to_double(circle.squared_radius()) < 1e-24;
    }

    Segment_2 as_segment() const
    {
        return Segment_2(start, end);
    }

    Vector_2 start_tangent() const
    {
        if (is_line()) {
            return end - start;
        }
        Vector_2 radial = start - circle.center();
        return radial.perpendicular(clockwise ? CGAL::CLOCKWISE : CGAL::COUNTERCLOCKWISE);
    }

    Vector_2 end_tangent() const
    {
        if (is_line()) {
            return end - start;
        }
        Vector_2 radial = end - circle.center();
        return radial.perpendicular(clockwise ? CGAL::CLOCKWISE : CGAL::COUNTERCLOCKWISE);
    }

    TrochoidArc reversed() const
    {
        return TrochoidArc{circle, end, start, is_line() ? clockwise : !clockwise};
    }

    double sweep() const
    {
        if (is_line()) {
            return 0.0;
        }

        const Point_2& c = circle.center();
        const double ux = CGAL::to_double(start.x() - c.x());
        const double uy = CGAL::to_double(start.y() - c.y());
        const double vx = CGAL::to_double(end.x() - c.x());
        const double vy = CGAL::to_double(end.y() - c.y());

        const double cross = ux * vy - uy * vx;
        const double dot_val = ux * vx + uy * vy;
        double ccw = std::atan2(cross, dot_val);
        if (ccw < 0.0) {
            ccw += 2.0 * PI;
        }
        if (ccw <= 1e-12) {
            return 0.0;
        }
        return clockwise ? 2.0 * PI - ccw : ccw;
    }

    double radius() const
    {
        return std::sqrt(std::max(0.0, CGAL::to_double(circle.squared_radius())));
    }

    bool completes_circle(const TrochoidArc& next, double tol) const
    {
        if (clockwise != next.clockwise) {
            return false;
        }

        const double r0 = radius();
        const double r1 = next.radius();
        const double scale = std::max(1.0, std::max(r0, r1));
        const double tol_sq = tol * tol * scale * scale;

        if (CGAL::to_double(CGAL::squared_distance(circle.center(), next.circle.center())) > tol_sq) {
            return false;
        }
        if (std::abs(r0 - r1) > tol * scale) {
            return false;
        }
        if (CGAL::to_double(CGAL::squared_distance(end, next.start)) > tol_sq) {
            return false;
        }
        if (CGAL::to_double(CGAL::squared_distance(start, next.end)) > tol_sq) {
            return false;
        }
        return std::abs((sweep() + next.sweep()) - 2.0 * PI) <= 1e-5;
    }

    static TrochoidArc make_line(const Point_2& s, const Point_2& e)
    {
        return TrochoidArc{Circle_2(s, 0.0), s, e, false};
    }

    static TrochoidArc make_arc(const Point_2& center, double r, const Point_2& s, const Point_2& e, bool cw)
    {
        return TrochoidArc{Circle_2(center, r * r), s, e, cw};
    }
};
```

**Step 2: Rebuild and verify nothing broke**

Run: `pip install --no-build-isolation -ve .`
Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: All tests PASS (new code is unused, purely additive)

**Step 3: Commit**

```bash
git add src/toolpath.cpp
git commit -m "add TrochoidArc struct with CGAL kernel types"
```

---

### Task 3: Write trochoid_circles and trochoid_chain

Add the two construction functions that replace `trochoid_segment` and the DP solver. Still additive — old code untouched.

**Files:**
- Modify: `src/toolpath.cpp` — add after `TrochoidArc` struct, still inside anonymous namespace

**Step 1: Add trochoid_circles**

```cpp
std::vector<Circle_2>
trochoid_circles(
    const Point_2& p0,
    const Point_2& p1,
    double r0,
    double r1,
    double pitch)
{
    const double length = std::sqrt(std::max(0.0, CGAL::to_double(CGAL::squared_distance(p0, p1))));
    if (length <= 1e-12) {
        return {};
    }

    const int cycles = std::max(2, static_cast<int>(std::ceil(length / std::max(pitch, 1e-12))));

    std::vector<Circle_2> circles;
    circles.reserve(cycles + 1);
    for (int i = 0; i <= cycles; ++i) {
        const double t = static_cast<double>(i) / static_cast<double>(cycles);
        const Point_2 center(
            CGAL::to_double(p0.x()) + t * (CGAL::to_double(p1.x()) - CGAL::to_double(p0.x())),
            CGAL::to_double(p0.y()) + t * (CGAL::to_double(p1.y()) - CGAL::to_double(p0.y())));
        const double radius = std::max(0.0, r0 + t * (r1 - r0));
        circles.emplace_back(center, radius * radius);
    }
    return circles;
}
```

**Step 2: Add external_tangent function**

```cpp
// Compute the two external tangent segments between two circles.
// Returns false if circles are concentric or one contains the other.
bool
external_tangents(
    const Circle_2& c0,
    const Circle_2& c1,
    Segment_2& tangent_a,
    Segment_2& tangent_b)
{
    const Vector_2 d = c1.center() - c0.center();
    const double length_sq = CGAL::to_double(d.squared_length());
    if (length_sq <= 1e-24) {
        return false;
    }

    const double length = std::sqrt(length_sq);
    const double r0 = std::sqrt(std::max(0.0, CGAL::to_double(c0.squared_radius())));
    const double r1 = std::sqrt(std::max(0.0, CGAL::to_double(c1.squared_radius())));

    double delta = r1 - r0;
    if (std::abs(delta) >= length) {
        delta = (delta >= 0.0 ? 1.0 : -1.0) * (length - 1e-9);
    }

    const double ux = CGAL::to_double(d.x()) / length;
    const double uy = CGAL::to_double(d.y()) / length;
    const double vx = -uy;
    const double vy = ux;
    const double m = -delta / length;
    const double h = std::sqrt(std::max(0.0, 1.0 - m * m));

    const double n1x = m * ux + h * vx;
    const double n1y = m * uy + h * vy;
    const double n2x = m * ux - h * vx;
    const double n2y = m * uy - h * vy;

    const double c0x = CGAL::to_double(c0.center().x());
    const double c0y = CGAL::to_double(c0.center().y());
    const double c1x = CGAL::to_double(c1.center().x());
    const double c1y = CGAL::to_double(c1.center().y());

    tangent_a = Segment_2(
        Point_2(c0x + r0 * n1x, c0y + r0 * n1y),
        Point_2(c1x + r1 * n1x, c1y + r1 * n1y));
    tangent_b = Segment_2(
        Point_2(c0x + r0 * n2x, c0y + r0 * n2y),
        Point_2(c1x + r1 * n2x, c1y + r1 * n2y));
    return true;
}
```

**Step 3: Add trochoid_chain**

```cpp
// Build a trochoidal arc chain from a circle sequence.
// Winding direction + edge direction determine tangent side — no DP needed.
std::vector<TrochoidArc>
trochoid_chain(
    const std::vector<Circle_2>& circles,
    const Vector_2& edge_direction,
    bool winding_ccw)
{
    if (circles.size() < 2) {
        return {};
    }

    // Determine the "left" side normal from edge direction.
    // Winding CCW means the trochoid loops to the left of travel;
    // winding CW means it loops to the right.
    const Vector_2 normal = edge_direction.perpendicular(CGAL::COUNTERCLOCKWISE);

    std::vector<TrochoidArc> chain;
    chain.reserve(circles.size() * 2);

    Point_2 prev_tangent_end;
    bool has_prev = false;

    for (std::size_t i = 0; i + 1 < circles.size(); ++i) {
        Segment_2 ta, tb;
        if (!external_tangents(circles[i], circles[i + 1], ta, tb)) {
            continue;
        }

        // Pick the tangent consistent with winding direction.
        // The tangent start lies on circle[i]; check which side of
        // the center-to-center line it's on.
        const Point_2& ci = circles[i].center();
        const auto orient_a = CGAL::orientation(ci, ci + edge_direction, ta.source());
        const auto orient_b = CGAL::orientation(ci, ci + edge_direction, tb.source());

        // CCW winding → tangent point on LEFT of travel direction
        // CW winding → tangent point on RIGHT of travel direction
        const Segment_2& tangent = winding_ccw
            ? (orient_a == CGAL::LEFT_TURN ? ta : tb)
            : (orient_a == CGAL::RIGHT_TURN ? ta : tb);

        // Arc from previous tangent endpoint to current tangent startpoint
        if (has_prev) {
            const double ri = std::sqrt(std::max(0.0, CGAL::to_double(circles[i].squared_radius())));
            if (CGAL::to_double(CGAL::squared_distance(prev_tangent_end, tangent.source())) > 1e-18) {
                chain.push_back(TrochoidArc::make_arc(
                    ci, ri, prev_tangent_end, tangent.source(), !winding_ccw));
            }
        }

        // Tangent line segment
        if (CGAL::to_double(tangent.squared_length()) > 1e-18) {
            chain.push_back(TrochoidArc::make_line(tangent.source(), tangent.target()));
        }

        prev_tangent_end = tangent.target();
        has_prev = true;
    }

    return chain;
}
```

**Step 4: Rebuild and verify nothing broke**

Run: `pip install --no-build-isolation -ve .`
Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: All tests PASS (new code is unused)

**Step 5: Commit**

```bash
git add src/toolpath.cpp
git commit -m "add trochoid_circles, external_tangents, trochoid_chain"
```

---

### Task 4: Add tessellate_chain and rewrite pmp_trochoidal_mat_toolpath

Replace the polyline code path. This is the first functional change — `pmp_trochoidal_mat_toolpath` switches to the new implementation.

**Files:**
- Modify: `src/toolpath.cpp` — add `tessellate_chain`, rewrite `pmp_trochoidal_mat_toolpath`

**Step 1: Add tessellate_chain**

Add after `trochoid_chain`, still in anonymous namespace:

```cpp
std::vector<Point_2>
tessellate_chain(const std::vector<TrochoidArc>& chain, int samples_per_arc)
{
    std::vector<Point_2> points;
    points.reserve(chain.size() * samples_per_arc);

    for (const auto& arc : chain) {
        if (arc.is_line()) {
            points.push_back(arc.start);
        } else {
            const double r = arc.radius();
            const Point_2& c = arc.circle.center();
            const double cx = CGAL::to_double(c.x());
            const double cy = CGAL::to_double(c.y());

            const double sx = CGAL::to_double(arc.start.x()) - cx;
            const double sy = CGAL::to_double(arc.start.y()) - cy;
            const double start_angle = std::atan2(sy, sx);

            const double sw = arc.sweep();
            const double signed_sweep = arc.clockwise ? -sw : sw;

            const int n = std::max(2, samples_per_arc);
            for (int i = 0; i < n; ++i) {
                const double t = static_cast<double>(i) / static_cast<double>(n - 1);
                const double theta = start_angle + signed_sweep * t;
                points.emplace_back(cx + r * std::cos(theta), cy + r * std::sin(theta));
            }
        }
    }

    // Ensure we end at the last arc's endpoint
    if (!chain.empty()) {
        points.push_back(chain.back().end);
    }

    return points;
}
```

**Step 2: Rewrite pmp_trochoidal_mat_toolpath**

Replace the function body (keep the signature identical). The skeleton traversal and edge clipping stay the same; only the geometry generation changes.

The new body uses:
- `trochoid_circles` → `trochoid_chain` → `tessellate_chain` → `points_to_matrix`
- Same MAT edge iteration, same `compute_radius`, same clipping logic

```cpp
// Replace the body of pmp_trochoidal_mat_toolpath starting after the validation checks
// and skeleton creation (keep everything up to and including the skeleton null check).
// Replace the edge iteration loop with:

    const double tool_radius = 0.5 * tool_diameter;
    const double min_centerline_distance = tool_radius + radial_clearance;

    auto compute_radius = [&](double boundary_distance) {
        const double available = mat_scale * std::max(0.0, boundary_distance - tool_radius - radial_clearance);
        if (available <= 0.0) {
            return 0.0;
        }
        double radius = std::min(max_trochoid_radius, available);
        if (min_trochoid_radius > 0.0) {
            radius = std::min(available, std::max(radius, min_trochoid_radius));
        }
        return radius;
    };

    std::vector<compas::RowMatrixXd> toolpaths;
    toolpaths.reserve(static_cast<std::size_t>(max_passes));

    int emitted_paths = 0;
    for (auto edge_iter = skeleton->halfedges_begin(); edge_iter != skeleton->halfedges_end(); ++edge_iter) {
        // ... same halfedge filtering and clipping as current code ...
        // (keep lines 397-438 verbatim — halfedge selection, vertex extraction, clipping)

        // After clipping, compute radii:
        d0 = distance_to_boundary_xy(p0, boundary);
        d1 = distance_to_boundary_xy(p1, boundary);
        const double radius0 = compute_radius(d0);
        const double radius1 = compute_radius(d1);

        // NEW: build arc chain and tessellate
        const Vector_2 edge_dir(p1.x() - p0.x(), p1.y() - p0.y());
        auto circles = trochoid_circles(p0, p1, radius0, radius1, pitch);
        if (circles.size() < 2) {
            continue;
        }

        auto chain = trochoid_chain(circles, edge_dir, true);
        if (chain.empty()) {
            continue;
        }

        auto path_points = tessellate_chain(chain, samples_per_cycle);
        deduplicate_consecutive_points(path_points, 1e-9);
        if (path_points.size() < 2) {
            continue;
        }

        toolpaths.push_back(points_to_matrix(path_points));
        emitted_paths++;
        if (emitted_paths >= max_passes) {
            break;
        }
    }

    return toolpaths;
```

**Step 3: Rebuild and run tests**

Run: `pip install --no-build-isolation -ve .`
Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: `test_trochoidal_mat_toolpath_inside_polygon` and `test_trochoidal_mat_toolpath_maximizes_clearance` PASS.

If any polyline tests fail, the `trochoid_chain` winding logic may need adjustment — debug by comparing output geometry with the old code. The arc chain should produce the same trochoidal shape when tessellated.

**Step 4: Commit**

```bash
git add src/toolpath.cpp
git commit -m "rewrite polyline toolpath to use trochoid_chain"
```

---

### Task 5: Rewrite pmp_trochoidal_mat_toolpath_circular_raw

Replace the 450-line monolith with `trochoid_circles` + `trochoid_chain`. This eliminates the DP solver, `choose_arc_transition`, `external_tangent_candidates` lambda, `TransitionDecision`, `PrimitiveRecord`, `TangentPair`, `Cost` structs, `normalize_xy`, `signed_span`.

**Files:**
- Modify: `src/toolpath.cpp` — rewrite `pmp_trochoidal_mat_toolpath_circular_raw`

**Step 1: Rewrite the function**

Keep the signature. Replace the body after validation + skeleton creation:

```cpp
    // ... keep validation checks (lines 499-519) and skeleton creation ...
    // ... keep compute_radius lambda ...

    std::vector<TrochoidArc> all_primitives;
    std::vector<int> primitive_path_indices;
    int emitted_paths = 0;

    for (auto edge_iter = skeleton->halfedges_begin(); edge_iter != skeleton->halfedges_end(); ++edge_iter) {
        // ... same halfedge filtering and clipping as before ...

        d0 = distance_to_boundary_xy(p0, boundary);
        d1 = distance_to_boundary_xy(p1, boundary);
        const double radius0 = compute_radius(d0);
        const double radius1 = compute_radius(d1);

        const Vector_2 edge_dir(p1.x() - p0.x(), p1.y() - p0.y());
        auto circles = trochoid_circles(p0, p1, radius0, radius1, pitch);
        if (circles.size() < 2) {
            continue;
        }

        auto chain = trochoid_chain(circles, edge_dir, true);

        // Must have at least one arc (not all lines)
        bool has_arc = false;
        for (const auto& arc : chain) {
            if (!arc.is_line()) {
                has_arc = true;
                break;
            }
        }
        if (!has_arc) {
            continue;
        }

        for (const auto& arc : chain) {
            all_primitives.push_back(arc);
            primitive_path_indices.push_back(emitted_paths);
        }
        emitted_paths++;
        if (emitted_paths >= max_passes) {
            break;
        }
    }

    // Serialize to matrices
    const int n = static_cast<int>(all_primitives.size());
    compas::RowMatrixXd meta(n, 3);
    compas::RowMatrixXd starts(n, 3);
    compas::RowMatrixXd ends(n, 3);
    compas::RowMatrixXd centers(n, 3);
    compas::RowMatrixXd radii(n, 1);

    for (int i = 0; i < n; ++i) {
        const auto& arc = all_primitives[i];
        meta(i, 0) = static_cast<double>(primitive_path_indices[i]);
        meta(i, 1) = arc.is_line() ? 0.0 : 1.0;
        meta(i, 2) = arc.clockwise ? 1.0 : 0.0;

        starts(i, 0) = CGAL::to_double(arc.start.x());
        starts(i, 1) = CGAL::to_double(arc.start.y());
        starts(i, 2) = 0.0;
        ends(i, 0) = CGAL::to_double(arc.end.x());
        ends(i, 1) = CGAL::to_double(arc.end.y());
        ends(i, 2) = 0.0;
        centers(i, 0) = CGAL::to_double(arc.circle.center().x());
        centers(i, 1) = CGAL::to_double(arc.circle.center().y());
        centers(i, 2) = 0.0;
        radii(i, 0) = arc.radius();
    }

    return std::make_tuple(meta, starts, ends, centers, radii);
```

**Step 2: Rebuild and run tests**

Run: `pip install --no-build-isolation -ve .`
Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: `test_circular_returns_toolpath_operations`, `test_circular_exit_tangent_alignment` PASS.

**Step 3: Commit**

```bash
git add src/toolpath.cpp
git commit -m "rewrite circular_raw with trochoid_chain, eliminate DP solver"
```

---

### Task 6: Rewrite linking layer with ToolpathPrimitive

Replace `LinkedPrimitive` (12 raw doubles) with `ToolpathPrimitive` wrapping `TrochoidArc`. Rewrite `pmp_trochoidal_mat_toolpath_circular`.

**Files:**
- Modify: `src/toolpath.cpp` — replace second anonymous namespace and `pmp_trochoidal_mat_toolpath_circular`

**Step 1: Replace LinkedPrimitive and helper functions**

Delete the entire second `namespace { }` block (lines 966-1103: `LinkedPrimitive`, `path_length_xy`, `reverse_primitive`, `reverse_path`, `path_start_tangent`, `path_end_tangent`, `merge_circle_pairs`).

Replace with:

```cpp
namespace
{

struct ToolpathPrimitive {
    TrochoidArc arc;
    int path_index;
    int operation;  // 0=cut 1=lead_in 2=lead_out 3=link 4=retract 5=plunge
    double z;
};

double
path_length(const std::vector<TrochoidArc>& path)
{
    double length = 0.0;
    for (const auto& a : path) {
        if (a.is_line()) {
            length += std::sqrt(std::max(0.0, CGAL::to_double(CGAL::squared_distance(a.start, a.end))));
        } else {
            length += a.radius() * a.sweep();
        }
    }
    return length;
}

void
merge_circle_pairs(std::vector<ToolpathPrimitive>& ops, double tol = 1e-6)
{
    if (ops.size() < 2) {
        return;
    }
    std::vector<ToolpathPrimitive> merged;
    merged.reserve(ops.size());
    std::size_t i = 0;
    while (i < ops.size()) {
        if (i + 1 < ops.size() &&
            !ops[i].arc.is_line() && !ops[i + 1].arc.is_line() &&
            ops[i].operation == ops[i + 1].operation &&
            ops[i].path_index == ops[i + 1].path_index &&
            ops[i].arc.completes_circle(ops[i + 1].arc, tol)) {

            // Merge into circle: type 2, start == end
            ToolpathPrimitive circle = ops[i];
            circle.arc.end = circle.arc.start;
            merged.push_back(circle);
            i += 2;
            continue;
        }
        merged.push_back(ops[i]);
        i += 1;
    }
    ops.swap(merged);
}

} // namespace
```

**Step 2: Rewrite pmp_trochoidal_mat_toolpath_circular**

The function parses raw output into per-path arc chains, orders them, adds lead-in/out/links/retract/plunge, and serializes. Replace the body:

```cpp
    // Parse raw output into per-path arc chains
    // ... (same parsing logic as current, but building vector<vector<TrochoidArc>>
    //      instead of vector<vector<LinkedPrimitive>>)

    // Ordering: greedy nearest-neighbor using CGAL::squared_distance
    // Lead-in/out: arc.start_tangent() / arc.end_tangent() for direction
    // Links: TrochoidArc::make_line between paths
    // Retract/plunge: TrochoidArc::make_line vertical moves

    // Serialize ToolpathPrimitive vector to matrices (meta is Nx4 with operation column)
    // For circle-merged arcs: type = 2 (start == end)
    // For lines: type = 0
    // For arcs: type = 1
```

The full rewrite of this function follows the same pattern as the current code but uses `TrochoidArc` methods instead of `tangent_line_xy`, `tangent_arc_xy`, `path_start_tangent`, `path_end_tangent`. The `make_line` static factory handles all degenerate cases.

**Step 3: Rebuild and run tests**

Run: `pip install --no-build-isolation -ve .`
Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: ALL tests PASS including:
- `test_circular_with_leads_and_links`
- `test_circular_with_clearance_z`
- `test_circular_continuity`
- `test_circular_merge_circles`

**Step 4: Commit**

```bash
git add src/toolpath.cpp
git commit -m "rewrite linking layer with ToolpathPrimitive + TrochoidArc"
```

---

### Task 7: Delete dead code and final cleanup

Remove all old `_xy` functions, old structs, and unused code. The first anonymous namespace should now contain only: `TrochoidArc`, `trochoid_circles`, `external_tangents`, `trochoid_chain`, `tessellate_chain`, plus the retained helpers (`data_to_polygon`, `distance_to_boundary_xy`, `polygon_medial_axis_transform_internal`, `deduplicate_consecutive_points`, `points_to_matrix`).

**Files:**
- Modify: `src/toolpath.cpp`

**Step 1: Delete dead functions**

Remove from the first anonymous namespace:
- `tangent_line_xy`
- `tangent_arc_xy`
- `reverse_line_xy`
- `reverse_arc_xy`
- `arc_sweep_abs_xy`
- `arc_pair_is_full_circle_xy`
- `trochoid_segment` (replaced by `trochoid_chain` + `tessellate_chain`)

**Step 2: Delete dead structs**

These should no longer exist after Task 5-6 but verify removal:
- `PrimitiveRecord`
- `TransitionDecision`
- `TangentPair`
- `Cost`
- `LinkedPrimitive`

**Step 3: Delete dead lambdas**

Inside `pmp_trochoidal_mat_toolpath_circular_raw` (if any remain):
- `normalize_xy`
- `signed_span`
- `choose_arc_transition`
- `external_tangent_candidates`

**Step 4: Verify line count**

Run: `wc -l src/toolpath.cpp`
Expected: ~400-500 lines (down from 1439)

**Step 5: Final test run**

Run: `pip install --no-build-isolation -ve .`
Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: ALL 10 tests PASS

**Step 6: Commit**

```bash
git add src/toolpath.cpp
git commit -m "remove dead _xy functions, old structs, DP solver"
```

---

### Task 8: Run example and verify visual output

**Files:**
- Run: `docs/examples/example_toolpath_trochoidal_mat.py`

**Step 1: Run the example script**

Run: `python docs/examples/example_toolpath_trochoidal_mat.py`
Expected: Viewer opens showing trochoidal toolpath on the irregular polygon. Visually verify:
- Arcs are smooth and continuous
- Lead-in/out lines are tangent to arcs
- Links connect paths at clearance height
- No self-intersecting or wildly wrong geometry

**Step 2: Run full test suite one more time**

Run: `pytest tests/test_toolpath.py -n auto -v`
Expected: ALL PASS

**Step 3: Final commit**

```bash
git add -u
git commit -m "toolpath.cpp: rewrite complete, CGAL kernel types throughout"
```
