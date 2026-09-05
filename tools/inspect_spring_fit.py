import os
import trimesh
import numpy as np

v12_dir = r"d:\GIT_Repo\GrenadeFidgetToy_3DPrinting\Hybrid_Grenade_v1.2"
asy_dir = os.path.join(v12_dir, "All_Parts_Assembled_Coordinates")

spring = trimesh.load(os.path.join(asy_dir, "28_09_Rod_Spring_Hinge_T_Head.stl"))
mid = trimesh.load(os.path.join(asy_dir, "23_Custom_Rod_Middle.stl"))
hl = trimesh.load(os.path.join(asy_dir, "29_Custom_Handle_Left.stl"))
hr = trimesh.load(os.path.join(asy_dir, "30_Custom_Handle_Right.stl"))
dpin = trimesh.load(os.path.join(asy_dir, "36_15_Handle_Rotating_Lock_D_Pin.stl"))
neck = trimesh.load(os.path.join(asy_dir, "34_Custom_16_Handle_Lock_Neck.stl"))

print("=== 1. SPRING BOUNDS & GEOMETRY ===")
print("Spring Bounds:", spring.bounds)
print("Spring Extents [X, Y, Z]:", spring.extents)

print("\n=== 2. ROD MIDDLE CAVITY FOR SPRING ===")
# Mid rod bounds
print("Mid Rod Bounds:", mid.bounds)
# Inspect cavity in Mid Rod between Y=64 and Y=86
# Spring is inside X in [-3, 3], Y in [63.96, 85.65]
sec_mid_y75 = mid.section(plane_origin=[0, 75, 0], plane_normal=[0, 1, 0])
p2d, _ = sec_mid_y75.to_2D()
print("Mid Rod at Y=75 mm:")
print("  Outer bounds:", sec_mid_y75.bounds)
print("  Number of polygons / rails:", len(p2d.polygons_full))
for i, poly in enumerate(p2d.polygons_full):
    print(f"    Rail {i}: bounds={poly.bounds}")

print("\n=== 3. HINGE PIVOT & D-PIN ===")
print("D-Pin Bounds:", dpin.bounds)
print("D-Pin Extents:", dpin.extents)
pivot_y = (dpin.bounds[0, 1] + dpin.bounds[1, 1]) / 2.0
pivot_z = (dpin.bounds[0, 2] + dpin.bounds[1, 2]) / 2.0
print(f"Hinge Axis Pivot: Y={pivot_y:.3f}, Z={pivot_z:.3f}, along X in [{dpin.bounds[0, 0]:.1f}, {dpin.bounds[1, 0]:.1f}]")

print("\n=== 4. SPRING DETENT TIP VS HINGE CAM ===")
# Top tip of the spring
y_top = spring.bounds[1, 1]
print(f"Spring Top Y={y_top:.3f}")
# Distance from pivot to spring top:
print(f"Vertical distance from Pivot to Spring Top: {pivot_y - y_top:.3f} mm")

# Find vertices of the handle around the hinge
h_combo = hl + hr
# Section at X = -1.0, 0.0, 1.0, and X = -5.0 (cheek)
for x_plane in [0.0, -2.5, -4.5, -7.0]:
    sec = hl.section(plane_origin=[x_plane, 0, 0], plane_normal=[1, 0, 0])
    if sec is not None:
        p2d, _ = sec.to_2D()
        print(f"Handle section at X={x_plane:.1f}: area={p2d.area:.2f}, bounds in (Y, Z)={sec.bounds[:, [1, 2]].tolist()}")
    else:
        print(f"Handle section at X={x_plane:.1f}: None")
