#pragma once

#include "compas.h"

/**
 * @brief Computes the surface area of a triangle mesh.
 * 
 * @param V An Eigen matrix of vertex positions where each row contains the x,y,z coordinates of a vertex
 * @param F An Eigen matrix of face indices where each row contains three vertex indices defining a triangle
 * @return double The total surface area of the mesh
 */
double
pmp_area(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F);

/**
 * @brief Computes the volume of a closed triangle mesh.
 * 
 * @param V An Eigen matrix of vertex positions where each row contains the x,y,z coordinates of a vertex
 * @param F An Eigen matrix of face indices where each row contains three vertex indices defining a triangle
 * @return double The volume enclosed by the mesh. Returns 0 if the mesh is not closed.
 */
double
pmp_volume(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F);

/**
 * @brief Computes the centroid (center of mass) of a triangle mesh.
 * 
 * @param V An Eigen matrix of vertex positions where each row contains the x,y,z coordinates of a vertex
 * @param F An Eigen matrix of face indices where each row contains three vertex indices defining a triangle
 * @return std::vector<double> A vector containing the x,y,z coordinates of the mesh centroid
 */
std::vector<double>
pmp_centroid(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F);
