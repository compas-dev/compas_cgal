#include "meshing.h"

#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>

namespace PMP = CGAL::Polygon_mesh_processing;
namespace params = PMP::parameters;
namespace py = pybind11;


compas::Result
pmp_remesh(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & F,
    double target_edge_length,
    unsigned int number_of_iterations,
    bool do_project)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    // protect sharp features

    // typedef boost::property_map<Mesh, CGAL::edge_is_feature_t>::type EIFMap;
    // EIFMap eif = get(CGAL::edge_is_feature, mesh);
    // PMP::detect_sharp_edges(mesh, 60, eif);

    PMP::isotropic_remeshing(
        faces(mesh),
        target_edge_length,
        mesh,
        params::number_of_iterations(number_of_iterations).do_project(do_project));

    mesh.collect_garbage();

    // Result
    compas::Result R = compas::result_from_mesh(mesh);

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
