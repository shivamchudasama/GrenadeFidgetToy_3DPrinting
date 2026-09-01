import os
import sys
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v1_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring.stl")
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")

m1 = trimesh.load(v1_path, process=True)
m2 = trimesh.load(v2_path, process=True)

print("Mesh 1 (v1): bounds=", m1.bounds, "extents=", m1.extents)
print("Mesh 2 (v2): bounds=", m2.bounds, "extents=", m2.extents)

# Take sections
for name, m in [("v1", m1), ("v2", m2)]:
    pl, _ = m.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
    print(f"\n--- {name} 2D Section ---")
    print(f"Polygons count: {len(pl.polygons_full)}")
    for i, poly in enumerate(pl.polygons_full):
        print(f"Poly {i}: bounds={poly.bounds}, area={poly.area}")
        if poly.interiors:
            print(f"  Holes count: {len(poly.interiors)}")
            for j, interior in enumerate(poly.interiors):
                print(f"    Hole {j}: bounds={interior.bounds}")
