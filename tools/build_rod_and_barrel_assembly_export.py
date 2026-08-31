"""Build and export the complete 16-part assembled GLB for the combined
Internal Barrel, Upper Station & Rod Assembly.

Combines:
  - 03_Internal_Barrel_And_Upper_Station (10 parts)
  - 04_Rod_Assembly_And_Locks (6 parts)

Outputs:
  - Hybrid_Grenade_v1.2/Custom_Internal_Barrel_And_Rod_Assembly.glb
  - Hybrid_Grenade_v1.2/Custom_Internal_Barrel_And_Rod_Assembly_Cutaway.glb
  - Hybrid_Grenade_v1.2/Custom_Internal_Barrel_And_Rod_Assembly_Exploded.glb
  - Hybrid_Grenade_v1.2/03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_And_Rod_Assembly.glb
  - Hybrid_Grenade_v1.2/04_Rod_Assembly_And_Locks/Custom_Rod_And_Internal_Barrel_Assembly.glb
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
SUBASSY_03_DIR = os.path.join(V12_DIR, "03_Internal_Barrel_And_Upper_Station")
SUBASSY_04_DIR = os.path.join(V12_DIR, "04_Rod_Assembly_And_Locks")

ASSEMBLY_PARTS = [
    # --- 03 Internal Barrel & Upper Station (10 parts) ---
    {
        "id": 10,
        "filename": "10_Custom_Internal_Barrel_4Slot.stl",
        "name": "10_Custom_Internal_Barrel_4Slot",
        "title": "4-Slot Internal Barrel Chassis (10)",
        "color_rgb": (55, 65, 75),
        "metallic": 0.35,
        "roughness": 0.45,
        "disp": np.array([0.0, 0.0, 0.0]),
    },
    {
        "id": 11,
        "filename": "11_Custom_Internal_Barrel_Cap.stl",
        "name": "11_Custom_Internal_Barrel_Cap",
        "title": "Internal Barrel Retention Cap (11)",
        "color_rgb": (70, 80, 90),
        "metallic": 0.35,
        "roughness": 0.45,
        "disp": np.array([0.0, 8.0, 0.0]),
    },
    {
        "id": 12,
        "filename": "12_Custom_Rod_Detent_Spring_01.stl",
        "name": "12_Custom_Rod_Detent_Spring_01",
        "title": "Axial Rod Detent Spring 01 (az 0°)",
        "color_rgb": (255, 130, 45),
        "metallic": 0.2,
        "roughness": 0.35,
        "disp": np.array([-14.0, 0.0, 0.0]),
    },
    {
        "id": 13,
        "filename": "13_Custom_Rod_Detent_Spring_02.stl",
        "name": "13_Custom_Rod_Detent_Spring_02",
        "title": "Axial Rod Detent Spring 02 (az 90°)",
        "color_rgb": (255, 130, 45),
        "metallic": 0.2,
        "roughness": 0.35,
        "disp": np.array([0.0, 0.0, 14.0]),
    },
    {
        "id": 14,
        "filename": "14_Custom_Rod_Detent_Spring_03.stl",
        "name": "14_Custom_Rod_Detent_Spring_03",
        "title": "Axial Rod Detent Spring 03 (az 180°)",
        "color_rgb": (255, 130, 45),
        "metallic": 0.2,
        "roughness": 0.35,
        "disp": np.array([14.0, 0.0, 0.0]),
    },
    {
        "id": 15,
        "filename": "15_Custom_Rod_Detent_Spring_04.stl",
        "name": "15_Custom_Rod_Detent_Spring_04",
        "title": "Axial Rod Detent Spring 04 (az 270°)",
        "color_rgb": (255, 130, 45),
        "metallic": 0.2,
        "roughness": 0.35,
        "disp": np.array([0.0, 0.0, -14.0]),
    },
    {
        "id": 18,
        "filename": "18_27_Upper_Shell_Top.stl",
        "name": "18_27_Upper_Shell_Top",
        "title": "Upper Shell Top Housing (27)",
        "color_rgb": (122, 181, 102),
        "metallic": 0.1,
        "roughness": 0.6,
        "disp": np.array([0.0, 36.0, 0.0]),
    },
    {
        "id": 19,
        "filename": "19_28_Upper_Shell_Gear.stl",
        "name": "19_28_Upper_Shell_Gear",
        "title": "Upper Shell Clicker Gear (28)",
        "color_rgb": (195, 205, 215),
        "metallic": 0.85,
        "roughness": 0.25,
        "disp": np.array([0.0, 18.0, 0.0]),
    },
    {
        "id": 20,
        "filename": "20_29_Upper_Shell_Lock_Ring.stl",
        "name": "20_29_Upper_Shell_Lock_Ring",
        "title": "Upper Shell Lock Ring (29)",
        "color_rgb": (140, 190, 115),
        "metallic": 0.15,
        "roughness": 0.55,
        "disp": np.array([0.0, 12.0, 0.0]),
    },
    {
        "id": 21,
        "filename": "21_30_Upper_Shell_Rotating_Spring.stl",
        "name": "21_30_Upper_Shell_Rotating_Spring",
        "title": "Upper Shell Rotating Spring (30)",
        "color_rgb": (255, 110, 30),
        "metallic": 0.2,
        "roughness": 0.35,
        "disp": np.array([0.0, 26.0, 0.0]),
    },

    # --- 04 Rod Assembly & Locks (6 parts) ---
    {
        "id": 22,
        "filename": "22_Custom_Rod_Right.stl",
        "name": "22_Custom_Rod_Right",
        "title": "Custom Rod Right Clamp (22)",
        "color_rgb": (86, 182, 178),
        "metallic": 0.25,
        "roughness": 0.4,
        "disp": np.array([-18.0, 0.0, 0.0]),
    },
    {
        "id": 23,
        "filename": "23_Custom_Rod_Middle.stl",
        "name": "23_Custom_Rod_Middle",
        "title": "Custom Rod Middle Core & Yoke (23)",
        "color_rgb": (55, 65, 81),
        "metallic": 0.35,
        "roughness": 0.45,
        "disp": np.array([0.0, 50.0, 0.0]),
    },
    {
        "id": 24,
        "filename": "24_Custom_Rod_Left.stl",
        "name": "24_Custom_Rod_Left",
        "title": "Custom Rod Left Clamp (24)",
        "color_rgb": (184, 126, 152),
        "metallic": 0.25,
        "roughness": 0.4,
        "disp": np.array([18.0, 0.0, 0.0]),
    },
    {
        "id": 25,
        "filename": "25_Custom_Rod_Lock_Upper_06.stl",
        "name": "25_Custom_Rod_Lock_Upper_06",
        "title": "Upper Transverse Cross-Key 06 (25)",
        "color_rgb": (239, 68, 68),
        "metallic": 0.15,
        "roughness": 0.4,
        "disp": np.array([0.0, 0.0, 22.0]),
    },
    {
        "id": 26,
        "filename": "26_Custom_Rod_Lock_Lower_07.stl",
        "name": "26_Custom_Rod_Lock_Lower_07",
        "title": "Lower Transverse Cross-Key 07 (26)",
        "color_rgb": (245, 158, 11),
        "metallic": 0.15,
        "roughness": 0.4,
        "disp": np.array([0.0, 0.0, 22.0]),
    },
    {
        "id": 27,
        "filename": "27_Spinner_Lever_08_Rod_Lock.stl",
        "name": "27_Spinner_Lever_08_Rod_Lock",
        "title": "Bottom Retainer Disc 08 (27)",
        "color_rgb": (16, 185, 129),
        "metallic": 0.2,
        "roughness": 0.4,
        "disp": np.array([0.0, -25.0, 0.0]),
    },
]


def load_assembly_parts():
    loaded = []
    for info in ASSEMBLY_PARTS:
        path = os.path.join(ASY_DIR, info["filename"])
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing assembled source: {path}")
        mesh = trimesh.load(path, force="mesh", process=True)
        loaded.append({
            **info,
            "mesh": mesh,
        })
    return loaded


def export_assembled_glb(parts, output_path):
    """Export fully assembled 16-part GLB with PBR materials."""
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

    glb_bytes = scene_asy.export(file_type="glb")
    with open(output_path, "wb") as f:
        f.write(glb_bytes)
    return glb_bytes


def export_cutaway_glb(parts, output_path):
    """Export sagittal half-cutaway GLB (clipping Z >= 0 on outer housings) to reveal internal rack & springs."""
    scene_cut = trimesh.Scene()
    plane_origin = [0.0, 0.0, 0.0]
    plane_normal = [0.0, 0.0, 1.0]

    for p in parts:
        m = p["mesh"].copy()
        # Cut only outer housings and barrel, keep springs and rod core full
        if p["id"] in [10, 11, 18, 19, 20]:
            try:
                m_cut = trimesh.intersections.slice_mesh_plane(
                    mesh=m,
                    plane_normal=plane_normal,
                    plane_origin=plane_origin,
                    cap=True,
                )
                if m_cut is not None and len(m_cut.vertices) > 0:
                    m = m_cut
            except Exception as e:
                print(f"Warning cutting {p['name']}: {e}")

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
            name=f"mat_cut_{p['id']}",
        )
        m.visual.material = mat
        scene_cut.add_geometry(m, node_name=f"{p['name']}_Cutaway", geom_name=f"{p['name']}_Cutaway")

    glb_bytes = scene_cut.export(file_type="glb")
    with open(output_path, "wb") as f:
        f.write(glb_bytes)
    return glb_bytes


def export_exploded_glb(parts, output_path):
    """Export exploded view GLB with parts displaced along their functional axes."""
    scene_exp = trimesh.Scene()
    for p in parts:
        m = p["mesh"].copy()
        disp = p["disp"]
        m.apply_translation(disp)

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
            name=f"mat_exp_{p['id']}",
        )
        m.visual.material = mat
        scene_exp.add_geometry(m, node_name=f"{p['name']}_Exploded", geom_name=f"{p['name']}_Exploded")

    glb_bytes = scene_exp.export(file_type="glb")
    with open(output_path, "wb") as f:
        f.write(glb_bytes)
    return glb_bytes


def main():
    print("=" * 80)
    print("BUILDING COMBINED INTERNAL BARREL, UPPER STATION & ROD ASSEMBLY GLBs")
    print("=" * 80)

    parts = load_assembly_parts()
    print(f"Loaded {len(parts)} parts:")
    for p in parts:
        m = p["mesh"]
        print(f"  - [{p['id']:02d}] {p['title']:40s} (faces={len(m.faces):5d}, vol={m.volume:8.2f} mm3)")

    out_paths = [
        os.path.join(V12_DIR, "Custom_Internal_Barrel_And_Rod_Assembly.glb"),
        os.path.join(SUBASSY_03_DIR, "Custom_Internal_Barrel_And_Rod_Assembly.glb"),
        os.path.join(SUBASSY_04_DIR, "Custom_Rod_And_Internal_Barrel_Assembly.glb"),
    ]

    print("\n--- Exporting Full Assembled GLBs ---")
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        b = export_assembled_glb(parts, path)
        print(f"  [SUCCESS] {path} ({len(b):,} bytes)")

    cutaway_path = os.path.join(V12_DIR, "Custom_Internal_Barrel_And_Rod_Assembly_Cutaway.glb")
    print("\n--- Exporting Cutaway GLB ---")
    b_cut = export_cutaway_glb(parts, cutaway_path)
    print(f"  [SUCCESS] {cutaway_path} ({len(b_cut):,} bytes)")

    print("\n" + "=" * 80)
    print("COMBINED ASSEMBLY GLBs GENERATED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
