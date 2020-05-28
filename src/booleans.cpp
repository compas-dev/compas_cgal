#include "booleans.h"


Mesh mesh_from_vertices_and_faces(compas::RowMatrixXd V, compas::RowMatrixXi F) {

    int v = V.rows();
    int f = F.rows();
    Mesh m;
    Mesh::Vertex_index index_descriptor[v];

    for (int i=0; i < v; i++) {
        index_descriptor[i] = m.add_vertex(K::Point_3(V(i, 0), V(i, 1), V(i, 2)));
    }

    Mesh::Vertex_index a;
    Mesh::Vertex_index b;
    Mesh::Vertex_index c;

    for (int i=0; i < f; i++) {
        a = index_descriptor[F(i, 0)];
        b = index_descriptor[F(i, 1)];
        c = index_descriptor[F(i, 2)];
        m.add_face(a, b, c);
    }

    return m;
}


compas::Mesh pmp_boolean_union(compas::RowMatrixXd VA, compas::RowMatrixXi FA, compas::RowMatrixXd VB, compas::RowMatrixXi FB) {

    Mesh A = mesh_from_vertices_and_faces(VA, FA);
    Mesh B = mesh_from_vertices_and_faces(VB, FB);
    Mesh C;

    PMP::corefine_and_compute_union(A, B, C);

    int v = C.number_of_vertices();
    int f = C.number_of_faces();

    compas::Mesh M;
    compas::RowMatrixXd VC(v, 3);
    compas::RowMatrixXi FC(f, 3);

    Mesh::Property_map<Mesh::Vertex_index, K::Point_3> location = C.points();

    for (Mesh::Vertex_index vd : C.vertices()) {
        VC(vd, 0) = location[vd][0];
        VC(vd, 1) = location[vd][1];
        VC(vd, 2) = location[vd][2];
    }

    for (Mesh::Face_index fd : C.faces()) {
        int i = 0;
        for (Mesh::Vertex_index vd : vertices_around_face(C.halfedge(fd), C)) {
            FC(fd, i) = vd;
            i++;
        }
    }

    M.vertices = VC;
    M.faces = FC;

    return M;
}


void init_booleans(py::module & m) {
    py::module submodule = m.def_submodule("booleans");

    submodule.def(
        "boolean_union",
        &pmp_boolean_union,
        py::arg("VA").noconvert(),
        py::arg("FA").noconvert(),
        py::arg("VB").noconvert(),
        py::arg("FB").noconvert()
    );

    py::class_<compas::Mesh>(m, "Mesh")
    	.def_readonly("vertices", &compas::Mesh::vertices)
    	.def_readonly("faces", &compas::Mesh::faces);
}
