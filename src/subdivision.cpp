#include "subdivision.h"

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_catmullclark(
    compas::RowMatrixXd vertices,
    std::vector<std::vector<int>> faces,
    unsigned int num_iterations)
{
    compas::Mesh mesh = compas::ngon_from_vertices_and_faces(vertices, faces);
    CGAL::Subdivision_method_3::CatmullClark_subdivision(mesh, CGAL::parameters::number_of_iterations(num_iterations));
    mesh.collect_garbage();
    return compas::quadmesh_to_vertices_and_faces(mesh);
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_loop(
    compas::RowMatrixXd vertices,
    compas::RowMatrixXi faces,
    unsigned int num_iterations)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    CGAL::Subdivision_method_3::Loop_subdivision(mesh, CGAL::parameters::number_of_iterations(num_iterations));
    mesh.collect_garbage();
    return compas::mesh_to_vertices_and_faces(mesh);
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_sqrt3(
    compas::RowMatrixXd vertices,
    compas::RowMatrixXi faces,
    unsigned int num_iterations)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    CGAL::Subdivision_method_3::Sqrt3_subdivision(mesh, CGAL::parameters::number_of_iterations(num_iterations));
    mesh.collect_garbage();
    return compas::mesh_to_vertices_and_faces(mesh);
}

void init_subdivision(nb::module_& m) {
    auto submodule = m.def_submodule("subdivision");

    submodule.def(
        "subd_catmullclark",
        &subd_catmullclark,
        "Catmull-Clark subdivision of a polygonal mesh.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx3, float64)\n"
        "faces : list\n"
        "    List of face vertex indices (list of lists)\n"
        "num_iterations : int\n"
        "    Number of subdivision steps\n"
        "\n"
        "Returns\n"
        "-------\n"
        "tuple\n"
        "    - Matrix of subdivided vertex positions (Mx3, float64)\n"
        "    - Matrix of subdivided face vertex indices (Px4, int32)",
        "vertices"_a,
        "faces"_a,
        "num_iterations"_a);

    submodule.def(
        "subd_loop",
        &subd_loop,
        "Loop subdivision of a triangular mesh.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx3, float64)\n"
        "faces : array-like\n"
        "    Matrix of face vertex indices (Mx3, int32)\n"
        "num_iterations : int\n"
        "    Number of subdivision steps\n"
        "\n"
        "Returns\n"
        "-------\n"
        "tuple\n"
        "    - Matrix of subdivided vertex positions (Px3, float64)\n"
        "    - Matrix of subdivided face vertex indices (Qx3, int32)",
        "vertices"_a,
        "faces"_a,
        "num_iterations"_a);

    submodule.def(
        "subd_sqrt3",
        &subd_sqrt3,
        "Sqrt3 subdivision of a triangular mesh.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx3, float64)\n"
        "faces : array-like\n"
        "    Matrix of face vertex indices (Mx3, int32)\n"
        "num_iterations : int\n"
        "    Number of subdivision steps\n"
        "\n"
        "Returns\n"
        "-------\n"
        "tuple\n"
        "    - Matrix of subdivided vertex positions (Px3, float64)\n"
        "    - Matrix of subdivided face vertex indices (Qx3, int32)",
        "vertices"_a,
        "faces"_a,
        "num_iterations"_a);
}
