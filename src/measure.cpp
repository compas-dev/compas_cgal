#include "measure.h"

#include <CGAL/Polygon_mesh_processing/measure.h>

namespace PMP = CGAL::Polygon_mesh_processing;
namespace py = pybind11;

double
pmp_volume(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & F)
{
    Mesh mesh = compas::trimesh_from_vertices_and_faces(V, F);

    double volume = PMP::volume(mesh);

    return volume;
};

void init_measure(py::module & m) {
    py::module submodule = m.def_submodule("measure");

    submodule.def(
        "volume",
        &pmp_volume,
        py::arg("V").noconvert(),
        py::arg("F").noconvert()
    );
};
