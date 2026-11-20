#pragma once

#include "compas.h"

#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits_3.h>
#include <CGAL/AABB_face_graph_triangle_primitive.h>
#include <CGAL/Polygon_mesh_processing/shape_predicates.h>
#include <CGAL/Side_of_triangle_mesh.h>
#include <CGAL/boost/graph/helpers.h>

// MeshDistance class is defined in distance.cpp and exposed via nanobind
