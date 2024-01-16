#ifndef COMPAS_POLYGONAL_SURFACE_RECONSTRUCTION_H
#define COMPAS_POLYGONAL_SURFACE_RECONSTRUCTION_H

#include <compas.h>

std::tuple<compas::RowMatrixXd, std::vector<std::vector<int>>>
polygonal_surface_reconstruction_ransac(
    Eigen::Ref<const compas::RowMatrixXd> &P, 
    Eigen::Ref<const compas::RowMatrixXd> &N);

#endif /* COMPAS_POLYGONAL_SURFACE_RECONSTRUCTION_H */
