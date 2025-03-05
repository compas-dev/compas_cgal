/**
 * @file compas_cgal.cpp
 * @brief Main module file for COMPAS CGAL bindings using Nanobind
 */

#include "compas.h"

// Forward declarations
void init_meshing(nb::module_ &);

/**
 * @brief Modifies a matrix in-place by scaling all elements
 * 
 * @param mat Reference to an Eigen matrix to be modified in-place
 * @details Scales every element of the input matrix by a factor of 2.
 *          The modification is done directly on the input matrix.
 *          Uses row-major order to match NumPy's default.
 */
void scale_matrix(Eigen::Ref<Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>> mat) {
    mat *= 2;  // Scale every element by 2 (modifies input directly)
}

/**
 * @brief Creates and returns a new 3x3 matrix with predefined values
 * 
 * @return Eigen::Matrix<double, Dynamic, Dynamic, RowMajor> A new matrix that will be automatically converted to NumPy array
 * @details Creates a 3x3 matrix with predefined double values.
 *          Uses row-major order to match NumPy's default.
 *          The matrix is automatically converted to a NumPy array by Nanobind.
 */
Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> create_matrix() {
    Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> mat(3, 3);
    mat << 1.1, 2.2, 3.3,
           4.4, 5.5, 6.6,
           7.7, 8.8, 9.9;
    return mat;
}

/**
 * @brief Module initialization function for COMPAS CGAL extension
 * 
 * @param m Nanobind module instance
 * @details Initializes the Python module by defining functions and their bindings.
 *          Each function is exposed to Python with appropriate documentation.
 */
NB_MODULE(compas_cgal_ext, m) {
    m.doc() = "CGAL via Nanobind says hello to COMPAS!";
    
    m.def("add", 
          [](int a, int b) { return a + b; }, 
          "Add two integers together",
          "a"_a, "b"_a);
    
    m.def("scale_matrix", 
          &scale_matrix, 
          "Scale an Eigen Matrix in-place by multiplying all elements by 2",
          "mat"_a);
    
    m.def("create_matrix", 
          &create_matrix, 
          "Create and return a new 3x3 matrix with predefined values");
    
    init_meshing(m);
}
