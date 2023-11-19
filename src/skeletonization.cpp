#include skeletonization.h

// #include <CGAL/Polyhedron_3.h>
// #include <CGAL/Simple_cartesian.h>
// #include <CGAL/Mean_curvature_flow_skeletonization.h>

// std::vector<compas::RowMatrixXd>
void pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    Eigen::Ref<const compas::RowMatrixXi> &F){

};

void init_skeletonization(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("skeletonization");

    submodule.def(
        "mesh_skeleton",
        &pmp_mesh_skeleton,
        pybind11::arg("V").noconvert(),
        pybind11::arg("F").noconvert());
};
