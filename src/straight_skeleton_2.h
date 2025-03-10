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
    const compas::RowMatrixXd& points
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
    const compas::RowMatrixXd& boundary,
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
pmp_create_offset_polygons_2_inner(const compas::RowMatrixXd& V, double &offset);

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
    const compas::RowMatrixXd& V,
    const std::vector<compas::RowMatrixXd>& holes,
    double &offset
);

/**
 * @brief Creates offset polygons from a simple polygon.
 * 
 * @param points Input polygon vertices as a matrix where each row is a 2D point
 * @param offset Offset distance (positive for inward, negative for outward)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as a matrix of 2D points
 */
std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_outer(const compas::RowMatrixXd& V, double &offset);

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
    const compas::RowMatrixXd& V,
    const std::vector<compas::RowMatrixXd>& holes,
    double &offset);

/**
 * Create weighted offset polygons for the interior of a polygon.
 * 
 * @param V Matrix of vertex coordinates (n x 3)
 * @param offset Offset distance (positive)
 * @param weights Matrix of weights for each edge (n x 1), must be positive
 * @return Vector of offset polygon vertex matrices
 * @throws std::invalid_argument if weights size doesn't match vertices or if weights are not positive
 * @throws std::runtime_error if CGAL fails to create the skeleton or offset
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_inner(
    const compas::RowMatrixXd& V,
    double offset,
    const compas::RowMatrixXd& weights);

/**
 * Create weighted offset polygons for the exterior of a polygon.
 * 
 * @param V Matrix of vertex coordinates (n x 3)
 * @param offset Offset distance (positive)
 * @param weights Matrix of weights for each edge (n x 1), must be positive
 * @return Vector of offset polygon vertex matrices
 * @throws std::invalid_argument if weights size doesn't match vertices or if weights are not positive
 * @throws std::runtime_error if CGAL fails to create the skeleton or offset
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_outer(
    const compas::RowMatrixXd& V,
    double offset,
    const compas::RowMatrixXd& weights);

void init_straight_skeleton_2(nb::module_& m);