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
mesh_data_from_skeleton(std::shared_ptr<Ss>& skeleton)
{
    std::size_t num_vertices = skeleton->size_of_vertices();
    std::size_t num_edges = skeleton->size_of_halfedges() / 2; // halfedges are stored twice

    compas::RowMatrixXd vertex_matrix(num_vertices, 3);
    std::vector<int> vertex_indices; // to save the vertex ids
    compas::RowMatrixXi edge_matrix(num_edges, 2);
    std::vector<int> edge_types; // to save the edge type: 0: inner bisector, 1: bisector, 2: boundary

    std::size_t i = 0;
    for (auto vertex_iter = skeleton->vertices_begin(); vertex_iter != skeleton->vertices_end(); ++vertex_iter)
    {
        const Vertex_const_handle vertex = vertex_iter;
        vertex_matrix(i, 0) = (double)vertex->point().x();
        vertex_matrix(i, 1) = (double)vertex->point().y();
        vertex_matrix(i, 2) = 0;
        vertex_indices.push_back((int)vertex->id());
        i++;
    }
    i = 0;
    for (auto edge_iter = skeleton->halfedges_begin(); edge_iter != skeleton->halfedges_end(); ++edge_iter)
    {
        const Halfedge_const_handle halfedge = edge_iter;
        const Vertex_const_handle& vertex1 = halfedge->vertex();
        const Vertex_const_handle& vertex2 = halfedge->opposite()->vertex();

        if (&*vertex1 < &*vertex2)
        {
            edge_matrix(i, 0) = (int)vertex1->id();
            edge_matrix(i, 1) = (int)vertex2->id();

            if (halfedge->is_inner_bisector())
            {
                edge_types.push_back(0);
            }
            else if (halfedge->is_bisector())
            {
                edge_types.push_back(1);
            }
            else
            {
                edge_types.push_back(2);
            }
            i++;
        }
    }
    return std::make_tuple(vertex_matrix, vertex_indices, edge_matrix, edge_types);
}

compas::RowMatrixXd 
polygon_to_data(Polygon_2 const& polygon)
{
    std::size_t n = polygon.size();
    compas::RowMatrixXd points(n, 3);
    int i = 0;
    for(typename Polygon_2::Vertex_const_iterator vertex_iter = polygon.vertices_begin(); 
        vertex_iter != polygon.vertices_end(); ++vertex_iter)
    {
        points(i, 0) = (double)(*vertex_iter).x();
        points(i, 1) = (double)(*vertex_iter).y();
        points(i, 2) = 0;
        i++;
    }
    return points;
}

std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>
polygon_with_holes_to_data(Polygon_with_holes const& polygon_with_holes)
{
    std::vector<compas::RowMatrixXd> holes;
    compas::RowMatrixXd boundary_points = polygon_to_data(polygon_with_holes.outer_boundary());
    for(typename Polygon_with_holes::Hole_const_iterator hole_iter = polygon_with_holes.holes_begin(); 
        hole_iter != polygon_with_holes.holes_end(); ++hole_iter)
    {
        compas::RowMatrixXd hole_points = polygon_to_data(*hole_iter);
        holes.push_back(hole_points);
    }
    return std::make_tuple(boundary_points, holes);
}

Polygon_2
data_to_polygon(const compas::RowMatrixXd& vertices)
{
    Polygon_2 polygon;
    for (int i = 0; i < vertices.rows(); i++) {
        polygon.push_back(Point(vertices(i, 0), vertices(i, 1)));
    }
    return polygon;
}

Polygon_with_holes
data_to_polygon_with_holes(
    const compas::RowMatrixXd& boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices)
{
    Polygon_2 outer_polygon = data_to_polygon(boundary_vertices);
    Polygon_with_holes polygon_with_holes(outer_polygon);
    for (const auto& hole_points : hole_vertices) {
        Polygon_2 hole;
        for (int i = 0; i < hole_points.rows(); i++) {
            hole.push_back(Point(hole_points(i, 0), hole_points(i, 1)));
        }
        polygon_with_holes.add_hole(hole);
    }
    return polygon_with_holes;
}

std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>>
pmp_create_interior_straight_skeleton(
    const compas::RowMatrixXd& vertices)
{
    Polygon_2 polygon = data_to_polygon(vertices);
    SsPtr skeleton = CGAL::create_interior_straight_skeleton_2(polygon.vertices_begin(), polygon.vertices_end());
    return mesh_data_from_skeleton(skeleton);
}

std::tuple<compas::RowMatrixXd, std::vector<int>, compas::RowMatrixXi, std::vector<int>>
pmp_create_interior_straight_skeleton_with_holes(
    const compas::RowMatrixXd& boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices)
{
    Polygon_with_holes polygon = data_to_polygon_with_holes(boundary_vertices, hole_vertices);
    SsPtr skeleton = CGAL::create_interior_straight_skeleton_2(polygon);
    return mesh_data_from_skeleton(skeleton);
}

std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_inner(
    const compas::RowMatrixXd& vertices,
    double& offset_distance)
{
    Polygon_2 polygon = data_to_polygon(vertices);
    PolygonPtrVector offset_polygons = CGAL::create_interior_skeleton_and_offset_polygons_2(offset_distance, polygon);

    std::vector<compas::RowMatrixXd> result;
    for(const auto& offset_polygon : offset_polygons) {
        compas::RowMatrixXd points = polygon_to_data(*offset_polygon);
        result.push_back(points);
    }
    return result;
}

std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_inner_with_holes(
    const compas::RowMatrixXd& boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices,
    double& offset_distance)
{
    Polygon_with_holes polygon = data_to_polygon_with_holes(boundary_vertices, hole_vertices);
    PolygonWithHolesPtrVector offset_polygons = CGAL::create_interior_skeleton_and_offset_polygons_with_holes_2(
        offset_distance, polygon);

    std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> result;
    for(const auto& offset_polygon : offset_polygons) {
        result.push_back(polygon_with_holes_to_data(*offset_polygon));
    }
    return result;
}

std::vector<compas::RowMatrixXd>
pmp_create_offset_polygons_2_outer(
    const compas::RowMatrixXd& vertices,
    double& offset_distance)
{
    Polygon_2 polygon = data_to_polygon(vertices);
    PolygonPtrVector offset_polygons = CGAL::create_exterior_skeleton_and_offset_polygons_2(offset_distance, polygon);

    std::vector<compas::RowMatrixXd> result;
    for(const auto& offset_polygon : offset_polygons) {
        compas::RowMatrixXd points = polygon_to_data(*offset_polygon);
        result.push_back(points);
    }
    return result;
}

std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>>
pmp_create_offset_polygons_2_outer_with_holes(
    const compas::RowMatrixXd& boundary_vertices,
    const std::vector<compas::RowMatrixXd>& hole_vertices,
    double& offset_distance)
{
    Polygon_with_holes polygon = data_to_polygon_with_holes(boundary_vertices, hole_vertices);
    PolygonWithHolesPtrVector offset_polygons = CGAL::create_exterior_skeleton_and_offset_polygons_with_holes_2(
        offset_distance, polygon);

    std::vector<std::tuple<compas::RowMatrixXd, std::vector<compas::RowMatrixXd>>> result;
    for(const auto& offset_polygon : offset_polygons) {
        result.push_back(polygon_with_holes_to_data(*offset_polygon));
    }
    return result;
}

std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_inner(
    const compas::RowMatrixXd& vertices,
    double offset_distance,
    const compas::RowMatrixXd& edge_weights)
{
    if (edge_weights.rows() != vertices.rows()) {
        throw std::invalid_argument("Number of weights must match number of polygon vertices");
    }

    Polygon_2 polygon = data_to_polygon(vertices);
    std::vector<double> weight_values;
    weight_values.reserve(edge_weights.rows());
    for (int i = 0; i < edge_weights.rows(); i++) {
        if (edge_weights(i, 0) <= 0) {
            throw std::invalid_argument("Weights must be positive");
        }
        weight_values.push_back(edge_weights(i, 0));
    }

    try {
        SsPtr skeleton = CGAL::create_interior_weighted_straight_skeleton_2(polygon, weight_values);
        if (!skeleton) {
            throw std::runtime_error("Failed to create weighted straight skeleton");
        }

        PolygonPtrVector offset_polygons = CGAL::create_offset_polygons_2<Polygon_2>(offset_distance, *skeleton);
        std::vector<compas::RowMatrixXd> result;
        result.reserve(offset_polygons.size());
        for(const auto& offset_polygon : offset_polygons) {
            result.push_back(polygon_to_data(*offset_polygon));
        }
        return result;
    } catch (const CGAL::Precondition_exception& e) {
        throw std::runtime_error("CGAL precondition failed: Invalid input for weighted offset");
    }
}

std::vector<compas::RowMatrixXd>
pmp_create_weighted_offset_polygons_2_outer(
    const compas::RowMatrixXd& vertices,
    double offset_distance,
    const compas::RowMatrixXd& edge_weights)
{
    if (edge_weights.rows() != vertices.rows()) {
        throw std::invalid_argument("Number of weights must match number of polygon vertices");
    }

    Polygon_2 polygon = data_to_polygon(vertices);
    std::vector<double> weight_values;
    weight_values.reserve(edge_weights.rows());
    for (int i = 0; i < edge_weights.rows(); i++) {
        if (edge_weights(i, 0) <= 0) {
            throw std::invalid_argument("Weights must be positive");
        }
        weight_values.push_back(edge_weights(i, 0));
    }

    try {
        SsPtr skeleton = CGAL::create_exterior_weighted_straight_skeleton_2(offset_distance, weight_values, polygon);
        if (!skeleton) {
            throw std::runtime_error("Failed to create weighted straight skeleton");
        }

        PolygonPtrVector offset_polygons = CGAL::create_offset_polygons_2<Polygon_2>(offset_distance, *skeleton);
        std::vector<compas::RowMatrixXd> result;
        result.reserve(offset_polygons.size());
        for(const auto& offset_polygon : offset_polygons) {
            result.push_back(polygon_to_data(*offset_polygon));
        }
        return result;
    } catch (const CGAL::Precondition_exception& e) {
        throw std::runtime_error("CGAL precondition failed: Invalid input for weighted offset");
    }
}

void init_straight_skeleton_2(nb::module_& m) {
    auto submodule = m.def_submodule("straight_skeleton_2");

    submodule.def(
        "create_interior_straight_skeleton",
        &pmp_create_interior_straight_skeleton,
        "Create an interior straight skeleton from a polygon.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx2, float64)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "tuple\n"
        "    - Matrix of skeleton vertices (Mx2, float64)\n"
        "    - Vector of source vertex indices\n"
        "    - Matrix of skeleton edges (Kx2, int32)\n"
        "    - Vector of source edge indices",
        "vertices"_a);

    submodule.def(
        "create_interior_straight_skeleton_with_holes",
        &pmp_create_interior_straight_skeleton_with_holes,
        "Create an interior straight skeleton from a polygon with holes.\n\n"
        "Parameters\n"
        "----------\n"
        "boundary_vertices : array-like\n"
        "    Matrix of boundary vertex positions (Nx2, float64)\n"
        "hole_vertices : list\n"
        "    List of hole vertex matrices (each Mx2, float64)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "tuple\n"
        "    - Matrix of skeleton vertices (Px2, float64)\n"
        "    - Vector of source vertex indices\n"
        "    - Matrix of skeleton edges (Qx2, int32)\n"
        "    - Vector of source edge indices",
        "boundary_vertices"_a,
        "hole_vertices"_a);

    submodule.def(
        "create_offset_polygons_2_inner",
        &pmp_create_offset_polygons_2_inner,
        "Create inward offset polygons from a simple polygon.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx2, float64)\n"
        "offset_distance : float\n"
        "    Offset distance (positive for inward)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of offset polygon matrices (each Mx2, float64)",
        "vertices"_a,
        "offset_distance"_a);

    submodule.def(
        "create_offset_polygons_2_inner_with_holes",
        &pmp_create_offset_polygons_2_inner_with_holes,
        "Create inward offset polygons from a polygon with holes.\n\n"
        "Parameters\n"
        "----------\n"
        "boundary_vertices : array-like\n"
        "    Matrix of boundary vertex positions (Nx2, float64)\n"
        "hole_vertices : list\n"
        "    List of hole vertex matrices (each Mx2, float64)\n"
        "offset_distance : float\n"
        "    Offset distance (positive for inward)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of tuples (outer polygon, list of hole polygons)",
        "boundary_vertices"_a,
        "hole_vertices"_a,
        "offset_distance"_a);

    submodule.def(
        "create_offset_polygons_2_outer",
        &pmp_create_offset_polygons_2_outer,
        "Create outward offset polygons from a simple polygon.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx2, float64)\n"
        "offset_distance : float\n"
        "    Offset distance (positive for outward)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of offset polygon matrices (each Mx2, float64)",
        "vertices"_a,
        "offset_distance"_a);

    submodule.def(
        "create_offset_polygons_2_outer_with_holes",
        &pmp_create_offset_polygons_2_outer_with_holes,
        "Create outward offset polygons from a polygon with holes.\n\n"
        "Parameters\n"
        "----------\n"
        "boundary_vertices : array-like\n"
        "    Matrix of boundary vertex positions (Nx2, float64)\n"
        "hole_vertices : list\n"
        "    List of hole vertex matrices (each Mx2, float64)\n"
        "offset_distance : float\n"
        "    Offset distance (positive for outward)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of tuples (outer polygon, list of hole polygons)",
        "boundary_vertices"_a,
        "hole_vertices"_a,
        "offset_distance"_a);

    submodule.def(
        "create_weighted_offset_polygons_2_inner",
        &pmp_create_weighted_offset_polygons_2_inner,
        "Create inward weighted offset polygons from a simple polygon.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx2, float64)\n"
        "offset_distance : float\n"
        "    Offset distance (must be positive)\n"
        "edge_weights : array-like\n"
        "    Matrix of edge weights (Nx1, float64, must be positive)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of offset polygon matrices (each Mx2, float64)",
        "vertices"_a,
        "offset_distance"_a,
        "edge_weights"_a);

    submodule.def(
        "create_weighted_offset_polygons_2_outer",
        &pmp_create_weighted_offset_polygons_2_outer,
        "Create outward weighted offset polygons from a simple polygon.\n\n"
        "Parameters\n"
        "----------\n"
        "vertices : array-like\n"
        "    Matrix of vertex positions (Nx2, float64)\n"
        "offset_distance : float\n"
        "    Offset distance (must be positive)\n"
        "edge_weights : array-like\n"
        "    Matrix of edge weights (Nx1, float64, must be positive)\n"
        "\n"
        "Returns\n"
        "-------\n"
        "list\n"
        "    List of offset polygon matrices (each Mx2, float64)",
        "vertices"_a,
        "offset_distance"_a,
        "edge_weights"_a);
}