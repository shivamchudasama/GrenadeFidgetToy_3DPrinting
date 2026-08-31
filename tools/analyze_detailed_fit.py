import os
import numpy as np
import trimesh
import trimesh.boolean

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(tools_dir)
v12_dir = os.path.join(root_dir, "Hybrid_Grenade_v1.2")
asy_dir = os.path.join(v12_dir, "All_Parts_Assembled_Coordinates")

print("=== DETAILED GEOMETRY ANALYSIS ===")

# Load all individual parts
barrel_parts = {
    "10_barrel": trimesh.load(os.path.join(asy_dir, "10_Custom_Internal_Barrel_4Slot.stl")),
    "11_cap": trimesh.load(os.path.join(asy_dir, "11_Custom_Internal_Barrel_Cap.stl")),
    "12_spring1": trimesh.load(os.path.join(asy_dir, "12_Custom_Rod_Detent_Spring_01.stl")),
    "13_spring2": trimesh.load(os.path.join(asy_dir, "13_Custom_Rod_Detent_Spring_02.stl")),
    "14_spring3": trimesh.load(os.path.join(asy_dir, "14_Custom_Rod_Detent_Spring_03.stl")),
    "15_spring4": trimesh.load(os.path.join(asy_dir, "15_Custom_Rod_Detent_Spring_04.stl")),
    "18_shell_top": trimesh.load(os.path.join(asy_dir, "18_27_Upper_Shell_Top.stl")),
    "19_shell_gear": trimesh.load(os.path.join(asy_dir, "19_28_Upper_Shell_Gear.stl")),
    "20_lock_ring": trimesh.load(os.path.join(asy_dir, "20_29_Upper_Shell_Lock_Ring.stl")),
    "21_rot_spring": trimesh.load(os.path.join(asy_dir, "21_30_Upper_Shell_Rotating_Spring.stl")),
}

rod_parts = {
    "22_rod_right": trimesh.load(os.path.join(asy_dir, "22_Custom_Rod_Right.stl")),
    "23_rod_middle": trimesh.load(os.path.join(asy_dir, "23_Custom_Rod_Middle.stl")),
    "24_rod_left": trimesh.load(os.path.join(asy_dir, "24_Custom_Rod_Left.stl")),
    "25_lock_upper": trimesh.load(os.path.join(asy_dir, "25_Custom_Rod_Lock_Upper_06.stl")),
    "26_lock_lower": trimesh.load(os.path.join(asy_dir, "26_Custom_Rod_Lock_Lower_07.stl")),
    "27_disc": trimesh.load(os.path.join(asy_dir, "27_Spinner_Lever_08_Rod_Lock.stl")),
}

print("\n--- Part Bounds & Dimensions ---")
for k, m in barrel_parts.items():
    b = m.bounds
    ext = m.extents
    print(f"Barrel Part {k:20s}: Y [{b[0][1]:.2f} to {b[1][1]:.2f}], X span {ext[0]:.2f}, Z span {ext[2]:.2f}, total extents: {ext.round(2).tolist()}")

print("\n--- Rod Part Bounds & Dimensions ---")
for k, m in rod_parts.items():
    b = m.bounds
    ext = m.extents
    print(f"Rod Part    {k:20s}: Y [{b[0][1]:.2f} to {b[1][1]:.2f}], X span {ext[0]:.2f}, Z span {ext[2]:.2f}, total extents: {ext.round(2).tolist()}")

# Create combined rod mesh and combined barrel mesh
rod_combined = trimesh.util.concatenate(list(rod_parts.values()))
barrel_combined = trimesh.util.concatenate(list(barrel_parts.values()))

print(f"\nRod Combined Bounds: {rod_combined.bounds.round(3).tolist()}")
print(f"Rod Combined Extents: {rod_combined.extents.round(3).tolist()}")

print(f"\nBarrel Combined Bounds: {barrel_combined.bounds.round(3).tolist()}")
print(f"Barrel Combined Extents: {barrel_combined.extents.round(3).tolist()}")

# Analyze cross-sections along Y axis
print("\n--- Cross-Section Profiles along Y ---")
y_levels = np.linspace(16, 98, 42)

for y in y_levels:
    plane_origin = [0, y, 0]
    plane_normal = [0, 1, 0]
    
    # Rod cross section
    try:
        rod_slice = rod_combined.section(plane_origin=plane_origin, plane_normal=plane_normal)
        if rod_slice is not None:
            # rod slice 2D bounds
            r_pts = rod_slice.vertices
            r_x_min, r_x_max = r_pts[:, 0].min(), r_pts[:, 0].max()
            r_z_min, r_z_max = r_pts[:, 2].min(), r_pts[:, 2].max()
            r_max_r = np.sqrt(r_pts[:, 0]**2 + r_pts[:, 2]**2).max()
            rod_str = f"Rod: X[{r_x_min:5.1f},{r_x_max:5.1f}] Z[{r_z_min:5.1f},{r_z_max:5.1f}] maxR={r_max_r:4.1f}mm"
        else:
            rod_str = "Rod: None"
    except Exception as e:
        rod_str = f"Rod: Err ({e})"

    # Barrel cross section
    try:
        barrel_slice = barrel_combined.section(plane_origin=plane_origin, plane_normal=plane_normal)
        if barrel_slice is not None:
            b_pts = barrel_slice.vertices
            b_x_min, b_x_max = b_pts[:, 0].min(), b_pts[:, 0].max()
            b_z_min, b_z_max = b_pts[:, 2].min(), b_pts[:, 2].max()
            # Calculate inner radius (approx by finding points closest to origin in 2D)
            r_all = np.sqrt(b_pts[:, 0]**2 + b_pts[:, 2]**2)
            b_min_r = r_all.min()
            b_max_r = r_all.max()
            barrel_str = f"Barrel: minR={b_min_r:4.1f}mm maxR={b_max_r:4.1f}mm"
        else:
            barrel_str = "Barrel: None"
    except Exception as e:
        barrel_str = f"Barrel: Err ({e})"
        
    print(f"Y={y:5.1f}mm | {rod_str:48s} | {barrel_str}")

