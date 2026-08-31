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

barrel_manifolds = {}
for fn in barrel_part_names:
    tm = trimesh.load(os.path.join(asy_dir, fn), force='mesh', process=True)
    barrel_manifolds[fn] = to_manifold(tm)

rod_manifolds = {}
for fn in rod_part_names:
    tm = trimesh.load(os.path.join(asy_dir, fn), force='mesh', process=True)
    rod_manifolds[fn] = to_manifold(tm)

print("=== EXACT VOLUMETRIC INTERSECTION AT NOMINAL ASSEMBLED POSITION ===")
for r_name, r_man in rod_manifolds.items():
    print(f"\nChecking {r_name} (volume = {r_man.volume():.2f} mm3):")
    for b_name, b_man in barrel_manifolds.items():
        inter = r_man ^ b_man  # intersection
        vol = inter.volume()
        if vol > 0.001:
            box = inter.bounding_box()
            print(f"  --> CLASH with {b_name}: overlap volume = {vol:.3f} mm3, bbox = {box}")
        else:
            print(f"  [OK] No clash with {b_name}")

print("\n=== COMBINED HOUSING (WITHOUT SPRINGS) VS COMBINED ROD ===")
rod_total = manifold3d.Manifold()
for m in rod_manifolds.values():
    rod_total += m

housings = ["10_Custom_Internal_Barrel_4Slot.stl", "11_Custom_Internal_Barrel_Cap.stl", "18_27_Upper_Shell_Top.stl", "19_28_Upper_Shell_Gear.stl", "20_29_Upper_Shell_Lock_Ring.stl"]
housing_total = manifold3d.Manifold()
for fn in housings:
    housing_total += barrel_manifolds[fn]

inter_housing = rod_total ^ housing_total
print(f"Total Rod Volume: {rod_total.volume():.2f} mm3")
print(f"Total Housing Volume: {housing_total.volume():.2f} mm3")
print(f"Overlap between Rigid Rod & Rigid Housings: {inter_housing.volume():.4f} mm3")
if inter_housing.volume() > 0.001:
    box = inter_housing.bounding_box()
    print(f"Overlap bounding box: {box}")

