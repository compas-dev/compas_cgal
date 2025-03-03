/**
 * @file meshing.cpp
 * @brief Implementation of mesh processing operations using CGAL
 */

#include "meshing.h"
#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>

namespace PMP = CGAL::Polygon_mesh_processing;

/**
 * @brief Implementation of the remeshing algorithm
 * 
 * @param V Input vertex matrix (row-major)
 * @param F Input face matrix (row-major)
 * @param target_edge_length Target length for mesh edges
 * @param number_of_iterations Number of remeshing iterations
 * @param do_project Whether to project vertices onto the input surface
 * @return std::tuple<RowMatrixXd, RowMatrixXi> 
 *         Returns a tuple containing:
 *         - New vertex matrix after remeshing (row-major)
 *         - New face matrix after remeshing (row-major)
 */
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

    // Convert back to matrices and return
    return compas::mesh_to_vertices_and_faces(mesh);
}

/**
 * @brief Initialize the meshing submodule
 * 
 * @param m Parent module to which the meshing submodule will be added
 */
void init_meshing(nb::module_& m) {
    auto submodule = m.def_submodule("meshing");

    submodule.def(
        "remesh",
        [](Eigen::Ref<compas::RowMatrixXd> V,
           Eigen::Ref<compas::RowMatrixXi> F,
           double target_edge_length,
           unsigned int number_of_iterations = 10,
           bool do_project = true) {
            auto result = pmp_remesh(V, F, target_edge_length, number_of_iterations, do_project);
            return nb::make_tuple(std::get<0>(result), std::get<1>(result));
        },
        "Remesh a triangular mesh to achieve a target edge length",
        "V"_a,
        "F"_a,
        "target_edge_length"_a,
        "number_of_iterations"_a = 10,
        "do_project"_a = true,
        nb::rv_policy::move
    );
}
