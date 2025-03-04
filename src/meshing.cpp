/**
 * @file meshing.cpp
 * @brief Implementation of mesh processing operations using CGAL
 */

#include "meshing.h"
#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>

namespace PMP = CGAL::Polygon_mesh_processing;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_remesh(
    Eigen::Ref<compas::RowMatrixXd> V,
    Eigen::Ref<compas::RowMatrixXi> F,
    double target_edge_length,
    unsigned int number_of_iterations,
    bool do_project)
{
    // Convert input matrices to CGAL mesh
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    // Perform isotropic remeshing
    PMP::isotropic_remeshing(
        faces(mesh),
        target_edge_length,
        mesh,
        PMP::parameters::number_of_iterations(number_of_iterations)
                       .do_project(do_project));

    // Clean up the mesh
    mesh.collect_garbage();

    // Convert back to matrices - compiler will use RVO automatically
    return compas::mesh_to_vertices_and_faces(mesh);
}

void init_meshing(nb::module_& m) {
    auto submodule = m.def_submodule("meshing");

    submodule.def(
        "remesh",
        &pmp_remesh,
        "Remesh a triangular mesh to achieve a target edge length",
        "V"_a,
        "F"_a,
        "target_edge_length"_a,
        "number_of_iterations"_a = 10,
        "do_project"_a = true
    );
}
