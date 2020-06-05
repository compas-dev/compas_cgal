#include "slicer.h"
#include <CGAL/Polygon_mesh_slicer.h>

namespace py = pybind11;


compas::RowMatrixXd pmp_slice_mesh(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    compas::RowMatrixXd point,
    compas::RowMatrixXd normal)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    Kernel::Plane_3 plane = Kernel::Plane_3(
        Kernel::Point_3(point(0, 0), point(0, 1), point(0, 2)),
        Kernel::Vector_3(normal(0, 0), normal(0, 1), normal(0, 2)));

    CGAL::Polygon_mesh_slicer<Mesh, Kernel> slicer(mesh);
    Polylines polylines;

    slicer(plane, std::back_inserter(polylines));

    // std::cout << "The slicer intersects " << polylines.size() << " polylines.";

    compas::RowMatrixXd R = compas::result_from_polylines(polylines);

    return R;
};


void init_slicer(py::module & m) {
    py::module submodule = m.def_submodule("slicer");

    submodule.def(
        "slice_mesh",
        &pmp_slice_mesh,
        py::arg("V").noconvert(),
        py::arg("F").noconvert(),
        py::arg("point").noconvert(),
        py::arg("normal").noconvert()
    );
}
