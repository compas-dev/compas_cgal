from pathlib import Path
from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_view2.app import App
from compas_cgal.reconstruction import pointset_outlier_removal

HERE = Path(__file__).parent
FILE = HERE / ".." / ".." / "data" / "forked_branch_1.ply"

cloud1 = Pointcloud.from_ply(FILE)

points = pointset_outlier_removal(cloud1, 30, 2.0)

cloud2 = Pointcloud(points)

viewer = App(width=1600, height=900)
viewer.view.camera.scale = 1000
viewer.view.grid.cell_size = 1000

viewer.add(cloud1)
viewer.add(cloud2.transformed(Translation.from_vector([1000, 0, 0])))

viewer.view.camera.zoom_extents()
viewer.run()
