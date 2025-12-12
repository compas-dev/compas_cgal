#pragma once

#include "compas.h"

// CGAL Heat Method for geodesic distances
#include <CGAL/Heat_method_3/Surface_mesh_geodesic_distances_3.h>
#include <CGAL/Polygon_mesh_processing/refine_mesh_at_isolevel.h>
#include <CGAL/Polygon_mesh_processing/connected_components.h>

/**
 * @brief Compute geodesic distances from source vertices using CGAL heat method.
 *
 * @param vertices Matrix of vertex positions as Nx3 matrix (float64)
 * @param faces Matrix of face indices as Mx3 matrix (int32)
 * @param sources Vector of source vertex indices
 * @return RowMatrixXd containing distances from sources to all vertices (Nx1)
 */
compas::RowMatrixXd
pmp_heat_geodesic_distances(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources);

/**
 * @brief Split mesh into components along geodesic isolines.
 *
 * Computes geodesic distances from sources, then refines the mesh along
 * specified isolevel values and splits into connected components.
 *
 * @param vertices Matrix of vertex positions as Nx3 matrix (float64)
 * @param faces Matrix of face indices as Mx3 matrix (int32)
 * @param sources Vector of source vertex indices
 * @param isovalues Vector of isovalue thresholds for splitting
 * @return Tuple of (list of vertices arrays, list of faces arrays) for each mesh component
 */
std::tuple<std::vector<compas::RowMatrixXd>, std::vector<compas::RowMatrixXi>>
pmp_geodesic_isolines_split(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources,
    const std::vector<double>& isovalues);

/**
 * @brief Extract isoline polylines from geodesic distance field.
 *
 * Computes geodesic distances and extracts polylines along specified isovalues.
 *
 * @param vertices Matrix of vertex positions as Nx3 matrix (float64)
 * @param faces Matrix of face indices as Mx3 matrix (int32)
 * @param sources Vector of source vertex indices
 * @param isovalues Vector of isovalue thresholds
 * @return Vector of polylines, each as Nx3 matrix of points
 */
std::vector<compas::RowMatrixXd>
pmp_geodesic_isolines(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources,
    const std::vector<double>& isovalues);

// HeatGeodesicSolver class is defined in geodesics.cpp and exposed via nanobind
