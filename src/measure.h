#pragma once

#include "compas.h"

/**
 * @brief Computes the surface area of a triangle mesh.
 * 
 * @param vertices Matrix of vertex positions as Nx3 matrix in row-major order (float64)
 * @param faces Matrix of face indices as Mx3 matrix in row-major order (int32)
 * @return double The total surface area of the mesh
 */
double
pmp_area(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces);

/**
 * @brief Computes the volume of a closed triangle mesh.
 * 
 * @param vertices Matrix of vertex positions as Nx3 matrix in row-major order (float64)
 * @param faces Matrix of face indices as Mx3 matrix in row-major order (int32)
 * @return double The volume enclosed by the mesh. Returns 0 if the mesh is not closed.
 */
double
pmp_volume(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces);

/**
 * @brief Computes the centroid (center of mass) of a triangle mesh.
 * 
 * @param vertices Matrix of vertex positions as Nx3 matrix in row-major order (float64)
 * @param faces Matrix of face indices as Mx3 matrix in row-major order (int32)
 * @return std::vector<double> A vector containing the x,y,z coordinates of the mesh centroid
 */
std::vector<double>
pmp_centroid(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces);
