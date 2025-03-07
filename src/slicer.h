#pragma once

#include "compas.h"

/**
 * @brief Slice a mesh with a set of planes.
 *
 * @param V The vertices of the mesh.
 * @param F The faces of the mesh.
 * @param P The points of the cloud.
 * @param N The normals of the points.
 * @return std::vector<compas::RowMatrixXd>
 */
std::vector<compas::RowMatrixXd>
pmp_slice_mesh(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F,
    Eigen::Ref<const compas::RowMatrixXd> P,
    Eigen::Ref<const compas::RowMatrixXd> N);
