#include "booleans.h"

#include <CGAL/Polygon_mesh_processing/corefinement.h>

namespace PMP = CGAL::Polygon_mesh_processing;
namespace params = PMP::parameters;
namespace py = pybind11;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> &VA,
    Eigen::Ref<const compas::RowMatrixXi> &FA,
    Eigen::Ref<const compas::RowMatrixXd> &VB,
    Eigen::Ref<const compas::RowMatrixXi> &FB)
{
    Mesh A = compas::trimesh_from_vertices_and_faces(VA, FA);
    Mesh B = compas::trimesh_from_vertices_and_faces(VB, FB);
    Mesh C;

    PMP::corefine_and_compute_union(A, B, C);

    // Result

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::trimesh_to_vertices_and_faces(C);

    return R;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> &VA,
    Eigen::Ref<const compas::RowMatrixXi> &FA,
    Eigen::Ref<const compas::RowMatrixXd> &VB,
    Eigen::Ref<const compas::RowMatrixXi> &FB)
{
    Mesh A = compas::trimesh_from_vertices_and_faces(VA, FA);
    Mesh B = compas::trimesh_from_vertices_and_faces(VB, FB);
    Mesh C;

    PMP::corefine_and_compute_difference(A, B, C);

    // Result

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::trimesh_to_vertices_and_faces(C);

    return R;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> &VA,
    Eigen::Ref<const compas::RowMatrixXi> &FA,
    Eigen::Ref<const compas::RowMatrixXd> &VB,
    Eigen::Ref<const compas::RowMatrixXi> &FB)
{
    Mesh A = compas::trimesh_from_vertices_and_faces(VA, FA);
    Mesh B = compas::trimesh_from_vertices_and_faces(VB, FB);
    Mesh C;

    PMP::corefine_and_compute_intersection(A, B, C);

    // Result

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::trimesh_to_vertices_and_faces(C);

    return R;
};

void init_booleans(py::module &m)
{
    py::module submodule = m.def_submodule("booleans");

    submodule.def(
        "boolean_union",
        &pmp_boolean_union,
        py::arg("VA").noconvert(),
        py::arg("FA").noconvert(),
        py::arg("VB").noconvert(),
        py::arg("FB").noconvert());

    submodule.def(
        "boolean_difference",
        &pmp_boolean_difference,
        py::arg("VA").noconvert(),
        py::arg("FA").noconvert(),
        py::arg("VB").noconvert(),
        py::arg("FB").noconvert());

    submodule.def(
        "boolean_intersection",
        &pmp_boolean_intersection,
        py::arg("VA").noconvert(),
        py::arg("FA").noconvert(),
        py::arg("VB").noconvert(),
        py::arg("FB").noconvert());
};
