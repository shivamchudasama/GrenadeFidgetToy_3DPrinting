import os
import sys
import trimesh
import numpy as np
import shapely
from shapely.ops import unary_union
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]

# Left arm in native coordinates (X <= 0, Y in [15.375, 48.000])
left_arm = poly_v2.intersection(shapely.box(-30.0, 15.375, 0.0, 55.0))
coords = np.array(left_arm.exterior.coords)
# Mirror X -> positive radius R
coords_mir = np.column_stack([-coords[:, 0], coords[:, 1]])
ref_arm_full = shapely.Polygon(coords_mir)

# Let's inspect the entire polygon bounds:
print("Full v2 Arm Bounds (R, Y):", ref_arm_full.bounds)

# In ref_arm_full:
# R in [0.0, 14.4509], Y in [15.375, 48.000]
# Below y = 19.60 is the bridge connector to the other arm (R from 0 to 7.384)
# When cut at the bridge (R >= 7.384 or Y >= 19.60):
ref_arm_cut = ref_arm_full.difference(shapely.box(-10.0, -10.0, 30.0, 19.60))
if ref_arm_cut.geom_type == 'MultiPolygon':
    ref_arm_cut = max(ref_arm_cut.geoms, key=lambda q: q.area)

print("Cut v2 Arm Bounds (R, Y):", ref_arm_cut.bounds)

# Let's directly map the ENTIRE cut v2 arm:
# 1. Axial:
# Map Y from [19.60, 48.00] to [36.00, 62.92] in toy coordinates:
# toy_y = 36.00 + (y - 19.60) * ((62.92 - 36.00) / (48.00 - 19.60))
# s_y = (62.92 - 36.00) / (48.00 - 19.60) = 26.92 / 28.40 = 0.947887
# Nose in v2 is at y = 40.5404 -> toy_y = 36.00 + (40.5404 - 19.60) * 0.947887 = 55.85 mm
# To place nose at exact tooth position y = 57.407 mm:
# Let's solve: toy_y(19.60) = 36.00, toy_y(40.5404) = 57.407, toy_y(48.00) = 62.92
# Using a smooth piecewise affine or linear mapping:
def map_axial(y):
    # From y = 19.60 to 40.5404: maps to [36.00, 57.407] -> s1 = (57.407 - 36.00) / (40.5404 - 19.60) = 21.407 / 20.9404 = 1.02228
    # From y = 40.5404 to 48.00: maps to [57.407, 62.920] -> s2 = (62.920 - 57.407) / (48.00 - 40.5404) = 5.513 / 7.4596 = 0.73905
    if y <= 40.5404:
        return 36.00 + (y - 19.60) * 1.02228
    else:
        return 57.407 + (y - 40.5404) * 0.73905

# 2. Radial:
# Continuous mapping of R from v2 space [5.8532, 14.4509] to toy space [5.54, 12.20]:
# Features in v2:
# Nose apex: 5.8532 -> 5.54
# Flank: 7.1240 -> 7.00
# Shaft inner face at base: 7.384 -> 7.40
# Descending beam inner: 8.6509 -> 7.60
# Descending beam outer: 9.4509 -> 8.35
# Ascending beam inner: 10.4509 -> 8.90
# Ascending beam outer: 11.2509 -> 9.65
# Outer spine inner: 12.6509 -> 10.25
# Outer spine outer (upper): 14.4509 -> 10.90
# Outer spine at base (y=19.60): 9.950 -> 12.20 (at foot)

# Let's map every point (R, Y) of the pristine v2 profile
def map_v2_point_pure(p):
    r, y = p[0], p[1]
    toy_y = map_axial(y)
    
    # Smooth continuous radial interpolation
    # At upper loop (y > 35.0):
    x_src_up = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst_up = np.array([5.5400, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, 10.9000])
    
    # At lower base (y < 25.0):
    x_src_lo = np.array([7.384, 9.950])
    r_dst_lo = np.array([7.400, 12.200])
    
    t = float(np.clip((y - 25.0) / 10.0, 0.0, 1.0))
    
    r_up = float(np.interp(r, x_src_up, r_dst_up))
    # For lower interpolation:
    r_lo = float(np.interp(r, x_src_lo, r_dst_lo))
    
    toy_r = (1.0 - t) * r_lo + t * r_up
    return (toy_y, toy_r)

mapped_pts = [map_v2_point_pure(c) for c in ref_arm_cut.exterior.coords]
pure_poly = shapely.Polygon(mapped_pts)

print("Pure Mapped v2 Poly Bounds (Y, R):", pure_poly.bounds)

# Plot pure mapped v2 profile
fig, axes = plt.subplots(1, 2, figsize=(12, 14))

# 1. Native v2 left arm
axes[0].plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2)
axes[0].fill(coords[:, 0], coords[:, 1], color='#999999', alpha=0.9)
axes[0].set_aspect('equal')
axes[0].grid(True, color='#444444')
axes[0].set_facecolor('#222222')
axes[0].set_title("11 - Middle Spring v2 Native (Reference)", color='white')
axes[0].tick_params(colors='white')

# 2. Pure Mapped Spring (-R vs Toy Y)
py, pr = pure_poly.exterior.xy
axes[1].plot([-r for r in pr], py, color='#22cc66', linewidth=2)
axes[1].fill([-r for r in pr], py, color='#999999', alpha=0.9)
axes[1].set_aspect('equal')
axes[1].grid(True, color='#444444')
axes[1].set_facecolor('#222222')
axes[1].set_title("Pure Mapped Spring (100% Curvy & Organic)", color='white')
axes[1].tick_params(colors='white')

fig.patch.set_facecolor('#181818')
plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "pure_v2_mapped_comparison.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved pure_v2_mapped_comparison.png")
