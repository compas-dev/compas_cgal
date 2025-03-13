from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_cgal.reconstruction import pointset_smoothing
from compas_viewer import Viewer
from compas_viewer.config import Config
from line_profiler import profile


@profile
def reconstruction_pointset_smoothing():
    ply_file_path = Path(__file__).parent.parent.parent / "data" / "box.ply"
    original_points = Pointcloud.from_ply(ply_file_path)
    original_points.transform(Translation.from_vector([-10000, 0, 0]))
    transformed_points = Pointcloud.from_ply(ply_file_path)
    transformed_points.transform(Translation.from_vector([10000, 0, 0]))
    smoothed_points = pointset_smoothing(transformed_points, 1000, 3)
    c_original = Pointcloud(original_points)
    c_transformed = Pointcloud(smoothed_points)
    return c_original, c_transformed


if __name__ == "__main__":
    c_smoothing_0, c_smoothing_1 = reconstruction_pointset_smoothing()
    config = Config()
    config.camera.target = [0, 5000, -10000]
    config.camera.position = [0, -10000, 30000]
    config.camera.scale = 1000
    config.renderer.gridsize = (20000, 20, 20000, 20)
    viewer = Viewer(config=config)
    viewer.scene.add(c_smoothing_0, pointcolor=(0.0, 0.0, 0.0))
    viewer.scene.add(c_smoothing_1, pointcolor=(1.0, 0.0, 0.0))
    viewer.show()
