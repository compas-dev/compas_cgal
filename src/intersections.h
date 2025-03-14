#pragma once

#include "compas.h"

/**
 * Compute intersection between two triangle meshes.
 *
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order (float64)
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order (int32)
 * @param vertices_b Vertices of mesh B as Px3 matrix in row-major order (float64)
 * @param faces_b Faces of mesh B as Qx3 matrix of vertex indices in row-major order (int32)
 * @return std::vector<RowMatrixXd> containing:
 *         - List of intersection polylines, each as Rx3 matrix of points (float64)
 * @note Input meshes must be manifold and closed
 */
std::vector<compas::RowMatrixXd>
pmp_intersection_mesh_mesh(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);