import os
import numpy as np
import trimesh
import manifold3d

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(tools_dir)
v12_dir = os.path.join(root_dir, "Hybrid_Grenade_v1.2")
asy_dir = os.path.join(v12_dir, "All_Parts_Assembled_Coordinates")

barrel_part_names = [
    "10_Custom_Internal_Barrel_4Slot.stl",
    "11_Custom_Internal_Barrel_Cap.stl",
    "18_27_Upper_Shell_Top.stl",
    "19_28_Upper_Shell_Gear.stl",
    "20_29_Upper_Shell_Lock_Ring.stl",
]

rod_part_names = [
    "22_Custom_Rod_Right.stl",
    "23_Custom_Rod_Middle.stl",
    "24_Custom_Rod_Left.stl",
    "25_Custom_Rod_Lock_Upper_06.stl",
    "26_Custom_Rod_Lock_Lower_07.stl",
    "27_Spinner_Lever_08_Rod_Lock.stl",
]

def to_manifold(tm):
    m64 = manifold3d.Mesh64(
        np.ascontiguousarray(tm.vertices, dtype=np.float64),
        np.ascontiguousarray(tm.faces, dtype=np.uint64)
    )
    return manifold3d.Manifold(m64)

barrel_manifolds = {fn: to_manifold(trimesh.load(os.path.join(asy_dir, fn), force='mesh', process=True)) for fn in barrel_part_names}
rod_manifolds = {fn: to_manifold(trimesh.load(os.path.join(asy_dir, fn), force='mesh', process=True)) for fn in rod_part_names}

barrel_rigid = manifold3d.Manifold()
for fn in barrel_part_names:
    barrel_rigid += barrel_manifolds[fn]

print("=== PART-BY-PART COLLISION IDENTIFICATION DURING INSERTION ===")
# Test sliding each rod component individually through the barrel assembly
for dy in [-40, -30, -20, -10, -5, 0, 5, 10, 20, 30, 35, 40, 50]:
    print(f"\n--- Delta Y = {dy:+3d} mm ---")
    for r_name, r_man in rod_manifolds.items():
        r_trans = r_man.translate([0, dy, 0])
        inter = r_trans ^ barrel_rigid
        vol = inter.volume()
        if vol > 0.01:
            # Check which barrel part it clashes with
            clashing_with = []
            for b_name, b_man in barrel_manifolds.items():
                b_inter = r_trans ^ b_man
                if b_inter.volume() > 0.01:
                    clashing_with.append(f"{b_name} ({b_inter.volume():.1f}mm3)")
            print(f"  {r_name:35s} CLASH with: {', '.join(clashing_with)}")

