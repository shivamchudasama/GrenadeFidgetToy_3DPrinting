import os
import trimesh
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_DIR = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap")
FLAT_DIR = os.path.join(PKG_DIR, "Flat_Bed_Oriented")

files = [
    "11_Custom_Internal_Barrel_Cap_Option_B.stl",
    "12_Custom_Rod_Detent_Spring_01.stl",
    "13_Custom_Rod_Detent_Spring_02_Dual_Headed.stl",
    "14_Custom_Rod_Detent_Spring_03.stl",
    "15_Custom_Rod_Detent_Spring_04_Dual_Headed.stl",
]

print("=== VERIFYING ASSEMBLED STLs ===")
for fn in files:
    fp = os.path.join(PKG_DIR, fn)
    m = trimesh.load(fp, process=True)
    print(f"{fn:45s} | Watertight: {str(m.is_watertight):5s} | Bodies: {m.body_count:1d} | Volume: {m.volume:8.2f} mm3 | Bounds: {m.bounds}")

print("\n=== VERIFYING FLAT-BED ORIENTED STLs ===")
for fn in files:
    fp = os.path.join(FLAT_DIR, fn)
    m = trimesh.load(fp, process=True)
    print(f"{fn:45s} | Watertight: {str(m.is_watertight):5s} | Bodies: {m.body_count:1d} | Z min: {m.bounds[0][2]:6.3f} mm | Z max: {m.bounds[1][2]:6.3f} mm")
