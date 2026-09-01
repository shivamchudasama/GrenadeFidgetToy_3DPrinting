import os
import sys
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]

left_part = poly_v2.intersection(shapely.box(-30.0, 15.0, 0.0, 55.0))
coords = np.array(left_part.exterior.coords)
# In original v2 left part (outer spine on the left, x < 0):
# Let's inspect the outer spine coordinates (min x for each y)
print("Original v2 left part points count:", len(coords))

# Let's mirror so outer spine is at max x (or min x)
coords_mirrored = np.column_stack([-coords[:, 0], coords[:, 1]])
arm = shapely.Polygon(coords_mirrored)

# Let's plot the original v2 outer spine vs what we had in build_dual_headed_springs
import build_dual_headed_springs as BDHS
poly_single = BDHS.build_v2_single_profile()

fig, ax = plt.subplots(figsize=(8, 14))

# Plot our generated poly_single:
# poly_single coordinates are (toy_y, toy_r)
# In the user image, vertical is toy_y, horizontal is toy_r (or toy_r is horizontal, outer spine on left)
# Let's plot with Y on vertical axis, and -R on horizontal axis (so outer spine is on the left, matching user screenshot!)
py, pr = poly_single.exterior.xy
ax.plot([-r for r in pr], py, 'r-', linewidth=2, label='Current single spring profile')
ax.fill([-r for r in pr], py, color='#aaaaaa', alpha=0.5)

ax.set_aspect('equal')
ax.grid(True)
ax.set_title("Current Single Spring (-R vs Y)")
ax.set_xlabel("-R (Outer spine on left)")
ax.set_ylabel("Toy Y (Axial)")
ax.legend()

plt.savefig(os.path.join(ROOT_DIR, "tools", "inspect_outer_spine_notch.png"), dpi=200)
print("Saved inspect_outer_spine_notch.png")
