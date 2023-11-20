#ifndef COMPAS_H
#define COMPAS_H

#include <pybind11/eigen.h>
#include <pybind11/stl.h>

#include <Eigen/StdVector>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_items_with_id_3.h>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Point = Kernel::Point_3;
using Vector = Kernel::Vector_3;
using Polyline = std::vector<Point>;
using Polylines = std::list<Polyline>;
using Polyhedron = CGAL::Polyhedron_3<Kernel, CGAL::Polyhedron_items_with_id_3>;
using Mesh = CGAL::Surface_mesh<Point>;

namespace compas
{
    using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
    using RowMatrixXi = Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

    Polyhedron polyhedron_from_vertices_and_faces(const RowMatrixXd &V, const RowMatrixXi &F);

    Mesh mesh_from_vertices_and_faces(const RowMatrixXd &V, const RowMatrixXi &F);

    Mesh ngon_from_vertices_and_faces(const RowMatrixXd &V, const std::vector<std::vector<int>> &faces);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> mesh_to_vertices_and_faces(const Mesh &mesh);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> quadmesh_to_vertices_and_faces(const Mesh &mesh);

    std::vector<compas::RowMatrixXd> polylines_to_lists_of_points(Polylines polylines);

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> polyhedron_to_vertices_and_faces(Polyhedron polyhedron);
}

#endif /* COMPAS_H */
