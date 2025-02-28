#include "stdafx.h"

// Explanation of submodules can be found here:
// https://nanobind.readthedocs.io/en/latest/faq.html#how-can-i-reduce-build-time
void init_meshing(nb::module_ &);

NB_MODULE(compas_cgal_ext, m) {
    m.doc() = "CGAL via Nanobind says hello to COMPAS!";
    m.def("add", [](int a, int b) { return a + b; }, "a"_a, "b"_a);

    init_meshing(m);


}
