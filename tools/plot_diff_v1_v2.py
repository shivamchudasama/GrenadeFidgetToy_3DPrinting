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

p1 = pl1.polygons_full[0].intersection(shapely.box(0, 15, 25, 55))
p2 = pl2.polygons_full[0].intersection(shapely.box(0, 15, 25, 55))

diff1 = p1.difference(p2)
diff2 = p2.difference(p1)

fig, ax = plt.subplots(figsize=(10, 12))

x1, y1 = p1.exterior.xy
ax.plot(x1, y1, 'b--', label='v1 outline', alpha=0.6)

x2, y2 = p2.exterior.xy
ax.plot(x2, y2, 'r-', label='v2 outline', linewidth=2)

if diff1.geom_type == 'Polygon':
    dx, dy = diff1.exterior.xy
    ax.fill(dx, dy, color='cyan', alpha=0.5, label='Removed in v2')
elif diff1.geom_type == 'MultiPolygon':
    for g in diff1.geoms:
        dx, dy = g.exterior.xy
        ax.fill(dx, dy, color='cyan', alpha=0.5)

if diff2.geom_type == 'Polygon':
    dx, dy = diff2.exterior.xy
    ax.fill(dx, dy, color='magenta', alpha=0.5, label='Added in v2')
elif diff2.geom_type == 'MultiPolygon':
    for g in diff2.geoms:
        dx, dy = g.exterior.xy
        ax.fill(dx, dy, color='magenta', alpha=0.5)

ax.set_aspect('equal')
ax.grid(True)
ax.legend()
ax.set_title("Comparison: v1 vs v2 (Right Arm)")

plt.savefig(os.path.join(ROOT_DIR, "tools", "diff_v1_v2_plot.png"), dpi=200)
print("Saved diff_v1_v2_plot.png")
