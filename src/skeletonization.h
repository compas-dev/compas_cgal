#ifndef COMPAS_SKELETONIZATION_H
#define COMPAS_SKELETONIZATION_H

#include <compas.h>

// std::vector<compas::RowMatrixXd>
void pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    Eigen::Ref<const compas::RowMatrixXi> &F);

#endif /* COMPAS_SKELETONISATION_H */
