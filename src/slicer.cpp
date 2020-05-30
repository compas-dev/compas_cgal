#include "slicer.h"


SliceMesh slicemesh_from_vertices_and_faces(const compas::RowMatrixXd & V, const compas::RowMatrixXi & F) {

    int v = V.rows();
    int f = F.rows();

    SliceMesh mesh;
    std::vector<SliceMesh::Vertex_index> index_descriptor(v);

    for (int i=0; i < v; i++) {
        index_descriptor[i] = mesh.add_vertex(K::Point_3(V(i, 0), V(i, 1), V(i, 2)));
    }

    SliceMesh::Vertex_index a;
    SliceMesh::Vertex_index b;
    SliceMesh::Vertex_index c;

    for (int i=0; i < f; i++) {
        a = index_descriptor[F(i, 0)];
        b = index_descriptor[F(i, 1)];
        c = index_descriptor[F(i, 2)];
        mesh.add_face(a, b, c);
    }

    return mesh;
}


void pmp_slice_mesh(compas::RowMatrixXd V, compas::RowMatrixXi F, compas::RowMatrixXd P, compas::RowMatrixXd N) {

    SliceMesh mesh = slicemesh_from_vertices_and_faces(V, F);

    K::Plane_3 plane = K::Plane_3(K::Point_3(P(0, 0), P(0, 1), P(0, 2)),
                                  K::Vector_3(N(0, 0), N(0, 1), N(0, 2)));

    CGAL::Polygon_mesh_slicer<SliceMesh, K> slicer(mesh);
    Polylines polylines;

    slicer(plane, std::back_inserter(polylines));

    std::cout << "The slicer intersects " << polylines.size() << " polylines.";

}


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
