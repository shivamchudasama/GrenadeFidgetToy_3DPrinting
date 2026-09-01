import os
import sys
import trimesh
import numpy as np
import shapely
from shapely.ops import unary_union
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))
import flexure_rate as FR
import build_rod_detent as BRD

v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]

# Left arm mirrored to positive X
poly_left = poly_v2.intersection(shapely.box(-25.0, 15.0, 0.0, 55.0))
coords = np.array(poly_left.exterior.coords)
coords_mirrored = np.column_stack([-coords[:, 0], coords[:, 1]])
ref_v2 = shapely.Polygon(coords_mirrored).difference(shapely.box(-10.0, -10.0, 30.0, 19.60))
if ref_v2.geom_type == 'MultiPolygon':
    ref_v2 = max(ref_v2.geoms, key=lambda q: q.area)

def build_v2_spring_profile(r_nose=5.54, s_y=0.74, arm_y0=41.90, arm_r_out=10.90):
    # Precise radial anchors preserving v2 geometry with print-safe 0.75-0.80mm walls & 0.55mm gaps
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([r_nose, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, arm_r_out])

    def map_c(c):
        x, y = c[0], c[1]
        toy_y = arm_y0 + (y - 19.60) * s_y
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped = shapely.Polygon([map_c(c) for c in ref_v2.exterior.coords])
    
    # Add the rigid foot at y in [36.00, 42.60], r in [7.40, 12.20]
    foot_y1 = arm_y0 + 0.70
    foot_poly = shapely.Polygon([
        (36.00, 7.40),
        (36.00, 12.20),
        (foot_y1, 12.20),
        (foot_y1, 9.851),
        (47.00, 9.851),
        (47.00, 7.40),
        (36.00, 7.40)
    ])
    
    # Merge mapped body with foot
    merged = unary_union([mapped, foot_poly])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
    
    # Clip inner bore face below foot_y1 to r >= 7.40
    merged = merged.difference(shapely.box(0.0, 0.0, foot_y1, 7.40))
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
        
    return shapely.Polygon(merged.exterior)

poly_single = build_v2_spring_profile()

print(f"Single Spring Polygon Bounds (Y_toy, R): {poly_single.bounds}, Area: {poly_single.area:.3f} mm2")

# Calculate FE Rate
res = FR.rate(poly_single, thickness=3.00,
              fixed=lambda V: (V[:, 0] < 43.0) & (V[:, 1] > 11.0),
              loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] < 60.0),
              direction=(0.0, 1.0), h=0.06)

print("\n--- Finite Element Flexure Analysis (Single Spring) ---")
print(f"Spring Rate k: {res.k:.4f} N/mm")
print(f"Strain per mm: {res.strain_per_mm * 100:.3f} %/mm")
print(f"Max displacement at nose: {res.u_tip:.4f} mm")

# Calculate click forces for 4 springs on the rod rack:
# Deflection delta = R_crest (6.8901) - R_apex (5.54) = 1.350 mm
# Peak radial force per spring: F_rad_peak = k * delta = res.k * 1.350 N
# Axial force conversion on 40.63 deg flank (flank angle theta = 40.63 deg, friction mu ~ 0.15):
# F_axial ~ F_rad * (tan(theta) + mu) / (1 - mu*tan(theta))
theta = np.radians(40.63)
mu = 0.15
f_rad_peak_1 = res.k * (6.8901 - 5.54)
f_ax_peak_1 = f_rad_peak_1 * (np.tan(theta) + mu) / (1.0 - mu * np.tan(theta))
f_ax_peak_4 = 4.0 * f_ax_peak_1

print(f"\nRadial peak force (1 spring): {f_rad_peak_1:.3f} N")
print(f"Axial peak force (1 spring):   {f_ax_peak_1:.3f} N")
print(f"Total Axial Detent Force (4 springs): {f_ax_peak_4:.3f} N")
