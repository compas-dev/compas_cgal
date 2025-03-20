#include "types_std.h"

NB_MODULE(_types_std, m) {

    nb::bind_vector<std::vector<double>>(m, "VectorDouble");
    nb::bind_vector<std::vector<int>>(m, "VectorInt");
    nb::bind_vector<std::vector<std::vector<int>>>(m, "VectorVectorInt");
    nb::bind_vector<std::vector<compas::RowMatrixXd>>(m, "VectorRowMatrixXd");

}