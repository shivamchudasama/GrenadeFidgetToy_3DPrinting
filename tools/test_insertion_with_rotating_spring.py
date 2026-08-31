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
    "21_30_Upper_Shell_Rotating_Spring.stl",
]

rod_part_names_no_disc = [
    "22_Custom_Rod_Right.stl",
    "23_Custom_Rod_Middle.stl",
    "24_Custom_Rod_Left.stl",
    "25_Custom_Rod_Lock_Upper_06.stl",
    "26_Custom_Rod_Lock_Lower_07.stl",
]

def to_manifold(tm):
    m64 = manifold3d.Mesh64(
        np.ascontiguousarray(tm.vertices, dtype=np.float64),
        np.ascontiguousarray(tm.faces, dtype=np.uint64)
    )
    return manifold3d.Manifold(m64)

barrel_manifolds = {fn: to_manifold(trimesh.load(os.path.join(asy_dir, fn), force='mesh', process=True)) for fn in barrel_part_names}
rod_manifolds = {fn: to_manifold(trimesh.load(os.path.join(asy_dir, fn), force='mesh', process=True)) for fn in rod_part_names_no_disc}

rod_no_disc = manifold3d.Manifold()
for m in rod_manifolds.values():
    rod_no_disc += m

barrel_all_rigid = manifold3d.Manifold()
for fn in barrel_part_names:
    barrel_all_rigid += barrel_manifolds[fn]

print("=== SLIDING ROD (WITHOUT DISC 27) FROM TOP (+Y = +70 down to 0) INTO ALL BARREL & UPPER STATION PARTS ===")
for dy in range(70, -2, -2):
    rod_trans = rod_no_disc.translate([0, dy, 0])
    inter = rod_trans ^ barrel_all_rigid
    vol = inter.volume()
    status = f"CLASH ({vol:.2f} mm3)" if vol > 0.01 else "CLEAR (0 mm3)"
    print(f"  Delta Y = {dy:+3d} mm : {status}")

