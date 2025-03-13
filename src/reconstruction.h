#pragma once

#include "compas.h"

/**
 * @brief Perform Poisson surface reconstruction on an oriented pointcloud with normals.
 *
 * @param points Matrix of point positions as Nx3 matrix in row-major order (float64)
 * @param normals Matrix of point normals as Nx3 matrix in row-major order (float64)
 * @return std::tuple<RowMatrixXd, RowMatrixXi> containing:
 *         - vertices as Rx3 matrix (float64)
 *         - faces as Sx3 matrix (int32)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
poisson_surface_reconstruction(
    Eigen::Ref<const compas::RowMatrixXd> points,
    Eigen::Ref<const compas::RowMatrixXd> normals);

/**
 * @brief Remove outliers from a pointcloud.
 *
 * @param points Matrix of point positions as Nx3 matrix in row-major order (float64)
 * @param num_neighbors The number of nearest neighbors to consider
 * @param radius The radius of the sphere to consider as a multiplication factor of the average spacing
 * @return compas::RowMatrixXd
 *         - Filtered points as Mx3 matrix (float64), where M <= N
 */
compas::RowMatrixXd
pointset_outlier_removal(
    Eigen::Ref<const compas::RowMatrixXd> points,
    int num_neighbors,
    double radius);

/**
 * @brief Reduce number of points using hierarchy simplification.
 * https://doc.cgal.org/latest/Point_set_processing_3/Point_set_processing_3_2hierarchy_simplification_example_8cpp-example.html
 *
 * @param points Matrix of point positions as Nx3 matrix in row-major order (float64)
 * @param spacing The scale for the average spacing
 * @return compas::RowMatrixXd
 *         - Reduced points as Mx3 matrix (float64), where M <= N
 */
compas::RowMatrixXd
pointset_reduction(
    Eigen::Ref<const compas::RowMatrixXd> points,
    double spacing = 2.0);

/**
 * @brief Smooth a pointcloud by number of neighbors and iterations using jet_smoothing algorithm.
 * https://doc.cgal.org/4.3/Point_set_processing_3/Point_set_processing_3_2jet_smoothing_example_8cpp-example.html
 *
 * @param points Matrix of point positions as Nx3 matrix in row-major order (float64)
 * @param num_neighbors The number of nearest neighbors to consider
 * @param num_iterations The number of iterations
 * @return compas::RowMatrixXd
 *         - Smoothed points as Nx3 matrix (float64)
 */
compas::RowMatrixXd
pointset_smoothing(
    Eigen::Ref<const compas::RowMatrixXd> points,
    int num_neighbors = 8,
    int num_iterations = 1);

/**
 * @brief Estimate pointcloud normals and oriented them.
 * https://doc.cgal.org/latest/Point_set_processing_3/Point_set_processing_3_2normals_example_8cpp-example.html
 *
 * @param points Matrix of point positions as Nx3 matrix in row-major order (float64)
 * @param num_neighbors The number of nearest neighbors to consider
 * @param erase_unoriented Erase points that are not oriented properly
 * @return std::tuple<RowMatrixXd, RowMatrixXd> containing:
 *         - points as Mx3 matrix (float64), where M <= N if erase_unoriented is true
 *         - normals as Mx3 matrix (float64)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
pointset_normal_estimation(
    Eigen::Ref<const compas::RowMatrixXd> points,
    int num_neighbors=8,
    bool erase_unoriented=true);
