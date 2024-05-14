#ifndef COMPAS_STRAIGHT_SKELETON_2_H
#define COMPAS_STRAIGHT_SKELETON_2_H

#include <compas.h>


compas::Edges pmp_create_interior_straight_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V);


compas::Edges pmp_create_interior_straight_skeleton_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    std::vector<Eigen::Ref<const compas::RowMatrixXd>> &holes);

#endif /* COMPAS_STRAIGHT_SKELETON_2_H */
