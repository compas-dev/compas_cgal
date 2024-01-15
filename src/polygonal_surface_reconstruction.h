#ifndef COMPAS_POLYGONAL_SURFACE_RECONSTRUCTION_H
#define COMPAS_POLYGONAL_SURFACE_RECONSTRUCTION_H

#include <compas.h>

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
polygonal_surface_reconstruction_ransac(
    Eigen::Ref<const compas::RowMatrixXd> &P, 
    Eigen::Ref<const compas::RowMatrixXd> &N);

#endif /* COMPAS_POLYGONAL_SURFACE_RECONSTRUCTION_H */
