import os
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m2 = trimesh.load(v2_path, process=True)
pl2, _ = m2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
p2 = pl2.polygons_full[0]

# Positive X arm (right arm)
# In the original coordinate system of 11 - Middle Spring v2.stl:
# Let's inspect the bounding box of the whole part and the right arm
coords = np.array(p2.exterior.coords)

# Let's find vertices where x > 0
right_arm = p2.intersection(shapely.box(0.0, 0.0, 20.0, 60.0))

print("Right arm bounds (x_min, y_min, x_max, y_max):", right_arm.bounds)

# Let's find:
# 1. Outer rail x coordinate
# 2. Loop top y coordinate
# 3. Slender stalk x coordinates (inner and outer face of stalk)
# 4. Nose apex (x, y) coordinates and apex radius
# 5. Gap width between outer rail and stalk, and between stalk and head
# 6. Head geometry / bulb coordinates

# Let's print vertices of the right arm in order
pts = np.array(right_arm.exterior.coords)
print(f"Number of exterior points in right arm: {len(pts)}")

# Let's inspect specific features:
# Highest Y point:
top_pt_idx = np.argmax(pts[:, 1])
print(f"Top point: {pts[top_pt_idx]}")

# Lowest X point in the nose head region (y between 30 and 45):
head_pts = pts[(pts[:, 1] >= 28.0) & (pts[:, 1] <= 45.0) & (pts[:, 0] <= 10.0)]
if len(head_pts) > 0:
    min_x_head = head_pts[np.argmin(head_pts[:, 0])]
    print(f"Innermost head point (nose tip): {min_x_head}")

# Max X point (outer rail):
max_x_pt = pts[np.argmax(pts[:, 0])]
print(f"Outermost point: {max_x_pt}")

# Let's measure stalk thickness and gap widths across horizontal scanlines (y = 35, 38, 40, 42, 44)
for y_scan in [25.0, 30.0, 35.0, 38.0, 40.0, 42.0, 44.0, 46.0]:
    line = shapely.LineString([(-1.0, y_scan), (20.0, y_scan)])
    inter = right_arm.intersection(line)
    if inter.geom_type == 'MultiLineString':
        segments = [(seg.coords[0][0], seg.coords[-1][0]) for seg in inter.geoms]
        print(f"Scanline y={y_scan:4.1f}: segments={segments}")
    elif inter.geom_type == 'LineString' and not inter.is_empty:
        print(f"Scanline y={y_scan:4.1f}: segment=({inter.coords[0][0]:.3f}, {inter.coords[-1][0]:.3f})")
