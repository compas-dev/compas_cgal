#pragma once

#include "compas.h"

#include <nanobind/stl/vector.h>

// CGAL straight skeleton 2
#include <CGAL/Polygon_2.h>
#include <CGAL/create_straight_skeleton_2.h>
#include <CGAL/create_straight_skeleton_from_polygon_with_holes_2.h>
#include <CGAL/create_offset_polygons_2.h>
#include <CGAL/create_weighted_offset_polygons_from_polygon_with_holes_2.h>
#include <CGAL/create_weighted_straight_skeleton_2.h>
#include <CGAL/create_offset_polygons_from_polygon_with_holes_2.h>

// CGAL straight skeleton extrusion (roofs)
#include <CGAL/extrude_skeleton.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/remesh_planar_patches.h>


/**
 * @brief Creates a straight skeleton from a simple polygon without holes.
 * 
 * @param vertices Matrix of polygon vertices as Nx2 matrix in row-major order (float64)
 * @return std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> containing:
 *         - Matrix of skeleton vertices (Mx2, float64)
 *         - Vector of source vertex indices from input polygon for each skeleton vertex
 *         - Matrix of skeleton edges as vertex pairs (Kx2, int32)
 *         - Vector of source edge indices from input polygon for each skeleton edge
 */
std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>>
pmp_create_interior_straight_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> vertices
);

/**
 * @brief Creates a straight skeleton from a polygon with holes.
 * 
 * @param boundary_vertices Matrix of boundary polygon vertices as Nx2 matrix in row-major order (float64)
 * @param hole_vertices Vector of hole polygons, each as Mx2 matrix in row-major order (float64)
 * @return std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> containing:
 *         - Matrix of skeleton vertices (Px2, float64)
 *         - Vector of source vertex indices from input polygon for each skeleton vertex
 *         - Matrix of skeleton edges as vertex pairs (Qx2, int32)
 *         - Vector of source edge indices from input polygon for each skeleton edge
 */
std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>>
pmp_create_interior_straight_skeleton_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices
);

/**
 * @brief Creates offset polygons from a simple polygon.
 * 
 * @param vertices Matrix of polygon vertices as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 */
std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_inner(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double& offset_distance
);

/**
 * @brief Creates offset polygons from a polygon with holes.
 * 
 * @param boundary_vertices Matrix of boundary polygon vertices as Nx2 matrix in row-major order (float64)
 * @param hole_vertices Vector of hole polygons, each as Mx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> Vector containing:
 *         - For each offset: tuple of outer polygon (Px2, float64) and vector of inner polygons (each Qx2, float64)
 */
std::vector<std::vector<compas::RowMatrixXd>>
pmp_create_offset_polygons_2_inner_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices,
    double& offset_distance
);
// std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
// pmp_create_offset_polygons_2_inner_with_holes(
//     const compas::RowMatrixXd& boundary_vertices,
//     const std::vector<compas::RowMatrixXd>& hole_vertices,
//     double& offset_distance
// );

/**
 * @brief Creates outward offset polygons from a simple polygon.
 * 
 * @param vertices Matrix of polygon vertices as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 */
std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_outer(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double& offset_distance
);

/**
 * @brief Creates outward offset polygons from a polygon with holes.
 * 
 * @param boundary_vertices Matrix of boundary polygon vertices as Nx2 matrix in row-major order (float64)
 * @param hole_vertices Vector of hole polygons, each as Mx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (positive for inward, negative for outward)
 * @return std::vector<std::vector<compas::RowMatrixXd>> Vector containing:
 *         - For each offset: tuple of outer polygon (Px2, float64) and vector of inner polygons (each Qx2, float64)
 */
std::vector<std::vector<compas::RowMatrixXd>>
pmp_create_offset_polygons_2_outer_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices,
    double& offset_distance
);

/**
 * @brief Create weighted offset polygons for the interior of a polygon.
 * 
 * @param vertices Matrix of vertex coordinates as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (must be positive)
 * @param edge_weights Matrix of weights for each edge as Nx1 matrix (float64, must be positive)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 * @throws std::invalid_argument if edge_weights size doesn't match vertices or if weights are not positive
 * @throws std::runtime_error if CGAL fails to create the skeleton or offset
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_inner(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double offset_distance,
    Eigen::Ref<const compas::RowMatrixXd> edge_weights
);

/**
 * @brief Create weighted offset polygons for the exterior of a polygon.
 * 
 * @param vertices Matrix of vertex coordinates as Nx2 matrix in row-major order (float64)
 * @param offset_distance Offset distance (must be positive)
 * @param edge_weights Matrix of weights for each edge as Nx1 matrix (float64, must be positive)
 * @return std::vector<compas::RowMatrixXd> Vector of offset polygons, each as Mx2 matrix of vertices (float64)
 * @throws std::invalid_argument if edge_weights size doesn't match vertices or if weights are not positive
 * @throws std::runtime_error if CGAL fails to create the skeleton or offset
 */
std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_outer(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double offset_distance,
    Eigen::Ref<const compas::RowMatrixXd> edge_weights
);

/**
 * @brief Extrude a 2D polygon (with optional holes) into a closed 3D surface mesh
 *        using the straight skeleton. This produces roof-like geometry from a
 *        building footprint.
 *
 * The propagation speed of each contour edge is controlled either by weights or by
 * taper angles (in degrees). Weight 1 (or angle 45) yields a standard 45 degree slope.
 *
 * @param boundary_vertices Matrix of the outer boundary vertices as Nx2 or Nx3 matrix
 *        in row-major order (float64). The boundary must be counter-clockwise oriented.
 * @param hole_vertices Vector of hole polygons, each as Mx2 or Mx3 matrix in row-major
 *        order (float64). Holes must be clockwise oriented.
 * @param speeds Propagation speed per contour edge. One inner vector per contour
 *        (outer boundary first, then each hole), each holding one value per edge.
 * @param use_angles If true, the speeds are interpreted as taper angles in degrees,
 *        otherwise as straight skeleton edge weights.
 * @param maximum_height Maximum extrusion height. Values <= 0 mean unbounded, in which
 *        case an inward slope is extruded up to the apex of the skeleton.
 * @return std::tuple<compas::RowMatrixXd, std::vector<std::vector<int>>> containing:
 *         - Matrix of mesh vertices (Vx3, float64)
 *         - Vector of faces, each a vector of vertex indices. Coplanar faces are merged
 *           into a single polygon; only planar patches with holes remain triangulated.
 * @throws std::runtime_error if CGAL fails to extrude the skeleton.
 */
std::tuple<compas::RowMatrixXd, std::vector<std::vector<int>>>
pmp_extrude_straight_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices,
    const std::vector<std::vector<double>>& speeds,
    bool use_angles,
    double maximum_height
);

void init_straight_skeleton_2(nb::module_& m);