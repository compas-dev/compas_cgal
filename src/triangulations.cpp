#include "triangulations.h"

// #include <CGAL/Polygon_mesh_processing/remesh.h>
// #include <CGAL/Polygon_mesh_processing/detect_features.h>

// namespace PMP = CGAL::Polygon_mesh_processing;
// namespace params = PMP::parameters;
namespace py = pybind11;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_tetrahedralisation(
    Eigen::Ref<const compas::RowMatrixXd> & Points)
{
    mesh.collect_garbage();

    // Result
    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(mesh);

    return R;
};

// void init_meshing(py::module & m) {
//     py::module submodule = m.def_submodule("meshing");

//     submodule.def(
//         "remesh",
//         &pmp_remesh,
//         py::arg("V").noconvert(),
//         py::arg("F").noconvert(),
//         py::arg("target_edge_length"),
//         py::arg("number_of_iterations") = 10,
//         py::arg("do_project") = true
//     );
// };
