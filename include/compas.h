#ifndef COMPAS_H
#define COMPAS_H

#include <pybind11/eigen.h>
#include <pybind11/stl.h>

#include <Eigen/StdVector>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Polyline = std::vector<Kernel::Point_3>;
using Polylines = std::list<Polyline>;
using Mesh = CGAL::Surface_mesh<Kernel::Point_3>;

// How to define and work with Polyhedra?
// Define and register structured output.

namespace compas
{
    using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
    using RowMatrixXi = Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

    struct Point
    {
        double x;
        double y;
        double z;
    };

    // Polyhedron
    // polyhedron_from_vertices_and_faces(
    //     const RowMatrixXd &V,
    //     const RowMatrixXi &F);

    Mesh mesh_from_vertices_and_faces(const RowMatrixXd &V, const RowMatrixXi &F);

    Mesh ngon_from_vertices_and_faces(const RowMatrixXd &V, const std::vector<std::vector<int>> &faces);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> mesh_to_vertices_and_faces(const Mesh &mesh);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> quadmesh_to_vertices_and_faces(const Mesh &mesh);

    std::vector<compas::RowMatrixXd> polylines_to_lists_of_points(Polylines polylines);
}

#endif /* COMPAS_H */
