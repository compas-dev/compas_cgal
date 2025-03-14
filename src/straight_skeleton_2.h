#pragma once

#include "compas.h"

/**
 * @brief Creates a straight skeleton from a simple polygon without holes.
 * 
 * @param vertices Matrix of polygon vertices as Nx2 matrix in row-major order (float64)
 * @return std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> containing:
 *         - Matrix of skeleton vertices (Mx2, float64)
 *         - Vector of source vertex indices from input polygon for each skeleton vertex
 *         - Matrix of skeleton edges as vertex pairs (Kx2, int32)
 *         - Vector of source edge indices from input polygon for each skeleton edge
 */
std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> 
pmp_create_interior_straight_skeleton(
    const compas::RowMatrixXd& vertices
);

/**
 * @brief Creates a straight skeleton from a polygon with holes.
 * 
 * @param boundary_vertices Matrix of boundary polygon vertices as Nx2 matrix in row-major order (float64)
 * @param hole_vertices Vector of hole polygons, each as Mx2 matrix in row-major order (float64)
 * @return std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> containing:
 *         - Matrix of skeleton vertices (Px2, float64)
 *         - Vector of source vertex indices from input polygon for each skeleton vertex
 *         - Matrix of skeleton edges as vertex pairs (Qx2, int32)
 *         - Vector of source edge indices from input polygon for each skeleton edge
 */
std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> 
pmp_create_interior_straight_skeleton_with_holes(
    const compas::RowMatrixXd& boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices
);

/**
 * @brief Creates offset polygons from a simple polygon.
 * 
 * @param vertices Matrix of polygon vertices as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 */
std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_inner(
    const compas::RowMatrixXd& vertices,
    double& offset_distance
);

/**
 * @brief Creates offset polygons from a polygon with holes.
 * 
 * @param boundary_vertices Matrix of boundary polygon vertices as Nx2 matrix in row-major order (float64)
 * @param hole_vertices Vector of hole polygons, each as Mx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> Vector containing:
 *         - For each offset: tuple of outer polygon (Px2, float64) and vector of inner polygons (each Qx2, float64)
 */
std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_inner_with_holes(
    const compas::RowMatrixXd& boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices,
    double& offset_distance
);

/**
 * @brief Creates outward offset polygons from a simple polygon.
 * 
 * @param vertices Matrix of polygon vertices as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 */
std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_outer(
    const compas::RowMatrixXd& vertices,
    double& offset_distance
);

/**
 * @brief Creates outward offset polygons from a polygon with holes.
 * 
 * @param boundary_vertices Matrix of boundary polygon vertices as Nx2 matrix in row-major order (float64)
 * @param hole_vertices Vector of hole polygons, each as Mx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> Vector containing:
 *         - For each offset: tuple of outer polygon (Px2, float64) and vector of inner polygons (each Qx2, float64)
 */
std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_outer_with_holes(
    const compas::RowMatrixXd& boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices,
    double& offset_distance
);

/**
 * @brief Create weighted offset polygons for the interior of a polygon.
 * 
 * @param vertices Matrix of vertex coordinates as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (must be positive)
 * @param edge_weights Matrix of weights for each edge as Nx1 matrix (float64, must be positive)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 * @throws std::invalid_argument if edge_weights size doesn't match vertices or if weights are not positive
 * @throws std::runtime_error if CGAL fails to create the skeleton or offset
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_inner(
    const compas::RowMatrixXd& vertices,
    double offset_distance,
    const compas::RowMatrixXd& edge_weights
);

/**
 * @brief Create weighted offset polygons for the exterior of a polygon.
 * 
 * @param vertices Matrix of vertex coordinates as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (must be positive)
 * @param edge_weights Matrix of weights for each edge as Nx1 matrix (float64, must be positive)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 * @throws std::invalid_argument if edge_weights size doesn't match vertices or if weights are not positive
 * @throws std::runtime_error if CGAL fails to create the skeleton or offset
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_outer(
    const compas::RowMatrixXd& vertices,
    double offset_distance,
    const compas::RowMatrixXd& edge_weights
);

void init_straight_skeleton_2(nb::module_& m);