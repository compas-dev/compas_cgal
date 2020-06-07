#ifndef COMPAS_BOOLEANS_H
#define COMPAS_BOOLEANS_H

#include <compas.h>

compas::Result
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> & VA,
    Eigen::Ref<const compas::RowMatrixXi> & FA,
    Eigen::Ref<const compas::RowMatrixXd> & VB,
    Eigen::Ref<const compas::RowMatrixXi> & FB);

compas::Result
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> & VA,
    Eigen::Ref<const compas::RowMatrixXi> & FA,
    Eigen::Ref<const compas::RowMatrixXd> & VB,
    Eigen::Ref<const compas::RowMatrixXi> & FB);

compas::Result
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> & VA,
    Eigen::Ref<const compas::RowMatrixXi> & FA,
    Eigen::Ref<const compas::RowMatrixXd> & VB,
    Eigen::Ref<const compas::RowMatrixXi> & FB);

#endif /* COMPAS_BOOLEANS_H */
