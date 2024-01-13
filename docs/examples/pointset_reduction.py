from pathlib import Path
from compas.geometry import Pointcloud, Translation
from compas_view2.app import App
from compas_cgal.reconstruction import pointset_reduction

# Define the file path for the point cloud data
FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"

# Load the original point cloud
original_points = Pointcloud.from_ply(FILE)

# Create a copy of the point cloud for processing
cloud = Pointcloud.from_ply(FILE)

# Translate the original point cloud
cloud.transform(Translation.from_vector([-1000, 0, 0]))

# Apply point set reduction to the translated point cloud
points = pointset_reduction(cloud, 50)
print(f"Original points: {len(cloud)}, Reduced points: {len(points)}")

# Initialize the COMPAS viewer
viewer = App(width=1600, height=900)

# Adjust viewer settings
viewer.view.camera.scale = 1000
viewer.view.grid.cell_size = 1000

# Add the reduced point cloud and the original point cloud to the viewer
viewer.add(Pointcloud(points))
viewer.add(Pointcloud(original_points))

# Set the camera to zoom to fit all points
viewer.view.camera.zoom_extents()

# Run the viewer
viewer.run()
