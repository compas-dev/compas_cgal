#include <pybind11/pybind11.h>
#include <compas.h>

namespace py = pybind11;

void init_meshing(py::module&);
void init_booleans(py::module&);
void init_slicer(py::module&);
void init_intersections(py::module&);
void init_measure(py::module&);
void init_measuring(py::module&);
void init_triangulations(py::module&);
void init_subdivision(py::module&);

PYBIND11_MODULE(_cgal, m) {
    m.doc() = "";

    py::class_<compas::Result>(m, "Result")
    	.def_readonly("vertices", &compas::Result::vertices)
    	.def_readonly("faces", &compas::Result::faces);

    init_meshing(m);
    init_booleans(m);
    init_slicer(m);
    init_intersections(m);
    init_measure(m);
    init_measuring(m);
    init_triangulations(m);
    init_subdivision(m);
}
