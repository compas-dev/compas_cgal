#include <nanobind/nanobind.h>

namespace nb = nanobind;

using namespace nb::literals;

NB_MODULE(compas_cgal_ext, m) {
    m.doc() = "Nanobind says hello to COMPAS!";
    m.def("add", [](int a, int b) { return a + b; }, "a"_a, "b"_a);
}
