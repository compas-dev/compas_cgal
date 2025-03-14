#include "compas.h"
#include "nanobind_types.h"

// Forward declarations
void init_meshing(nb::module_ &);
void init_measure(nb::module_ &);
void init_booleans(nb::module_ &);
void init_intersections(nb::module_ &);
void init_reconstruction(nb::module_ &);
void init_skeletonization(nb::module_ &);
void init_slicer(nb::module_ &);
void init_subdivision(nb::module_ &);
void init_triangulation(nb::module_ &);
void init_straight_skeleton_2(nb::module_ &);

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

    nb::bind_vector<std::vector<double>>(m, "VectorDouble"); // Be aware that both Pybind11 and Nanobind makes copy for vectors
    init_measure(m);

    init_booleans(m);

    nb::bind_vector<std::vector<compas::RowMatrixXd>>(m, "VectorRowMatrixXd"); // Be aware that both Pybind11 and Nanobind makes copy for vectors
    init_intersections(m);

    init_reconstruction(m);

    init_skeletonization(m);

    init_slicer(m);

    nb::bind_vector<std::vector<int>>(m, "VectorInt");
    nb::bind_vector<std::vector<std::vector<int>>>(m, "VectorVectorInt");
    init_subdivision(m);

    init_triangulation(m);

    init_straight_skeleton_2(m);
}
