"""Build and export the complete 3-part assembled GLB from 02_Waist_Mechanism.

This script loads the 3 parts forming the complete Waist Mechanism Assembly:
  1. 07_32_Mid_Shell_P02_Ratchet (Inner rotating 33-lobe waist ratchet ring)
  2. 08_33_Mid_Shell_P01_Outer (Outer waist shell body with tactile ribs)
  3. 09_Custom_Mid_Shell_Spring_33 (3-arm 33-click waist detent leaf spring)

Outputs:
  - Hybrid_Grenade_v1.2/02_Waist_Mechanism/Custom_Waist_Assembly.glb
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
WAIST_DIR = os.path.join(V12_DIR, "02_Waist_Mechanism")

WAIST_PARTS = [
    {
        "id": 7,
        "filename": "07_32_Mid_Shell_P02_Ratchet.stl",
        "name": "07_32_Mid_Shell_P02_Ratchet",
        "title": "Inner 33-Lobe Waist Ratchet Ring (32)",
        "color_rgb": (140, 190, 115),     # Olive Drab Accent
        "metallic": 0.15,
        "roughness": 0.55,
    },
    {
        "id": 8,
        "filename": "08_33_Mid_Shell_P01_Outer.stl",
        "name": "08_33_Mid_Shell_P01_Outer",
        "title": "Outer Waist Shell Body (33)",
        "color_rgb": (122, 181, 102),     # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
    },
    {
        "id": 9,
        "filename": "09_Custom_Mid_Shell_Spring_33.stl",
        "name": "09_Custom_Mid_Shell_Spring_33",
        "title": "Waist Detent Leaf Spring (3-Arm 33-Click)",
        "color_rgb": (255, 125, 40),      # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
]


def load_waist_parts():
    loaded = []
    for info in WAIST_PARTS:
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
    """Export PBR GLB model for the fully assembled waist mechanism."""
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
    print("BUILDING WAIST MECHANISM ASSEMBLED GLB")
    print("=" * 80)

    print("\nLoading 3 waist mechanism components from assembled coordinate space...")
    parts = load_waist_parts()
    for p in parts:
        m = p["mesh"]
        print(f"  - [{p['id']:02d}] {p['title']}: {p['filename']} (vol={m.volume:.2f} mm3)")

    os.makedirs(WAIST_DIR, exist_ok=True)
    out_glb = os.path.join(WAIST_DIR, "Custom_Waist_Assembly.glb")

    glb_bytes = export_assembled_glb(parts, out_glb)
    print(f"\n[SUCCESS] Exported: {out_glb} ({len(glb_bytes):,} bytes)")
    print("=" * 80)


if __name__ == "__main__":
    main()
