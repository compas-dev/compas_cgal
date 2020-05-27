#include "meshing.h"


void pmp_refine(compas::RowMatrixXd V, compas::RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


void pmp_fair(compas::RowMatrixXd V, compas::RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


void pmp_triangulate(compas::RowMatrixXd V, compas::RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


void pmp_remesh(compas::RowMatrixXd V, compas::RowMatrixXi F) {

    TriMesh m = trimesh_from_vertices_and_faces(V, F);
}


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
