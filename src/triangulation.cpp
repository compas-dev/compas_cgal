#include "triangulation.h"

struct face_info
{
    face_info(){};
    int nesting_level;
    bool in_domain()
    {
        return nesting_level % 2 == 1;
    }
};

using delaunay_polygon = CGAL::Polygon_2<compas::Kernel>;

using vertex_base1 = CGAL::Triangulation_vertex_base_with_info_2<unsigned, compas::Kernel>;
using tds1 = CGAL::Triangulation_data_structure_2<vertex_base1>;
using dt = CGAL::Delaunay_triangulation_2<compas::Kernel, tds1>;

using vertex_base2 = CGAL::Triangulation_vertex_base_2<compas::Kernel>;
using _face_base2 = CGAL::Triangulation_face_base_with_info_2<face_info, compas::Kernel>;
using face_base2 = CGAL::Constrained_triangulation_face_base_2<compas::Kernel, _face_base2>;
using tds2 = CGAL::Triangulation_data_structure_2<vertex_base2, face_base2>;
using cdt2 = CGAL::Constrained_Delaunay_triangulation_2<compas::Kernel, tds2>;

using vertex_base3 = CGAL::Delaunay_mesh_vertex_base_2<compas::Kernel>;
using face_base3 = CGAL::Delaunay_mesh_face_base_2<compas::Kernel>;
using tds3 = CGAL::Triangulation_data_structure_2<vertex_base3, face_base3>;
using itag = CGAL::Exact_predicates_tag;
using cdt3 = CGAL::Constrained_Delaunay_triangulation_2<compas::Kernel, tds3, itag>;
using criteria = CGAL::Delaunay_mesh_size_criteria_2<cdt3>;

compas::RowMatrixXi
pmp_delaunay_triangulation(Eigen::Ref<compas::RowMatrixXd> vertices)
{
    dt triangulation;
    std::vector<std::pair<dt::Point, unsigned>> points(vertices.rows());

    for (int i = 0; i < vertices.rows(); i++)
    {
        dt::Point point = dt::Point(vertices(i, 0), vertices(i, 1));
        points[i] = std::make_pair(point, i);
    }

    triangulation.insert(points.begin(), points.end());

    compas::RowMatrixXi faces(triangulation.number_of_faces(), 3);

    int j = 0;
    for (dt::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++)
    {
        dt::Face_handle face = fit;

        faces(j, 0) = face->vertex(0)->info();
        faces(j, 1) = face->vertex(1)->info();
        faces(j, 2) = face->vertex(2)->info();

        j++;
    }

    return faces;
}

void mark_domains(cdt2 &triangulation,
                  cdt2::Face_handle start,
                  int index,
                  std::list<cdt2::Edge> &border)
{
    if (start->info().nesting_level != -1)
    {
        return;
    }

    std::list<cdt2::Face_handle> queue;
    queue.push_back(start);

    while (!queue.empty())
    {
        cdt2::Face_handle face = queue.front();
        queue.pop_front();

        if (face->info().nesting_level == -1)
        {
            face->info().nesting_level = index;

            for (int i = 0; i < 3; i++)
            {
                cdt2::Edge edge(face, i);
                cdt2::Face_handle nbr = face->neighbor(i);

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

void mark_domains(cdt2 &triangulation)
{
    for (cdt2::Face_handle face : triangulation.all_face_handles())
    {
        face->info().nesting_level = -1;
    }

    std::list<cdt2::Edge> border;

    mark_domains(triangulation, triangulation.infinite_face(), 0, border);

    while (!border.empty())
    {
        cdt2::Edge edge = border.front();
        border.pop_front();

        cdt2::Face_handle nbr = edge.first->neighbor(edge.second);

        if (nbr->info().nesting_level == -1)
        {
            mark_domains(triangulation, nbr, edge.first->info().nesting_level + 1, border);
        }
    }
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_constrained_delaunay_triangulation(
    Eigen::Ref<compas::RowMatrixXd> boundary_vertices,
    Eigen::Ref<compas::RowMatrixXd> internal_vertices,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    bool is_conforming
    )
{
    cdt2 triangulation;

    // Add specific (isolated) points
    std::vector<cdt2::Point> points(internal_vertices.rows());

    for (int i = 0; i < internal_vertices.rows(); i++)
    {
        points[i] = cdt2::Point(internal_vertices(i, 0), internal_vertices(i, 1));
    }

    triangulation.insert(points.begin(), points.end());

    // Add the boundary as polygon constraint.
    delaunay_polygon boundary;

    for (int i = 0; i < boundary_vertices.rows(); i++)
    {
        boundary.push_back(cdt2::Point(boundary_vertices(i, 0), boundary_vertices(i, 1)));
    }

    triangulation.insert_constraint(boundary.vertices_begin(), boundary.vertices_end(), true);

    // Add the holes as polygon constraints.
    for (auto hit : holes)
    {
        compas::RowMatrixXd hole_vertices = hit;
        delaunay_polygon hole;

        for (int i = 0; i < hole_vertices.rows(); i++)
        {
            hole.push_back(cdt2::Point(hole_vertices(i, 0), hole_vertices(i, 1)));
        }

        triangulation.insert_constraint(hole.vertices_begin(), hole.vertices_end(), true);
    }

    // Add the curves as polyline constraints.
    for (auto cit : curves)
    {
        compas::RowMatrixXd curve_vertices = cit;
        std::vector<cdt2::Point> curve(curve_vertices.rows());

        for (int i = 0; i < curve_vertices.rows(); i++)
        {
            curve[i] = cdt2::Point(curve_vertices(i, 0), curve_vertices(i, 1));
        }

        triangulation.insert_constraint(curve.begin(), curve.end());
    }

    if (is_conforming)
    {
        CGAL::make_conforming_Delaunay_2(triangulation);
    }

    // Mark the faces belonging to the boundary constraint
    mark_domains(triangulation);

    // Count the number of faces belonging to the boundary domain
    int face_count = 0;
    for (cdt2::Face_handle face : triangulation.finite_face_handles())
    {
        if (face->info().in_domain())
        {
            face_count++;
        }
    }

    // Prepare result matrices
    compas::RowMatrixXd vertices_out(triangulation.number_of_vertices(), 3);
    compas::RowMatrixXi faces_out(face_count, 3);

    // Make vertex index map
    std::unordered_map<cdt2::Vertex_handle, unsigned> vertex_indices;

    // Load the vertices into the result
    int i = 0;
    for (cdt2::Vertex_handle vertex : triangulation.finite_vertex_handles())
    {
        cdt2::Point point = vertex->point();
        vertex_indices.insert({vertex, i});

        vertices_out(i, 0) = point.hx();
        vertices_out(i, 1) = point.hy();
        vertices_out(i, 2) = 0.0;

        i++;
    }

    // Load the faces into the result
    int j = 0;
    for (cdt2::Face_handle face : triangulation.finite_face_handles())
    {
        if (face->info().in_domain())
        {
            cdt2::Vertex_handle v0 = face->vertex(0);
            cdt2::Vertex_handle v1 = face->vertex(1);
            cdt2::Vertex_handle v2 = face->vertex(2);

            faces_out(j, 0) = vertex_indices[v0];
            faces_out(j, 1) = vertex_indices[v1];
            faces_out(j, 2) = vertex_indices[v2];

            j++;
        }
    }

    return std::make_tuple(vertices_out, faces_out);
}

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_refined_delaunay_mesh(
    Eigen::Ref<compas::RowMatrixXd> boundary_vertices,
    Eigen::Ref<compas::RowMatrixXd> internal_vertices,
    const std::vector<compas::RowMatrixXd> & holes,
    const std::vector<compas::RowMatrixXd> & curves,
    double min_angle,
    double max_length,
    bool is_optimized)
{
    cdt3 triangulation;

    // Add specific (isolated) points
    std::vector<cdt3::Point> points(internal_vertices.rows());

    for (int i = 0; i < internal_vertices.rows(); i++)
    {
        points[i] = cdt3::Point(internal_vertices(i, 0), internal_vertices(i, 1));
    }

    triangulation.insert(points.begin(), points.end());

    // Add the boundary as polygon constraint.
    delaunay_polygon boundary;

    for (int i = 0; i < boundary_vertices.rows(); i++)
    {
        boundary.push_back(cdt3::Point(boundary_vertices(i, 0), boundary_vertices(i, 1)));
    }

    triangulation.insert_constraint(boundary.vertices_begin(), boundary.vertices_end(), true);

    // Add the holes as polygon constraints.
    for (auto hit : holes)
    {
        compas::RowMatrixXd hole_vertices = hit;
        delaunay_polygon hole;

        for (int i = 0; i < hole_vertices.rows(); i++)
        {
            hole.push_back(cdt3::Point(hole_vertices(i, 0), hole_vertices(i, 1)));
        }

        triangulation.insert_constraint(hole.vertices_begin(), hole.vertices_end(), true);
    }

    // Add the curves as polyline constraints.
    for (auto cit : curves)
    {
        compas::RowMatrixXd curve_vertices = cit;
        std::vector<cdt3::Point> curve(curve_vertices.rows());

        for (int i = 0; i < curve_vertices.rows(); i++)
        {
            curve[i] = cdt3::Point(curve_vertices(i, 0), curve_vertices(i, 1));
        }

        triangulation.insert_constraint(curve.begin(), curve.end());
    }

    // Calculate hole centers for seeding
    std::list<cdt3::Point> seeds;
    for (auto hit : holes)
    {
        compas::RowMatrixXd hole_vertices = hit;
        double n = (double)hole_vertices.rows();

        double x = hole_vertices.block(0, 0, hole_vertices.rows(), 1).sum() / n;
        double y = hole_vertices.block(0, 1, hole_vertices.rows(), 1).sum() / n;

        seeds.push_back(cdt3::Point(x, y));
    }

    // Apply mesh refinement criteria
    criteria mesh_criteria;
    if (max_length > 0.0)
    {
        mesh_criteria = criteria(0.0, max_length);
    }
    else
    {
        mesh_criteria = criteria();
    }

    CGAL::refine_Delaunay_mesh_2(triangulation, seeds.begin(), seeds.end(), mesh_criteria);

    if (is_optimized)
    {
        CGAL::lloyd_optimize_mesh_2(triangulation,
                                    CGAL::parameters::max_iteration_number = 100,
                                    CGAL::parameters::seeds_begin = seeds.begin(),
                                    CGAL::parameters::seeds_end = seeds.end());
    }

    // Count faces in domain
    int face_count = 0;
    for (cdt3::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++)
    {
        if (fit->is_in_domain())
        {
            face_count++;
        }
    }

    // Prepare result matrices
    compas::RowMatrixXd vertices_out(triangulation.number_of_vertices(), 3);
    compas::RowMatrixXi faces_out(face_count, 3);

    // Make vertex index map
    std::unordered_map<cdt3::Vertex_handle, unsigned> vertex_indices;

    // Load vertices
    int i = 0;
    for (cdt3::Vertex_handle vertex : triangulation.finite_vertex_handles())
    {
        cdt3::Point point = vertex->point();
        vertex_indices.insert({vertex, i});

        vertices_out(i, 0) = point.hx();
        vertices_out(i, 1) = point.hy();
        vertices_out(i, 2) = 0.0;

        i++;
    }

    // Load faces
    int j = 0;
    for (cdt3::Finite_faces_iterator fit = triangulation.finite_faces_begin(); fit != triangulation.finite_faces_end(); fit++)
    {
        if (fit->is_in_domain())
        {
            cdt3::Face_handle face = fit;
            cdt3::Vertex_handle v0 = face->vertex(0);
            cdt3::Vertex_handle v1 = face->vertex(1);
            cdt3::Vertex_handle v2 = face->vertex(2);

            faces_out(j, 0) = vertex_indices[v0];
            faces_out(j, 1) = vertex_indices[v1];
            faces_out(j, 2) = vertex_indices[v2];

            j++;
        }
    }

    return std::make_tuple(vertices_out, faces_out);
}

void init_triangulation(nb::module_& m) {
    nb::module_ submodule = m.def_submodule("triangulation");

    submodule.def(
        "delaunay_triangulation",
        &pmp_delaunay_triangulation,
        "Create a Delaunay triangulation from a set of points.",
        "vertices"_a);

    submodule.def(
        "constrained_delaunay_triangulation",
        &pmp_constrained_delaunay_triangulation,
        "Create a constrained Delaunay triangulation with boundary, holes, and constraints.",
        "boundary_vertices"_a,
        "internal_vertices"_a,
        "holes"_a,
        "curves"_a,
        "is_conforming"_a = false);

    submodule.def(
        "refined_delaunay_mesh",
        &pmp_refined_delaunay_mesh,
        "Create a refined Delaunay mesh with quality constraints.",
        "boundary_vertices"_a,
        "internal_vertices"_a,
        "holes"_a,
        "curves"_a,
        "min_angle"_a = 0.0,
        "max_length"_a = 0.0,
        "is_optimized"_a = true);
}