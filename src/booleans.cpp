#include "booleans.h"

namespace PMP = CGAL::Polygon_mesh_processing;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB)
{
    compas::Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    compas::Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);
    compas::Mesh C;

    PMP::corefine_and_compute_union(A, B, C);

    // Result

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(C);

    return R;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB)
{
    compas::Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    compas::Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);
    compas::Mesh C;

    PMP::corefine_and_compute_difference(A, B, C);

    // Result

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(C);

    return R;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB)
{
    compas::Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    compas::Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);
    compas::Mesh C;

    PMP::corefine_and_compute_intersection(A, B, C);

    // Result

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(C);

    return R;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_split(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB)
{
    compas::Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    compas::Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);
    PMP::split(A, B);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(A);

    return R;
};

void init_booleans(nb::module_& m) {
    auto submodule = m.def_submodule("booleans");

    submodule.def(
        "boolean_union",
        &pmp_boolean_union,
        "Boolean Union from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    submodule.def(
        "boolean_difference",
        &pmp_boolean_difference,
        "Boolean Difference from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    submodule.def(
        "boolean_intersection",
        &pmp_boolean_intersection,
        "Boolean Intersection from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    submodule.def(
        "split",
        &pmp_split,
        "Boolean Split from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);
}