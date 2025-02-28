NB_MODULE(compas_cgal_ext, m) {
    m.doc() = "CGAL via Nanobind says hello to COMPAS!";
    m.def("add", [](int a, int b) { return a + b; }, "a"_a, "b"_a);
}
