#include "polylines.h"
#include <cmath>

// 3D types for AABB tree queries
using Segment_3 = compas::Kernel::Segment_3;
using Primitive = CGAL::AABB_segment_primitive<compas::Kernel, std::vector<Segment_3>::const_iterator>;
using AABB_traits = CGAL::AABB_traits_3<compas::Kernel, Primitive>;
using AABB_tree = CGAL::AABB_tree<AABB_traits>;


// Douglas-Peucker simplification helper
// Returns perpendicular distance from point to line segment
static double perpendicular_distance(
    double px, double py,
    double x1, double y1, double x2, double y2)
{
    double dx = x2 - x1;
    double dy = y2 - y1;
    double len_sq = dx * dx + dy * dy;

    if (len_sq < 1e-12) {
        // Degenerate segment
        return std::sqrt((px - x1) * (px - x1) + (py - y1) * (py - y1));
    }

    // Project point onto line
    double t = ((px - x1) * dx + (py - y1) * dy) / len_sq;
    t = std::max(0.0, std::min(1.0, t));

    double proj_x = x1 + t * dx;
    double proj_y = y1 + t * dy;

    return std::sqrt((px - proj_x) * (px - proj_x) + (py - proj_y) * (py - proj_y));
}

// Iterative Douglas-Peucker (avoids stack overflow on large polylines)
static void rdp_simplify(
    const compas::RowMatrixXd& polyline,
    int start, int end,
    double threshold,
    std::vector<bool>& keep)
{
    std::vector<std::pair<int, int>> stack;
    stack.reserve(128);  // Reasonable default to avoid reallocs
    stack.push_back({start, end});

    while (!stack.empty()) {
        auto [seg_start, seg_end] = stack.back();
        stack.pop_back();

        if (seg_end <= seg_start + 1) continue;

        double max_dist = 0.0;
        int max_idx = seg_start;

        double x1 = polyline(seg_start, 0);
        double y1 = polyline(seg_start, 1);
        double x2 = polyline(seg_end, 0);
        double y2 = polyline(seg_end, 1);

        for (int i = seg_start + 1; i < seg_end; ++i) {
            double dist = perpendicular_distance(
                polyline(i, 0), polyline(i, 1),
                x1, y1, x2, y2);
            if (dist > max_dist) {
                max_dist = dist;
                max_idx = i;
            }
        }

        if (max_dist > threshold) {
            keep[max_idx] = true;
            stack.push_back({seg_start, max_idx});
            stack.push_back({max_idx, seg_end});
        }
    }
}

std::vector<compas::RowMatrixXd>
pmp_simplify_polylines(
    const std::vector<compas::RowMatrixXd>& polylines,
    double threshold)
{
    std::vector<compas::RowMatrixXd> results;
    results.reserve(polylines.size());

    for (const auto& polyline : polylines) {
        int n = polyline.rows();
        int cols = polyline.cols();

        if (n < 3) {
            results.push_back(polyline);
            continue;
        }

        // Mark which points to keep
        std::vector<bool> keep(n, false);
        keep[0] = true;
        keep[n - 1] = true;

        // Run Douglas-Peucker
        rdp_simplify(polyline, 0, n - 1, threshold, keep);

        // Count kept points
        int kept_count = 0;
        for (int i = 0; i < n; ++i) {
            if (keep[i]) ++kept_count;
        }

        // Build result
        compas::RowMatrixXd result(kept_count, cols);
        int j = 0;
        for (int i = 0; i < n; ++i) {
            if (keep[i]) {
                for (int c = 0; c < cols; ++c) {
                    result(j, c) = polyline(i, c);
                }
                ++j;
            }
        }
        results.push_back(std::move(result));
    }

    return results;
}


compas::RowMatrixXd
pmp_closest_points_on_polyline(
    Eigen::Ref<const compas::RowMatrixXd> query_points,
    Eigen::Ref<const compas::RowMatrixXd> polyline)
{
    int n_queries = query_points.rows();
    int q_cols = query_points.cols();
    int n_poly = polyline.rows();
    int p_cols = polyline.cols();
    int out_cols = std::min(q_cols, p_cols);

    compas::RowMatrixXd result(n_queries, out_cols);

    if (n_poly == 0) {
        result.setZero();
        return result;
    }

    if (n_poly == 1) {
        // Degenerate: single point
        for (int i = 0; i < n_queries; ++i) {
            for (int j = 0; j < out_cols; ++j) {
                result(i, j) = polyline(0, j);
            }
        }
        return result;
    }

    // Build segments from polyline
    std::vector<Segment_3> segments;
    segments.reserve(n_poly - 1);
    for (int i = 0; i < n_poly - 1; ++i) {
        double z1 = (p_cols == 3) ? polyline(i, 2) : 0.0;
        double z2 = (p_cols == 3) ? polyline(i + 1, 2) : 0.0;
        compas::Point p1(polyline(i, 0), polyline(i, 1), z1);
        compas::Point p2(polyline(i + 1, 0), polyline(i + 1, 1), z2);
        if (p1 != p2) {  // Skip degenerate segments
            segments.emplace_back(p1, p2);
        }
    }

    if (segments.empty()) {
        // All points coincide
        for (int i = 0; i < n_queries; ++i) {
            for (int j = 0; j < out_cols; ++j) {
                result(i, j) = polyline(0, j);
            }
        }
        return result;
    }

    // Build AABB tree
    AABB_tree tree(segments.begin(), segments.end());
    tree.build();

    // Query closest points
    for (int i = 0; i < n_queries; ++i) {
        double z = (q_cols == 3) ? query_points(i, 2) : 0.0;
        compas::Point query(query_points(i, 0), query_points(i, 1), z);
        compas::Point closest = tree.closest_point(query);

        result(i, 0) = CGAL::to_double(closest.x());
        result(i, 1) = CGAL::to_double(closest.y());
        if (out_cols == 3) {
            result(i, 2) = CGAL::to_double(closest.z());
        }
    }

    return result;
}


NB_MODULE(_polylines, m) {
    m.def(
        "simplify_polylines",
        &pmp_simplify_polylines,
        "Simplify polylines using Douglas-Peucker algorithm.\n\n"
        "Parameters\n"
        "----------\n"
        "polylines : list of array-like\n"
        "    List of polylines, each as Nx2 or Nx3 matrix (float64)\n"
        "threshold : float\n"
        "    Distance threshold for simplification\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of simplified polylines as matrices",
        "polylines"_a,
        "threshold"_a);

    m.def(
        "closest_points_on_polyline",
        &pmp_closest_points_on_polyline,
        "Find closest points on a polyline for batch of query points.\n\n"
        "Parameters\n"
        "----------\n"
        "query_points : array-like\n"
        "    Query points as Mx2 or Mx3 matrix (float64)\n"
        "polyline : array-like\n"
        "    Polyline points as Nx2 or Nx3 matrix (float64)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "array\n"
        "    Closest points on polyline (same dimensions as input)",
        "query_points"_a,
        "polyline"_a);
}
