#include "slicer.h"
#include <CGAL/Polygon_mesh_slicer.h>

namespace py = pybind11;


compas::RowMatrixXd pmp_slice_mesh(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    compas::RowMatrixXd P,
    compas::RowMatrixXd N)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    CGAL::Polygon_mesh_slicer<Mesh, Kernel> slicer(mesh);
    Polylines polylines;
    Kernel::Plane_3 plane;

    int number_of_planes = P.rows();

    for (int i = 0; i < number_of_planes; i++){
        plane = Kernel::Plane_3(
            Kernel::Point_3(P(0, 0), P(0, 1), P(0, 2)),
            Kernel::Vector_3(N(0, 0), N(0, 1), N(0, 2)));

        slicer(plane, std::back_inserter(polylines));
    }

    // std::vector<compas::RowMatrixXd> result = compas::result_from_polylines(polylines);
    // return result;

    // this avoids the segmentation fault
    // but returns only one of the results

    Polyline poly = polylines.front();
    int n = poly.size();
    compas::RowMatrixXd points(n, 3);

    for(int j = 0; j < n; j++){
        points(j, 0) = (double) poly[j].x();
        points(j, 1) = (double) poly[j].y();
        points(j, 2) = (double) poly[j].z();
    }

    return points;
};


void init_slicer(py::module & m) {
    py::module submodule = m.def_submodule("slicer");

    submodule.def(
        "slice_mesh",
        &pmp_slice_mesh,
        py::arg("V").noconvert(),
        py::arg("F").noconvert(),
        py::arg("P").noconvert(),
        py::arg("N").noconvert()
    );
}
