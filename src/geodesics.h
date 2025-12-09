#pragma once

#include "compas.h"

// CGAL Heat Method for geodesic distances
#include <CGAL/Heat_method_3/Surface_mesh_geodesic_distances_3.h>

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

// HeatGeodesicSolver class is defined in geodesics.cpp and exposed via nanobind
