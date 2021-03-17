#ifndef COMPAS_TRIANGULATIONS_H
#define COMPAS_TRIANGULATIONS_H

#include <compas.h>

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_tetrahedralisation(
    Eigen::Ref<const compas::RowMatrixXd> & Points);

#endif /* COMPAS_TRIANGULATIONS_H */
