#pragma once

#include "compas.h"

/**
 * @brief Creates a straight skeleton from a simple polygon without holes.
 * 
 * @param points Input polygon vertices as a matrix where each row is a 2D point
 * @return std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> 
 *         First matrix: skeleton vertices (n x 2)
 *         Second vector: vertex indices of the input polygon that generated each skeleton vertex
 *         Third matrix: skeleton edges as vertex pairs (m x 2)
 *         Fourth vector: edge indices of the input polygon that generated each skeleton edge
 */
std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> 
pmp_create_interior_straight_skeleton(
    Eigen::Ref<compas::RowMatrixXd> points
);

/**
 * @brief Creates a straight skeleton from a polygon with holes.
 * 
 * @param boundary Boundary polygon vertices as a matrix where each row is a 2D point
 * @param holes Vector of hole polygons, each represented as a matrix of 2D points
 * @return std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> 
 *         First matrix: skeleton vertices (n x 2)
 *         Second vector: vertex indices of the input polygon that generated each skeleton vertex
 *         Third matrix: skeleton edges as vertex pairs (m x 2)
 *         Fourth vector: edge indices of the input polygon that generated each skeleton edge
 */
std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> 
pmp_create_interior_straight_skeleton_with_holes(
    Eigen::Ref<compas::RowMatrixXd> boundary,
    const std::vector<compas::RowMatrixXd>& holes
);

/**
 * @brief Creates offset polygons from a simple polygon.
 * 
 * @param points Input polygon vertices as a matrix where each row is a 2D point
 * @param offset Offset distance (positive for inward, negative for outward)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as a matrix of 2D points
 */
std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_inner(
    Eigen::Ref<compas::RowMatrixXd> points,
    double offset
);

/**
 * @brief Creates offset polygons from a polygon with holes.
 * 
 * @param boundary Boundary polygon vertices as a matrix where each row is a 2D point
 * @param holes Vector of hole polygons, each represented as a matrix of 2D points
 * @param offset Offset distance (positive for inward, negative for outward)
 * @return std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> 
 *         Vector of offset polygons, each as a tuple containing the outer polygon and a vector of inner polygons
 */
std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_inner_with_holes(
    Eigen::Ref<compas::RowMatrixXd> boundary,
    const std::vector<compas::RowMatrixXd>& holes,
    double offset
);

/**
 * @brief Creates offset polygons from a simple polygon.
 * 
 * @param points Input polygon vertices as a matrix where each row is a 2D point
 * @param offset Offset distance (positive for inward, negative for outward)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as a matrix of 2D points
 */
std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_outer(
    Eigen::Ref<compas::RowMatrixXd> points,
    double offset
);

/**
 * @brief Creates offset polygons from a polygon with holes.
 * 
 * @param boundary Boundary polygon vertices as a matrix where each row is a 2D point
 * @param holes Vector of hole polygons, each represented as a matrix of 2D points
 * @param offset Offset distance (positive for inward, negative for outward)
 * @return std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> 
 *         Vector of offset polygons, each as a tuple containing the outer polygon and a vector of inner polygons
 */
std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_outer_with_holes(
    Eigen::Ref<compas::RowMatrixXd> boundary,
    const std::vector<compas::RowMatrixXd>& holes,
    double offset
);

/**
 * @brief Creates weighted offset polygons from a simple polygon.
 * 
 * @param points Input polygon vertices as a matrix where each row is a 2D point
 * @param offset Offset distance (positive for inward, negative for outward)
 * @param weights Weights for each vertex of the input polygon
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as a matrix of 2D points
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_inner(
    Eigen::Ref<compas::RowMatrixXd> points,
    double offset,
    Eigen::Ref<compas::RowMatrixXd> weights
);

/**
 * @brief Creates weighted offset polygons from a simple polygon.
 * 
 * @param points Input polygon vertices as a matrix where each row is a 2D point
 * @param offset Offset distance (positive for inward, negative for outward)
 * @param weights Weights for each vertex of the input polygon
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as a matrix of 2D points
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_outer(
    Eigen::Ref<compas::RowMatrixXd> points,
    double offset,
    Eigen::Ref<compas::RowMatrixXd> weights
);

