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

# Left arm in native v2 coordinates
# Let's inspect the entire left arm of v2 without any arbitrary cuts
left_arm = poly_v2.intersection(shapely.box(-30.0, 15.0, 0.0, 55.0))
coords = np.array(left_arm.exterior.coords)

# Plot the pristine v2 left arm
fig, ax = plt.subplots(figsize=(6, 14))
ax.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2)
ax.fill(coords[:, 0], coords[:, 1], color='#999999', alpha=0.9)
ax.set_aspect('equal')
ax.grid(True, color='#444444')
ax.set_facecolor('#222222')
fig.patch.set_facecolor('#181818')
ax.set_title("Pristine 11 - Middle Spring v2 (Left Arm)", color='white')
ax.tick_params(colors='white')

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "pristine_v2_arm_full.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved pristine_v2_arm_full.png")
