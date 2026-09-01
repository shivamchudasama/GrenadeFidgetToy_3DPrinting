import os
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v1_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring.stl")
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")

m1 = trimesh.load(v1_path, process=True)
m2 = trimesh.load(v2_path, process=True)

pl1, _ = m1.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
pl2, _ = m2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))

p1 = pl1.polygons_full[0]
p2 = pl2.polygons_full[0]

fig, axes = plt.subplots(1, 2, figsize=(12, 10))

for ax, poly, title in [(axes[0], p1, "v1"), (axes[1], p2, "v2")]:
    x, y = poly.exterior.xy
    ax.plot(x, y, 'b-', label='exterior')
    for interior in poly.interiors:
        ix, iy = interior.xy
        ax.plot(ix, iy, 'r--', label='interior')
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.grid(True)

plt.savefig(os.path.join(ROOT_DIR, "tools", "compare_v1_v2.png"), dpi=150)
print("Saved compare_v1_v2.png")
