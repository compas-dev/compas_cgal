#include "compas.h"

#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/refine_mesh_at_isolevel.h>
#include <CGAL/boost/graph/split_graph_into_polylines.h>

#include <algorithm>
#include <array>
#include <numeric>
#include <stdexcept>

using vertex_descriptor = boost::graph_traits<compas::Mesh>::vertex_descriptor;
using edge_descriptor = boost::graph_traits<compas::Mesh>::edge_descriptor;


using ScalarMap = compas::Mesh::Property_map<vertex_descriptor, double>;
using ConstraintMap = compas::Mesh::Property_map<edge_descriptor, bool>;


// Refine the mesh at the isovalue and return the polylines along the edges on it
std::vector<std::vector<compas::Kernel::Point_3>>
trace_isoline(
    compas::Mesh& mesh,
    ScalarMap scalar_pmap,
    ConstraintMap ecm,
    double isovalue)
{
    typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::undirectedS,
        vertex_descriptor> IsolineGraph;
    typedef boost::graph_traits<IsolineGraph>::vertex_descriptor ig_vertex;

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

    return trace_isoline(mesh, scalar_pmap, ecm, isovalue);
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


// Extract the isolines of many isovalues, meshing for each only the faces it crosses
std::tuple<std::vector<compas::RowMatrixXd>, Eigen::VectorXi>
pmp_isolines_with_indices(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    Eigen::Ref<const compas::RowMatrixXd> scalars,
    const std::vector<double>& isovalues)
{
    if (vertices.cols() != 3) {
        throw std::invalid_argument("vertices must be an Nx3 array");
    }
    if (faces.cols() != 3) {
        throw std::invalid_argument("faces must be an Mx3 array of vertex indices");
    }
    if (scalars.rows() != vertices.rows() || scalars.cols() != 1) {
        throw std::invalid_argument("there must be one scalar per vertex");
    }
    if (faces.rows() > 0 && (faces.minCoeff() < 0 || faces.maxCoeff() >= vertices.rows())) {
        throw std::invalid_argument("a face refers to a vertex that does not exist");
    }

    const std::size_t num_isovalues = isovalues.size();

    // Isovalues in increasing order, each with its position in the input
    std::vector<std::size_t> order(num_isovalues);
    std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(),
        [&](std::size_t a, std::size_t b) { return isovalues[a] < isovalues[b]; });
    std::vector<double> sorted_isovalues(num_isovalues);
    for (std::size_t k = 0; k < num_isovalues; ++k) {
        sorted_isovalues[k] = isovalues[order[k]];
    }

    // One pass over the faces: each face goes to the isovalues within the range of its scalars.
    // A face is listed in input order, so the faces of one isovalue build the same edges, in
    // the same direction, as the whole mesh would.
    std::vector<std::vector<int>> crossed_faces(num_isovalues);
    for (Eigen::Index f = 0; f < faces.rows(); ++f) {
        const double a = scalars(faces(f, 0), 0);
        const double b = scalars(faces(f, 1), 0);
        const double c = scalars(faces(f, 2), 0);
        const double low = std::min({a, b, c});
        const double high = std::max({a, b, c});
        auto first = std::lower_bound(sorted_isovalues.begin(), sorted_isovalues.end(), low);
        auto last = std::upper_bound(first, sorted_isovalues.end(), high);
        for (auto it = first; it != last; ++it) {
            crossed_faces[order[it - sorted_isovalues.begin()]].push_back(static_cast<int>(f));
        }
    }

    std::vector<compas::RowMatrixXd> all_polylines;
    std::vector<int> all_indices;

    // Vertex of the input mesh -> vertex of the mesh of the current isovalue
    std::vector<vertex_descriptor> local(vertices.rows());
    std::vector<bool> is_local(vertices.rows(), false);
    std::vector<int> touched;

    for (std::size_t i = 0; i < num_isovalues; ++i) {
        if (crossed_faces[i].empty()) {
            continue;
        }

        compas::Mesh mesh;
        auto scalar_pmap = mesh.add_property_map<vertex_descriptor, double>("v:scalar", 0.0).first;
        touched.clear();

        for (int f : crossed_faces[i]) {
            std::array<vertex_descriptor, 3> corners;
            for (int j = 0; j < 3; ++j) {
                const int v = faces(f, j);
                if (!is_local[v]) {
                    local[v] = mesh.add_vertex(compas::Kernel::Point_3(vertices(v, 0), vertices(v, 1), vertices(v, 2)));
                    scalar_pmap[local[v]] = scalars(v, 0);
                    is_local[v] = true;
                    touched.push_back(v);
                }
                corners[j] = local[v];
            }
            if (mesh.add_face(corners[0], corners[1], corners[2]) == compas::Mesh::null_face()) {
                throw std::invalid_argument("the faces do not form a manifold triangle mesh");
            }
        }
        for (int v : touched) {
            is_local[v] = false;
        }

        auto ecm = mesh.add_property_map<edge_descriptor, bool>("e:is_constrained", false).first;
        auto polyline_points = trace_isoline(mesh, scalar_pmap, ecm, isovalues[i]);

        for (const auto& pl : polyline_points) {
            compas::RowMatrixXd pts(pl.size(), 3);
            for (std::size_t j = 0; j < pl.size(); ++j) {
                pts(j, 0) = CGAL::to_double(pl[j].x());
                pts(j, 1) = CGAL::to_double(pl[j].y());
                pts(j, 2) = CGAL::to_double(pl[j].z());
            }
            all_polylines.push_back(std::move(pts));
            all_indices.push_back(static_cast<int>(i));
        }
    }

    Eigen::VectorXi indices = Eigen::Map<Eigen::VectorXi>(all_indices.data(), all_indices.size());
    return std::make_tuple(std::move(all_polylines), std::move(indices));
}


NB_MODULE(_isolines, m) {
    m.def(
        "isolines",
        &pmp_isolines,
        "Extract isoline polylines from vertex scalar field.",
        "vertices"_a, "faces"_a, "scalars"_a, "isovalues"_a, "refine"_a = 0);

    m.def(
        "isolines_with_indices",
        &pmp_isolines_with_indices,
        "Extract isoline polylines for many isovalues, each with the index of its isovalue.",
        "vertices"_a, "faces"_a, "scalars"_a, "isovalues"_a);
}
