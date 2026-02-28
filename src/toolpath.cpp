#include "toolpath.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <tuple>
#include <vector>

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef K::Point_2 Point_2;
typedef CGAL::Polygon_2<K> Polygon_2;
typedef CGAL::Straight_skeleton_2<K> Ss;

typedef std::shared_ptr<Ss> SsPtr;

namespace
{
constexpr double PI = 3.14159265358979323846;

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

std::vector<TrochoidArc>
trochoid_chain(
    const std::vector<Circle_2>& circles,
    const Vector_2& edge_direction,
    bool winding_ccw)
{
    if (circles.size() < 2) {
        return {};
    }

    std::vector<TrochoidArc> chain;
    chain.reserve(circles.size() * 2);

    Point_2 prev_tangent_end;
    bool has_prev = false;

    for (std::size_t i = 0; i + 1 < circles.size(); ++i) {
        Segment_2 ta, tb;
        if (!external_tangents(circles[i], circles[i + 1], ta, tb)) {
            continue;
        }

        // Alternate tangent side on consecutive iterations.
        // Even iterations pick one side, odd the other — this places
        // arrival/departure points on opposite sides of each intermediate
        // circle, producing the half-circle arcs that form the trochoid.
        const Point_2& ci = circles[i].center();
        const auto orient_a = CGAL::orientation(ci, ci + edge_direction, ta.source());

        const bool pick_left = ((i % 2 == 0) == winding_ccw);
        const Segment_2& tangent = pick_left
            ? (orient_a == CGAL::LEFT_TURN ? ta : tb)
            : (orient_a == CGAL::RIGHT_TURN ? ta : tb);

        // Arc on intermediate circle: arrival to departure point.
        // Arc winding matches the departure side: LEFT → CW, RIGHT → CCW.
        // This ensures the arc exit tangent aligns with the departing line.
        if (has_prev && prev_tangent_end != tangent.source()) {
            const double ri = std::sqrt(std::max(0.0, CGAL::to_double(circles[i].squared_radius())));
            chain.push_back(TrochoidArc::make_arc(
                ci, ri, prev_tangent_end, tangent.source(), pick_left));
        }

        // Tangent line segment
        if (tangent.source() != tangent.target()) {
            chain.push_back(TrochoidArc::make_line(tangent.source(), tangent.target()));
        }

        prev_tangent_end = tangent.target();
        has_prev = true;
    }

    return chain;
}

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

Polygon_2
data_to_polygon(Eigen::Ref<const compas::RowMatrixXd> vertices)
{
    if (vertices.rows() < 3) {
        throw std::invalid_argument("Expected at least three polygon vertices.");
    }

    Polygon_2 polygon;
    polygon.reserve(vertices.rows());

    for (int i = 0; i < vertices.rows(); ++i) {
        polygon.push_back(Point_2(vertices(i, 0), vertices(i, 1)));
    }

    if (polygon.is_clockwise_oriented()) {
        polygon.reverse_orientation();
    }

    return polygon;
}

double
distance_to_boundary_xy(const Point_2& point, const Polygon_2& boundary)
{
    if (boundary.size() < 2) {
        return 0.0;
    }

    double sq_distance = std::numeric_limits<double>::infinity();
    for (auto edge_iter = boundary.edges_begin(); edge_iter != boundary.edges_end(); ++edge_iter) {
        const double sq = CGAL::to_double(CGAL::squared_distance(point, *edge_iter));
        if (sq < sq_distance) {
            sq_distance = sq;
        }
    }

    return std::sqrt(std::max(0.0, sq_distance));
}

std::tuple<std::vector<Point_2>, std::vector<double>>
polygon_medial_axis_transform_internal(const Polygon_2& polygon)
{
    SsPtr skeleton = CGAL::create_interior_straight_skeleton_2(polygon.vertices_begin(), polygon.vertices_end());
    if (!skeleton) {
        return std::make_tuple(std::vector<Point_2>{}, std::vector<double>{});
    }

    std::vector<Point_2> points;
    std::vector<double> radii;
    points.reserve(skeleton->size_of_vertices());
    radii.reserve(skeleton->size_of_vertices());

    for (auto vertex_iter = skeleton->vertices_begin(); vertex_iter != skeleton->vertices_end(); ++vertex_iter) {
        const auto& point = vertex_iter->point();
        Point_2 point_xy(point.x(), point.y());
        const double radius = distance_to_boundary_xy(point_xy, polygon);

        // Keep only interior MAT samples.
        if (radius > 1e-8) {
            points.push_back(point_xy);
            radii.push_back(radius);
        }
    }

    return std::make_tuple(points, radii);
}

void
deduplicate_consecutive_points(std::vector<Point_2>& points, double tol)
{
    if (points.size() < 2) {
        return;
    }
    const double tol_sq = tol * tol;
    auto last = std::unique(points.begin(), points.end(),
        [tol_sq](const Point_2& a, const Point_2& b) {
            return CGAL::to_double(CGAL::squared_distance(a, b)) <= tol_sq;
        });
    points.erase(last, points.end());
}

compas::RowMatrixXd
points_to_matrix(const std::vector<Point_2>& points)
{
    compas::RowMatrixXd matrix(points.size(), 3);
    for (std::size_t i = 0; i < points.size(); ++i) {
        matrix(i, 0) = points[i].x();
        matrix(i, 1) = points[i].y();
        matrix(i, 2) = 0.0;
    }
    return matrix;
}

} // namespace

std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
pmp_polygon_medial_axis_transform(
    Eigen::Ref<const compas::RowMatrixXd> vertices)
{
    Polygon_2 polygon = data_to_polygon(vertices);
    auto [mat_points, mat_radii] = polygon_medial_axis_transform_internal(polygon);

    compas::RowMatrixXd points_matrix(mat_points.size(), 3);
    compas::RowMatrixXd radii_matrix(mat_radii.size(), 1);

    for (std::size_t i = 0; i < mat_points.size(); ++i) {
        points_matrix(i, 0) = mat_points[i].x();
        points_matrix(i, 1) = mat_points[i].y();
        points_matrix(i, 2) = 0.0;
        radii_matrix(i, 0) = mat_radii[i];
    }

    return std::make_tuple(points_matrix, radii_matrix);
}

std::vector<compas::RowMatrixXd>
pmp_trochoidal_mat_toolpath(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double tool_diameter,
    double stepover,
    double pitch,
    double min_trochoid_radius,
    double max_trochoid_radius,
    double mat_scale,
    double radial_clearance,
    int samples_per_cycle,
    int max_passes)
{
    if (tool_diameter <= 0.0) {
        throw std::invalid_argument("tool_diameter should be positive.");
    }
    if (stepover <= 0.0) {
        throw std::invalid_argument("stepover should be positive.");
    }
    if (pitch <= 0.0) {
        throw std::invalid_argument("pitch should be positive.");
    }
    if (min_trochoid_radius < 0.0) {
        throw std::invalid_argument("min_trochoid_radius should be >= 0.");
    }
    if (max_trochoid_radius < 0.0) {
        throw std::invalid_argument("max_trochoid_radius should be >= 0.");
    }
    if (samples_per_cycle < 4) {
        throw std::invalid_argument("samples_per_cycle should be at least 4.");
    }
    if (max_passes <= 0) {
        throw std::invalid_argument("max_passes should be positive.");
    }

    (void)stepover; // Reserved for API compatibility.

    Polygon_2 boundary = data_to_polygon(vertices);
    SsPtr skeleton = CGAL::create_interior_straight_skeleton_2(boundary.vertices_begin(), boundary.vertices_end());
    if (!skeleton) {
        return {};
    }

    const double tool_radius = 0.5 * tool_diameter;
    const double min_centerline_distance = tool_radius + radial_clearance;

    std::vector<compas::RowMatrixXd> toolpaths;
    toolpaths.reserve(static_cast<std::size_t>(max_passes));

    int emitted_paths = 0;
    for (auto edge_iter = skeleton->halfedges_begin(); edge_iter != skeleton->halfedges_end(); ++edge_iter) {
        const auto halfedge = edge_iter;

        if (!(halfedge->is_bisector() || halfedge->is_inner_bisector())) {
            continue;
        }

        const auto vertex0 = halfedge->vertex();
        const auto vertex1 = halfedge->opposite()->vertex();
        if (&*vertex0 >= &*vertex1) {
            continue;
        }

        Point_2 p0(vertex0->point().x(), vertex0->point().y());
        Point_2 p1(vertex1->point().x(), vertex1->point().y());

        double d0 = distance_to_boundary_xy(p0, boundary);
        double d1 = distance_to_boundary_xy(p1, boundary);

        // Clip edge to the valid cutter-center domain.
        if (d0 < min_centerline_distance && d1 < min_centerline_distance) {
            continue;
        }

        if (d0 < min_centerline_distance || d1 < min_centerline_distance) {
            const double denom = d1 - d0;
            if (std::abs(denom) < 1e-12) {
                continue;
            }
            const double t = (min_centerline_distance - d0) / denom;
            const double clamped_t = std::max(0.0, std::min(1.0, t));
            const Point_2 clip_point(
                p0.x() + clamped_t * (p1.x() - p0.x()),
                p0.y() + clamped_t * (p1.y() - p0.y())
            );

            if (d0 < min_centerline_distance) {
                p0 = clip_point;
            } else {
                p1 = clip_point;
            }
        }

        d0 = distance_to_boundary_xy(p0, boundary);
        d1 = distance_to_boundary_xy(p1, boundary);

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

        const double radius0 = compute_radius(d0);
        const double radius1 = compute_radius(d1);

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
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd>
pmp_trochoidal_mat_toolpath_circular_raw(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double tool_diameter,
    double stepover,
    double pitch,
    double min_trochoid_radius,
    double max_trochoid_radius,
    double mat_scale,
    double radial_clearance,
    int samples_per_cycle,
    int max_passes)
{
    if (tool_diameter <= 0.0) {
        throw std::invalid_argument("tool_diameter should be positive.");
    }
    if (stepover <= 0.0) {
        throw std::invalid_argument("stepover should be positive.");
    }
    if (pitch <= 0.0) {
        throw std::invalid_argument("pitch should be positive.");
    }
    if (min_trochoid_radius < 0.0) {
        throw std::invalid_argument("min_trochoid_radius should be >= 0.");
    }
    if (max_trochoid_radius < 0.0) {
        throw std::invalid_argument("max_trochoid_radius should be >= 0.");
    }
    if (samples_per_cycle < 4) {
        throw std::invalid_argument("samples_per_cycle should be at least 4.");
    }
    if (max_passes <= 0) {
        throw std::invalid_argument("max_passes should be positive.");
    }

    (void)stepover;
    (void)samples_per_cycle;

    Polygon_2 boundary = data_to_polygon(vertices);
    SsPtr skeleton = CGAL::create_interior_straight_skeleton_2(boundary.vertices_begin(), boundary.vertices_end());
    if (!skeleton) {
        return std::make_tuple(compas::RowMatrixXd(0, 3), compas::RowMatrixXd(0, 3), compas::RowMatrixXd(0, 3), compas::RowMatrixXd(0, 3), compas::RowMatrixXd(0, 1));
    }

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

    std::vector<TrochoidArc> all_primitives;
    std::vector<int> primitive_path_indices;
    int emitted_paths = 0;

    for (auto edge_iter = skeleton->halfedges_begin(); edge_iter != skeleton->halfedges_end(); ++edge_iter) {
        const auto halfedge = edge_iter;
        if (!(halfedge->is_bisector() || halfedge->is_inner_bisector())) {
            continue;
        }

        const auto vertex0 = halfedge->vertex();
        const auto vertex1 = halfedge->opposite()->vertex();
        if (&*vertex0 >= &*vertex1) {
            continue;
        }

        Point_2 p0(vertex0->point().x(), vertex0->point().y());
        Point_2 p1(vertex1->point().x(), vertex1->point().y());

        double d0 = distance_to_boundary_xy(p0, boundary);
        double d1 = distance_to_boundary_xy(p1, boundary);

        if (d0 < min_centerline_distance && d1 < min_centerline_distance) {
            continue;
        }

        if (d0 < min_centerline_distance || d1 < min_centerline_distance) {
            const double denom = d1 - d0;
            if (std::abs(denom) < 1e-12) {
                continue;
            }
            const double t = std::max(0.0, std::min(1.0, (min_centerline_distance - d0) / denom));
            const Point_2 clip_point(p0.x() + t * (p1.x() - p0.x()), p0.y() + t * (p1.y() - p0.y()));
            if (d0 < min_centerline_distance) {
                p0 = clip_point;
            } else {
                p1 = clip_point;
            }
        }

        d0 = distance_to_boundary_xy(p0, boundary);
        d1 = distance_to_boundary_xy(p1, boundary);

        // Canonicalize edge direction: narrower end first, tie-break by x then y.
        // This ensures deterministic results regardless of which halfedge is selected.
        if (d0 > d1 + 1e-12 ||
            (std::abs(d0 - d1) <= 1e-12 && (p0.x() > p1.x() + 1e-12 ||
             (std::abs(p0.x() - p1.x()) <= 1e-12 && p0.y() > p1.y() + 1e-12)))) {
            std::swap(p0, p1);
            std::swap(d0, d1);
        }

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
}

// ============================================================================
// Linked circular toolpath with path ordering, leads, links, retract/plunge
// ============================================================================

namespace
{

struct ToolpathPrimitive {
    TrochoidArc arc;
    int path_index;
    int operation;  // 0=cut 1=lead_in 2=lead_out 3=link 4=retract 5=plunge
    double z_start;
    double z_end;
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

            ToolpathPrimitive circle = ops[i];
            circle.arc.end = circle.arc.start;  // circle: start == end
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

std::tuple<compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd>
pmp_trochoidal_mat_toolpath_circular(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double tool_diameter,
    double stepover,
    double pitch,
    double min_trochoid_radius,
    double max_trochoid_radius,
    double mat_scale,
    double radial_clearance,
    int samples_per_cycle,
    int max_passes,
    double lead_in,
    double lead_out,
    bool link_paths,
    bool optimize_order,
    double cut_z,
    double clearance_z,
    bool has_clearance_z,
    bool retract_at_end,
    bool merge_circles)
{
    // Generate raw circular primitives
    auto [raw_meta, raw_starts, raw_ends, raw_centers, raw_radii] =
        pmp_trochoidal_mat_toolpath_circular_raw(
            vertices, tool_diameter, stepover, pitch,
            min_trochoid_radius, max_trochoid_radius,
            mat_scale, radial_clearance, samples_per_cycle, max_passes);

    const int raw_n = static_cast<int>(raw_meta.rows());
    if (raw_n == 0) {
        compas::RowMatrixXd empty_meta(0, 4);
        compas::RowMatrixXd empty3(0, 3);
        compas::RowMatrixXd empty1(0, 1);
        return std::make_tuple(empty_meta, empty3, empty3, empty3, empty1);
    }

    // Parse raw output into per-path lists of TrochoidArc
    int path_count = 0;
    for (int i = 0; i < raw_n; ++i) {
        path_count = std::max(path_count, static_cast<int>(raw_meta(i, 0)) + 1);
    }

    std::vector<std::vector<TrochoidArc>> paths(path_count);
    for (int i = 0; i < raw_n; ++i) {
        int pidx = static_cast<int>(raw_meta(i, 0));
        int ptype = static_cast<int>(raw_meta(i, 1));
        bool cw = raw_meta(i, 2) > 0.5;

        Point_2 s(raw_starts(i, 0), raw_starts(i, 1));
        Point_2 e(raw_ends(i, 0), raw_ends(i, 1));
        Point_2 c(raw_centers(i, 0), raw_centers(i, 1));
        double r = raw_radii(i, 0);

        if (ptype == 0) {
            paths[pidx].push_back(TrochoidArc::make_line(s, e));
        } else {
            paths[pidx].push_back(TrochoidArc::make_arc(c, r, s, e, cw));
        }
    }

    // Remove empty paths
    std::vector<std::vector<TrochoidArc>> nonempty;
    nonempty.reserve(path_count);
    for (auto& p : paths) {
        if (!p.empty()) nonempty.push_back(std::move(p));
    }
    paths.swap(nonempty);
    if (paths.empty()) {
        compas::RowMatrixXd empty_meta(0, 4);
        compas::RowMatrixXd empty3(0, 3);
        compas::RowMatrixXd empty1(0, 1);
        return std::make_tuple(empty_meta, empty3, empty3, empty3, empty1);
    }

    // Greedy nearest-neighbor path ordering
    if (optimize_order && paths.size() > 1) {
        double max_len = -1.0;
        int start_idx = 0;
        for (int i = 0; i < static_cast<int>(paths.size()); ++i) {
            double len = path_length(paths[i]);
            if (len > max_len) { max_len = len; start_idx = i; }
        }

        std::vector<bool> used(paths.size(), false);
        std::vector<std::vector<TrochoidArc>> ordered;
        ordered.reserve(paths.size());
        ordered.push_back(paths[start_idx]);
        used[start_idx] = true;

        for (std::size_t step = 1; step < paths.size(); ++step) {
            const Point_2 cur_end = ordered.back().back().end;
            int best_idx = -1;
            double best_dist = std::numeric_limits<double>::infinity();

            for (int i = 0; i < static_cast<int>(paths.size()); ++i) {
                if (used[i]) continue;
                double dist = CGAL::to_double(CGAL::squared_distance(cur_end, paths[i].front().start));
                if (dist < best_dist) {
                    best_dist = dist; best_idx = i;
                }
            }

            ordered.push_back(paths[best_idx]);
            used[best_idx] = true;
        }
        paths.swap(ordered);
    }

    // Build linked operation stream using ToolpathPrimitive
    const bool use_clearance = has_clearance_z && (clearance_z > cut_z + 1e-12);
    const double safe_z = has_clearance_z ? clearance_z : cut_z;

    std::vector<ToolpathPrimitive> operations;
    operations.reserve(raw_n + paths.size() * 6);

    auto make_tp_line = [](double sx, double sy, double sz, double ex, double ey, double ez, int op, int pidx) {
        ToolpathPrimitive tp;
        tp.arc = TrochoidArc::make_line(Point_2(sx, sy), Point_2(ex, ey));
        tp.path_index = pidx;
        tp.operation = op;
        tp.z_start = sz;
        tp.z_end = ez;
        return tp;
    };

    double cur_x = 0, cur_y = 0, cur_z = 0;
    bool has_current = false;

    for (int pidx = 0; pidx < static_cast<int>(paths.size()); ++pidx) {
        auto& path = paths[pidx];
        if (path.empty()) continue;

        const double path_sx = CGAL::to_double(path.front().start.x());
        const double path_sy = CGAL::to_double(path.front().start.y());
        const double path_ex = CGAL::to_double(path.back().end.x());
        const double path_ey = CGAL::to_double(path.back().end.y());

        // Compute lead-in start point via start tangent
        double lead_in_sx = path_sx, lead_in_sy = path_sy;
        bool has_start_tangent = false;
        {
            const Vector_2 st = path.front().start_tangent();
            const double st_len = std::sqrt(CGAL::to_double(st.squared_length()));
            if (lead_in > 1e-12 && st_len > 1e-12) {
                double start_tx = CGAL::to_double(st.x()) / st_len;
                double start_ty = CGAL::to_double(st.y()) / st_len;
                lead_in_sx = path_sx - lead_in * start_tx;
                lead_in_sy = path_sy - lead_in * start_ty;
                has_start_tangent = true;
            }
        }

        // Connect to this path
        if (!has_current) {
            if (use_clearance) {
                operations.push_back(make_tp_line(lead_in_sx, lead_in_sy, safe_z, lead_in_sx, lead_in_sy, cut_z, 5 /*plunge*/, pidx));
            }
            cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
            has_current = true;
        } else if (link_paths) {
            if (use_clearance) {
                // retract
                operations.push_back(make_tp_line(cur_x, cur_y, cur_z, cur_x, cur_y, safe_z, 4 /*retract*/, pidx));
                cur_z = safe_z;
                // link at clearance
                double ddx = lead_in_sx - cur_x, ddy = lead_in_sy - cur_y;
                if (std::sqrt(ddx * ddx + ddy * ddy) > 1e-9) {
                    operations.push_back(make_tp_line(cur_x, cur_y, safe_z, lead_in_sx, lead_in_sy, safe_z, 3 /*link*/, pidx));
                }
                // plunge
                operations.push_back(make_tp_line(lead_in_sx, lead_in_sy, safe_z, lead_in_sx, lead_in_sy, cut_z, 5 /*plunge*/, pidx));
                cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
            } else {
                double ddx = lead_in_sx - cur_x, ddy = lead_in_sy - cur_y;
                if (std::sqrt(ddx * ddx + ddy * ddy) > 1e-9) {
                    operations.push_back(make_tp_line(cur_x, cur_y, cut_z, lead_in_sx, lead_in_sy, cut_z, 3 /*link*/, pidx));
                    cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
                }
            }
        } else {
            cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
        }

        // Lead-in
        if (lead_in > 1e-12 && has_start_tangent) {
            operations.push_back(make_tp_line(lead_in_sx, lead_in_sy, cut_z, path_sx, path_sy, cut_z, 1 /*lead_in*/, pidx));
            cur_x = path_sx; cur_y = path_sy; cur_z = cut_z;
        }

        // Cut primitives
        for (const auto& arc : path) {
            ToolpathPrimitive tp;
            tp.arc = arc;
            tp.path_index = pidx;
            tp.operation = 0;  // cut
            tp.z_start = cut_z;
            tp.z_end = cut_z;
            operations.push_back(tp);
            cur_x = CGAL::to_double(arc.end.x());
            cur_y = CGAL::to_double(arc.end.y());
            cur_z = cut_z;
        }

        // Lead-out via end tangent
        {
            const Vector_2 et = path.back().end_tangent();
            const double et_len = std::sqrt(CGAL::to_double(et.squared_length()));
            if (lead_out > 1e-12 && et_len > 1e-12) {
                double end_tx = CGAL::to_double(et.x()) / et_len;
                double end_ty = CGAL::to_double(et.y()) / et_len;
                double lo_ex = path_ex + lead_out * end_tx;
                double lo_ey = path_ey + lead_out * end_ty;
                operations.push_back(make_tp_line(path_ex, path_ey, cut_z, lo_ex, lo_ey, cut_z, 2 /*lead_out*/, pidx));
                cur_x = lo_ex; cur_y = lo_ey; cur_z = cut_z;
            }
        }
    }

    // Final retract
    if (use_clearance && retract_at_end && has_current) {
        if (std::abs(cur_z - safe_z) > 1e-9) {
            operations.push_back(make_tp_line(cur_x, cur_y, cur_z, cur_x, cur_y, safe_z, 4 /*retract*/, static_cast<int>(paths.size())));
        }
    }

    // Circle merging
    if (merge_circles) {
        merge_circle_pairs(operations);
    }

    // Serialize to matrices (meta Nx4)
    const int n = static_cast<int>(operations.size());
    compas::RowMatrixXd meta(n, 4);
    compas::RowMatrixXd starts(n, 3);
    compas::RowMatrixXd ends(n, 3);
    compas::RowMatrixXd centers_out(n, 3);
    compas::RowMatrixXd radii_out(n, 1);
    for (int i = 0; i < n; ++i) {
        const auto& op = operations[i];
        bool is_circle = merge_circles && !op.arc.is_line() &&
            op.arc.start == op.arc.end;

        meta(i, 0) = static_cast<double>(op.path_index);
        meta(i, 1) = op.arc.is_line() ? 0.0 : (is_circle ? 2.0 : 1.0);
        meta(i, 2) = op.arc.clockwise ? 1.0 : 0.0;
        meta(i, 3) = static_cast<double>(op.operation);

        starts(i, 0) = CGAL::to_double(op.arc.start.x());
        starts(i, 1) = CGAL::to_double(op.arc.start.y());
        starts(i, 2) = op.z_start;
        ends(i, 0) = CGAL::to_double(op.arc.end.x());
        ends(i, 1) = CGAL::to_double(op.arc.end.y());
        ends(i, 2) = op.z_end;
        centers_out(i, 0) = CGAL::to_double(op.arc.circle.center().x());
        centers_out(i, 1) = CGAL::to_double(op.arc.circle.center().y());
        centers_out(i, 2) = op.z_start;  // center z matches start z
        radii_out(i, 0) = op.arc.radius();
    }

    return std::make_tuple(meta, starts, ends, centers_out, radii_out);
}

NB_MODULE(_toolpath, m)
{
    m.def(
        "polygon_medial_axis_transform",
        &pmp_polygon_medial_axis_transform,
        "Compute MAT samples from polygon interior straight skeleton.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of polygon vertices (Nx3, float64)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "tuple\n"
        "    - MAT points (Mx3, float64)\n"
        "    - MAT radii (Mx1, float64)",
        "vertices"_a);

    m.def(
        "trochoidal_mat_toolpath",
        &pmp_trochoidal_mat_toolpath,
        "Create MAT-constrained trochoidal toolpaths for a polygon pocket.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of polygon vertices (Nx3, float64)\n"
        "tool_diameter : float\n"
        "    Cutter diameter\n"
        "stepover : float\n"
        "    Reserved for API compatibility (currently unused)\n"
        "pitch : float\n"
        "    Trochoid pitch\n"
        "min_trochoid_radius : float\n"
        "    Minimum trochoid radius\n"
        "max_trochoid_radius : float\n"
        "    Maximum trochoid radius\n"
        "mat_scale : float\n"
        "    MAT availability scale factor\n"
        "radial_clearance : float\n"
        "    Clearance from available radius\n"
        "samples_per_cycle : int\n"
        "    Samples per trochoid cycle\n"
        "max_passes : int\n"
        "    Maximum number of emitted MAT-edge toolpaths\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of toolpath polylines (each Kx3, float64)",
        "vertices"_a,
        "tool_diameter"_a,
        "stepover"_a,
        "pitch"_a,
        "min_trochoid_radius"_a,
        "max_trochoid_radius"_a,
        "mat_scale"_a,
        "radial_clearance"_a,
        "samples_per_cycle"_a,
        "max_passes"_a);

    m.def(
        "trochoidal_mat_toolpath_circular",
        &pmp_trochoidal_mat_toolpath_circular,
        "Create linked circular toolpath with path ordering, leads, and links.\n\n"
        "Returns tuple:\n"
        "- meta (Nx4 float): [path_index, type(0=line,1=arc,2=circle), clockwise, operation(0=cut,1=lead_in,2=lead_out,3=link,4=retract,5=plunge)]\n"
        "- start points (Nx3 float)\n"
        "- end points (Nx3 float)\n"
        "- centers (Nx3 float)\n"
        "- radii (Nx1 float)",
        "vertices"_a,
        "tool_diameter"_a,
        "stepover"_a,
        "pitch"_a,
        "min_trochoid_radius"_a,
        "max_trochoid_radius"_a,
        "mat_scale"_a,
        "radial_clearance"_a,
        "samples_per_cycle"_a,
        "max_passes"_a,
        "lead_in"_a = 0.0,
        "lead_out"_a = 0.0,
        "link_paths"_a = true,
        "optimize_order"_a = true,
        "cut_z"_a = 0.0,
        "clearance_z"_a = 0.0,
        "has_clearance_z"_a = false,
        "retract_at_end"_a = true,
        "merge_circles"_a = true);
}
