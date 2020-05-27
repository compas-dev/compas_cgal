#include <trimesh.h>


TriMesh trimesh_from_vertices_and_faces(compas::RowMatrixXd V, compas::RowMatrixXi F) {

    int v = V.rows();
    TriMesh m;
    TriMesh::Vertex_index index_descriptor[v];

    for (int i=0; i < V.rows(); i++) {
        index_descriptor[i] = m.add_vertex(Point_3(V(i, 0), V(i, 1), V(i, 2)));
    }

    TriMesh::Vertex_index a;
    TriMesh::Vertex_index b;
    TriMesh::Vertex_index c;

    for (int i=0; i < F.rows(); i++) {
        a = index_descriptor[F(i, 0)];
        b = index_descriptor[F(i, 1)];
        c = index_descriptor[F(i, 2)];
        m.add_face(a, b, c);
    }

    return m;
}
