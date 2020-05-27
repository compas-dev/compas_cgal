#ifndef COMPAS_H
#define COMPAS_H

#include <pybind11/eigen.h>

namespace compas
{
    using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
    using RowMatrixXi = Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

    struct Mesh {
        RowMatrixXd vertices;
        RowMatrixXi faces;
    };
}

#endif /* COMPAS_H */
