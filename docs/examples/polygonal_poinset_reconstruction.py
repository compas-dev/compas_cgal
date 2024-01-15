from pathlib import Path
from compas.geometry import Pointcloud, Point, Line, Polygon
from compas_view2.app import App
from compas_view2.collections import Collection
from compas.colors import Color
from compas_cgal.reconstruction import pointset_normal_estimation
from compas_cgal.polygonal_surface_reconstruction import (
    polygonal_surface_reconstruction_ransac,
)

# Define the file path for the point cloud data
FILE = Path(__file__).parent.parent.parent / "data" / "two_intersecting_boxes.ply"

# Load the point cloud data from the PLY file
cloud = Pointcloud.from_ply(FILE)

# Estimate normals for the point cloud
points, vectors = pointset_normal_estimation(cloud, 4, True)
vertices, faces = polygonal_surface_reconstruction_ransac(points, vectors)

# Create polygons from vertices and faces
polygons = []
for face in faces:
    polygon = []
    for i in face:
        polygon.append(Point(*vertices[i]))
    polygons.append(Polygon(polygon))


# Create lines and properties for visualizing normals
lines = []
line_properties = []
line_scale = 25

# Iterate over points and vectors to create lines and color properties
for p, v in zip(points, vectors):
    # Create lines
    lines.append(
        Line(
            Point(p[0], p[1], p[2]),
            Point(
                p[0] + v[0] * line_scale,
                p[1] + v[1] * line_scale,
                p[2] + v[2] * line_scale,
            ),
        )
    )

    # Normalize vector components to be in the range [0, 1] for color representation
    r = (v[0] + 1) * 0.5
    g = (v[1] + 1) * 0.5
    b = (v[2] + 1) * 0.5

    # Store line color properties
    line_properties.append({"linecolor": Color(r, g, b)})

# Create a viewer
viewer = App(width=1600, height=900)
viewer.view.camera.position = [5, -4, 2]
viewer.view.camera.look_at([0, 1, 0])
viewer.add(Pointcloud(points))
line_collection = Collection(lines, line_properties)
# Uncomment to see the normals:
# viewer.add(line_collection)
for polygon in polygons:
    viewer.add(polygon, linewidth=2)
viewer.run()
