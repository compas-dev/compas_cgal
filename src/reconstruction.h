#ifndef COMPAS_RECONSTRUCTION_H
#define COMPAS_RECONSTRUCTION_H

#include <compas.h>

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
poisson_surface_reconstruction(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    Eigen::Ref<const compas::RowMatrixXd> &N);

compas::RowMatrixXd
pointset_outlier_removal(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int nnnbrs,
    double radius);

void pointset_reduction(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    double radius = 0.0);

void pointset_smoothing(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int k = 10,
    double radius = 0.0);

void pointset_normal_esitmation(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int k = 10,
    double radius = 0.0);

#endif /* COMPAS_RECONSTRUCTION_H */
