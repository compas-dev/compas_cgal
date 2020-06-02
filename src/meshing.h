#ifndef COMPAS_MESHING_H
#define COMPAS_MESHING_H

#include <compas.h>

compas::Result pmp_remesh(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    double target_edge_length,
    unsigned int niter);


#endif /* COMPAS_MESHING_H */
