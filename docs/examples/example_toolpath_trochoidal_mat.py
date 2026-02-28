from compas.colors import Color
from compas.geometry import Arc
from compas.geometry import Circle
from compas.geometry import Line
from compas.geometry import Polygon
from compas.geometry import Polyline
from compas.scene import get_sceneobject_cls
from compas.scene import register
from compas.scene.exceptions import SceneObjectNotRegisteredError
from compas_viewer import Viewer
from compas_viewer.scene.geometryobject import GeometryObject

from compas_cgal.toolpath import trochoidal_mat_toolpath_circular

polygon = Polygon(
    [
        (-1.91, 3.59, 0.0),
        (-5.53, -5.22, 0.0),
        (-0.39, -1.98, 0.0),
        (2.98, -5.51, 0.0),
        (4.83, -2.02, 0.0),
        (9.70, -3.63, 0.0),
        (12.23, 1.25, 0.0),
        (3.42, 0.66, 0.0),
        (2.92, 4.03, 0.0),
    ]
)

operations = trochoidal_mat_toolpath_circular(
    polygon,
    tool_diameter=1.0,
    stepover=0.5,
    pitch=0.75,
    mat_scale=1.0,
    lead_in=0.15,
    lead_out=0.15,
    link_paths=True,
    optimize_order=True,
    cut_z=-0.2,
    clearance_z=2.0,
    merge_circles=False,
)


class ArcObject(GeometryObject):
    geometry: Arc

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_lines = True

    @property
    def lines(self):
        return self.geometry.to_polyline(n=self.u).lines


def ensure_viewer_arc_registered():
    try:
        get_sceneobject_cls(Arc, context="Viewer")
    except SceneObjectNotRegisteredError:
        register(Arc, ArcObject, context="Viewer")


def add_curve_compatible(scene, curve, **kwargs):
    try:
        scene.add(curve, **kwargs)
    except SceneObjectNotRegisteredError:
        if isinstance(curve, Line):
            scene.add(Polyline([curve.start, curve.end]), **kwargs)
        elif isinstance(curve, Arc):
            scene.add(curve.to_polyline(n=64), **kwargs)
        elif isinstance(curve, Circle):
            scene.add(curve.to_polyline(n=64), **kwargs)


# ==============================================================================
# Visualize
# ==============================================================================

ensure_viewer_arc_registered()

viewer = Viewer()
viewer.config.renderer.show_grid = False

viewer.scene.add(polygon, show_faces=False, linecolor=Color.black())

operation_styles = {
    "cut": {
        "default": (Color.from_rgb255(220, 120, 30), 2.0, None),
        Circle: (Color.from_rgb255(210, 40, 150), 2.8, "circle"),
        Arc: (Color.from_rgb255(230, 70, 40), 2.2, "arc"),
    },
    "link": (Color.from_rgb255(60, 90, 220), 1.5),
    "lead_in": (Color.from_rgb255(20, 170, 80), 2.0),
    "retract": (Color.from_rgb255(20, 120, 220), 2.0),
    "plunge": (Color.from_rgb255(40, 180, 220), 2.0),
    "default": (Color.from_rgb255(200, 140, 20), 2.0),
}

cut_counts = {"circle": 0, "arc": 0}

for op in operations:
    curve = op.geometry

    if op.operation == "cut":
        cut_style = operation_styles["cut"]
        color, width, kind = cut_style["default"]
        for geometry_type, style in cut_style.items():
            if geometry_type == "default":
                continue
            if isinstance(curve, geometry_type):
                color, width, kind = style
                break
        if kind:
            cut_counts[kind] += 1
    else:
        color, width = operation_styles.get(op.operation, operation_styles["default"])

    add_curve_compatible(viewer.scene, curve, linecolor=color, linewidth=width)

print("Cut primitive counts -> circles: {}, arcs: {}".format(cut_counts["circle"], cut_counts["arc"]))

viewer.show()
