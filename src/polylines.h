#ifndef POLYLINES_H
#define POLYLINES_H

#include <compas.h>

std::vector<compas::RowMatrixXd> pmp_simplify_polylines(
    std::vector<Eigen::Ref<const compas::RowMatrixXd>> &polylines,
    double &threshold);

compas::RowMatrixXd pmp_closest_points_on_polyline(
    Eigen::Ref<const compas::RowMatrixXd> &query_points,
    Eigen::Ref<const compas::RowMatrixXd> &polyline);

#endif /* POLYLINES_H */
