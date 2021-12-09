#ifndef COMPAS_MEASURING_H
#define COMPAS_MEASURING_H

#include <compas.h>

double
pmp_voluming(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & F);

#endif /* COMPAS_MEASURE_H */
