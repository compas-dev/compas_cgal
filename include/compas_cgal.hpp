#include <pybind11/eigen.h>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>


using Kernel = CGAL::Simple_cartesian<double>;
using Point3 = Kernel::Point_3;
using Mesh = CGAL::Surface_mesh<Point3>;

using vertex_descriptor = Mesh::Vertex_index;

using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
using RowMatrixXi = Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;


Mesh mesh_from_vertices_and_faces(RowMatrixXd V, RowMatrixXi F);
