/**
 * @file meshing.h
 * @brief Header file for mesh processing operations using CGAL
 */

#pragma once

#include "compas.h"

namespace compas {

    /**
     * @brief Calculate the surface area of a mesh
     * @param V Matrix of vertex coordinates
     * @param F Matrix of face indices
     * @return Surface area of the mesh
     */
    double pmp_area(
        Eigen::Ref<const RowMatrixXd>& V,
        Eigen::Ref<const RowMatrixXi>& F);

    /**
     * @brief Calculate the volume enclosed by a mesh
     * @param V Matrix of vertex coordinates
     * @param F Matrix of face indices
     * @return Volume enclosed by the mesh
     */
    double pmp_volume(
        Eigen::Ref<const RowMatrixXd>& V,
        Eigen::Ref<const RowMatrixXi>& F);

    /**
     * @brief Calculate the centroid of a mesh
     * @param V Matrix of vertex coordinates
     * @param F Matrix of face indices
     * @return Coordinates of the mesh centroid
     */
    std::vector<double> pmp_centroid(
        Eigen::Ref<const RowMatrixXd>& V,
        Eigen::Ref<const RowMatrixXi>& F);

} // namespace compas

/**
 * @brief Remesh a triangle mesh with target edge length
 * @param V Matrix of vertex coordinates (row-major)
 * @param F Matrix of face indices (row-major)
 * @param target_edge_length Desired length for mesh edges
 * @param number_of_iterations Number of remeshing iterations
 * @param do_project Whether to project vertices onto the input surface
 * @return Tuple containing new vertices and faces matrices (row-major)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_remesh(
    Eigen::Ref<compas::RowMatrixXd> V,
    Eigen::Ref<compas::RowMatrixXi> F,
    double target_edge_length,
    unsigned int number_of_iterations = 10,
    bool do_project = true);
