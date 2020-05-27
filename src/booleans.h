#ifndef COMPAS_BOOLEANS_H
#define COMPAS_BOOLEANS_H


#include <compas.h>

#include <pybind11/pybind11.h>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/corefinement.h>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Point_3 = Kernel::Point_3;
using BoolMesh = CGAL::Surface_mesh<Point_3>;

namespace PMP = CGAL::Polygon_mesh_processing;
namespace py = pybind11;

BoolMesh boolmesh_from_vertices_and_faces(compas::RowMatrixXd V, compas::RowMatrixXi F);

compas::Mesh pmp_boolean_union(compas::RowMatrixXd VA, compas::RowMatrixXi FA, compas::RowMatrixXd VB, compas::RowMatrixXi FB);


#endif /* COMPAS_BOOLEANS_H */
