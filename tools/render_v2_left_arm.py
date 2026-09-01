import os
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m2 = trimesh.load(v2_path, process=True)

pl2, _ = m2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
p2 = pl2.polygons_full[0]

# Left arm (x <= 0)
left_arm = p2.intersection(shapely.box(-20.0, 15.0, 0.0, 50.0))

fig, ax = plt.subplots(figsize=(8, 14))

x, y = left_arm.exterior.xy
ax.fill(x, y, color='#999999', edgecolor='black', linewidth=1.5)

for interior in left_arm.interiors:
    ix, iy = interior.xy
    ax.fill(ix, iy, color='white', edgecolor='black', linewidth=1.5)

ax.set_aspect('equal')
ax.set_facecolor('#2b2b2b')
fig.patch.set_facecolor('#2b2b2b')
ax.grid(True, color='#3d3d3d', linestyle='-', linewidth=0.5)
ax.set_title("11 - Middle Spring v2 (Left Arm)", color='white')
ax.tick_params(colors='white')

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "v2_left_arm_render.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved v2_left_arm_render.png")
