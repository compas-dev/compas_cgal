#pragma once

#include "compas.h"

/**
 * @brief Subdivide a mesh with the Catmull-Clark scheme.
 * 
 * @param vertices Matrix of vertex positions (Nx3, float64)
 * @param faces List of face vertex indices (list of lists)
 * @param num_iterations Number of subdivision steps
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> 
 *         Tuple containing:
 *         - Matrix of subdivided vertex positions (Mx3, float64)
 *         - Matrix of subdivided face vertex indices (Px4, int32)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_catmullclark(
    compas::RowMatrixXd vertices,
    std::vector<std::vector<int>> faces,
    unsigned int num_iterations);

/**
 * @brief Subdivide a mesh with the Loop scheme.
 * 
 * @param vertices Matrix of vertex positions (Nx3, float64)
 * @param faces Matrix of face vertex indices (Mx3, int32)
 * @param num_iterations Number of subdivision steps
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 *         Tuple containing:
 *         - Matrix of subdivided vertex positions (Px3, float64)
 *         - Matrix of subdivided face vertex indices (Qx3, int32)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_loop(
    compas::RowMatrixXd vertices,
    compas::RowMatrixXi faces,
    unsigned int num_iterations);

/**
 * @brief Subdivide a mesh with the Sqrt3 scheme.
 * 
 * @param vertices Matrix of vertex positions (Nx3, float64)
 * @param faces Matrix of face vertex indices (Mx3, int32)
 * @param num_iterations Number of subdivision steps
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 *         Tuple containing:
 *         - Matrix of subdivided vertex positions (Px3, float64)
 *         - Matrix of subdivided face vertex indices (Qx3, int32)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_sqrt3(
    compas::RowMatrixXd vertices,
    compas::RowMatrixXi faces,
    unsigned int num_iterations);