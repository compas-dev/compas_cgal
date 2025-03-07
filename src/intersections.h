#pragma once

#include "compas.h"

/**
 * Compute intersection between two meshes.
 *
 * @param VA Vertices of first mesh as Nx3 matrix in row-major order (float64)
 * @param FA Faces of first mesh as Mx3 matrix of vertex indices in row-major order (int32)
 * @param VB Vertices of second mesh as Nx3 matrix in row-major order (float64)
 * @param FB Faces of second mesh as Mx3 matrix of vertex indices in row-major order (int32)
 * @return List of intersection points as Nx3 matrix in row-major order (float64)
 * @note Input meshes must be manifold and closed
 */
std::vector<compas::RowMatrixXd>
pmp_intersection_mesh_mesh(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB);