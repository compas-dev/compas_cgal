#pragma once

#include "compas.h"

// CGAL remesh
#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>
#include <CGAL/boost/graph/Dual.h>

namespace compas {

    /**
     * @brief Calculate the surface area of a mesh
     * @param vertices Matrix of vertex coordinates
     * @param faces Matrix of face indices
     * @return Surface area of the mesh
     */
    double pmp_area(
        Eigen::Ref<const RowMatrixXd>& vertices,
        Eigen::Ref<const RowMatrixXi>& faces);

    /**
     * @brief Calculate the volume enclosed by a mesh
     * @param vertices Matrix of vertex coordinates
     * @param faces Matrix of face indices
     * @return Volume enclosed by the mesh
     */
    double pmp_volume(
        Eigen::Ref<const RowMatrixXd>& vertices,
        Eigen::Ref<const RowMatrixXi>& faces);

    /**
     * @brief Calculate the centroid of a mesh
     * @param vertices Matrix of vertex coordinates
     * @param faces Matrix of face indices
     * @return Coordinates of the mesh centroid
     */
    std::vector<double> pmp_centroid(
        Eigen::Ref<const RowMatrixXd>& vertices,
        Eigen::Ref<const RowMatrixXi>& faces);

} // namespace compas

/**
 * @brief Remesh a triangle mesh with target edge length.
 * 
 * @param vertices_a Matrix of vertex positions as Nx3 matrix in row-major order (float64)
 * @param faces_a Matrix of face indices as Mx3 matrix in row-major order (int32)
 * @param target_edge_length Desired length for mesh edges
 * @param number_of_iterations Number of remeshing iterations
 * @param do_project Whether to project vertices onto the input surface
 * @return std::tuple<RowMatrixXd, RowMatrixXi> containing:
 *         - New vertices as Rx3 matrix (float64)
 *         - New faces as Sx3 matrix (int32)
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_remesh(
    Eigen::Ref<compas::RowMatrixXd> vertices_a,
    Eigen::Ref<compas::RowMatrixXi> faces_a,
    double target_edge_length,
    unsigned int number_of_iterations = 10,
    bool do_project = true);


/**
 * @brief Create a dual mesh from a triangular mesh.
 * 
 * @param vertices_a Matrix of vertex positions as Nx3 matrix in row-major order (float64)
 * @param faces_a Matrix of face indices as Mx3 matrix in row-major order (int32)
 * @param target_edge_length Desired length for mesh edges
 * @param number_of_iterations Number of remeshing iterations
 * @param angle_radians Angle limit in radians for boundary vertices
 * @param circumcenter Whether to use the circumcenter of the triangle instead of the centroid
 * @return std::tuple<RowMatrixXd, std::vector<std::vector<int>>> containing:
 *         - New vertices as Rx3 matrix (float64)
 *         - New faces as Sx3 matrix (int32)
 */
std::tuple<compas::RowMatrixXd, std::vector<std::vector<int>>>
pmp_remesh_dual(
    Eigen::Ref<compas::RowMatrixXd> vertices_a,
    Eigen::Ref<compas::RowMatrixXi> faces_a,
    double target_edge_length,
    unsigned int number_of_iterations = 10,
    double angle_radians = 0.5,
    bool circumcenter = true);
