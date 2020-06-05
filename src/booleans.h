#ifndef COMPAS_BOOLEANS_H
#define COMPAS_BOOLEANS_H

#include <compas.h>

compas::Result pmp_boolean_union(
    compas::RowMatrixXd VA,
    compas::RowMatrixXi FA,
    compas::RowMatrixXd VB,
    compas::RowMatrixXi FB);

compas::Result pmp_boolean_difference(
    compas::RowMatrixXd VA,
    compas::RowMatrixXi FA,
    compas::RowMatrixXd VB,
    compas::RowMatrixXi FB);

compas::Result pmp_boolean_intersection(
    compas::RowMatrixXd VA,
    compas::RowMatrixXi FA,
    compas::RowMatrixXd VB,
    compas::RowMatrixXi FB);

#endif /* COMPAS_BOOLEANS_H */
