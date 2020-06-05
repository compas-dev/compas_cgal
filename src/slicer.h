#ifndef COMPAS_SLICER_H
#define COMPAS_SLICER_H

#include <compas.h>

compas::RowMatrixXd pmp_slice_mesh(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    compas::RowMatrixXd point,
    compas::RowMatrixXd normal);


#endif /* COMPAS_SLICER_H */
