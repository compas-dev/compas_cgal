#include "compas.h"

/**
 * Compute the geometric skeleton of a triangle mesh using mean curvature flow.
 * 
 * @param V Vertices as Nx3 matrix in row-major order
 * @param F Faces as Mx3 matrix of vertex indices in row-major order
 * @return Tuple of start and end point vectors for the skeleton edges
 */
std::tuple<std::vector<double>, std::vector<double>>
pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F);