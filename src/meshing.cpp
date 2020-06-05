#include "meshing.h"
#include <CGAL/Polygon_mesh_processing/remesh.h>

namespace PMP = CGAL::Polygon_mesh_processing;
namespace params = PMP::parameters;
namespace py = pybind11;


compas::Result pmp_remesh(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    double target_edge_length,
    unsigned int niter)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    // PMP::isotropic_remeshing(
    //     faces(mesh),
    //     target_edge_length,
    //     mesh,
    //     params::number_of_iterations(niter));

    // Result

    compas::Result R = compas::result_from_mesh(mesh);

    return R;
}


void init_meshing(py::module & m) {
    py::module submodule = m.def_submodule("meshing");

    submodule.def(
        "remesh",
        &pmp_remesh,
        py::arg("V").noconvert(),
        py::arg("F").noconvert(),
        py::arg("target_edge_length"),
        py::arg("niter")
    );
}
