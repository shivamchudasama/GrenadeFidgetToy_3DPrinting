"""Build, validate, and export the combined Custom Rod & Folding Handle Assembly GLB.

Includes:
  From 04_Rod_Assembly_And_Locks/Custom_Rod_Assembly.glb:
    1. Custom Rod Right Clamp (22)
    2. Custom Rod Middle Core (23)
    3. Custom Rod Left Clamp (24)
    4. Upper Transverse Cross-Key 06 (25)
    5. Lower Transverse Cross-Key 07 (26)
    6. Bottom Retainer Disc 08 (27)
  From 05_Folding_Head_And_Spinner:
    7. 28_09_Rod_Spring_Hinge (Hinge detent leaf spring)
    8. 29_Custom_Handle_Left (Left folding lever cheek)
    9. 30_Custom_Handle_Right (Right folding lever cheek)
    10. 34_Custom_16_Handle_Lock_Neck (Neck retention pin)
    11. 36_15_Handle_Rotating_Lock_D_Pin (Keyed rotating D-pin hinge axle)

Outputs:
  - Hybrid_Grenade_v1.2/Custom_Rod_And_Folding_Handle_Assembly.glb
"""
from __future__ import annotations

import base64
import json
import os
import sys
import numpy as np
import trimesh
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
ASY_DIR = os.path.join(V12_DIR, "All_Parts_Assembled_Coordinates")

def to_manifold(mesh: trimesh.Trimesh) -> manifold3d.Manifold:
    return manifold3d.Manifold(manifold3d.Mesh(
        vert_properties=np.ascontiguousarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.ascontiguousarray(mesh.faces, dtype=np.uint32)
    ))

PARTS_SPEC = [
    {
        "id": 22,
        "name": "Custom Rod Right Clamp",
        "file": "22_Custom_Rod_Right.stl",
        "category": "rod",
        "color_rgb": (86, 182, 178),
        "metallic": 0.2,
        "roughness": 0.45,
        "disp": np.array([-20.0, 0.0, 0.0]),
    },
    {
        "id": 23,
        "name": "Custom Rod Middle Core",
        "file": "23_Custom_Rod_Middle.stl",
        "category": "rod",
        "color_rgb": (55, 65, 81),
        "metallic": 0.35,
        "roughness": 0.45,
        "disp": np.array([0.0, 0.0, 0.0]),
    },
    {
        "id": 24,
        "name": "Custom Rod Left Clamp",
        "file": "24_Custom_Rod_Left.stl",
        "category": "rod",
        "color_rgb": (184, 126, 152),
        "metallic": 0.2,
        "roughness": 0.45,
        "disp": np.array([20.0, 0.0, 0.0]),
    },
    {
        "id": 25,
        "name": "Upper Transverse Cross-Key (06)",
        "file": "25_Custom_Rod_Lock_Upper_06.stl",
        "category": "rod",
        "color_rgb": (239, 68, 68),
        "metallic": 0.3,
        "roughness": 0.35,
        "disp": np.array([0.0, 0.0, 22.0]),
    },
    {
        "id": 26,
        "name": "Lower Transverse Cross-Key (07)",
        "file": "26_Custom_Rod_Lock_Lower_07.stl",
        "category": "rod",
        "color_rgb": (245, 158, 11),
        "metallic": 0.3,
        "roughness": 0.35,
        "disp": np.array([0.0, 0.0, 22.0]),
    },
    {
        "id": 27,
        "name": "Bottom Retainer Disc (08)",
        "file": "27_Spinner_Lever_08_Rod_Lock.stl",
        "category": "rod",
        "color_rgb": (16, 185, 129),
        "metallic": 0.4,
        "roughness": 0.35,
        "disp": np.array([0.0, -22.0, 0.0]),
    },
    {
        "id": 28,
        "name": "28_09_Rod_Spring_Hinge",
        "file": "28_09_Rod_Spring_Hinge.stl",
        "category": "hinge",
        "color_rgb": (255, 110, 30),
        "metallic": 0.2,
        "roughness": 0.35,
        "disp": np.array([0.0, 28.0, 0.0]),
    },
    {
        "id": 29,
        "name": "29_Custom_Handle_Left",
        "file": "29_Custom_Handle_Left.stl",
        "category": "handle",
        "color_rgb": (122, 181, 102),
        "metallic": 0.1,
        "roughness": 0.55,
        "disp": np.array([-26.0, 18.0, -12.0]),
    },
    {
        "id": 30,
        "name": "30_Custom_Handle_Right",
        "file": "30_Custom_Handle_Right.stl",
        "category": "handle",
        "color_rgb": (122, 181, 102),
        "metallic": 0.1,
        "roughness": 0.55,
        "disp": np.array([26.0, 18.0, -12.0]),
    },
    {
        "id": 34,
        "name": "34_Custom_16_Handle_Lock_Neck",
        "file": "34_Custom_16_Handle_Lock_Neck.stl",
        "category": "handle",
        "color_rgb": (230, 50, 50),
        "metallic": 0.25,
        "roughness": 0.4,
        "disp": np.array([0.0, 14.0, -32.0]),
    },
    {
        "id": 36,
        "name": "36_15_Handle_Rotating_Lock_D_Pin",
        "file": "36_15_Handle_Rotating_Lock_D_Pin.stl",
        "category": "hinge",
        "color_rgb": (217, 56, 30),
        "metallic": 0.35,
        "roughness": 0.35,
        "disp": np.array([-36.0, 0.0, 0.0]),
    },
]

def load_all_parts():
    loaded = []
    for spec in PARTS_SPEC:
        p_path = os.path.join(ASY_DIR, spec["file"])
        if not os.path.exists(p_path):
            raise FileNotFoundError(f"Missing file: {p_path}")
        m = trimesh.load(p_path, force="mesh", process=True)
        loaded.append({
            **spec,
            "mesh": m
        })
    return loaded

def export_pbr_scene(parts, out_path, exploded=False, cutaway=False):
    scene = trimesh.Scene()
    
    for p in parts:
        m = p["mesh"].copy()
        
        if cutaway:
            # Coronal cutaway plane at Z=0 for positive Z to expose interior spring slot
            # Keep parts if they cross or remain, cut front half (Z > 0)
            # We cut with box Z in [0, 50] for rod parts to expose interior
            if p["category"] in ["rod"] and p["name"] != "Custom Rod Middle Core":
                # Only cut the clamps to expose middle core & spring
                if "Left" in p["name"]:
                    continue  # suppress left clamp in cutaway to see right into cavity
            elif p["category"] == "handle":
                if "Right" in p["name"]:
                    continue  # suppress right cheek to see inside hinge
        
        if exploded:
            m.apply_translation(p["disp"])
            
        r, g, b = p["color_rgb"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        rgba_byte = list(p["color_rgb"]) + [255]
        
        m.visual = trimesh.visual.ColorVisuals(
            mesh=m,
            face_colors=np.tile(rgba_byte, (len(m.faces), 1))
        )
        mat = trimesh.visual.material.PBRMaterial(
            baseColorFactor=color_norm,
            metallicFactor=float(p["metallic"]),
            roughnessFactor=float(p["roughness"]),
            name=f"mat_{p['id']}"
        )
        m.visual.material = mat
        scene.add_geometry(m, node_name=p["name"], geom_name=p["name"])
        
    glb_bytes = scene.export(file_type="glb")
    with open(out_path, "wb") as f:
        f.write(glb_bytes)
    return glb_bytes

def main():
    print("=" * 80)
    print("BUILDING CUSTOM ROD & FOLDING HANDLE COMBINED ASSEMBLY")
    print("=" * 80)
    
    parts = load_all_parts()
    print(f"Loaded {len(parts)} precision parts in Assembled Coordinate Space.")
    
    print("\n[1/4] Manifold Pairwise Interference Checks...")
    manifolds = [to_manifold(p["mesh"]) for p in parts]
    collisions = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            vol = (manifolds[i] ^ manifolds[j]).volume()
            if vol > 1e-4:
                collisions.append((parts[i]["name"], parts[j]["name"], vol))
                print(f"  [!] COLLISION: {parts[i]['name']} vs {parts[j]['name']} = {vol:.4f} mm3")
            else:
                pass
    if len(collisions) == 0:
        print("  [SUCCESS] PERFECT 100% COLLISION FREE: 0.0000 mm3 across all pairs!")
    else:
        print(f"  [WARN] Total collisions detected: {len(collisions)}")
        
    print("\n[2/2] Exporting Primary Assembled GLB...")
    out_glb_root = os.path.join(V12_DIR, "Custom_Rod_And_Folding_Handle_Assembly.glb")
    b_asy = export_pbr_scene(parts, out_glb_root, exploded=False, cutaway=False)
    print(f"  Exported Assembled GLB -> {out_glb_root} ({len(b_asy):,} bytes)")

    print("\nAssembly generation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
