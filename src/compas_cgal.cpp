#include <pybind11/pybind11.h>

namespace py = pybind11;

void init_meshing(py::module&);
void init_booleans(py::module&);

PYBIND11_MODULE(_cgal, m) {
    m.doc() = "";

    init_meshing(m);
    init_booleans(m);
}
