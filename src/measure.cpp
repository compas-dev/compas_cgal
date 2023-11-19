#include "measure.h"
#include <CGAL/Polygon_mesh_processing/measure.h>
#include <CGAL/Point_3.h>

namespace PMP = CGAL::Polygon_mesh_processing;

double
pmp_area(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    Eigen::Ref<const compas::RowMatrixXi> &F)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    double area = PMP::area(mesh);

    return area;
};

double
pmp_volume(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    Eigen::Ref<const compas::RowMatrixXi> &F)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    double volume = PMP::volume(mesh);

    return volume;
};

std::vector<double>
pmp_centroid(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    Eigen::Ref<const compas::RowMatrixXi> &F)
{
    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    Kernel::Point_3 centroid = PMP::centroid(mesh);

    return std::vector<double>{centroid.x(), centroid.y(), centroid.z()};
};

void init_measure(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("measure");

    submodule.def(
        "area",
        &pmp_area,
        pybind11::arg("V").noconvert(),
        pybind11::arg("F").noconvert());

    submodule.def(
        "volume",
        &pmp_volume,
        pybind11::arg("V").noconvert(),
        pybind11::arg("F").noconvert());

    submodule.def(
        "centroid",
        &pmp_centroid,
        pybind11::arg("V").noconvert(),
        pybind11::arg("F").noconvert());
};
