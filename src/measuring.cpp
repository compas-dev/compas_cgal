#include "measuring.h"

#include <CGAL/Polygon_mesh_processing/measure.h>

namespace PMP = CGAL::Polygon_mesh_processing;
namespace py = pybind11;

double
pmp_voluming(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & F)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    double volume = PMP::volume(mesh);

    return volume;
};

void init_measuring(py::module & m) {
    py::module submodule = m.def_submodule("measuring");

    submodule.def(
        "voluming",
        &pmp_voluming,
        py::arg("V").noconvert(),
        py::arg("F").noconvert()
    );
};
