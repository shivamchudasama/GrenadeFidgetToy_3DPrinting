import os
import numpy as np
import trimesh

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(tools_dir)
v12_dir = os.path.join(root_dir, "Hybrid_Grenade_v1.2")
asy_dir = os.path.join(v12_dir, "All_Parts_Assembled_Coordinates")

parts = {
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
    "22_rod_right": trimesh.load(os.path.join(asy_dir, "22_Custom_Rod_Right.stl")),
    "23_rod_middle": trimesh.load(os.path.join(asy_dir, "23_Custom_Rod_Middle.stl")),
    "24_rod_left": trimesh.load(os.path.join(asy_dir, "24_Custom_Rod_Left.stl")),
    "25_lock_upper": trimesh.load(os.path.join(asy_dir, "25_Custom_Rod_Lock_Upper_06.stl")),
    "26_lock_lower": trimesh.load(os.path.join(asy_dir, "26_Custom_Rod_Lock_Lower_07.stl")),
    "27_disc": trimesh.load(os.path.join(asy_dir, "27_Spinner_Lever_08_Rod_Lock.stl")),
}

print("=== INNER BORE APERTURES OF HOUSINGS ===")
for name in ["10_barrel", "11_cap", "18_shell_top", "19_shell_gear", "20_lock_ring"]:
    m = parts[name]
    # Slice at multiple heights
    b = m.bounds
    y_vals = np.linspace(b[0][1] + 0.5, b[1][1] - 0.5, 5)
    print(f"\n--- {name} (Y from {b[0][1]:.2f} to {b[1][1]:.2f}) ---")
    for y in y_vals:
        sec = m.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
        if sec:
            pts = sec.vertices
            r = np.sqrt(pts[:, 0]**2 + pts[:, 2]**2)
            # Find innermost ring
            print(f"  Y={y:5.2f}mm: min_radius={r.min():.2f}mm (diameter {2*r.min():.2f}mm), max_radius={r.max():.2f}mm (diameter {2*r.max():.2f}mm)")

print("\n=== ROD CROSS SECTION SIZES ===")
for name in ["22_rod_right", "23_rod_middle", "24_rod_left", "25_lock_upper", "26_lock_lower", "27_disc"]:
    m = parts[name]
    b = m.bounds
    print(f"Part {name:15s}: Bounds X [{b[0][0]:.2f}, {b[1][0]:.2f}], Y [{b[0][1]:.2f}, {b[1][1]:.2f}], Z [{b[0][2]:.2f}, {b[1][2]:.2f}]")

