#include "skeletonization.h"
#include <CGAL/Mean_curvature_flow_skeletonization.h>
#include <CGAL/boost/graph/split_graph_into_polylines.h>

typedef CGAL::Mean_curvature_flow_skeletonization<Mesh> Skeletonization;
typedef Skeletonization::Skeleton Skeleton;

typedef boost::graph_traits<Mesh>::vertex_descriptor vertex_descriptor;

typedef Skeleton::vertex_descriptor Skeleton_vertex;
typedef Skeleton::edge_descriptor Skeleton_edge;

struct Split_polylines
{
    const Skeleton &skeleton;
    Polylines &polylines;
    Polyline polyline;
    int polyline_index = 0;
    int polyline_size;

    Split_polylines(const Skeleton &skeleton, Polylines &polylines)
        : skeleton(skeleton), polylines(polylines)
    {
    }

    void start_new_polyline()
    {
        polyline = Polyline();
    }

    void add_node(Skeleton_vertex v)
    {
        polyline.push_back(skeleton[v].point);
    }

    void end_polyline()
    {
        polylines.push_back(polyline);
    }
};

Edges pmp_mesh_skeleton(
    Eigen::Ref<const compas::RowMatrixXd> &V,
    Eigen::Ref<const compas::RowMatrixXi> &F)
{

    Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    Skeleton skeleton;
    Skeletonization mcs(mesh);

    // mcs.contract_geometry();
    // mcs.collapse_edges();
    // mcs.split_faces();
    // mcs.detect_degeneracies();

    // mcs.contract();

    mcs.contract_until_convergence();
    mcs.convert_to_skeleton(skeleton);

    // Polylines polylines;
    // Split_polylines splitter(skeleton, polylines);
    // CGAL::split_graph_into_polylines(skeleton, splitter);

    Edges edgelist;

    for (Skeleton_edge e : CGAL::make_range(edges(skeleton)))
    {
        const Kernel::Point_3 &s = skeleton[source(e, skeleton)].point;
        const Kernel::Point_3 &t = skeleton[target(e, skeleton)].point;

        std::vector<double> s_vec = {s.x(), s.y(), s.z()};
        std::vector<double> t_vec = {t.x(), t.y(), t.z()};
        Edge edge = std::make_tuple(s_vec, t_vec);

        edgelist.push_back(edge);
    }

    return edgelist;
};

// ===========================================================================
// PyBind11
// ===========================================================================

void init_skeletonization(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("skeletonization");

    submodule.def(
        "mesh_skeleton",
        &pmp_mesh_skeleton,
        pybind11::arg("V").noconvert(),
        pybind11::arg("F").noconvert());
};
