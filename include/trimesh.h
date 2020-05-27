#ifndef TRIMESH_H
#define TRIMESH_H


#include <compas.h>

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>

using Kernel = CGAL::Simple_cartesian<double>;
using Point_3 = Kernel::Point_3;
using TriMesh = CGAL::Surface_mesh<Point_3>;


TriMesh trimesh_from_vertices_and_faces(compas::RowMatrixXd V, compas::RowMatrixXi F);


#endif /* TRIMESH_H */
