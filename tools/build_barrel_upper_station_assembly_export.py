"""Build and export the complete 10-part assembled GLB from 03_Internal_Barrel_And_Upper_Station.

This script loads the 10 parts forming the complete Internal Barrel & Upper Station Sub-Assembly:
  1. 10_Custom_Internal_Barrel_4Slot (4-slot barrel chassis with filled pin channels)
  2. 11_Custom_Internal_Barrel_Cap (Disc top cap trapping all 4 springs)
  3. 12_Custom_Rod_Detent_Spring_01 (Axial rod detent spring 1 - az 0 deg)
  4. 13_Custom_Rod_Detent_Spring_02 (Axial rod detent spring 2 - az 90 deg)
  5. 14_Custom_Rod_Detent_Spring_03 (Axial rod detent spring 3 - az 180 deg)
  6. 15_Custom_Rod_Detent_Spring_04 (Axial rod detent spring 4 - az 270 deg)
  7. 18_27_Upper_Shell_Top (Original Tactical upper top housing shell)
  8. 19_28_Upper_Shell_Gear (Upper station clicker gear)
  9. 20_29_Upper_Shell_Lock_Ring (Bottom thrust lock ring for gear)
  10. 21_30_Upper_Shell_Rotating_Spring (Upper station detent spring)

Outputs:
  - Hybrid_Grenade_v1.2/03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_And_Upper_Station_Assembly.glb
"""
from __future__ import annotations

import os
import sys
import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
ASY_DIR = os.path.join(V12_DIR, "All_Parts_Assembled_Coordinates")
SUBASSY_DIR = os.path.join(V12_DIR, "03_Internal_Barrel_And_Upper_Station")

BARREL_UPPER_STATION_PARTS = [
    {
        "id": 10,
        "filename": "10_Custom_Internal_Barrel_4Slot.stl",
        "name": "10_Custom_Internal_Barrel_4Slot",
        "title": "4-Slot Internal Barrel Chassis (10)",
        "color_rgb": (55, 65, 75),        # Dark Gunmetal Chassis
        "metallic": 0.35,
        "roughness": 0.45,
    },
    {
        "id": 11,
        "filename": "11_Custom_Internal_Barrel_Cap.stl",
        "name": "11_Custom_Internal_Barrel_Cap",
        "title": "Internal Barrel Retention Cap (11)",
        "color_rgb": (70, 80, 90),        # Gunmetal
        "metallic": 0.35,
        "roughness": 0.45,
    },
    {
        "id": 12,
        "filename": "12_Custom_Rod_Detent_Spring_01.stl",
        "name": "12_Custom_Rod_Detent_Spring_01",
        "title": "Axial Rod Detent Spring 01 (az 0°)",
        "color_rgb": (255, 130, 45),      # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
    {
        "id": 13,
        "filename": "13_Custom_Rod_Detent_Spring_02.stl",
        "name": "13_Custom_Rod_Detent_Spring_02",
        "title": "Axial Rod Detent Spring 02 (az 90°)",
        "color_rgb": (255, 130, 45),      # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
    {
        "id": 14,
        "filename": "14_Custom_Rod_Detent_Spring_03.stl",
        "name": "14_Custom_Rod_Detent_Spring_03",
        "title": "Axial Rod Detent Spring 03 (az 180°)",
        "color_rgb": (255, 130, 45),      # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
    {
        "id": 15,
        "filename": "15_Custom_Rod_Detent_Spring_04.stl",
        "name": "15_Custom_Rod_Detent_Spring_04",
        "title": "Axial Rod Detent Spring 04 (az 270°)",
        "color_rgb": (255, 130, 45),      # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
    {
        "id": 18,
        "filename": "18_27_Upper_Shell_Top.stl",
        "name": "18_27_Upper_Shell_Top",
        "title": "Upper Shell Top Housing (27)",
        "color_rgb": (122, 181, 102),     # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
    },
    {
        "id": 19,
        "filename": "19_28_Upper_Shell_Gear.stl",
        "name": "19_28_Upper_Shell_Gear",
        "title": "Upper Shell Clicker Gear (28)",
        "color_rgb": (195, 205, 215),     # Knurled Steel Silver
        "metallic": 0.85,
        "roughness": 0.25,
    },
    {
        "id": 20,
        "filename": "20_29_Upper_Shell_Lock_Ring.stl",
        "name": "20_29_Upper_Shell_Lock_Ring",
        "title": "Upper Shell Lock Ring (29)",
        "color_rgb": (140, 190, 115),     # Olive Drab Accent
        "metallic": 0.15,
        "roughness": 0.55,
    },
    {
        "id": 21,
        "filename": "21_30_Upper_Shell_Rotating_Spring.stl",
        "name": "21_30_Upper_Shell_Rotating_Spring",
        "title": "Upper Shell Rotating Spring (30)",
        "color_rgb": (255, 110, 30),      # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
]


def load_barrel_upper_station_parts():
    loaded = []
    for info in BARREL_UPPER_STATION_PARTS:
        path = os.path.join(ASY_DIR, info["filename"])
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing assembled source: {path}")
        mesh = trimesh.load(path, force="mesh", process=True)
        loaded.append({
            **info,
            "mesh": mesh,
        })
    return loaded


def export_assembled_glb(parts, assembled_glb_path):
    """Export PBR GLB model for the fully assembled internal barrel and upper station."""
    scene_asy = trimesh.Scene()
    for p in parts:
        m = p["mesh"].copy()
        r, g, b = p["color_rgb"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        rgba_byte = list(p["color_rgb"]) + [255]
        m.visual = trimesh.visual.ColorVisuals(
            mesh=m,
            face_colors=np.tile(rgba_byte, (len(m.faces), 1)),
        )
        mat = trimesh.visual.material.PBRMaterial(
            baseColorFactor=color_norm,
            metallicFactor=float(p["metallic"]),
            roughnessFactor=float(p["roughness"]),
            name=f"mat_{p['id']}",
        )
        m.visual.material = mat
        scene_asy.add_geometry(m, node_name=p["name"], geom_name=p["name"])

    glb_asy_bytes = scene_asy.export(file_type="glb")
    with open(assembled_glb_path, "wb") as f:
        f.write(glb_asy_bytes)
    return glb_asy_bytes


def main():
    print("=" * 80)
    print("BUILDING INTERNAL BARREL & UPPER STATION ASSEMBLED GLB")
    print("=" * 80)

    print("\nLoading 10 parts from assembled coordinate space...")
    parts = load_barrel_upper_station_parts()
    for p in parts:
        m = p["mesh"]
        print(f"  - [{p['id']}] {p['title']}: {p['filename']} (vol={m.volume:.2f} mm3)")

    os.makedirs(SUBASSY_DIR, exist_ok=True)
    out_glb = os.path.join(SUBASSY_DIR, "Custom_Internal_Barrel_And_Upper_Station_Assembly.glb")

    glb_bytes = export_assembled_glb(parts, out_glb)
    print(f"\n[SUCCESS] Exported: {out_glb} ({len(glb_bytes):,} bytes)")
    print("=" * 80)


if __name__ == "__main__":
    main()
