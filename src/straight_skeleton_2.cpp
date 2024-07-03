
#include "straight_skeleton_2.h"
#include <CGAL/Polygon_2.h>
#include <CGAL/create_straight_skeleton_2.h>
#include <CGAL/create_straight_skeleton_from_polygon_with_holes_2.h>
#include <CGAL/create_offset_polygons_2.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef K::Point_2 Point;
typedef CGAL::Polygon_2<K> Polygon_2;
typedef CGAL::Polygon_with_holes_2<K> Polygon_with_holes;
typedef CGAL::Straight_skeleton_2<K> Ss;
typedef boost::shared_ptr<Ss> SsPtr;
typedef CGAL::Straight_skeleton_2<K>::Halfedge_const_handle Halfedge_const_handle;
typedef CGAL::Straight_skeleton_2<K>::Vertex_const_handle Vertex_const_handle;
typedef boost::shared_ptr<Polygon_2> PolygonPtr;
typedef std::vector<PolygonPtr> PolygonPtrVector;

compas::Edges pmp_create_interior_straight_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V)
{
    Polygon_2 poly;
    for (int i = 0; i < V.rows(); i++)
    {
        poly.push_back(Point(V(i, 0), V(i, 1)));
    }
    SsPtr iss = CGAL::create_interior_straight_skeleton_2(poly.vertices_begin(), poly.vertices_end());
    compas::Edges edgelist;
    for(auto hit = iss->halfedges_begin(); hit != iss->halfedges_end(); ++hit){
        const Halfedge_const_handle h = hit;
        if(!h->is_bisector()){
            continue;
        }
        const Vertex_const_handle& v1 = h->vertex();
        const Vertex_const_handle& v2 = h->opposite()->vertex();
        if(&*v1 < &*v2){
            std::vector<double> s_vec = {v1->point().x(), v1->point().y(), 0};
            std::vector<double> t_vec = {v2->point().x(), v2->point().y(), 0};
            compas::Edge edge = std::make_tuple(s_vec, t_vec);
            edgelist.push_back(edge);
        }

    }
    return edgelist;
};

compas::Edges pmp_create_interior_straight_skeleton_with_holes(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    std::vector<Eigen::Ref<const compas::RowMatrixXd>> &holes)
{
    Polygon_2 outer;
    for (int i = 0; i < V.rows(); i++)
    {
        outer.push_back(Point(V(i, 0), V(i, 1)));
    }
    Polygon_with_holes poly(outer);


    for (auto hit : holes)
    {
        compas::RowMatrixXd H = hit;
        Polygon_2 hole;
        for (int i = 0; i < H.rows(); i++)
        {
            hole.push_back(Point(H(i, 0), H(i, 1)));
        }
        poly.add_hole(hole);

    }

    SsPtr iss = CGAL::create_interior_straight_skeleton_2(poly);
    compas::Edges edgelist;
    for(auto hit = iss->halfedges_begin(); hit != iss->halfedges_end(); ++hit){
        const Halfedge_const_handle h = hit;
        if(!h->is_bisector()){
            continue;
        }
        const Vertex_const_handle& v1 = h->vertex();
        const Vertex_const_handle& v2 = h->opposite()->vertex();
        if(&*v1 < &*v2){
            std::vector<double> s_vec = {v1->point().x(), v1->point().y(), 0};
            std::vector<double> t_vec = {v2->point().x(), v2->point().y(), 0};
            compas::Edge edge = std::make_tuple(s_vec, t_vec);
            edgelist.push_back(edge);
        }

    }
    return edgelist;

}

std::vector<compas::RowMatrixXd> pmp_create_offset_polygons_2_inner(Eigen::Ref<const compas::RowMatrixXd> &V, double &offset){
    Polygon_2 poly;
    for (int i = 0; i < V.rows(); i++){
        poly.push_back(Point(V(i, 0), V(i, 1)));
    }
    PolygonPtrVector offset_polygons = CGAL::create_interior_skeleton_and_offset_polygons_2(offset, poly);

    std::vector<compas::RowMatrixXd> result;
    for(auto pi = offset_polygons.begin(); pi != offset_polygons.end(); ++pi){
        std::size_t n = (*pi)->size();
        compas::RowMatrixXd points(n, 3);
        int j = 0;
        for (auto vi = (*pi)->vertices_begin(); vi != (*pi)->vertices_end(); ++vi){
            points(j, 0) = (double)(*vi).x();
            points(j, 1) = (double)(*vi).y();
            points(j, 2) = 0;
            j++;
        }
        result.push_back(points);
    }
    return result;
}

std::vector<compas::RowMatrixXd> pmp_create_offset_polygons_2_outer(Eigen::Ref<const compas::RowMatrixXd> &V, double &offset){
    Polygon_2 poly;
    for (int i = 0; i < V.rows(); i++){
        poly.push_back(Point(V(i, 0), V(i, 1)));
    }
    PolygonPtrVector offset_polygons = CGAL::create_exterior_skeleton_and_offset_polygons_2(offset, poly);

    std::vector<compas::RowMatrixXd> result;
    for(auto pi = offset_polygons.begin(); pi != offset_polygons.end(); ++pi){
        std::size_t n = (*pi)->size();
        compas::RowMatrixXd points(n, 3);
        int j = 0;
        for (auto vi = (*pi)->vertices_begin(); vi != (*pi)->vertices_end(); ++vi){
            points(j, 0) = (double)(*vi).x();
            points(j, 1) = (double)(*vi).y();
            points(j, 2) = 0;
            j++;
        }
        result.push_back(points);
    }
    return result;
}

// ===========================================================================
// PyBind11
// ===========================================================================

void init_straight_skeleton_2(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("straight_skeleton_2");

    submodule.def(
        "create_interior_straight_skeleton",
        &pmp_create_interior_straight_skeleton,
        pybind11::arg("V").noconvert());

    submodule.def(
        "create_interior_straight_skeleton_with_holes",
        &pmp_create_interior_straight_skeleton_with_holes,
        pybind11::arg("V").noconvert(),
        pybind11::arg("holes").noconvert());

    submodule.def(
        "create_offset_polygons_2_inner",
        &pmp_create_offset_polygons_2_inner,
        pybind11::arg("V").noconvert(),
        pybind11::arg("offset").noconvert());

    submodule.def(
        "create_offset_polygons_2_outer",
        &pmp_create_offset_polygons_2_outer,
        pybind11::arg("V").noconvert(),
        pybind11::arg("offset").noconvert());
};
