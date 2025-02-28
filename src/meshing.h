#pragma once

#include "stdafx.h"

namespace compas
{
    double
    pmp_area(
        Eigen::Ref<const compas::RowMatrixXd> &V,
        Eigen::Ref<const compas::RowMatrixXi> &F);

    double
    pmp_volume(
        Eigen::Ref<const compas::RowMatrixXd> &V,
        Eigen::Ref<const compas::RowMatrixXi> &F);

    std::vector<double>
    pmp_centroid(
        Eigen::Ref<const compas::RowMatrixXd> &V,
        Eigen::Ref<const compas::RowMatrixXi> &F);
}

void init_meshing(nb::module_ & m);