#ifndef COMPAS_SLICER_H
#define COMPAS_SLICER_H

#include <compas.h>

// std::vector<compas::RowMatrixXd, Eigen::aligned_allocator<compas::RowMatrixXd>>
compas::RowMatrixXd
pmp_slice_mesh(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    compas::RowMatrixXd P,
    compas::RowMatrixXd N);


#endif /* COMPAS_SLICER_H */
