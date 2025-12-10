#include "skeletonization.h"

typedef CGAL::Mean_curvature_flow_skeletonization<compas::Mesh> Skeletonization;
typedef Skeletonization::Skeleton Skeleton;
typedef boost::graph_traits<Skeleton>::vertex_descriptor SkeletonVertex;
typedef boost::graph_traits<Skeleton>::edge_descriptor SkeletonEdge;

std::tuple<std::vector<double>, std::vector<double>, std::vector<std::vector<int>>, std::vector<std::vector<int>>>
pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);

    Skeleton skeleton;
    Skeletonization mcs(mesh);

    // Create a vertex index map for the mesh
    std::map<compas::Mesh::Vertex_index, int> vertex_index_map;
    for (auto v : mesh.vertices()) {
        vertex_index_map[v] = v.idx();
    }

    mcs.contract_until_convergence();
    mcs.convert_to_skeleton(skeleton);

    // Initialize vectors to store start and end points and vertex indices
    std::vector<double> start_points;
    std::vector<double> end_points;
    std::vector<std::vector<int>> start_vertex_indices;
    std::vector<std::vector<int>> end_vertex_indices;

    // Reserve space for efficiency
    size_t num_edges = boost::num_edges(skeleton);
    start_points.reserve(num_edges * 3);  // Each point has 3 coordinates
    end_points.reserve(num_edges * 3);
    start_vertex_indices.reserve(num_edges);
    end_vertex_indices.reserve(num_edges);

    // Extract skeleton edges
    for (SkeletonEdge edge : CGAL::make_range(edges(skeleton))) {
        SkeletonVertex source_vertex = source(edge, skeleton);
        SkeletonVertex target_vertex = target(edge, skeleton);

        const compas::Kernel::Point_3& start = skeleton[source_vertex].point;
        const compas::Kernel::Point_3& end = skeleton[target_vertex].point;

        // Add start point coordinates
        start_points.push_back(start.x());
        start_points.push_back(start.y());
        start_points.push_back(start.z());

        // Add end point coordinates
        end_points.push_back(end.x());
        end_points.push_back(end.y());
        end_points.push_back(end.z());

        // Extract vertex indices for start vertex
        std::vector<int> start_indices;
        for (auto v : skeleton[source_vertex].vertices) {
            start_indices.push_back(vertex_index_map[v]);
        }
        start_vertex_indices.push_back(start_indices);

        // Extract vertex indices for end vertex
        std::vector<int> end_indices;
        for (auto v : skeleton[target_vertex].vertices) {
            end_indices.push_back(vertex_index_map[v]);
        }
        end_vertex_indices.push_back(end_indices);
    }

    return std::make_tuple(start_points, end_points, start_vertex_indices, end_vertex_indices);
};

NB_MODULE(_skeletonization, m) {


    m.def(
        "mesh_skeleton",
        &pmp_mesh_skeleton,
        "Create a geometric skeleton from a mesh using mean curvature flow",
        "vertices"_a,
        "faces"_a
    );
}
