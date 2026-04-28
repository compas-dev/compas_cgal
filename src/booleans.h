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
 * Run a left-folded chain of boolean operations entirely in C++:
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
 * Self-intersections introduced by EPICK's approximate constructions on
 * cut boundaries are repaired between steps via
 * autorefine_and_remove_self_intersections, which is what makes long
 * chains robust.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_chain(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);

/**
 * Like `pmp_boolean_chain`, but additionally tracks which input mesh and
 * which input face each output triangle descended from. Returns
 * `(V, F, S)`, where `S` is an Mx2 int array: `S[i] = [mesh_id, face_id]`.
 *
 * Tracking is done via a CGAL corefinement visitor that propagates per-face
 * tags through subface creation and face copies. The chain runs entirely on
 * Surface_mesh objects (no Python round-trip and no triangle-soup
 * conversion) because the face-tag property maps cannot survive the soup
 * round-trip used by `autorefine_triangle_soup` / snap rounding.
 *
 * Consequence: this chain does NOT apply iterative snap rounding between
 * steps. It is the right entry point when face-source tracking is the
 * priority and the geometry is well-conditioned. For degenerate geometry
 * (e.g., cylinders sharing a common axis point) prefer `pmp_boolean_chain`
 * which gives up source tracking in exchange for snap-rounding robustness.
 *
 * `xor` (operation code 3) is not supported here — use one of the three
 * primary ops.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_chain_with_face_source(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);

/**
 * Same input contract as pmp_boolean_chain, but uses
 * `Exact_predicates_exact_constructions_kernel` (EPECK) instead of EPICK.
 * Constructions are lazy-exact: there are no rounding artifacts on cut
 * boundaries, so no snap rounding is needed and the chain handles
 * geometrically degenerate input (e.g., three cylinders meeting at the
 * origin) without any shifts. Slower than the EPICK chain by some factor
 * that depends on the geometry.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_boolean_chain_exact(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);

/**
 * Like pmp_boolean_chain_with_face_source but using EPECK. Because EPECK has
 * no rounding artifacts, the corefinement visitor that propagates per-face
 * tags works directly without any snap-rounding workaround — face tracking
 * is exact even on degenerate geometry.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi, compas::RowMatrixXi>
pmp_boolean_chain_with_face_source_exact(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces,
    const std::vector<int>& mesh_v_counts,
    const std::vector<int>& mesh_f_counts,
    const std::vector<int>& operations);
