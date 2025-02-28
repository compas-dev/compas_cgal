#include "meshing.h"
#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>


namespace PMP = CGAL::Polygon_mesh_processing;


std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_remesh(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & F,
    double target_edge_length,
    unsigned int number_of_iterations,
    bool do_project)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    // protect sharp features

    // typedef boost::property_map<compas::Mesh, CGAL::edge_is_feature_t>::type EIFMap;
    // EIFMap eif = get(CGAL::edge_is_feature, mesh);
    // PMP::detect_sharp_edges(mesh, 60, eif);

    PMP::isotropic_remeshing(
        faces(mesh),
        target_edge_length,
        mesh,
        PMP::parameters::number_of_iterations(number_of_iterations).do_project(do_project));

    mesh.collect_garbage();

    // Result
    // compas::Result R = compas::result_from_mesh(mesh);
    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::mesh_to_vertices_and_faces(mesh);

    return R;
};


void init_meshing(nb::module_ & m){
    auto submodule = m.def_submodule("meshing");

    submodule.def(
        "remesh",
        &pmp_remesh,
        "V"_a,
        "F"_a,
        "target_edge_length"_a,
        "number_of_iterations"_a = 10,
        "do_project"_a = true,
        "Remesh a triangular mesh with target edge length."
    );
    
}