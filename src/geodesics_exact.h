#pragma once

#include "compas.h"

/**
 * @brief Register the exact-geodesic entry points on the `_geodesics` module.
 *
 * Exact polyhedral geodesics (CGAL `Surface_mesh_shortest_path`) live in their own
 * translation unit so that editing the heat method does not recompile their templates,
 * and vice versa. The module itself stays single, so `compas_cgal.geodesics` keeps one
 * extension module behind it.
 *
 * @param m The `_geodesics` module being defined in geodesics.cpp.
 */
void bind_exact_geodesics(nb::module_& m);
