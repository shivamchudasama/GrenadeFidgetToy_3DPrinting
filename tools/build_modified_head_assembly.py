"""Build assembled and exploded .glb/.3mf/.stl scenes for the Modified Custom Head.

Uses the pristine modified handle halves and relocated lock pins from:
  Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/

Outputs:
  - Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/Custom_Head_assembled.glb
  - Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/Custom_Head_exploded.glb
  - Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/Custom_Head_assembled.3mf
  - Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/Custom_Head_exploded.3mf
  - Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/Custom_Head_assembled.stl
  - Derivatives/custom/Custom_Head_assembled.glb (updated with modified handles)
  - Derivatives/custom/Custom_Head_exploded.glb (updated with modified handles)
"""
from __future__ import annotations

import os
import sys
import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import assembly as A
import custom
import fidget

MOD_DIR = os.path.join(
    ROOT_DIR, "Derivatives", "custom", "Complete_STL_Set", "Native_Waist_33_Click_Modified"
)
CUSTOM_DIR = os.path.join(ROOT_DIR, "Derivatives", "custom")

# Refined distinct color palette for the 11 head components
HEAD_COLORS = {
    "Custom Hinge Yoke": (86, 182, 178),          # Cyan / Teal
    "Custom Rod Upper Lock": (214, 93, 84),       # Coral Red
    "09 - Rod Spring": (228, 169, 73),            # Amber Gold
    "Custom Handle Left": (93, 150, 209),         # Slate Blue
    "Custom Handle Right": (110, 132, 203),       # Cobalt Blue
    "Custom Ring Spinner": (122, 181, 102),       # Olive Green
    "Spinner Lever 05 - Gear": (219, 124, 171),   # Rose / Magenta
    "Spinner Lever 04 - Spring": (206, 140, 90),  # Terracotta Orange
    "Custom 16 Handle Lock (Neck)": (150, 120, 196),  # Purple
    "Custom 16 Handle Lock (Pod)": (184, 126, 152),   # Mauve
    "15 - Handle Rotating Lock": (160, 168, 74),      # Lime / Khaki
}


def get_modified_head_items() -> list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]:
    """Load and prepare all 11 head components in assembled head coordinates."""
    left = trimesh.load(os.path.join(MOD_DIR, "Custom_Handle_Left.stl"))
    right = trimesh.load(os.path.join(MOD_DIR, "Custom_Handle_Right.stl"))
    ring = trimesh.load(os.path.join(MOD_DIR, "Custom_Ring_Spinner.stl"))
    neck_lock = trimesh.load(os.path.join(MOD_DIR, "Custom_16_Handle_Lock.stl"))
    pod_lock = trimesh.load(os.path.join(MOD_DIR, "Custom_16_Handle_Lock_pod.stl"))
    rot_lock = trimesh.load(os.path.join(MOD_DIR, "15 - Handle Rotating Lock.stl"))
    rod_spring = trimesh.load(os.path.join(MOD_DIR, "09 - Rod Spring.stl"))
    gear = custom.gear_posed()
    spring = custom.gear_spring_arm()
    yoke = custom.hinge_yoke()
    yoke_lock = custom.hinge_yoke_lock()

    raw_items = [
        ("Custom Hinge Yoke", yoke),
        ("Custom Rod Upper Lock", yoke_lock),
        ("09 - Rod Spring", rod_spring),
        ("Custom Handle Left", left),
        ("Custom Handle Right", right),
        ("Custom Ring Spinner", ring),
        ("Spinner Lever 05 - Gear", gear),
        ("Spinner Lever 04 - Spring", spring),
        ("Custom 16 Handle Lock (Neck)", neck_lock),
        ("Custom 16 Handle Lock (Pod)", pod_lock),
        ("15 - Handle Rotating Lock", rot_lock),
    ]

    items = []
    for name, m in raw_items:
        color = HEAD_COLORS.get(name, (180, 180, 180))
        items.append((name, m, color))

    return items


def compute_exploded_displacements(items: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]) -> np.ndarray:
    """Compute an intuitive, symmetric exploded layout for the Head assembly."""
    n = len(items)
    disp = np.zeros((n, 3))
    
    # Names map to indices
    idx = {name: i for i, (name, _, _) in enumerate(items)}
    
    # Axial displacement (along Z - parting axis)
    # Right half & locks spread in +Z direction
    disp[idx["Custom Handle Right"]] = [0.0, 0.0, 22.0]
    disp[idx["Custom 16 Handle Lock (Neck)"]] = [0.0, 0.0, 36.0]
    disp[idx["Custom 16 Handle Lock (Pod)"]] = [0.0, 0.0, 36.0]
    disp[idx["15 - Handle Rotating Lock"]] = [0.0, 0.0, 36.0]
    
    # Left half spreads in -Z direction
    disp[idx["Custom Handle Left"]] = [0.0, 0.0, -22.0]
    
    # Yoke and hinge parts spread downward (-Y direction)
    disp[idx["Custom Hinge Yoke"]] = [0.0, -25.0, 0.0]
    disp[idx["Custom Rod Upper Lock"]] = [-15.0, -25.0, 0.0]
    disp[idx["09 - Rod Spring"]] = [0.0, -10.0, 0.0]
    
    # Gear pawl spring slides outward along its arm direction
    rad, _ = custom._arm_axis()
    disp[idx["Spinner Lever 04 - Spring"]] = [rad[0] * 18.0, rad[1] * 18.0, 0.0]
    
    # Gear moves radially outward at 45 degrees (+X, +Y)
    disp[idx["Spinner Lever 05 - Gear"]] = [18.0, 18.0, 0.0]
    
    # Ring spinner stays at the core center (or slight offset)
    disp[idx["Custom Ring Spinner"]] = [0.0, 0.0, 0.0]
    
    return disp


def build_head_scenes():
    print("=" * 70)
    print("Building Modified Custom Head Assemblies (.glb, .3mf, .stl)")
    print("=" * 70)
    
    items = get_modified_head_items()
    print(f"\nLoaded {len(items)} components for Modified Custom Head Assembly:")
    for name, m, c in items:
        print(f"  - {name:32s} (vol: {m.volume:7.2f} mm3, color: RGB{c})")
        
    disp = compute_exploded_displacements(items)
    
    # 1. Assembled Scene
    scene_assembled = trimesh.Scene()
    for name, m, color in items:
        g = m.copy()
        g.visual.face_colors = np.tile(
            np.array(list(color) + [255], np.uint8), (len(g.faces), 1)
        )
        scene_assembled.add_geometry(g, node_name=name, geom_name=name)
        
    # 2. Exploded Scene
    scene_exploded = trimesh.Scene()
    for i, (name, m, color) in enumerate(items):
        g = m.copy()
        g.apply_translation(disp[i])
        g.visual.face_colors = np.tile(
            np.array(list(color) + [255], np.uint8), (len(g.faces), 1)
        )
        scene_exploded.add_geometry(g, node_name=name, geom_name=name)

    # 3. Export to Native_Waist_33_Click_Modified
    print(f"\n[1/2] Saving to:\n      {MOD_DIR}")
    
    # Assembled GLB, 3MF, STL
    fidget.save(scene_assembled, "Custom_Head_assembled.glb", subdir="custom/Complete_STL_Set/Native_Waist_33_Click_Modified")
    fidget.save(scene_assembled, "Custom_Head_assembled.3mf", subdir="custom/Complete_STL_Set/Native_Waist_33_Click_Modified")
    merged_assembled = trimesh.util.concatenate([g for g in scene_assembled.geometry.values()])
    fidget.save(merged_assembled, "Custom_Head_assembled.stl", subdir="custom/Complete_STL_Set/Native_Waist_33_Click_Modified")
    
    # Exploded GLB, 3MF, STL
    fidget.save(scene_exploded, "Custom_Head_exploded.glb", subdir="custom/Complete_STL_Set/Native_Waist_33_Click_Modified")
    fidget.save(scene_exploded, "Custom_Head_exploded.3mf", subdir="custom/Complete_STL_Set/Native_Waist_33_Click_Modified")
    merged_exploded = trimesh.util.concatenate([g for g in scene_exploded.geometry.values()])
    fidget.save(merged_exploded, "Custom_Head_exploded.stl", subdir="custom/Complete_STL_Set/Native_Waist_33_Click_Modified")
    
    # 4. Also update top-level Derivatives/custom/
    print(f"\n[2/2] Updating top-level Derivatives/custom/ files:")
    fidget.save(scene_assembled, "Custom_Head_assembled.glb", subdir="custom")
    fidget.save(scene_assembled, "Custom_Head_assembled.3mf", subdir="custom")
    fidget.save(merged_assembled, "Custom_Head_assembled.stl", subdir="custom")
    fidget.save(scene_exploded, "Custom_Head_exploded.glb", subdir="custom")
    fidget.save(scene_exploded, "Custom_Head_exploded.3mf", subdir="custom")
    fidget.save(merged_exploded, "Custom_Head_exploded.stl", subdir="custom")
    
    print("\nSuccessfully generated all Modified Custom Head assemblies!")


if __name__ == "__main__":
    build_head_scenes()
