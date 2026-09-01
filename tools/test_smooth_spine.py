import os
import sys
import trimesh
import numpy as np
import shapely
from shapely.ops import unary_union
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

import build_rod_detent as BRD

v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]

left_part = poly_v2.intersection(shapely.box(-30.0, 15.0, 0.0, 55.0))
coords = np.array(left_part.exterior.coords)
coords_mirrored = np.column_stack([-coords[:, 0], coords[:, 1]])
ref_arm = shapely.Polygon(coords_mirrored).difference(shapely.box(-10.0, -10.0, 30.0, 19.60))
if ref_arm.geom_type == 'MultiPolygon':
    ref_arm = max(ref_arm.geoms, key=lambda q: q.area)

def build_smooth_v2_single_profile(r_nose=BRD.NOSE_APEX, s_y=BRD.ARM_SCALE_Y, arm_y0=BRD.ARM_Y0, arm_r_out=BRD.ARM_R_OUT):
    # Mapping v2 coordinates
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([r_nose, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, arm_r_out])

    def map_c(c):
        x, y = c[0], c[1]
        toy_y = arm_y0 + (y - 19.60) * s_y
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped = shapely.Polygon([map_c(c) for c in ref_arm.exterior.coords])

    # Foot anchor:
    # We want the foot block at y in [36.00, 42.60], r in [7.40, 12.20].
    # Instead of an arbitrary box cutting in at r = 9.851 up to y = 47.0,
    # the foot block is strictly at y in [36.00, 42.60], r in [7.40, 12.20].
    # Above y = 42.60, the outer spine follows the pristine smooth v2 curve!
    foot_y1 = arm_y0 + BRD.FOOT_OVERLAP # 42.60 mm
    
    # We create a clean foot block from y = 36.00 to y = foot_y1
    # with a smooth fillet / bevel from (foot_y1, 12.20) to (foot_y1 + 1.50, r_spine at that height)
    # Let's find r_spine at foot_y1 from mapped geometry:
    # At foot_y1 = 42.60: mapped exterior on outer spine
    
    foot_poly = shapely.Polygon([
        (BRD.FOOT_Y0, BRD.LEAF_R0),
        (BRD.FOOT_Y0, BRD.RAIL_R1),
        (foot_y1, BRD.RAIL_R1),
        (foot_y1, BRD.LEAF_R0),
        (BRD.FOOT_Y0, BRD.LEAF_R0)
    ])

    merged = unary_union([mapped, foot_poly])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)

    # Ensure inner bore face below foot_y1 is flush at r >= 7.40
    merged = merged.difference(shapely.box(0.0, 0.0, foot_y1, BRD.LEAF_R0))
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)

    return shapely.Polygon(merged.exterior)

poly_old = build_smooth_v2_single_profile() # let's check

# Let's plot old vs new smooth version
fig, axes = plt.subplots(1, 2, figsize=(12, 14))

# 1. Old profile (with notch)
import build_dual_headed_springs as BDHS
p_old = BDHS.build_v2_single_profile()
py_o, pr_o = p_old.exterior.xy
axes[0].plot([-r for r in pr_o], py_o, 'r-', linewidth=2)
axes[0].fill([-r for r in pr_o], py_o, color='#aaaaaa', alpha=0.5)
axes[0].set_aspect('equal')
axes[0].grid(True)
axes[0].set_title("Previous (With Irregularity Notch)")
axes[0].set_xlabel("-R (Outer spine on left)")
axes[0].set_ylabel("Toy Y (Axial)")

# 2. Smooth profile
p_smooth = build_smooth_v2_single_profile()
py_s, pr_s = p_smooth.exterior.xy
axes[1].plot([-r for r in pr_s], py_s, 'g-', linewidth=2)
axes[1].fill([-r for r in pr_s], py_s, color='#aaccbb', alpha=0.5)
axes[1].set_aspect('equal')
axes[1].grid(True)
axes[1].set_title("New (Smooth Continuous Curve)")
axes[1].set_xlabel("-R (Outer spine on left)")
axes[1].set_ylabel("Toy Y (Axial)")

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "compare_smooth_spine.png"), dpi=200)
print("Saved compare_smooth_spine.png")
