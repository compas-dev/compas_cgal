#include "slicer.h"

std::vector<compas::RowMatrixXd>
pmp_slice_mesh(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    Eigen::Ref<const compas::RowMatrixXd> points,
    Eigen::Ref<const compas::RowMatrixXd> normals)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);

    CGAL::Polygon_mesh_slicer<compas::Mesh, compas::Kernel> slicer(mesh);
    compas::Polylines polylines;
    std::back_insert_iterator<compas::Polylines> slices(polylines);

    int num_planes = points.rows();

    for (int i = 0; i < num_planes; i++)
    {
        compas::Kernel::Plane_3 plane = compas::Kernel::Plane_3(
            compas::Kernel::Point_3(points(i, 0), points(i, 1), points(i, 2)),
            compas::Kernel::Vector_3(normals(i, 0), normals(i, 1), normals(i, 2)));

        slicer(plane, slices);
    }

    std::vector<compas::RowMatrixXd> result = compas::polylines_to_lists_of_points(polylines);
    return result;
};

void init_slicer(nb::module_& m) {
    auto submodule = m.def_submodule("slicer");

    submodule.def(
        "slice_mesh",
        &pmp_slice_mesh,
        "Slice a mesh with a set of planes defined by points and normals.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx3, float64)\n"
        "faces : array-like\n"
        "    Matrix of face indices (Mx3, int32)\n"
        "points : array-like\n"
        "    Matrix of plane points (Kx3, float64)\n"
        "normals : array-like\n"
        "    Matrix of plane normals (Kx3, float64)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of polylines, each represented as a matrix of points (Px3, float64)",
        "vertices"_a,
        "faces"_a,
        "points"_a,
        "normals"_a);
}
