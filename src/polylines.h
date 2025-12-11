#pragma once

#include "compas.h"

// CGAL AABB tree for closest point queries
#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits_3.h>
#include <CGAL/AABB_segment_primitive.h>

/**
 * @brief Simplify polylines using Douglas-Peucker algorithm.
 *
 * Simplification is performed in the XY plane only. For 3D polylines,
 * Z coordinates are preserved but not considered in distance calculations.
 *
 * @param polylines Vector of polylines, each as Nx2 or Nx3 matrix (float64)
 * @param threshold Distance threshold for simplification
 * @return std::vector<compas::RowMatrixXd> Simplified polylines
 */
std::vector<compas::RowMatrixXd>
pmp_simplify_polylines(
    const std::vector<compas::RowMatrixXd>& polylines,
    double threshold);

/**
 * @brief Find closest points on a polyline for batch of query points.
 *
 * @param query_points Query points as Mx2 or Mx3 matrix (float64)
 * @param polyline Polyline points as Nx2 or Nx3 matrix (float64)
 * @return compas::RowMatrixXd Closest points on polyline (Mx2 or Mx3)
 */
compas::RowMatrixXd
pmp_closest_points_on_polyline(
    const compas::RowMatrixXd& query_points,
    const compas::RowMatrixXd& polyline);
