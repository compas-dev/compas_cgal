#include "meshing.h"


Mesh mesh1_from_vertices_and_faces(const compas::RowMatrixXd & V, const compas::RowMatrixXi & F) {

    int v = V.rows();
    int f = F.rows();

    Mesh m;
    std::vector<Mesh::Vertex_index> index_descriptor(v);

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


compas::Mesh pmp_remesh(compas::RowMatrixXd V, compas::RowMatrixXi F, double target_edge_length, unsigned int niter) {

    Mesh mesh = mesh1_from_vertices_and_faces(V, F);

    PMP::isotropic_remeshing(
        mesh.faces(),
        target_edge_length,
        mesh,
        params::number_of_iterations(niter));

    // Result

    int v = mesh.number_of_vertices();
    int f = mesh.number_of_faces();

    compas::Mesh R;
    compas::RowMatrixXd RV(v, 3);
    compas::RowMatrixXi RF(f, 3);

    Mesh::Property_map<Mesh::Vertex_index, K::Point_3> location = mesh.points();

    for (Mesh::Vertex_index vd : mesh.vertices()) {
        RV(vd, 0) = location[vd][0];
        RV(vd, 1) = location[vd][1];
        RV(vd, 2) = location[vd][2];
    }

    for (Mesh::Face_index fd : mesh.faces()) {
        int i = 0;
        for (Mesh::Vertex_index vd : vertices_around_face(mesh.halfedge(fd), mesh)) {
            RF(fd, i) = vd;
            i++;
        }
    }

    R.vertices = RV;
    R.faces = RF;

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
