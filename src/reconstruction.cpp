#include "reconstruction.h"
#include <CGAL/poisson_surface_reconstruction.h>

typedef std::pair<Point, Vector> PwN;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
poisson_surface_reconstruction(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    Eigen::Ref<const compas::RowMatrixXd> &N)
{
    Polyhedron mesh;
    std::vector<PwN> points;

    for (int i = 0; i < P.rows(); i++)
    {
        points.push_back(PwN(
            Point(P(i, 0), P(i, 1), P(i, 2)),
            Vector(N(i, 0), N(i, 1), N(i, 2))));
    }

    double average_spacing = CGAL::compute_average_spacing<CGAL::Sequential_tag>(
        points,
        6,
        CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PwN>()));

    CGAL::poisson_surface_reconstruction_delaunay(
        points.begin(),
        points.end(),
        CGAL::First_of_pair_property_map<PwN>(),
        CGAL::Second_of_pair_property_map<PwN>(),
        mesh,
        average_spacing);

    return compas::polyhedron_to_vertices_and_faces(mesh);
}

// ===========================================================================
// PyBind11
// ===========================================================================

void init_reconstruction(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("reconstruction");

    submodule.def(
        "poisson_surface_reconstruction",
        &poisson_surface_reconstruction,
        pybind11::arg("P").noconvert(),
        pybind11::arg("N").noconvert());
};
