"""Build and export Assembled, Exploded, and Cutaway GLB models for the package
named by ``package_paths.PACKAGE_NAME``.

Called by ``export_3d_print_package.py`` via :func:`build_all_glbs`; not a
standalone step in the rebuild order.

Reads every part from ``<PACKAGE_DIR>/All_Parts_Assembled_Coordinates``:
  - 01_Base_And_Bottom_Shell (6 parts)
  - 02_Waist_Mechanism (3 parts)
  - 03_Internal_Barrel_And_Upper_Station (10 parts)
  - 04_Rod_Assembly_And_Locks (6 parts)
  - 05_Folding_Head_And_Spinner (9 parts)

Outputs, into ``<PACKAGE_DIR>``:
  - 3D_Print_Custom_Hybrid_Grenade_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_Exploded.glb
  - 3D_Print_Custom_Hybrid_Grenade_Cutaway.glb
"""
from __future__ import annotations

import io
import os
import sys
import numpy as np
import trimesh
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import assembly as A
import custom
import fidget

if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
from package_paths import PACKAGE_DIR
ASSEMBLED_STLS_DIR = os.path.join(PACKAGE_DIR, "All_Parts_Assembled_Coordinates")

# Comprehensive 36-part specification with PBR Material Properties
PARTS_SPECS = [
    # 01 - Base & Bottom Shell
    {
        "id": 1,
        "name": "01_04_Bottom_Shell_01",
        "file": "01_04_Bottom_Shell_01.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "load_type": "tactical_pose",
        "tactical_key": "04 - Bottom Shell 01",
        "color": (122, 181, 102),  # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, -52.0, 0.0]),
    },
    {
        "id": 2,
        "name": "02_05_Bottom_Shell_02",
        "file": "02_05_Bottom_Shell_02.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "load_type": "tactical_pose",
        "tactical_key": "05 - Bottom Shell 02",
        "color": (122, 181, 102),  # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, -40.0, 0.0]),
    },
    {
        "id": 3,
        "name": "03_06_Bottom_Shell_03",
        "file": "03_06_Bottom_Shell_03.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "load_type": "tactical_pose",
        "tactical_key": "06 - Bottom Shell 03",
        "color": (122, 181, 102),  # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, -28.0, 0.0]),
    },
    {
        "id": 4,
        "name": "04_01_Bottom_Lock_Shell",
        "file": "04_01_Bottom_Lock_Shell.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "load_type": "tactical_pose",
        "tactical_key": "01 - Bottom Lock Shell",
        "color": (65, 75, 85),  # Gunmetal
        "metallic": 0.4,
        "roughness": 0.45,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, -44.0, 0.0]),
    },
    {
        "id": 5,
        "name": "05_02_Bottom_Spring",
        "file": "05_02_Bottom_Spring.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "load_type": "tactical_pose",
        "tactical_key": "02 - Bottom Spring",
        "color": (255, 110, 30),  # Vibrant Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, -32.0, 0.0]),
    },
    {
        "id": 6,
        "name": "06_03_Bottom_Shell_Spacer",
        "file": "06_03_Bottom_Shell_Spacer.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "load_type": "tactical_pose",
        "tactical_key": "03 - Bottom Shell Spacer",
        "color": (80, 90, 100),  # Slate Gunmetal
        "metallic": 0.4,
        "roughness": 0.45,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, -16.0, 0.0]),
    },

    # 02 - Waist Mechanism
    {
        "id": 7,
        "name": "07_32_Mid_Shell_P02_Ratchet",
        "file": "07_32_Mid_Shell_P02_Ratchet.stl",
        "subassembly": "02_Waist_Mechanism",
        "load_type": "tactical_pose",
        "tactical_key": "32 - Mid Shell P02",
        "color": (140, 190, 115),  # Olive Drab Accent
        "metallic": 0.15,
        "roughness": 0.55,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([36.0, 0.0, 0.0]),
    },
    {
        "id": 8,
        "name": "08_33_Mid_Shell_P01_Outer",
        "file": "08_33_Mid_Shell_P01_Outer.stl",
        "subassembly": "02_Waist_Mechanism",
        "load_type": "tactical_pose",
        "tactical_key": "33 - Mid Shell P01",
        "color": (122, 181, 102),  # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([-36.0, 0.0, 0.0]),
    },
    {
        "id": 9,
        "name": "09_Custom_Mid_Shell_Spring_33",
        "file": "09_Custom_Mid_Shell_Spring_33.stl",
        "subassembly": "02_Waist_Mechanism",
        "color": (255, 125, 40),  # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 0.0, 34.0]),
    },

    # 03 - Internal Barrel & Upper Station
    {
        "id": 10,
        "name": "10_Custom_Internal_Barrel_4Slot",
        "file": "10_Custom_Internal_Barrel_4Slot.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "08 - Internal Barrel",
        "color": (55, 65, 75),  # Dark Gunmetal Chassis
        "metallic": 0.35,
        "roughness": 0.45,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, 0.0, 0.0]),  # Base Anchor
    },
    {
        "id": 11,
        "name": "11_Custom_Internal_Barrel_Cap",
        "file": "11_Custom_Internal_Barrel_Cap.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "07 - Internal Barrel Cap",
        "color": (70, 80, 90),  # Gunmetal
        "metallic": 0.35,
        "roughness": 0.45,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, 20.0, 0.0]),
    },
    {
        "id": 12,
        "name": "12_Custom_Rod_Detent_Spring_01",
        "file": "12_Custom_Rod_Detent_Spring_01.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "Custom_Rod_Detent_Spring_01",
        "color": (255, 130, 45),  # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([-44.0, 0.0, 24.0]),
    },
    {
        "id": 13,
        "name": "13_Custom_Rod_Detent_Spring_02",
        "file": "13_Custom_Rod_Detent_Spring_02.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "Custom_Rod_Detent_Spring_02",
        "color": (255, 130, 45),  # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([44.0, 0.0, 24.0]),
    },
    {
        "id": 14,
        "name": "14_Custom_Rod_Detent_Spring_03",
        "file": "14_Custom_Rod_Detent_Spring_03.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "Custom_Rod_Detent_Spring_03",
        "color": (255, 130, 45),  # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([-44.0, 0.0, -24.0]),
    },
    {
        "id": 15,
        "name": "15_Custom_Rod_Detent_Spring_04",
        "file": "15_Custom_Rod_Detent_Spring_04.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "Custom_Rod_Detent_Spring_04",
        "color": (255, 130, 45),  # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([44.0, 0.0, -24.0]),
    },
    {
        "id": 16,
        "name": "16_Custom_Internal_Barrel_Pin_01",
        "file": "16_Custom_Internal_Barrel_Pin_01.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "color": (65, 75, 85),  # Gunmetal / Black
        "metallic": 0.3,
        "roughness": 0.45,
        "is_cutaway_shell": False,
        "disp": np.array([20.0, 56.0, 12.0]),
    },
    {
        "id": 17,
        "name": "17_Custom_Internal_Barrel_Pin_02",
        "file": "17_Custom_Internal_Barrel_Pin_02.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "color": (65, 75, 85),  # Gunmetal / Black
        "metallic": 0.3,
        "roughness": 0.45,
        "is_cutaway_shell": False,
        "disp": np.array([-20.0, 56.0, 12.0]),
    },
    {
        "id": 16,
        "name": "16_Custom_Internal_Barrel_Pin_03",
        "file": "16_Custom_Internal_Barrel_Pin_03.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "color": (65, 75, 85),  # Gunmetal / Black
        "metallic": 0.3,
        "roughness": 0.45,
        "is_cutaway_shell": False,
        "disp": np.array([-20.0, 56.0, -12.0]),
    },
    {
        "id": 17,
        "name": "17_Custom_Internal_Barrel_Pin_04",
        "file": "17_Custom_Internal_Barrel_Pin_04.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "color": (65, 75, 85),  # Gunmetal / Black
        "metallic": 0.3,
        "roughness": 0.45,
        "is_cutaway_shell": False,
        "disp": np.array([20.0, 56.0, -12.0]),
    },
    {
        "id": 18,
        "name": "18_27_Upper_Shell_Top",
        "file": "18_27_Upper_Shell_Top.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "27 - Upper Shell Top",
        "color": (122, 181, 102),  # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, 56.0, 0.0]),
    },
    {
        "id": 19,
        "name": "19_28_Upper_Shell_Gear",
        "file": "19_28_Upper_Shell_Gear.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "28 - Upper Shell Gear",
        "color": (195, 205, 215),  # Knurled Steel Silver
        "metallic": 0.85,
        "roughness": 0.25,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, 32.0, 0.0]),
    },
    {
        "id": 20,
        "name": "20_29_Upper_Shell_Lock_Ring",
        "file": "20_29_Upper_Shell_Lock_Ring.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "29 - Upper Shell Lock Ring",
        "color": (140, 190, 115),  # Olive Drab Accent
        "metallic": 0.15,
        "roughness": 0.55,
        "is_cutaway_shell": True,
        "cut_axis": "z",
        "disp": np.array([0.0, 24.0, 0.0]),
    },
    {
        "id": 21,
        "name": "21_30_Upper_Shell_Rotating_Spring",
        "file": "21_30_Upper_Shell_Rotating_Spring.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "load_type": "tactical_pose",
        "tactical_key": "30 - Upper Shell Rotating Spring",
        "color": (255, 110, 30),  # Safety Orange
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 44.0, 0.0]),
    },

    # 04 - Rod Assembly & Locks
    {
        "id": 22,
        "name": "22_Custom_Rod_Right",
        "file": "22_Custom_Rod_Right.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "color": (75, 85, 95),  # Gunmetal Steel
        "metallic": 0.4,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([24.0, 68.0, 0.0]),
    },
    {
        "id": 23,
        "name": "23_Custom_Rod_Middle",
        "file": "23_Custom_Rod_Middle.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "color": (50, 58, 68),  # Charcoal Black Center Rod
        "metallic": 0.5,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 68.0, 0.0]),
    },
    {
        "id": 24,
        "name": "24_Custom_Rod_Left",
        "file": "24_Custom_Rod_Left.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "color": (75, 85, 95),  # Gunmetal Steel
        "metallic": 0.4,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([-24.0, 68.0, 0.0]),
    },
    {
        "id": 25,
        "name": "25_Custom_Rod_Lock_Upper_06",
        "file": "25_Custom_Rod_Lock_Upper_06.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "color": (230, 50, 50),  # Crimson Red Lock Key
        "metallic": 0.25,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 68.0, 22.0]),
    },
    {
        "id": 26,
        "name": "26_Custom_Rod_Lock_Lower_07",
        "file": "26_Custom_Rod_Lock_Lower_07.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "color": (230, 50, 50),  # Crimson Red Lock Key
        "metallic": 0.25,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 68.0, 22.0]),
    },
    {
        "id": 27,
        "name": "27_Spinner_Lever_08_Rod_Lock",
        "file": "27_Spinner_Lever_08_Rod_Lock.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "color": (60, 70, 80),  # Gunmetal Retainer Disc
        "metallic": 0.45,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 50.0, 0.0]),
    },

    # 05 - Folding Head & Spinner
    {
        "id": 28,
        "name": "28_09_Rod_Spring_Hinge_T_Head",
        "file": "28_09_Rod_Spring_Hinge_T_Head.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (255, 110, 30),  # Safety Orange Hinge Leaf Spring
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 102.0, 0.0]),
    },
    {
        "id": 29,
        "name": "29_Custom_Handle_Left",
        "file": "29_Custom_Handle_Left.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (122, 181, 102),  # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
        "is_cutaway_shell": False,
        "disp": np.array([-32.0, 114.0, 0.0]),
    },
    {
        "id": 30,
        "name": "30_Custom_Handle_Right",
        "file": "30_Custom_Handle_Right.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (122, 181, 102),  # Olive Drab Green
        "metallic": 0.1,
        "roughness": 0.6,
        "is_cutaway_shell": True,
        "cut_axis": "x",
        "disp": np.array([32.0, 114.0, 0.0]),
    },
    {
        "id": 31,
        "name": "31_Custom_Ring_Spinner",
        "file": "31_Custom_Ring_Spinner.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (235, 185, 65),  # Silk Gold / Polished Brass
        "metallic": 0.9,
        "roughness": 0.2,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 114.0, -42.0]),
    },
    {
        "id": 32,
        "name": "32_Spinner_Lever_05_Gear",
        "file": "32_Spinner_Lever_05_Gear.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (200, 210, 220),  # Silk Silver Chrome Gear
        "metallic": 0.85,
        "roughness": 0.25,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 114.0, -26.0]),
    },
    {
        "id": 33,
        "name": "33_Spinner_Lever_04_Spring",
        "file": "33_Spinner_Lever_04_Spring.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (255, 125, 40),  # Safety Orange Clicker Spring
        "metallic": 0.2,
        "roughness": 0.35,
        "is_cutaway_shell": False,
        "disp": np.array([0.0, 114.0, -12.0]),
    },
    {
        "id": 34,
        "name": "34_Custom_16_Handle_Lock_Neck",
        "file": "34_Custom_16_Handle_Lock_Neck.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (230, 50, 50),  # Crimson Red Pin
        "metallic": 0.25,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([44.0, 114.0, -14.0]),
    },
    {
        "id": 35,
        "name": "35_Custom_16_Handle_Lock_Pod",
        "file": "35_Custom_16_Handle_Lock_Pod.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (230, 50, 50),  # Crimson Red Pin
        "metallic": 0.25,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([44.0, 114.0, -28.0]),
    },
    {
        "id": 36,
        "name": "36_15_Handle_Rotating_Lock_D_Pin",
        "file": "36_15_Handle_Rotating_Lock_D_Pin.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "color": (230, 50, 50),  # Crimson Red Keyed D-Pin
        "metallic": 0.25,
        "roughness": 0.4,
        "is_cutaway_shell": False,
        "disp": np.array([-44.0, 114.0, 0.0]),
    },
]


def load_all_posed_parts() -> list[dict]:
    """Load every part from exact global assembled coordinates."""
    loaded_parts = []
    for spec in PARTS_SPECS:
        stl_path = os.path.join(ASSEMBLED_STLS_DIR, spec["file"])
        m = trimesh.load(stl_path, force="mesh", process=True)
        loaded_parts.append({
            "spec": spec,
            "mesh": m,
        })
    return loaded_parts


def attach_pbr_visuals(mesh: trimesh.Trimesh, spec: dict) -> trimesh.Trimesh:
    """Attach high-fidelity PBR material and fallback RGBA vertex/face colors."""
    m = mesh.copy()
    color_rgb = spec["color"]
    rgba_f = [color_rgb[0] / 255.0, color_rgb[1] / 255.0, color_rgb[2] / 255.0, 1.0]
    rgba_byte = list(color_rgb) + [255]

    # Assign face colors for basic viewers
    m.visual = trimesh.visual.ColorVisuals(
        mesh=m,
        face_colors=np.tile(rgba_byte, (len(m.faces), 1)),
    )
    # Assign PBR Material for modern GLTF/GLB engines
    mat = trimesh.visual.material.PBRMaterial(
        name=spec["name"] + "_PBR",
        baseColorFactor=rgba_f,
        metallicFactor=float(spec.get("metallic", 0.2)),
        roughnessFactor=float(spec.get("roughness", 0.5)),
    )
    m.visual.material = mat
    return m


def export_assembled_glb(loaded_parts: list[dict], out_paths: list[str]):
    """Export the fully assembled 36-part model."""
    scene = trimesh.Scene()
    for item in loaded_parts:
        spec = item["spec"]
        mesh = item["mesh"]
        m = attach_pbr_visuals(mesh, spec)
        scene.add_geometry(m, node_name=spec["name"], geom_name=spec["name"])

    glb_bytes = scene.export(file_type="glb")
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(glb_bytes)
        print(f"[ASSEMBLED GLB] Exported -> {path} ({len(glb_bytes):,} bytes)")


def export_exploded_glb(loaded_parts: list[dict], out_paths: list[str]):
    """Export the cleanly separated exploded 36-part model."""
    scene = trimesh.Scene()
    for item in loaded_parts:
        spec = item["spec"]
        mesh = item["mesh"]
        disp = spec["disp"]

        m = mesh.copy()
        m.apply_translation(disp)
        m = attach_pbr_visuals(m, spec)
        scene.add_geometry(m, node_name=spec["name"], geom_name=spec["name"])

    glb_bytes = scene.export(file_type="glb")
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(glb_bytes)
        print(f"[EXPLODED GLB] Exported -> {path} ({len(glb_bytes):,} bytes)")


def export_cutaway_glb(loaded_parts: list[dict], out_paths: list[str]):
    """Export the CAD coronal/sagittal cutaway model exposing all internal mechanisms."""
    box_z_cut = trimesh.creation.box(
        extents=[250.0, 350.0, 150.0],
        transform=trimesh.transformations.translation_matrix([0.0, 50.0, 75.0 + 0.001]),
    )
    box_x_cut = trimesh.creation.box(
        extents=[150.0, 350.0, 250.0],
        transform=trimesh.transformations.translation_matrix([75.0 + 0.001, 50.0, 0.0]),
    )

    scene = trimesh.Scene()
    for item in loaded_parts:
        spec = item["spec"]
        mesh = item["mesh"]

        if spec.get("is_cutaway_shell", False):
            cut_axis = spec.get("cut_axis", "z")
            cutter = box_x_cut if cut_axis == "x" else box_z_cut
            try:
                m_cut = fidget.cut(mesh, cutter)
            except Exception as e:
                print(f"Warning: CSG cut failed for {spec['name']}: {e}, using uncut mesh.")
                m_cut = mesh.copy()
        else:
            m_cut = mesh.copy()

        m_cut = attach_pbr_visuals(m_cut, spec)
        scene.add_geometry(m_cut, node_name=spec["name"], geom_name=spec["name"])

    glb_bytes = scene.export(file_type="glb")
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(glb_bytes)
        print(f"[CUTAWAY GLB] Exported -> {path} ({len(glb_bytes):,} bytes)")


def sync_assembled_stl_files(loaded_parts: list[dict]):
    """Ensure All_Parts_Assembled_Coordinates contains STLs in exact solved global positions."""
    os.makedirs(ASSEMBLED_STLS_DIR, exist_ok=True)
    for item in loaded_parts:
        spec = item["spec"]
        mesh = item["mesh"]
        out_stl = os.path.join(ASSEMBLED_STLS_DIR, spec["file"])
        mesh.export(out_stl)
    print(f"[STL SYNC] Successfully updated {len(loaded_parts)} STLs in {ASSEMBLED_STLS_DIR}")


def build_all_glbs():
    print("=" * 80)
    print("BUILDING 3D_PRINT_CUSTOM_HYBRID_GRENADE ASSEMBLED, EXPLODED & CUTAWAY GLBS")
    print("=" * 80)

    print(f"\n1. Loading and positioning all {len(PARTS_SPECS)} components...")
    loaded_parts = load_all_posed_parts()
    print(f"   Loaded {len(loaded_parts)} parts successfully.")

    # Update Assembled Coordinates folder
    print("\n2. Updating All_Parts_Assembled_Coordinates STLs...")
    sync_assembled_stl_files(loaded_parts)

    # 1. Assembled GLB
    print("\n3. Generating Assembled GLB...")
    assembled_outputs = [
        os.path.join(PACKAGE_DIR, "3D_Print_Custom_Hybrid_Grenade_Assembled.glb"),
    ]
    export_assembled_glb(loaded_parts, assembled_outputs)

    # 2. Exploded GLB
    print("\n4. Generating Exploded GLB...")
    exploded_outputs = [
        os.path.join(PACKAGE_DIR, "3D_Print_Custom_Hybrid_Grenade_Exploded.glb"),
    ]
    export_exploded_glb(loaded_parts, exploded_outputs)

    # 3. Cutaway GLB
    print("\n5. Generating Cutaway GLB...")
    cutaway_outputs = [
        os.path.join(PACKAGE_DIR, "3D_Print_Custom_Hybrid_Grenade_Cutaway.glb"),
    ]
    export_cutaway_glb(loaded_parts, cutaway_outputs)

    print("\n" + "=" * 80)
    print("ALL GLB FILES SUCCESSFULLY CREATED!")
    print("=" * 80)


if __name__ == "__main__":
    build_all_glbs()
