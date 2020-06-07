#ifndef COMPAS_MESHING_H
#define COMPAS_MESHING_H

#include <compas.h>

compas::Result
pmp_remesh(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & F,
    double target_edge_length,
    unsigned int niter);


#endif /* COMPAS_MESHING_H */
