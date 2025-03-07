#include "subdivision.h"


std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_catmullclark(
    compas::RowMatrixXd V,
    std::vector<std::vector<int>> faces,
    unsigned int k)
{
    compas::Mesh mesh = compas::ngon_from_vertices_and_faces(V, faces);
    CGAL::Subdivision_method_3::CatmullClark_subdivision(mesh, CGAL::parameters::number_of_iterations(k));
    mesh.collect_garbage();
    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::quadmesh_to_vertices_and_faces(mesh);
    return R;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_loop(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    unsigned int k)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);
    CGAL::Subdivision_method_3::Loop_subdivision(mesh, CGAL::parameters::number_of_iterations(k));
    mesh.collect_garbage();
    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(mesh);
    return R;
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_sqrt3(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    unsigned int k)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);
    CGAL::Subdivision_method_3::Sqrt3_subdivision(mesh, CGAL::parameters::number_of_iterations(k));
    mesh.collect_garbage();
    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(mesh);
    return R;
};

void init_subdivision(nb::module_& m) {
    auto submodule = m.def_submodule("subdivision");

    submodule.def(
        "subd_catmullclark",
        &subd_catmullclark,
        """ Catmullclark subdivision of a polygonal mesh."""
        "V"_a,
        "faces"_a,
        "k"_a);

    submodule.def(
        "subd_loop",
        &subd_loop,
        """ Loop subdivision of a polygonal mesh.""",
        "V"_a,
        "F"_a,
        "k"_a);

    submodule.def(
        "subd_sqrt3",
        &subd_sqrt3,
        """ Sqrt3 subdivision of a polygonal mesh.""",
        "V"_a,
        "F"_a,
        "k"_a);
}
