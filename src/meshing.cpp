#include "meshing.h"

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_remesh(
    Eigen::Ref<compas::RowMatrixXd> vertices_a,
    Eigen::Ref<compas::RowMatrixXi> faces_a,
    double target_edge_length,
    unsigned int number_of_iterations,
    bool do_project)
{
    // Convert input matrices to CGAL mesh
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);

    // Perform isotropic remeshing
    CGAL::Polygon_mesh_processing::isotropic_remeshing(
        faces(mesh_a),
        target_edge_length,
        mesh_a,
        CGAL::Polygon_mesh_processing::parameters::number_of_iterations(number_of_iterations)
                       .do_project(do_project));

    // Clean up the mesh
    mesh_a.collect_garbage();

    // Convert back to matrices - compiler will use RVO automatically
    return compas::mesh_to_vertices_and_faces(mesh_a);
}

void init_meshing(nb::module_& m) {
    auto submodule = m.def_submodule("meshing");

    submodule.def(
        "remesh",
        &pmp_remesh,
        "Remesh a triangular mesh to achieve a target edge length",
        "vertices_a"_a,
        "faces_a"_a,
        "target_edge_length"_a,
        "number_of_iterations"_a = 10,
        "do_project"_a = true
    );
}
