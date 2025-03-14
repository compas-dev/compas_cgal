********************************************************************************
CMake Configuration
********************************************************************************

This project uses CMake with scikit-build-core and nanobind for building Python extensions.

Core Settings
=============

.. code-block:: cmake

    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

External Dependencies
=====================

We use CMake's ExternalProject to manage external dependencies (CGAL, Boost, Eigen) as header-only libraries. This approach:

1. Downloads dependencies at configure time
2. Extracts them to the ``external`` directory
3. Sets them up as header-only libraries
4. Requires no system-wide installation

Configuration
-------------

.. code-block:: cmake

    # Define source directories
    set(EXTERNAL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/external")
    set(CGAL_SOURCE_DIR "${EXTERNAL_DIR}/cgal")
    set(BOOST_SOURCE_DIR "${EXTERNAL_DIR}/boost")
    set(EIGEN_SOURCE_DIR "${EXTERNAL_DIR}/eigen")

    # Create target for all downloads
    add_custom_target(external_downloads ALL)

Example: CGAL Setup
-------------------

.. code-block:: cmake

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
        )
        add_dependencies(external_downloads cgal_download)
    endif()

Key Components
--------------

* ``SOURCE_DIR``: Where to extract the downloaded files
* Empty ``CONFIGURE_COMMAND``, ``BUILD_COMMAND``, ``INSTALL_COMMAND``: Treat as header-only
* ``LOG_DOWNLOAD ON``: Enable download progress logging
* ``add_dependencies``: Ensure downloads complete before building

Include Directories
-------------------

After download, headers are made available through:

.. code-block:: cmake

    include_directories(
        ${CGAL_INCLUDE_DIR}
        ${BOOST_INCLUDE_DIR}
        ${EIGEN_INCLUDE_DIR}
    )

Build Flags
-----------

Dependencies are configured as header-only libraries with specific compiler flags:

.. code-block:: cmake

    add_definitions(
        -DCGAL_HEADER_ONLY
        -DBOOST_ALL_NO_LIB 
        -DBOOST_ALL_DYN_LINK=0
        -DCGAL_DISABLE_GMP
        -DCGAL_USE_BOOST_MP
    )

    # Platform-specific flags
    if(MSVC)
        set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
    endif()
    set(CGAL_DO_NOT_WARN_ABOUT_CMAKE_BUILD_TYPE ON)

This setup ensures:
* No compilation of external libraries needed
* Consistent headers across different platforms
* Simplified dependency management
* Reproducible builds

Precompiled Headers
===================

We use precompiled headers to improve build times. The configuration is optimized for template-heavy code:

.. code-block:: cmake

    # Enhanced PCH configuration
    set(CMAKE_PCH_INSTANTIATE_TEMPLATES ON)  # Improve template compilation
    set(CMAKE_PCH_WARN_INVALID ON)          # Warn about invalid PCH usage

    # Configure PCH for the extension
    target_precompile_headers(compas_cgal_ext 
        PRIVATE 
        src/compas.h
    )

Note: When adding new headers that are frequently included, consider adding them to the precompiled header ``src/compas.h`` to further improve build times. Common headers to precompile:

* STL containers (vector, string)
* CGAL core headers
* Boost headers used by CGAL
* Eigen matrix types