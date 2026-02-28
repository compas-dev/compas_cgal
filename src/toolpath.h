#pragma once

#include "compas.h"

// CGAL straight skeleton / offset
#include <CGAL/Polygon_2.h>
#include <CGAL/create_straight_skeleton_2.h>
#include <CGAL/squared_distance_2.h>

/**
 * @brief Compute medial-axis-transform (MAT) samples for a polygon.
 *
 * @param vertices Matrix of polygon vertices as Nx3 matrix in row-major order (float64)
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXd> containing:
 *         - MAT points as Mx3 matrix (float64)
 *         - MAT radii as Mx1 matrix (float64)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXd>
pmp_polygon_medial_axis_transform(
    Eigen::Ref<const compas::RowMatrixXd> vertices
);

/**
 * @brief Create trochoidal pocket toolpaths using MAT-constrained radii.
 *
 * @param vertices Matrix of polygon vertices as Nx3 matrix in row-major order (float64)
 * @param tool_diameter Cutter diameter
 * @param stepover Reserved for API compatibility (currently unused)
 * @param pitch Trochoid advance per cycle
 * @param min_trochoid_radius Minimum trochoid radius
 * @param max_trochoid_radius Maximum trochoid radius
 * @param mat_scale Scale factor for MAT availability
 * @param radial_clearance Clearance subtracted from available radius
 * @param samples_per_cycle Polyline samples per trochoid cycle (>= 4)
 * @param max_passes Maximum number of emitted MAT-edge toolpaths
 * @return std::vector<compas::RowMatrixXd> List of toolpath polylines, each as Kx3 matrix
 */
std::vector<compas::RowMatrixXd>
pmp_trochoidal_mat_toolpath(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double tool_diameter,
    double stepover,
    double pitch,
    double min_trochoid_radius,
    double max_trochoid_radius,
    double mat_scale,
    double radial_clearance,
    int samples_per_cycle,
    int max_passes
);

/**
 * @brief Create linked circular arc toolpath with path ordering, leads, links, retract/plunge.
 *
 * Meta matrix columns: [path_index, type(0=line,1=arc,2=circle), clockwise, operation]
 * Operation codes: 0=cut, 1=lead_in, 2=lead_out, 3=link, 4=retract, 5=plunge
 *
 * @return std::tuple of (meta Nx4, starts Nx3, ends Nx3, centers Nx3, radii Nx1)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd, compas::RowMatrixXd>
pmp_trochoidal_mat_toolpath_circular(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    double tool_diameter,
    double stepover,
    double pitch,
    double min_trochoid_radius,
    double max_trochoid_radius,
    double mat_scale,
    double radial_clearance,
    int samples_per_cycle,
    int max_passes,
    double lead_in,
    double lead_out,
    bool link_paths,
    bool optimize_order,
    double cut_z,
    double clearance_z,
    bool has_clearance_z,
    bool retract_at_end,
    bool merge_circles
);
