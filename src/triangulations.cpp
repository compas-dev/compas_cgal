#include "triangulations.h"

#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/Constrained_triangulation_2.h>
#include <CGAL/Constrained_Delaunay_triangulation_2.h>
#include <CGAL/Triangulation_vertex_base_with_info_2.h>

using DT = CGAL::Delaunay_triangulation_2<Kernel>;
using DT_Point = DT::Point;
using DT_Vertex = DT::Vertex_handle;

using CDT_VertexBase = CGAL::Triangulation_vertex_base_with_info_2<unsigned, Kernel>;
using CDT_DS = CGAL::Triangulation_data_structure_2<CDT_VertexBase>;
using CDT = CGAL::Constrained_Delaunay_triangulation_2<Kernel, CDT_DS>;
using CDT_Point = CDT::Point;
using CDT_Vertex = CDT::Vertex_handle;

namespace py = pybind11;

compas::RowMatrixXi
pmp_delaunay_triangulation(
    Eigen::Ref<const compas::RowMatrixXd> & V)
{
    DT dt;

    int v = V.rows();

    std::vector< std::pair<Point, unsigned> > points(v);
    // std::vector< Vertex > vertex_handles(v);

    for (int i=0; i < v; i++) {
        points[i] = std::make_pair(Point(V(i, 0), V(i, 1)), i);
    }

    cdt.insert(points.begin(), points.end());

    // for (int i=0; i < v; i++) {
    //     std::pair<Point, unsigned> point;
    //     point = std::make_pair(Point(V(i, 0), V(i, 1)), i);
    //     vertex_handles[i] = cdt.insert(point);
    // }

    for (int i=0; i < e; i++) {
        cdt.insert_constraint(vertex_handles[E(i, 0)], vertex_handles[E(i, 1)]);
    }

    // int cdt_v = cdt.number_of_vertices();
    int cdt_f = cdt.number_of_faces();

    compas::RowMatrixXi RF(cdt_f, 3);

    // int i = 0;
    // for (auto point = cdt.points_begin(); point != cdt.points_end(); point++) {
    //     RV(i, 0) = point->hx();
    //     RV(i, 1) = point->hy();
    //     i++;
    // }

    int j = 0;
    for (CDT::Finite_faces_iterator fit = cdt.finite_faces_begin(); fit != cdt.finite_faces_end(); fit++) {
        CDT::Face_handle face = fit;
        RF(j, 0) = face->vertex(0)->info();
        RF(j, 1) = face->vertex(1)->info();
        RF(j, 2) = face->vertex(2)->info();
        j++;
    }

    // std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(RV, RF);
    return RF;
}

void
pmp_constrained_delaunay_triangulation(
    Eigen::Ref<const compas::RowMatrixXd> & V,
    Eigen::Ref<const compas::RowMatrixXi> & E)
{
    // CDT cdt;

    // int v = V.rows();
    // int e = E.rows();

    // std::vector< std::pair<Point, unsigned> > points(v);
    // // std::vector< Vertex > vertex_handles(v);

    // for (int i=0; i < v; i++) {
    //     points[i] = std::make_pair(Point(V(i, 0), V(i, 1)), i);
    // }

    // cdt.insert(points.begin(), points.end());

    // // for (int i=0; i < v; i++) {
    // //     std::pair<Point, unsigned> point;
    // //     point = std::make_pair(Point(V(i, 0), V(i, 1)), i);
    // //     vertex_handles[i] = cdt.insert(point);
    // // }

    // for (int i=0; i < e; i++) {
    //     cdt.insert_constraint(vertex_handles[E(i, 0)], vertex_handles[E(i, 1)]);
    // }

    // // int cdt_v = cdt.number_of_vertices();
    // int cdt_f = cdt.number_of_faces();

    // compas::RowMatrixXi RF(cdt_f, 3);

    // // int i = 0;
    // // for (auto point = cdt.points_begin(); point != cdt.points_end(); point++) {
    // //     RV(i, 0) = point->hx();
    // //     RV(i, 1) = point->hy();
    // //     i++;
    // // }

    // int j = 0;
    // for (CDT::Finite_faces_iterator fit = cdt.finite_faces_begin(); fit != cdt.finite_faces_end(); fit++) {
    //     CDT::Face_handle face = fit;
    //     RF(j, 0) = face->vertex(0)->info();
    //     RF(j, 1) = face->vertex(1)->info();
    //     RF(j, 2) = face->vertex(2)->info();
    //     j++;
    // }

    // // std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(RV, RF);
    // return RF;
}

void init_triangulations(py::module & m) {
    py::module submodule = m.def_submodule("triangulations");

    submodule.def(
        "constrained_delaunay_triangulation",
        &pmp_constrained_delaunay_triangulation,
        py::arg("V").noconvert(),
        py::arg("E").noconvert()
    );
};
