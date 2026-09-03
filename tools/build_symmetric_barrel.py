import os
import sys
import numpy as np
import trimesh

# Add tools to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_rod_detent import barrel_with_slots

print("=" * 70)
print("BUILDING 10_Custom_Internal_Barrel_4Slot WITH BILATERAL SYMMETRIC SLOTS")
print("=" * 70)

stock, filled, barrel = barrel_with_slots()
print(f"Barrel built: volume = {barrel.volume:.2f} mm3, watertight = {barrel.is_watertight}, bodies = {barrel.body_count}")
print(f"Bounds in assembled space: {np.round(barrel.bounds, 3).tolist()}")

if not barrel.is_watertight or barrel.body_count != 1:
    raise RuntimeError("Barrel is not watertight or has multiple bodies!")

# Target paths
assembled_path = r"d:\GIT_Repo\GrenadeFidgetToy_3DPrinting\Hybrid_Grenade_v1.2\All_Parts_Assembled_Coordinates\10_Custom_Internal_Barrel_4Slot.stl"
subassembly_path = r"d:\GIT_Repo\GrenadeFidgetToy_3DPrinting\Hybrid_Grenade_v1.2\03_Internal_Barrel_And_Upper_Station\10_Custom_Internal_Barrel_4Slot.stl"
flat_bed_path = r"d:\GIT_Repo\GrenadeFidgetToy_3DPrinting\Hybrid_Grenade_v1.2\All_Parts_Flat_Bed_Oriented\10_Custom_Internal_Barrel_4Slot.stl"

# 1. Export Assembled STL
barrel.export(assembled_path)
print(f"[OK] Exported Assembled: {assembled_path}")

# 2. Transform to Bed Pose:
# Bed pose for barrel is rot_matrix = [[1, 0, 0], [0, 0, 1], [0, -1, 0]], yaw = 0
rot_mat = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
m_bed = barrel.copy()
T = np.eye(4)
T[:3, :3] = rot_mat
m_bed.apply_transform(T)
# Align bottom to Z = 0
min_z = m_bed.bounds[0][2]
T_z = np.eye(4)
T_z[2, 3] = -min_z
m_bed.apply_transform(T_z)

# Center X and Y at 0
cx = 0.5 * (m_bed.bounds[0][0] + m_bed.bounds[1][0])
cy = 0.5 * (m_bed.bounds[0][1] + m_bed.bounds[1][1])
T_xy = np.eye(4)
T_xy[0, 3] = -cx
T_xy[1, 3] = -cy
m_bed.apply_transform(T_xy)

print(f"Bed pose bounds: {np.round(m_bed.bounds, 3).tolist()}")

m_bed.export(subassembly_path)
print(f"[OK] Exported Subassembly: {subassembly_path}")
m_bed.export(flat_bed_path)
print(f"[OK] Exported Flat Bed: {flat_bed_path}")

print("\nAll 3 barrel STLs successfully exported!")
