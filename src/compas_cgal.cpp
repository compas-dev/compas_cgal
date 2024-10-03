#include <pybind11/pybind11.h>
#include <compas.h>

// here all modules of "_cgal" are declared.
void init_meshing(pybind11::module &);
void init_booleans(pybind11::module &);
void init_slicer(pybind11::module &);
void init_intersections(pybind11::module &);
void init_measure(pybind11::module &);
void init_triangulations(pybind11::module &);
void init_subdivision(pybind11::module &);
void init_skeletonization(pybind11::module &);
void init_reconstruction(pybind11::module &);
void init_polygonal_surface_reconstruction(pybind11::module &);
void init_straight_skeleton_2(pybind11::module &);

// the first parameter here ("cgal") will be the name of the "so" or "pyd" file that will be produced by PyBind11
// which is the entry point from where all other modules will be accessible.
PYBIND11_MODULE(cgal, m)
{
    m.doc() = "";

    // here all modules of "cgal" are initializied.
    init_meshing(m);
    init_booleans(m);
    init_slicer(m);
    init_intersections(m);
    init_measure(m);
    init_triangulations(m);
    init_subdivision(m);
    init_skeletonization(m);
    init_reconstruction(m);
    init_polygonal_surface_reconstruction(m);
    init_straight_skeleton_2(m);
}
