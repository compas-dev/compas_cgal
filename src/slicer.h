#pragma once

#include "compas.h"

/**
 * @brief Slice a mesh with a set of planes defined by points and normals.
 *
 * @param vertices Matrix of vertex positions as Nx3 matrix in row-major order (float64)
 * @param faces Matrix of face indices as Mx3 matrix in row-major order (int32)
 * @param points Matrix of plane points as Kx3 matrix in row-major order (float64)
 * @param normals Matrix of plane normals as Kx3 matrix in row-major order (float64)
 * @return std::vector<compas::RowMatrixXd> Vector of polylines, each represented as a matrix of points (Px3 float64)
 */
std::vector<compas::RowMatrixXd>
pmp_slice_mesh(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    Eigen::Ref<const compas::RowMatrixXd> points,
    Eigen::Ref<const compas::RowMatrixXd> normals);
