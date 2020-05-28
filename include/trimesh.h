#ifndef TRIMESH_H
#define TRIMESH_H


#include <compas.h>

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>

using K = CGAL::Simple_cartesian<double>;
using TriMesh = CGAL::Surface_mesh<K::Point_3>;


TriMesh trimesh_from_vertices_and_faces(const compas::RowMatrixXd & V, const compas::RowMatrixXi & F);


#endif /* TRIMESH_H */
