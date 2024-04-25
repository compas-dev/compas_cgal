#ifndef COMPAS_STRAIGHT_SKELETON_2_H
#define COMPAS_STRAIGHT_SKELETON_2_H

#include <compas.h>

typedef std::tuple<std::vector<double>, std::vector<double>> Edge;
typedef std::list<Edge> Edges;

Edges pmp_create_interior_straight_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V);

#endif /* COMPAS_STRAIGHT_SKELETON_2_H */
