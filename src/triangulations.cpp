#include "triangulations.h"

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

#include <unordered_map>


struct FaceInfo
{
    FaceInfo() {};

    int nesting_level;

    bool in_domain() {
        return nesting_level % 2 == 1;
    }
};


using VertexBase1 = CGAL::Triangulation_vertex_base_with_info_2<unsigned, Kernel>;
using TDS1 = CGAL::Triangulation_data_structure_2<VertexBase1>;
using DT = CGAL::Delaunay_triangulation_2<Kernel, TDS1>;

// using VertexBase2 = CGAL::Triangulation_vertex_base_2<Kernel>;
// using _FaceBase = CGAL::Triangulation_face_base_with_info_2<FaceInfo, Kernel>;
// using FaceBase2 = CGAL::Constrained_triangulation_face_base_2<Kernel, _FaceBase>;
using VertexBase2 = CGAL::Delaunay_mesh_vertex_base_2<Kernel>;
using FaceBase2 = CGAL::Delaunay_mesh_face_base_2<Kernel>;
using TDS2 = CGAL::Triangulation_data_structure_2<VertexBase2, FaceBase2>;
using Itag = CGAL::Exact_predicates_tag;
using CDT = CGAL::Constrained_Delaunay_triangulation_2<Kernel, TDS2, Itag>;

using Criteria = CGAL::Delaunay_mesh_size_criteria_2<CDT>;
// using Mesher = CGAL::Delaunay_mesher_2<CDT, Criteria>;

using Polygon = CGAL::Polygon_2<Kernel>;

namespace py = pybind11;

// ===========================================================================
// ===========================================================================
// ===========================================================================
// DT
// ===========================================================================
// ===========================================================================
// ===========================================================================

compas::RowMatrixXi
pmp_delaunay_triangulation(Eigen::Ref<const compas::RowMatrixXd> & V)
{
    DT triangulation;

    std::vector< std::pair<DT::Point, unsigned> > points(V.rows());

    for (int i=0; i < V.rows(); i++) {
        DT::Point point = DT::Point(V(i, 0), V(i, 1));
        points[i] = std::make_pair(point, i);
    }

    triangulation.insert(points.begin(), points.end());

    compas::RowMatrixXi F(triangulation.number_of_faces(), 3);

    int j = 0;
    for (DT::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++) {
        DT::Face_handle face = fit;

        F(j, 0) = face->vertex(0)->info();
        F(j, 1) = face->vertex(1)->info();
        F(j, 2) = face->vertex(2)->info();

        j++;
    }

    return F;
}

// ===========================================================================
// ===========================================================================
// ===========================================================================
// CDT
// ===========================================================================
// ===========================================================================
// ===========================================================================

// compas::RowMatrixXd
// pmp_constrained_delaunay_triangulation(
//     Eigen::Ref<const compas::RowMatrixXd> & V,
//     Eigen::Ref<const compas::RowMatrixXi> & E)
// {
//     CDT triangulation;

//     std::vector< CDT::Vertex_handle > vertex_handles(V.rows());

//     for (int i=0; i < V.rows(); i++) {
//         CDT::Point point = CDT::Point(V(i, 0), V(i, 1));
//         vertex_handles[i] = triangulation.insert(point);
//     }

//     for (int i=0; i < E.rows(); i++) {
//         triangulation.insert_constraint(
//             vertex_handles[E(i, 0)],
//             vertex_handles[E(i, 1)]
//         );
//     }

//     compas::RowMatrixXd F(triangulation.number_of_faces(), 6);

//     int j = 0;
//     for (CDT::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++) {
//         CDT::Face_handle face = fit;

//         CDT::Point a = face->vertex(0)->point();
//         CDT::Point b = face->vertex(1)->point();
//         CDT::Point c = face->vertex(2)->point();

//         F(j, 0) = a.hx();
//         F(j, 1) = a.hy();

//         F(j, 2) = b.hx();
//         F(j, 3) = b.hy();

//         F(j, 4) = c.hx();
//         F(j, 5) = c.hy();

//         j++;
//     }

//     return F;
// }

// ===========================================================================
// ===========================================================================
// ===========================================================================
// CDT2
// ===========================================================================
// ===========================================================================
// ===========================================================================


// void
// mark_domains(CDT & triangulation,
//              CDT::Face_handle start,
//              int index,
//              std::list<CDT::Edge> & border)
// {
//     if (start->info().nesting_level != -1) {
//         return;
//     }

//     std::list<CDT::Face_handle> queue;
//     queue.push_back(start);

//     while (! queue.empty()) {
//         CDT::Face_handle face = queue.front();

//         queue.pop_front();
        
//         if (face->info().nesting_level == -1) {
//             face->info().nesting_level = index;

//             for (int i = 0; i < 3; i++) {
//                 CDT::Edge edge(face, i);
//                 CDT::Face_handle nbr = face->neighbor(i);

//                 if (nbr->info().nesting_level == -1) {
//                     if (triangulation.is_constrained(edge)) {
//                         border.push_back(edge);
//                     }
//                     else {
//                         queue.push_back(nbr);
//                     }
//                 }
//             }
//         }
//     }
// }


//explore set of facets connected with non constrained edges,
//and attribute to each such set a nesting level.
//We start from facets incident to the infinite vertex, with a nesting
//level of 0. Then we recursively consider the non-explored facets incident
//to constrained edges bounding the former set and increase the nesting level by 1.
//Facets in the domain are those with an odd nesting level.
// void
// mark_domains(CDT & triangulation)
// {
//     for (CDT::Face_handle face : triangulation.all_face_handles()) {
//         face->info().nesting_level = -1;
//     }
    
//     std::list<CDT::Edge> border;

//     mark_domains(triangulation, triangulation.infinite_face(), 0, border);
    
//     while (! border.empty()) {
//         CDT::Edge edge = border.front();
//         border.pop_front();

//         CDT::Face_handle nbr = edge.first->neighbor(edge.second);

//         if (nbr->info().nesting_level == -1) {
//             mark_domains(triangulation, nbr, edge.first->info().nesting_level + 1, border);
//         }
//     }
// }


/**
 * Constrained delaunay triangulation of a given boundary
 * with internal holes and constraint curves.
 *
 * @param B The vertices of the boundary.
 * @param holes A list of holes in the triangulation.
 * @param curves A list of internal polyline constraints.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_constrained_delaunay_triangulation(
    Eigen::Ref<const compas::RowMatrixXd> & B,
    std::vector< Eigen::Ref<const compas::RowMatrixXd> > & holes,
    std::vector< Eigen::Ref<const compas::RowMatrixXd> > & curves,
    double minangle,
    double maxlength)
{
    CDT triangulation;

    // Add the boundary as polygon constraint.

    Polygon boundary;

    for (int i=0; i < B.rows(); i++) {
        boundary.push_back(CDT::Point(B(i, 0), B(i, 1)));
    }

    triangulation.insert_constraint(boundary.vertices_begin(), boundary.vertices_end(), true);

    // Add the holes as polygon constraints.

    for (auto hit : holes) {
        compas::RowMatrixXd H = hit;

        Polygon hole;

        for (int i=0; i < H.rows(); i++) {
            hole.push_back(CDT::Point(H(i, 0), H(i, 1)));
        }

        triangulation.insert_constraint(hole.vertices_begin(), hole.vertices_end(), true);
    }

    // Add the curves as polyline constraints.

    for (auto cit : curves) {
        compas::RowMatrixXd C = cit;

        std::vector<CDT::Point> points(C.rows());

        for (int i = 0; i < C.rows(); i++) {
            points[i] = CDT::Point(C(i, 0), C(i, 1));
        }

        triangulation.insert_constraint(points.begin(), points.end());
    }

    // Mark the faces belonging to the boundary constraint

    // mark_domains(triangulation);

    // Remesh

    std::list<CDT::Point> seeds;

    for (auto hit : holes) {
        compas::RowMatrixXd H = hit;

        double n = (double) H.rows();

        double x = H.block(0, 0, H.rows(), 1).sum() / n;
        double y = H.block(0, 1, H.rows(), 1).sum() / n;

        seeds.push_back(CDT::Point(x, y));
    }

    Criteria criteria;

    if (maxlength > 0.0) {
        criteria = Criteria(0.0, maxlength);
    }
    else {
        criteria = Criteria();
    }

    CGAL::refine_Delaunay_mesh_2(triangulation, seeds.begin(), seeds.end(), criteria);
    CGAL::lloyd_optimize_mesh_2(triangulation,
                                CGAL::parameters::max_iteration_number = 10,
                                CGAL::parameters::seeds_begin = seeds.begin(),
                                CGAL::parameters::seeds_end = seeds.end());

    // CGAL::make_conforming_Delaunay_2(triangulation);
    // CGAL::make_conforming_Gabriel_2(triangulation);

    // Count the number of faces belonging to the boundary domain

    int f = 0;
    for (CDT::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++) {
        if (fit->is_in_domain()) {
            f++;
        }
    }

    // Prepare result matrices

    compas::RowMatrixXd TV(triangulation.number_of_vertices(), 3);
    compas::RowMatrixXi TF(f, 3);

    // Make vertex index map

    std::unordered_map<CDT::Vertex_handle, unsigned> vertex_index;

    // Load the vertices into the result

    int i = 0;
    for (CDT::Finite_vertices_iterator vit = triangulation.finite_vertices_begin(); vit != triangulation.finite_vertices_end(); vit++) {
        CDT::Vertex_handle vertex = vit;
        CDT::Point point = vertex->point();

        vertex_index.insert({vertex, i});

        TV(i, 0) = point.hx();
        TV(i, 1) = point.hy();
        TV(i, 2) = 0.0;

        i++;
    }

    // Load the faces into the result

    int j = 0;
    for (CDT::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++) {
        CDT::Face_handle face = fit;

        // if (face->info().in_domain()) {
        if (fit->is_in_domain()) {
            CDT::Vertex_handle a = face->vertex(0);
            CDT::Vertex_handle b = face->vertex(1);
            CDT::Vertex_handle c = face->vertex(2);

            TF(j, 0) = vertex_index[a];
            TF(j, 1) = vertex_index[b];
            TF(j, 2) = vertex_index[c];

            j++;
        }
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(TV, TF);
    return result;
}


// /**
//  * Conforming delaunay triangulation of a given boundary
//  * with internal holes and constraint curves.
//  *
//  * @param B The vertices of the boundary.
//  * @param holes A list of holes in the triangulation.
//  * @param curves A list of internal polyline constraints.
//  */
// std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
// pmp_conforming_delaunay_triangulation(
//     Eigen::Ref<const compas::RowMatrixXd> & B,
//     std::vector< Eigen::Ref<const compas::RowMatrixXd> > & holes,
//     std::vector< Eigen::Ref<const compas::RowMatrixXd> > & curves)
// {
//     std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> cdt = pmp_constrained_delaunay_triangulation(B, holes, curves);

//     std::list<CDT::Point> seeds;

//     for (auto hit : holes) {
//         compas::RowMatrixXd H = hit;

//         double n = (double) H.rows();

//         double x = H.block(0, 0, H.rows(), 1).sum() / n;
//         double y = H.block(0, 1, H.rows(), 1).sum() / n;

//         seeds.push_back(CDT::Point(x, y));
//     }

//     CGAL::refine_Delaunay_mesh_2(cdt, seeds.begin(), seeds.end(), Criteria());
// }


// ===========================================================================
// ===========================================================================
// ===========================================================================
// PyBind
// ===========================================================================
// ===========================================================================
// ===========================================================================

void init_triangulations(py::module & m) {
    py::module submodule = m.def_submodule("triangulations");

    submodule.def(
        "delaunay_triangulation",
        &pmp_delaunay_triangulation,
        py::arg("V").noconvert()
    );

    // submodule.def(
    //     "constrained_delaunay_triangulation",
    //     &pmp_constrained_delaunay_triangulation,
    //     py::arg("V").noconvert(),
    //     py::arg("E").noconvert()
    // );

    submodule.def(
        "constrained_delaunay_triangulation",
        &pmp_constrained_delaunay_triangulation,
        py::arg("B").noconvert(),
        py::arg("holes").noconvert(),
        py::arg("curves").noconvert(),
        py::arg("minangle") = 0.0,
        py::arg("maxlength") = 0.0
    );
};
