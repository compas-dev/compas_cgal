# Critique: Under-utilization of CGAL Geometric Primitives in `toolpath.cpp`

The `_xy` suffix functions are the clearest symptom. The code does **manual 2D analytic geometry in raw doubles** when CGAL provides exact, robust kernel types designed for exactly these operations.

## 1. `tangent_arc_xy` — reinventing `K::Direction_2` / `CGAL::perpendicular()`

**Lines 188–208.** Manually computes the tangent to a circle at a point by normalizing the radial vector and rotating 90°. CGAL's kernel provides:

- `K::Vector_2` with `.perpendicular(CGAL::COUNTERCLOCKWISE)` / `CGAL::CLOCKWISE`
- `K::Direction_2` for unit-direction semantics
- `CGAL::Circle_2<K>` which already knows its center/radius and can be queried

Instead, the code passes `(cx, cy, px, py, clockwise)` as 5 raw doubles and hand-codes the perpendicular rotation. This is exactly what `Vector_2(px-cx, py-cy).perpendicular(orientation)` does, but with exact predicates.

## 2. `reverse_line_xy` / `reverse_arc_xy` — should be `Segment_2::opposite()`

**Lines 211–229.** `reverse_line_xy` is a 4-arg function that swaps two coordinate pairs. CGAL's `Segment_2` has `.opposite()` which returns the reversed segment. If the geometry were represented as `Segment_2` objects rather than `(sx, sy, ex, ey)` tuples, this function wouldn't exist.

## 3. `arc_sweep_abs_xy` — manual atan2 sweep instead of `Circle_2` + `Direction_2`

**Lines 232–270.** Computes the angular sweep between two points on an arc via manual `atan2`/cross-product/dot-product. CGAL's `Circle_2` with `Direction_2` pairs would give angular relationships through kernel predicates. More importantly, `CGAL::orientation()` and `CGAL::angle()` handle the exact-predicate side of these queries.

## 4. `arc_pair_is_full_circle_xy` — 16 parameters

**Lines 273–323.** Takes **16 scalar parameters** to decide if two arcs form a full circle. If arcs were represented as even a lightweight struct holding `Circle_2` + start/end `Point_2` + orientation, this collapses dramatically. CGAL's `Circle_2` already encapsulates center + squared-radius and supports equality comparison with exact predicates.

## 5. `external_tangent_candidates` — reimplementing computational geometry from scratch

**Lines 673–702.** External tangent lines between two circles is a classical CGAL operation. `CGAL::Circle_2` supports tangent line construction. The code manually derives the tangent geometry with delta-radius/angle math that's well-trodden in `CGAL::Circular_kernel_2` or even just with `Line_2` tangent constructions from `Circle_2`.

## 6. `normalize_xy` lambda — should be `K::Vector_2::direction()`

**Lines 568–576.** Repeated throughout. `K::Vector_2` already normalizes via `.direction()`. With exact predicates, you get robustness guarantees for free instead of the `1e-12` epsilon guards sprinkled everywhere.

## 7. `LinkedPrimitive` struct — should use kernel types

**Lines 967–976.** Stores geometry as 12 raw doubles `(sx, sy, sz, ex, ey, ez, cx, cy, cz, radius)`. This is effectively a hand-rolled `Circular_arc_2` or `Segment_2` without any kernel exactness guarantees. A discriminated union of `Segment_2` / `Circular_arc_2` / `Circle_2` would be type-safe and let CGAL handle intersection, containment, and distance queries.

## Root observation

The code uses CGAL only for two things:

1. **`Polygon_2`** + **`create_interior_straight_skeleton_2`** (the MAT computation)
2. **`CGAL::squared_distance`** (point-to-edge distance)

Everything after skeleton extraction drops to raw scalar arithmetic. The entire arc/tangent/sweep/circle-merge machinery is a hand-coded 2D computational geometry library sitting *inside* a CGAL wrapper project. The `Circular_kernel_2`, `Circle_2`, `Circular_arc_2`, `Direction_2`, `Vector_2`, and `Segment_2` types exist specifically to eliminate this kind of code.

## Why this matters beyond aesthetics

The manual epsilon tolerances (`1e-12`, `1e-7`, `1e-9`, `1e-18`) scattered throughout are the real cost. CGAL's exact predicates kernel (`Exact_predicates_inexact_constructions_kernel` — already the chosen kernel `K`) guarantees that orientation tests, incircle tests, and comparisons are *exact* — no epsilon needed. By dropping to raw doubles for geometric decisions, the code loses the very guarantee it imported CGAL to get. The `_xy` functions are doing inexact geometry inside an exact-predicates framework.

The `Circular_kernel_2` (`CGAL::Exact_circular_kernel_2`) is specifically designed for arc/circle operations — tangent computations, arc intersections, sweep angles — and would replace most of the anonymous namespace. It's an algebraic kernel extension that handles the exact representation of circular arcs as first-class objects.
