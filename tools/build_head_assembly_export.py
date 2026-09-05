"""Build and export the complete 9-part assembled head GLB from 05_Folding_Head_And_Spinner.

This script loads the 9 parts forming the complete Folding Head & Spinner Assembly:
  1. 28_09_Rod_Spring_Hinge (Hinge detent leaf spring providing 4 fold clicks)
  2. 29_Custom_Handle_Left (Left folding lever cheek with gear journal & ring socket)
  3. 30_Custom_Handle_Right (Right folding lever cheek with flush mating face)
  4. 31_Custom_Ring_Spinner (Slimmed free-spinning center ring - 360 deg)
  5. 32_Spinner_Lever_05_Gear (Outer rim clicker gear - 20 clicks/rev)
  6. 33_Spinner_Lever_04_Spring (Leaf spring inside handle pod driving rim gear clicks)
  7. 34_Custom_16_Handle_Lock_Neck (Lock pin securing folding handle neck)
  8. 35_Custom_16_Handle_Lock_Pod (Lock pin securing folding handle pod)
  9. 36_15_Handle_Rotating_Lock_D_Pin (Keyed D-pin locking hinge rotation to upper rod yoke)

Outputs:
  - Hybrid_Grenade_v1.2/05_Folding_Head_And_Spinner/Custom_Head_Assembly.glb
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
HEAD_DIR = os.path.join(V12_DIR, "05_Folding_Head_And_Spinner")

HEAD_PARTS = [
    {
        "id": 28,
        "filename": "28_09_Rod_Spring_Hinge_T_Head.stl",
        "name": "28_09_Rod_Spring_Hinge_T_Head",
        "title": "T-Head Hinge Detent Leaf Spring (09)",
        "color_rgb": (255, 110, 30),      # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
    },
    {
        "id": 29,
        "filename": "29_Custom_Handle_Left.stl",
        "name": "29_Custom_Handle_Left",
        "title": "Left Folding Lever Cheek",
        "color_rgb": (122, 181, 102),     # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
    },
    {
        "id": 30,
        "filename": "30_Custom_Handle_Right.stl",
        "name": "30_Custom_Handle_Right",
        "title": "Right Folding Lever Cheek",
        "color_rgb": (122, 181, 102),     # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
    },
    {
        "id": 31,
        "filename": "31_Custom_Ring_Spinner.stl",
        "name": "31_Custom_Ring_Spinner",
        "title": "Central Spinner Ring",
        "color_rgb": (235, 185, 65),      # Silk Gold / Brass
        "metallic": 0.9,
        "roughness": 0.2,
    },
    {
        "id": 32,
        "filename": "32_Spinner_Lever_05_Gear.stl",
        "name": "32_Spinner_Lever_05_Gear",
        "title": "Outer Rim Clicker Gear (05)",
        "color_rgb": (200, 210, 220),     # Silk Chrome Silver
        "metallic": 0.85,
        "roughness": 0.25,
    },
    {
        "id": 33,
        "filename": "33_Spinner_Lever_04_Spring.stl",
        "name": "33_Spinner_Lever_04_Spring",
        "title": "Rim Gear Clicker Spring (04)",
        "color_rgb": (255, 125, 40),      # Safety Orange Clicker
        "metallic": 0.2,
        "roughness": 0.35,
    },
    {
        "id": 34,
        "filename": "34_Custom_16_Handle_Lock_Neck.stl",
        "name": "34_Custom_16_Handle_Lock_Neck",
        "title": "Handle Neck Lock Pin (16 Neck)",
        "color_rgb": (230, 50, 50),       # Crimson Red Pin
        "metallic": 0.25,
        "roughness": 0.4,
    },
    {
        "id": 35,
        "filename": "35_Custom_16_Handle_Lock_Pod.stl",
        "name": "35_Custom_16_Handle_Lock_Pod",
        "title": "Handle Pod Lock Pin (16 Pod)",
        "color_rgb": (230, 50, 50),       # Crimson Red Pin
        "metallic": 0.25,
        "roughness": 0.4,
    },
    {
        "id": 36,
        "filename": "36_15_Handle_Rotating_Lock_D_Pin.stl",
        "name": "36_15_Handle_Rotating_Lock_D_Pin",
        "title": "Hinge D-Pin (15 Rotating Lock)",
        "color_rgb": (230, 50, 50),       # Crimson Red Keyed Pin
        "metallic": 0.25,
        "roughness": 0.4,
    },
]


def load_head_parts():
    loaded = []
    for info in HEAD_PARTS:
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
    """Export PBR GLB model for the fully assembled head."""
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
    print("BUILDING FOLDING HEAD & SPINNER ASSEMBLED GLB")
    print("=" * 80)

    print("\nLoading 9 head assembly components from assembled coordinate space...")
    parts = load_head_parts()
    for p in parts:
        m = p["mesh"]
        print(f"  - [{p['id']}] {p['title']}: {p['filename']} (vol={m.volume:.2f} mm3)")

    os.makedirs(HEAD_DIR, exist_ok=True)
    out_glb = os.path.join(HEAD_DIR, "Custom_Head_Assembly.glb")

    glb_bytes = export_assembled_glb(parts, out_glb)
    print(f"\n[SUCCESS] Exported: {out_glb} ({len(glb_bytes):,} bytes)")
    print("=" * 80)


if __name__ == "__main__":
    main()
