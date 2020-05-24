#include <iostream>
#include <pybind11/pybind11.h>


int hello_compas() {
    std::cout << "Hello COMPAS\n";
    return 0;
}


namespace py = pybind11;


void init_hello(py::module & m) {
    py::module submodule = m.def_submodule("hello");

    submodule.def("hello_compas", &hello_compas);
}
