#include "reconstruction.h"

std::tuple<compas::RowMatrixXd, compas::RowMatrixXi>
poisson_surface_reconstruction(
    Eigen::Ref<const compas::RowMatrixXd> &P)
{
}

// ===========================================================================
// PyBind11
// ===========================================================================

void init_reconstruction(pybind11::module &m)
{
    pybind11::module submodule = m.def_submodule("reconstruction");

    submodule.def(
        "poisson_surface_reconstruction",
        &poisson_surface_reconstruction,
        pybind11::arg("P").noconvert());
};
