/**
 * @file meshing.h
 * @brief Header file for mesh processing operations using CGAL
 */

#pragma once

#include "stdafx.h"

namespace compas {
    /**
     * @brief Calculate the surface area of a mesh
     * 
     * @param V Matrix of vertex coordinates
     * @param F Matrix of face indices
     * @return double Surface area of the mesh
     */
    double pmp_area(
        Eigen::Ref<const compas::RowMatrixXd>& V,
        Eigen::Ref<const compas::RowMatrixXi>& F);

    /**
     * @brief Calculate the volume enclosed by a mesh
     * 
     * @param V Matrix of vertex coordinates
     * @param F Matrix of face indices
     * @return double Volume enclosed by the mesh
     */
    double pmp_volume(
        Eigen::Ref<const compas::RowMatrixXd>& V,
        Eigen::Ref<const compas::RowMatrixXi>& F);

    /**
     * @brief Calculate the centroid of a mesh
     * 
     * @param V Matrix of vertex coordinates
     * @param F Matrix of face indices
     * @return std::vector<double> Coordinates of the mesh centroid
     */
    std::vector<double> pmp_centroid(
        Eigen::Ref<const compas::RowMatrixXd>& V,
        Eigen::Ref<const compas::RowMatrixXi>& F);
}

/**
 * @brief Remesh a triangle mesh with target edge length
 * 
 * @param V Matrix of vertex coordinates (row-major)
 * @param F Matrix of face indices (row-major)
 * @param target_edge_length Desired length for mesh edges
 * @param number_of_iterations Number of remeshing iterations
 * @param do_project Whether to project vertices onto the input surface
 * @return std::tuple<RowMatrixXd, RowMatrixXi> Tuple containing new vertices and faces (both row-major)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_remesh(
    Eigen::Ref<compas::RowMatrixXd> V,
    Eigen::Ref<compas::RowMatrixXi> F,
    double target_edge_length,
    unsigned int number_of_iterations,
    bool do_project);
