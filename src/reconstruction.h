#pragma once

#include "compas.h"

/**
 * @brief Perform Poisson surface reconstruction on an oriented pointcloud with normals.
 *
 * @param P The points of the cloud.
 * @param N The normals of the points.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
poisson_surface_reconstruction(
    Eigen::Ref<const compas::RowMatrixXd> P,
    Eigen::Ref<const compas::RowMatrixXd> N);

/**
 * @brief Remove outliers from a pointcloud.
 *
 * @param P The points of the cloud.
 * @param nnnbrs The number of nearest neighbors to consider.
 * @param radius The radius of the sphere to consider as a multiplication factor of the average spacing.
 * @return compas::RowMatrixXd
 *
 */
compas::RowMatrixXd
pointset_outlier_removal(
    Eigen::Ref<const compas::RowMatrixXd> P,
    int nnnbrs,
    double radius);

/**
 * @brief Reduce number of points using hierarcy simplification.
 * https://doc.cgal.org/latest/Point_set_processing_3/Point_set_processing_3_2hierarchy_simplification_example_8cpp-example.html
 *
 * @param P The points of the cloud.
 * @param spacing The scale for the average spacing.
 * @return compas::RowMatrixXd
 *
 */
compas::RowMatrixXd
pointset_reduction(
    Eigen::Ref<const compas::RowMatrixXd> P,
    double spacing = 2.0);

/**
 * @brief Smooth a pointcloud by number of neighbors and iterations using jet_smoothing algorithm.
 * https://doc.cgal.org/4.3/Point_set_processing_3/Point_set_processing_3_2jet_smoothing_example_8cpp-example.html
 *
 * @param P The points of the cloud.
 * @param neighbors The number of nearest neighbors to consider.
 * @param iterations The number of iterations.
 * @return compas::RowMatrixXd
 *
 */
compas::RowMatrixXd
pointset_smoothing(
    Eigen::Ref<const compas::RowMatrixXd> P,
    int neighbors = 8,
    int iterations = 1);

/**
 * @brief Estimate pointcloud normals and oriented them.
 * https://doc.cgal.org/latest/Point_set_processing_3/Point_set_processing_3_2normals_example_8cpp-example.html
 *
 * @param P The points of the cloud.
 * @param neighbors The number of nearest neighbors to consider.
 * @param erase Erase points that are not oriented properly.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
 *
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
pointset_normal_estimation(
    Eigen::Ref<const compas::RowMatrixXd> P,
    int neighbors=8,
    bool erase=true);
