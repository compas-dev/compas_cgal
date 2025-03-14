#pragma once

#include "compas.h"

/**
 * @brief Delaunay Triangulation of a given set of points.
 * 
 * @param vertices The given vertex locations.
 * @return compas::RowMatrixXi
 */
compas::RowMatrixXi
pmp_delaunay_triangulation(
    Eigen::Ref<compas::RowMatrixXd> vertices);


/**
 * @brief Conforming delaunay triangulation of a given boundary with internal holes and constraint curves.
 * 
 * @param boundary_vertices The vertices of the boundary.
 * @param internal_vertices Additional internal vertices.
 * @param holes A list of holes in the triangulation.
 * @param curves A list of internal polyline constraints.
 * @param is_conforming Whether the mesh is conforming.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_constrained_delaunay_triangulation(
    Eigen::Ref<compas::RowMatrixXd> boundary_vertices,
    Eigen::Ref<compas::RowMatrixXd> internal_vertices,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    bool is_conforming = false
    );

/**
 * @brief Conforming delaunay triangulation of a given boundary with internal holes and constraint curves.
 * 
 * @param boundary_vertices The vertices of the boundary.
 * @param internal_vertices Additional internal vertices.
 * @param holes A list of holes in the triangulation.
 * @param curves A list of internal polyline constraints.
 * @param min_angle The minimum angle of the mesh.
 * @param max_length The maximum length of the mesh.
 * @param is_optimized  Apply additional optimization to the mesh geometry.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_refined_delaunay_mesh(
    Eigen::Ref<compas::RowMatrixXd> boundary_vertices,
    Eigen::Ref<compas::RowMatrixXd> internal_vertices,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    double min_angle = 0.0,
    double max_length = 0.0,
    bool is_optimized = true);