#include "geodesics_exact.h"

#include <CGAL/AABB_face_graph_triangle_primitive.h>
#include <CGAL/AABB_traits_3.h>
#include <CGAL/AABB_tree.h>
#include <CGAL/Surface_mesh_shortest_path.h>

#include <cmath>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace {

using Traits = CGAL::Surface_mesh_shortest_path_traits<compas::Kernel, compas::Mesh>;
using ShortestPath = CGAL::Surface_mesh_shortest_path<Traits>;
using AABBPrimitive = CGAL::AABB_face_graph_triangle_primitive<compas::Mesh>;
using AABBTraits = CGAL::AABB_traits_3<compas::Kernel, AABBPrimitive>;
using AABBTree = CGAL::AABB_tree<AABBTraits>;
using vertex_descriptor = boost::graph_traits<compas::Mesh>::vertex_descriptor;

// Barycentric coordinates are DIMENSIONLESS and bounded in [0, 1], so this threshold is
// scale free -- it is not a length tolerance and does not change meaning with model units.
//
// It repairs a real defect in the composition CGAL itself documents. `locate()` performs an
// inexact CONSTRUCTION under Epick, so for a point lying exactly on a mesh vertex it returns
// coordinates carrying round-off -- measured on a plain planar grid: (0, -6.5919e-17, 1) and
// (-1.1102e-16, 6.0986e-17, 1). `Classify_barycentric_coordinates` then tests EXACTLY, so a
// location that is geometrically ON a vertex is classified as face-interior, and
// `expand_root` roots the wavefront at the wrong place. The failure is silent: no exception,
// and the vertex's own distance comes back as one edge length instead of zero. It is
// intermittent across mesh sizes with identical topology, because it turns on the last bit.
//
// 8 ulps of 1.0 clears the measured round-off by ~16x. A source point genuinely that close to
// a vertex is displaced onto it by at most 8 * DBL_EPSILON of the containing face's extent,
// which is far below any geometric meaning; a source anywhere else is untouched.
constexpr double BARYCENTRIC_SNAP = 8.0 * std::numeric_limits<double>::epsilon();

/**
 * @brief Make a located face position classify as the simplex it geometrically lies on.
 *
 * Drives sub-ulp components (negative round-off included) to exactly zero and renormalizes,
 * so that a point on a vertex reads as BARYCENTRIC_COORDINATES_ON_VERTEX and a point on an
 * edge as ON_BOUNDARY. See BARYCENTRIC_SNAP for why this is not a tolerance on a length.
 */
void snap_to_simplex(ShortestPath::Face_location& location)
{
    auto& b = location.second;
    double total = 0.0;
    for (std::size_t i = 0; i < 3; ++i)
    {
        if (b[i] < BARYCENTRIC_SNAP)
        {
            b[i] = 0.0;
        }
        total += b[i];
    }
    if (!(total > 0.0))
    {
        throw std::runtime_error(
            "exact geodesics: a source point located to degenerate barycentric coordinates");
    }
    for (std::size_t i = 0; i < 3; ++i)
    {
        b[i] /= total;
    }
}

/**
 * @brief Exact-geodesic engine over one surface, reusable across source sets.
 *
 * Holds state on three different clocks. The mesh and its index property maps last as
 * long as the engine. The AABB tree is built on the first point-source query and never
 * again, so a vertex-source-only engine never pays for it. The sequence tree belongs to
 * one source set and is rebuilt by CGAL whenever the sources change -- that is the whole
 * cost of the algorithm and it is not reusable, unlike the heat method's factorization.
 */
class ExactContext
{
public:
    ExactContext(
        Eigen::Ref<compas::RowMatrixXd> vertices,
        Eigen::Ref<compas::RowMatrixXi> faces)
        : mesh_(compas::mesh_from_vertices_and_faces(vertices, faces)),
          n_(static_cast<int>(mesh_.number_of_vertices())),
          shortest_path_(mesh_)
    {
        if (n_ < 3)
        {
            throw std::invalid_argument(
                "exact geodesics: a surface needs at least 3 vertices");
        }
    }

    // Surface_mesh_shortest_path holds a reference to mesh_, so the engine must not move.
    ExactContext(const ExactContext&) = delete;
    ExactContext& operator=(const ExactContext&) = delete;

    int num_vertices() const { return n_; }

    /// All-vertex exact distances from a set of source VERTICES.
    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
    solve(const std::vector<int>& sources)
    {
        reset_sources();
        // Out-of-range indices are ignored and duplicates collapse, matching the heat
        // backend. The recorded ordinal indexes the sequence AS GIVEN, so that
        // `sources[ordinal]` recovers the vertex index.
        std::vector<char> seen(static_cast<std::size_t>(n_), 0);
        int accepted = 0;
        for (std::size_t k = 0; k < sources.size(); ++k)
        {
            const int s = sources[k];
            if (s < 0 || s >= n_ || seen[static_cast<std::size_t>(s)])
            {
                continue;
            }
            seen[static_cast<std::size_t>(s)] = 1;
            record(
                shortest_path_.add_source_point(
                    vertex_descriptor(static_cast<std::size_t>(s))),
                static_cast<int>(k));
            ++accepted;
        }
        if (accepted == 0)
        {
            throw std::invalid_argument(
                "exact geodesics: at least one valid source vertex index is required");
        }
        return harvest();
    }

    /// All-vertex exact distances from source POINTS, located on the surface.
    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
    solve_from_points(Eigen::Ref<compas::RowMatrixXd> points)
    {
        if (points.cols() != 3)
        {
            throw std::invalid_argument(
                "exact geodesics: source points require shape (S, 3)");
        }
        if (points.rows() == 0)
        {
            throw std::invalid_argument(
                "exact geodesics: at least one source point is required");
        }
        if (!points.allFinite())
        {
            throw std::invalid_argument(
                "exact geodesics: source points contain non-finite coordinates");
        }
        if (!aabb_)
        {
            aabb_.emplace();
            shortest_path_.build_aabb_tree(*aabb_);
        }
        reset_sources();
        for (Eigen::Index k = 0; k < points.rows(); ++k)
        {
            const compas::Kernel::Point_3 p(points(k, 0), points(k, 1), points(k, 2));
            // locate() projects to the closest point on the surface. Callers that must
            // bound that projection compose with compas_cgal.projection, which owns
            // point-to-mesh proximity; imposing a tolerance here would not be unit-free.
            ShortestPath::Face_location location = shortest_path_.locate(p, *aabb_);
            snap_to_simplex(location);
            record(shortest_path_.add_source_point(location), static_cast<int>(k));
        }
        return harvest();
    }

private:
    void reset_sources()
    {
        shortest_path_.remove_all_source_points();
        ordinal_.clear();
    }

    /**
     * @brief Remember which ordinal a source iterator stands for.
     *
     * The source points live in a std::list, so std::distance to recover an ordinal
     * would be O(sources) per vertex, O(vertices * sources) overall. List nodes are
     * address stable, so the element address keys an O(1) lookup instead.
     */
    void record(ShortestPath::Source_point_iterator it, int ordinal)
    {
        ordinal_.emplace(static_cast<const void*>(&(*it)), ordinal);
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> harvest()
    {
        compas::RowMatrixXd distances(n_, 1);
        compas::RowMatrixXi nearest(n_, 1);
        int unreachable = 0;

        for (vertex_descriptor vd : mesh_.vertices())
        {
            const Eigen::Index row = static_cast<Eigen::Index>(vd.idx());
            const auto result = shortest_path_.shortest_distance_to_source_points(vd);
            // An unreachable vertex yields (-1, source_points_end()), not infinity.
            if (result.second == shortest_path_.source_points_end())
            {
                ++unreachable;
                distances(row, 0) = -1.0;
                nearest(row, 0) = -1;
                continue;
            }
            const auto found = ordinal_.find(static_cast<const void*>(&(*result.second)));
            if (found == ordinal_.end())
            {
                throw std::runtime_error(
                    "exact geodesics: the nearest source could not be identified");
            }
            distances(row, 0) = CGAL::to_double(result.first);
            nearest(row, 0) = found->second;
        }

        if (unreachable > 0)
        {
            throw std::runtime_error(
                "exact geodesics: " + std::to_string(unreachable) +
                " vertices are unreachable from the source set (disconnected component)");
        }
        return {distances, nearest};
    }

    compas::Mesh mesh_;
    int n_;
    ShortestPath shortest_path_;
    std::optional<AABBTree> aabb_;
    std::unordered_map<const void*, int> ordinal_;
};

}  // namespace

/**
 * @brief Exact geodesic distances from source vertices, one shot.
 */
static std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_exact_geodesic_distances(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    const std::vector<int>& sources)
{
    ExactContext ctx(vertices, faces);
    return ctx.solve(sources);
}

/**
 * @brief Exact geodesic distances from source points located on the surface, one shot.
 */
static std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_exact_geodesic_distances_from_points(
    Eigen::Ref<compas::RowMatrixXd> vertices,
    Eigen::Ref<compas::RowMatrixXi> faces,
    Eigen::Ref<compas::RowMatrixXd> points)
{
    ExactContext ctx(vertices, faces);
    return ctx.solve_from_points(points);
}

/**
 * @brief Exact-geodesic solver retaining the mesh across source sets.
 */
class ExactGeodesicSolver
{
public:
    ExactGeodesicSolver(
        Eigen::Ref<compas::RowMatrixXd> vertices,
        Eigen::Ref<compas::RowMatrixXi> faces)
        : ctx_(vertices, faces)
    {
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
    solve(const std::vector<int>& sources) { return ctx_.solve(sources); }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
    solve_from_points(Eigen::Ref<compas::RowMatrixXd> points)
    {
        return ctx_.solve_from_points(points);
    }

    int num_vertices() const { return ctx_.num_vertices(); }

private:
    ExactContext ctx_;
};

void bind_exact_geodesics(nb::module_& m)
{
    m.def(
        "exact_geodesic_distances",
        &pmp_exact_geodesic_distances,
        "Exact polyhedral geodesic distances from a set of source vertices.",
        "vertices"_a, "faces"_a, "sources"_a);

    m.def(
        "exact_geodesic_distances_from_points",
        &pmp_exact_geodesic_distances_from_points,
        "Exact polyhedral geodesic distances from source points located on the surface.",
        "vertices"_a, "faces"_a, "points"_a);

    nb::class_<ExactGeodesicSolver>(m, "ExactGeodesicSolver",
        "Exact geodesic solver retaining the mesh and its index maps across source sets.")
        .def(nb::init<Eigen::Ref<compas::RowMatrixXd>, Eigen::Ref<compas::RowMatrixXi>>(),
             "vertices"_a, "faces"_a)
        .def("solve", &ExactGeodesicSolver::solve, "sources"_a)
        .def("solve_from_points", &ExactGeodesicSolver::solve_from_points, "points"_a)
        .def_prop_ro("num_vertices", &ExactGeodesicSolver::num_vertices);
}
