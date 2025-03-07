#include "skeletonization.h"

typedef CGAL::Mean_curvature_flow_skeletonization<compas::Mesh> Skeletonization;
typedef Skeletonization::Skeleton Skeleton;
typedef boost::graph_traits<compas::Mesh>::vertex_descriptor vertex_descriptor;
typedef boost::graph_traits<Skeleton>::vertex_descriptor Skeleton_vertex;
typedef boost::graph_traits<Skeleton>::edge_descriptor Skeleton_edge;

std::tuple<std::vector<double>, std::vector<double>>
pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

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
    for (Skeleton_edge e : CGAL::make_range(edges(skeleton))) {
        const compas::Kernel::Point_3& s = skeleton[source(e, skeleton)].point;
        const compas::Kernel::Point_3& t = skeleton[target(e, skeleton)].point;

        // Add start point coordinates
        start_points.push_back(s.x());
        start_points.push_back(s.y());
        start_points.push_back(s.z());

        // Add end point coordinates
        end_points.push_back(t.x());
        end_points.push_back(t.y());
        end_points.push_back(t.z());
    }

    return std::make_tuple(start_points, end_points);
};

void init_skeletonization(nb::module_& m) {
    auto submodule = m.def_submodule("skeletonization");

    submodule.def(
        "mesh_skeleton",
        &pmp_mesh_skeleton,
        """ Create a skeleton from a mesh. """,
        "V"_a,
        "F"_a);

}
