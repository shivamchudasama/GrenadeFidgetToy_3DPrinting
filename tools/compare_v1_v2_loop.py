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

p1 = pl1.polygons_full[0].intersection(shapely.box(0, 15, 25, 55))
p2 = pl2.polygons_full[0].intersection(shapely.box(0, 15, 25, 55))

print("v1 area:", p1.area)
print("v2 area:", p2.area)

# Let's inspect the U-loop and nose region in v1 vs v2
print("\n--- Comparing loop top ---")
pts1 = np.array(p1.exterior.coords)
pts2 = np.array(p2.exterior.coords)

# Top Y in v1:
print("v1 top pt:", pts1[np.argmax(pts1[:, 1])])
print("v2 top pt:", pts2[np.argmax(pts2[:, 1])])

# Nose tip in v1:
head1 = pts1[(pts1[:, 1] >= 35.0) & (pts1[:, 1] <= 45.0) & (pts1[:, 0] <= 10.0)]
head2 = pts2[(pts2[:, 1] >= 35.0) & (pts2[:, 1] <= 45.0) & (pts2[:, 0] <= 10.0)]

print("v1 nose tip:", head1[np.argmin(head1[:, 0])])
print("v2 nose tip:", head2[np.argmin(head2[:, 0])])
