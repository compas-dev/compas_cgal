#include "compas.h"

#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/refine_mesh_at_isolevel.h>
#include <CGAL/boost/graph/split_graph_into_polylines.h>

using vertex_descriptor = boost::graph_traits<compas::Mesh>::vertex_descriptor;
using edge_descriptor = boost::graph_traits<compas::Mesh>::edge_descriptor;


// Extract a single isoline with optional local refinement
std::vector<std::vector<compas::Kernel::Point_3>>
extract_single_isoline(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    Eigen::Ref<const compas::RowMatrixXd> scalars,
    double isovalue,
    double iso_spacing,
    int refine)
{
    typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS,
        vertex_descriptor> IsolineGraph;
    typedef boost::graph_traits<IsolineGraph>::vertex_descriptor ig_vertex;

    // Fresh mesh for this isoline
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    std::size_t num_verts_before = mesh.number_of_vertices();

    // Create and populate scalar property map
    auto scalar_pmap = mesh.add_property_map<vertex_descriptor, double>("v:scalar", 0.0).first;
    for (vertex_descriptor vd : mesh.vertices()) {
        scalar_pmap[vd] = scalars(vd.idx(), 0);
    }

    // Edge constraint map (only used for tracking, not refinement passes)
    auto ecm = mesh.add_property_map<edge_descriptor, bool>("e:is_constrained", false).first;

    // Pre-refine with values very close to the target to subdivide crossing edges
    if (refine > 0 && iso_spacing > 0) {
        // Use small offsets (fraction of spacing) to split edges that span the isovalue
        double base_offset = iso_spacing * 0.1;  // 10% of spacing
        for (int i = 1; i <= refine; ++i) {
            double offset = base_offset * i / refine;

            // Refine below - new vertices get the isovalue they were inserted at
            CGAL::Polygon_mesh_processing::refine_mesh_at_isolevel(
                mesh, scalar_pmap, isovalue - offset,
                CGAL::parameters::edge_is_constrained_map(ecm));

            // Update scalar values for new vertices
            for (std::size_t idx = num_verts_before; idx < mesh.number_of_vertices(); ++idx) {
                scalar_pmap[vertex_descriptor(idx)] = isovalue - offset;
            }
            num_verts_before = mesh.number_of_vertices();

            // Refine above
            CGAL::Polygon_mesh_processing::refine_mesh_at_isolevel(
                mesh, scalar_pmap, isovalue + offset,
                CGAL::parameters::edge_is_constrained_map(ecm));

            for (std::size_t idx = num_verts_before; idx < mesh.number_of_vertices(); ++idx) {
                scalar_pmap[vertex_descriptor(idx)] = isovalue + offset;
            }
            num_verts_before = mesh.number_of_vertices();
        }

        // Clear constraints from pre-refinement
        for (auto e : mesh.edges()) {
            put(ecm, e, false);
        }
    }

    // Extract the actual isoline
    CGAL::Polygon_mesh_processing::refine_mesh_at_isolevel(
        mesh, scalar_pmap, isovalue,
        CGAL::parameters::edge_is_constrained_map(ecm));

    // Build graph from constrained edges
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

    return polyline_points;
}


std::vector<compas::RowMatrixXd>
pmp_isolines(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    Eigen::Ref<const compas::RowMatrixXd> scalars,
    const std::vector<double>& isovalues,
    int refine)
{
    // Compute spacing between isovalues for refinement offsets
    double iso_spacing = 0.0;
    if (isovalues.size() > 1) {
        iso_spacing = std::abs(isovalues[1] - isovalues[0]);
    } else {
        double smin = scalars.minCoeff();
        double smax = scalars.maxCoeff();
        iso_spacing = (smax - smin) / 100.0;
    }

    std::vector<compas::RowMatrixXd> all_polylines;

    // Process each isovalue independently
    for (double isovalue : isovalues) {
        auto polyline_points = extract_single_isoline(
            vertices, faces, scalars, isovalue, iso_spacing, refine);

        // Convert to output format
        for (const auto& pl : polyline_points) {
            compas::RowMatrixXd pts(pl.size(), 3);
            for (std::size_t i = 0; i < pl.size(); ++i) {
                pts(i, 0) = CGAL::to_double(pl[i].x());
                pts(i, 1) = CGAL::to_double(pl[i].y());
                pts(i, 2) = CGAL::to_double(pl[i].z());
            }
            all_polylines.push_back(std::move(pts));
        }
    }

    return all_polylines;
}


NB_MODULE(_isolines, m) {
    m.def(
        "isolines",
        &pmp_isolines,
        "Extract isoline polylines from vertex scalar field.",
        "vertices"_a, "faces"_a, "scalars"_a, "isovalues"_a, "refine"_a = 0);
}
