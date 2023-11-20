#ifndef COMPAS_SKELETONIZATION_H
#define COMPAS_SKELETONIZATION_H

#include <compas.h>

typedef std::tuple<std::vector<double>, std::vector<double>> Edge;
typedef std::list<Edge> Edges;

Edges pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    Eigen::Ref<const compas::RowMatrixXi> &F);

#endif /* COMPAS_SKELETONISATION_H */
