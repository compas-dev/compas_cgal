
#include "slicer.h"

std::vector<compas::RowMatrixXd>
pmp_slice_mesh(
    Eigen::Ref<const compas::RowMatrixXd> V,
    Eigen::Ref<const compas::RowMatrixXi> F,
    Eigen::Ref<const compas::RowMatrixXd> P,
    Eigen::Ref<const compas::RowMatrixXd> N)
{
    compas::Mesh mesh = compas::mesh_from_vertices_and_faces(V, F);

    CGAL::Polygon_mesh_slicer<compas::Mesh, compas::Kernel> slicer(mesh);
    compas::Polylines polylines;
    std::back_insert_iterator<compas::Polylines> slices(polylines);

    int number_of_planes = P.rows();

    for (int i = 0; i < number_of_planes; i++)
    {
        compas::Kernel::Plane_3 plane = compas::Kernel::Plane_3(
            compas::Kernel::Point_3(P(i, 0), P(i, 1), P(i, 2)),
            compas::Kernel::Vector_3(N(i, 0), N(i, 1), N(i, 2)));

        slicer(plane, slices);
    }

    std::vector<compas::RowMatrixXd> result = compas::polylines_to_lists_of_points(polylines);
    return result;
};

void init_slicer(nb::module_& m) {
    auto submodule = m.def_submodule("slicer");

    submodule.def(
        "slice_mesh",
        &pmp_slice_mesh,
        """ Slice a mesh with a set of planes. """,
        "V"_a,
        "F"_a,
        "P"_a,
        "N"_a);

}
