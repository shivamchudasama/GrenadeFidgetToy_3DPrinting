import os
import sys
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stl_path = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap", "12_Custom_Rod_Detent_Spring_01.stl")
m = trimesh.load(stl_path, process=True)

# In 12_Custom_Rod_Detent_Spring_01.stl (oriented at azimuth 0, which is rotated by -90 deg about Y from azimuth 90)
# Let's take a section
# For azimuth 0: X is vertical/axial or Z is radial?
# Let's check mesh bounds:
print("Mesh bounds:", m.bounds)
# Bounds: X in [-12.2, -5.54], Y in [36.0, 62.92], Z in [-1.5, 2.5]
# So:
# Y is the axial direction (36.0 to 62.92)
# X is the radial direction (-12.2 to -5.54) -> -X is outer spine (X = -12.2), -X = -5.54 is the nose
# Z is the thickness direction (-1.5 to 2.5, where rib step is at Z in [1.5, 2.5])

# Let's take 2D section at Z = 0
pl, _ = m.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly = pl.polygons_full[0]

# In poly coords:
# x is toy X (-12.2 to -5.54), y is toy Y (36.0 to 62.92)
# In the user screenshot:
# Vertical axis is Y (36 to 63)
# Horizontal axis: Left is outer spine (X = -12.2 to -10.9), Right is inner / nose (X = -5.54 to -7.4)
coords = np.array(poly.exterior.coords)

print(f"Total polygon vertices: {len(coords)}")

# Let's plot the polygon in the exact visual orientation of the user screenshot:
# Horizontal axis: X (so left is -12.2, right is -5.54)
# Vertical axis: Y (36.0 at bottom, 63.0 at top)
fig, ax = plt.subplots(figsize=(6, 14))
ax.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=1.5)
ax.fill(coords[:, 0], coords[:, 1], color='#cccccc', alpha=0.8)

# Highlight left box: Y in [48.0, 56.0], X in [-11.5, -10.0]
rect1 = plt.Rectangle((-11.5, 48.0), 1.5, 8.0, fill=False, edgecolor='red', linewidth=2)
ax.add_patch(rect1)

# Highlight right box: Y in [36.0, 48.0], X in [-8.0, -7.0]
rect2 = plt.Rectangle((-8.0, 36.0), 1.0, 12.0, fill=False, edgecolor='red', linewidth=2)
ax.add_patch(rect2)

ax.set_aspect('equal')
ax.grid(True)
ax.set_title("12_Custom_Rod_Detent_Spring_01 Cross-Section")
ax.set_xlabel("X (Radial: Outer spine on Left, Inner on Right)")
ax.set_ylabel("Y (Axial)")

plt.savefig(os.path.join(ROOT_DIR, "tools", "inspect_two_boxes.png"), dpi=200)
print("Saved inspect_two_boxes.png")
