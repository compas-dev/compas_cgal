#pragma once

#include "compas.h"

// CGAL skeletonization
#include <CGAL/Mean_curvature_flow_skeletonization.h>
#include <CGAL/boost/graph/split_graph_into_polylines.h>

/**
 * @brief Compute the geometric skeleton of a triangle mesh using mean curvature flow.
 *
 * @param vertices Matrix of vertex positions as Nx3 matrix in row-major order (float64)
 * @param faces Matrix of face indices as Mx3 matrix in row-major order (int32)
 * @return std::tuple<std::vector<double>, std::vector<double>, std::vector<std::vector<int>>, std::vector<std::vector<int>>> containing:
 *         - Start points of skeleton edges as vector of 3D coordinates (float64)
 *         - End points of skeleton edges as vector of 3D coordinates (float64)
 *         - Start vertex indices: for each skeleton edge, indices of original mesh vertices that contracted to the start vertex
 *         - End vertex indices: for each skeleton edge, indices of original mesh vertices that contracted to the end vertex
 */
std::tuple<std::vector<double>, std::vector<double>, std::vector<std::vector<int>>, std::vector<std::vector<int>>>
pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces);