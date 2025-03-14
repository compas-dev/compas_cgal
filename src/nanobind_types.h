#pragma once

#include "compas.h"
    
// Example functions for nanobind demonstration
// This file is used to quickly test C++ dummy methods with new types that haven't been tested before.
// It helps isolate problems for debugging when you want to focus on type conversion rather than implementation details.
// Only use these methods when C++ and Python input/output types match exactly.
// Also just use inline methods so that you do not have to declare cpp declarations.

inline void scale_matrix(Eigen::Ref<compas::RowMatrixXd> mat) {
    mat *= 2.0;
}

inline compas::RowMatrixXd create_matrix() {
    compas::RowMatrixXd mat(3, 3);
    mat << 1.1, 2.2, 3.3,
            4.4, 5.5, 6.6,
            7.7, 8.8, 9.9;
    return mat;
}