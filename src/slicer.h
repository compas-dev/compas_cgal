#ifndef COMPAS_SLICER_H
#define COMPAS_SLICER_H

#include <compas.h>

using Polyline_type = std::vector<Kernel::Point_3>;
using Polylines = std::list<Polyline_type>;

void pmp_slice_mesh(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    compas::RowMatrixXd point,
    compas::RowMatrixXd normal);


#endif /* COMPAS_SLICER_H */
