include(FetchContent)


### Configuration
set(CompasCGAL_ROOT "${CMAKE_CURRENT_LIST_DIR}/..")
set(CompasCGAL_EXTERNAL "${CompasCGAL_ROOT}/ext")

# Download and update 3rdparty libraries
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
list(REMOVE_DUPLICATES CMAKE_MODULE_PATH)
include(CompasCGALDownloadExternal)

# Eigen
if(NOT TARGET Eigen3::Eigen)
    CompasCGAL_download_eigen()
endif()

# pybind11
if(NOT TARGET pybind11::pybind11)
    CompasCGAL_download_pybind11()
endif()
