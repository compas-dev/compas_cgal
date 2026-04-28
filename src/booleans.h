#pragma once

#include "compas.h"

// CGAL boolean
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/Polygon_mesh_processing/clip.h>

/**
 * Compute the boolean union of two triangle meshes.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_union(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Compute the boolean difference (A - B) of two triangle meshes.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_difference(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Compute the boolean intersection of two triangle meshes.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_intersection(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Clip mesh A using mesh B as a clipping volume.
 * Points of mesh A that lie inside mesh B are removed.
 * 
 * @param vertices_a Vertices of mesh A as Nx3 matrix in row-major order
 * @param faces_a Faces of mesh A as Mx3 matrix of vertex indices in row-major order
 * @param vertices_b Vertices of clipping mesh B as Px3 matrix in row-major order
 * @param faces_b Faces of clipping mesh B as Qx3 matrix of vertex indices in row-major order
 * @return Tuple containing:
 *         - Resulting vertices as Rx3 matrix
 *         - Resulting faces as Sx3 matrix of vertex indices
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_clip(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Boolean union with the intersection-curve edges of the output reported.
 * Same result mesh as pmp_boolean_union, plus an Ex2 matrix of vertex-index
 * pairs (in the output mesh's V) marking edges that lie on the corefinement
 * intersection curve. Useful for recovering clean polygonal outlines / face
 * groupings without remeshing.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_union_with_edges(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Boolean difference (A - B) with the intersection-curve edges of the output
 * reported. See pmp_boolean_union_with_edges for the edge-output contract.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_difference_with_edges(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Boolean intersection with the intersection-curve edges of the output
 * reported. See pmp_boolean_union_with_edges for the edge-output contract.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_intersection_with_edges(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Boolean union returning, for every output face, which input mesh and which
 * original face it was generated from. The returned third tuple element is an
 * Mx2 int matrix where row i is `[mesh_id, face_id]` for output face i:
 *   mesh_id == 0 → output face came from mesh A; face_id is its index in FA.
 *   mesh_id == 1 → output face came from mesh B; face_id is its index in FB.
 * Tracking is done through a CGAL corefinement visitor (before/after subface
 * creation + after_face_copy) so face splits during the boolean are handled.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_union_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Boolean difference (A - B) with per-face source tracking. See
 * pmp_boolean_union_with_face_source for the output contract.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_difference_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Boolean intersection with per-face source tracking. See
 * pmp_boolean_union_with_face_source for the output contract.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_intersection_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices_a,
    Eigen::Ref<const compas::RowMatrixXi> faces_a,
    Eigen::Ref<const compas::RowMatrixXd> vertices_b,
    Eigen::Ref<const compas::RowMatrixXi> faces_b);

/**
 * Run a left-folded chain of boolean operations entirely in C++ using
 * `Exact_predicates_exact_constructions_kernel` (EPECK):
 *     result = mesh_0
 *     for i in range(len(operations)):
 *         result = result  ops[i]  mesh_{i+1}
 *
 * Marshalling: the entire collection of input meshes is sent in a SINGLE
 * Python→C++ call as flat arrays. Mesh `i` occupies the rows
 * [v_offset_i, v_offset_i + mesh_v_counts[i]) of `vertices` and
 * [f_offset_i, f_offset_i + mesh_f_counts[i]) of `faces`. Face indices are
 * mesh-local (each mesh's faces refer to its own `vertices` slice). Only
 * the final `(V, F)` is returned to Python; intermediate Surface_meshes
 * never leave C++.
 *
 * Operation codes (length = number of meshes - 1):
 *     0 = union
 *     1 = difference (result - mesh_{i+1})
 *     2 = intersection
 *     3 = xor (symmetric difference, computed as (A - B) union (B - A))
 *
 * EPECK constructions are lazy-exact: there are no rounding artifacts on
 * cut boundaries, so the chain handles geometrically degenerate input
 * (e.g., three cylinders meeting at the origin) without any geometric
 * workarounds.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_chain(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);

/**
 * Like `pmp_boolean_chain` but additionally tracks which input mesh and
 * which input face each output triangle descended from. Returns
 * `(V, F, S)` where `S[i] = [mesh_id, face_id]`. Tracking is done via a
 * CGAL corefinement visitor that propagates per-face tags through subface
 * creation and face copies. `xor` (op code 3) is not supported here.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_chain_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);

/**
 * Hybrid kernel chain: Surface_mesh<Point_3> stored in EPICK, but every
 * vertex carries an EPECK::Point_3 in a vertex property map that is passed
 * to corefinement via parameters::vertex_point_map(). All new intersection
 * vertices are constructed in EPECK and then converted back to EPICK for
 * storage, which gives the robustness of EPECK on cut boundaries while
 * keeping mesh storage and traversal at native double speed. This is the
 * pattern from CGAL's "consecutive boolean operations with exact point
 * maps" example.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_chain_hybrid(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);

/**
 * Hybrid-kernel variant of pmp_boolean_chain_with_face_source. Same exact
 * point-map machinery as pmp_boolean_chain_hybrid; the corefinement visitor
 * tracks per-face source through every step, just like the EPICK and EPECK
 * variants, because the visitor and the vertex_point_map are independent
 * named parameters.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_chain_with_face_source_hybrid(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);
