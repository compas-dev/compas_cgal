#pragma once

#include "compas.h"

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_catmullclark(
    compas::RowMatrixXd V,
    std::vector<std::vector<int>> faces,
    unsigned int k);

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_loop(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    unsigned int k);

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_sqrt3(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    unsigned int k);