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
    "12_Custom_Rod_Detent_Spring_01.stl",
    "13_Custom_Rod_Detent_Spring_02.stl",
    "14_Custom_Rod_Detent_Spring_03.stl",
    "15_Custom_Rod_Detent_Spring_04.stl",
    "18_27_Upper_Shell_Top.stl",
    "19_28_Upper_Shell_Gear.stl",
    "20_29_Upper_Shell_Lock_Ring.stl",
    "21_30_Upper_Shell_Rotating_Spring.stl",
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

rod_rigid = manifold3d.Manifold()
for m in rod_manifolds.values():
    rod_rigid += m

# Rigid barrel (without flexure springs)
barrel_rigid = manifold3d.Manifold()
for fn in ["10_Custom_Internal_Barrel_4Slot.stl", "11_Custom_Internal_Barrel_Cap.stl", "18_27_Upper_Shell_Top.stl", "19_28_Upper_Shell_Gear.stl", "20_29_Upper_Shell_Lock_Ring.stl"]:
    barrel_rigid += barrel_manifolds[fn]

# Just 10_barrel
barrel_10 = barrel_manifolds["10_Custom_Internal_Barrel_4Slot.stl"]
cap_11 = barrel_manifolds["11_Custom_Internal_Barrel_Cap.stl"]
top_shell_18 = barrel_manifolds["18_27_Upper_Shell_Top.stl"]

print("=== TESTING INSERTION TRAJECTORY ===")
# delta_y ranges from -80 to +80 mm (0 is nominal position)
# Positive delta_y means rod is higher than nominal (sliding down from top)
# Negative delta_y means rod is lower than nominal (sliding up from bottom)

print("\n--- Sliding FULL PRE-ASSEMBLED ROD (All 6 parts) into BARREL CHASSIS (Part 10 only) ---")
for dy in range(-60, 65, 5):
    # translate rod by dy in Y
    rod_trans = rod_rigid.translate([0, dy, 0])
    inter = rod_trans ^ barrel_10
    vol = inter.volume()
    status = f"CLASH ({vol:.1f} mm3)" if vol > 0.01 else "CLEAR (0 mm3)"
    print(f"  Delta Y = {dy:+4d} mm (Y pos = {15.3+dy:5.1f} to {99.6+dy:5.1f}) : {status}")

print("\n--- Sliding FULL PRE-ASSEMBLED ROD into FULL RIGID UPPER & BARREL ASSEMBLY ---")
for dy in range(-60, 65, 5):
    rod_trans = rod_rigid.translate([0, dy, 0])
    inter = rod_trans ^ barrel_rigid
    vol = inter.volume()
    status = f"CLASH ({vol:.1f} mm3)" if vol > 0.01 else "CLEAR (0 mm3)"
    print(f"  Delta Y = {dy:+4d} mm : {status}")

