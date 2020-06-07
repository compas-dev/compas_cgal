cmake_minimum_required(VERSION 3.1.0 FATAL_ERROR)
project(compas_cgal)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
                      ${CMAKE_CURRENT_SOURCE_DIR}/cmake
                      ${CMAKE_CURRENT_SOURCE_DIR}/cmake/CGAL)

# #Python
# get_filename_component(PYTHON_DIR ${PYTHON_EXECUTABLE} DIRECTORY)
# if (NOT WIN32)
#     # on OSX the executable is in "bin"
#     # so go one more level up
#     get_filename_component(PYTHON_DIR ${PYTHON_DIR} DIRECTORY)
# endif ()

#Pybind11
include(CompasCGALDependencies)
add_subdirectory(ext/pybind11)
set(PYBIND11_CPP_STANDARD -std=c++14)

#GMP
find_package(GMP REQUIRED)
find_package(MPFR REQUIRED)

#include directory
include_directories(include ext/eigen)
if (WIN32)
    include_directories("$ENV{CONDA_PREFIX}/Library/include")
else ()
    include_directories("$ENV{CONDA_PREFIX}/include")
endif ()

# #Eigen
# if (WIN32)
#     set(EIGEN3_INCLUDE_DIR "${PYTHON_DIR}/Library/include/eigen3")
# else ()
#     set(EIGEN3_INCLUDE_DIR "${PYTHON_DIR}/include/eigen3")
# endif ()

# #Boost
# if (WIN32)
#     set(BOOST_ROOT "${PYTHON_DIR}/Library/include")
# else ()
#     set(BOOST_ROOT "${PYTHON_DIR}/include")
# endif ()

pybind11_add_module(_cgal
    src/booleans.cpp
    src/compas.cpp
    src/compas_cgal.cpp
    src/intersections.cpp
    src/meshing.cpp
    src/slicer.cpp
)

target_link_libraries(_cgal
    PRIVATE
    ${GMP_LIBRARIES}
    ${MPFR_LIBRARIES}
)

set_target_properties(_cgal
    PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/compas_cgal/compas_cgal"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/compas_cgal"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/compas_cgal"
)
