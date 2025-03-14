#pragma once

// This file contains headers that are compiled once.
// It helps to have faster compilation times during development.
// This file is referenced in CMakeLists PCH section.

// STD
#include <stdlib.h>
#include <vector>
#include <array>
#include <map>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <algorithm>
#include <unordered_map>
#include <numeric>
#include <limits>
#include <chrono>
#include <float.h>
#include <inttypes.h>
#include <cstring>
#include <set>
#include <unordered_set>
#include <list>
#include <string>
#include <fstream>
#include <sstream>
#include <iostream>
#include <filesystem>
#include <utility>


// Nanobind
#include <nanobind/nanobind.h>
#include <nanobind/eigen/dense.h>
#include <nanobind/eigen/sparse.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/array.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/bind_vector.h>
#include <nanobind/stl/shared_ptr.h>
#include <nanobind/stl/string.h>

namespace nb = nanobind;
using namespace nb::literals; // enables syntax for annotating function and arguments

// Boost Multiprecision
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/multiprecision/cpp_int.hpp>


// Eigen
#include <Eigen/Core>
#include <Eigen/Dense>
#include <Eigen/StdVector>

// CGAL
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Polyhedron_incremental_builder_3.h>
#include <CGAL/Polyhedron_items_with_id_3.h>

// CGAL remesh
#include <CGAL/Polygon_mesh_processing/remesh.h>
#include <CGAL/Polygon_mesh_processing/detect_features.h>

// CGAL measure
#include <CGAL/Polygon_mesh_processing/measure.h>
#include <CGAL/Point_3.h>

// CGAL boolean
#include <CGAL/Polygon_mesh_processing/corefinement.h>
#include <CGAL/Polygon_mesh_processing/clip.h>

// CGAL intersection
#include <CGAL/Polygon_mesh_processing/intersection.h>

// CGAL reconstruction
#include <CGAL/poisson_surface_reconstruction.h>
#include <CGAL/property_map.h>
#include <CGAL/remove_outliers.h>
#include <CGAL/compute_average_spacing.h>
#include <CGAL/pca_estimate_normals.h>
#include <CGAL/mst_orient_normals.h>
#include <CGAL/property_map.h>
#include <CGAL/jet_smooth_point_set.h>
#include <CGAL/Point_set_3.h>
#include <CGAL/grid_simplify_point_set.h>

// CGAL skeletonization
#include <CGAL/Mean_curvature_flow_skeletonization.h>
#include <CGAL/boost/graph/split_graph_into_polylines.h>

// CGAL slicer
#include <CGAL/Polygon_mesh_slicer.h>

// CGAL subdivision
#include <CGAL/subdivision_method_3.h>

// CGAL triangulation
#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/Constrained_triangulation_2.h>
#include <CGAL/Constrained_Delaunay_triangulation_2.h>
#include <CGAL/Triangulation_vertex_base_with_info_2.h>
#include <CGAL/Triangulation_face_base_with_info_2.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Delaunay_mesher_2.h>
#include <CGAL/Delaunay_mesh_vertex_base_2.h>
#include <CGAL/Delaunay_mesh_face_base_2.h>
#include <CGAL/Delaunay_mesh_size_criteria_2.h>
#include <CGAL/Triangulation_conformer_2.h>
#include <CGAL/lloyd_optimize_mesh_2.h>

// CGAL straight skeleton 2
#include <CGAL/Polygon_2.h>
#include <CGAL/create_straight_skeleton_2.h>
#include <CGAL/create_straight_skeleton_from_polygon_with_holes_2.h>
#include <CGAL/create_offset_polygons_2.h>
#include <CGAL/create_weighted_offset_polygons_from_polygon_with_holes_2.h>
#include <CGAL/create_weighted_straight_skeleton_2.h>
#include <CGAL/create_offset_polygons_from_polygon_with_holes_2.h>


namespace compas
{
    using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
    using Point = Kernel::Point_3;
    using Vector = Kernel::Vector_3;
    using Polyline = std::vector<Point>;
    using Polylines = std::list<Polyline>;
    using Polyhedron = CGAL::Polyhedron_3<Kernel, CGAL::Polyhedron_items_with_id_3>;
    using Mesh = CGAL::Surface_mesh<Point>;
    using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
    using RowMatrixXi = Eigen::Matrix<int, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

    template <class HDS>
    class Build_polyhedron : public CGAL::Modifier_base<HDS>
    {
    private:
        const RowMatrixXd &m_vertices;
        const RowMatrixXi &m_faces;

    public:
        Build_polyhedron(const RowMatrixXd &V, const RowMatrixXi &F) : m_vertices(V), m_faces(F) {}

        void operator()(HDS &hds)
        {
            typedef typename HDS::Vertex Vertex;
            typedef typename Vertex::Point Point;

            CGAL::Polyhedron_incremental_builder_3<HDS> Builder(hds, true);
            Builder.begin_surface(m_vertices.rows(), m_faces.rows());

            for (int i = 0; i < m_vertices.rows(); i++)
            {
                Builder.add_vertex(Point(m_vertices(i, 0), m_vertices(i, 1), m_vertices(i, 2)));
            }

            for (int i = 0; i < m_faces.rows(); i++)
            {
                Builder.begin_facet();
                for (int j = 0; j < m_faces.cols(); j++)
                {
                    Builder.add_vertex_to_facet(m_faces(i, j));
                }
                Builder.end_facet();
            }

            Builder.end_surface();
        }
    };

    inline Polyhedron polyhedron_from_vertices_and_faces(const RowMatrixXd &V, const RowMatrixXi &F)
    {
        Polyhedron polyhedron;
        Build_polyhedron<Polyhedron::HalfedgeDS> build(V, F);
        polyhedron.delegate(build);
        return polyhedron;
    }

    inline Mesh mesh_from_vertices_and_faces(const RowMatrixXd &V, const RowMatrixXi &F)
    {
        int v = V.rows();
        int f = F.rows();

        Mesh mesh;
        std::vector<Mesh::Vertex_index> index_descriptor;
        index_descriptor.reserve(v);

        for (int i = 0; i < v; i++)
        {
            auto point = Kernel::Point_3(V(i, 0), V(i, 1), V(i, 2));
            index_descriptor.push_back(mesh.add_vertex(std::move(point)));
        }

        mesh.reserve(v, f * 3, f);

        for (int i = 0; i < f; i++)
        {
            auto a = index_descriptor[F(i, 0)];
            auto b = index_descriptor[F(i, 1)];
            auto c = index_descriptor[F(i, 2)];
            mesh.add_face(a, b, c);
        }

        return mesh;
    }

    inline Mesh ngon_from_vertices_and_faces(const RowMatrixXd &V, const std::vector<std::vector<int>> &faces)
    {
        int v = V.rows();
        Mesh mesh;
        std::vector<Mesh::Vertex_index> index_descriptor(v);

        for (int i = 0; i < v; i++)
        {
            index_descriptor[i] = mesh.add_vertex(Kernel::Point_3(V(i, 0), V(i, 1), V(i, 2)));
        }

        for (std::size_t i = 0; i < faces.size(); i++)
        {
            std::vector<Mesh::Vertex_index> face;
            for (std::size_t j = 0; j < faces[i].size(); j++)
            {
                face.push_back(index_descriptor[faces[i][j]]);
            }
            mesh.add_face(face);
        }

        return mesh;
    }

    /**
     * @brief Convert a Surface_mesh to vertices and faces matrices
     * @param mesh A Surface_mesh containing only triangles
     * @return Tuple containing vertices and faces matrices (row-major)
     */
    inline std::tuple<RowMatrixXd, RowMatrixXi> mesh_to_vertices_and_faces(const Mesh& mesh)
    {
        std::size_t v = mesh.number_of_vertices();
        std::size_t f = mesh.number_of_faces();

        RowMatrixXd V(v, 3);
        RowMatrixXi F(f, 3);

        Mesh::Property_map<Mesh::Vertex_index, Kernel::Point_3> location = mesh.points();

        for (Mesh::Vertex_index vd : mesh.vertices()) {
            std::size_t v_idx = vd.idx();
            V(v_idx, 0) = CGAL::to_double(location[vd][0]);
            V(v_idx, 1) = CGAL::to_double(location[vd][1]);
            V(v_idx, 2) = CGAL::to_double(location[vd][2]);
        }

        for (Mesh::Face_index fd : mesh.faces()) {
            std::size_t f_idx = fd.idx();
            int i = 0;
            for (Mesh::Vertex_index vd : vertices_around_face(mesh.halfedge(fd), mesh)) {
                F(f_idx, i) = static_cast<int>(vd.idx());
                i++;
            }
        }

        return std::make_tuple(std::move(V), std::move(F));
    }

    /**
     * @brief Convert a Surface_mesh to vertices and quad faces matrices
     * @param mesh A Surface_mesh containing only quads
     * @return Tuple containing vertices and faces matrices (row-major)
     */
    inline std::tuple<RowMatrixXd, RowMatrixXi> quadmesh_to_vertices_and_faces(const Mesh& mesh)
    {
        std::size_t v = mesh.number_of_vertices();
        std::size_t f = mesh.number_of_faces();

        RowMatrixXd V(v, 3);
        RowMatrixXi F(f, 4);

        Mesh::Property_map<Mesh::Vertex_index, Kernel::Point_3> vertex_location = mesh.points();

        for (Mesh::Vertex_index vd : mesh.vertices()) {
            std::size_t v_idx = vd.idx();
            V(v_idx, 0) = CGAL::to_double(vertex_location[vd][0]);
            V(v_idx, 1) = CGAL::to_double(vertex_location[vd][1]);
            V(v_idx, 2) = CGAL::to_double(vertex_location[vd][2]);
        }

        for (Mesh::Face_index fd : mesh.faces()) {
            std::size_t f_idx = fd.idx();
            int i = 0;
            for (Mesh::Vertex_index vd : vertices_around_face(mesh.halfedge(fd), mesh)) {
                F(f_idx, i) = static_cast<int>(vd.idx());
                i++;
            }
        }

        return std::make_tuple(std::move(V), std::move(F));
    }

    /**
     * @brief Convert polylines to list of point matrices
     * @param polylines List of polylines
     * @return Vector of matrices containing point coordinates
     */
    inline std::vector<RowMatrixXd> polylines_to_lists_of_points(Polylines polylines)
    {
        std::vector<RowMatrixXd> pointsets;

        for (auto i = polylines.begin(); i != polylines.end(); i++)
        {
            const Polyline &poly = *i;
            std::size_t n = poly.size();
            RowMatrixXd points(n, 3);

            for (int j = 0; j < n; j++)
            {
                points(j, 0) = (double)poly[j].x();
                points(j, 1) = (double)poly[j].y();
                points(j, 2) = (double)poly[j].z();
            }

            pointsets.push_back(points);
        }

        return pointsets;
    }

    /**
     * @brief Convert a CGAL Polyhedron to vertices and faces matrices
     * @param polyhedron Input polyhedron
     * @return Tuple containing vertices and faces matrices (row-major)
     */
    inline std::tuple<RowMatrixXd, RowMatrixXi> polyhedron_to_vertices_and_faces(Polyhedron polyhedron)
    {
        std::size_t v = polyhedron.size_of_vertices();
        std::size_t f = polyhedron.size_of_facets();

        RowMatrixXd V(v, 3);
        RowMatrixXi F(f, 3);

        std::unordered_map<Polyhedron::Vertex_const_handle, int> vertex_id_map;
        int i = 0;

        for (Polyhedron::Vertex_const_iterator it = polyhedron.vertices_begin(); it != polyhedron.vertices_end(); ++it, ++i)
        {
            vertex_id_map[it] = i;
            V(i, 0) = CGAL::to_double(it->point().x());
            V(i, 1) = CGAL::to_double(it->point().y());
            V(i, 2) = CGAL::to_double(it->point().z());
        }

        i = 0;
        for (Polyhedron::Facet_const_iterator it = polyhedron.facets_begin(); it != polyhedron.facets_end(); ++it, ++i)
        {
            int j = 0;
            Polyhedron::Halfedge_around_facet_const_circulator jt = it->facet_begin();
            do
            {
                F(i, j) = vertex_id_map[jt->vertex()];
                ++j;
            } while (++jt != it->facet_begin());
        }

        return std::make_tuple(std::move(V), std::move(F));
    }

} // namespace compas