import numpy as np
from compas.geometry import Polyline
from compas_viewer import Viewer
from compas_viewer.config import Config

from compas_cgal.polylines import simplify_polyline


# Create a complex polyline: spiral with noise
n_points = 200
t = np.linspace(0, 6 * np.pi, n_points)
radius = 1 + t / 10
noise = np.random.uniform(-0.05, 0.05, n_points)

x = radius * np.cos(t) + noise
y = radius * np.sin(t) + noise
z = t / 5

original_points = np.column_stack([x, y, z])

# Simplify with different thresholds
simplified_high = simplify_polyline(original_points, threshold=0.5)

# Create polylines offset in X for visualization
offset = 6.0
original_polyline = Polyline(original_points.tolist())
simplified_high_polyline = Polyline((simplified_high + [offset, 0, 0]).tolist())

# ==============================================================================
# Visualize
# ==============================================================================

config = Config()
config.camera.target = [5, 0, 5]
config.camera.position = [5, -20, 10]

viewer = Viewer(config=config)

viewer.scene.add(original_polyline, linewidth=2, show_points=False)
viewer.scene.add(simplified_high_polyline, linewidth=3, show_points=False)

viewer.show()
