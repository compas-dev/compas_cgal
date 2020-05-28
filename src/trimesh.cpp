#include <trimesh.h>


TriMesh trimesh_from_vertices_and_faces(const compas::RowMatrixXd & V, const compas::RowMatrixXi & F) {

    int v = V.rows();
    int f = F.rows();

    TriMesh mesh;
    std::vector<TriMesh::Vertex_index> index_descriptor(v);

    for (int i=0; i < v; i++) {
        index_descriptor[i] = mesh.add_vertex(K::Point_3(V(i, 0), V(i, 1), V(i, 2)));
    }

    TriMesh::Vertex_index a;
    TriMesh::Vertex_index b;
    TriMesh::Vertex_index c;

    for (int i=0; i < f; i++) {
        a = index_descriptor[F(i, 0)];
        b = index_descriptor[F(i, 1)];
        c = index_descriptor[F(i, 2)];
        mesh.add_face(a, b, c);
    }

    return mesh;
}
