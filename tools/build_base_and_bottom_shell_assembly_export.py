"""Build and export the complete 6-part assembled GLB from 01_Base_And_Bottom_Shell.

This script loads the 6 parts forming the complete Base & Bottom Shell Assembly:
  1. 01_04_Bottom_Shell_01 (Outer bottom shell tier 1)
  2. 02_05_Bottom_Shell_02 (Outer bottom shell tier 2)
  3. 03_06_Bottom_Shell_03 (Outer bottom shell tier 3)
  4. 04_01_Bottom_Lock_Shell (Inner bottom retaining lock cylinder)
  5. 05_02_Bottom_Spring (Bottom compression flexure spring)
  6. 06_03_Bottom_Shell_Spacer (Spacer ring sealing bottom spring pocket)

Outputs:
  - Hybrid_Grenade_v1.2/01_Base_And_Bottom_Shell/Custom_Base_And_Bottom_Shell_Assembly.glb
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
SUBASSY_DIR = os.path.join(V12_DIR, "01_Base_And_Bottom_Shell")

BASE_BOTTOM_SHELL_PARTS = [
    {
        "id": 1,
        "filename": "01_04_Bottom_Shell_01.stl",
        "name": "01_04_Bottom_Shell_01",
        "title": "Outer Bottom Shell Tier 1 (04)",
        "color_rgb": (122, 181, 102),     # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
    },
    {
        "id": 2,
        "filename": "02_05_Bottom_Shell_02.stl",
        "name": "02_05_Bottom_Shell_02",
        "title": "Outer Bottom Shell Tier 2 (05)",
        "color_rgb": (122, 181, 102),     # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
    },
    {
        "id": 3,
        "filename": "03_06_Bottom_Shell_03.stl",
        "name": "03_06_Bottom_Shell_03",
        "title": "Outer Bottom Shell Tier 3 (06)",
        "color_rgb": (122, 181, 102),     # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
    },
    {
        "id": 4,
        "filename": "04_01_Bottom_Lock_Shell.stl",
        "name": "04_01_Bottom_Lock_Shell",
        "title": "Inner Bottom Lock Cylinder Shell (01)",
        "color_rgb": (65, 75, 85),        # Gunmetal
        "metallic": 0.4,
        "roughness": 0.45,
    },
    {
        "id": 5,
        "filename": "05_02_Bottom_Spring.stl",
        "name": "05_02_Bottom_Spring",
        "title": "Bottom Compression Flexure Spring (02)",
        "color_rgb": (255, 110, 30),      # Vibrant Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
    {
        "id": 6,
        "filename": "06_03_Bottom_Shell_Spacer.stl",
        "name": "06_03_Bottom_Shell_Spacer",
        "title": "Bottom Shell Spacer Ring (03)",
        "color_rgb": (80, 90, 100),       # Slate Gunmetal
        "metallic": 0.4,
        "roughness": 0.45,
    },
]


def load_base_bottom_shell_parts():
    loaded = []
    for info in BASE_BOTTOM_SHELL_PARTS:
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
    """Export PBR GLB model for the fully assembled base and bottom shell."""
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
    print("BUILDING BASE & BOTTOM SHELL ASSEMBLED GLB")
    print("=" * 80)

    print("\nLoading 6 base and bottom shell parts from assembled coordinate space...")
    parts = load_base_bottom_shell_parts()
    for p in parts:
        m = p["mesh"]
        print(f"  - [{p['id']:02d}] {p['title']}: {p['filename']} (vol={m.volume:.2f} mm3, vertices={len(m.vertices)})")

    os.makedirs(SUBASSY_DIR, exist_ok=True)
    out_glb = os.path.join(SUBASSY_DIR, "Custom_Base_And_Bottom_Shell_Assembly.glb")

    glb_bytes = export_assembled_glb(parts, out_glb)
    print(f"\n[SUCCESS] Exported: {out_glb} ({len(glb_bytes):,} bytes)")
    print("=" * 80)


if __name__ == "__main__":
    main()
