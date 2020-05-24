#pragma once
#include <compas.h>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>


using Kernel = CGAL::Simple_cartesian<double>;
using Point_3 = Kernel::Point_3;
using TriMesh = CGAL::Surface_mesh<Point_3>;


TriMesh trimesh_from_vertices_and_faces(RowMatrixXd V, RowMatrixXi F);
