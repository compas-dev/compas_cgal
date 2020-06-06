#ifndef COMPAS_H
#define COMPAS_H

#include <Eigen/StdVector>

#include <pybind11/eigen.h>
#include <pybind11/stl.h>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>


using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Mesh = CGAL::Surface_mesh<Kernel::Point_3>;
using Polyline = std::vector<Kernel::Point_3>;
using Polylines = std::list<Polyline>;

namespace compas
{
    using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
    using RowMatrixXi = Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;


    struct Result {
        RowMatrixXd vertices;
        RowMatrixXi faces;
    };

    Mesh mesh_from_vertices_and_faces(const RowMatrixXd & V, const RowMatrixXi & F);

    Result result_from_mesh(const Mesh & mesh);

    std::vector<compas::RowMatrixXd, Eigen::aligned_allocator<compas::RowMatrixXd>> result_from_polylines(const Polylines & polylines);
}


#endif /* COMPAS_H */
