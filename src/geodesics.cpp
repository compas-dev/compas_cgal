#include "geodesics.h"

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Heat_method_3/Surface_mesh_geodesic_distances_3.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/boost/graph/split_graph_into_polylines.h>

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


std::tuple<std::vector<compas::RowMatrixXd>, std::vector<compas::RowMatrixXi>>
pmp_geodesic_isolines_split(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources,
    const std::vector<double>& isovalues)
{
    using vertex_descriptor = boost::graph_traits<compas::Mesh>::vertex_descriptor;
    using edge_descriptor = boost::graph_traits<compas::Mesh>::edge_descriptor;

    // Convert input to CGAL mesh
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    int n_vertices = mesh.number_of_vertices();

    // Create property map for distances
    auto distance_pmap = mesh.add_property_map<vertex_descriptor, double>("v:distance", 0.0).first;

    // Create heat method solver and compute geodesic distances
    HeatMethod hm(mesh);
    for (int src : sources) {
        if (src >= 0 && src < n_vertices) {
            hm.add_source(vertex_descriptor(src));
        }
    }
    hm.estimate_geodesic_distances(distance_pmap);

    // Create edge constraint map to mark isoline edges
    auto ecm = mesh.add_property_map<edge_descriptor, bool>("e:is_constrained", false).first;

    // Refine mesh along each isovalue
    for (double isovalue : isovalues) {
        CGAL::Polygon_mesh_processing::refine_mesh_at_isolevel(
            mesh, distance_pmap, isovalue,
            CGAL::parameters::edge_is_constrained_map(ecm));
    }

    // Triangulate any polygon faces created by refinement
    // (faces with >2 vertices on isoline are not split by refine_mesh_at_isolevel)
    CGAL::Polygon_mesh_processing::triangulate_faces(mesh);

    // Split the mesh into connected components bounded by isocurves
    std::vector<compas::Mesh> components;
    CGAL::Polygon_mesh_processing::split_connected_components(
        mesh, components,
        CGAL::parameters::edge_is_constrained_map(ecm));

    // Convert each component back to vertices/faces with proper index remapping
    // CGAL mesh indices may have gaps, so we need to create contiguous indices
    std::vector<compas::RowMatrixXd> all_vertices;
    std::vector<compas::RowMatrixXi> all_faces;
    all_vertices.reserve(components.size());
    all_faces.reserve(components.size());

    for (const auto& comp : components) {
        std::size_t nv = comp.number_of_vertices();
        std::size_t nf = comp.number_of_faces();

        compas::RowMatrixXd V(nv, 3);
        compas::RowMatrixXi F(nf, 3);

        // Build vertex index remapping (CGAL index -> contiguous index)
        std::unordered_map<std::size_t, int> vertex_remap;
        int v_idx = 0;
        for (auto vd : comp.vertices()) {
            vertex_remap[vd.idx()] = v_idx;
            auto pt = comp.point(vd);
            V(v_idx, 0) = CGAL::to_double(pt.x());
            V(v_idx, 1) = CGAL::to_double(pt.y());
            V(v_idx, 2) = CGAL::to_double(pt.z());
            v_idx++;
        }

        // Build faces with remapped vertex indices
        int f_idx = 0;
        for (auto fd : comp.faces()) {
            int i = 0;
            for (auto vd : vertices_around_face(comp.halfedge(fd), comp)) {
                F(f_idx, i) = vertex_remap[vd.idx()];
                i++;
            }
            f_idx++;
        }

        all_vertices.push_back(std::move(V));
        all_faces.push_back(std::move(F));
    }

    return std::make_tuple(std::move(all_vertices), std::move(all_faces));
}


std::vector<compas::RowMatrixXd>
pmp_geodesic_isolines(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources,
    const std::vector<double>& isovalues)
{
    using vertex_descriptor = boost::graph_traits<compas::Mesh>::vertex_descriptor;
    using edge_descriptor = boost::graph_traits<compas::Mesh>::edge_descriptor;

    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    int n_vertices = mesh.number_of_vertices();

    auto distance_pmap = mesh.add_property_map<vertex_descriptor, double>("v:distance", 0.0).first;

    HeatMethod hm(mesh);
    for (int src : sources) {
        if (src >= 0 && src < n_vertices) {
            hm.add_source(vertex_descriptor(src));
        }
    }
    hm.estimate_geodesic_distances(distance_pmap);

    auto ecm = mesh.add_property_map<edge_descriptor, bool>("e:is_constrained", false).first;

    for (double isovalue : isovalues) {
        CGAL::Polygon_mesh_processing::refine_mesh_at_isolevel(
            mesh, distance_pmap, isovalue,
            CGAL::parameters::edge_is_constrained_map(ecm));
    }

    // Build a graph from constrained edges for polyline extraction
    typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS,
        vertex_descriptor> IsolineGraph;
    typedef boost::graph_traits<IsolineGraph>::vertex_descriptor ig_vertex;

    IsolineGraph iso_graph;
    std::map<vertex_descriptor, ig_vertex> v_map;

    for (auto e : mesh.edges()) {
        if (get(ecm, e)) {
            auto h = mesh.halfedge(e);
            auto src = mesh.source(h);
            auto tgt = mesh.target(h);

            if (v_map.find(src) == v_map.end()) {
                v_map[src] = boost::add_vertex(src, iso_graph);
            }
            if (v_map.find(tgt) == v_map.end()) {
                v_map[tgt] = boost::add_vertex(tgt, iso_graph);
            }
            boost::add_edge(v_map[src], v_map[tgt], iso_graph);
        }
    }

    // Visitor to collect polylines
    struct PolylineVisitor {
        const compas::Mesh& mesh;
        std::vector<std::vector<compas::Kernel::Point_3>>& polylines;
        std::vector<compas::Kernel::Point_3> current;

        PolylineVisitor(const compas::Mesh& m, std::vector<std::vector<compas::Kernel::Point_3>>& p)
            : mesh(m), polylines(p) {}

        void start_new_polyline() { current.clear(); }
        void add_node(ig_vertex v) {
            vertex_descriptor vd = boost::get(boost::vertex_bundle, *graph_ptr)[v];
            current.push_back(mesh.point(vd));
        }
        void end_polyline() {
            if (current.size() >= 2) polylines.push_back(current);
        }
        const IsolineGraph* graph_ptr;
    };

    std::vector<std::vector<compas::Kernel::Point_3>> polyline_points;
    PolylineVisitor visitor(mesh, polyline_points);
    visitor.graph_ptr = &iso_graph;

    CGAL::split_graph_into_polylines(iso_graph, visitor, CGAL::internal::IsTerminalDefault());

    // Convert to output format
    std::vector<compas::RowMatrixXd> polylines;
    for (const auto& pl : polyline_points) {
        compas::RowMatrixXd pts(pl.size(), 3);
        for (std::size_t i = 0; i < pl.size(); ++i) {
            pts(i, 0) = CGAL::to_double(pl[i].x());
            pts(i, 1) = CGAL::to_double(pl[i].y());
            pts(i, 2) = CGAL::to_double(pl[i].z());
        }
        polylines.push_back(std::move(pts));
    }

    return polylines;
}


NB_MODULE(_geodesics, m) {
    m.def(
        "heat_geodesic_distances",
        &pmp_heat_geodesic_distances,
        "Compute geodesic distances using CGAL heat method.",
        "vertices"_a, "faces"_a, "sources"_a);

    nanobind::class_<HeatGeodesicSolver>(m, "HeatGeodesicSolver",
        "Precomputed heat method solver for repeated geodesic queries.")
        .def(nanobind::init<Eigen::Ref<compas::RowMatrixXd>, Eigen::Ref<compas::RowMatrixXi>>(),
             "vertices"_a, "faces"_a)
        .def("solve", &HeatGeodesicSolver::solve, "sources"_a)
        .def_prop_ro("num_vertices", &HeatGeodesicSolver::num_vertices);

    m.def(
        "geodesic_isolines_split",
        &pmp_geodesic_isolines_split,
        "Split mesh into components along geodesic isolines.",
        "vertices"_a, "faces"_a, "sources"_a, "isovalues"_a);

    m.def(
        "geodesic_isolines",
        &pmp_geodesic_isolines,
        "Extract isoline polylines from geodesic distance field.",
        "vertices"_a, "faces"_a, "sources"_a, "isovalues"_a);
}
