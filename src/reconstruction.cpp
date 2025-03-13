#include "reconstruction.h"

typedef std::pair<compas::Point, compas::Vector> PointVectorPair;
typedef CGAL::Point_set_3<compas::Point, compas::Vector> PointSet;
typedef CGAL::Parallel_if_available_tag ConcurrencyTag;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
poisson_surface_reconstruction(
    Eigen::Ref<const compas::RowMatrixXd> points,
    Eigen::Ref<const compas::RowMatrixXd> normals)
{
    compas::Polyhedron mesh;
    std::vector<PointVectorPair> points_with_normals;

    for (int i = 0; i < points.rows(); i++)
    {
        points_with_normals.push_back(PointVectorPair(
            compas::Point(points(i, 0), points(i, 1), points(i, 2)),
            compas::Vector(normals(i, 0), normals(i, 1), normals(i, 2))));
    }

    double average_spacing = CGAL::compute_average_spacing<CGAL::Sequential_tag>(
        points_with_normals,
        6,
        CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()));

    CGAL::poisson_surface_reconstruction_delaunay(
        points_with_normals.begin(),
        points_with_normals.end(),
        CGAL::First_of_pair_property_map<PointVectorPair>(),
        CGAL::Second_of_pair_property_map<PointVectorPair>(),
        mesh,
        average_spacing);

    return compas::polyhedron_to_vertices_and_faces(mesh);
}


compas::RowMatrixXd
pointset_outlier_removal(
    Eigen::Ref<const compas::RowMatrixXd> points,
    int num_neighbors,
    double radius)
{
    int p = points.rows();
    std::vector<compas::Point> points_vector;

    for (int i = 0; i < p; i++)
    {
        points_vector.push_back(compas::Point(points(i, 0), points(i, 1), points(i, 2)));
    }

    const double average_spacing = CGAL::compute_average_spacing<CGAL::Sequential_tag>(points_vector, num_neighbors);

    std::vector<compas::Point>::iterator to_remove = CGAL::remove_outliers<CGAL::Parallel_if_available_tag>(
        points_vector,
        num_neighbors,
        CGAL::parameters::threshold_percent(100.).threshold_distance(radius * average_spacing));

    points_vector.erase(to_remove, points_vector.end());
    std::vector<compas::Point>(points_vector).swap(points_vector);

    std::size_t s = points_vector.size();
    compas::RowMatrixXd result(s, 3);

    for (int i = 0; i < s; i++)
    {
        result(i, 0) = (double)points_vector[i].x();
        result(i, 1) = (double)points_vector[i].y();
        result(i, 2) = (double)points_vector[i].z();
    }

    return result;
}


compas::RowMatrixXd
pointset_reduction(
    Eigen::Ref<const compas::RowMatrixXd> points,
    double spacing
    )
{

    // ======================================================================
    // Convert Eigen matrix to a vector of cgal points.
    // ======================================================================
    int p = points.rows();
    std::vector<compas::Point> points_vector;

    for (int i = 0; i < p; i++)
        points_vector.emplace_back(points.row(i)[0], points.row(i)[1], points.row(i)[2]);

    // ======================================================================
    // Simplification by voxelization.
    // ======================================================================
    double cell_size = spacing;
    auto iterator_to_first_to_remove = CGAL::grid_simplify_point_set(points_vector, cell_size);
    points_vector.erase(iterator_to_first_to_remove, points_vector.end());

    // Optional: after erase(), shrink_to_fit to trim excess capacity
    points_vector.shrink_to_fit();

    // ======================================================================
    // Convert the vector of cgal points to an Eigen matrix.
    // ======================================================================
    std::size_t s = points_vector.size();
    compas::RowMatrixXd smoothed_eigen_points(s, 3);

    for (std::size_t i = 0; i < s; i++)
        smoothed_eigen_points.row(i) << static_cast<double>(points_vector[i].x()), static_cast<double>(points_vector[i].y()), static_cast<double>(points_vector[i].z());

    return smoothed_eigen_points;


}


compas::RowMatrixXd
pointset_smoothing(
    Eigen::Ref<const compas::RowMatrixXd> points,
    int num_neighbors,
    int num_iterations)
{

    // ======================================================================
    // Convert Eigen matrix to a vector of cgal points.
    // ======================================================================
    int p = points.rows();
    std::vector<compas::Point> points_vector;

    for (int i = 0; i < p; i++)
        points_vector.emplace_back(points.row(i)[0], points.row(i)[1], points.row(i)[2]);
        
    // ======================================================================
    // Smooth the points, default is 24.
    // ======================================================================
    for (int i = 0; i < num_iterations; i++)
        CGAL::jet_smooth_point_set<CGAL::Sequential_tag>(points_vector, num_neighbors);

    // ======================================================================
    // Convert the vector of cgal points to an Eigen matrix
    // ======================================================================
    std::size_t s = points_vector.size();
    compas::RowMatrixXd smoothed_eigen_points(s, 3);

    for (std::size_t i = 0; i < s; i++)
        smoothed_eigen_points.row(i) << static_cast<double>(points_vector[i].x()), static_cast<double>(points_vector[i].y()), static_cast<double>(points_vector[i].z());

    return smoothed_eigen_points;

}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
pointset_normal_estimation(
    Eigen::Ref<const compas::RowMatrixXd> points,
    int num_neighbors,
    bool erase_unoriented)
{

    // ======================================================================
    // Convert Eigen matrix to CGAL point vector pair.
    // ======================================================================
    int p = points.rows();
    std::list<PointVectorPair> points_with_normals;

    for (int i = 0; i < p; i++)
        points_with_normals.emplace_back(PointVectorPair(
            compas::Point(points(i, 0), points(i, 1), points(i, 2)),
            compas::Vector(0, 0, 0)
        ));


    // ===========================================================================
    // Estimates normals direction.
    // Case 1 - the radius is precomputed by the average spacing.
    // Case 2 - the normals are estimated with a fixed number of neighbors.
    // ===========================================================================
    if ( num_neighbors < 1 ) {

        // First compute a spacing using the K parameter
        double spacing
            = CGAL::compute_average_spacing<ConcurrencyTag>
            (points_with_normals, num_neighbors,
            CGAL::parameters::point_map(CGAL::First_of_pair_property_map<PointVectorPair>()));

        // Then, estimate normals with a fixed radius
        CGAL::pca_estimate_normals<ConcurrencyTag> (points_with_normals,0, // when using a neighborhood radius, K=0 means no limit on the number of neighbors returns
                CGAL::parameters::point_map (CGAL::First_of_pair_property_map<PointVectorPair> ()).
                normal_map (CGAL::Second_of_pair_property_map<PointVectorPair> ()).
                neighbor_radius (2. * spacing)); // use 2*spacing as neighborhood radius

    } else {

        CGAL::pca_estimate_normals<ConcurrencyTag>
            (points_with_normals, num_neighbors,
                CGAL::parameters::point_map (CGAL::First_of_pair_property_map<PointVectorPair> ()).
                normal_map (CGAL::Second_of_pair_property_map<PointVectorPair> ()));
    }

    // ===========================================================================
    // Orients normals, give at least 3 points to make a plane.
    // ===========================================================================
    unsigned orientation_neighbors = (num_neighbors < 3) ? 3 : num_neighbors;
    std::list<PointVectorPair>::iterator unoriented_points_begin =
        CGAL::mst_orient_normals (points_with_normals, num_neighbors,
            CGAL::parameters::point_map (CGAL::First_of_pair_property_map<PointVectorPair> ()).
            normal_map (CGAL::Second_of_pair_property_map<PointVectorPair> ()));

    // ===========================================================================
    // Optional: delete points with an unoriented normal.
    // ===========================================================================
    if(erase_unoriented)
        points_with_normals.erase (unoriented_points_begin, points_with_normals.end ());

    // ===========================================================================
    // Convert CGAL normals vector pair to Eigen matrix.
    // ===========================================================================

    std::size_t s = points_with_normals.size();
    compas::RowMatrixXd eigen_points(s, 3);
    compas::RowMatrixXd eigen_vectors(s, 3);

    std::size_t i = 0;
    for (const auto& e : points_with_normals) {
        eigen_points.row(i) << static_cast<double>(e.first.x()), static_cast<double>(e.first.y()), static_cast<double>(e.first.z());
        eigen_vectors.row(i) << static_cast<double>(e.second.x()), static_cast<double>(e.second.y()), static_cast<double>(e.second.z());
        i++;
    }

    return std::make_tuple(eigen_points, eigen_vectors);

}

void init_reconstruction(nb::module_& m) {
    auto submodule = m.def_submodule("reconstruction");

    submodule.def(
        "poisson_surface_reconstruction",
        &poisson_surface_reconstruction,
        "Perform Poisson surface reconstruction on an oriented pointcloud with normals",
        "points"_a,
        "normals"_a
    );

    submodule.def(
        "pointset_outlier_removal",
        &pointset_outlier_removal,
        "Remove outliers from a pointcloud",
        "points"_a,
        "num_neighbors"_a,
        "radius"_a
    );

    submodule.def(
        "pointset_reduction",
        &pointset_reduction,
        "Reduce number of points using hierarchy simplification",
        "points"_a,
        "spacing"_a = 2.0
    );

    submodule.def(
        "pointset_smoothing",
        &pointset_smoothing,
        "Smooth a pointcloud using jet smoothing",
        "points"_a,
        "num_neighbors"_a = 8,
        "num_iterations"_a = 1
    );

    submodule.def(
        "pointset_normal_estimation",
        &pointset_normal_estimation,
        "Estimate pointcloud normals and orient them",
        "points"_a,
        "num_neighbors"_a = 8,
        "erase_unoriented"_a = true
    );
}
