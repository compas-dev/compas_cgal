#include "skeletonization.h"

typedef CGAL::Mean_curvature_flow_skeletonization<compas::Mesh> Skeletonization;
typedef Skeletonization::Skeleton Skeleton;
typedef boost::graph_traits<Skeleton>::vertex_descriptor SkeletonVertex;
typedef boost::graph_traits<Skeleton>::edge_descriptor SkeletonEdge;

std::tuple<std::vector<double>, std::vector<double>>
pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);

    Skeleton skeleton;
    Skeletonization mcs(mesh);

    mcs.contract_until_convergence();
    mcs.convert_to_skeleton(skeleton);

    // Initialize vectors to store start and end points
    std::vector<double> start_points;
    std::vector<double> end_points;

    // Reserve space for efficiency
    size_t num_edges = boost::num_edges(skeleton);
    start_points.reserve(num_edges * 3);  // Each point has 3 coordinates
    end_points.reserve(num_edges * 3);

    // Extract skeleton edges
    for (SkeletonEdge edge : CGAL::make_range(edges(skeleton))) {
        const compas::Kernel::Point_3& start = skeleton[source(edge, skeleton)].point;
        const compas::Kernel::Point_3& end = skeleton[target(edge, skeleton)].point;

        // Add start point coordinates
        start_points.push_back(start.x());
        start_points.push_back(start.y());
        start_points.push_back(start.z());

        // Add end point coordinates
        end_points.push_back(end.x());
        end_points.push_back(end.y());
        end_points.push_back(end.z());
    }

    return std::make_tuple(start_points, end_points);
};

void init_skeletonization(nb::module_& m) {
    auto submodule = m.def_submodule("skeletonization");

    submodule.def(
        "mesh_skeleton",
        &pmp_mesh_skeleton,
        "Create a geometric skeleton from a mesh using mean curvature flow",
        "vertices"_a,
        "faces"_a
    );
}
