import os
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)

# Let's inspect the exact 2D section of v2
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]

# Left arm (x <= 0) and right arm (x >= 0)
arm_right = poly_v2.intersection(shapely.box(0, 15, 25, 55))
arm_left = poly_v2.intersection(shapely.box(-25, 15, 0, 55))

print("=== 11 - Middle Spring v2 Dimensions ===")
print("Thickness (Z extents):", m_v2.extents[2], "mm (bounds Z:", m_v2.bounds[:, 2], ")")
print("Total X span:", m_v2.extents[0], "mm (bounds X:", m_v2.bounds[:, 0], ")")
print("Total Y span:", m_v2.extents[1], "mm (bounds Y:", m_v2.bounds[:, 1], ")")

# In arm_right:
# What are the exact coordinates of:
# 1. Outer rail: x = 14.45088
# 2. Outer rail inner face: x = 12.65088 (width = 1.800 mm)
# 3. Outer slot width = 12.65088 - 11.25088 = 1.400 mm
# 4. Flexure stalk ascending beam: x in [10.45088, 11.25088] (width = 0.800 mm)
# 5. Inner slot between beams: width = 10.45088 - 9.45088 = 1.000 mm
# 6. Flexure stalk descending beam: x in [8.65088, 9.45088] (width = 0.800 mm)
# 7. Nose apex: x = 5.85319, y = 40.54041
# 8. Top of U-turn loop: y = 43.86230
# 9. Top of outer rail: y = 48.00000

# Let's inspect the rod rack in Hybrid_Grenade_v1.2:
rod_path = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Assembled_Coordinates", "23_Custom_Rod_Middle.stl")
m_rod = trimesh.load(rod_path, process=True)
print("\n=== Custom Rod Middle Dimensions ===")
print("Rod bounds:", m_rod.bounds)

# Let's check barrel dimensions:
barrel_path = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Assembled_Coordinates", "10_Custom_Internal_Barrel_4Slot.stl")
m_barrel = trimesh.load(barrel_path, process=True)
print("\n=== Custom Internal Barrel 4Slot Dimensions ===")
print("Barrel bounds:", m_barrel.bounds)

cap_path = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap", "11_Custom_Internal_Barrel_Cap_Option_B.stl")
m_cap = trimesh.load(cap_path, process=True)
print("\n=== Slotted Cap Option B Dimensions ===")
print("Cap bounds:", m_cap.bounds)
