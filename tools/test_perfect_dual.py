import os
import sys
import numpy as np
import shapely
from shapely.ops import unary_union
import trimesh

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD
from test_perfect_smooth import build_perfect_smooth_v2_profile, ref_arm

def build_perfect_smooth_dual_profile():
    poly_single = build_perfect_smooth_v2_profile()

    # Upper flexure loop in v2 starts at y >= 35.0 in ref_arm coords
    upper_loop_ref = ref_arm.intersection(shapely.box(0.0, 35.0, 20.0, 55.0))

    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([BRD.NOSE_APEX, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, BRD.ARM_R_OUT])

    pitch_shift = 3.0 * BRD.TOOTH_PITCH  # 9.53199 mm -> upper nose at y = 66.939 mm

    def map_upper(c):
        x, y = c[0], c[1]
        toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y + pitch_shift
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped_upper = shapely.Polygon([map_upper(c) for c in upper_loop_ref.exterior.coords])

    # Solid outer spine connecting lower body to upper loop through the cap
    spine_bridge = shapely.Polygon([
        (54.00, 10.250),
        (54.00, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, 10.250),
        (54.00, 10.250)
    ])

    merged = unary_union([poly_single, mapped_upper, spine_bridge])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)

    return shapely.Polygon(merged.exterior)

p_s = build_perfect_smooth_v2_profile()
p_d = build_perfect_smooth_dual_profile()

print(f"Single Profile: Bounds={p_s.bounds}, Area={p_s.area:.3f} mm2")
print(f"Dual Profile:   Bounds={p_d.bounds}, Area={p_d.area:.3f} mm2")
