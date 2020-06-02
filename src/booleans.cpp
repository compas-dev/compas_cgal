#include "booleans.h"

#include <CGAL/Polygon_mesh_processing/corefinement.h>

namespace PMP = CGAL::Polygon_mesh_processing;
namespace params = PMP::parameters;
namespace py = pybind11;


compas::Result pmp_boolean_union(
    compas::RowMatrixXd VA,
    compas::RowMatrixXi FA,
    compas::RowMatrixXd VB,
    compas::RowMatrixXi FB)
{
    Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);
    Mesh C;

    PMP::corefine_and_compute_union(A, B, C);

    // Result

    compas::Result R = compas::result_from_mesh(C);

    return R;
}


void init_booleans(py::module & m) {
    py::module submodule = m.def_submodule("booleans");

    submodule.def(
        "boolean_union",
        &pmp_boolean_union,
        py::arg("VA").noconvert(),
        py::arg("FA").noconvert(),
        py::arg("VB").noconvert(),
        py::arg("FB").noconvert()
    );
}
