#include <compas.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

void init_meshing(py::module&);
void init_booleans(py::module&);
void init_slicer(py::module&);

PYBIND11_MODULE(_cgal, m) {
    m.doc() = "";

    py::class_<compas::Mesh>(m, "Mesh")
    	.def_readonly("vertices", &compas::Mesh::vertices)
    	.def_readonly("faces", &compas::Mesh::faces);

    init_meshing(m);
    init_booleans(m);
    init_slicer(m);
}
