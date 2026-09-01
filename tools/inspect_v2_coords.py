import os
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m2 = trimesh.load(v2_path, process=True)

pl2, _ = m2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
p2 = pl2.polygons_full[0]

# Left arm (x <= 0) - matches the orientation in the user's screenshot where outer spine is on the left
left_arm = p2.intersection(shapely.box(-25.0, 15.0, 0.0, 55.0))
# Right arm (x >= 0)
right_arm = p2.intersection(shapely.box(0.0, 15.0, 25.0, 55.0))

print("Left arm bounds:", left_arm.bounds)
print("Right arm bounds:", right_arm.bounds)

# Let's inspect the right arm (mirrored or unmirrored)
# Let's see all points of right arm exterior
coords = np.array(right_arm.exterior.coords)

# Let's analyze the profile sections of the right arm:
# 1. Base / bridge cut (y ~ 15.375 to 20)
# 2. Lower stem (y ~ 20 to 33)
# 3. Flare to outer rail (y ~ 33 to 48)
# 4. Outer rail (x ~ 14.45)
# 5. Top U-bend of outer rail / top cap (y ~ 48, x ~ 10.8 to 14.45)
# 6. Slot between outer rail and stalk
# 7. Stalk going up from y ~ 34.5 to y ~ 46.5
# 8. Stalk U-bend at top (y ~ 46.5)
# 9. Stalk descending to head (y ~ 46.5 down to 42)
# 10. Head bulb and nose apex (y ~ 40.5, x ~ 5.85)

print("\n--- Key Geometric Features of 11 - Middle Spring v2 (Right Arm) ---")
# Let's find slot bottom:
# The slot is between stalk and outer rail
# Let's find local minima of y on the inner cutout boundary
print("Exterior point count:", len(coords))

# Print sorted points around the U-loop and nose
for idx, (x, y) in enumerate(coords):
    if y > 35.0:
        print(f"[{idx:3d}] x={x:8.4f}, y={y:8.4f}")
