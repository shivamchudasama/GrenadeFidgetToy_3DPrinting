import os
import numpy as np
import trimesh
import trimesh.collision

tools_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(tools_dir)
v12_dir = os.path.join(root_dir, "Hybrid_Grenade_v1.2")
asy_dir = os.path.join(v12_dir, "All_Parts_Assembled_Coordinates")

# Load individual parts
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

barrel_meshes = {fn: trimesh.load(os.path.join(asy_dir, fn)) for fn in barrel_part_names}
rod_meshes = {fn: trimesh.load(os.path.join(asy_dir, fn)) for fn in rod_part_names}

rod_rigid = trimesh.util.concatenate(list(rod_meshes.values()))
barrel_rigid = trimesh.util.concatenate(list(barrel_meshes.values()))

# Check collision manager at nominal position
collision_mgr = trimesh.collision.CollisionManager()
for fn, m in barrel_meshes.items():
    collision_mgr.add_object(f"barrel_{fn}", m)

print("=== CHECK COLLISION AT NOMINAL ASSEMBLED POSITION ===")
for r_name, r_mesh in rod_meshes.items():
    is_col, contact_data = collision_mgr.in_collision_single(r_mesh, return_data=True)
    if is_col:
        print(f"COLLISION: {r_name} collides with barrel parts:")
        for cd in contact_data:
            print(f"   with {cd.names[0] if cd.names[0] != r_name else cd.names[1]}")
    else:
        print(f"OK: {r_name} has NO collision with barrel assembly.")

print("\n=== DETAILED CLEARANCE & INTERFERENCE WITH SPRINGS ===")
# Detent springs (12-15) are flexible springs that rest against the rod detents.
# Check without flexible springs (housing only)
housing_mgr = trimesh.collision.CollisionManager()
for fn in ["10_Custom_Internal_Barrel_4Slot.stl", "11_Custom_Internal_Barrel_Cap.stl", "18_27_Upper_Shell_Top.stl", "19_28_Upper_Shell_Gear.stl", "20_29_Upper_Shell_Lock_Ring.stl"]:
    housing_mgr.add_object(f"housing_{fn}", barrel_meshes[fn])

is_col, contact_data = housing_mgr.in_collision_single(rod_rigid, return_data=True)
print(f"Rigid Rod vs Rigid Housings (without springs): Collision = {is_col}")
if is_col:
    for cd in contact_data:
        print(f"   Contact between {cd.names[0]} and {cd.names[1]}")

