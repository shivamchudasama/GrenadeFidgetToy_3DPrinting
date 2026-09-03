import os
import sys
import numpy as np
import trimesh
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD

print("=" * 80)
print("BUILDING 10_Custom_Internal_Barrel_4Slot.stl WITH RIGHT-ANGLED L-SHAPED SLOTS")
print("=" * 80)

# Right-angled L-slot cutter cross section in (x, r) coordinates at azimuth 90:
# Matching Right-Angled L-shaped spring foot with 0.25 mm 3D printing clearances:
# - Spring flat guide wall is at X = -1.500 mm -> Slot flat wall at X = -1.750 mm
# - Spring neck wall is at X = +1.500 mm -> Slot neck wall at X = +1.750 mm
# - Spring pocket wall is at X = +3.300 mm -> Slot pocket wall at X = +3.550 mm
# - Spring shoulder step is at R = 9.600 mm -> Slot shoulder step at R = 9.450 mm
# - Spring outer radius is at R = 13.350 mm -> Slot back wall at R = 13.500 mm
# - Central bore opening at R = 6.000 mm
X_FLAT = -1.750
X_NECK = 1.750
X_POCKET = 3.550
R_IN = 6.000
R_STEP = 9.450
R_OUT = 13.500

section = shapely.Polygon([
    (X_FLAT, R_IN),
    (X_NECK, R_IN),
    (X_NECK, R_STEP),
    (X_POCKET, R_STEP),
    (X_POCKET, R_OUT),
    (X_FLAT, R_OUT),
    (X_FLAT, R_IN)
])

def slot_cut_L(azimuth):
    """One L-shaped slot cutter, extruded and turned to the target azimuth."""
    solid = trimesh.creation.extrude_polygon(section, height=BRD.SLOT_Y1 - BRD.SLOT_Y0)
    return BRD._roty(azimuth - 90.0, BRD._stand_up(solid, BRD.SLOT_Y1))

# Load stock barrel, fill legacy features, and re-bore
stock = BRD._load(BRD.STOCK_BARREL)
plugged = trimesh.boolean.union(
    [stock, BRD.pin_fill(stock), BRD.legacy_fill(stock)], engine=BRD.ENGINE)
if plugged.body_count != 1:
    raise RuntimeError(f"Barrel filling left {plugged.body_count} bodies!")

filled = trimesh.boolean.difference([plugged, BRD.bore_solid(stock)], engine=BRD.ENGINE)
if filled.body_count != 1:
    raise RuntimeError(f"Re-boring left {filled.body_count} bodies!")

# Cut the 4 L-shaped slots
barrel_L = trimesh.boolean.difference(
    [filled] + [slot_cut_L(az) for az in BRD.SLOT_AZIMUTHS], engine=BRD.ENGINE)

if not barrel_L.is_watertight or barrel_L.body_count != 1:
    raise RuntimeError(f"L-slot cut failed: watertight={barrel_L.is_watertight}, bodies={barrel_L.body_count}")

print("\n--- MEASURED BARREL RESULTS ---")
print(f"Watertight: {barrel_L.is_watertight}")
print(f"Body count: {barrel_L.body_count}")
print(f"Volume: {barrel_L.volume:.2f} mm3")
print(f"Assembled bounds: {np.round(barrel_L.bounds, 3).tolist()}")

# Export targets
assembled_path = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Assembled_Coordinates", "10_Custom_Internal_Barrel_4Slot.stl")
subassembly_path = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "03_Internal_Barrel_And_Upper_Station", "10_Custom_Internal_Barrel_4Slot.stl")
flat_bed_path = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Flat_Bed_Oriented", "10_Custom_Internal_Barrel_4Slot.stl")

# 1. Export assembled STL
barrel_L.export(assembled_path)
print(f"[OK] Exported Assembled: {assembled_path}")

# 2. Transform to Bed Pose (standing upright on printer bed)
# Canonical bed pose for barrel: rot_matrix = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]
rot_mat = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
m_bed = barrel_L.copy()
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
