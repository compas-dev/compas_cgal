#include "meshing.h"

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/boost/graph/Dual.h>
#include <CGAL/boost/graph/helpers.h>
#include <CGAL/Polygon_mesh_processing/compute_normal.h>
 
#include <iostream>
#include <fstream>
 
#include <boost/graph/filtered_graph.hpp>
#include <boost/graph/connected_components.hpp>

typedef CGAL::Dual<compas::Mesh> Dual;
typedef boost::graph_traits<Dual>::edge_descriptor edge_descriptor;



template <typename G>
struct noborder {
  noborder() : g(nullptr) {} // default-constructor required by filtered_graph
  noborder(G& g) : g(&g) {}
 
  bool operator()(const edge_descriptor& e) const
  { return !is_border(e,*g); }
 
  G* g;
};
 
// A dual border edge has a null_face as the source or target "vertex"
// BGL algorithms won't like that, so we remove border edges through a
// boost::filtered_graph.
typedef boost::filtered_graph<Dual, noborder<compas::Mesh> >   FiniteDual;
typedef boost::graph_traits<Dual>::vertex_descriptor   vertex_descriptor;
typedef boost::graph_traits<Dual>::face_descriptor     face_descriptor;
typedef boost::graph_traits<Dual>::edge_descriptor     edge_descriptor;


std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
pmp_trimesh_remesh(
    Eigen::Ref<compas::RowMatrixXd> vertices_a,
    Eigen::Ref<compas::RowMatrixXi> faces_a,
    double target_edge_length,
    unsigned int number_of_iterations,
    bool do_project)
{
    // Convert input matrices to CGAL mesh and keep a copy for projection
    compas::Mesh original_mesh = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);

    // Perform isotropic remeshing
    CGAL::Polygon_mesh_processing::isotropic_remeshing(
        faces(mesh_a),
        target_edge_length,
        mesh_a,
        CGAL::Polygon_mesh_processing::parameters::number_of_iterations(number_of_iterations)
                       .do_project(do_project));

                       
    // Clean up the mesh
    mesh_a.collect_garbage();

    // Convert back to matrices - compiler will use RVO automatically
    return compas::mesh_to_vertices_and_faces(mesh_a);
}



// Calculate face normals for a mesh using CGAL's Polygon Mesh Processing
std::vector<CGAL::Vector_3<compas::Kernel>> get_face_normals(const compas::Mesh& mesh, bool normalize = false)
{
    std::vector<CGAL::Vector_3<compas::Kernel>> normals(mesh.number_of_faces());
    
    
    for (std::size_t i = 0; i < mesh.number_of_faces(); ++i) {
        auto face = compas::Mesh::Face_index(i);
        
        // Use PMP to compute face normal
        CGAL::Vector_3<compas::Kernel> normal = CGAL::Polygon_mesh_processing::compute_face_normal(face, mesh);
        
        // Normalize if requested
        if (normalize && normal != CGAL::NULL_VECTOR) {
            normal = normal / std::sqrt(normal.squared_length());
        }
        
        normals[i] = normal;
    }
    
    return normals;
}

std::vector<double> get_face_areas_doubled(const std::vector<CGAL::Vector_3<compas::Kernel>>& faceNormals)
{
    std::vector<double> areas;
    areas.reserve(faceNormals.size());
    
    // Calculate area by getting the length of each face normal vector
    for (const auto& normal : faceNormals) {
        // The length of the normal is twice the area of the face
        areas.emplace_back(std::sqrt(normal.squared_length()));
    }
    
    return areas;
}

std::vector<double> get_vertex_areas(compas::Mesh mesh, std::vector<double> faceAreas)
{
    // Create a vector to store areas for each vertex
    std::vector<double> vertexAreas(mesh.number_of_vertices(), 0.0);
    
    // Process each vertex
    
    for (std::size_t i = 0; i < mesh.number_of_vertices(); ++i) {
        auto vertex = compas::Mesh::Vertex_index(i);
        double area_sum = 0.0;
        
        // Iterate through all faces connected to this vertex
        for (auto face : faces_around_target(mesh.halfedge(vertex), mesh)) {
            // Access face index and add its area to the sum
            std::size_t face_idx = face.idx();
            if (face_idx < faceAreas.size()) {
                area_sum += faceAreas[face_idx];
            }
        }
        
        // Store the result
            vertexAreas[i] = area_sum;
    }
    
    return vertexAreas;
}

std::tuple<
compas::RowMatrixXd, 
compas::RowMatrixXi,
compas::RowMatrixXd, 
std::vector<std::vector<int>>>
pmp_trimesh_remesh_dual(
    Eigen::Ref<compas::RowMatrixXd> vertices_a,
    Eigen::Ref<compas::RowMatrixXi> faces_a,
    const std::vector<int>& fixed_vertices,
    double length_factor,
    unsigned int number_of_iterations,
    double angle_radians,
    double scale_factor
)
{

    // Convert input matrices to CGAL mesh and keep a copy for projection
    compas::Mesh original_mesh = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);
    
    // Calculate average edge length
    double average_length = 0.0;
    double total_length = 0.0;
    int edge_count = 0;
    
    for (auto edge : edges(mesh_a)) {
        total_length += CGAL::Polygon_mesh_processing::edge_length(edge, mesh_a);
        edge_count++;
    }
    
    double target_edge_length = length_factor * total_length / edge_count;

    if (target_edge_length <= 0.0) {
        target_edge_length = 1.0;
    }


    // Define a property map for constrained vertices using CGAL's dynamic property map
    auto constrained = get(CGAL::dynamic_vertex_property_t<bool>(), mesh_a);


    // Before remeshing, store coordinates of fixed vertices 
    std::vector<compas::Kernel::Point_3> fixed_points;
    fixed_points.reserve(fixed_vertices.size()); // Pre-allocate for performance
    
    for (const auto& idx : fixed_vertices) {
        if (idx >= 0 && idx < vertices_a.rows()) {
            // Get directly from the input Eigen matrix
            fixed_points.emplace_back(
                vertices_a(idx, 0), 
                vertices_a(idx, 1), 
                vertices_a(idx, 2)
            );
        }
    }

    // Mark specified vertices as constrained
    if (!fixed_vertices.empty()) {
        // Use vertices from the fixed_vertices list
        for (const auto& vertex_idx : fixed_vertices) {
            if (vertex_idx >= 0 && vertex_idx < static_cast<int>(num_vertices(mesh_a))) {
                auto v = *(vertices(mesh_a).first + vertex_idx);
                put(constrained, v, true);
            }
        }
    }
    
    // Perform isotropic remeshing with constrained vertices
    CGAL::Polygon_mesh_processing::isotropic_remeshing(
        faces(mesh_a),
        target_edge_length,
        mesh_a,
        CGAL::Polygon_mesh_processing::parameters::number_of_iterations(number_of_iterations)
                        .vertex_is_constrained_map(constrained)
                        .do_project(true));

                        
    // Clean up the mesh
    mesh_a.collect_garbage();

    /////////////////////////////////////////////////////////////////////////////////
    // Scaled inner vertices
    /////////////////////////////////////////////////////////////////////////////////

    if (scale_factor != 1.0 && scale_factor > 0.0){
        // Make a copy of the original mesh before scaling
        compas::Mesh original_mesh = mesh_a;

        // Calculate mesh centroid first
        CGAL::Point_3<compas::Kernel> centroid(0, 0, 0);
        int vertex_count = 0;
        for(auto v : vertices(mesh_a)) {
            centroid = centroid + (mesh_a.point(v) - CGAL::ORIGIN);
            vertex_count++;
        }
        centroid = CGAL::ORIGIN + (centroid - CGAL::ORIGIN) / vertex_count;

        // Scale inner vertices relative to centroid
        for(auto v : vertices(mesh_a)) {
            // Check if the vertex is on the boundary
            bool is_boundary = false;
            for(auto h : CGAL::halfedges_around_target(v, mesh_a)) {
                if(is_border(h, mesh_a)) {
                    is_boundary = true;
                    break;
                }
            }
            
            // Only scale inner vertices
            if(!is_boundary) {
                auto p = mesh_a.point(v);
                // Calculate vector from centroid to point, scale it, then set the new position
                CGAL::Vector_3<compas::Kernel> vec(centroid, p);
                vec = vec * scale_factor;
                mesh_a.point(v) = centroid + vec;
            }
        }

    }
    
    


    /////////////////////////////////////////////////////////////////////////////////
    // Dual Graph Creation
    /////////////////////////////////////////////////////////////////////////////////
    // Create the dual graph structure and a filtered version that excludes border
    // elements. This filtered graph will be used to generate the interior portion
    // of the dual mesh.
    
    
    
    typedef CGAL::Dual<compas::Mesh> DualMesh;
    DualMesh dual(mesh_a);
    
    typedef boost::filtered_graph<DualMesh, noborder<compas::Mesh>> FiniteDual;
    FiniteDual finite_dual(dual, noborder<compas::Mesh>(mesh_a));
    
    compas::Mesh dual_mesh; // Create a new mesh for the dual
    
    std::map<typename boost::graph_traits<compas::Mesh>::face_descriptor, 
              typename boost::graph_traits<compas::Mesh>::vertex_descriptor> face_to_vertex; // Map to track face-to-vertex conversion
    
    /////////////////////////////////////////////////////////////////////////////////
    // Dual Mesh Vertex Creation
    /////////////////////////////////////////////////////////////////////////////////
    // For each face in the primal mesh, create a corresponding vertex in the dual mesh.
    // The position of each dual vertex is determined by weighted centroid approach.
    
    // Calculate face normals, face areas, and vertex areas
    auto faceNormals = get_face_normals(mesh_a, false);
    auto faceAreas = get_face_areas_doubled(faceNormals);
    auto vertexAreas = get_vertex_areas(mesh_a, faceAreas);
    
    for(auto face : faces(mesh_a)) {
        auto h = CGAL::halfedge(face, mesh_a);

        // Calculate weighted centroid based on vertex areas
        CGAL::Point_3<compas::Kernel> point;
        CGAL::Vector_3<compas::Kernel> weightedSum(0, 0, 0);
        double totalWeight = 0.0;
        
        // Get vertices of this face
        auto v0 = target(h, mesh_a);
        auto v1 = target(next(h, mesh_a), mesh_a);
        auto v2 = target(next(next(h, mesh_a), mesh_a), mesh_a);
        
        // Apply weights based on vertex areas (sqrt of the area as weight)
        double weight0 = std::sqrt(vertexAreas[v0]);
        double weight1 = std::sqrt(vertexAreas[v1]);
        double weight2 = std::sqrt(vertexAreas[v2]);
        
        totalWeight = weight0 + weight1 + weight2;
        
        weightedSum = (mesh_a.point(v0) - CGAL::ORIGIN) * weight0 + 
                      (mesh_a.point(v1) - CGAL::ORIGIN) * weight1 + 
                      (mesh_a.point(v2) - CGAL::ORIGIN) * weight2;
        
        // Convert back to a point by dividing by total weight
        point = CGAL::ORIGIN + (weightedSum / totalWeight);
        
        auto v = dual_mesh.add_vertex(); // Add vertex to dual mesh
        dual_mesh.point(v) = point;
        face_to_vertex[face] = v;
    }

    /////////////////////////////////////////////////////////////////////////////////
    // Project to the original mesh
    /////////////////////////////////////////////////////////////////////////////////

    // Define triangle type
    typedef CGAL::Kernel_traits<CGAL::Point_3<compas::Kernel>>::Kernel K;
    typedef CGAL::Triangle_3<K> Triangle;
    typedef std::vector<Triangle>::iterator Iterator;
    
    // Build a list of triangles from the mesh
    std::vector<Triangle> triangles;
    for(auto face : faces(original_mesh)) {
        auto halfedge = original_mesh.halfedge(face);
        auto v0 = original_mesh.source(halfedge);
        auto v1 = original_mesh.target(halfedge);
        auto v2 = original_mesh.target(next(halfedge, original_mesh));
        
        // Add the triangle
        triangles.push_back(Triangle(
            original_mesh.point(v0),
            original_mesh.point(v1),
            original_mesh.point(v2)
        ));
    }
    
    // Create the AABB tree
    typedef CGAL::AABB_triangle_primitive_3<K, Iterator> Primitive;
    typedef CGAL::AABB_traits_3<K, Primitive> Traits;
    typedef CGAL::AABB_tree<Traits> Tree;
    
    Tree tree(triangles.begin(), triangles.end());
    tree.accelerate_distance_queries();
    
    // Project each inner vertex to closest point on original mesh
    for(auto v : vertices(dual_mesh)) {
        bool is_boundary = false;
        for(auto h : CGAL::halfedges_around_target(v, dual_mesh)) {
            if(is_border(h, dual_mesh)) {
                is_boundary = true;
                break;
            }
        }
        
        if(!is_boundary) {
            auto p = dual_mesh.point(v);
            auto closest = tree.closest_point(p);
            dual_mesh.point(v) = closest;
        }
    }
    
    /////////////////////////////////////////////////////////////////////////////////
    // Dual Mesh Edge Creation
    /////////////////////////////////////////////////////////////////////////////////
    // Create edges in the dual mesh for each non-border edge in the filtered dual graph.
    // Each edge in the dual mesh connects two vertices that correspond to adjacent
    // faces in the primal mesh.
    
    for(auto edge : CGAL::make_range(edges(finite_dual))) {
        auto source_face = source(edge, finite_dual);
        auto target_face = target(edge, finite_dual);
        
        dual_mesh.add_edge(face_to_vertex[source_face], face_to_vertex[target_face]);
    }
    
    /////////////////////////////////////////////////////////////////////////////////
    // Dual Mesh Face Creation
    /////////////////////////////////////////////////////////////////////////////////
    // Create variable-length faces in the dual mesh. Each face corresponds to a vertex
    // in the primal mesh and consists of the dual vertices (face centroids) that
    // surround the primal vertex.
    
    std::map<typename boost::graph_traits<compas::Mesh>::vertex_descriptor, std::vector<int>> vertex_to_face;
    
    typename compas::Mesh::Property_map<typename boost::graph_traits<compas::Mesh>::face_descriptor, int> fccmap;
    fccmap = mesh_a.add_property_map<typename boost::graph_traits<compas::Mesh>::face_descriptor, int>("f:CC").first;
    int num_components = connected_components(finite_dual, fccmap);
    
    for(auto v : vertices(mesh_a)) {
        if(is_border(v, mesh_a)) {
            continue; // Skip border vertices
        }
        
        std::vector<int> face_indices;
        
        for(auto h : CGAL::halfedges_around_target(v, mesh_a)) {
            if(is_border(h, mesh_a)) continue;
            
            auto f = face(h, mesh_a);
            if(face_to_vertex.find(f) != face_to_vertex.end()) {
                auto dual_vertex = face_to_vertex[f];
                int idx = dual_vertex;
                face_indices.push_back(idx);
            }
        }
        
        if(face_indices.size() >= 3) {
            vertex_to_face[v] = face_indices; // Only add valid faces (with 3 or more vertices)
        }
    }

    std::vector<std::vector<int>> variable_faces;
    for(const auto& pair : vertex_to_face) {
        variable_faces.push_back(pair.second);
    }
    
    /////////////////////////////////////////////////////////////////////////////////
    // Boundary Processing
    /////////////////////////////////////////////////////////////////////////////////
    // The boundary processing algorithm creates special polylines/faces for boundary vertices:
    // 1. For each boundary vertex in the primal mesh, we create a sequence in the dual mesh
    // 2. This sequence consists of:
    //    a) The boundary vertex itself (same position as in primal)
    //    b) The midpoint of the first boundary edge connected to this vertex
    //    c) The centroids of all faces adjacent to this vertex, sorted by connectivity
    //       from the first boundary edge to the second boundary edge
    //    d) The midpoint of the second boundary edge connected to this vertex
    // 3. This creates a polyline that traces the boundary while connecting to the interior dual mesh
    
    /////////////////////////////////////////////////////////////////////////////////
    // Boundary Edge Midpoint Creation
    /////////////////////////////////////////////////////////////////////////////////
    // Create vertices at the midpoints of all boundary edges. These will be used
    // as the endpoints of the boundary polylines in the dual mesh.
    
    std::map<typename boost::graph_traits<compas::Mesh>::edge_descriptor,
              typename boost::graph_traits<compas::Mesh>::vertex_descriptor> edge_to_midpoint;
              
    for(auto e : edges(mesh_a)) {
        if(is_border(e, mesh_a)) {
            auto h = halfedge(e, mesh_a);
            auto source_v = source(h, mesh_a);
            auto target_v = target(h, mesh_a);
            auto midpoint = CGAL::midpoint(
                mesh_a.point(source_v),
                mesh_a.point(target_v)
            );
            
            auto midpoint_v = dual_mesh.add_vertex(); // Add midpoint vertex to dual mesh
            dual_mesh.point(midpoint_v) = midpoint;
            edge_to_midpoint[e] = midpoint_v;
        }
    }
    
    /////////////////////////////////////////////////////////////////////////////////
    // Boundary Vertex Processing
    /////////////////////////////////////////////////////////////////////////////////
    // For each boundary vertex, create a polyline in the dual mesh that connects
    // the midpoints of its adjacent boundary edges via the centroids of faces
    // adjacent to the boundary vertex.
    
    std::map<typename boost::graph_traits<compas::Mesh>::vertex_descriptor,
              typename boost::graph_traits<compas::Mesh>::vertex_descriptor> vertex_to_dual_vertex;

    std::vector<int> vertices_to_remove;
    
    for(auto v : vertices(mesh_a)) {
        if(is_border(v, mesh_a)) {

            
            std::vector<typename boost::graph_traits<compas::Mesh>::halfedge_descriptor> boundary_halfedges;
            
            for(auto h : CGAL::halfedges_around_target(v, mesh_a)) {
                if(is_border(edge(h, mesh_a), mesh_a)) {
                    boundary_halfedges.push_back(h);
                }
            }
            
            if(boundary_halfedges.size() != 2) {
                continue; // We need exactly two boundary halfedges
            }
            
            auto h1 = boundary_halfedges[0];
            auto h2 = boundary_halfedges[1];
            
            auto e1 = edge(h1, mesh_a);
            auto e2 = edge(h2, mesh_a);
            
            auto midpoint1_v = edge_to_midpoint[e1];
            auto midpoint2_v = edge_to_midpoint[e2];
            
            /////////////////////////////////////////////////////////////////////////////////
            // Face Collection and Edge Extraction
            /////////////////////////////////////////////////////////////////////////////////
            // Collect all faces adjacent to the boundary vertex and extract their edges.
            // This information will be used to determine the adjacency between faces.
            
            std::vector<typename boost::graph_traits<compas::Mesh>::face_descriptor> vertex_faces;
            std::vector<std::vector<typename boost::graph_traits<compas::Mesh>::edge_descriptor>> faces_edges;

            for(auto h : CGAL::halfedges_around_target(v, mesh_a)) {
                auto f = face(h, mesh_a);

                if(f != boost::graph_traits<compas::Mesh>::null_face() && std::find(vertex_faces.begin(), vertex_faces.end(), f) == vertex_faces.end()) {
                    vertex_faces.push_back(f);

                    auto h = halfedge(f, mesh_a);

                    std::vector<typename boost::graph_traits<compas::Mesh>::edge_descriptor> edges;
                    for(auto h : CGAL::halfedges_around_face(h, mesh_a)) {
                        auto e = edge(h, mesh_a);
                        edges.push_back(e);
                    }
                    faces_edges.push_back(edges);
                }
            }

            // Find the face containing the first boundary edge
            int e2_face = -1;
            for(int i = 0; i < faces_edges.size(); i++) {
                if(std::find(faces_edges[i].begin(), faces_edges[i].end(), e2) != faces_edges[i].end()) {
                    e2_face = i;
                    break;
                }
            }

            /////////////////////////////////////////////////////////////////////////////////
            // Face Ordering Algorithm
            /////////////////////////////////////////////////////////////////////////////////
            // Order the faces around the boundary vertex by starting from the face
            // containing the first boundary edge and traversing through adjacent faces
            // based on shared non-boundary edges.
            
            std::vector<typename boost::graph_traits<compas::Mesh>::face_descriptor> ordered_faces;
            std::vector<bool> visited(vertex_faces.size(), false);

            int current_face_idx = e2_face;
            ordered_faces.push_back(vertex_faces[current_face_idx]);
            visited[current_face_idx] = true;

            while (true) {
                bool found_next = false;
                auto& current_edges = faces_edges[current_face_idx];
                
                for (auto edge1 : current_edges) {
                    if (edge1 == e1 || edge1 == e2) continue; // Skip boundary edges
                    
                    for (size_t j = 0; j < vertex_faces.size(); j++) {
                        if (visited[j]) continue;
                        
                        if (std::find(faces_edges[j].begin(), faces_edges[j].end(), edge1) != faces_edges[j].end()) {
                            ordered_faces.push_back(vertex_faces[j]);
                            visited[j] = true;
                            current_face_idx = j;
                            found_next = true;
                            break;
                        }
                    }
                    
                    if (found_next) break;
                }
                
                if (!found_next) break; // Exit when no more adjacent faces are found
            }

 
            bool keep_boundary_vertex = false;

            /////////////////////////////////////////////////////////////////////////////////
            // Check which points to keep by angle
            /////////////////////////////////////////////////////////////////////////////////


            if(angle_radians > 0) {

                // Get the endpoints of each edge
                auto he1_src = mesh_a.source(h1);
                auto he1_tgt = mesh_a.target(h1);
                auto he2_src = mesh_a.source(h2);
                auto he2_tgt = mesh_a.target(h2);

                // Get vector directions (making sure they point away from the current vertex)
                auto get_vector = [&mesh_a](auto p1, auto p2) {
                    auto p1_point = mesh_a.point(p1);
                    auto p2_point = mesh_a.point(p2);
                    return CGAL::Vector_3<compas::Kernel>(p1_point, p2_point);
                };

                CGAL::Vector_3<compas::Kernel> v1, v2;
                if (he1_src == v) { // Use v instead of vh
                    v1 = get_vector(he1_src, he1_tgt);
                } else {
                    v1 = get_vector(he1_tgt, he1_src);
                }

                if (he2_src == v) { // Use v instead of vh
                    v2 = get_vector(he2_src, he2_tgt);
                } else {
                    v2 = get_vector(he2_tgt, he2_src);
                }
                
                // Calculate angle between vectors
                double dot_product = v1 * v2; // CGAL dot product
                double v1_length = std::sqrt(v1.squared_length());
                double v2_length = std::sqrt(v2.squared_length());
                double cos_angle = dot_product / (v1_length * v2_length);
                
                // Clamp to valid range for acos
                if (cos_angle < -1.0) cos_angle = -1.0;
                if (cos_angle > 1.0) cos_angle = 1.0;
                
                double angle = std::acos(cos_angle);
                
                // Check if angle meets the threshold criteria (angle % π > angle_radians)
                constexpr double PI = 3.14159265358979323846;
                keep_boundary_vertex = std::fmod(angle, PI) < angle_radians;

            }

            /////////////////////////////////////////////////////////////////////////////////
            // Check which points by fixed vertices
            /////////////////////////////////////////////////////////////////////////////////

            for (const auto& fixed_point : fixed_points) {
                if (CGAL::squared_distance(mesh_a.point(v), fixed_point) < 1e-6) {
                    keep_boundary_vertex = true;
                    break;
                }
            }

            /////////////////////////////////////////////////////////////////////////////////
            // Boundary Sequence Creation
            /////////////////////////////////////////////////////////////////////////////////
            // Assemble the final boundary sequence by combining the boundary vertex,
            // edge midpoints, and face centroids in the correct order.
            
            std::vector<int> boundary_sequence;

            if (keep_boundary_vertex) {

                auto dual_v = dual_mesh.add_vertex(); // Create a vertex in dual mesh at the same position
                dual_mesh.point(dual_v) = mesh_a.point(v);
                vertex_to_dual_vertex[v] = dual_v;

                boundary_sequence.push_back(vertex_to_dual_vertex[v]);
            }
           
            boundary_sequence.push_back(midpoint2_v); // Add first edge midpoint
            
            for(auto f : ordered_faces) {
                if(face_to_vertex.find(f) != face_to_vertex.end()) {
                    boundary_sequence.push_back(face_to_vertex[f]); // Add all face centroids in order
                }
            }
            
            boundary_sequence.push_back(midpoint1_v); // Add second edge midpoint
            
            if(boundary_sequence.size() >= 3) {
                variable_faces.push_back(boundary_sequence); // Only add valid sequences
            }


        }
    }
    
    /////////////////////////////////////////////////////////////////////////////////
    // Final Output Generation
    /////////////////////////////////////////////////////////////////////////////////
    // Convert the dual mesh to matrix format and return the complete dual mesh
    // representation, consisting of vertex coordinates and variable-length faces.


    
    auto [tri_vertices, tri_faces] = compas::mesh_to_vertices_and_faces(mesh_a);
    auto [dual_vertices, dual_faces] = compas::mesh_to_vertices_and_faces(dual_mesh);

    //Reverse the order of the faces
    for (auto& face : variable_faces) {
        std::reverse(face.begin(), face.end());
    }
    // Return a 4-element tuple to match the function declaration
    // Remeshed vertices, remeshed faces, dual vertices, dual mesh variable faces
    return std::make_tuple(tri_vertices, tri_faces, dual_vertices, variable_faces);

}

void pmp_pull(
    Eigen::Ref<compas::RowMatrixXd> vertices_a,
    Eigen::Ref<compas::RowMatrixXi> faces_a,
    Eigen::Ref<compas::RowMatrixXd> vertices_b,
    Eigen::Ref<compas::RowMatrixXd> normals_b)
{
    /////////////////////////////////////////////////////////////////////////////////
    // Mesh Creation
    /////////////////////////////////////////////////////////////////////////////////
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);

    // After scaling, use proper AABB tree for projection
    // Define triangle type
    typedef CGAL::Kernel_traits<CGAL::Point_3<compas::Kernel>>::Kernel K;
    typedef CGAL::Triangle_3<K> Triangle;
    typedef std::vector<Triangle>::iterator Iterator;
    typedef CGAL::Ray_3<K> Ray;
    
    // Build a list of triangles from the mesh
    std::vector<Triangle> triangles;
    for(auto face : mesh_a.faces()) {
        auto halfedge = mesh_a.halfedge(face);
        auto v0 = mesh_a.source(halfedge);
        auto v1 = mesh_a.target(halfedge);
        auto v2 = mesh_a.target(mesh_a.next(halfedge));
        
        // Add the triangle
        triangles.push_back(Triangle(
            mesh_a.point(v0),
            mesh_a.point(v1),
            mesh_a.point(v2)
        ));
    }
    
    // Create the AABB tree
    typedef CGAL::AABB_triangle_primitive_3<K, Iterator> Primitive;
    typedef CGAL::AABB_traits_3<K, Primitive> Traits;
    typedef CGAL::AABB_tree<Traits> Tree;
    
    Tree tree(triangles.begin(), triangles.end());
    tree.accelerate_distance_queries();
    
    // Check if we have valid normals (non-empty matrix)
    bool use_normals = normals_b.rows() == vertices_b.rows() && normals_b.cols() == 3;
    
    // Project each vertex
    for (int i = 0; i < vertices_b.rows(); ++i) {
        // Extract the point from the row and convert to CGAL point
        CGAL::Point_3<K> query_point(vertices_b(i, 0), vertices_b(i, 1), vertices_b(i, 2));
        
        CGAL::Point_3<K> projected_point;
        bool projection_successful = false;
        
        // If we have valid normals, try ray-based projection first
        if (use_normals) {
            // Create ray using vertex position and normal direction
            CGAL::Vector_3<K> normal(normals_b(i, 0), normals_b(i, 1), normals_b(i, 2));
            
            // Only proceed if normal has non-zero length
            if (normal.squared_length() > 1e-10) {
                // Normalize the normal vector
                normal = normal / std::sqrt(normal.squared_length());
                
                // Try rays in both normal directions - first try in negative normal direction
                Ray ray(query_point, normal);
                
                if (tree.do_intersect(ray)) {
                    auto intersection = tree.any_intersection(ray);
                    if (intersection) {
                        // Handle the variant result properly
                        auto& intersection_variant = intersection->first;
                        
                        // Check if this is a Point_3 intersection using std::get_if for std::variant
                        if (const CGAL::Point_3<K>* p = std::get_if<CGAL::Point_3<K>>(&intersection_variant)) {
                            projected_point = *p;
                            projection_successful = true;
                        }
                        // Handle Segment_3 intersection case using std::get_if for std::variant
                        else if (const CGAL::Segment_3<K>* s = std::get_if<CGAL::Segment_3<K>>(&intersection_variant)) {
                            // For a segment intersection, take the endpoint closest to the query point
                            double dist1 = CGAL::squared_distance(query_point, s->source());
                            double dist2 = CGAL::squared_distance(query_point, s->target());
                            projected_point = (dist1 < dist2) ? s->source() : s->target();
                            projection_successful = true;
                        }
                    }
                }
                
                // If no intersection found in negative direction, try positive direction
                if (!projection_successful) {
                    Ray ray(query_point, -normal);
                    
                    if (tree.do_intersect(ray)) {
                        auto intersection = tree.any_intersection(ray);
                        if (intersection) {
                            // Handle the variant result properly
                            auto& intersection_variant = intersection->first;
                            
                            // Check if this is a Point_3 intersection using std::get_if for std::variant
                            if (const CGAL::Point_3<K>* p = std::get_if<CGAL::Point_3<K>>(&intersection_variant)) {
                                projected_point = *p;
                                projection_successful = true;
                            }
                            // Handle Segment_3 intersection case using std::get_if for std::variant
                            else if (const CGAL::Segment_3<K>* s = std::get_if<CGAL::Segment_3<K>>(&intersection_variant)) {
                                // For a segment intersection, take the endpoint closest to the query point
                                double dist1 = CGAL::squared_distance(query_point, s->source());
                                double dist2 = CGAL::squared_distance(query_point, s->target());
                                projected_point = (dist1 < dist2) ? s->source() : s->target();
                                projection_successful = true;
                            }
                        }
                    }
                }
            }
        }
        
        // If ray projection didn't work or we don't have normals, use closest point method as fallback
        if (!projection_successful) {
            projected_point = tree.closest_point(query_point);
        }
        
        // Update the vertex in the matrix
        vertices_b(i, 0) = projected_point.x();
        vertices_b(i, 1) = projected_point.y();
        vertices_b(i, 2) = projected_point.z();
    }
}


void pmp_project(
    Eigen::Ref<compas::RowMatrixXd> vertices_a,
    Eigen::Ref<compas::RowMatrixXi> faces_a,
    Eigen::Ref<compas::RowMatrixXd> vertices_b)
{
    /////////////////////////////////////////////////////////////////////////////////
    // Mesh Creation
    /////////////////////////////////////////////////////////////////////////////////
    compas::Mesh mesh_a = compas::mesh_from_vertices_and_faces(vertices_a, faces_a);

    // After scaling, use proper AABB tree for projection
    // Define triangle type
    typedef CGAL::Kernel_traits<CGAL::Point_3<compas::Kernel>>::Kernel K;
    typedef CGAL::Triangle_3<K> Triangle;
    typedef std::vector<Triangle>::iterator Iterator;
    typedef CGAL::Ray_3<K> Ray;
    
    // Build a list of triangles from the mesh
    std::vector<Triangle> triangles;
    for(auto face : mesh_a.faces()) {
        auto halfedge = mesh_a.halfedge(face);
        auto v0 = mesh_a.source(halfedge);
        auto v1 = mesh_a.target(halfedge);
        auto v2 = mesh_a.target(mesh_a.next(halfedge));
        
        // Add the triangle
        triangles.push_back(Triangle(
            mesh_a.point(v0),
            mesh_a.point(v1),
            mesh_a.point(v2)
        ));
    }
    
    // Create the AABB tree
    typedef CGAL::AABB_triangle_primitive_3<K, Iterator> Primitive;
    typedef CGAL::AABB_traits_3<K, Primitive> Traits;
    typedef CGAL::AABB_tree<Traits> Tree;
    
    Tree tree(triangles.begin(), triangles.end());
    tree.accelerate_distance_queries();
    
    // Project each vertex
    for (int i = 0; i < vertices_b.rows(); ++i) {
        // Extract the point from the row and convert to CGAL point
        CGAL::Point_3<K> query_point(vertices_b(i, 0), vertices_b(i, 1), vertices_b(i, 2));
        
        CGAL::Point_3<K> projected_point;

        projected_point = tree.closest_point(query_point);
        
        // Update the vertex in the matrix
        vertices_b(i, 0) = projected_point.x();
        vertices_b(i, 1) = projected_point.y();
        vertices_b(i, 2) = projected_point.z();
    }
}

NB_MODULE(_meshing, m) {
    m.def(
        "pmp_trimesh_remesh",
        &pmp_trimesh_remesh,
        "Remesh a triangle mesh with target edge length",
        "vertices_a"_a,
        "faces_a"_a,
        "target_edge_length"_a,
        "number_of_iterations"_a = 10,
        "do_project"_a = true
    );
    
    m.def(
        "pmp_trimesh_remesh_dual",
        &pmp_trimesh_remesh_dual,
        "Remesh a triangle mesh with target edge length",
        "vertices_a"_a,
        "faces_a"_a,
        "fixed_vertices"_a,
        "length_factor"_a=1,
        "number_of_iterations"_a = 10,
        "angle_radians"_a = 0.9,
        "scale_factor"_a = 1.0
    );

    m.def(
        "pmp_pull",
        &pmp_pull,
        "Pull a set of points to a mesh using vectors by ray-mesh intersection",
        "vertices_a"_a,
        "faces_a"_a,
        "vertices_b"_a,
        "normals_b"_a
    );

    m.def(
        "pmp_project",
        &pmp_project,
        "Project a set of points to the closest point on a mesh",
        "vertices_a"_a,
        "faces_a"_a,
        "vertices_b"_a
    );
}