import os
import sys
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]
left_v2 = poly_v2.intersection(shapely.box(-30.0, 15.375, 0.0, 55.0))

print("=== Native v2 Left Arm Inner Face Scan ===")
for y_test in [19.6, 22.0, 25.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0]:
    line = shapely.LineString([(-20.0, y_test), (0.0, y_test)])
    inter = left_v2.intersection(line)
    if not inter.is_empty:
        if inter.geom_type == 'LineString':
            print(f"  y = {y_test:4.1f} mm: inner x = {-inter.coords[-1][0]:.3f} mm, outer x = {-inter.coords[0][0]:.3f} mm")
        elif inter.geom_type == 'MultiLineString':
            inner_seg = inter.geoms[-1]
            print(f"  y = {y_test:4.1f} mm: inner x = {-inner_seg.coords[-1][0]:.3f} mm, outer x = {-inter.geoms[0].coords[0][0]:.3f} mm")
