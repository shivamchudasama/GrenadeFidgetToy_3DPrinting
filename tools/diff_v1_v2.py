import os
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v1_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring.stl")
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")

m1 = trimesh.load(v1_path, process=True)
m2 = trimesh.load(v2_path, process=True)

pl1, _ = m1.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
pl2, _ = m2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))

p1 = pl1.polygons_full[0]
p2 = pl2.polygons_full[0]

# Let's inspect differences on the right side
box = shapely.box(0, 0, 30, 60)
p1_r = p1.intersection(box)
p2_r = p2.intersection(box)

print("v1 right side bounds:", p1_r.bounds)
print("v2 right side bounds:", p2_r.bounds)

# What are the differences?
diff1 = p1_r.difference(p2_r)
diff2 = p2_r.difference(p1_r)

print(f"v1 - v2 area: {diff1.area:.3f} mm2, bounds: {diff1.bounds}")
print(f"v2 - v1 area: {diff2.area:.3f} mm2, bounds: {diff2.bounds}")
