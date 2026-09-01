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

def build_perfect_smooth_v2_profile(r_nose=BRD.NOSE_APEX, s_y=BRD.ARM_SCALE_Y, arm_y0=BRD.ARM_Y0, arm_r_out=BRD.ARM_R_OUT):
    # In ref_arm:
    # x in [5.8532, 14.4509], y in [19.60, 48.00]
    # Let's inspect the upper flexure loop (y >= 35.0) and lower waist (y < 35.0)
    
    # 1. Map the upper flexure loop and head (y >= 35.0)
    # Target radii for upper features:
    # Nose apex: r_nose = 5.54
    # Flank: 7.00
    # Descending beam inner: 7.60, outer: 8.35 (beam = 0.75 mm)
    # Inner loop gap: 8.35 to 8.90 (gap = 0.55 mm)
    # Ascending beam inner: 8.90, outer: 9.65 (beam = 0.75 mm)
    # Outer slot gap: 9.65 to 10.25 (gap = 0.60 mm)
    # Outer spine: 10.25 to arm_r_out (10.90) (spine = 0.65 to 1.05 mm)
    
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([r_nose, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, arm_r_out])

    def map_upper(c):
        x, y = c[0], c[1]
        toy_y = arm_y0 + (y - 19.60) * s_y
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    # Let's map the upper loop directly (y >= 35.0 in v2 coords -> toy_y >= 53.3 mm)
    upper_part = ref_arm.intersection(shapely.box(0.0, 35.0, 20.0, 55.0))
    mapped_upper = shapely.Polygon([map_upper(c) for c in upper_part.exterior.coords])

    # 2. Lower Body & Foot (toy_y from 36.00 to 54.00):
    # We construct a single, perfectly smooth, continuous solid body:
    # - Inner face: perfectly smooth curve from (36.00, 7.400) to (53.30, mapped inner stalk at 7.600)
    #   Using a C2 quintic transition from 7.400 to 7.600!
    # - Outer face: perfectly smooth curve from (36.00, 12.200) -> (42.60, 12.200) -> smooth C2 transition to (54.50, 10.900)
    #   Connecting directly with the outer spine of mapped_upper at r=10.900!
    # - Bottom face: flat at y = 36.00 from r = 7.400 to r = 12.200 (foot base)

    # Inner curve (toy_y in [36.00, 53.50]):
    y_inner = np.linspace(36.00, 53.50, 40)
    # Stays straight at 7.400 from 36.00 to 44.00, then smoothly transitions from 7.400 to 7.600 between 44.00 and 53.50
    u_in = np.clip((y_inner - 44.00) / (53.50 - 44.00), 0.0, 1.0)
    s_in = 6.0 * u_in**5 - 15.0 * u_in**4 + 10.0 * u_in**3
    r_inner = 7.400 + (7.600 - 7.400) * s_in

    # Outer curve (toy_y in [36.00, 55.00]):
    # Foot bearing face: r = 12.200 from y = 36.00 to y = 42.60
    # Smooth transition from 12.200 down to 10.900 from y = 42.60 to y = 54.50
    y_outer = np.linspace(42.60, 54.50, 40)
    u_out = (y_outer - 42.60) / (54.50 - 42.60)
    s_out = 6.0 * u_out**5 - 15.0 * u_out**4 + 10.0 * u_out**3
    r_outer = 12.200 - (12.200 - arm_r_out) * s_out

    # Construct lower body polygon
    pts_lower = [
        (36.00, 7.400),
        (36.00, 12.200),
        (42.60, 12.200),
    ]
    for y_p, r_p in zip(y_outer[1:], r_outer[1:]):
        pts_lower.append((y_p, r_p))
    pts_lower.append((54.50, 10.250)) # blend with inner face of outer spine
    pts_lower.append((54.00, 9.650))  # blend across slot bottom
    pts_lower.append((53.50, 7.600))  # connect to inner stalk
    
    for y_p, r_p in reversed(list(zip(y_inner, r_inner))):
        pts_lower.append((y_p, r_p))
    
    poly_lower = shapely.Polygon(pts_lower)

    merged = unary_union([mapped_upper, poly_lower])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)

    return shapely.Polygon(merged.exterior)

p_perfect = build_perfect_smooth_v2_profile()

fig, ax = plt.subplots(figsize=(6, 14))
py, pr = p_perfect.exterior.xy
ax.plot([-r for r in pr], py, 'g-', linewidth=2)
ax.fill([-r for r in pr], py, color='#bbddcc', alpha=0.8)

ax.set_aspect('equal')
ax.grid(True)
ax.set_title("Refined Spring Profile (-R vs Y)")
ax.set_xlabel("-R (Outer spine on Left, Inner on Right)")
ax.set_ylabel("Toy Y (Axial)")

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "perfect_smooth_spring.png"), dpi=200)
print("Saved perfect_smooth_spring.png")
