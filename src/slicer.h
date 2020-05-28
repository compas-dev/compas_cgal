#ifndef COMPAS_SLICER_H
#define COMPAS_SLICER_H


#include <compas.h>

#include <pybind11/pybind11.h>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>

#include <CGAL/Polygon_mesh_slicer.h>

using K = CGAL::Exact_predicates_inexact_constructions_kernel;
using SliceMesh = CGAL::Surface_mesh<K::Point_3>;
using Polyline_type = std::vector<K::Point_3>;
using Polylines = std::list<Polyline_type>;

namespace py = pybind11;

SliceMesh slicemesh_from_vertices_and_faces(const compas::RowMatrixXd & V, const compas::RowMatrixXi & F);

void pmp_slice_mesh(compas::RowMatrixXd V, compas::RowMatrixXi F, compas::RowMatrixXd P, compas::RowMatrixXd N);


#endif /* COMPAS_SLICER_H */
