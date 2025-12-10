#include "geodesics.h"

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Heat_method_3/Surface_mesh_geodesic_distances_3.h>

// Type definitions for heat method
using HeatMethod = CGAL::Heat_method_3::Surface_mesh_geodesic_distances_3<compas::Mesh>;
using vertex_descriptor = boost::graph_traits<compas::Mesh>::vertex_descriptor;


compas::RowMatrixXd
pmp_heat_geodesic_distances(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources)
{
    // Convert input to CGAL mesh
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);

    int n_vertices = mesh.number_of_vertices();

    // Create property map for distances
    auto distance_pmap = mesh.add_property_map<vertex_descriptor, double>(
        "v:distance", 0.0).first;

    // Create heat method solver (precomputation happens here)
    HeatMethod hm(mesh);

    // Add all sources
    for (int src : sources) {
        if (src >= 0 && src < n_vertices) {
            vertex_descriptor vd = vertex_descriptor(src);
            hm.add_source(vd);
        }
    }

    // Compute geodesic distances
    hm.estimate_geodesic_distances(distance_pmap);

    // Copy results to output matrix
    compas::RowMatrixXd result(n_vertices, 1);
    for (vertex_descriptor vd : mesh.vertices()) {
        result(vd.idx(), 0) = get(distance_pmap, vd);
    }

    return result;
}


/**
 * @brief Heat method solver with precomputation for repeated queries.
 *
 * This class stores the mesh and precomputed data to allow efficient
 * repeated geodesic distance computations from different source vertices.
 */
class HeatGeodesicSolver {
public:
    HeatGeodesicSolver(
        Eigen::Ref<compas::RowMatrixXd> vertices,
        Eigen::Ref<compas::RowMatrixXi> faces)
        : mesh_(compas::mesh_from_vertices_and_faces(vertices, faces)),
          n_vertices_(mesh_.number_of_vertices()),
          distance_pmap_(mesh_.add_property_map<vertex_descriptor, double>("v:distance", 0.0).first),
          hm_(mesh_)
    {}

    compas::RowMatrixXd solve(const std::vector<int>& sources) {
        // Clear previous sources
        hm_.clear_sources();

        // Add all sources
        for (int src : sources) {
            if (src >= 0 && src < n_vertices_) {
                vertex_descriptor vd = vertex_descriptor(src);
                hm_.add_source(vd);
            }
        }

        // Compute geodesic distances
        hm_.estimate_geodesic_distances(distance_pmap_);

        // Copy results to output matrix
        compas::RowMatrixXd result(n_vertices_, 1);
        for (vertex_descriptor vd : mesh_.vertices()) {
            result(vd.idx(), 0) = get(distance_pmap_, vd);
        }

        return result;
    }

    int num_vertices() const { return n_vertices_; }

private:
    compas::Mesh mesh_;
    int n_vertices_;
    compas::Mesh::Property_map<vertex_descriptor, double> distance_pmap_;
    HeatMethod hm_;
};


NB_MODULE(_geodesics, m) {
    m.def(
        "heat_geodesic_distances",
        &pmp_heat_geodesic_distances,
        "Compute geodesic distances using CGAL heat method.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Vertex positions as Nx3 matrix (float64)\n"
        "faces : array-like\n"
        "    Face indices as Mx3 matrix (int32)\n"
        "sources : list[int]\n"
        "    Source vertex indices\n"
        "\n"
        "Returns\n"
        "-------\n"
        "array\n"
        "    Geodesic distances from sources to all vertices (Nx1)",
        "vertices"_a,
        "faces"_a,
        "sources"_a);

    nanobind::class_<HeatGeodesicSolver>(m, "HeatGeodesicSolver",
        "Precomputed heat method solver for repeated geodesic queries.\n\n"
        "Use this class when computing geodesic distances from multiple\n"
        "different sources on the same mesh. The expensive precomputation\n"
        "is done once in the constructor, and solve() can be called many\n"
        "times efficiently.")
        .def(nanobind::init<Eigen::Ref<compas::RowMatrixXd>, Eigen::Ref<compas::RowMatrixXi>>(),
             "vertices"_a, "faces"_a,
             "Create solver with precomputation for the given mesh.")
        .def("solve", &HeatGeodesicSolver::solve,
             "sources"_a,
             "Compute geodesic distances from source vertices.\n\n"
             "Parameters\n"
             "----------\n"
             "sources : list[int]\n"
             "    Source vertex indices\n"
             "\n"
             "Returns\n"
             "-------\n"
             "array\n"
             "    Geodesic distances (Nx1)")
        .def_prop_ro("num_vertices", &HeatGeodesicSolver::num_vertices,
             "Number of vertices in the mesh.");
}
