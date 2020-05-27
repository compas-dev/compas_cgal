#ifndef COMPAS_MESHING_H
#define COMPAS_MESHING_H


#include <compas.h>
#include <trimesh.h>

#include <pybind11/pybind11.h>

#include <CGAL/Polygon_mesh_processing/refine.h>
#include <CGAL/Polygon_mesh_processing/fair.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/remesh.h>


namespace PMP = CGAL::Polygon_mesh_processing;
namespace py = pybind11;


void pmp_refine(compas::RowMatrixXd V, compas::RowMatrixXi F);

void pmp_fair(compas::RowMatrixXd V, compas::RowMatrixXi F);

void pmp_triangulate(compas::RowMatrixXd V, compas::RowMatrixXi F);

void pmp_remesh(compas::RowMatrixXd V, compas::RowMatrixXi F);


#endif /* COMPAS_MESHING_H */
