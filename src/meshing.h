#ifndef COMPAS_MESHING_H
#define COMPAS_MESHING_H


#include <compas.h>

#include <pybind11/pybind11.h>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polygon_mesh_processing/remesh.h>

using K = CGAL::Exact_predicates_inexact_constructions_kernel;
using Mesh = CGAL::Surface_mesh<K::Point_3>;

namespace PMP = CGAL::Polygon_mesh_processing;
namespace params = PMP::parameters;
namespace py = pybind11;

Mesh mesh1_from_vertices_and_faces(const compas::RowMatrixXd & V, const compas::RowMatrixXi & F);

compas::Mesh pmp_remesh(compas::RowMatrixXd V, compas::RowMatrixXi F, double target_edge_length, unsigned int niter);


#endif /* COMPAS_MESHING_H */
