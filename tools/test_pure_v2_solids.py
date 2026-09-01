import os
import sys
import shutil
import numpy as np
import shapely
from shapely.ops import unary_union
import trimesh

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD
import flexure_rate as FR
from test_pure_v2_mapping import ref_arm_cut, map_v2_point_pure

ENGINE = "manifold"
V2_SPRING_PATH = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")

def build_pure_v2_single_profile():
    mapped_pts = [map_v2_point_pure(c) for c in ref_arm_cut.exterior.coords]
    poly = shapely.Polygon(mapped_pts)
    return shapely.Polygon(poly.exterior)

def build_pure_v2_dual_profile():
    poly_single = build_pure_v2_single_profile()
    
    # Upper flexure loop in v2 starts at y >= 33.0 in ref_arm_cut coords
    upper_loop_ref = ref_arm_cut.intersection(shapely.box(0.0, 33.0, 20.0, 55.0))
    
    pitch_shift = 3.0 * BRD.TOOTH_PITCH # 9.53199 mm
    
    x_src_up = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst_up = np.array([5.5400, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, 10.9000])

    def map_upper(c):
        r, y = c[0], c[1]
        toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y + pitch_shift
        toy_r = float(np.interp(r, x_src_up, r_dst_up))
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

ps = build_pure_v2_single_profile()
pd = build_pure_v2_dual_profile()

print(f"Single Profile: Bounds={ps.bounds}, Area={ps.area:.3f} mm2")
print(f"Dual Profile:   Bounds={pd.bounds}, Area={pd.area:.3f} mm2")

# Calculate Rate
res_s = FR.rate(ps, thickness=3.00,
                fixed=lambda V: (V[:, 0] < 42.6) & (V[:, 1] > 11.0),
                loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] < 60.0),
                direction=(0.0, 1.0), h=0.06)

print(f"Single Spring Rate: k = {res_s.k:.4f} N/mm, strain/mm = {res_s.strain_per_mm*100:.3f}%/mm")
