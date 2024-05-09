
#include "straight_skeleton_2.h"
#include <CGAL/Polygon_2.h>
#include <CGAL/create_straight_skeleton_2.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef K::Point_2 Point;
typedef CGAL::Polygon_2<K> Polygon_2;
typedef CGAL::Straight_skeleton_2<K> Ss;
typedef boost::shared_ptr<Ss> SsPtr;
typedef CGAL::Straight_skeleton_2<K>::Halfedge_const_handle Halfedge_const_handle;
typedef CGAL::Straight_skeleton_2<K>::Vertex_const_handle Vertex_const_handle;

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
};
