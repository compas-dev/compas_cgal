cmake_minimum_required(VERSION 3.15...3.26)

project(cgal_wrapper LANGUAGES CXX)

# =====================================================================
# Dependencies
# =====================================================================
include(ExternalProject)

# Define source directories for external dependencies
set(EXTERNAL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external")
set(CGAL_SOURCE_DIR "${EXTERNAL_DIR}/cgal")
set(BOOST_SOURCE_DIR "${EXTERNAL_DIR}/boost")
set(EIGEN_SOURCE_DIR "${EXTERNAL_DIR}/eigen")

# ========================================================================
# CGAL
# ========================================================================
if(NOT EXISTS "${CGAL_SOURCE_DIR}")
    message(STATUS "Downloading CGAL...")
    ExternalProject_Add(
        cgal_download
        URL https://github.com/CGAL/cgal/releases/download/v6.0.1/CGAL-6.0.1.zip
        SOURCE_DIR       "${CGAL_SOURCE_DIR}"
        CONFIGURE_COMMAND ""
        BUILD_COMMAND     ""
        INSTALL_COMMAND   ""
        LOG_DOWNLOAD ON
        UPDATE_COMMAND    ""
        PATCH_COMMAND     ""
        TLS_VERIFY       ON
    )
endif()

# ========================================================================
# BOOST
# ========================================================================
if(NOT EXISTS "${BOOST_SOURCE_DIR}")
    message(STATUS "Downloading Boost...")
    ExternalProject_Add(boost
    URL https://archives.boost.io/release/1.82.0/source/boost_1_82_0.tar.gz
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR>/boost ${CMAKE_BINARY_DIR}/install/boost/include/boost
  )
endif()

# ========================================================================
# EIGEN
# ========================================================================
if(NOT EXISTS "${EIGEN_SOURCE_DIR}")
    message(STATUS "Downloading Eigen...")
    ExternalProject_Add(
        eigen_download
        URL https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
        SOURCE_DIR       "${EIGEN_SOURCE_DIR}"
        CONFIGURE_COMMAND ""
        BUILD_COMMAND     ""
        INSTALL_COMMAND   ""
        LOG_DOWNLOAD ON
        UPDATE_COMMAND    ""
        PATCH_COMMAND     ""
    )
endif()

# Add include directories
set(CGAL_INCLUDE_DIR "${CGAL_SOURCE_DIR}/include")
set(BOOST_INCLUDE_DIR "${BOOST_SOURCE_DIR}")
set(EIGEN_INCLUDE_DIR "${EIGEN_SOURCE_DIR}")

# Print include directories for verification
message(STATUS "====================================================")
message(STATUS "CGAL INCLUDE DIRECTORY: ${CGAL_INCLUDE_DIR}")
message(STATUS "BOOST INCLUDE DIRECTORY: ${BOOST_INCLUDE_DIR}")
message(STATUS "EIGEN INCLUDE DIRECTORY: ${EIGEN_INCLUDE_DIR}")
message(STATUS "====================================================")

include_directories(
    ${CGAL_INCLUDE_DIR}
    ${BOOST_INCLUDE_DIR}
    ${EIGEN_INCLUDE_DIR}
)

# Define CGAL as header only
add_definitions(-DCGAL_HEADER_ONLY)

# =====================================================================
# Binding
# =====================================================================

if (NOT SKBUILD)
  message(WARNING "\
  This CMake file is meant to be executed using 'scikit-build'. Running
  it directly will almost certainly not produce the desired result. If
  you are a user trying to install this package, please use the command
  below, which will install all necessary build dependencies, compile
  the package in an isolated environment, and then install it.
  =====================================================================
   $ pip install .
  =====================================================================
  If you are a software developer, and this is your own package, then
  it is usually much more efficient to install the build dependencies
  in your environment once and use the following command that avoids
  a costly creation of a new virtual environment at every compilation:
  =====================================================================
   $ pip install nanobind scikit-build-core[pyproject]
   $ conda install cmake
   $ pip install --no-build-isolation -ve .
   $ pip install --no-build-isolation -ve . -Ceditable.rebuild=true
  =====================================================================
  You may optionally add -Ceditable.rebuild=true to auto-rebuild when
  the package is imported. Otherwise, you need to re-run the above
  after editing C++ files.")
endif()

# Try to import all Python components potentially needed by nanobind
find_package(Python 3.8
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

# Import nanobind through CMake's find_package mechanism
find_package(nanobind CONFIG REQUIRED)

# We are now ready to compile the actual extension module
nanobind_add_module(
  compas_cgal_ext
  STABLE_ABI
  NB_STATIC
  src/compas_cgal_hello_world.cpp
)

# Set include directories for the extension
target_include_directories(compas_cgal_ext PRIVATE 
    ${CGAL_INCLUDE_DIR}
    ${BOOST_INCLUDE_DIR}
    ${EIGEN_INCLUDE_DIR}
)

# Install directive for scikit-build-core
install(TARGETS compas_cgal_ext LIBRARY DESTINATION compas_cgal)