import os
import sys
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

from test_pure_v2_mapping import ref_arm_cut, map_axial

# In ref_arm_cut, let's inspect the points on the inner face (right edge in screenshot)
# In (R, Y) space:
# Right edge has smaller R (or in screenshot, inner face is at R ~ 7.4 to 8.6)
# Note: In our plot:
# -R is on the horizontal axis (so larger R is on the Left, smaller R is on the Right)
# The inner face is the right-hand boundary of the spring!
# Let's inspect the right-hand boundary points for Y between 42.0 and 56.0

v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]
left_v2 = poly_v2.intersection(shapely.box(-30.0, 15.375, 0.0, 55.0))
coords_v2 = np.array(left_v2.exterior.coords)
# Mirror X
coords_mir = np.column_stack([-coords_v2[:, 0], coords_v2[:, 1]])

# Let's see how the inner face in v2 looks:
# In v2 coords, for y between 25.0 and 38.0:
# Inner face has x values between 7.384 and 10.45!
# In the original v2 spring:
# At y = 25.0: x = 7.384
# At y = 30.0: x = 7.384
# At y = 35.0: x = 9.481
# At y = 38.0: x = 10.451!
# That means in v2, the inner face sweeps from x = 7.384 out to x = 10.451 (a delta of 3.067 mm!)

print("v2 inner face measurements:")
for y_test in [20.0, 25.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0]:
    line = shapely.LineString([(0.0, y_test), (20.0, y_test)])
    inter = left_v2.intersection(line)
    if not inter.is_empty:
        # In left_v2, x is negative, so inner face is max x (closest to 0)
        if inter.geom_type == 'LineString':
            print(f"  y = {y_test:4.1f} mm: inner x = {-inter.coords[-1][0]:.3f} mm, outer x = {-inter.coords[0][0]:.3f} mm")
        elif inter.geom_type == 'MultiLineString':
            inner_seg = inter.geoms[-1]
            print(f"  y = {y_test:4.1f} mm: inner x = {-inner_seg.coords[-1][0]:.3f} mm (multi)")
