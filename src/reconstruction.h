#ifndef COMPAS_RECONSTRUCTION_H
#define COMPAS_RECONSTRUCTION_H

#include <compas.h>

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
poisson_surface_reconstruction(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    Eigen::Ref<const compas::RowMatrixXd> &N);

#endif /* COMPAS_RECONSTRUCTION_H */
