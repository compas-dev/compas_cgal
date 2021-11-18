#include "meshing.h"

#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>

namespace PMP = CGAL::Polygon_mesh_processing;
namespace params = PMP::parameters;
namespace py = pybind11;

using edge_descriptor = boost::graph_traits<Mesh>::edge_descriptor;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_remesh(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & F,
    double target_edge_length,
    unsigned int number_of_iterations,
    bool do_project)
{
    Mesh mesh = compas::trimesh_from_vertices_and_faces(V, F);

    // protect sharp features

    typedef boost::property_map<Mesh, CGAL::edge_is_feature_t>::type EIFMap;
    EIFMap eif = get(CGAL::edge_is_feature, mesh);
    PMP::detect_sharp_edges(mesh, 60, eif);

    std::vector<edge_descriptor> features;
    for (edge_descriptor e : edges(mesh)) {
        if (get(eif, e)) {
            features.push_back(e);
        }
    }

    // split long edges of the protected features

    PMP::split_long_edges(features, target_edge_length, mesh);

    // protect the border
    // protect constrained edges
    // protect constrained vertices

    // remesh

    PMP::isotropic_remeshing(
        faces(mesh),
        target_edge_length,
        mesh,
        params::number_of_iterations(number_of_iterations)
               .do_project(do_project)
               .edge_is_constrained_map(eif));

    // clean up

    mesh.collect_garbage();

    // Result

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> R = compas::trimesh_to_vertices_and_faces(mesh);
    return R;
};

void init_meshing(py::module & m) {
    py::module submodule = m.def_submodule("meshing");

    submodule.def(
        "remesh",
        &pmp_remesh,
        py::arg("V").noconvert(),
        py::arg("F").noconvert(),
        py::arg("target_edge_length"),
        py::arg("number_of_iterations") = 10,
        py::arg("do_project") = true
    );
};
