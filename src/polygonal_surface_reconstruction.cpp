#include "polygonal_surface_reconstruction.h"

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/property_map.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Shape_detection/Efficient_RANSAC.h>
#include <CGAL/Polygonal_surface_reconstruction.h>
#include <CGAL/SCIP_mixed_integer_program_traits.h>
#include <CGAL/Timer.h>
#include <fstream>

typedef boost::tuple<compas::Point, compas::Vector, int> PNI;
typedef std::vector<PNI> Point_vector;
typedef CGAL::Nth_of_tuple_property_map<0, PNI> Point_map;
typedef CGAL::Nth_of_tuple_property_map<1, PNI> Normal_map;
typedef CGAL::Nth_of_tuple_property_map<2, PNI> Plane_index_map;

typedef CGAL::Shape_detection::Efficient_RANSAC_traits<compas::Kernel, Point_vector, Point_map, Normal_map> Traits;
typedef CGAL::Shape_detection::Efficient_RANSAC<Traits> Efficient_ransac;
typedef CGAL::Shape_detection::Plane<Traits> Plane;
typedef CGAL::Shape_detection::Point_to_shape_index_map<Traits> Point_to_shape_index_map;
typedef CGAL::Polygonal_surface_reconstruction<compas::Kernel> Polygonal_surface_reconstruction;
typedef CGAL::Surface_mesh<compas::Point> Surface_mesh;

typedef CGAL::SCIP_mixed_integer_program_traits<double> MIP_Solver;

// Function for polygonal surface reconstruction using RANSAC
std::tuple<compas::RowMatrixXd, std::vector<std::vector<int>>>
polygonal_surface_reconstruction_ransac(
    Eigen::Ref<const compas::RowMatrixXd> &P,
    Eigen::Ref<const compas::RowMatrixXd> &N)
{
    // Convert Eigen matrix to a vector of CGAL points.
    int p = P.rows();
    Point_vector points;

    for (int i = 0; i < p; i++)
    {
        points.push_back(boost::tuple<compas::Point, compas::Vector, int>(compas::Point(P.row(i)[0], P.row(i)[1], P.row(i)[2]), compas::Vector(N.row(i)[0], N.row(i)[1], N.row(i)[2]), -1));
    }

    std::cout << "Done. " << points.size() << " points loaded." << std::endl;

    // Efficient RANSAC for plane extraction
    Efficient_ransac ransac;
    ransac.set_input(points);
    ransac.add_shape_factory<Plane>();
    std::cout << "Extracting planes...";
    ransac.detect();
    Efficient_ransac::Plane_range planes = ransac.planes();
    std::size_t num_planes = planes.size();
    std::cout << " Done. " << num_planes << " planes extracted. " << std::endl;

    // Assign plane index to each point
    Point_to_shape_index_map shape_index_map(points, planes);
    for (std::size_t i = 0; i < points.size(); ++i)
    {
        int plane_index = get(shape_index_map, i);
        points[i].get<2>() = plane_index;
    }

    std::cout << "Generating candidate faces...";
    // Polygonal surface reconstruction
    Polygonal_surface_reconstruction algo(
        points,
        Point_map(),
        Normal_map(),
        Plane_index_map());

    Surface_mesh model;
    std::cout << "Reconstructing...";

    // Reconstruct surface using mixed-integer programming solver
    if (!algo.reconstruct<MIP_Solver>(model))
    {
        std::cout << " Failed:...";
        std::cerr << algo.error_message() << std::endl;
    }else{
        std::cout << " Reconstruction is finished. " << std::endl;
    }

    Surface_mesh candidate_faces;
    algo.output_candidate_faces(candidate_faces);
    candidate_faces = model;

    // Extract vertices and faces for result
    std::size_t v = candidate_faces.number_of_vertices();
    std::size_t f = candidate_faces.number_of_faces();

    compas::RowMatrixXd V(v, 3);
    std::vector<std::vector<int>> F;

    compas::Mesh::Property_map<compas::Mesh::Vertex_index, compas::Kernel::Point_3> location = candidate_faces.points();

    for (compas::Mesh::Vertex_index vd : candidate_faces.vertices())
    {
        V(vd, 0) = (double)location[vd][0];
        V(vd, 1) = (double)location[vd][1];
        V(vd, 2) = (double)location[vd][2];
    }

    for (compas::Mesh::Face_index fd : candidate_faces.faces())
    {
        std::vector<int> fv;
        int i = 0;
        for (compas::Mesh::Vertex_index vd : vertices_around_face(candidate_faces.halfedge(fd), candidate_faces))
        {
            fv.emplace_back((int)vd);
        }
        F.emplace_back(fv);
    }

    std::tuple<compas::RowMatrixXd, std::vector<std::vector<int>>> result = std::make_tuple(V, F);

    return result;
}

// Pybind11 initialization function
void init_polygonal_surface_reconstruction(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("polygonal_surface_reconstruction");

    submodule.def(
        "polygonal_surface_reconstruction_ransac",
        &polygonal_surface_reconstruction_ransac,
        pybind11::arg("P").noconvert(),
        pybind11::arg("N").noconvert());
};
