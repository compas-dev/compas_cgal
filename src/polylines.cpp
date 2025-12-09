#include "polylines.h"
#include <list>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Constrained_Delaunay_triangulation_2.h>
#include <CGAL/Constrained_triangulation_plus_2.h>
#include <CGAL/Polyline_simplification_2/simplify.h>
#include <CGAL/Polyline_simplification_2/Squared_distance_cost.h>
#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits_2.h>
#include <CGAL/AABB_segment_primitive_2.h>

namespace PS = CGAL::Polyline_simplification_2;

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef K::Point_2 Point_2;
typedef K::Segment_2 Segment_2;
typedef CGAL::Polygon_2<K> Polygon_2;

// Simplification types
typedef PS::Vertex_base_2<K> Vb;
typedef CGAL::Constrained_triangulation_face_base_2<K> Fb;
typedef CGAL::Triangulation_data_structure_2<Vb, Fb> TDS;
typedef CGAL::Constrained_Delaunay_triangulation_2<K, TDS, CGAL::Exact_predicates_tag> CDT;
typedef CGAL::Constrained_triangulation_plus_2<CDT> CT;
typedef PS::Stop_above_cost_threshold Stop;
typedef PS::Squared_distance_cost Cost;

// AABB tree types for closest point queries
typedef std::list<Segment_2> SegmentRange;
typedef SegmentRange::const_iterator SegmentIterator;
typedef CGAL::AABB_segment_primitive_2<K, SegmentIterator> Primitive;
typedef CGAL::AABB_traits_2<K, Primitive> Traits;
typedef CGAL::AABB_tree<Traits> Tree;

/**
 * @brief Simplify polylines using Douglas-Peucker algorithm via CGAL.
 *
 * @param polylines Vector of Nx2 or Nx3 matrices (z is ignored for 2D simplification)
 * @param threshold Squared distance threshold for simplification
 * @return std::vector<compas::RowMatrixXd> Simplified polylines
 */
std::vector<compas::RowMatrixXd> pmp_simplify_polylines(
    std::vector<Eigen::Ref<const compas::RowMatrixXd>> &polylines,
    double &threshold)
{
    std::vector<compas::RowMatrixXd> result;

    for (auto &polyline_ref : polylines)
    {
        compas::RowMatrixXd polyline = polyline_ref;
        int n = polyline.rows();
        if (n < 3)
        {
            // Can't simplify polyline with less than 3 points
            result.push_back(polyline);
            continue;
        }

        // Create constrained triangulation and insert polyline as constraint
        CT ct;
        std::vector<Point_2> points;
        for (int i = 0; i < n; i++)
        {
            points.push_back(Point_2(polyline(i, 0), polyline(i, 1)));
        }

        // Check if polyline is closed (first == last point)
        bool is_closed = (points.front() == points.back());

        if (is_closed)
        {
            // Insert as polygon constraint
            Polygon_2 poly(points.begin(), points.end() - 1); // exclude duplicate last point
            ct.insert_constraint(poly);
        }
        else
        {
            // Insert as open polyline constraint
            ct.insert_constraint(points.begin(), points.end());
        }

        // Simplify with squared distance cost and threshold stop criterion
        PS::simplify(ct, Cost(), Stop(threshold * threshold));

        // Extract simplified polyline
        for (auto cit = ct.constraints_begin(); cit != ct.constraints_end(); ++cit)
        {
            std::vector<Point_2> simplified_pts;
            for (auto vit = ct.points_in_constraint_begin(*cit);
                 vit != ct.points_in_constraint_end(*cit); ++vit)
            {
                simplified_pts.push_back(*vit);
            }

            // Determine output columns (preserve z if present)
            int cols = (polyline.cols() >= 3) ? 3 : 2;
            compas::RowMatrixXd simplified(simplified_pts.size(), cols);

            for (std::size_t i = 0; i < simplified_pts.size(); i++)
            {
                simplified(i, 0) = simplified_pts[i].x();
                simplified(i, 1) = simplified_pts[i].y();
                if (cols == 3)
                {
                    simplified(i, 2) = 0.0; // z is lost in 2D simplification
                }
            }

            result.push_back(simplified);
        }
    }

    return result;
}

/**
 * @brief Find closest points on a polyline for a batch of query points.
 *
 * Uses CGAL AABB tree for efficient O(log n) queries per point.
 *
 * @param query_points Mx2 or Mx3 matrix of query points
 * @param polyline Nx2 or Nx3 matrix of polyline vertices
 * @return compas::RowMatrixXd Mx2 or Mx3 matrix of closest points on polyline
 */
compas::RowMatrixXd pmp_closest_points_on_polyline(
    Eigen::Ref<const compas::RowMatrixXd> &query_points,
    Eigen::Ref<const compas::RowMatrixXd> &polyline)
{
    int m = query_points.rows();
    int n = polyline.rows();
    int cols = (query_points.cols() >= 3) ? 3 : 2;

    compas::RowMatrixXd result(m, cols);

    if (n < 2)
    {
        // Degenerate case: single point polyline
        for (int i = 0; i < m; i++)
        {
            result(i, 0) = polyline(0, 0);
            result(i, 1) = polyline(0, 1);
            if (cols == 3)
            {
                result(i, 2) = (polyline.cols() >= 3) ? polyline(0, 2) : 0.0;
            }
        }
        return result;
    }

    // Build segment list from polyline
    std::list<Segment_2> segments;
    for (int i = 0; i < n - 1; i++)
    {
        Point_2 p1(polyline(i, 0), polyline(i, 1));
        Point_2 p2(polyline(i + 1, 0), polyline(i + 1, 1));
        segments.push_back(Segment_2(p1, p2));
    }

    // Build AABB tree
    Tree tree(segments.begin(), segments.end());
    tree.build();
    tree.accelerate_distance_queries();

    // Query closest point for each query point
    for (int i = 0; i < m; i++)
    {
        Point_2 query(query_points(i, 0), query_points(i, 1));
        Point_2 closest = tree.closest_point(query);

        result(i, 0) = closest.x();
        result(i, 1) = closest.y();
        if (cols == 3)
        {
            // For 3D, we'd need to interpolate z along the segment
            // For now, return 0 (this is a 2D operation)
            result(i, 2) = 0.0;
        }
    }

    return result;
}

// ===========================================================================
// PyBind11
// ===========================================================================

void init_polylines(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("polylines");

    submodule.def(
        "simplify_polylines",
        &pmp_simplify_polylines,
        pybind11::arg("polylines").noconvert(),
        pybind11::arg("threshold").noconvert());

    submodule.def(
        "closest_points_on_polyline",
        &pmp_closest_points_on_polyline,
        pybind11::arg("query_points").noconvert(),
        pybind11::arg("polyline").noconvert());
}
