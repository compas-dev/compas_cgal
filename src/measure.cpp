#include "measure.h"

double
pmp_area(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    double area = CGAL::Polygon_mesh_processing::area(mesh);
    return area;
}

double
pmp_volume(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    double volume = CGAL::Polygon_mesh_processing::volume(mesh);
    int a = 0;
    return volume;
}

std::vector<double>
pmp_centroid(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    compas::Kernel::Point_3 centroid = CGAL::Polygon_mesh_processing::centroid(mesh);
    return std::vector<double>{centroid.x(), centroid.y(), centroid.z()};
}


NB_MODULE(_measure, m) {


    m.def(
        "area",
        &pmp_area,
        "Calculate the surface area of a mesh",
        "vertices"_a,
        "faces"_a);

    m.def(
        "volume",
        &pmp_volume,
        "Calculate the volume enclosed by a mesh",
        "vertices"_a,
        "faces"_a);

    m.def(
        "centroid",
        &pmp_centroid,
        "Calculate the centroid of a mesh",
        "vertices"_a,
        "faces"_a);
}