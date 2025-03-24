# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] 2025-03-24

### Added

### Changed

### Removed


## [0.7.7] 2025-03-20

### Added

* Added GitHub release action.

### Changed

* Split binding into separate dynamic libraries.
* The documentation contribution guide has been updated based on the single-file and single dynamic library build process.
* Example images in the documentation have been updated.
* The Python/C++ module name has been changed from `name_ext` to `_name`.

### Removed


## [0.7.6] 2025-03-19

### Added

### Changed

* Temp remove reconstruction and 2D skeleton to fix memory problems during conda build for windows.

### Removed


## [0.7.5] 2025-03-19

### Added

### Changed

### Removed


## [0.7.4] 2025-03-19

### Added

* Added build flags for file size reduction in `CMakeLists.txt`.

### Changed

* Precompiled header is optional and set to OFF to reduce deployment built size.
* Moved `compas.h` module specific headers to the individual source files.

### Removed

* Remove unnecessary headers from `compas_cgal.h`.
* Remove `reconstruction.h` and `reconstruction.cpp`.
* Remove `straight_skeleton_2.h` and `straight_skeleton_2.cpp`.


## [0.7.3] 2025-03-18

### Added

### Changed

* Nanobind integration.

### Removed

* Files related to pybind11.


## [0.7.2] 2024-10-29

### Added

* Added recipe hasher.
* Added `scip` to dev install instructions in README.md
* Added `compas_cgal.straight_skeleton_2.offset_polygon_with_holes`.

### Changed

* Changed name of `compas_cgal.straight_skeleton_2.create_interior_straight_skeleton` to `interior_straight_skeleton`
* Changed name of `compas_cgal.straight_skeleton_2.create_interior_straight_skeleton_with_holes` to `interior_straight_skeleton_with_holes`
* Changed name of `compas_cgal.straight_skeleton_2.create_offset_polygons_2` to `offset_polygon`
* Changed name of `compas_cgal.straight_skeleton_2.create_weighted_offset_polygons_2` to `weighted_offset_polygon`
* Changed version to `scip=9.0.0` for windows.

### Removed

* Removed optional support for GLPK for polygonal surface reconstruction.

## [0.7.1] 2024-09-26

### Added

### Changed

* Changed the return values of `compas_cgal.straight_skeleton_2.create_interior_straight_skeleton` and `compas_cgal.straight_skeleton_2.create_interior_straight_skeleton_with_holes`.
* Changed the return values of `compas_cgal.create_interior_straight_skeleton`.

### Removed

## [0.7.0] 2024-05-14

### Added

* Added `compas_cgal.straight_skeleton_2.create_interior_straight_skeleton`.
* Added `compas_cgal.straight_skeleton_2.create_interior_straight_skeleton_with_holes`.
* Added `compas_cgal.straight_skeleton_2.create_offset_polygons_2_inner`.
* Added `compas_cgal.straight_skeleton_2.create_offset_polygons_2_outer`.
* Added `compas_cgal.straight_skeleton_2.create_weighted_offset_polygons_2_inner`.
* Added `compas_cgal.straight_skeleton_2.create_weighted_offset_polygons_2_outer`.

### Changed

### Removed

## [0.6.0] 2024-02-01

### Added

* Added `compas_cgal.reconstruction.poission_surface_reconstruction`.
* Added `compas_cgal.reconstruction.pointset_outlier_removal`.
* Added `compas_cgal.reconstruction.pointset_reduction`.
* Added `compas_cgal.reconstruction.pointset_smoothing`.
* Added `compas_cgal.reconstruction.pointset_normal_estimation`.
* Added `compas_cgal.skeletonization.mesh_skeleton`.
* Added `compas_cgal.subdivision.mesh_subdivision_catmull_clark`.
* Added `compas_cgal.subdivision.mesh_subdivision_loop`.
* Added `compas_cgal.subdivision.mesh_subdivision_sqrt3`.
* Added `compas_cgal.triangulation.refined_delaunay_mesh`.

### Changed

* Moved main include types like `Point`, `Vector`, `Polyline` and etc. to the `compas` namespace.

### Removed

## [0.5.0] 2022-10-07

### Added

* Support to python 3.10.
* Added Changelog check in PRs.
* Exposing mesh `compas_cgal.booleans.split` function.

### Changed

* Updated github workflow.

### Removed

## [0.4.0] 2022-01-20

### Added

* Added type annotations.
* Added dimension checks to trimesh setters.
* Added `compas_cgal.measure.volume`.
* Added `compas_cgal.subdivision.catmull_clark`.

### Changed

### Removed

## [0.3.0] 2021-12-14

### Added

* Added `compas_cgal.booleans.boolean_union`.
* Added `compas_cgal.booleans.boolean_difference`.
* Added `compas_cgal.booleans.boolean_intersection`.
* Added `compas_cgal.intersections.intersection_mesh_mesh`.
* Added `compas_cgal.meshing.remesh`.
* Added `compas_cgal.slicer.slice_mesh`.
* Added `compas_cgal.triangulation.delaunay_triangulation`.
* Added `compas_cgal.triangulation.constrained_delaunay_triangulation`.
* Added `compas_cgal.triangulation.conforming_delaunay_triangulation`.

### Changed

### Removed
