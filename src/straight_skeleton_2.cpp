#include "straight_skeleton_2.h"

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef K::Point_2 Point;
typedef CGAL::Polygon_2<K> Polygon_2;
typedef CGAL::Polygon_with_holes_2<K> Polygon_with_holes;
typedef CGAL::Straight_skeleton_2<K> Ss;
typedef Ss::Halfedge_const_handle Halfedge_const_handle;
typedef Ss::Vertex_const_handle Vertex_const_handle;

// Change from boost to std shared_ptr
typedef std::shared_ptr<Ss> SsPtr;
typedef std::shared_ptr<Polygon_2> PolygonPtr;
typedef std::vector<PolygonPtr> PolygonPtrVector;
typedef std::shared_ptr<Polygon_with_holes> PolygonWithHolesPtr;
typedef std::vector<PolygonWithHolesPtr> PolygonWithHolesPtrVector;

std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>>
mesh_data_from_skeleton(std::shared_ptr<Ss> &iss)
{
    std::size_t v = iss->size_of_vertices();
    std::size_t e = iss->size_of_halfedges() / 2; // halfedges are stored twice

    compas::RowMatrixXd Mv(v, 3);
    std::vector<int> Mvi; // to save the vertex ids
    compas::RowMatrixXi Me(e, 2);
    std::vector<int> Mei; // to save the edge type: 0: inner bisector, 1: bisector, 2: boundary

    std::size_t i = 0;
    for (auto hit = iss->vertices_begin(); hit != iss->vertices_end(); ++hit)
    {
        const Vertex_const_handle vh = hit;
        Mv(i, 0) = (double)vh->point().x();
        Mv(i, 1) = (double)vh->point().y();
        Mv(i, 2) = 0;
        Mvi.push_back((int)vh->id());
        i++;
    }
    i = 0;
    for (auto hit = iss->halfedges_begin(); hit != iss->halfedges_end(); ++hit)
    {
        const Halfedge_const_handle h = hit;
        const Vertex_const_handle &v1 = h->vertex();
        const Vertex_const_handle &v2 = h->opposite()->vertex();

        if (&*v1 < &*v2)
        {
            Me(i, 0) = (int)v1->id();
            Me(i, 1) = (int)v2->id();

            if (h->is_inner_bisector())
            {
                Mei.push_back(0);
            }
            else if (h->is_bisector())
            {
                Mei.push_back(1);
            }
            else
            {
                Mei.push_back(2);
            }
            i++;
        }
    }
    std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>> result = std::make_tuple(Mv, Mvi, Me, Mei);
    return result;
}

compas::RowMatrixXd 
polygon_to_data(Polygon_2 const& poly)
{
    std::size_t n = poly.size();
    compas::RowMatrixXd points(n, 3);
    int j = 0;
    for(typename Polygon_2::Vertex_const_iterator vi = poly.vertices_begin() ; vi != poly.vertices_end() ; ++ vi){
        points(j, 0) = (double)(*vi).x();
        points(j, 1) = (double)(*vi).y();
        points(j, 2) = 0;
        j++;
    }
    return points;
}

std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>
polygon_with_holes_to_data(Polygon_with_holes const& polywh)
{
    std::vector<compas::RowMatrixXd> holes;
    compas::RowMatrixXd points = polygon_to_data(polywh.outer_boundary());
    for(typename Polygon_with_holes::Hole_const_iterator hi = polywh.holes_begin() ; hi != polywh.holes_end() ; ++ hi){
        compas::RowMatrixXd hole = polygon_to_data(*hi);
        holes.push_back(hole);
    }
    std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>> result = std::make_tuple(points, holes);
    return result;
}

Polygon_2
data_to_polygon(Eigen::Ref<compas::RowMatrixXd> V)
{
    Polygon_2 poly;
    for (int i = 0; i < V.rows(); i++){
        poly.push_back(Point(V(i, 0), V(i, 1)));
    }
    return poly;
}

Polygon_with_holes
data_to_polygon_with_holes(
    Eigen::Ref<compas::RowMatrixXd> V,
    const std::vector<Eigen::Ref<compas::RowMatrixXd>> holes)
{
    Polygon_2 outer = data_to_polygon(V);
    Polygon_with_holes poly(outer);
    for (auto hit : holes){
        compas::RowMatrixXd H = hit;
        //Polygon_2 hole = data_to_polygon(*H); // why does this not work?
        Polygon_2 hole;
        for (int i = 0; i < H.rows(); i++){
            hole.push_back(Point(H(i, 0), H(i, 1)));
        }
        poly.add_hole(hole);
    }
    return poly;
}

std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>>
pmp_create_interior_straight_skeleton(
    Eigen::Ref<compas::RowMatrixXd> V)
{
    Polygon_2 poly = data_to_polygon(V);
    SsPtr iss = CGAL::create_interior_straight_skeleton_2(poly.vertices_begin(), poly.vertices_end());
    return mesh_data_from_skeleton(iss);
};

std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>>
pmp_create_interior_straight_skeleton_with_holes(
    Eigen::Ref<compas::RowMatrixXd> V,
    const std::vector<Eigen::Ref<compas::RowMatrixXd>> &holes)
{
    Polygon_with_holes poly = data_to_polygon_with_holes(V, holes);
    SsPtr iss = CGAL::create_interior_straight_skeleton_2(poly);
    return mesh_data_from_skeleton(iss);
}

std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_inner(Eigen::Ref<compas::RowMatrixXd> V, double &offset)
{
    Polygon_2 poly = data_to_polygon(V);
    PolygonPtrVector offset_polygons = CGAL::create_interior_skeleton_and_offset_polygons_2(offset, poly);

    std::vector<compas::RowMatrixXd> result;
    for(typename PolygonPtrVector::const_iterator pi = offset_polygons.begin() ; pi != offset_polygons.end() ; ++ pi ){
        compas::RowMatrixXd points = polygon_to_data(**pi);
        result.push_back(points);
    }
    return result;
}

std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_inner_with_holes(
    Eigen::Ref<compas::RowMatrixXd> V,
    const std::vector<Eigen::Ref<compas::RowMatrixXd>> &holes,
    double &offset)
{

    Polygon_with_holes poly = data_to_polygon_with_holes(V, holes);
    PolygonWithHolesPtrVector offset_polygons = CGAL::create_interior_skeleton_and_offset_polygons_with_holes_2(offset, poly);

    std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> result;
    for(typename PolygonWithHolesPtrVector::const_iterator pi = offset_polygons.begin() ; pi != offset_polygons.end() ; ++ pi ){
        std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>> polywh_data = polygon_with_holes_to_data(**pi);
        result.push_back(polywh_data);
    }
    return result;
}

std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_outer(Eigen::Ref<compas::RowMatrixXd> V, double &offset)
{
    Polygon_2 poly = data_to_polygon(V);
    PolygonPtrVector offset_polygons = CGAL::create_exterior_skeleton_and_offset_polygons_2(offset, poly);

    std::vector<compas::RowMatrixXd> result;
    for(typename PolygonPtrVector::const_iterator pi = offset_polygons.begin() ; pi != offset_polygons.end() ; ++ pi ){
        compas::RowMatrixXd points = polygon_to_data(**pi);
        result.push_back(points);
    }
    return result;
}

std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_outer_with_holes(
    Eigen::Ref<compas::RowMatrixXd> V,
    const std::vector<Eigen::Ref<compas::RowMatrixXd>> &holes,
    double &offset)
{
    Polygon_with_holes poly = data_to_polygon_with_holes(V, holes);
    PolygonWithHolesPtrVector offset_polygons = CGAL::create_exterior_skeleton_and_offset_polygons_with_holes_2(offset, poly);

    std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> result;
    for(typename PolygonWithHolesPtrVector::const_iterator pi = offset_polygons.begin() ; pi != offset_polygons.end() ; ++ pi ){
        std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>> polywh_data = polygon_with_holes_to_data(**pi);
        result.push_back(polywh_data);
    }
    return result;
}

std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_inner(
    Eigen::Ref<compas::RowMatrixXd> V,
    double &offset,
    Eigen::Ref<compas::RowMatrixXd> weights)
{
    Polygon_2 poly = data_to_polygon(V);
    std::vector<double> weights_vec;
    for (int i = 0; i < weights.rows(); i++)
    {
        weights_vec.push_back(weights(i, 0));
    }
    SsPtr iss = CGAL::create_interior_weighted_straight_skeleton_2(poly, weights_vec);
    PolygonPtrVector offset_polygons = CGAL::create_offset_polygons_2<Polygon_2>(offset, *iss);

    std::vector<compas::RowMatrixXd> result;
    for(typename PolygonPtrVector::const_iterator pi = offset_polygons.begin() ; pi != offset_polygons.end() ; ++ pi ){
        compas::RowMatrixXd points = polygon_to_data(**pi);
        result.push_back(points);
    }
    return result;
}

std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_outer(
    Eigen::Ref<compas::RowMatrixXd> V,
    double &offset,
    Eigen::Ref<compas::RowMatrixXd> weights)
{
    Polygon_2 poly = data_to_polygon(V);
    std::vector<double> weights_vec;
    for (int i = 0; i < weights.rows(); i++)
    {
        weights_vec.push_back(weights(i, 0));
    }
    SsPtr iss = CGAL::create_exterior_weighted_straight_skeleton_2(offset, weights_vec, poly);
    PolygonPtrVector offset_polygons = CGAL::create_offset_polygons_2<Polygon_2>(offset, *iss);

    std::vector<compas::RowMatrixXd> result;
    for(typename PolygonPtrVector::const_iterator pi = offset_polygons.begin() ; pi != offset_polygons.end() ; ++ pi ){
        compas::RowMatrixXd points = polygon_to_data(**pi);
        result.push_back(points);
    }
    return result;
}

void init_straight_skeleton_2(nb::module_& m) {
    auto submodule = m.def_submodule("straight_skeleton_2");

}



// void init_straight_skeleton_2(pybind11::module &m)
// {
//     pybind11::module submodule = m.def_submodule("straight_skeleton_2");

//     submodule.def(
//         "create_interior_straight_skeleton",
//         &pmp_create_interior_straight_skeleton,
//         pybind11::arg("V").noconvert());

//     submodule.def(
//         "create_interior_straight_skeleton_with_holes",
//         &pmp_create_interior_straight_skeleton_with_holes,
//         pybind11::arg("V").noconvert(),
//         pybind11::arg("holes").noconvert());

//     submodule.def(
//         "create_offset_polygons_2_inner",
//         &pmp_create_offset_polygons_2_inner,
//         pybind11::arg("V").noconvert(),
//         pybind11::arg("offset").noconvert());

//     submodule.def(
//         "create_offset_polygons_2_inner_with_holes",
//         &pmp_create_offset_polygons_2_inner_with_holes,
//         pybind11::arg("V").noconvert(),
//         pybind11::arg("holes").noconvert(),
//         pybind11::arg("offset").noconvert());

//     submodule.def(
//         "create_offset_polygons_2_outer",
//         &pmp_create_offset_polygons_2_outer,
//         pybind11::arg("V").noconvert(),
//         pybind11::arg("offset").noconvert());

//     submodule.def(
//         "create_offset_polygons_2_outer_with_holes",
//         &pmp_create_offset_polygons_2_outer_with_holes,
//         pybind11::arg("V").noconvert(),
//         pybind11::arg("holes").noconvert(),
//         pybind11::arg("offset").noconvert());

//     submodule.def(
//         "create_weighted_offset_polygons_2_inner",
//         &pmp_create_weighted_offset_polygons_2_inner,
//         pybind11::arg("V").noconvert(),
//         pybind11::arg("offset").noconvert(),
//         pybind11::arg("weights").noconvert());

//     submodule.def(
//         "create_weighted_offset_polygons_2_outer",
//         &pmp_create_weighted_offset_polygons_2_outer,
//         pybind11::arg("V").noconvert(),
//         pybind11::arg("offset").noconvert(),
//         pybind11::arg("weights").noconvert());
// };