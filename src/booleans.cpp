#include "booleans.h"

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    compas::Mesh mesh_out;

    CGAL::Polygon_mesh_processing::corefine_and_compute_union(mesh_a, mesh_b, mesh_out);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = compas::mesh_to_vertices_and_faces(mesh_out);
    return result;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    compas::Mesh mesh_out;

    CGAL::Polygon_mesh_processing::corefine_and_compute_difference(mesh_a, mesh_b, mesh_out);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = compas::mesh_to_vertices_and_faces(mesh_out);
    return result;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    compas::Mesh mesh_out;

    CGAL::Polygon_mesh_processing::corefine_and_compute_intersection(mesh_a, mesh_b, mesh_out);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = compas::mesh_to_vertices_and_faces(mesh_out);
    return result;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_split(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    CGAL::Polygon_mesh_processing::split(mesh_a, mesh_b);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = compas::mesh_to_vertices_and_faces(mesh_a);
    return result;
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