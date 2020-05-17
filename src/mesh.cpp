#include <compas_cgal.hpp>
#include <pybind11/pybind11.h>


void mesh_test(RowMatrixXd V, RowMatrixXi F) {

    Mesh m = mesh_from_vertices_and_faces(V, F);
}


namespace py = pybind11;


void init_mesh(py::module & m) {
    py::module submodule = m.def_submodule("mesh");

    submodule.def(
        "mesh_test", &mesh_test, py::arg("V").noconvert(), py::arg("F").noconvert());
}
