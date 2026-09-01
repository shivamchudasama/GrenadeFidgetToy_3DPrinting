import os
import sys
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stl_path = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap", "12_Custom_Rod_Detent_Spring_01.stl")
m = trimesh.load(stl_path, process=True)
pl, _ = m.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly = pl.polygons_full[0]

coords = np.array(poly.exterior.coords)

# In poly coords, x is radial (negative), y is axial
# Let's inspect points in Box 1: Outer edge (x < -9.5), y between 48 and 58
box1_pts = coords[(coords[:, 0] < -9.5) & (coords[:, 1] >= 48.0) & (coords[:, 1] <= 58.0)]
box1_pts = box1_pts[np.argsort(box1_pts[:, 1])]

print("=== BOX 1 (Outer edge around Y=48..58) ===")
for x, y in box1_pts:
    print(f"  Y = {y:7.3f}, X (radial) = {x:7.3f}")

# Let's inspect points in Box 2: Inner edge (x > -8.5), y between 36 and 48
box2_pts = coords[(coords[:, 0] > -8.5) & (coords[:, 1] >= 36.0) & (coords[:, 1] <= 48.0)]
box2_pts = box2_pts[np.argsort(box2_pts[:, 1])]

print("\n=== BOX 2 (Inner edge around Y=36..48) ===")
for x, y in box2_pts:
    print(f"  Y = {y:7.3f}, X (radial) = {x:7.3f}")
