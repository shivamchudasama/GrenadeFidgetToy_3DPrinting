import os
import sys
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))
import flexure_rate as FR

v1_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring.stl")
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")

m1 = trimesh.load(v1_path, process=True)
m2 = trimesh.load(v2_path, process=True)

pl1, _ = m1.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
pl2, _ = m2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))

p1 = pl1.polygons_full[0]
p2 = pl2.polygons_full[0]

# Left arm mirrored
for name, poly in [("11 - Middle Spring (v1)", p1), ("11 - Middle Spring v2", p2)]:
    left = poly.intersection(shapely.box(-25, 15, 0, 55))
    coords = np.array(left.exterior.coords)
    coords_mir = np.column_stack([-coords[:, 0], coords[:, 1]])
    arm = shapely.Polygon(coords_mir)
    
    # In this arm frame:
    # X is radial (outer spine at ~14.45, nose at ~5.85)
    # Y is axial (bridge at ~19.6, top at ~48.0)
    # Let's fix the outer spine / bridge (x > 13.5 or y < 22) and load the nose (x < 6.5, y in [38, 42]) in X direction (radial)
    # Note: flexure_rate takes coordinates (c0, c1). direction=(1.0, 0.0) means load along coordinate 0 (X).
    res = FR.rate(arm, thickness=3.00,
                  fixed=lambda V: (V[:, 0] > 13.0) & (V[:, 1] > 35.0) | (V[:, 1] < 22.0),
                  loaded=lambda V: (V[:, 0] < 6.5) & (V[:, 1] > 38.0) & (V[:, 1] < 43.0),
                  direction=(1.0, 0.0), h=0.08)
    print(f"=== {name} ===")
    print(f"  Radial Rate k: {res.k:.4f} N/mm")
    print(f"  Strain per mm: {res.strain_per_mm * 100:.3f} %/mm")
