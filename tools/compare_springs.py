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

pl1, _ = m1.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
pl2, _ = m2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))

p1 = pl1.polygons_full[0]
p2 = pl2.polygons_full[0]

# Let's inspect the positive half (x >= 0)
cut_box = shapely.box(0.0, 10.0, 30.0, 60.0)
p1_half = p1.intersection(cut_box)
p2_half = p2.intersection(cut_box)

print("v1 half bounds:", p1_half.bounds)
print("v2 half bounds:", p2_half.bounds)

# Let's check difference between p1_half and p2_half
diff_1_2 = p1_half.difference(p2_half)
diff_2_1 = p2_half.difference(p1_half)

print("Area in v1 not in v2:", diff_1_2.area)
print("Area in v2 not in v1:", diff_2_1.area)

# Let's inspect coords around the spring arm and nose
# In p2_half, where is the nose?
# Let's find vertices of p2_half
coords2 = np.array(p2_half.exterior.coords)
print("v2 half coords shape:", coords2.shape)
print("v2 min x, max x:", np.min(coords2[:, 0]), np.max(coords2[:, 0]))
print("v2 min y, max y:", np.min(coords2[:, 1]), np.max(coords2[:, 1]))

# Let's find the nose apex, inner beam, outer beam in v2
# Let's print out the segments
