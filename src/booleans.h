#pragma once

#include "compas.h"

/**
 * Compute the boolean union of two triangle meshes.
 * 
 * @param VA Vertices of mesh A as Nx3 matrix in row-major order
 * @param FA Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param VB Vertices of mesh B as Px3 matrix in row-major order
 * @param FB Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB);

/**
 * Compute the boolean difference (A - B) of two triangle meshes.
 * 
 * @param VA Vertices of mesh A as Nx3 matrix in row-major order
 * @param FA Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param VB Vertices of mesh B as Px3 matrix in row-major order
 * @param FB Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB);

/**
 * Compute the boolean intersection of two triangle meshes.
 * 
 * @param VA Vertices of mesh A as Nx3 matrix in row-major order
 * @param FA Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param VB Vertices of mesh B as Px3 matrix in row-major order
 * @param FB Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB);

/**
 * Clip mesh A using mesh B as a clipping volume.
 * Points of mesh A that lie inside mesh B are removed.
 * 
 * @param VA Vertices of mesh A as Nx3 matrix in row-major order
 * @param FA Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param VB Vertices of clipping mesh B as Px3 matrix in row-major order
 * @param FB Faces of clipping mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_clip(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB);
