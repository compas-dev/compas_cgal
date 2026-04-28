#include "booleans.h"

#include <array>
#include <map>

// Local-only: enables std::vector<int> auto-conversion from Python lists for
// the boolean_chain binding. Kept out of compas.h because types_std binds
// std::vector<double> opaquely and the two cannot coexist in the same TU.
#include <nanobind/stl/vector.h>

#include <CGAL/boost/graph/properties.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Polygon_mesh_processing/autorefinement.h>
#include <CGAL/Polygon_mesh_processing/polygon_mesh_to_polygon_soup.h>
#include <CGAL/Polygon_mesh_processing/polygon_soup_to_polygon_mesh.h>

namespace PMP = CGAL::Polygon_mesh_processing;

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    compas::Mesh mesh_out;

    PMP::corefine_and_compute_union(mesh_a, mesh_b, mesh_out);

    return compas::mesh_to_vertices_and_faces(mesh_out);
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    compas::Mesh mesh_out;

    PMP::corefine_and_compute_difference(mesh_a, mesh_b, mesh_out);

    return compas::mesh_to_vertices_and_faces(mesh_out);
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    compas::Mesh mesh_out;

    PMP::corefine_and_compute_intersection(mesh_a, mesh_b, mesh_out);

    return compas::mesh_to_vertices_and_faces(mesh_out);
};

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_split(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_b = compas::mesh_from_vertices_and_faces(vertices_b, faces_b);
    PMP::split(mesh_a, mesh_b);

    return compas::mesh_to_vertices_and_faces(mesh_a);
};

namespace {

// Mark intersection-curve edges of the output mesh and return them as an Ex2
// matrix of vertex indices. The boolean op is supplied as a callable so the
// three variants share the corefinement plumbing.
template <typename BoolOp>
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
boolean_with_edges_impl(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB,
    BoolOp op)
{
    compas::Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    compas::Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);
    compas::Mesh out;

    auto ecm = get(CGAL::dynamic_edge_property_t<bool>(), out);

    op(A, B, out,
       PMP::parameters::default_values(),
       PMP::parameters::default_values(),
       PMP::parameters::edge_is_constrained_map(ecm));

    auto [V, F] = compas::mesh_to_vertices_and_faces(out);

    std::vector<std::pair<int, int>> intersection_edges;
    for (auto e : out.edges())
    {
        if (get(ecm, e))
        {
            auto h = out.halfedge(e);
            intersection_edges.emplace_back(
                static_cast<int>(out.source(h).idx()),
                static_cast<int>(out.target(h).idx()));
        }
    }

    compas::RowMatrixXi E(static_cast<Eigen::Index>(intersection_edges.size()), 2);
    for (std::size_t i = 0; i < intersection_edges.size(); ++i)
    {
        E(static_cast<Eigen::Index>(i), 0) = intersection_edges[i].first;
        E(static_cast<Eigen::Index>(i), 1) = intersection_edges[i].second;
    }

    return {std::move(V), std::move(F), std::move(E)};
}

} // namespace

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_union_with_edges(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    return boolean_with_edges_impl(
        vertices_a, faces_a, vertices_b, faces_b,
        [](compas::Mesh& a, compas::Mesh& b, compas::Mesh& out,
           auto np1, auto np2, auto npout) {
            PMP::corefine_and_compute_union(a, b, out, np1, np2, npout);
        });
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_difference_with_edges(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    return boolean_with_edges_impl(
        vertices_a, faces_a, vertices_b, faces_b,
        [](compas::Mesh& a, compas::Mesh& b, compas::Mesh& out,
           auto np1, auto np2, auto npout) {
            PMP::corefine_and_compute_difference(a, b, out, np1, np2, npout);
        });
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_intersection_with_edges(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    return boolean_with_edges_impl(
        vertices_a, faces_a, vertices_b, faces_b,
        [](compas::Mesh& a, compas::Mesh& b, compas::Mesh& out,
           auto np1, auto np2, auto npout) {
            PMP::corefine_and_compute_intersection(a, b, out, np1, np2, npout);
        });
}

namespace {

// Per-face tag carried through the corefinement: which input mesh the face
// originated from (0 = A, 1 = B) and the face's index in that input.
struct FaceTag
{
    int mesh_id = -1;
    int face_id = -1;
};

// Corefinement visitor that propagates FaceTag values across face splits and
// face copies. Mirrors the technique used in the Cockroach project for CGAL
// face-color tracking through booleans.
struct FaceSourceVisitor
    : public PMP::Corefinement::Default_visitor<compas::Mesh>
{
    using face_descriptor = compas::Mesh::Face_index;
    using TagMap = compas::Mesh::Property_map<face_descriptor, FaceTag>;

    std::map<const compas::Mesh*, TagMap> tags;
    FaceTag pending;

    void before_subface_creations(face_descriptor f, compas::Mesh& tm)
    {
        pending = tags[&tm][f];
    }

    void after_subface_created(face_descriptor f_new, compas::Mesh& tm)
    {
        tags[&tm][f_new] = pending;
    }

    void after_face_copy(face_descriptor f_src, compas::Mesh& tm_src,
                         face_descriptor f_tgt, compas::Mesh& tm_tgt)
    {
        tags[&tm_tgt][f_tgt] = tags[&tm_src][f_src];
    }
};

template <typename BoolOp>
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
boolean_with_face_source_impl(
    Eigen::Ref<const compas::RowMatrixXd> VA,
    Eigen::Ref<const compas::RowMatrixXi> FA,
    Eigen::Ref<const compas::RowMatrixXd> VB,
    Eigen::Ref<const compas::RowMatrixXi> FB,
    BoolOp op)
{
    compas::Mesh A = compas::mesh_from_vertices_and_faces(VA, FA);
    compas::Mesh B = compas::mesh_from_vertices_and_faces(VB, FB);
    compas::Mesh out;

    auto tag_a = A.add_property_map<compas::Mesh::Face_index, FaceTag>("f:src", FaceTag{}).first;
    auto tag_b = B.add_property_map<compas::Mesh::Face_index, FaceTag>("f:src", FaceTag{}).first;
    auto tag_o = out.add_property_map<compas::Mesh::Face_index, FaceTag>("f:src", FaceTag{}).first;

    int idx = 0;
    for (auto f : A.faces()) tag_a[f] = {0, idx++};
    idx = 0;
    for (auto f : B.faces()) tag_b[f] = {1, idx++};

    FaceSourceVisitor visitor;
    visitor.tags[&A] = tag_a;
    visitor.tags[&B] = tag_b;
    visitor.tags[&out] = tag_o;

    // The visitor named parameter is read from np1 (the first input mesh's pack).
    op(A, B, out,
       PMP::parameters::visitor(visitor),
       PMP::parameters::default_values(),
       PMP::parameters::default_values());

    auto [V, F] = compas::mesh_to_vertices_and_faces(out);

    compas::RowMatrixXi S(static_cast<Eigen::Index>(out.number_of_faces()), 2);
    for (auto fd : out.faces())
    {
        const FaceTag& t = tag_o[fd];
        const Eigen::Index row = static_cast<Eigen::Index>(fd.idx());
        S(row, 0) = t.mesh_id;
        S(row, 1) = t.face_id;
    }

    return {std::move(V), std::move(F), std::move(S)};
}

} // namespace

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_union_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    return boolean_with_face_source_impl(
        vertices_a, faces_a, vertices_b, faces_b,
        [](compas::Mesh& a, compas::Mesh& b, compas::Mesh& out,
           auto np1, auto np2, auto npout) {
            PMP::corefine_and_compute_union(a, b, out, np1, np2, npout);
        });
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_difference_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    return boolean_with_face_source_impl(
        vertices_a, faces_a, vertices_b, faces_b,
        [](compas::Mesh& a, compas::Mesh& b, compas::Mesh& out,
           auto np1, auto np2, auto npout) {
            PMP::corefine_and_compute_difference(a, b, out, np1, np2, npout);
        });
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_intersection_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b)
{
    return boolean_with_face_source_impl(
        vertices_a, faces_a, vertices_b, faces_b,
        [](compas::Mesh& a, compas::Mesh& b, compas::Mesh& out,
           auto np1, auto np2, auto npout) {
            PMP::corefine_and_compute_intersection(a, b, out, np1, np2, npout);
        });
}

namespace {

// Build a Surface_mesh from a slice of pre-flattened V and F. Face indices
// are local to the slice (each mesh's faces refer to its own V slice).
compas::Mesh slice_to_mesh(
    const compas::RowMatrixXd& V_all,
    const compas::RowMatrixXi& F_all,
    int v_offset, int v_count,
    int f_offset, int f_count)
{
    compas::Mesh mesh;
    std::vector<compas::Mesh::Vertex_index> idx;
    idx.reserve(v_count);
    for (int i = 0; i < v_count; ++i)
    {
        idx.push_back(mesh.add_vertex(compas::Kernel::Point_3(
            V_all(v_offset + i, 0), V_all(v_offset + i, 1), V_all(v_offset + i, 2))));
    }
    for (int i = 0; i < f_count; ++i)
    {
        mesh.add_face(idx[F_all(f_offset + i, 0)],
                      idx[F_all(f_offset + i, 1)],
                      idx[F_all(f_offset + i, 2)]);
    }
    return mesh;
}

// Snap-round and rebuild a Surface_mesh in place. Used between chain steps
// and inside xor's internal sub-operations to keep them robust per
// https://www.cgal.org/2025/06/13/autorefine-and-snap/
void snap_round_in_place(compas::Mesh& m)
{
    std::vector<compas::Kernel::Point_3> soup_points;
    std::vector<std::array<std::size_t, 3>> soup_triangles;
    PMP::polygon_mesh_to_polygon_soup(m, soup_points, soup_triangles);
    PMP::autorefine_triangle_soup(
        soup_points, soup_triangles,
        PMP::parameters::apply_iterative_snap_rounding(true));
    compas::Mesh refreshed;
    PMP::polygon_soup_to_polygon_mesh(soup_points, soup_triangles, refreshed);
    m = std::move(refreshed);
}

} // namespace

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_chain(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations)
{
    if (mesh_v_counts.size() != mesh_f_counts.size())
    {
        throw std::invalid_argument("mesh_v_counts and mesh_f_counts must have the same length");
    }
    if (mesh_v_counts.empty())
    {
        throw std::invalid_argument("at least one mesh is required");
    }
    if (operations.size() + 1 != mesh_v_counts.size())
    {
        throw std::invalid_argument(
            "operations must have length number_of_meshes - 1");
    }

    // Sanity check: the per-mesh counts must sum to the totals.
    long long total_v = 0, total_f = 0;
    for (int c : mesh_v_counts) total_v += c;
    for (int c : mesh_f_counts) total_f += c;
    if (total_v != vertices.rows() || total_f != faces.rows())
    {
        throw std::invalid_argument("per-mesh counts do not sum to vertices/faces row counts");
    }

    // Materialize V/F into owning matrices once for slice access.
    compas::RowMatrixXd V_all = vertices;
    compas::RowMatrixXi F_all = faces;

    // Build first mesh.
    int v_off = 0, f_off = 0;
    compas::Mesh m = slice_to_mesh(V_all, F_all, v_off, mesh_v_counts[0], f_off, mesh_f_counts[0]);
    v_off += mesh_v_counts[0];
    f_off += mesh_f_counts[0];

    for (std::size_t i = 0; i < operations.size(); ++i)
    {
        compas::Mesh B = slice_to_mesh(V_all, F_all,
                                       v_off, mesh_v_counts[i + 1],
                                       f_off, mesh_f_counts[i + 1]);
        v_off += mesh_v_counts[i + 1];
        f_off += mesh_f_counts[i + 1];

        compas::Mesh tmp;

        switch (operations[i])
        {
        case 0: // union
            PMP::corefine_and_compute_union(m, B, tmp);
            break;
        case 1: // difference (m - B)
            PMP::corefine_and_compute_difference(m, B, tmp);
            break;
        case 2: // intersection
            PMP::corefine_and_compute_intersection(m, B, tmp);
            break;
        case 3: // xor / symmetric difference, computed as (A union B) - (A intersect B)
        {
            // The alternative formula (A - B) union (B - A) is mathematically
            // equivalent but unions two halves that share the A intersect B
            // boundary curve — under EPICK that shared curve gets snap-rounded
            // to near-coincidence in both halves and the union collapses. The
            // (A∪B)−(A∩B) formula avoids that: each step's operands intersect
            // along a single closed surface, not a curve.
            compas::Mesh a_union_b;
            compas::Mesh a_intersect_b;
            compas::Mesh m_copy = m;
            compas::Mesh B_copy = B;
            PMP::corefine_and_compute_union(m, B, a_union_b);
            PMP::corefine_and_compute_intersection(m_copy, B_copy, a_intersect_b);
            snap_round_in_place(a_union_b);
            snap_round_in_place(a_intersect_b);
            PMP::corefine_and_compute_difference(a_union_b, a_intersect_b, tmp);
            break;
        }
        default:
            throw std::invalid_argument(
                "operation must be 0 (union), 1 (difference), 2 (intersection), or 3 (xor)");
        }

        // CGAL 6.1's recommended pipeline for chained corefinements with the
        // inexact-constructions kernel — clean rounding-induced
        // self-intersections at the cut boundary so the next corefinement
        // doesn't trip CGAL's preconditions. Stays in C++.
        // See: https://www.cgal.org/2025/06/13/autorefine-and-snap/
        snap_round_in_place(tmp);
        m = std::move(tmp);
    }

    return compas::mesh_to_vertices_and_faces(m);
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_chain_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations)
{
    // ---- validation (mirrors pmp_boolean_chain) ----
    if (mesh_v_counts.size() != mesh_f_counts.size())
        throw std::invalid_argument("mesh_v_counts and mesh_f_counts must have the same length");
    if (mesh_v_counts.empty())
        throw std::invalid_argument("at least one mesh is required");
    if (operations.size() + 1 != mesh_v_counts.size())
        throw std::invalid_argument("operations must have length number_of_meshes - 1");

    long long total_v = 0, total_f = 0;
    for (int c : mesh_v_counts) total_v += c;
    for (int c : mesh_f_counts) total_f += c;
    if (total_v != vertices.rows() || total_f != faces.rows())
        throw std::invalid_argument("per-mesh counts do not sum to vertices/faces row counts");

    compas::RowMatrixXd V_all = vertices;
    compas::RowMatrixXi F_all = faces;

    // ---- build mesh 0 with FaceTag(0, j) on every original face ----
    int v_off = 0, f_off = 0;
    compas::Mesh m = slice_to_mesh(V_all, F_all, v_off, mesh_v_counts[0], f_off, mesh_f_counts[0]);
    v_off += mesh_v_counts[0];
    f_off += mesh_f_counts[0];

    auto m_tag = m.add_property_map<compas::Mesh::Face_index, FaceTag>("f:src", FaceTag{}).first;
    {
        int j = 0;
        for (auto f : m.faces()) m_tag[f] = FaceTag{0, j++};
    }

    // ---- chain ----
    for (std::size_t i = 0; i < operations.size(); ++i)
    {
        // Build mesh i+1 with FaceTag(i+1, j).
        compas::Mesh B = slice_to_mesh(V_all, F_all,
                                       v_off, mesh_v_counts[i + 1],
                                       f_off, mesh_f_counts[i + 1]);
        v_off += mesh_v_counts[i + 1];
        f_off += mesh_f_counts[i + 1];

        auto b_tag = B.add_property_map<compas::Mesh::Face_index, FaceTag>("f:src", FaceTag{}).first;
        {
            int j = 0;
            const int mesh_id = static_cast<int>(i + 1);
            for (auto f : B.faces()) b_tag[f] = FaceTag{mesh_id, j++};
        }

        // tmp will receive the boolean result; pre-attach an empty tag map so
        // the visitor has somewhere to write copies/subfaces into.
        compas::Mesh tmp;
        auto tmp_tag = tmp.add_property_map<compas::Mesh::Face_index, FaceTag>("f:src", FaceTag{}).first;

        FaceSourceVisitor visitor;
        visitor.tags[&m] = m_tag;
        visitor.tags[&B] = b_tag;
        visitor.tags[&tmp] = tmp_tag;

        switch (operations[i])
        {
        case 0:
            PMP::corefine_and_compute_union(m, B, tmp, PMP::parameters::visitor(visitor));
            break;
        case 1:
            PMP::corefine_and_compute_difference(m, B, tmp, PMP::parameters::visitor(visitor));
            break;
        case 2:
            PMP::corefine_and_compute_intersection(m, B, tmp, PMP::parameters::visitor(visitor));
            break;
        case 3:
            throw std::invalid_argument("xor (op code 3) is not supported by boolean_chain_with_face_source");
        default:
            throw std::invalid_argument("operation must be 0 (union), 1 (difference), or 2 (intersection)");
        }

        // Move the result into m. The property map travels with the mesh,
        // but the previously-fetched handles become stale, so re-fetch.
        // CGAL 6.1's property_map<>(name) returns std::optional<...>.
        m = std::move(tmp);
        m_tag = *m.property_map<compas::Mesh::Face_index, FaceTag>("f:src");
    }

    // ---- extract V, F, S ----
    auto [V_out, F_out] = compas::mesh_to_vertices_and_faces(m);

    compas::RowMatrixXi S(static_cast<Eigen::Index>(m.number_of_faces()), 2);
    for (auto fd : m.faces())
    {
        const FaceTag& t = m_tag[fd];
        const Eigen::Index row = static_cast<Eigen::Index>(fd.idx());
        S(row, 0) = t.mesh_id;
        S(row, 1) = t.face_id;
    }

    return {std::move(V_out), std::move(F_out), std::move(S)};
}

// =============================================================================
// EPECK chain: same shape as the EPICK chain above, but using exact
// constructions. No snap rounding needed because constructions are exact.
// =============================================================================

namespace exact_chain {

using EKernel = CGAL::Exact_predicates_exact_constructions_kernel;
using EPoint = EKernel::Point_3;
using EMesh = CGAL::Surface_mesh<EPoint>;

EMesh slice_to_mesh(
    const compas::RowMatrixXd& V_all,
    const compas::RowMatrixXi& F_all,
    int v_offset, int v_count,
    int f_offset, int f_count)
{
    EMesh mesh;
    std::vector<EMesh::Vertex_index> idx;
    idx.reserve(v_count);
    for (int i = 0; i < v_count; ++i)
    {
        idx.push_back(mesh.add_vertex(EPoint(
            V_all(v_offset + i, 0), V_all(v_offset + i, 1), V_all(v_offset + i, 2))));
    }
    for (int i = 0; i < f_count; ++i)
    {
        mesh.add_face(idx[F_all(f_offset + i, 0)],
                      idx[F_all(f_offset + i, 1)],
                      idx[F_all(f_offset + i, 2)]);
    }
    return mesh;
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> mesh_to_VF(const EMesh& m)
{
    const std::size_t v = m.number_of_vertices();
    const std::size_t f = m.number_of_faces();
    compas::RowMatrixXd V(v, 3);
    compas::RowMatrixXi F(f, 3);
    auto location = m.points();
    for (auto vd : m.vertices())
    {
        const std::size_t r = vd.idx();
        V(r, 0) = CGAL::to_double(location[vd][0]);
        V(r, 1) = CGAL::to_double(location[vd][1]);
        V(r, 2) = CGAL::to_double(location[vd][2]);
    }
    for (auto fd : m.faces())
    {
        const std::size_t r = fd.idx();
        int i = 0;
        for (auto vd : vertices_around_face(m.halfedge(fd), m))
        {
            F(r, i++) = static_cast<int>(vd.idx());
        }
    }
    return {std::move(V), std::move(F)};
}

void check_inputs(
    const compas::RowMatrixXd& V_all, const compas::RowMatrixXi& F_all,
    const std::vector<int>& vc, const std::vector<int>& fc,
    const std::vector<int>& ops)
{
    if (vc.size() != fc.size())
        throw std::invalid_argument("mesh_v_counts and mesh_f_counts must have the same length");
    if (vc.empty())
        throw std::invalid_argument("at least one mesh is required");
    if (ops.size() + 1 != vc.size())
        throw std::invalid_argument("operations must have length number_of_meshes - 1");
    long long tv = 0, tf = 0;
    for (int c : vc) tv += c;
    for (int c : fc) tf += c;
    if (tv != V_all.rows() || tf != F_all.rows())
        throw std::invalid_argument("per-mesh counts do not sum to vertices/faces row counts");
}

struct EFaceTag
{
    int mesh_id = -1;
    int face_id = -1;
};

struct EFaceSourceVisitor
    : public PMP::Corefinement::Default_visitor<EMesh>
{
    using face_descriptor = EMesh::Face_index;
    using TagMap = EMesh::Property_map<face_descriptor, EFaceTag>;

    std::map<const EMesh*, TagMap> tags;
    EFaceTag pending;

    void before_subface_creations(face_descriptor f, EMesh& tm) { pending = tags[&tm][f]; }
    void after_subface_created(face_descriptor f_new, EMesh& tm) { tags[&tm][f_new] = pending; }
    void after_face_copy(face_descriptor f_src, EMesh& tm_src,
                         face_descriptor f_tgt, EMesh& tm_tgt)
    {
        tags[&tm_tgt][f_tgt] = tags[&tm_src][f_src];
    }
};

} // namespace exact_chain

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_chain_exact(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations)
{
    compas::RowMatrixXd V_all = vertices;
    compas::RowMatrixXi F_all = faces;
    exact_chain::check_inputs(V_all, F_all, mesh_v_counts, mesh_f_counts, operations);

    int v_off = 0, f_off = 0;
    exact_chain::EMesh m = exact_chain::slice_to_mesh(V_all, F_all, v_off, mesh_v_counts[0], f_off, mesh_f_counts[0]);
    v_off += mesh_v_counts[0];
    f_off += mesh_f_counts[0];

    for (std::size_t i = 0; i < operations.size(); ++i)
    {
        exact_chain::EMesh B = exact_chain::slice_to_mesh(V_all, F_all,
                                v_off, mesh_v_counts[i + 1],
                                f_off, mesh_f_counts[i + 1]);
        v_off += mesh_v_counts[i + 1];
        f_off += mesh_f_counts[i + 1];

        exact_chain::EMesh tmp;
        switch (operations[i])
        {
        case 0: PMP::corefine_and_compute_union(m, B, tmp); break;
        case 1: PMP::corefine_and_compute_difference(m, B, tmp); break;
        case 2: PMP::corefine_and_compute_intersection(m, B, tmp); break;
        case 3: // xor: (A - B) union (B - A) — works robustly under EPECK
        {
            exact_chain::EMesh m_copy = m, B_copy = B;
            exact_chain::EMesh a_minus_b, b_minus_a;
            PMP::corefine_and_compute_difference(m, B, a_minus_b);
            PMP::corefine_and_compute_difference(B_copy, m_copy, b_minus_a);
            PMP::corefine_and_compute_union(a_minus_b, b_minus_a, tmp);
            break;
        }
        default:
            throw std::invalid_argument(
                "operation must be 0 (union), 1 (difference), 2 (intersection), or 3 (xor)");
        }
        m = std::move(tmp);
    }

    return exact_chain::mesh_to_VF(m);
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_chain_with_face_source_exact(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations)
{
    compas::RowMatrixXd V_all = vertices;
    compas::RowMatrixXi F_all = faces;
    exact_chain::check_inputs(V_all, F_all, mesh_v_counts, mesh_f_counts, operations);

    int v_off = 0, f_off = 0;
    exact_chain::EMesh m = exact_chain::slice_to_mesh(V_all, F_all, v_off, mesh_v_counts[0], f_off, mesh_f_counts[0]);
    v_off += mesh_v_counts[0];
    f_off += mesh_f_counts[0];

    auto m_tag = m.add_property_map<exact_chain::EMesh::Face_index, exact_chain::EFaceTag>("f:src", exact_chain::EFaceTag{}).first;
    {
        int j = 0;
        for (auto f : m.faces()) m_tag[f] = exact_chain::EFaceTag{0, j++};
    }

    for (std::size_t i = 0; i < operations.size(); ++i)
    {
        exact_chain::EMesh B = exact_chain::slice_to_mesh(V_all, F_all,
                                v_off, mesh_v_counts[i + 1],
                                f_off, mesh_f_counts[i + 1]);
        v_off += mesh_v_counts[i + 1];
        f_off += mesh_f_counts[i + 1];

        auto b_tag = B.add_property_map<exact_chain::EMesh::Face_index, exact_chain::EFaceTag>("f:src", exact_chain::EFaceTag{}).first;
        {
            int j = 0;
            const int mesh_id = static_cast<int>(i + 1);
            for (auto f : B.faces()) b_tag[f] = exact_chain::EFaceTag{mesh_id, j++};
        }

        exact_chain::EMesh tmp;
        auto tmp_tag = tmp.add_property_map<exact_chain::EMesh::Face_index, exact_chain::EFaceTag>("f:src", exact_chain::EFaceTag{}).first;

        exact_chain::EFaceSourceVisitor visitor;
        visitor.tags[&m] = m_tag;
        visitor.tags[&B] = b_tag;
        visitor.tags[&tmp] = tmp_tag;

        switch (operations[i])
        {
        case 0:
            PMP::corefine_and_compute_union(m, B, tmp, PMP::parameters::visitor(visitor));
            break;
        case 1:
            PMP::corefine_and_compute_difference(m, B, tmp, PMP::parameters::visitor(visitor));
            break;
        case 2:
            PMP::corefine_and_compute_intersection(m, B, tmp, PMP::parameters::visitor(visitor));
            break;
        case 3:
            throw std::invalid_argument("xor (op code 3) is not supported by boolean_chain_with_face_source");
        default:
            throw std::invalid_argument("operation must be 0 (union), 1 (difference), or 2 (intersection)");
        }

        m = std::move(tmp);
        m_tag = *m.property_map<exact_chain::EMesh::Face_index, exact_chain::EFaceTag>("f:src");
    }

    auto [V_out, F_out] = exact_chain::mesh_to_VF(m);

    compas::RowMatrixXi S(static_cast<Eigen::Index>(m.number_of_faces()), 2);
    for (auto fd : m.faces())
    {
        const exact_chain::EFaceTag& t = m_tag[fd];
        const Eigen::Index row = static_cast<Eigen::Index>(fd.idx());
        S(row, 0) = t.mesh_id;
        S(row, 1) = t.face_id;
    }

    return {std::move(V_out), std::move(F_out), std::move(S)};
}

NB_MODULE(_booleans, m) {

    m.def(
        "boolean_union",
        &pmp_boolean_union,
        "Boolean Union from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_difference",
        &pmp_boolean_difference,
        "Boolean Difference from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_intersection",
        &pmp_boolean_intersection,
        "Boolean Intersection from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "split",
        &pmp_split,
        "Boolean Split from triangular mesh vertices and faces.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_union_with_edges",
        &pmp_boolean_union_with_edges,
        "Boolean Union returning (V, F, E) where E lists vertex-index pairs of intersection-curve edges.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_difference_with_edges",
        &pmp_boolean_difference_with_edges,
        "Boolean Difference returning (V, F, E) where E lists vertex-index pairs of intersection-curve edges.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_intersection_with_edges",
        &pmp_boolean_intersection_with_edges,
        "Boolean Intersection returning (V, F, E) where E lists vertex-index pairs of intersection-curve edges.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_union_with_face_source",
        &pmp_boolean_union_with_face_source,
        "Boolean Union returning (V, F, S) where S[i] = [mesh_id, face_id] of the input face that produced output face i.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_difference_with_face_source",
        &pmp_boolean_difference_with_face_source,
        "Boolean Difference returning (V, F, S) where S[i] = [mesh_id, face_id] of the input face that produced output face i.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_intersection_with_face_source",
        &pmp_boolean_intersection_with_face_source,
        "Boolean Intersection returning (V, F, S) where S[i] = [mesh_id, face_id] of the input face that produced output face i.",
        "VA"_a,
        "FA"_a,
        "VB"_a,
        "FB"_a);

    m.def(
        "boolean_chain",
        &pmp_boolean_chain,
        "Run a chain of boolean operations entirely in C++. The full collection of input "
        "meshes is sent in a single call as flat (V, F) arrays plus per-mesh row counts. "
        "operations is a list of int codes (0=union, 1=difference, 2=intersection, 3=xor) "
        "of length number_of_meshes - 1. Self-intersections are repaired between steps so "
        "long chains are robust.",
        "vertices"_a,
        "faces"_a,
        "mesh_v_counts"_a,
        "mesh_f_counts"_a,
        "operations"_a);

    m.def(
        "boolean_chain_with_face_source",
        &pmp_boolean_chain_with_face_source,
        "Like boolean_chain but additionally returns S (Mx2 int): for each output face, "
        "[mesh_id, face_id] of the input face that produced it. Tracks via a corefinement "
        "visitor and therefore skips snap rounding (the visitor's property maps cannot "
        "survive the soup conversion). xor (op 3) is not supported here.",
        "vertices"_a,
        "faces"_a,
        "mesh_v_counts"_a,
        "mesh_f_counts"_a,
        "operations"_a);

    m.def(
        "boolean_chain_exact",
        &pmp_boolean_chain_exact,
        "Same as boolean_chain but using EPECK (exact constructions). No snap rounding "
        "needed; handles geometrically degenerate input (e.g., shared axes) without shifts.",
        "vertices"_a,
        "faces"_a,
        "mesh_v_counts"_a,
        "mesh_f_counts"_a,
        "operations"_a);

    m.def(
        "boolean_chain_with_face_source_exact",
        &pmp_boolean_chain_with_face_source_exact,
        "Same as boolean_chain_with_face_source but using EPECK. The corefinement visitor "
        "works directly because there are no rounding artifacts to repair.",
        "vertices"_a,
        "faces"_a,
        "mesh_v_counts"_a,
        "mesh_f_counts"_a,
        "operations"_a);
}
