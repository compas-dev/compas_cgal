#pragma once

#include "compas.h"

/**
 * @brief Delaunay Triangulation of a given set of points.
 * 
 * @param V The given vertex locations.
 * @return compas::RowMatrixXi
 */
compas::RowMatrixXi
pmp_delaunay_triangulation(
    Eigen::Ref<compas::RowMatrixXd> V);


/**
 * @brief Conforming delaunay triangulation of a given boundary with internal holes and constraint curves.
 * 
 * @param B The vertices of the boundary.
 * @param P Additional internal vertices.
 * @param holes A list of holes in the triangulation.
 * @param curves A list of internal polyline constraints.
 * @param is_conforming Whether the mesh is conforming.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_constrained_delaunay_triangulation(
    Eigen::Ref<compas::RowMatrixXd> B,
    Eigen::Ref<compas::RowMatrixXd> P,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    bool is_conforming = false
    );

/**
 * @brief Conforming delaunay triangulation of a given boundary with internal holes and constraint curves.
 * 
 * @param B The vertices of the boundary.
 * @param P Additional internal vertices.
 * @param holes A list of holes in the triangulation.
 * @param curves A list of internal polyline constraints.
 * @param minangle The minimum angle of the mesh.
 * @param maxlength The maximum length of the mesh.
 * @param is_optimized  Apply additional optimization to the mesh geometry.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_refined_delaunay_mesh(
    Eigen::Ref<compas::RowMatrixXd> B,
    Eigen::Ref<compas::RowMatrixXd> P,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    double minangle = 0.0,
    double maxlength = 0.0,
    bool is_optimized = true);