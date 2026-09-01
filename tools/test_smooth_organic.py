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

def build_smooth_organic_profile():
    # 1. Map v2 geometry
    # v2 source features: nose(5.8532), flank(7.1240), desc_in(8.6509), desc_out(9.4509), asc_in(10.4509), asc_out(11.2509), spine_in(12.6509), spine_out(14.4509)
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([BRD.NOSE_APEX, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, BRD.ARM_R_OUT])

    def map_c(c):
        x, y = c[0], c[1]
        toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped = shapely.Polygon([map_c(c) for c in ref_arm.exterior.coords])

    # 2. Smooth transition on the outer spine from y=42.60 (foot top at r=12.20) to y=54.0 (r=10.90)
    # Using a quintic smoothstep (C2 continuous: zero velocity & acceleration at both endpoints)
    # y in [42.60, 52.00]
    y_trans = np.linspace(42.60, 52.00, 30)
    u = (y_trans - 42.60) / (52.00 - 42.60)
    s_curve = 6.0 * u**5 - 15.0 * u**4 + 10.0 * u**3
    r_outer_smooth = 12.20 - (12.20 - 10.90) * s_curve

    # Foot block with smooth organic outer blend
    pts_foot = [
        (BRD.FOOT_Y0, BRD.LEAF_R0),
        (BRD.FOOT_Y0, BRD.RAIL_R1),
        (42.60, BRD.RAIL_R1),
    ]
    for y_p, r_p in zip(y_trans[1:], r_outer_smooth[1:]):
        pts_foot.append((y_p, r_p))
    pts_foot += [
        (52.00, 8.50),
        (42.60, 7.40),
        (BRD.FOOT_Y0, BRD.LEAF_R0)
    ]
    foot_poly = shapely.Polygon(pts_foot)

    merged = unary_union([mapped, foot_poly])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)

    # Ensure inner bore face below foot_y1 is flush at r >= 7.40
    merged = merged.difference(shapely.box(0.0, 0.0, 42.60, BRD.LEAF_R0))
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)

    return shapely.Polygon(merged.exterior)

p_organic = build_smooth_organic_profile()

fig, ax = plt.subplots(figsize=(6, 14))

py, pr = p_organic.exterior.xy
ax.plot([-r for r in pr], py, 'b-', linewidth=2)
ax.fill([-r for r in pr], py, color='#bbccdd', alpha=0.6)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title("Smooth Organic Spine Profile (-R vs Y)")
ax.set_xlabel("-R (Outer spine on left)")
ax.set_ylabel("Toy Y (Axial)")

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "smooth_organic_spine.png"), dpi=200)
print("Saved smooth_organic_spine.png")
