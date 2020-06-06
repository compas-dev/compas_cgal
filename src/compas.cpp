#include <compas.h>

#include <pybind11/pybind11.h>

namespace py = pybind11;

// construct a CGAL surface mesh
// from vertices and faces
// contained in nx3 and fx3 eigen matrices
// using the Exact Predicates Exact Constructions Kernel
Mesh compas::mesh_from_vertices_and_faces(
    const compas::RowMatrixXd & V,
    const compas::RowMatrixXi & F)
{
    int v = V.rows();
    int f = F.rows();

    Mesh mesh;
    std::vector<Mesh::Vertex_index> index_descriptor(v);

    for (int i=0; i < v; i++) {
        index_descriptor[i] = mesh.add_vertex(Kernel::Point_3(V(i, 0), V(i, 1), V(i, 2)));
    }

    Mesh::Vertex_index a;
    Mesh::Vertex_index b;
    Mesh::Vertex_index c;

    for (int i=0; i < f; i++) {
        a = index_descriptor[F(i, 0)];
        b = index_descriptor[F(i, 1)];
        c = index_descriptor[F(i, 2)];
        mesh.add_face(a, b, c);
    }

    return mesh;
}

// TODO: rename to ResultMesh
// construct a result mesh
// from a CGAL surface mesh
compas::Result compas::result_from_mesh(const Mesh & mesh)
{
    int v = mesh.number_of_vertices();
    int f = mesh.number_of_faces();


    compas::Result R;
    compas::RowMatrixXd R_vertices(v, 3);
    compas::RowMatrixXi R_faces(f, 3);

    Mesh::Property_map<Mesh::Vertex_index, Kernel::Point_3> location = mesh.points();

    for (Mesh::Vertex_index vd : mesh.vertices()) {
        R_vertices(vd, 0) = (double) location[vd][0];
        R_vertices(vd, 1) = (double) location[vd][1];
        R_vertices(vd, 2) = (double) location[vd][2];
    }

    for (Mesh::Face_index fd : mesh.faces()) {
        int i = 0;
        for (Mesh::Vertex_index vd : vertices_around_face(mesh.halfedge(fd), mesh)) {
            R_faces(fd, i) = (int) vd;
            i++;
        }
    }

    R.vertices = R_vertices;
    R.faces = R_faces;

    return R;
}

// construct a set of result polylines
// from CGAL polylines
// the CGAL polylines are a list of vectors of points
std::vector<compas::RowMatrixXd, Eigen::aligned_allocator<compas::RowMatrixXd>>
compas::result_from_polylines(const Polylines & polylines)
{
    std::vector<compas::RowMatrixXd, Eigen::aligned_allocator<compas::RowMatrixXd>> pointsets;
    compas::RowMatrixXd points;
    int n;

    for (auto i = polylines.begin(); i != polylines.end(); i++){
        const Polyline & poly = *i;
        n = poly.size();
        points(n, 3);

        for(int j = 0; j < n; j++){
            points(j, 0) = (double) poly[j].x();
            points(j, 1) = (double) poly[j].y();
            points(j, 2) = (double) poly[j].z();
        }

        pointsets.push_back(points);
    }

    return pointsets;
}
