import os
import numpy as np
import trimesh

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(tools_dir)
v12_dir = os.path.join(root_dir, "Hybrid_Grenade_v1.2")
asy_dir = os.path.join(v12_dir, "All_Parts_Assembled_Coordinates")

rot_spring = trimesh.load(os.path.join(asy_dir, "21_30_Upper_Shell_Rotating_Spring.stl"))
rod_right = trimesh.load(os.path.join(asy_dir, "22_Custom_Rod_Right.stl"))
rod_middle = trimesh.load(os.path.join(asy_dir, "23_Custom_Rod_Middle.stl"))
rod_left = trimesh.load(os.path.join(asy_dir, "24_Custom_Rod_Left.stl"))
rod_upper = trimesh.util.concatenate([rod_right, rod_middle, rod_left])

print("=== ROTATING SPRING (Part 21) & UPPER ROD HEX PRISM ANALYSIS ===")
print(f"Rotating Spring Bounds: Y [{rot_spring.bounds[0][1]:.2f} to {rot_spring.bounds[1][1]:.2f}]")

for y in [64.0, 68.0, 72.0, 76.0]:
    sec_spring = rot_spring.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    sec_rod = rod_upper.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    
    if sec_spring and sec_rod:
        r_spring = np.sqrt(sec_spring.vertices[:, 0]**2 + sec_spring.vertices[:, 2]**2)
        r_rod = np.sqrt(sec_rod.vertices[:, 0]**2 + sec_rod.vertices[:, 2]**2)
        print(f"Y = {y:.1f} mm: Spring inner bore min R = {r_spring.min():.3f} mm, Rod outer max R = {r_rod.max():.3f} mm, Clearance = {r_spring.min() - r_rod.max():.3f} mm")

