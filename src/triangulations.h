#ifndef COMPAS_TRIANGULATIONS_H
#define COMPAS_TRIANGULATIONS_H

#include <compas.h>


compas::RowMatrixXi
pmp_delaunay_triangulation(
    Eigen::Ref<const compas::RowMatrixXd> & V);


compas::RowMatrixXi
pmp_constrained_delaunay_triangulation(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & E);

#endif /* COMPAS_TRIANGULATIONS_H */
