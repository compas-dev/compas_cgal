#pragma once

#include "compas.h"

/**
 * Compute the boolean union of two triangle meshes.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Compute the boolean difference (A - B) of two triangle meshes.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Compute the boolean intersection of two triangle meshes.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Clip mesh A using mesh B as a clipping volume.
 * Points of mesh A that lie inside mesh B are removed.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of clipping mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of clipping mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_clip(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);
