import compas_cgal
from compas.datastructures import Mesh
from compas_viewer import viewer
from compas_viewer.viewer import Viewer

try:
    import numpy as np
    from numpy.testing import assert_array_equal
    def needs_numpy_and_eigen(x):
        return x
except:
    needs_numpy_and_eigen = pytest.mark.skip(reason="NumPy and Eigen are required")



# @plugin(category="trimesh", pluggable_name="trimesh_remesh")
@needs_numpy_and_eigen
def mesh_remesh(
    mesh, #: VerticesFaces,
    target_edge_length: float,
    number_of_iterations: int = 10,
    do_project: bool = True,
): #-> VerticesFacesNumpy:
    """Remeshing of a triangle mesh.

    Parameters
    ----------
    mesh : :attr:`compas_cgal.types.VerticesFaces`
        The mesh to remesh.
    target_edge_length : float
        The target edge length.
    number_of_iterations : int, optional
        Number of remeshing iterations.
    do_project : bool, optional
        If True, reproject vertices onto the input surface when they are created or displaced.

    Returns
    -------
    :attr:`compas_cgal.types.VerticesFacesNumpy`

    Notes
    -----
    This remeshing function only constrains the edges on the boundary of the mesh.
    Protecting specific features or edges is not implemented yet.

    Examples
    --------
    >>> from compas.geometry import Sphere, Polyhedron
    >>> from compas_cgal.meshing import mesh_remesh

    >>> sphere = Sphere(0.5, point=[1, 1, 1])
    >>> mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    >>> V, F = mesh_remesh(mesh, 1.0)
    >>> shape = Polyhedron(V.tolist(), F.tolist())

    """
    V, F = mesh.to_vertices_and_faces()
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int32)
    return compas_cgal.remesh(V, F, target_edge_length, number_of_iterations)

mesh = Mesh.from_polyhedron(20)
# viewer = Viewer()
# viewer.scene.add(mesh)
# viewer.show()
mesh_remesh(mesh, 0.5)