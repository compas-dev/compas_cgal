from compas.plugins import plugin

from compas_cgal.types import VerticesFaces
from compas_cgal.types import ListOfPlanes
from compas_cgal.types import ListOfPolylinesNumpy


@plugin(category='trimesh', pluggable_name='trimesh_slice')
def slice_mesh(mesh: VerticesFaces,
               planes: ListOfPlanes) -> ListOfPolylinesNumpy:
    pass
