#include "intersections.h"

std::vector<compas::RowMatrixXd>
pmp_intersection_mesh_mesh(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);

    compas::Polylines polylines;
    CGAL::Polygon_mesh_processing::surface_intersection(mesh_a, mesh_b, std::back_inserter(polylines));

    std::vector<compas::RowMatrixXd> result = compas::polylines_to_lists_of_points(polylines);
    return result;
}

void init_intersections(nb::module_& m) {
    auto submodule = m.def_submodule("intersections");

    submodule.def(
        "intersection_mesh_mesh",
        &pmp_intersection_mesh_mesh,
        "Compute intersection polylines between two triangle meshes.",
        "vertices_a"_a,
        "faces_a"_a,
        "vertices_b"_a,
        "faces_b"_a);
}