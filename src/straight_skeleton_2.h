#ifndef COMPAS_STRAIGHT_SKELETON_2_H
#define COMPAS_STRAIGHT_SKELETON_2_H

#include <compas.h>


std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> pmp_create_interior_straight_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V);

std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> pmp_create_interior_straight_skeleton_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    std::vector<Eigen::Ref<const compas::RowMatrixXd>> &holes);

std::vector<compas::RowMatrixXd> pmp_create_offset_polygons_2_inner(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    double &offset);

std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> pmp_create_offset_polygons_2_inner_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    std::vector<Eigen::Ref<const compas::RowMatrixXd>> &holes,
    double &offset);

std::vector<compas::RowMatrixXd> pmp_create_offset_polygons_2_outer(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    double &offset);

std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> pmp_create_offset_polygons_2_outer_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    std::vector<Eigen::Ref<const compas::RowMatrixXd>> &holes,
    double &offset);

std::vector<compas::RowMatrixXd> pmp_create_weighted_offset_polygons_2_inner(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    double &offset,
    Eigen::Ref<const compas::RowMatrixXd> &weights);

std::vector<compas::RowMatrixXd> pmp_create_weighted_offset_polygons_2_outer(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    double &offset,
    Eigen::Ref<const compas::RowMatrixXd> &weights);

#endif /* COMPAS_STRAIGHT_SKELETON_2_H */
