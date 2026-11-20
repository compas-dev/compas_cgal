#include "distance.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <exception>
#include <iterator>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

namespace {

using Point = compas::Kernel::Point_3;
using Vector = compas::Kernel::Vector_3;
using Side = CGAL::Side_of_triangle_mesh<compas::Mesh, compas::Kernel>;
using Tree = Side::AABB_tree;
using face_descriptor = boost::graph_traits<compas::Mesh>::face_descriptor;

// Angle a face subtends at a point lying in its interior, and at a point on one of its edges (degrees).
constexpr double FULL_ANGLE = 360.0;
constexpr double STRAIGHT_ANGLE = 180.0;

// Queries a thread takes at a time. Far queries cost several times what near ones do, so
// the threads draw small blocks from a shared counter instead of one fixed share each.
constexpr Eigen::Index QUERIES_PER_BLOCK = 1024;

compas::Mesh
build_mesh(
    Eigen::Ref<const compas::RowMatrixXd> vertices,
    Eigen::Ref<const compas::RowMatrixXi> faces)
{
    if (vertices.cols() != 3) {
        throw std::invalid_argument("vertices must be an Nx3 array");
    }
    if (faces.cols() != 3) {
        throw std::invalid_argument("faces must be an Mx3 array of vertex indices");
    }
    if (faces.rows() == 0) {
        throw std::invalid_argument("the mesh has no faces");
    }
    if (faces.minCoeff() < 0 || faces.maxCoeff() >= vertices.rows()) {
        throw std::invalid_argument("a face refers to a vertex that does not exist");
    }

    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(vertices, faces);

    // Face indices are reported to the caller, so every input face has to be in the mesh.
    if (mesh.number_of_faces() != static_cast<std::size_t>(faces.rows())) {
        throw std::invalid_argument("the faces do not form a manifold triangle mesh");
    }
    return mesh;
}

void
check_points(Eigen::Ref<const compas::RowMatrixXd> points)
{
    if (points.cols() != 3) {
        throw std::invalid_argument("points must be an Nx3 array");
    }
}

// Number of threads to run `count` queries on: `requested`, or every hardware thread when it is 0.
Eigen::Index
thread_count(int requested, Eigen::Index count)
{
    if (requested < 0) {
        throw std::invalid_argument("the number of threads must not be negative");
    }
    Eigen::Index threads = requested;
    if (threads == 0) {
        threads = std::max(1u, std::thread::hardware_concurrency());
    }
    const Eigen::Index blocks = (count + QUERIES_PER_BLOCK - 1) / QUERIES_PER_BLOCK;
    return std::max<Eigen::Index>(1, std::min(threads, blocks));
}

// Threads that are joined when the scope ends, also when starting one of them throws.
struct Workers {
    std::vector<std::thread> threads;

    ~Workers()
    {
        for (std::thread& thread : threads) {
            if (thread.joinable()) {
                thread.join();
            }
        }
    }
};

// Call `body(begin, end)` on blocks covering [0, count), from `threads` threads, without the GIL.
// Each query writes its own rows only, so the result does not depend on the number of threads.
// An error raised by `body` is rethrown here once the threads are joined and the GIL is held again.
template <typename Body>
void
for_each_block(Eigen::Index count, Eigen::Index threads, const Body& body)
{
    std::atomic<Eigen::Index> next{0};
    std::vector<std::exception_ptr> errors(threads);

    auto work = [&](Eigen::Index worker) {
        try {
            for (;;) {
                const Eigen::Index begin = next.fetch_add(QUERIES_PER_BLOCK);
                if (begin >= count) {
                    return;
                }
                body(begin, std::min(begin + QUERIES_PER_BLOCK, count));
            }
        } catch (...) {
            errors[worker] = std::current_exception();
        }
    };

    {
        // The workers read the query array and write C++ arrays; none touches a Python object.
        nb::gil_scoped_release release;
        Workers workers;
        workers.threads.reserve(threads - 1);
        for (Eigen::Index worker = 1; worker < threads; ++worker) {
            workers.threads.emplace_back(work, worker);
        }
        work(0);
    }

    for (const std::exception_ptr& error : errors) {
        if (error) {
            std::rethrow_exception(error);
        }
    }
}

} // namespace


// Closest point, face and signed distance queries on one triangle mesh.
// The AABB tree is built once, in the constructor, and shared by all queries. Queries only
// read it: CGAL guards what it builds lazily when CGAL_HAS_THREADS is defined, as it is
// for this module (CMakeLists.txt).
class MeshDistance {
public:
    MeshDistance(
        Eigen::Ref<const compas::RowMatrixXd> vertices,
        Eigen::Ref<const compas::RowMatrixXi> faces)
        : mesh_(build_mesh(vertices, faces)),
          tree_(mesh_.faces().begin(), mesh_.faces().end(), mesh_, get(CGAL::vertex_point, std::as_const(mesh_))),
          side_(tree_),
          closed_(CGAL::is_closed(mesh_))
    {
        tree_.build();
        tree_.accelerate_distance_queries();
    }

    // The tree and the side-of structure point into this object.
    MeshDistance(const MeshDistance&) = delete;
    MeshDistance& operator=(const MeshDistance&) = delete;

    std::tuple<compas::RowMatrixXd, Eigen::VectorXi>
    closest(Eigen::Ref<const compas::RowMatrixXd> points, int num_threads) const
    {
        check_points(points);
        const Eigen::Index n = points.rows();
        const Eigen::Index threads = thread_count(num_threads, n);
        compas::RowMatrixXd closest_points(n, 3);
        Eigen::VectorXi face_indices(n);

        for_each_block(n, threads, [&](Eigen::Index begin, Eigen::Index end) {
            for (Eigen::Index i = begin; i < end; ++i) {
                const Point query(points(i, 0), points(i, 1), points(i, 2));
                const auto [closest, face] = tree_.closest_point_and_primitive(query);
                closest_points.row(i) << closest.x(), closest.y(), closest.z();
                face_indices(i) = static_cast<int>(face.idx());
            }
        });
        return std::make_tuple(std::move(closest_points), std::move(face_indices));
    }

    std::tuple<Eigen::VectorXd, compas::RowMatrixXd, Eigen::VectorXi, compas::RowMatrixXd>
    signed_distance(Eigen::Ref<const compas::RowMatrixXd> points, int num_threads) const
    {
        check_points(points);
        if (!closed_) {
            throw std::invalid_argument("a signed distance needs a closed mesh");
        }
        const Eigen::Index n = points.rows();
        const Eigen::Index threads = thread_count(num_threads, n);
        Eigen::VectorXd distances(n);
        compas::RowMatrixXd closest_points(n, 3);
        Eigen::VectorXi face_indices(n);
        compas::RowMatrixXd gradients(n, 3);

        for_each_block(n, threads, [&](Eigen::Index begin, Eigen::Index end) {
            std::vector<face_descriptor> containing;
            for (Eigen::Index i = begin; i < end; ++i) {
                const Point query(points(i, 0), points(i, 1), points(i, 2));
                const CGAL::Bounded_side side = side_(query);
                auto [closest, face] = tree_.closest_point_and_primitive(query);

                double distance;
                Vector gradient;
                if (side == CGAL::ON_BOUNDARY) {
                    // Exact verdict: the query is on the mesh, on every face collected here.
                    containing.clear();
                    tree_.all_intersected_primitives(query, std::back_inserter(containing));
                    if (containing.empty()) {
                        throw std::runtime_error("a query on the boundary of the mesh lies on none of its faces");
                    }
                    face = *std::min_element(containing.begin(), containing.end());
                    closest = query;
                    distance = 0.0;
                    gradient = pseudonormal(query, containing);
                } else {
                    distance = std::sqrt(CGAL::squared_distance(query, closest));
                    if (distance == 0.0) {
                        // Off the mesh by less than the closest point resolves.
                        gradient = face_normal(face);
                    } else {
                        gradient = (query - closest) / distance;
                        if (side == CGAL::ON_BOUNDED_SIDE) {
                            gradient = -gradient;
                            distance = -distance;
                        }
                    }
                }

                distances(i) = distance;
                closest_points.row(i) << closest.x(), closest.y(), closest.z();
                face_indices(i) = static_cast<int>(face.idx());
                gradients.row(i) << gradient.x(), gradient.y(), gradient.z();
            }
        });
        return std::make_tuple(
            std::move(distances), std::move(closest_points), std::move(face_indices), std::move(gradients));
    }

    bool is_closed() const { return closed_; }

private:
    std::array<Point, 3>
    corners(face_descriptor face) const
    {
        const auto h = mesh_.halfedge(face);
        return {mesh_.point(mesh_.source(h)), mesh_.point(mesh_.target(h)), mesh_.point(mesh_.target(mesh_.next(h)))};
    }

    Vector
    face_normal(face_descriptor face) const
    {
        const auto [a, b, c] = corners(face);
        return CGAL::unit_normal(a, b, c);
    }

    // Angle-weighted pseudonormal at a point that lies on each of the given faces:
    // every face counts by the angle it subtends at the point.
    Vector
    pseudonormal(const Point& point, const std::vector<face_descriptor>& faces) const
    {
        Vector sum = CGAL::NULL_VECTOR;
        for (face_descriptor face : faces) {
            const auto [a, b, c] = corners(face);
            double angle = FULL_ANGLE;
            if (point == a) {
                angle = CGAL::approximate_angle(b, a, c);
            } else if (point == b) {
                angle = CGAL::approximate_angle(c, b, a);
            } else if (point == c) {
                angle = CGAL::approximate_angle(a, c, b);
            } else if (CGAL::collinear(a, b, point) || CGAL::collinear(b, c, point) || CGAL::collinear(c, a, point)) {
                angle = STRAIGHT_ANGLE;
            }
            sum = sum + angle * CGAL::unit_normal(a, b, c);
        }
        return sum / std::sqrt(sum.squared_length());
    }

    compas::Mesh mesh_;
    Tree tree_;
    Side side_;
    bool closed_;
};


NB_MODULE(_distance, m) {
    nanobind::class_<MeshDistance>(m, "MeshDistance",
        "Closest point and signed distance queries on a triangle mesh, with the search tree built once.")
        .def(nanobind::init<Eigen::Ref<const compas::RowMatrixXd>, Eigen::Ref<const compas::RowMatrixXi>>(),
             "vertices"_a, "faces"_a)
        .def("closest", &MeshDistance::closest, "points"_a, "num_threads"_a = 0)
        .def("signed_distance", &MeshDistance::signed_distance, "points"_a, "num_threads"_a = 0)
        .def_prop_ro("is_closed", &MeshDistance::is_closed);
}
