#include <compas.h>
#include <compas_cgal/trimesh.h>

#include <pybind11/pybind11.h>

#include <CGAL/Polygon_mesh_processing/refine.h>
#include <CGAL/Polygon_mesh_processing/fair.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/remesh.h>


namespace PMP = CGAL::Polygon_mesh_processing;
namespace py = pybind11;


// =======================
// Functions
// =======================

void pmp_refine(RowMatrixXd V, RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


void pmp_fair(RowMatrixXd V, RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


void pmp_triangulate(RowMatrixXd V, RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


void pmp_remesh(RowMatrixXd V, RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


// =======================
// PyBind11
// =======================

void init_meshing(py::module & m) {
    py::module submodule = m.def_submodule("meshing");

    submodule.def(
        "refine",
        &pmp_refine,
        py::arg("V").noconvert(),
        py::arg("F").noconvert()
    );

    submodule.def(
        "fair",
        &pmp_fair,
        py::arg("V").noconvert(),
        py::arg("F").noconvert()
    );

    submodule.def(
        "triangulate",
        &pmp_triangulate,
        py::arg("V").noconvert(),
        py::arg("F").noconvert()
    );

    submodule.def(
        "remesh",
        &pmp_remesh,
        py::arg("V").noconvert(),
        py::arg("F").noconvert()
    );
}
