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

std::vector<Point_2>
trochoid_segment(
    const Point_2& p0,
    const Point_2& p1,
    double radius0,
    double radius1,
    double pitch,
    int samples_per_cycle)
{
    const double dx = p1.x() - p0.x();
    const double dy = p1.y() - p0.y();
    const double length = std::sqrt(std::max(0.0, CGAL::to_double(CGAL::squared_distance(p0, p1))));

    if (length <= 1e-12) {
        return std::vector<Point_2>{p0};
    }

    const double tx = dx / length;
    const double ty = dy / length;
    const double nx = -ty;
    const double ny = tx;

    const int cycles = std::max(1, static_cast<int>(std::ceil(length / std::max(pitch, 1e-12))));
    const int sample_count = std::max(2, cycles * std::max(samples_per_cycle, 4) + 1);

    std::vector<Point_2> points;
    points.reserve(sample_count);

    for (int i = 0; i < sample_count; ++i) {
        const double t = static_cast<double>(i) / static_cast<double>(sample_count - 1);
        const double s = length * t;
        const double theta = 2.0 * PI * cycles * t;
        const double radius = radius0 + (radius1 - radius0) * t;

        // Circle center advances along the medial-axis edge.
        // Radius is interpreted as clearance from centerline to trochoid.
        const double x = s + radius * std::sin(theta);
        const double y = radius * std::cos(theta);

        const double px = p0.x() + x * tx + y * nx;
        const double py = p0.y() + x * ty + y * ny;

        points.push_back(Point_2(px, py));
    }

    return points;
}

void
deduplicate_consecutive_points(std::vector<Point_2>& points, double tol)
{
    if (points.size() < 2) {
        return;
    }

    const double tol_sq = tol * tol;
    std::vector<Point_2> deduplicated;
    deduplicated.reserve(points.size());
    deduplicated.push_back(points.front());

    for (std::size_t i = 1; i < points.size(); ++i) {
        const double sq = CGAL::to_double(CGAL::squared_distance(points[i], deduplicated.back()));
        if (sq > tol_sq) {
            deduplicated.push_back(points[i]);
        }
    }

    points.swap(deduplicated);
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

std::tuple<double, double, bool>
tangent_line_xy(
    double sx,
    double sy,
    double ex,
    double ey)
{
    const double dx = ex - sx;
    const double dy = ey - sy;
    const double norm = std::sqrt(dx * dx + dy * dy);
    if (norm <= 1e-12) {
        return std::make_tuple(0.0, 0.0, false);
    }
    return std::make_tuple(dx / norm, dy / norm, true);
}

std::tuple<double, double, bool>
tangent_arc_xy(
    double cx,
    double cy,
    double px,
    double py,
    bool clockwise)
{
    const double rx = px - cx;
    const double ry = py - cy;
    const double norm = std::sqrt(rx * rx + ry * ry);
    if (norm <= 1e-12) {
        return std::make_tuple(0.0, 0.0, false);
    }

    const double ux = rx / norm;
    const double uy = ry / norm;
    if (clockwise) {
        return std::make_tuple(uy, -ux, true);
    }
    return std::make_tuple(-uy, ux, true);
}

std::tuple<double, double, double, double>
reverse_line_xy(
    double sx,
    double sy,
    double ex,
    double ey)
{
    return std::make_tuple(ex, ey, sx, sy);
}

std::tuple<double, double, double, double, bool>
reverse_arc_xy(
    double sx,
    double sy,
    double ex,
    double ey,
    bool clockwise)
{
    return std::make_tuple(ex, ey, sx, sy, !clockwise);
}

double
arc_sweep_abs_xy(
    double cx,
    double cy,
    double sx,
    double sy,
    double ex,
    double ey,
    bool clockwise)
{
    const double ux = sx - cx;
    const double uy = sy - cy;
    const double vx = ex - cx;
    const double vy = ey - cy;

    const double nu = std::sqrt(ux * ux + uy * uy);
    const double nv = std::sqrt(vx * vx + vy * vy);
    if (nu <= 1e-12 || nv <= 1e-12) {
        return 0.0;
    }

    const double uxn = ux / nu;
    const double uyn = uy / nu;
    const double vxn = vx / nv;
    const double vyn = vy / nv;

    const double cross = uxn * vyn - uyn * vxn;
    const double dot = uxn * vxn + uyn * vyn;
    double ccw = std::atan2(cross, dot);
    if (ccw < 0.0) {
        ccw += 2.0 * PI;
    }
    if (ccw <= 1e-12) {
        return 0.0;
    }
    if (clockwise) {
        return 2.0 * PI - ccw;
    }
    return ccw;
}

bool
arc_pair_is_full_circle_xy(
    double cax,
    double cay,
    double ra,
    double sax,
    double say,
    double eax,
    double eay,
    bool cwa,
    double cbx,
    double cby,
    double rb,
    double sbx,
    double sby,
    double ebx,
    double eby,
    bool cwb,
    double tol)
{
    if (cwa != cwb) {
        return false;
    }

    const double scale = std::max(1.0, std::max(std::abs(ra), std::abs(rb)));
    const double tol_scaled = tol * scale;
    const double tol_sq = tol_scaled * tol_scaled;

    const Point_2 ca(cax, cay);
    const Point_2 cb(cbx, cby);
    const Point_2 a_end(eax, eay);
    const Point_2 b_start(sbx, sby);
    const Point_2 a_start(sax, say);
    const Point_2 b_end(ebx, eby);

    if (CGAL::to_double(CGAL::squared_distance(ca, cb)) > tol_sq) {
        return false;
    }
    if (std::abs(ra - rb) > tol_scaled) {
        return false;
    }
    if (CGAL::to_double(CGAL::squared_distance(a_end, b_start)) > tol_sq) {
        return false;
    }
    if (CGAL::to_double(CGAL::squared_distance(a_start, b_end)) > tol_sq) {
        return false;
    }

    const double sweep_a = arc_sweep_abs_xy(cax, cay, sax, say, eax, eay, cwa);
    const double sweep_b = arc_sweep_abs_xy(cbx, cby, sbx, sby, ebx, eby, cwb);
    return std::abs((sweep_a + sweep_b) - 2.0 * PI) <= 1e-5;
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

        std::vector<Point_2> path_points = trochoid_segment(
            p0,
            p1,
            radius0,
            radius1,
            pitch,
            samples_per_cycle);

        if (path_points.empty()) {
            continue;
        }

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

    struct PrimitiveRecord {
        int path_index;
        int type;  // 0 line, 1 arc
        bool clockwise;
        Point_2 start;
        Point_2 end;
        Point_2 center;
        double radius;
    };

    struct TransitionDecision {
        bool valid;
        bool clockwise;
        double sweep;
        double quality;
        bool degenerate;
    };

    struct TangentPair {
        Point_2 start;
        Point_2 end;
    };

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

    auto normalize_xy = [](double x, double y, double& nx, double& ny) {
        const double norm = std::sqrt(x * x + y * y);
        if (norm <= 1e-12) {
            return false;
        }
        nx = x / norm;
        ny = y / norm;
        return true;
    };

    auto signed_span = [](const Point_2& center, const Point_2& start, const Point_2& end, bool clockwise) {
        const double ux = start.x() - center.x();
        const double uy = start.y() - center.y();
        const double vx = end.x() - center.x();
        const double vy = end.y() - center.y();

        double a0 = std::atan2(uy, ux);
        double a1 = std::atan2(vy, vx);
        if (clockwise && a1 > a0) {
            a1 -= 2.0 * PI;
        }
        if (!clockwise && a1 < a0) {
            a1 += 2.0 * PI;
        }
        return a1 - a0;
    };

    auto choose_arc_transition = [&](const Point_2& center, const Point_2& start, const Point_2& end, double incoming_x, double incoming_y, double outgoing_x, double outgoing_y) {
        constexpr double eps_quality = 1e-9;
        constexpr double eps_sweep = 1e-7;

        struct Candidate {
            bool clockwise;
            double sweep;
            double quality;
        };
        std::vector<Candidate> candidates;
        candidates.reserve(2);

        const double rsx = start.x() - center.x();
        const double rsy = start.y() - center.y();
        const double rex = end.x() - center.x();
        const double rey = end.y() - center.y();

        double rsnx = 0.0, rsny = 0.0, renx = 0.0, reny = 0.0;
        if (!normalize_xy(rsx, rsy, rsnx, rsny) || !normalize_xy(rex, rey, renx, reny)) {
            return TransitionDecision{false, true, 0.0, 0.0, true};
        }

        for (int i = 0; i < 2; ++i) {
            const bool clockwise = i == 0;
            const double tsx = clockwise ? rsny : -rsny;
            const double tsy = clockwise ? -rsnx : rsnx;
            const double tex = clockwise ? reny : -reny;
            const double tey = clockwise ? -renx : renx;
            // For trochoidal motion, entry tangent reversal is expected (dot ≈ -1).
            // Exit tangent alignment determines correct arc direction.
            const double quality = tex * outgoing_x + tey * outgoing_y;
            const double sweep = std::abs(signed_span(center, start, end, clockwise));
            candidates.push_back(Candidate{clockwise, sweep, quality});
        }

        std::vector<Candidate> nondegenerate;
        nondegenerate.reserve(2);
        for (const auto& candidate : candidates) {
            if (candidate.sweep > eps_sweep) {
                nondegenerate.push_back(candidate);
            }
        }

        if (!nondegenerate.empty()) {
            // Among tangent-aligned candidates (quality > 0), prefer larger sweep
            // (full trochoidal loop, not the shortcut arc). If neither is tangent-aligned,
            // fall back to best quality.
            std::sort(nondegenerate.begin(), nondegenerate.end(), [](const Candidate& a, const Candidate& b) {
                const bool a_tangent = a.quality > 0.0;
                const bool b_tangent = b.quality > 0.0;
                if (a_tangent && b_tangent) {
                    return a.sweep > b.sweep;
                }
                if (a_tangent != b_tangent) {
                    return a_tangent;
                }
                return a.quality > b.quality;
            });
            const auto& best = nondegenerate.front();
            return TransitionDecision{true, best.clockwise, best.sweep, best.quality, false};
        }

        std::vector<Candidate> tangent_only;
        tangent_only.reserve(2);
        for (const auto& candidate : candidates) {
            if (candidate.quality > eps_quality) {
                tangent_only.push_back(candidate);
            }
        }
        if (!tangent_only.empty()) {
            std::sort(tangent_only.begin(), tangent_only.end(), [](const Candidate& a, const Candidate& b) {
                return a.quality > b.quality;
            });
            const auto& best = tangent_only.front();
            return TransitionDecision{true, best.clockwise, best.sweep, best.quality, true};
        }

        return TransitionDecision{false, true, 0.0, 0.0, true};
    };

    auto external_tangent_candidates = [&](const Point_2& c0, double r0, const Point_2& c1, double r1, std::array<TangentPair, 2>& out) {
        const double dx = c1.x() - c0.x();
        const double dy = c1.y() - c0.y();
        const double length = std::sqrt(dx * dx + dy * dy);
        if (length <= 1e-12) {
            return false;
        }

        double delta = r1 - r0;
        if (std::abs(delta) >= length) {
            delta = (delta >= 0.0 ? 1.0 : -1.0) * (length - 1e-9);
        }

        const double ux = dx / length;
        const double uy = dy / length;
        const double vx = -uy;
        const double vy = ux;
        const double m = -delta / length;
        const double h2 = std::max(0.0, 1.0 - m * m);
        const double h = std::sqrt(h2);

        const double n1x = m * ux + h * vx;
        const double n1y = m * uy + h * vy;
        const double n2x = m * ux - h * vx;
        const double n2y = m * uy - h * vy;

        out[0] = TangentPair{Point_2(c0.x() + r0 * n1x, c0.y() + r0 * n1y), Point_2(c1.x() + r1 * n1x, c1.y() + r1 * n1y)};
        out[1] = TangentPair{Point_2(c0.x() + r0 * n2x, c0.y() + r0 * n2y), Point_2(c1.x() + r1 * n2x, c1.y() + r1 * n2y)};
        return true;
    };

    std::vector<PrimitiveRecord> primitives;
    primitives.reserve(static_cast<std::size_t>(max_passes) * 32);

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
        const double radius0 = compute_radius(d0);
        const double radius1 = compute_radius(d1);

        const double dx = p1.x() - p0.x();
        const double dy = p1.y() - p0.y();
        const double length = std::sqrt(dx * dx + dy * dy);
        if (length <= 1e-12) {
            continue;
        }

        const double tx = dx / length;
        const double ty = dy / length;
        const double snx = -ty;
        const double sny = tx;

        const int cycles = std::max(2, static_cast<int>(std::ceil(length / std::max(pitch, 1e-12))));
        std::vector<Point_2> centers;
        std::vector<double> radii;
        centers.reserve(cycles + 1);
        radii.reserve(cycles + 1);
        for (int i = 0; i <= cycles; ++i) {
            const double t = static_cast<double>(i) / static_cast<double>(cycles);
            centers.emplace_back(p0.x() + t * (p1.x() - p0.x()), p0.y() + t * (p1.y() - p0.y()));
            const double radius = radius0 + t * (radius1 - radius0);
            radii.push_back(std::max(radius, 0.0));
        }
        if (centers.size() < 2) {
            continue;
        }

        std::vector<std::array<TangentPair, 2>> tangent_candidates(centers.size() - 1);
        bool has_tangents = true;
        for (std::size_t i = 0; i + 1 < centers.size(); ++i) {
            if (!external_tangent_candidates(centers[i], radii[i], centers[i + 1], radii[i + 1], tangent_candidates[i])) {
                has_tangents = false;
                break;
            }
        }
        if (!has_tangents || tangent_candidates.empty()) {
            continue;
        }

        const int pair_count = static_cast<int>(tangent_candidates.size());
        std::vector<int> pair_choices(pair_count, 0);
        std::vector<bool> arc_clockwise(pair_count, true);

        if (pair_count > 1) {
            struct Cost {
                int degenerate_count;
                double sweep_sum;
                bool valid;
            };
            std::vector<std::array<Cost, 2>> dp(pair_count);
            std::vector<std::array<int, 2>> parent(pair_count, std::array<int, 2>{-1, -1});
            std::vector<std::array<bool, 2>> arc_choice(pair_count, std::array<bool, 2>{true, true});
            for (int i = 0; i < pair_count; ++i) {
                dp[i][0] = Cost{0, 0.0, false};
                dp[i][1] = Cost{0, 0.0, false};
            }
            dp[0][0] = Cost{0, 0.0, true};
            dp[0][1] = Cost{0, 0.0, true};

            auto better = [](const Cost& lhs, const Cost& rhs) {
                if (!rhs.valid) {
                    return true;
                }
                if (lhs.degenerate_count != rhs.degenerate_count) {
                    return lhs.degenerate_count < rhs.degenerate_count;
                }
                return lhs.sweep_sum < rhs.sweep_sum;
            };

            for (int i = 1; i < pair_count; ++i) {
                for (int curr = 0; curr < 2; ++curr) {
                    for (int prev = 0; prev < 2; ++prev) {
                        const Cost& prev_cost = dp[i - 1][prev];
                        if (!prev_cost.valid) {
                            continue;
                        }

                        const Point_2 arc_center = centers[i];
                        const Point_2 arc_start = tangent_candidates[i - 1][prev].end;
                        const Point_2 arc_end = tangent_candidates[i][curr].start;

                        const double in_dx = tangent_candidates[i - 1][prev].end.x() - tangent_candidates[i - 1][prev].start.x();
                        const double in_dy = tangent_candidates[i - 1][prev].end.y() - tangent_candidates[i - 1][prev].start.y();
                        const double out_dx = tangent_candidates[i][curr].end.x() - tangent_candidates[i][curr].start.x();
                        const double out_dy = tangent_candidates[i][curr].end.y() - tangent_candidates[i][curr].start.y();
                        double in_x = 0.0, in_y = 0.0, out_x = 0.0, out_y = 0.0;
                        if (!normalize_xy(in_dx, in_dy, in_x, in_y) || !normalize_xy(out_dx, out_dy, out_x, out_y)) {
                            continue;
                        }

                        const TransitionDecision decision = choose_arc_transition(arc_center, arc_start, arc_end, in_x, in_y, out_x, out_y);
                        if (!decision.valid) {
                            continue;
                        }

                        Cost value{
                            prev_cost.degenerate_count + (decision.degenerate ? 1 : 0),
                            prev_cost.sweep_sum + decision.sweep,
                            true,
                        };
                        if (better(value, dp[i][curr])) {
                            dp[i][curr] = value;
                            parent[i][curr] = prev;
                            arc_choice[i][curr] = decision.clockwise;
                        }
                    }
                }
            }

            if (!dp[pair_count - 1][0].valid && !dp[pair_count - 1][1].valid) {
                continue;
            }

            int end_state = 0;
            if (!dp[pair_count - 1][0].valid) {
                end_state = 1;
            } else if (dp[pair_count - 1][1].valid && !((dp[pair_count - 1][0].degenerate_count < dp[pair_count - 1][1].degenerate_count) ||
                                                         (dp[pair_count - 1][0].degenerate_count == dp[pair_count - 1][1].degenerate_count &&
                                                          dp[pair_count - 1][0].sweep_sum < dp[pair_count - 1][1].sweep_sum))) {
                end_state = 1;
            }

            pair_choices[pair_count - 1] = end_state;
            for (int i = pair_count - 1; i > 0; --i) {
                arc_clockwise[i] = arc_choice[i][pair_choices[i]];
                pair_choices[i - 1] = parent[i][pair_choices[i]];
            }
            if (pair_choices[0] < 0) {
                continue;
            }
        } else {
            const double d_left = (tangent_candidates[0][0].start.x() - centers[0].x()) * snx + (tangent_candidates[0][0].start.y() - centers[0].y()) * sny;
            const double d_right = (tangent_candidates[0][1].start.x() - centers[0].x()) * snx + (tangent_candidates[0][1].start.y() - centers[0].y()) * sny;
            pair_choices[0] = d_left >= d_right ? 0 : 1;
        }

        std::vector<TangentPair> tangent_pairs;
        tangent_pairs.reserve(pair_count);
        for (int i = 0; i < pair_count; ++i) {
            tangent_pairs.push_back(tangent_candidates[i][pair_choices[i]]);
        }

        std::vector<PrimitiveRecord> path_primitives;
        path_primitives.reserve(pair_count * 2);

        for (int i = 0; i < pair_count; ++i) {
            const Point_2 line_start = tangent_pairs[i].start;
            const Point_2 line_end = tangent_pairs[i].end;

            if (i > 0) {
                const Point_2 arc_center = centers[i];
                const double arc_radius = radii[i];
                const Point_2 arc_start = tangent_pairs[i - 1].end;
                const Point_2 arc_end = line_start;
                const bool clockwise = arc_clockwise[i];
                const double sweep = std::abs(signed_span(arc_center, arc_start, arc_end, clockwise));
                if (sweep > 1e-7) {
                    path_primitives.push_back(PrimitiveRecord{emitted_paths, 1, clockwise, arc_start, arc_end, arc_center, arc_radius});
                }
            }

            if (CGAL::to_double(CGAL::squared_distance(line_start, line_end)) > 1e-18) {
                path_primitives.push_back(PrimitiveRecord{emitted_paths, 0, false, line_start, line_end, Point_2(0.0, 0.0), 0.0});
            }
        }

        bool has_arc = false;
        for (const auto& primitive : path_primitives) {
            if (primitive.type == 1) {
                has_arc = true;
                break;
            }
        }
        if (!has_arc) {
            continue;
        }

        primitives.insert(primitives.end(), path_primitives.begin(), path_primitives.end());
        emitted_paths++;
        if (emitted_paths >= max_passes) {
            break;
        }
    }

    const int n = static_cast<int>(primitives.size());
    compas::RowMatrixXd meta(n, 3);
    compas::RowMatrixXd starts(n, 3);
    compas::RowMatrixXd ends(n, 3);
    compas::RowMatrixXd centers(n, 3);
    compas::RowMatrixXd radii(n, 1);
    for (int i = 0; i < n; ++i) {
        const auto& primitive = primitives[i];
        meta(i, 0) = static_cast<double>(primitive.path_index);
        meta(i, 1) = static_cast<double>(primitive.type);
        meta(i, 2) = static_cast<double>(primitive.clockwise ? 1 : 0);

        starts(i, 0) = primitive.start.x();
        starts(i, 1) = primitive.start.y();
        starts(i, 2) = 0.0;
        ends(i, 0) = primitive.end.x();
        ends(i, 1) = primitive.end.y();
        ends(i, 2) = 0.0;
        centers(i, 0) = primitive.center.x();
        centers(i, 1) = primitive.center.y();
        centers(i, 2) = 0.0;
        radii(i, 0) = primitive.radius;
    }

    return std::make_tuple(meta, starts, ends, centers, radii);
}

// ============================================================================
// Linked circular toolpath with path ordering, leads, links, retract/plunge
// ============================================================================

namespace
{

struct LinkedPrimitive {
    int path_index;
    int type;       // 0=line, 1=arc, 2=circle
    bool clockwise;
    int operation;  // 0=cut, 1=lead_in, 2=lead_out, 3=link, 4=retract, 5=plunge
    double sx, sy, sz;
    double ex, ey, ez;
    double cx, cy, cz;
    double radius;
};

// Path length for ordering heuristic
double
path_length_xy(const std::vector<LinkedPrimitive>& path)
{
    double length = 0.0;
    for (const auto& p : path) {
        if (p.type == 0) {
            const double dx = p.ex - p.sx;
            const double dy = p.ey - p.sy;
            length += std::sqrt(dx * dx + dy * dy);
        } else if (p.type == 1) {
            length += p.radius * arc_sweep_abs_xy(p.cx, p.cy, p.sx, p.sy, p.ex, p.ey, p.clockwise);
        } else {
            length += 2.0 * PI * p.radius;
        }
    }
    return length;
}

// Reverse a single primitive in-place (swap start/end, flip clockwise for arcs)
LinkedPrimitive
reverse_primitive(const LinkedPrimitive& p)
{
    LinkedPrimitive r = p;
    r.sx = p.ex; r.sy = p.ey; r.sz = p.ez;
    r.ex = p.sx; r.ey = p.sy; r.ez = p.sz;
    if (p.type == 1) {
        r.clockwise = !p.clockwise;
    }
    return r;
}

// Reverse an entire path
std::vector<LinkedPrimitive>
reverse_path(const std::vector<LinkedPrimitive>& path)
{
    std::vector<LinkedPrimitive> reversed;
    reversed.reserve(path.size());
    for (auto it = path.rbegin(); it != path.rend(); ++it) {
        reversed.push_back(reverse_primitive(*it));
    }
    return reversed;
}

// Tangent direction at start of path (unit XY vector)
bool
path_start_tangent(const std::vector<LinkedPrimitive>& path, double& tx, double& ty)
{
    if (path.empty()) return false;
    const auto& p = path.front();
    if (p.type == 0) {
        auto [ltx, lty, valid] = tangent_line_xy(p.sx, p.sy, p.ex, p.ey);
        if (!valid) return false;
        tx = ltx; ty = lty;
        return true;
    }
    if (p.type == 1) {
        auto [atx, aty, valid] = tangent_arc_xy(p.cx, p.cy, p.sx, p.sy, p.clockwise);
        if (!valid) return false;
        tx = atx; ty = aty;
        return true;
    }
    return false;
}

// Tangent direction at end of path (unit XY vector)
bool
path_end_tangent(const std::vector<LinkedPrimitive>& path, double& tx, double& ty)
{
    if (path.empty()) return false;
    const auto& p = path.back();
    if (p.type == 0) {
        auto [ltx, lty, valid] = tangent_line_xy(p.sx, p.sy, p.ex, p.ey);
        if (!valid) return false;
        tx = ltx; ty = lty;
        return true;
    }
    if (p.type == 1) {
        auto [atx, aty, valid] = tangent_arc_xy(p.cx, p.cy, p.ex, p.ey, p.clockwise);
        if (!valid) return false;
        tx = atx; ty = aty;
        return true;
    }
    return false;
}

// Merge consecutive arc pairs that form a full circle
void
merge_circle_pairs(std::vector<LinkedPrimitive>& ops, double tol = 1e-6)
{
    if (ops.size() < 2) return;
    std::vector<LinkedPrimitive> merged;
    merged.reserve(ops.size());
    std::size_t i = 0;
    while (i < ops.size()) {
        if (i + 1 < ops.size() &&
            ops[i].type == 1 && ops[i + 1].type == 1 &&
            ops[i].operation == ops[i + 1].operation &&
            ops[i].path_index == ops[i + 1].path_index) {

            bool is_circle = arc_pair_is_full_circle_xy(
                ops[i].cx, ops[i].cy, ops[i].radius,
                ops[i].sx, ops[i].sy, ops[i].ex, ops[i].ey, ops[i].clockwise,
                ops[i + 1].cx, ops[i + 1].cy, ops[i + 1].radius,
                ops[i + 1].sx, ops[i + 1].sy, ops[i + 1].ex, ops[i + 1].ey, ops[i + 1].clockwise,
                tol);
            if (is_circle) {
                LinkedPrimitive circle = ops[i];
                circle.type = 2;  // circle
                circle.ex = circle.sx;
                circle.ey = circle.sy;
                circle.ez = circle.sz;
                merged.push_back(circle);
                i += 2;
                continue;
            }
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

    // Parse raw output into per-path lists of LinkedPrimitive (cut operations)
    int path_count = 0;
    for (int i = 0; i < raw_n; ++i) {
        path_count = std::max(path_count, static_cast<int>(raw_meta(i, 0)) + 1);
    }

    std::vector<std::vector<LinkedPrimitive>> paths(path_count);
    for (int i = 0; i < raw_n; ++i) {
        LinkedPrimitive prim;
        prim.path_index = static_cast<int>(raw_meta(i, 0));
        prim.type = static_cast<int>(raw_meta(i, 1));
        prim.clockwise = raw_meta(i, 2) > 0.5;
        prim.operation = 0;  // cut
        prim.sx = raw_starts(i, 0); prim.sy = raw_starts(i, 1); prim.sz = cut_z;
        prim.ex = raw_ends(i, 0);   prim.ey = raw_ends(i, 1);   prim.ez = cut_z;
        prim.cx = raw_centers(i, 0); prim.cy = raw_centers(i, 1); prim.cz = cut_z;
        prim.radius = raw_radii(i, 0);
        paths[prim.path_index].push_back(prim);
    }

    // Remove empty paths
    std::vector<std::vector<LinkedPrimitive>> nonempty;
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

    // Greedy nearest-neighbor path ordering with reversal support
    if (optimize_order && paths.size() > 1) {
        // Start with longest path
        double max_len = -1.0;
        int start_idx = 0;
        for (int i = 0; i < static_cast<int>(paths.size()); ++i) {
            double len = path_length_xy(paths[i]);
            if (len > max_len) { max_len = len; start_idx = i; }
        }

        std::vector<bool> used(paths.size(), false);
        std::vector<std::vector<LinkedPrimitive>> ordered;
        ordered.reserve(paths.size());
        ordered.push_back(paths[start_idx]);
        used[start_idx] = true;

        for (std::size_t step = 1; step < paths.size(); ++step) {
            const auto& last = ordered.back();
            double cur_ex = last.back().ex;
            double cur_ey = last.back().ey;

            int best_idx = -1;
            double best_dist = std::numeric_limits<double>::infinity();

            for (int i = 0; i < static_cast<int>(paths.size()); ++i) {
                if (used[i]) continue;
                // Forward only — reversal breaks arc tangent alignment
                // (DP optimizes arc directions for original traversal direction)
                double dx = paths[i].front().sx - cur_ex;
                double dy = paths[i].front().sy - cur_ey;
                double dist = std::sqrt(dx * dx + dy * dy);
                if (dist < best_dist) {
                    best_dist = dist; best_idx = i;
                }
            }

            ordered.push_back(paths[best_idx]);
            used[best_idx] = true;
        }
        paths.swap(ordered);
    }

    // Build linked operation stream
    const bool use_clearance = has_clearance_z && (clearance_z > cut_z + 1e-12);
    const double safe_z = has_clearance_z ? clearance_z : cut_z;

    std::vector<LinkedPrimitive> operations;
    operations.reserve(raw_n + paths.size() * 6);

    auto make_line = [](double sx, double sy, double sz, double ex, double ey, double ez, int op, int pidx) {
        LinkedPrimitive lp;
        lp.path_index = pidx;
        lp.type = 0; lp.clockwise = false; lp.operation = op;
        lp.sx = sx; lp.sy = sy; lp.sz = sz;
        lp.ex = ex; lp.ey = ey; lp.ez = ez;
        lp.cx = 0; lp.cy = 0; lp.cz = 0; lp.radius = 0;
        return lp;
    };

    double cur_x = 0, cur_y = 0, cur_z = 0;
    bool has_current = false;

    for (int pidx = 0; pidx < static_cast<int>(paths.size()); ++pidx) {
        auto& path = paths[pidx];
        if (path.empty()) continue;

        double path_sx = path.front().sx;
        double path_sy = path.front().sy;
        double path_ex = path.back().ex;
        double path_ey = path.back().ey;

        // Compute lead-in start point
        double lead_in_sx = path_sx, lead_in_sy = path_sy;
        double start_tx = 0, start_ty = 0;
        bool has_start_tangent = path_start_tangent(path, start_tx, start_ty);
        if (lead_in > 1e-12 && has_start_tangent) {
            lead_in_sx = path_sx - lead_in * start_tx;
            lead_in_sy = path_sy - lead_in * start_ty;
        }

        // Connect to this path
        if (!has_current) {
            if (use_clearance) {
                operations.push_back(make_line(lead_in_sx, lead_in_sy, safe_z, lead_in_sx, lead_in_sy, cut_z, 5 /*plunge*/, pidx));
            }
            cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
            has_current = true;
        } else if (link_paths) {
            if (use_clearance) {
                // retract
                double dx1 = cur_x - cur_x, dy1 = cur_y - cur_y;
                (void)dx1; (void)dy1;
                operations.push_back(make_line(cur_x, cur_y, cur_z, cur_x, cur_y, safe_z, 4 /*retract*/, pidx));
                cur_z = safe_z;
                // link at clearance
                double ddx = lead_in_sx - cur_x, ddy = lead_in_sy - cur_y;
                if (std::sqrt(ddx * ddx + ddy * ddy) > 1e-9) {
                    operations.push_back(make_line(cur_x, cur_y, safe_z, lead_in_sx, lead_in_sy, safe_z, 3 /*link*/, pidx));
                }
                // plunge
                operations.push_back(make_line(lead_in_sx, lead_in_sy, safe_z, lead_in_sx, lead_in_sy, cut_z, 5 /*plunge*/, pidx));
                cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
            } else {
                double ddx = lead_in_sx - cur_x, ddy = lead_in_sy - cur_y;
                if (std::sqrt(ddx * ddx + ddy * ddy) > 1e-9) {
                    operations.push_back(make_line(cur_x, cur_y, cut_z, lead_in_sx, lead_in_sy, cut_z, 3 /*link*/, pidx));
                    cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
                }
            }
        } else {
            cur_x = lead_in_sx; cur_y = lead_in_sy; cur_z = cut_z;
        }

        // Lead-in
        if (lead_in > 1e-12 && has_start_tangent) {
            operations.push_back(make_line(lead_in_sx, lead_in_sy, cut_z, path_sx, path_sy, cut_z, 1 /*lead_in*/, pidx));
            cur_x = path_sx; cur_y = path_sy; cur_z = cut_z;
        }

        // Cut primitives
        for (auto& prim : path) {
            prim.path_index = pidx;
            prim.operation = 0;  // cut
            prim.sz = cut_z; prim.ez = cut_z; prim.cz = cut_z;
            operations.push_back(prim);
            cur_x = prim.ex; cur_y = prim.ey; cur_z = cut_z;
        }

        // Lead-out
        double end_tx = 0, end_ty = 0;
        bool has_end_tangent = path_end_tangent(path, end_tx, end_ty);
        if (lead_out > 1e-12 && has_end_tangent) {
            double lo_ex = path_ex + lead_out * end_tx;
            double lo_ey = path_ey + lead_out * end_ty;
            operations.push_back(make_line(path_ex, path_ey, cut_z, lo_ex, lo_ey, cut_z, 2 /*lead_out*/, pidx));
            cur_x = lo_ex; cur_y = lo_ey; cur_z = cut_z;
        }
    }

    // Final retract
    if (use_clearance && retract_at_end && has_current) {
        if (std::abs(cur_z - safe_z) > 1e-9) {
            operations.push_back(make_line(cur_x, cur_y, cur_z, cur_x, cur_y, safe_z, 4 /*retract*/, static_cast<int>(paths.size())));
        }
    }

    // Circle merging
    if (merge_circles) {
        merge_circle_pairs(operations);
    }

    // Pack into matrices (meta is now Nx4)
    const int n = static_cast<int>(operations.size());
    compas::RowMatrixXd meta(n, 4);
    compas::RowMatrixXd starts(n, 3);
    compas::RowMatrixXd ends(n, 3);
    compas::RowMatrixXd centers_out(n, 3);
    compas::RowMatrixXd radii_out(n, 1);
    for (int i = 0; i < n; ++i) {
        const auto& op = operations[i];
        meta(i, 0) = static_cast<double>(op.path_index);
        meta(i, 1) = static_cast<double>(op.type);
        meta(i, 2) = static_cast<double>(op.clockwise ? 1 : 0);
        meta(i, 3) = static_cast<double>(op.operation);

        starts(i, 0) = op.sx; starts(i, 1) = op.sy; starts(i, 2) = op.sz;
        ends(i, 0) = op.ex; ends(i, 1) = op.ey; ends(i, 2) = op.ez;
        centers_out(i, 0) = op.cx; centers_out(i, 1) = op.cy; centers_out(i, 2) = op.cz;
        radii_out(i, 0) = op.radius;
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
