#include "reconstruction.h"
#include <CGAL/poisson_surface_reconstruction.h>
#include <CGAL/property_map.h>
#include <CGAL/remove_outliers.h>

typedef std::pair<Point, Vector> PwN;

/**
 * @brief Perform Poisson surface reconstruction on an oriented pointcloud with normals.
 *
 * @param P The points of the cloud.
 * @param N The normals of the points.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
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

/**
 * @brief Remove outliers from a pointcloud.
 *
 * @param P The points of the cloud.
 * @param nnnbrs The number of nearest neighbors to consider.
 * @param radius The radius of the sphere to consider as a multiplication factor of the average spacing.
 * @return compas::RowMatrixXd
 *
 */
compas::RowMatrixXd
pointset_outlier_removal(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int nnnbrs,
    double radius)
{
    int p = P.rows();
    std::vector<Point> points;

    for (int i = 0; i < p; i++)
    {
        points.push_back(Point(P(i, 0), P(i, 1), P(i, 2)));
    }

    const double average_spacing = CGAL::compute_average_spacing<CGAL::Sequential_tag>(points, nnnbrs);

    std::vector<Point>::iterator to_remove = CGAL::remove_outliers<CGAL::Parallel_if_available_tag>(
        points,
        nnnbrs,
        CGAL::parameters::threshold_percent(100.).threshold_distance(radius * average_spacing));

    // std::vector<std::size_t> outliers;
    // for (it; it != points.end(); ++it)
    // {
    //     std::size_t index = std::distance(points.begin(), it);
    //     outliers.push_back(index);
    // }

    // return outliers;

    points.erase(to_remove, points.end());
    std::vector<Point>(points).swap(points);

    std::size_t s = points.size();
    compas::RowMatrixXd result(s, 3);

    for (int i = 0; i < s; i++)
    {
        result(i, 0) = (double)points[i].x();
        result(i, 1) = (double)points[i].y();
        result(i, 2) = (double)points[i].z();
    }

    return result;
}

void pointset_reduction(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    double radius)
{
    // TODO
}

void pointset_smoothing(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int k,
    double radius)
{
    // TODO
}

void pointset_normal_esitmation(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int k,
    double radius)
{
    // TODO
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

    submodule.def(
        "pointset_outlier_removal",
        &pointset_outlier_removal,
        pybind11::arg("P").noconvert(),
        pybind11::arg("nnnbrs") = 10,
        pybind11::arg("radius") = 1.0);
};
