#pragma once

#include "compas.h"


/**
 * @brief Subdivide a mesh with the Catmull-Clark scheme.
 * 
 * @param V The vertices of the mesh.
 * @param faces The faces of the mesh.
 * @param k The number of subdivision steps.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_catmullclark(
    compas::RowMatrixXd V,
    std::vector<std::vector<int>> faces,
    unsigned int k);

/**
 * @brief Subdivide a mesh with the Loop scheme.
 * 
 * @param V The vertices of the mesh.
 * @param F The faces of the mesh.
 * @param k The number of subdivision steps.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_loop(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    unsigned int k);

/**
 * @brief Subdivide a mesh with the Sqrt3 scheme.
 * 
 * @param V The vertices of the mesh.
 * @param F The faces of the mesh.
 * @param k The number of subdivision steps.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
subd_sqrt3(
    compas::RowMatrixXd V,
    compas::RowMatrixXi F,
    unsigned int k);