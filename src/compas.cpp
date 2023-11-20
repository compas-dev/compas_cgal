#include <compas.h>
#include <pybind11/pybind11.h>

template <class HDS>
class Build_polyhedron : public CGAL::Modifier_base<HDS>
{
private:
    const compas::RowMatrixXd &m_vertices;
    const compas::RowMatrixXi &m_faces;

public:
    Build_polyhedron(const compas::RowMatrixXd &V, const compas::RowMatrixXi &F) : m_vertices(V), m_faces(F)
    {
    }

    void operator()(HDS &hds)
    {
        typedef typename HDS::Vertex Vertex;
        typedef typename Vertex::Point Point;

        CGAL::Polyhedron_incremental_builder_3<HDS> Builder(hds, true);

        Builder.begin_surface(m_vertices.rows(), m_faces.rows());

        for (int i = 0; i < m_vertices.rows(); i++)
        {
            Builder.add_vertex(Point(m_vertices(i, 0), m_vertices(i, 1), m_vertices(i, 2)));
        }

        for (int i = 0; i < m_faces.rows(); i++)
        {
            Builder.begin_facet();
            for (int j = 0; j < m_faces.cols(); j++)
            {
                Builder.add_vertex_to_facet(m_faces(i, j));
            }
            Builder.end_facet();
        }

        Builder.end_surface();
    }
};

/**
 * @brief Construct a Polyhedron_3 from vertices and faces.
 *
 * @param V vx3 matrix of vertex coordinates.
 * @param F fx3 matrix of face vertex indices.
 * @return Polyhedron
 *
 * @todo: add support for Ngon faces.
 */
Polyhedron polyhedron_from_vertices_and_faces(
    const compas::RowMatrixXd &V,
    const compas::RowMatrixXi &F)
{
    Polyhedron polyhedron;
    Build_polyhedron<Polyhedron::HalfedgeDS> build(V, F);
    polyhedron.delegate(build);
    return polyhedron;
}

/**
 * @brief Construct a Surface_mesh from vertices and faces.
 *
 * @param V vx3 matrix of vertex coordinates.
 * @param F fx3 matrix of face vertex indices.
 * @return Mesh
 *
 * @todo: change name to trimesh_from_vertices_and_faces.
 * @todo: check that all faces are triangles.
 * @todo: add error message if not all faces are triangles.
 *
 */
Mesh compas::mesh_from_vertices_and_faces(
    const compas::RowMatrixXd &V,
    const compas::RowMatrixXi &F)
{
    int v = V.rows();
    int f = F.rows();

    Mesh mesh;
    std::vector<Mesh::Vertex_index> index_descriptor(v);

    for (int i = 0; i < v; i++)
    {
        index_descriptor[i] = mesh.add_vertex(Kernel::Point_3(V(i, 0), V(i, 1), V(i, 2)));
    }

    Mesh::Vertex_index a;
    Mesh::Vertex_index b;
    Mesh::Vertex_index c;

    for (int i = 0; i < f; i++)
    {
        a = index_descriptor[F(i, 0)];
        b = index_descriptor[F(i, 1)];
        c = index_descriptor[F(i, 2)];
        mesh.add_face(a, b, c);
    }

    return mesh;
}

/**
 * @brief Constrcut a Surface_mesh from vertices and faces.
 *
 * @param V nx3 matrix of vertex coordinates.
 * @param faces list of list of vertex indices.
 * @return Mesh
 *
 * @todo: rename to mesh_from_vertices_and_faces.
 */
Mesh compas::ngon_from_vertices_and_faces(
    const compas::RowMatrixXd &V,
    const std::vector<std::vector<int>> &faces)
{
    int v = V.rows();

    Mesh mesh;
    std::vector<Mesh::Vertex_index> index_descriptor(v);

    for (int i = 0; i < v; i++)
    {
        index_descriptor[i] = mesh.add_vertex(Kernel::Point_3(V(i, 0), V(i, 1), V(i, 2)));
    }

    for (std::size_t i = 0; i < faces.size(); i++)
    {
        std::vector<Mesh::Vertex_index> face;

        for (std::size_t j = 0; j < faces[i].size(); j++)
        {
            face.push_back(index_descriptor[faces[i][j]]);
        }

        mesh.add_face(face);
    }

    return mesh;
}

/**
 * @brief Convert a Surface_mesh to vertices and faces.
 *
 * @param mesh A Surface_mesh containing only triangles.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 *
 * @todo: rename to trimesh_to_vertices_and_faces.
 * @todo: check that all faces are triangles.
 * @todo: add error message if not all faces are triangles.
 *
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
compas::mesh_to_vertices_and_faces(
    const Mesh &mesh)
{
    std::size_t v = mesh.number_of_vertices();
    std::size_t f = mesh.number_of_faces();

    compas::RowMatrixXd V(v, 3);
    compas::RowMatrixXi F(f, 3);

    Mesh::Property_map<Mesh::Vertex_index, Kernel::Point_3> location = mesh.points();

    for (Mesh::Vertex_index vd : mesh.vertices())
    {
        V(vd, 0) = (double)location[vd][0];
        V(vd, 1) = (double)location[vd][1];
        V(vd, 2) = (double)location[vd][2];
    }

    for (Mesh::Face_index fd : mesh.faces())
    {
        int i = 0;
        for (Mesh::Vertex_index vd : vertices_around_face(mesh.halfedge(fd), mesh))
        {
            F(fd, i) = (int)vd;
            i++;
        }
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(V, F);
    return result;
}

/**
 * @brief Convert a Surface_mesh to vertices and faces.
 *
 * @param mesh A Surface_mesh containing only quads.
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 *
 * @todo: check that all faces are quads.
 * @todo: add error message if not all faces are quads.
 *
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
compas::quadmesh_to_vertices_and_faces(
    const Mesh &mesh)
{
    std::size_t v = mesh.number_of_vertices();
    std::size_t f = mesh.number_of_faces();

    compas::RowMatrixXd V(v, 3);
    compas::RowMatrixXi F(f, 4);

    Mesh::Property_map<Mesh::Vertex_index, Kernel::Point_3> vertex_location = mesh.points();

    for (Mesh::Vertex_index vd : mesh.vertices())
    {
        V(vd, 0) = (double)vertex_location[vd][0];
        V(vd, 1) = (double)vertex_location[vd][1];
        V(vd, 2) = (double)vertex_location[vd][2];
    }

    for (Mesh::Face_index fd : mesh.faces())
    {
        int i = 0;
        for (Mesh::Vertex_index vd : vertices_around_face(mesh.halfedge(fd), mesh))
        {
            F(fd, i) = (int)vd;
            i++;
        }
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(V, F);
    return result;
}

/**
 * @brief Convert a list of polylines to a list of list of point.
 *
 * @param polylines
 * @return std::vector<compas::RowMatrixXd>
 */
std::vector<compas::RowMatrixXd>
compas::polylines_to_lists_of_points(
    Polylines polylines)
{
    std::vector<compas::RowMatrixXd> pointsets;

    for (auto i = polylines.begin(); i != polylines.end(); i++)
    {
        const Polyline &poly = *i;
        std::size_t n = poly.size();
        compas::RowMatrixXd points(n, 3);

        for (int j = 0; j < n; j++)
        {
            points(j, 0) = (double)poly[j].x();
            points(j, 1) = (double)poly[j].y();
            points(j, 2) = (double)poly[j].z();
        }

        pointsets.push_back(points);
    }

    return pointsets;
}

/**
 * @brief Convert a Polyhedron_3 to vertices and faces.
 *
 * @param polyhedron
 * @return std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
 *
 * @todo: add support for Ngon faces.
 */
std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
compas::polyhedron_to_vertices_and_faces(
    Polyhedron polyhedron)
{
    std::size_t v = polyhedron.size_of_vertices();
    std::size_t f = polyhedron.size_of_facets();

    compas::RowMatrixXd V(v, 3);
    compas::RowMatrixXi F(f, 3);

    std::size_t i = 0;

    for (Polyhedron::Vertex_handle vh : polyhedron.vertex_handles())
    {
        V(i, 0) = (double)vh->point().x();
        V(i, 1) = (double)vh->point().y();
        V(i, 2) = (double)vh->point().z();

        vh->id() = i;

        i++;
    }

    i = 0;

    for (Polyhedron::Facet_handle fh : polyhedron.facet_handles())
    {
        std::size_t j = 0;

        Polyhedron::Halfedge_handle start = fh->halfedge(), h = start;
        do
        {
            F(i, j) = h->vertex()->id();
            h = h->next();
            j++;

        } while (h != start);

        i++;
    }

    std::tuple<compas::RowMatrixXd, compas::RowMatrixXi> result = std::make_tuple(V, F);
    return result;
}
