import os
import sys
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]
left_v2 = poly_v2.intersection(shapely.box(-30.0, 15.375, 0.0, 55.0))
coords_v2 = np.array(left_v2.exterior.coords)

# Load updated 12_Custom_Rod_Detent_Spring_01.stl
s12_path = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap", "12_Custom_Rod_Detent_Spring_01.stl")
m_12 = trimesh.load(s12_path, process=True)
pl_12, _ = m_12.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_12 = pl_12.polygons_full[0]
coords_12 = np.array(poly_12.exterior.coords)

fig, axes = plt.subplots(1, 2, figsize=(10, 14))

# 1. Reference v2
axes[0].plot(coords_v2[:, 0], coords_v2[:, 1], color='#3388ff', linewidth=2)
axes[0].fill(coords_v2[:, 0], coords_v2[:, 1], color='#999999', alpha=0.9)
axes[0].set_aspect('equal')
axes[0].grid(True, color='#444444')
axes[0].set_facecolor('#222222')
axes[0].set_title("Reference: 11 - Middle Spring v2", color='white', pad=10)
axes[0].tick_params(colors='white')

# 2. Enhanced Curvy 12 Spring
axes[1].plot(coords_12[:, 0], coords_12[:, 1], color='#22cc66', linewidth=2)
axes[1].fill(coords_12[:, 0], coords_12[:, 1], color='#999999', alpha=0.9)
# Green highlight box on enhanced waist curve
rect = plt.Rectangle((-9.8, 44.0), 2.8, 12.0, fill=False, edgecolor='#22cc66', linewidth=2.5, linestyle='-')
axes[1].add_patch(rect)

axes[1].set_aspect('equal')
axes[1].grid(True, color='#444444')
axes[1].set_facecolor('#222222')
axes[1].set_title("Enhanced Curvy Waist: 12_Custom_Rod_Detent_Spring_01", color='white', pad=10)
axes[1].tick_params(colors='white')

fig.patch.set_facecolor('#181818')
plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "verified_enhanced_waist.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved verified_enhanced_waist.png")
