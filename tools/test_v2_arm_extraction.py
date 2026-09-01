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

v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]

# Left arm (x <= 0) - outer spine at x = -14.4509, nose at x = -5.8532, y = 40.5404, top at y = 48.000
# If we mirror X -> -X: outer spine at x = +14.4509, nose at x = +5.8532, y = 40.5404, top at y = 48.000
poly_left = poly_v2.intersection(shapely.box(-25.0, 15.0, 0.0, 55.0))
# Let's mirror left arm so X is positive (radius) and Y is axial
coords = np.array(poly_left.exterior.coords)
coords_mirrored = np.column_stack([-coords[:, 0], coords[:, 1]])
poly_arm = shapely.Polygon(coords_mirrored)

print("Original v2 Arm bounds (R, Y):", poly_arm.bounds)
# In poly_arm:
# X (Radius): 0.0 to 14.4509
# Y (Axial): 15.375 to 48.000
# Nose apex in poly_arm:
nose_idx = np.argmin(coords_mirrored[(coords_mirrored[:, 1] > 35) & (coords_mirrored[:, 1] < 45)][:, 0])
nose_pts = coords_mirrored[(coords_mirrored[:, 1] > 35) & (coords_mirrored[:, 1] < 45)]
nose_apex = nose_pts[np.argmin(nose_pts[:, 0])]
print(f"Nose apex in v2: R = {nose_apex[0]:.4f}, Y = {nose_apex[1]:.4f}")

# Loop top in poly_arm:
loop_top = np.max(coords_mirrored[:, 1])
print(f"Loop top in v2: Y = {loop_top:.4f}")

# Let's inspect the exact shape of the upper flexure loop and head (Y >= 33.0):
# Cut off bridge below y = 19.60
poly_arm_trimmed = poly_arm.difference(shapely.box(-10.0, -10.0, 30.0, 19.60))
if poly_arm_trimmed.geom_type == 'MultiPolygon':
    poly_arm_trimmed = max(poly_arm_trimmed.geoms, key=lambda q: q.area)

print(f"Trimmed Arm bounds: {poly_arm_trimmed.bounds}, area: {poly_arm_trimmed.area:.3f} mm2")
