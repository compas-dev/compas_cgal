#include "reconstruction.h"
#include <CGAL/poisson_surface_reconstruction.h>
#include <CGAL/property_map.h>

#include <CGAL/remove_outliers.h>

#include <CGAL/compute_average_spacing.h>
#include <CGAL/pca_estimate_normals.h>
#include <CGAL/mst_orient_normals.h>
#include <CGAL/property_map.h>
#include <utility> // defines std::pair
#include <list>

#include <CGAL/jet_smooth_point_set.h>

#include <CGAL/Point_set_3.h>
#include <CGAL/grid_simplify_point_set.h>

typedef std::pair<compas::Point, compas::Vector> PointVectorPair;
typedef CGAL::Point_set_3<compas::Point, compas::Vector> PointSet;
typedef CGAL::Parallel_if_available_tag Concurrency_tag;

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
    compas::Polyhedron mesh;
    std::vector<PointVectorPair> points;

    for (int i = 0; i < P.rows(); i++)
    {
        points.push_back(PointVectorPair(
            compas::Point(P(i, 0), P(i, 1), P(i, 2)),
            compas::Vector(N(i, 0), N(i, 1), N(i, 2))));
    }

    double average_spacing = CGAL::compute_average_spacing<CGAL::Sequential_tag>(
        points,
        6,
        CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()));

    CGAL::poisson_surface_reconstruction_delaunay(
        points.begin(),
        points.end(),
        CGAL::First_of_pair_property_map<PointVectorPair>(),
        CGAL::Second_of_pair_property_map<PointVectorPair>(),
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
    std::vector<compas::Point> points;

    for (int i = 0; i < p; i++)
    {
        points.push_back(compas::Point(P(i, 0), P(i, 1), P(i, 2)));
    }

    const double average_spacing = CGAL::compute_average_spacing<CGAL::Sequential_tag>(points, nnnbrs);

    std::vector<compas::Point>::iterator to_remove = CGAL::remove_outliers<CGAL::Parallel_if_available_tag>(
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
    std::vector<compas::Point>(points).swap(points);

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

/**
 * @brief Reduce number of points using hierarcy simplification.
 * https://doc.cgal.org/latest/Point_set_processing_3/Point_set_processing_3_2hierarchy_simplification_example_8cpp-example.html
 *
 * @param P The points of the cloud.
 * @param spacing The scale for the average spacing.
 * @return compas::RowMatrixXd
 *
 */
compas::RowMatrixXd
pointset_reduction(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    double spacing
    )
{

    // ======================================================================
    // Convert Eigen matrix to a vector of cgal points.
    // ======================================================================
    int p = P.rows();
    std::vector<compas::Point> points;

    for (int i = 0; i < p; i++)
        points.emplace_back(P.row(i)[0], P.row(i)[1], P.row(i)[2]);

    // ======================================================================
    // Simplification by voxelization.
    // ======================================================================
    double cell_size = spacing;
    auto iterator_to_first_to_remove = CGAL::grid_simplify_point_set(points, cell_size);
    points.erase(iterator_to_first_to_remove, points.end());

    // Optional: after erase(), shrink_to_fit to trim excess capacity
    points.shrink_to_fit();

    // ======================================================================
    // Convert the vector of cgal points to an Eigen matrix.
    // ======================================================================
    std::size_t s = points.size();
    compas::RowMatrixXd smoothed_eigen_points(s, 3);

    for (std::size_t i = 0; i < s; i++)
        smoothed_eigen_points.row(i) << static_cast<double>(points[i].x()), static_cast<double>(points[i].y()), static_cast<double>(points[i].z());

    return smoothed_eigen_points;


}

/**
 * @brief Smooth a pointcloud by number of neighbors and iterations using jet_smoothing algorithm.
 * https://doc.cgal.org/4.3/Point_set_processing_3/Point_set_processing_3_2jet_smoothing_example_8cpp-example.html
 *
 * @param P The points of the cloud.
 * @param neighbors The number of nearest neighbors to consider.
 * @param iterations The number of iterations.
 * @return compas::RowMatrixXd
 *
 */
compas::RowMatrixXd
pointset_smoothing(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int neighbors,
    int iterations)
{

    // ======================================================================
    // Convert Eigen matrix to a vector of cgal points.
    // ======================================================================
    int p = P.rows();
    std::vector<compas::Point> points;

    for (int i = 0; i < p; i++)
        points.emplace_back(P.row(i)[0], P.row(i)[1], P.row(i)[2]);
        
    // ======================================================================
    // Smooth the points, default is 24.
    // ======================================================================
    for (int i = 0; i < iterations; i++)
        CGAL::jet_smooth_point_set<CGAL::Sequential_tag>(points, neighbors);

    // ======================================================================
    // Convert the vector of cgal points to an Eigen matrix
    // ======================================================================
    std::size_t s = points.size();
    compas::RowMatrixXd smoothed_eigen_points(s, 3);

    for (std::size_t i = 0; i < s; i++)
        smoothed_eigen_points.row(i) << static_cast<double>(points[i].x()), static_cast<double>(points[i].y()), static_cast<double>(points[i].z());

    return smoothed_eigen_points;

}

/**
 * @brief Estimate pointcloud normals and oriented them.
 * https://doc.cgal.org/latest/Point_set_processing_3/Point_set_processing_3_2normals_example_8cpp-example.html
 *
 * @param P The points of the cloud.
 * @param neighbors The number of nearest neighbors to consider.
 * @param erase Erase points that are not oriented properly.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
 *
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
pointset_normal_estimation(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    int neighbors,
    bool erase)
{

    // ======================================================================
    // Convert Eigen matrix to CGAL point vector pair.
    // ======================================================================
    int p = P.rows();
    std::list<PointVectorPair> points;

    for (int i = 0; i < p; i++)
        points.emplace_back(PointVectorPair(
            compas::Point(P(i, 0), P(i, 1), P(i, 2)),
            compas::Vector(0, 0, 0)
        ));


    // ===========================================================================
    // Estimates normals direction.
    // Case 1 - the radius is precomputed by the average spacing.
    // Case 2 - the normals are estimated with a fixed number of neighbors.
    // ===========================================================================
    if ( neighbors < 1 ) {

        // First compute a spacing using the K parameter
        double spacing
            = CGAL::compute_average_spacing<Concurrency_tag>
            (points, neighbors,
            CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()));

        // Then, estimate normals with a fixed radius
        CGAL::pca_estimate_normals<Concurrency_tag> (points,0, // when using a neighborhood radius, K=0 means no limit on the number of neighbors returns
                CGAL::parameters::point_map (CGAL::First_of_pair_property_map<PointVectorPair> ()).
                normal_map (CGAL::Second_of_pair_property_map<PointVectorPair> ()).
                neighbor_radius (2. * spacing)); // use 2*spacing as neighborhood radius

    } else {

        CGAL::pca_estimate_normals<Concurrency_tag>
            (points, neighbors,
                CGAL::parameters::point_map (CGAL::First_of_pair_property_map<PointVectorPair> ()).
                normal_map (CGAL::Second_of_pair_property_map<PointVectorPair> ()));
    }

    // ===========================================================================
    // Orients normals, give at least 3 points to make a plane.
    // ===========================================================================
    unsigned orientation_neighbors = (neighbors < 3) ? 3 : neighbors;
    std::list<PointVectorPair>::iterator unoriented_points_begin =
        CGAL::mst_orient_normals (points, neighbors,
            CGAL::parameters::point_map (CGAL::First_of_pair_property_map<PointVectorPair> ()).
            normal_map (CGAL::Second_of_pair_property_map<PointVectorPair> ()));

    // ===========================================================================
    // Optional: delete points with an unoriented normal.
    // ===========================================================================
    if(erase)
        points.erase (unoriented_points_begin, points.end ());

    // ===========================================================================
    // Convert CGAL normals vector pair to Eigen matrix.
    // ===========================================================================

    std::size_t s = points.size();
    compas::RowMatrixXd eigen_points(s, 3);
    compas::RowMatrixXd eigen_vectors(s, 3);

    std::size_t i = 0;
    for (const auto& e : points) {
        eigen_points.row(i) << static_cast<double>(e.first.x()), static_cast<double>(e.first.y()), static_cast<double>(e.first.z());
        eigen_vectors.row(i) << static_cast<double>(e.second.x()), static_cast<double>(e.second.y()), static_cast<double>(e.second.z());
        i++;
    }

    return std::make_tuple(eigen_points, eigen_vectors);

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

    submodule.def(
        "pointset_reduction",
        &pointset_reduction,
        pybind11::arg("P").noconvert(),
        pybind11::arg("spacing") = 1.0);

    submodule.def(
        "pointset_smoothing",
        &pointset_smoothing,
        pybind11::arg("P").noconvert(),
        pybind11::arg("neighbors") = 8,
        pybind11::arg("iterations") = 1);
    
    submodule.def(
        "pointset_normal_estimation",
        &pointset_normal_estimation,
        pybind11::arg("P").noconvert(),
        pybind11::arg("neighbors") = 8,
        pybind11::arg("erase") = true);
};
