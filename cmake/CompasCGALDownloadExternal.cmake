################################################################################
include(DownloadProject)

# With CMake 3.8 and above, we can hide warnings about git being in a
# detached head by passing an extra GIT_CONFIG option
if(NOT (${CMAKE_VERSION} VERSION_LESS "3.8.0"))
    set(CompasCGAL_EXTRA_OPTIONS "GIT_CONFIG advice.detachedHead=False")
else()
    set(CompasCGAL_EXTRA_OPTIONS "")
endif()

# Shortcut function
function(CompasCGAL_download_project name)
    download_project(
        PROJ         ${name}
        SOURCE_DIR   ${CompasCGAL_EXTERNAL}/${name}
        DOWNLOAD_DIR ${CompasCGAL_EXTERNAL}/.cache/${name}
        QUIET
        ${CompasCGAL_EXTRA_OPTIONS}
        ${ARGN}
    )
endfunction()

################################################################################
## Eigen
function(CompasCGAL_download_eigen)
    CompasCGAL_download_project(eigen
            GIT_REPOSITORY https://github.com/eigenteam/eigen-git-mirror.git
            GIT_TAG        3.3.7
            )
endfunction()

## Catch2
function(CompasCGAL_download_catch)
    CompasCGAL_download_project(catch2
            GIT_REPOSITORY https://github.com/catchorg/Catch2.git
            GIT_TAG        d63307279412de3870cf97cc6802bae8ab36089e # v 2.7.0
            )
endfunction()

## TBB
function(CompasCGAL_download_tbb)
    CompasCGAL_download_project(tbb
            GIT_REPOSITORY https://github.com/wjakob/tbb.git
            GIT_TAG        20357d83871e4cb93b2c724fe0c337cd999fd14f
            )
endfunction()

#function(CompasCGAL_download_tbb)
#    CompasCGAL_download_project(tbb
#            GIT_REPOSITORY https://github.com/oneapi-src/oneTBB.git
#            GIT_TAG        60b7d0a78f8910976678ba63a19fdaee22c0ef65)
#endfunction()


function(CompasCGAL_download_tbb_binary)
    CompasCGAL_download_project(tbb
            GIT_REPOSITORY https://github.com/KIKI007/tbb_binary.git
            GIT_TAG        8fb255d3d464b787e1629318c262d80befc87497)
endfunction()


## CLP
function(CompasCGAL_download_clp)
    CompasCGAL_download_project(clp
            GIT_REPOSITORY https://github.com/KIKI007/COIN-OR-osi-clp.git
            GIT_TAG        9822c5ab97770ade0c5adc58faf36778cd460db6            # v1.0.0
            )
endfunction()


## IPOPT
function(CompasCGAL_download_ipopt)
    CompasCGAL_download_project(ipopt
            GIT_REPOSITORY https://github.com/robin-forks/COIN-OR_Ipopt
            GIT_TAG        v1.2.0
            )
endfunction()

## COIN-OR LP
function(CompasCGAL_download_coinor_lp)
    CompasCGAL_download_project(coinor_lp
            GIT_REPOSITORY https://github.com/robin-forks/COIN-OR_suite_cmake_compatible.git
            GIT_TAG        7d69f4b48869e3f30db11cf04e1b3bc49480fca8
            )
endfunction()

## filesystem
function(CompasCGAL_download_filesystem)
    CompasCGAL_download_project(filesystem
            GIT_REPOSITORY     https://github.com/KIKI007/filesystem.git
            GIT_TAG            90fb57f9698bce2961d3a23bc6c957abddaeff68
            )
endfunction()

## libigl
function(CompasCGAL_download_libigl)
    CompasCGAL_download_project(libigl
            GIT_REPOSITORY     https://github.com/libigl/libigl.git
            GIT_TAG            87b54fc4dcc5aea182dd842a55ac75536fb69e1a
            )
endfunction()

### ShapeOp
#function(CompasCGAL_download_shapeop)
#    CompasCGAL_download_project(shapeop
#            GIT_REPOSITORY     https://github.com/EPFL-LGG/ShapeOp.git
#            GIT_TAG            9a79b808c5e4144b8b6f0f429df7273f61e95547
#            )
#endfunction()

# pugixml
function(CompasCGAL_download_pugixml)
    CompasCGAL_download_project(pugixml
            GIT_REPOSITORY     https://github.com/robin-forks/pugixml.git
            GIT_TAG            bbcc25dc72ecb8b9d53bd2342d7b37e9e8f33264
            )
endfunction()

# pybind11
function(CompasCGAL_download_pybind11)
    CompasCGAL_download_project(pybind11
            GIT_REPOSITORY     https://github.com/pybind/pybind11.git
            GIT_TAG            023487164915c5b62e16a9b4e0b37cb01cd5500a
            )
endfunction()

# nanogui
function(CompasCGAL_download_nanogui)
    CompasCGAL_download_project(nanogui
            GIT_REPOSITORY     https://github.com/mitsuba-renderer/nanogui.git
            GIT_TAG            741f3323c73891f62c71427c1fd766b8a32035f5
            )
endfunction()

function(CompasCGAL_download_json)
    CompasCGAL_download_project(json
            GIT_REPOSITORY     https://github.com/nlohmann/json.git
            GIT_TAG            dd7e25927fe7a49c81d07943c32444f0a9011665
            )
endfunction()
