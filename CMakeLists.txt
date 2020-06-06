cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)
project(compas_cgal)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
                      ${CMAKE_CURRENT_SOURCE_DIR}/cmake
                      ${CMAKE_CURRENT_SOURCE_DIR}/cmake/CGAL)


#Pybind11
include(CompasCGALDependencies)
add_subdirectory(ext/pybind11)
set(PYBIND11_CPP_STANDARD -std=c++14)

#GMP
find_package(GMP REQUIRED)
find_package(MPFR REQUIRED)

#include directory
include_directories(include ext/eigen)
include_directories("$ENV{HOME}/anaconda3/envs/cgal/include")

pybind11_add_module(_cgal src/booleans.cpp src/compas.cpp src/compas_cgal.cpp src/meshing.cpp src/slicer.cpp)
target_link_libraries(_cgal PRIVATE ${GMP_LIBRARIES} ${MPFR_LIBRARIES})

set_target_properties(_cgal
        PROPERTIES
        ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/compas_cgal/compas_cgal"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/compas_cgal"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/compas_cgal"
        )





