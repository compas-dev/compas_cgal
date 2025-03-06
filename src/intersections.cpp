#include "intersections.h"

namespace PMP = CGAL::Polygon_mesh_processing;

std::vector<compas::RowMatrixXd>
pmp_intersection_mesh_mesh(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB)
{
    compas::Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    compas::Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);

    compas::Polylines polylines;

    PMP::surface_intersection(A, B, std::back_inserter(polylines));

    std::vector<compas::RowMatrixXd> result = compas::polylines_to_lists_of_points(polylines);

    return result;
};


void init_intersections(nb::module_& m) {
    auto submodule = m.def_submodule("intersections");

    submodule.def(
        "intersection_mesh_mesh",
        &pmp_intersection_mesh_mesh,
        "Intersection from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

}