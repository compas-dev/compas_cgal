#include "measure.h"
#include <CGAL/Polygon_mesh_processing/measure.h>
#include <CGAL/Point_3.h>

namespace PMP = CGAL::Polygon_mesh_processing;

double
pmp_area(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    double area = PMP::area(mesh);

    return area;
};

double
pmp_volume(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    double volume = PMP::volume(mesh);

    return volume;
};

std::vector<double>
pmp_centroid(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    compas::Kernel::Point_3 centroid = PMP::centroid(mesh);

    return std::vector<double>{centroid.x(), centroid.y(), centroid.z()};
};

void init_measure(nb::module_& m) {
    auto submodule = m.def_submodule("measure");

    submodule.def(
        "area",
        &pmp_area,
        "Calculate the surface area of a mesh",
        "V"_a,
        "F"_a);

    submodule.def(
        "volume",
        &pmp_volume,
        "Calculate the volume enclosed by a mesh",
        "V"_a,
        "F"_a);

    submodule.def(
        "centroid",
        &pmp_centroid,
        "Calculate the centroid of a mesh",
        "V"_a,
        "F"_a);

}