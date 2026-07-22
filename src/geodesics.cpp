#include "geodesics.h"

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/boost/graph/split_graph_into_polylines.h>

#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <Eigen/SparseCholesky>

#include <algorithm>
#include <queue>
#include <stdexcept>
#include <vector>

using vertex_descriptor = boost::graph_traits<compas::Mesh>::vertex_descriptor;

namespace {

// ---------------------------------------------------------------------- heat method
//
// Own implementation of the heat method (Crane, Weischedel & Wardetzky 2017: one
// backward-Euler heat step -> normalized gradient field -> Poisson step), with the
// Poisson step Dirichlet-CONSTRAINED: phi is removed from the unknowns and pinned to
// 0 at every source vertex.
//
// This replaces CGAL::Heat_method_3 here because of that class's source-set
// normalization (`value_at_source_set`), which maps the Poisson potential phi through
//
//     d(i) = min over sources s of |phi(i) - phi(s)|
//
// i.e. the 1-D distance from the VALUE phi(i) to the SET of source values. phi is
// recovered only up to one additive constant and is not constant across a
// multi-vertex source set, so every vertex whose phi lands inside the source-value
// spread collapses toward 0, and the far field is shifted by the maximum source value
// instead of a proper constant. Single-source is unaffected (the rule degenerates to
// the correct shift); every multi-source call is affected, and the error grows with
// the spread. Measured against exact polyhedral (MMP) geodesics on
// data/flat_star_disk_irregular_rim.off with all 508 boundary vertices as sources
// (flat mesh: euclidean distance to the nearest source is the exact truth in the
// near band):
//
//     CGAL 6.1.1 fold:  band ratio 0.54, 83% of band vertices BELOW the euclidean
//                       lower bound;
//     this solver:      band ratio 0.98, ~1%.
//
// Pinning phi at the sources makes the distance exactly 0 on the source set (the
// contract documented by the Python API and its tests) and is correct for arbitrary
// source sets, including solid source regions.

// Cotan-matrix diagonal regularization, same value CGAL Heat_method_3 uses.
constexpr double kDiagRegularization = 1e-8;
// Pure 0/0 guard for degenerate face normals / vanishing far-field gradients
// (a numerical floor, not a comparison tolerance).
constexpr double kDenomFloor = 1e-300;

using SpMat = Eigen::SparseMatrix<double>;
using Triplet = Eigen::Triplet<double>;

struct HeatContext
{
    int n = 0;                                 // vertices
    int m = 0;                                 // faces
    compas::RowMatrixXd V;                     // own copies: the solver outlives numpy refs
    compas::RowMatrixXi F;
    Eigen::VectorXd cot_i, cot_j, cot_k;       // cotangent of the corner angle per face
    Eigen::MatrixXd normal;                    // unnormalized face normals (|.| = 2 * area)
    Eigen::VectorXd double_area;
    SpMat L;                                   // PSD cotan Laplacian + kDiagRegularization
    Eigen::VectorXd mass;                      // barycentric vertex areas (area / 3)
    double t = 0.0;                            // (mean edge length)^2
    Eigen::SimplicialLDLT<SpMat> heat;         // factorization of (M + t L)
    std::vector<std::vector<int>> adjacency;   // vertex adjacency over unique edges

    // Assembles everything source-independent; SimplicialLDLT is neither copyable
    // nor movable, so the context is built in place.
    HeatContext(
        Eigen::Ref<compas::RowMatrixXd> vertices,
        Eigen::Ref<compas::RowMatrixXi> faces);
};

HeatContext::HeatContext(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces)
{
    HeatContext& ctx = *this;
    ctx.V = vertices;
    ctx.F = faces;
    ctx.n = static_cast<int>(ctx.V.rows());
    ctx.m = static_cast<int>(ctx.F.rows());

    ctx.cot_i.resize(ctx.m);
    ctx.cot_j.resize(ctx.m);
    ctx.cot_k.resize(ctx.m);
    ctx.normal.resize(ctx.m, 3);
    ctx.double_area.resize(ctx.m);

    std::vector<Triplet> trip;
    trip.reserve(15 * ctx.m);
    ctx.mass = Eigen::VectorXd::Zero(ctx.n);

    // unique undirected edges (for the time step and the adjacency)
    std::vector<std::pair<int, int>> edges;
    edges.reserve(3 * ctx.m);

    for (int f = 0; f < ctx.m; f++) {
        const int i = ctx.F(f, 0);
        const int j = ctx.F(f, 1);
        const int k = ctx.F(f, 2);
        const Eigen::Vector3d pi = ctx.V.row(i);
        const Eigen::Vector3d pj = ctx.V.row(j);
        const Eigen::Vector3d pk = ctx.V.row(k);
        const Eigen::Vector3d e_ij = pj - pi;
        const Eigen::Vector3d e_ik = pk - pi;
        const Eigen::Vector3d e_jk = pk - pj;

        const Eigen::Vector3d nrm = e_ij.cross(e_ik);
        const double dbl = nrm.norm();  // = 2 * face area (any edge pair of the face)
        ctx.normal.row(f) = nrm;
        ctx.double_area(f) = dbl;
        const double denom = std::max(dbl, kDenomFloor);

        // cotangent of the interior angle at each corner
        const double ci = e_ij.dot(e_ik) / denom;
        const double cj = (-e_ij).dot(e_jk) / denom;
        const double ck = (-e_ik).dot(-e_jk) / denom;
        ctx.cot_i(f) = ci;
        ctx.cot_j(f) = cj;
        ctx.cot_k(f) = ck;

        // PSD cotan Laplacian: L(a,b) -= w, L(a,a) += w with w = cot(opposite)/2
        const int a[3] = {j, i, i};
        const int b[3] = {k, k, j};
        const double c[3] = {ci, cj, ck};
        for (int e = 0; e < 3; e++) {
            const double w = 0.5 * c[e];
            trip.emplace_back(a[e], b[e], -w);
            trip.emplace_back(b[e], a[e], -w);
            trip.emplace_back(a[e], a[e], w);
            trip.emplace_back(b[e], b[e], w);
        }
        for (int corner = 0; corner < 3; corner++) {
            trip.emplace_back(ctx.F(f, corner), ctx.F(f, corner), kDiagRegularization);
        }

        // barycentric lumped mass: area / 3 per corner
        const double third_area = dbl / 6.0;
        ctx.mass(i) += third_area;
        ctx.mass(j) += third_area;
        ctx.mass(k) += third_area;

        edges.emplace_back(std::min(i, j), std::max(i, j));
        edges.emplace_back(std::min(j, k), std::max(j, k));
        edges.emplace_back(std::min(i, k), std::max(i, k));
    }

    ctx.L.resize(ctx.n, ctx.n);
    ctx.L.setFromTriplets(trip.begin(), trip.end());

    std::sort(edges.begin(), edges.end());
    edges.erase(std::unique(edges.begin(), edges.end()), edges.end());
    double mean_edge = 0.0;
    ctx.adjacency.assign(ctx.n, {});
    for (const auto& e : edges) {
        mean_edge += (ctx.V.row(e.first) - ctx.V.row(e.second)).norm();
        ctx.adjacency[e.first].push_back(e.second);
        ctx.adjacency[e.second].push_back(e.first);
    }
    mean_edge /= static_cast<double>(edges.size());
    ctx.t = mean_edge * mean_edge;

    SpMat heat_op = ctx.t * ctx.L;
    for (int i = 0; i < ctx.n; i++) {
        heat_op.coeffRef(i, i) += ctx.mass(i);  // diagonal exists structurally (regularization)
    }
    ctx.heat.compute(heat_op);
    if (ctx.heat.info() != Eigen::Success) {
        throw std::runtime_error("heat geodesics: factorization of the heat operator failed");
    }
}

compas::RowMatrixXd
heat_geodesic_solve(const HeatContext& ctx, const std::vector<int>& sources)
{
    // validate + dedupe the source set (out-of-range indices are ignored, as before)
    std::vector<char> is_source(ctx.n, 0);
    std::vector<int> srcs;
    for (int s : sources) {
        if (s >= 0 && s < ctx.n && !is_source[s]) {
            is_source[s] = 1;
            srcs.push_back(s);
        }
    }
    if (srcs.empty()) {
        throw std::invalid_argument(
            "heat geodesics: at least one valid source vertex index is required");
    }

    // every vertex must be reachable from the source set, or its distance is
    // undefined (a disconnected component without sources) — fail loudly
    std::vector<char> reached(ctx.n, 0);
    std::queue<int> queue;
    for (int s : srcs) {
        reached[s] = 1;
        queue.push(s);
    }
    int n_reached = static_cast<int>(srcs.size());
    while (!queue.empty()) {
        const int v = queue.front();
        queue.pop();
        for (int w : ctx.adjacency[v]) {
            if (!reached[w]) {
                reached[w] = 1;
                n_reached++;
                queue.push(w);
            }
        }
    }
    if (n_reached != ctx.n) {
        throw std::runtime_error(
            "heat geodesics: " + std::to_string(ctx.n - n_reached) +
            " vertices are unreachable from the source set (disconnected component)");
    }

    // heat step: (M + t L) u = u0, u0 = source indicator
    Eigen::VectorXd u0 = Eigen::VectorXd::Zero(ctx.n);
    for (int s : srcs) {
        u0(s) = 1.0;
    }
    const Eigen::VectorXd u = ctx.heat.solve(u0);

    // normalized per-face gradient of u, and its integrated divergence
    Eigen::VectorXd div = Eigen::VectorXd::Zero(ctx.n);
    for (int f = 0; f < ctx.m; f++) {
        const int i = ctx.F(f, 0);
        const int j = ctx.F(f, 1);
        const int k = ctx.F(f, 2);
        const Eigen::Vector3d pi = ctx.V.row(i);
        const Eigen::Vector3d pj = ctx.V.row(j);
        const Eigen::Vector3d pk = ctx.V.row(k);
        const Eigen::Vector3d e_ij = pj - pi;
        const Eigen::Vector3d e_ik = pk - pi;
        const Eigen::Vector3d e_jk = pk - pj;

        const Eigen::Vector3d nrm =
            ctx.normal.row(f) / std::max(ctx.double_area(f), kDenomFloor);
        Eigen::Vector3d g = u(k) * nrm.cross(e_ij)     // corner value times opposite edge
                          + u(i) * nrm.cross(e_jk)
                          + u(j) * nrm.cross(pi - pk);
        const Eigen::Vector3d X = g / std::max(g.norm(), kDenomFloor);

        div(i) += 0.5 * (X.dot(e_ij) * ctx.cot_k(f) + X.dot(e_ik) * ctx.cot_j(f));
        div(j) += 0.5 * (X.dot(e_jk) * ctx.cot_i(f) + X.dot(-e_ij) * ctx.cot_k(f));
        div(k) += 0.5 * (X.dot(-e_ik) * ctx.cot_j(f) + X.dot(-e_jk) * ctx.cot_i(f));
    }

    // Poisson step with Dirichlet pin phi = 0 on the source set: solve only the
    // interior block L_II phi_I = div_I (source columns vanish with a 0 pin)
    const int n_int = ctx.n - static_cast<int>(srcs.size());
    Eigen::VectorXd d = Eigen::VectorXd::Zero(ctx.n);
    if (n_int > 0) {
        std::vector<int> interior_index(ctx.n, -1);
        int idx = 0;
        for (int v = 0; v < ctx.n; v++) {
            if (!is_source[v]) {
                interior_index[v] = idx++;
            }
        }
        std::vector<Triplet> trip;
        trip.reserve(ctx.L.nonZeros());
        for (int col = 0; col < ctx.L.outerSize(); col++) {
            if (is_source[col]) continue;
            for (SpMat::InnerIterator it(ctx.L, col); it; ++it) {
                if (is_source[it.row()]) continue;
                trip.emplace_back(interior_index[it.row()], interior_index[col], it.value());
            }
        }
        SpMat L_II(n_int, n_int);
        L_II.setFromTriplets(trip.begin(), trip.end());

        Eigen::VectorXd rhs(n_int);
        for (int v = 0; v < ctx.n; v++) {
            if (!is_source[v]) {
                rhs(interior_index[v]) = div(v);
            }
        }

        Eigen::SimplicialLDLT<SpMat> poisson(L_II);
        if (poisson.info() != Eigen::Success) {
            throw std::runtime_error("heat geodesics: Poisson factorization failed");
        }
        const Eigen::VectorXd phi = poisson.solve(rhs);
        if (!phi.allFinite()) {
            throw std::runtime_error("heat geodesics: Poisson solve produced non-finite values");
        }
        for (int v = 0; v < ctx.n; v++) {
            if (!is_source[v]) {
                d(v) = phi(interior_index[v]);
            }
        }
    }

    // A consistently clockwise-wound mesh negates the gradient field and therefore
    // phi EXACTLY (the Laplacian is winding-invariant); recover the field.
    if (d.mean() < 0.0) {
        d = -d;
    }
    // Distances are non-negative by contract; discretization can leave a few
    // interior values marginally below 0 near the sources (sub-edge-length noise).
    d = d.cwiseMax(0.0);

    compas::RowMatrixXd result(ctx.n, 1);
    result.col(0) = d;
    return result;
}

}  // namespace


compas::RowMatrixXd
pmp_heat_geodesic_distances(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources)
{
    const HeatContext ctx(vertices, faces);
    return heat_geodesic_solve(ctx, sources);
}


/**
 * @brief Heat method solver with precomputation for repeated queries.
 *
 * Stores the assembled operators (Laplacian, mass, factorized heat operator) so
 * repeated geodesic distance computations from different source sets reuse them.
 * Only the source-dependent Poisson block is re-factorized per solve.
 */
class HeatGeodesicSolver {
public:
    HeatGeodesicSolver(
        Eigen::Ref<compas::RowMatrixXd> vertices,
        Eigen::Ref<compas::RowMatrixXi> faces)
        : ctx_(vertices, faces)
    {}

    compas::RowMatrixXd solve(const std::vector<int>& sources) {
        return heat_geodesic_solve(ctx_, sources);
    }

    int num_vertices() const { return ctx_.n; }

private:
    HeatContext ctx_;
};


std::tuple<std::vector<compas::RowMatrixXd>, std::vector<compas::RowMatrixXi>>
pmp_geodesic_isolines_split(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources,
    const std::vector<double>& isovalues)
{
    using edge_descriptor = boost::graph_traits<compas::Mesh>::edge_descriptor;

    // geodesic distances from the source set (own heat method, see above)
    const HeatContext ctx(vertices, faces);
    const compas::RowMatrixXd distances = heat_geodesic_solve(ctx, sources);

    // CGAL mesh for the refinement/splitting; vertex indices match the input rows
    // (mesh_from_vertices_and_faces adds vertices in order)
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    auto distance_pmap = mesh.add_property_map<vertex_descriptor, double>("v:distance", 0.0).first;
    for (vertex_descriptor vd : mesh.vertices()) {
        put(distance_pmap, vd, distances(vd.idx(), 0));
    }

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
    using edge_descriptor = boost::graph_traits<compas::Mesh>::edge_descriptor;

    const HeatContext ctx(vertices, faces);
    const compas::RowMatrixXd distances = heat_geodesic_solve(ctx, sources);

    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);
    auto distance_pmap = mesh.add_property_map<vertex_descriptor, double>("v:distance", 0.0).first;
    for (vertex_descriptor vd : mesh.vertices()) {
        put(distance_pmap, vd, distances(vd.idx(), 0));
    }

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
        "Compute geodesic distances from a source set using the heat method.",
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
