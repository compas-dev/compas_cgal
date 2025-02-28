#pragma once

// This file contains headers that are compiled once.
// It helps to have faster compilation times during development.
// This file is referenced in CMakeLists PCH section.

// STD
#include <stdlib.h>
#include <vector>
#include <array>
#include <map>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <algorithm>
#include <unordered_map>
#include <numeric>
#include <limits>
#include <chrono>
#include <float.h>
#include <inttypes.h>
#include <cstring>
#include <set>
#include <unordered_set>
#include <list>
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
#include <filesystem>

// Boost Multiprecision
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/multiprecision/cpp_dec_float.hpp>

// Eigen
#include <Eigen/StdVector>

// CGAL
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_items_with_id_3.h>

namespace compas
{
    using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
    using Point = Kernel::Point_3;
    using Vector = Kernel::Vector_3;
    using Polyline = std::vector<Point>;
    using Polylines = std::list<Polyline>;
    using Polyhedron = CGAL::Polyhedron_3<Kernel, CGAL::Polyhedron_items_with_id_3>;
    using Mesh = CGAL::Surface_mesh<Point>;
    using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
    using RowMatrixXi = Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
    using Edge = std::tuple<std::vector<double>, std::vector<double>>;
    using Edges = std::list<Edge>;

    Polyhedron polyhedron_from_vertices_and_faces(const RowMatrixXd &V, const RowMatrixXi &F);

    Mesh mesh_from_vertices_and_faces(const RowMatrixXd &V, const RowMatrixXi &F);

    Mesh ngon_from_vertices_and_faces(const RowMatrixXd &V, const std::vector<std::vector<int>> &faces);

    std::tuple< RowMatrixXd,  RowMatrixXi> mesh_to_vertices_and_faces(const Mesh &mesh);

    std::tuple< RowMatrixXd,  RowMatrixXi> quadmesh_to_vertices_and_faces(const Mesh &mesh);

    std::vector< RowMatrixXd> polylines_to_lists_of_points(Polylines polylines);

    std::tuple< RowMatrixXd,  RowMatrixXi> polyhedron_to_vertices_and_faces(Polyhedron polyhedron);
}

// Nanobind
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/array.h>
#include <nanobind/stl/bind_vector.h>
#include <nanobind/stl/string.h>
namespace nb = nanobind;
using namespace nb::literals; // enables syntax for annotating function and arguments                              // arguments