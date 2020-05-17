#include <compas.hpp>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>


using Kernel = CGAL::Simple_cartesian<double>;
using Point3 = Kernel::Point_3;
using Mesh = CGAL::Surface_mesh<Point3>;

using vertex_descriptor = Mesh::Vertex_index;


Mesh mesh_from_vertices_and_faces(RowMatrixXd V, RowMatrixXi F);
