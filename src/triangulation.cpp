#include "triangulation.h"


struct FaceInfo
{
    FaceInfo(){};

    int nesting_level;

    bool in_domain()
    {
        return nesting_level % 2 == 1;
    }
};

using DelaunayPolygon = CGAL::Polygon_2<compas::Kernel>;

using VertexBase1 = CGAL::Triangulation_vertex_base_with_info_2<unsigned, compas::Kernel>;
using TDS1 = CGAL::Triangulation_data_structure_2<VertexBase1>;
using DT = CGAL::Delaunay_triangulation_2<compas::Kernel, TDS1>;

using VertexBase2 = CGAL::Triangulation_vertex_base_2<compas::Kernel>;
using _FaceBase2 = CGAL::Triangulation_face_base_with_info_2<FaceInfo, compas::Kernel>;
using FaceBase2 = CGAL::Constrained_triangulation_face_base_2<compas::Kernel, _FaceBase2>;
using TDS2 = CGAL::Triangulation_data_structure_2<VertexBase2, FaceBase2>;
using CDT2 = CGAL::Constrained_Delaunay_triangulation_2<compas::Kernel, TDS2>;

using VertexBase3 = CGAL::Delaunay_mesh_vertex_base_2<compas::Kernel>;
using FaceBase3 = CGAL::Delaunay_mesh_face_base_2<compas::Kernel>;
using TDS3 = CGAL::Triangulation_data_structure_2<VertexBase3, FaceBase3>;
using Itag = CGAL::Exact_predicates_tag;
using CDT3 = CGAL::Constrained_Delaunay_triangulation_2<compas::Kernel, TDS3, Itag>;
using Criteria = CGAL::Delaunay_mesh_size_criteria_2<CDT3>;

// ===========================================================================
// ===========================================================================
// ===========================================================================
// Delaunay
// ===========================================================================
// ===========================================================================
// ===========================================================================

compas::RowMatrixXi
pmp_delaunay_triangulation(Eigen::Ref<compas::RowMatrixXd> V)
{
    DT triangulation;

    std::vector<std::pair<DT::Point, unsigned>> points(V.rows());

    for (int i = 0; i < V.rows(); i++)
    {
        DT::Point point = DT::Point(V(i, 0), V(i, 1));
        points[i] = std::make_pair(point, i);
    }

    triangulation.insert(points.begin(), points.end());

    compas::RowMatrixXi F(triangulation.number_of_faces(), 3);

    int j = 0;
    for (DT::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++)
    {
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
// Regular
// ===========================================================================
// ===========================================================================
// ===========================================================================

// ===========================================================================
// ===========================================================================
// ===========================================================================
// Domains
// ===========================================================================
// ===========================================================================
// ===========================================================================

void mark_domains(CDT2 &triangulation,
                  CDT2::Face_handle start,
                  int index,
                  std::list<CDT2::Edge> &border)
{
    if (start->info().nesting_level != -1)
    {
        return;
    }

    std::list<CDT2::Face_handle> queue;
    queue.push_back(start);

    while (!queue.empty())
    {
        CDT2::Face_handle face = queue.front();

        queue.pop_front();

        if (face->info().nesting_level == -1)
        {
            face->info().nesting_level = index;

            for (int i = 0; i < 3; i++)
            {
                CDT2::Edge edge(face, i);
                CDT2::Face_handle nbr = face->neighbor(i);

                if (nbr->info().nesting_level == -1)
                {
                    if (triangulation.is_constrained(edge))
                    {
                        border.push_back(edge);
                    }
                    else
                    {
                        queue.push_back(nbr);
                    }
                }
            }
        }
    }
}

void mark_domains(CDT2 &triangulation)
{
    for (CDT2::Face_handle face : triangulation.all_face_handles())
    {
        face->info().nesting_level = -1;
    }

    std::list<CDT2::Edge> border;

    mark_domains(triangulation, triangulation.infinite_face(), 0, border);

    while (!border.empty())
    {
        CDT2::Edge edge = border.front();
        border.pop_front();

        CDT2::Face_handle nbr = edge.first->neighbor(edge.second);

        if (nbr->info().nesting_level == -1)
        {
            mark_domains(triangulation, nbr, edge.first->info().nesting_level + 1, border);
        }
    }
}

// ===========================================================================
// ===========================================================================
// ===========================================================================
// Constrained / Conforming Delaunay
// ===========================================================================
// ===========================================================================
// ===========================================================================

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_constrained_delaunay_triangulation(
    Eigen::Ref<compas::RowMatrixXd> B,
    Eigen::Ref<compas::RowMatrixXd> P,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    bool is_conforming
    )
{
    CDT2 triangulation;

    // Add specific (isolated) points

    std::vector<CDT2::Point> points(P.rows());

    for (int i = 0; i < P.rows(); i++)
    {
        points[i] = CDT2::Point(P(i, 0), P(i, 1));
    }

    triangulation.insert(points.begin(), points.end());

    // Add the boundary as polygon constraint.

    DelaunayPolygon boundary;

    for (int i = 0; i < B.rows(); i++)
    {
        boundary.push_back(CDT2::Point(B(i, 0), B(i, 1)));
    }

    triangulation.insert_constraint(boundary.vertices_begin(), boundary.vertices_end(), true);

    // Add the holes as polygon constraints.

    for (auto hit : holes)
    {
        compas::RowMatrixXd H = hit;

        DelaunayPolygon hole;

        for (int i = 0; i < H.rows(); i++)
        {
            hole.push_back(CDT2::Point(H(i, 0), H(i, 1)));
        }

        triangulation.insert_constraint(hole.vertices_begin(), hole.vertices_end(), true);
    }

    // Add the curves as polyline constraints.

    for (auto cit : curves)
    {
        compas::RowMatrixXd C = cit;

        std::vector<CDT2::Point> curve(C.rows());

        for (int i = 0; i < C.rows(); i++)
        {
            curve[i] = CDT2::Point(C(i, 0), C(i, 1));
        }

        triangulation.insert_constraint(curve.begin(), curve.end());
    }

    if (is_conforming)
    {
        CGAL::make_conforming_Delaunay_2(triangulation);
        //CGAL::make_conforming_Gabriel_2(triangulation);
    }

    // Mark the faces belonging to the boundary constraint

    mark_domains(triangulation);

    // Count the number of faces belonging to the boundary domain

    int f = 0;
    for (CDT2::Face_handle face : triangulation.finite_face_handles())
    {
        if (face->info().in_domain())
        {
            f++;
        }
    }

    // Prepare result matrices

    compas::RowMatrixXd TV(triangulation.number_of_vertices(), 3);
    compas::RowMatrixXi TF(f, 3);

    // Make vertex index map

    std::unordered_map<CDT2::Vertex_handle, unsigned> vertex_index;

    // Load the vertices into the result

    int i = 0;
    for (CDT2::Vertex_handle vertex : triangulation.finite_vertex_handles())
    {
        CDT2::Point point = vertex->point();

        vertex_index.insert({vertex, i});

        TV(i, 0) = point.hx();
        TV(i, 1) = point.hy();
        TV(i, 2) = 0.0;

        i++;
    }

    // Load the faces into the result

    int j = 0;
    for (CDT2::Face_handle face : triangulation.finite_face_handles())
    {
        if (face->info().in_domain())
        {
            CDT2::Vertex_handle a = face->vertex(0);
            CDT2::Vertex_handle b = face->vertex(1);
            CDT2::Vertex_handle c = face->vertex(2);

            TF(j, 0) = vertex_index[a];
            TF(j, 1) = vertex_index[b];
            TF(j, 2) = vertex_index[c];

            j++;
        }
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(TV, TF);
    return result;
}

// ===========================================================================
// ===========================================================================
// ===========================================================================
// Constrained Delaunay compas::Mesh
// ===========================================================================
// ===========================================================================
// ===========================================================================

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_refined_delaunay_mesh(
    Eigen::Ref<compas::RowMatrixXd> B,
    Eigen::Ref<compas::RowMatrixXd> P,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    double minangle,
    double maxlength,
    bool is_optimized)
{
    CDT3 triangulation;

    // Add specific (isolated) points

    std::vector<CDT3::Point> points(P.rows());

    for (int i = 0; i < P.rows(); i++)
    {
        points[i] = CDT3::Point(P(i, 0), P(i, 1));
    }

    triangulation.insert(points.begin(), points.end());

    // Add the boundary as polygon constraint.

    DelaunayPolygon boundary;

    for (int i = 0; i < B.rows(); i++)
    {
        boundary.push_back(CDT3::Point(B(i, 0), B(i, 1)));
    }

    triangulation.insert_constraint(boundary.vertices_begin(), boundary.vertices_end(), true);

    // Add the holes as polygon constraints.

    for (auto hit : holes)
    {
        compas::RowMatrixXd H = hit;

        DelaunayPolygon hole;

        for (int i = 0; i < H.rows(); i++)
        {
            hole.push_back(CDT3::Point(H(i, 0), H(i, 1)));
        }

        triangulation.insert_constraint(hole.vertices_begin(), hole.vertices_end(), true);
    }

    // Add the curves as polyline constraints.

    for (auto cit : curves)
    {
        compas::RowMatrixXd C = cit;

        std::vector<CDT3::Point> curve(C.rows());

        for (int i = 0; i < C.rows(); i++)
        {
            curve[i] = CDT3::Point(C(i, 0), C(i, 1));
        }

        triangulation.insert_constraint(curve.begin(), curve.end());
    }

    // Remesh

    std::list<CDT3::Point> seeds;

    for (auto hit : holes)
    {
        compas::RowMatrixXd H = hit;

        double n = (double)H.rows();

        double x = H.block(0, 0, H.rows(), 1).sum() / n;
        double y = H.block(0, 1, H.rows(), 1).sum() / n;

        seeds.push_back(CDT3::Point(x, y));
    }

    Criteria criteria;

    if (maxlength > 0.0)
    {
        criteria = Criteria(0.0, maxlength);
    }
    else
    {
        criteria = Criteria();
    }

    CGAL::refine_Delaunay_mesh_2(triangulation, seeds.begin(), seeds.end(), criteria);

    if (is_optimized)
    {
        CGAL::lloyd_optimize_mesh_2(triangulation,
                                    CGAL::parameters::max_iteration_number = 100,
                                    CGAL::parameters::seeds_begin = seeds.begin(),
                                    CGAL::parameters::seeds_end = seeds.end());
    }

    // Count the number of faces belonging to the boundary domain

    int f = 0;
    for (CDT3::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++)
    {
        if (fit->is_in_domain())
        {
            f++;
        }
    }

    // Prepare result matrices

    compas::RowMatrixXd TV(triangulation.number_of_vertices(), 3);
    compas::RowMatrixXi TF(f, 3);

    // Make vertex index map

    std::unordered_map<CDT3::Vertex_handle, unsigned> vertex_index;

    // Load the vertices into the result

    int i = 0;
    for (CDT3::Vertex_handle vertex : triangulation.finite_vertex_handles())
    {
        CDT3::Point point = vertex->point();

        vertex_index.insert({vertex, i});

        TV(i, 0) = point.hx();
        TV(i, 1) = point.hy();
        TV(i, 2) = 0.0;

        i++;
    }

    // Load the faces into the result

    int j = 0;
    for (CDT3::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++)
    {
        CDT3::Face_handle face = fit;

        if (fit->is_in_domain())
        {
            CDT3::Vertex_handle a = face->vertex(0);
            CDT3::Vertex_handle b = face->vertex(1);
            CDT3::Vertex_handle c = face->vertex(2);

            TF(j, 0) = vertex_index[a];
            TF(j, 1) = vertex_index[b];
            TF(j, 2) = vertex_index[c];

            j++;
        }
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(TV, TF);
    return result;
}

void init_triangulation(nb::module_& m) {
    auto submodule = m.def_submodule("triangulation");

    submodule.def(
        "delaunay_triangulation",
        &pmp_delaunay_triangulation,
        """Delaunary triangulation of a given set of points."""
        "V"_a);

    submodule.def(
        "constrained_delaunay_triangulation",
        &pmp_constrained_delaunay_triangulation,
        """Constrained Delaunay triangulation of a given boundary with internal holes and constraint curves.""",
        "B"_a,
        "P"_a,
        "holes"_a,
        "curves"_a,
        "is_conforming"_a = false);

    submodule.def(
        "refined_delaunay_mesh",
        &pmp_refined_delaunay_mesh,
        """Refined Delaunay mesh of a given boundary with internal holes and constraint curves.""",
        "B"_a,
        "P"_a,
        "holes"_a,
        "curves"_a,
        "minangle"_a = 0.0,
        "maxlength"_a = 0.0,
        "is_optimized"_a = true);

}
