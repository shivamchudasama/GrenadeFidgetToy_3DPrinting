import os
import sys
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stl_path = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap", "12_Custom_Rod_Detent_Spring_01.stl")
m = trimesh.load(stl_path, process=True)
pl, _ = m.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly = pl.polygons_full[0]
coords = np.array(poly.exterior.coords)

fig, ax = plt.subplots(figsize=(6, 14))
ax.plot(coords[:, 0], coords[:, 1], color='#22cc66', linewidth=2)
ax.fill(coords[:, 0], coords[:, 1], color='#999999', alpha=0.9)

# Green boxes over the previous problem areas
rect1 = plt.Rectangle((-11.5, 48.0), 1.5, 8.0, fill=False, edgecolor='#22cc66', linewidth=2.5, linestyle='-')
rect2 = plt.Rectangle((-8.0, 36.0), 1.0, 12.0, fill=False, edgecolor='#22cc66', linewidth=2.5, linestyle='-')
ax.add_patch(rect1)
ax.add_patch(rect2)

ax.set_aspect('equal')
ax.grid(True, color='#444444', linestyle=':')
ax.set_facecolor('#222222')
fig.patch.set_facecolor('#181818')
ax.set_title("12_Custom_Rod_Detent_Spring_01 (Refined)", color='white', pad=10)
ax.tick_params(colors='white')

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "final_refined_12_spring.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved final_refined_12_spring.png")
