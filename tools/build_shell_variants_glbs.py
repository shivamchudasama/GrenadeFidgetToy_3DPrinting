"""Build and export Assembled GLB models for all Mid Shell variants of the Custom Hybrid Grenade.

Variants:
  0. Baseline (Standard Tactile Ribs - 2-piece) [Assembled, Cutaway, Exploded]
  1. 01_AeroFlow (Softly swept ergonomic ribs - 1-piece) [Assembled]
  2. 02_Vector_Chevron (Sculpted continuous chevrons - 1-piece) [Assembled]
  3. 03_Orbit (Staggered raised traction pods - 1-piece) [Assembled]
  4. 04_Ergo_Scoops (Vertical rails with helical thread cuts - 1-piece) [Assembled]
  5. 05_Contour_Twist (Deep twisted torque flutes - 2-piece dual-color) [Assembled]
  6. 06_Hex_Tactical (Hexagonal knurled solid tactical shell - 1-piece) [Assembled]
  7. 07_Classic_Solid_Tactical (Monolithic 1-piece ribbed tactical shell) [Assembled]

Outputs in 3D_Print_Custom_Hybrid_Grenade/:
  - 3D_Print_Custom_Hybrid_Grenade_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_Cutaway.glb
  - 3D_Print_Custom_Hybrid_Grenade_Exploded.glb
  - 3D_Print_Custom_Hybrid_Grenade_01_AeroFlow_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_02_Vector_Chevron_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_03_Orbit_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_04_Ergo_Scoops_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_05_Contour_Twist_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_06_Hex_Tactical_Assembled.glb
  - 3D_Print_Custom_Hybrid_Grenade_07_Classic_Solid_Tactical_Assembled.glb
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import glob
import numpy as np
import trimesh

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
CODEX_DIR = os.path.join(ROOT_DIR, "Derivatives", "Codex_Professional_Shell_Designs")
FIDGET_TACTICAL_DIR = os.path.join(ROOT_DIR, "Fidget Fuse Tactical 7-in-1 Snap-Fit Fidget Toy")

# Base 36 parts specification (Non-waist parts 1-6 and 10-36 remain identical)
COMMON_PARTS_SPECS = [
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
        "name": "28_09_Rod_Spring_Hinge",
        "file": "28_09_Rod_Spring_Hinge.stl",
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


def get_canonical_transforms():
    """Compute the exact algebraic matrices mapping flat print-oriented mid shells to assembled space."""
    tactical_poses = {r["part"]: r for r in A.poses("tactical")["parts"]}

    # P01 (Outer shell transform)
    raw_p01 = fidget.load("33 - Mid Shell P01", product="tactical")
    c_xy1 = raw_p01.bounds[:, :2].mean(axis=0)
    M_print1 = trimesh.transformations.translation_matrix((-c_xy1[0], -c_xy1[1], -raw_p01.bounds[0, 2]))
    pose1 = np.asarray(tactical_poses["33 - Mid Shell P01"]["matrix"], dtype=float)
    T_outer = pose1 @ np.linalg.inv(M_print1)

    # P02 (Inner ratchet core transform)
    raw_p02 = fidget.load("32 - Mid Shell P02", product="tactical")
    c_xy2 = raw_p02.bounds[:, :2].mean(axis=0)
    M_print2 = trimesh.transformations.translation_matrix((-c_xy2[0], -c_xy2[1], -raw_p02.bounds[0, 2]))
    pose2 = np.asarray(tactical_poses["32 - Mid Shell P02"]["matrix"], dtype=float)
    T_inner = pose2 @ np.linalg.inv(M_print2)

    return T_outer, T_inner


def attach_pbr_visuals(mesh: trimesh.Trimesh, spec: dict) -> trimesh.Trimesh:
    m = mesh.copy()
    color_rgb = spec["color"]
    rgba_f = [color_rgb[0] / 255.0, color_rgb[1] / 255.0, color_rgb[2] / 255.0, 1.0]
    rgba_byte = list(color_rgb) + [255]

    m.visual = trimesh.visual.ColorVisuals(
        mesh=m,
        face_colors=np.tile(rgba_byte, (len(m.faces), 1)),
    )
    mat = trimesh.visual.material.PBRMaterial(
        name=spec["name"] + "_PBR",
        baseColorFactor=rgba_f,
        metallicFactor=float(spec.get("metallic", 0.2)),
        roughnessFactor=float(spec.get("roughness", 0.5)),
    )
    m.visual.material = mat
    return m


def load_common_parts() -> list[dict]:
    loaded = []
    for spec in COMMON_PARTS_SPECS:
        stl_path = os.path.join(ASSEMBLED_STLS_DIR, spec["file"])
        m = trimesh.load(stl_path, force="mesh", process=True)
        loaded.append({"spec": spec, "mesh": m})
    return loaded


# Definition of all variants
VARIANTS = [
    {
        "key": "Baseline",
        "title": "Baseline (Standard Tactile Ribs)",
        "file_suffix": "",  # Standard filenames
        "is_baseline": True,
        "mid_shells": [
            {
                "id": 7,
                "name": "07_32_Mid_Shell_P02_Ratchet",
                "file": "07_32_Mid_Shell_P02_Ratchet.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "tactical_pose",
                "tactical_key": "32 - Mid Shell P02",
                "color": (140, 190, 115),
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
                "load_mode": "tactical_pose",
                "tactical_key": "33 - Mid Shell P01",
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
    {
        "key": "01_AeroFlow",
        "title": "Variant 01 - AeroFlow",
        "file_suffix": "_01_AeroFlow",
        "is_baseline": False,
        "mid_shells": [
            {
                "id": 8,
                "name": "08_Mid_Shell_01_AeroFlow",
                "file": "01_AeroFlow_Mid_Shell.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_outer",
                "stl_path": os.path.join(CODEX_DIR, "01_AeroFlow", "01_AeroFlow_Mid_Shell.stl"),
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
    {
        "key": "02_Vector_Chevron",
        "title": "Variant 02 - Vector Chevron",
        "file_suffix": "_02_Vector_Chevron",
        "is_baseline": False,
        "mid_shells": [
            {
                "id": 8,
                "name": "08_Mid_Shell_02_Vector_Chevron",
                "file": "02_Vector_Chevron_Mid_Shell.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_outer",
                "stl_path": os.path.join(CODEX_DIR, "02_Vector_Chevron", "02_Vector_Chevron_Mid_Shell.stl"),
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
    {
        "key": "03_Orbit",
        "title": "Variant 03 - Orbit",
        "file_suffix": "_03_Orbit",
        "is_baseline": False,
        "mid_shells": [
            {
                "id": 8,
                "name": "08_Mid_Shell_03_Orbit",
                "file": "03_Orbit_Mid_Shell.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_outer",
                "stl_path": os.path.join(CODEX_DIR, "03_Orbit", "03_Orbit_Mid_Shell.stl"),
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
    {
        "key": "04_Ergo_Scoops",
        "title": "Variant 04 - Ergo Scoops",
        "file_suffix": "_04_Ergo_Scoops",
        "is_baseline": False,
        "mid_shells": [
            {
                "id": 8,
                "name": "08_Mid_Shell_04_Ergo_Scoops",
                "file": "04_Ergo_Scoops_Mid_Shell.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_outer",
                "stl_path": os.path.join(CODEX_DIR, "04_Ergo_Scoops", "04_Ergo_Scoops_Mid_Shell.stl"),
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
    {
        "key": "05_Contour_Twist",
        "title": "Variant 05 - Contour Twist",
        "file_suffix": "_05_Contour_Twist",
        "is_baseline": False,
        "mid_shells": [
            {
                "id": 7,
                "name": "07_Mid_Shell_05_Contour_Twist_Inner",
                "file": "05_Contour_Twist_Mid_Shell_Inner.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_inner",
                "stl_path": os.path.join(CODEX_DIR, "05_Contour_Twist", "05_Contour_Twist_Mid_Shell_Inner.stl"),
                "color": (140, 190, 115),
                "metallic": 0.15,
                "roughness": 0.55,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([36.0, 0.0, 0.0]),
            },
            {
                "id": 8,
                "name": "08_Mid_Shell_05_Contour_Twist_Outer",
                "file": "05_Contour_Twist_Mid_Shell_Outer.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_outer",
                "stl_path": os.path.join(CODEX_DIR, "05_Contour_Twist", "05_Contour_Twist_Mid_Shell_Outer.stl"),
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
    {
        "key": "06_Hex_Tactical",
        "title": "Variant 06 - Hex Tactical Solid",
        "file_suffix": "_06_Hex_Tactical",
        "is_baseline": False,
        "mid_shells": [
            {
                "id": 8,
                "name": "08_Mid_Shell_06_Hex_Tactical",
                "file": "08_Mid_Shell_Option_06_Hex_Tactical.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_outer",
                "stl_path": os.path.join(PACKAGE_DIR, "02_Waist_Mechanism", "Mid_Shell_Options", "08_Mid_Shell_Option_06_Hex_Tactical.stl"),
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
    {
        "key": "07_Classic_Solid_Tactical",
        "title": "Variant 07 - Classic Solid Tactical",
        "file_suffix": "_07_Classic_Solid_Tactical",
        "is_baseline": False,
        "mid_shells": [
            {
                "id": 8,
                "name": "08_Mid_Shell_07_Classic_Solid_Tactical",
                "file": "08_Mid_Shell_Option_07_Classic_Solid_Tactical.stl",
                "subassembly": "02_Waist_Mechanism",
                "load_mode": "flat_outer",
                "stl_path": os.path.join(PACKAGE_DIR, "02_Waist_Mechanism", "Mid_Shell_Options", "08_Mid_Shell_Option_07_Classic_Solid_Tactical.stl"),
                "color": (122, 181, 102),
                "metallic": 0.1,
                "roughness": 0.6,
                "is_cutaway_shell": True,
                "cut_axis": "z",
                "disp": np.array([-36.0, 0.0, 0.0]),
            },
        ],
    },
]

# Waist Spring (Common to all variants)
WAIST_SPRING_SPEC = {
    "id": 9,
    "name": "09_Custom_Mid_Shell_Spring_33",
    "file": "09_Custom_Mid_Shell_Spring_33.stl",
    "subassembly": "02_Waist_Mechanism",
    "color": (255, 125, 40),  # Safety Orange
    "metallic": 0.2,
    "roughness": 0.35,
    "is_cutaway_shell": False,
    "disp": np.array([0.0, 0.0, 34.0]),
}


def load_variant_parts(variant: dict, common_loaded: list[dict], T_outer: np.ndarray, T_inner: np.ndarray) -> list[dict]:
    tactical_poses = {r["part"]: r for r in A.poses("tactical")["parts"]}
    all_parts = [p.copy() for p in common_loaded]

    for spec in variant["mid_shells"]:
        mode = spec["load_mode"]
        if mode == "tactical_pose":
            m = A.posed(tactical_poses[spec["tactical_key"]], "tactical")
        elif mode == "flat_outer":
            m = trimesh.load(spec["stl_path"], force="mesh", process=True)
            m.apply_transform(T_outer)
        elif mode == "flat_inner":
            m = trimesh.load(spec["stl_path"], force="mesh", process=True)
            m.apply_transform(T_inner)
        else:
            raise ValueError(f"Unknown mode: {mode}")

        all_parts.append({"spec": spec, "mesh": m})

    m_spring = trimesh.load(os.path.join(ASSEMBLED_STLS_DIR, WAIST_SPRING_SPEC["file"]), force="mesh", process=True)
    all_parts.append({"spec": WAIST_SPRING_SPEC, "mesh": m_spring})

    all_parts.sort(key=lambda x: x["spec"]["id"])
    return all_parts


def export_assembled_glb(parts: list[dict], out_path: str):
    scene = trimesh.Scene()
    for item in parts:
        spec = item["spec"]
        mesh = item["mesh"]
        m = attach_pbr_visuals(mesh, spec)
        scene.add_geometry(m, node_name=spec["name"], geom_name=spec["name"])

    glb_bytes = scene.export(file_type="glb")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(glb_bytes)
    print(f"  [ASSEMBLED] -> {os.path.basename(out_path)} ({len(glb_bytes):,} bytes)")


def export_exploded_glb(parts: list[dict], out_path: str):
    scene = trimesh.Scene()
    for item in parts:
        spec = item["spec"]
        mesh = item["mesh"]
        disp = spec["disp"]

        m = mesh.copy()
        m.apply_translation(disp)
        m = attach_pbr_visuals(m, spec)
        scene.add_geometry(m, node_name=spec["name"], geom_name=spec["name"])

    glb_bytes = scene.export(file_type="glb")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(glb_bytes)
    print(f"  [EXPLODED]  -> {os.path.basename(out_path)} ({len(glb_bytes):,} bytes)")


def export_cutaway_glb(parts: list[dict], out_path: str):
    box_z_cut = trimesh.creation.box(
        extents=[250.0, 350.0, 150.0],
        transform=trimesh.transformations.translation_matrix([0.0, 50.0, 75.0 + 0.001]),
    )
    box_x_cut = trimesh.creation.box(
        extents=[150.0, 350.0, 250.0],
        transform=trimesh.transformations.translation_matrix([75.0 + 0.001, 50.0, 0.0]),
    )

    scene = trimesh.Scene()
    for item in parts:
        spec = item["spec"]
        mesh = item["mesh"]

        if spec.get("is_cutaway_shell", False):
            cut_axis = spec.get("cut_axis", "z")
            cutter = box_x_cut if cut_axis == "x" else box_z_cut
            try:
                m_cut = fidget.cut(mesh, cutter)
            except Exception as e:
                print(f"    Warning: CSG cut failed for {spec['name']}: {e}, using uncut mesh.")
                m_cut = mesh.copy()
        else:
            m_cut = mesh.copy()

        m_cut = attach_pbr_visuals(m_cut, spec)
        scene.add_geometry(m_cut, node_name=spec["name"], geom_name=spec["name"])

    glb_bytes = scene.export(file_type="glb")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(glb_bytes)
    print(f"  [CUTAWAY]   -> {os.path.basename(out_path)} ({len(glb_bytes):,} bytes)")


def cleanup_variant_glbs():
    """Remove Cutaway and Exploded GLB files for the mid shell combinations (keeping baseline)."""
    print("\n[CLEANING UP VARIANT CUTAWAY & EXPLODED GLBS]")
    patterns = [
        os.path.join(PACKAGE_DIR, "3D_Print_Custom_Hybrid_Grenade_*_Cutaway.glb"),
        os.path.join(PACKAGE_DIR, "3D_Print_Custom_Hybrid_Grenade_*_Exploded.glb"),
    ]
    for pattern in patterns:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
                print(f"  Removed: {os.path.basename(f)}")
            except Exception as e:
                print(f"  Error removing {f}: {e}")


def copy_shell_files_to_package():
    """Copy and organize all mid shell STLs into 3D_Print_Custom_Hybrid_Grenade directories."""
    waist_options_dir = os.path.join(PACKAGE_DIR, "02_Waist_Mechanism", "Mid_Shell_Options")
    flat_options_dir = os.path.join(PACKAGE_DIR, "All_Parts_Flat_Bed_Oriented", "Mid_Shell_Options")
    assem_options_dir = os.path.join(PACKAGE_DIR, "All_Parts_Assembled_Coordinates", "Mid_Shell_Options")

    os.makedirs(waist_options_dir, exist_ok=True)
    os.makedirs(flat_options_dir, exist_ok=True)
    os.makedirs(assem_options_dir, exist_ok=True)

    T_outer, T_inner = get_canonical_transforms()

    # 1. Codex 5 Shells
    shells_to_copy = [
        (CODEX_DIR, "01_AeroFlow", "01_AeroFlow_Mid_Shell.stl", "08_Mid_Shell_Option_01_AeroFlow.stl", T_outer, False),
        (CODEX_DIR, "02_Vector_Chevron", "02_Vector_Chevron_Mid_Shell.stl", "08_Mid_Shell_Option_02_Vector_Chevron.stl", T_outer, False),
        (CODEX_DIR, "03_Orbit", "03_Orbit_Mid_Shell.stl", "08_Mid_Shell_Option_03_Orbit.stl", T_outer, False),
        (CODEX_DIR, "04_Ergo_Scoops", "04_Ergo_Scoops_Mid_Shell.stl", "08_Mid_Shell_Option_04_Ergo_Scoops.stl", T_outer, False),
        (CODEX_DIR, "05_Contour_Twist", "05_Contour_Twist_Mid_Shell_Outer.stl", "08_Mid_Shell_Option_05_Contour_Twist_Outer.stl", T_outer, False),
        (CODEX_DIR, "05_Contour_Twist", "05_Contour_Twist_Mid_Shell_Inner.stl", "07_Mid_Shell_Option_05_Contour_Twist_Inner.stl", T_inner, False),
        # 2. Tactical 7-in-1 Shells (need centering from raw build plate)
        (FIDGET_TACTICAL_DIR, "", "Hex Mid Shell Solid Color.stl.stl", "08_Mid_Shell_Option_06_Hex_Tactical.stl", T_outer, True),
        (FIDGET_TACTICAL_DIR, "", "Mid Shell Solid Color.stl.stl", "08_Mid_Shell_Option_07_Classic_Solid_Tactical.stl", T_outer, True),
    ]

    print("\n[COPYING & EXPORTING ALL MID SHELL STLS]")
    for base_dir, sub, src_name, dest_name, T, need_center in shells_to_copy:
        src_path = os.path.join(base_dir, sub, src_name) if sub else os.path.join(base_dir, src_name)
        
        m_raw = trimesh.load(src_path, force="mesh")
        if need_center:
            c_xy = m_raw.bounds[:, :2].mean(axis=0)
            m_flat = m_raw.copy().apply_translation([-c_xy[0], -c_xy[1], -m_raw.bounds[0, 2]])
        else:
            m_flat = m_raw.copy()

        # 1. 02_Waist_Mechanism / Mid_Shell_Options
        dest_waist = os.path.join(waist_options_dir, dest_name)
        m_flat.export(dest_waist)

        # 2. All_Parts_Flat_Bed_Oriented / Mid_Shell_Options
        dest_flat = os.path.join(flat_options_dir, dest_name)
        m_flat.export(dest_flat)

        # 3. All_Parts_Assembled_Coordinates / Mid_Shell_Options
        m_assem = m_flat.copy().apply_transform(T)
        dest_assem = os.path.join(assem_options_dir, dest_name)
        m_assem.export(dest_assem)

        print(f"  Processed {src_name} -> {dest_name} (Flat & Assembled Coordinates)")

    # 2-Color Assembly: GLB for Waist Mechanism Options, 3MF for Plates_3MF
    contour_glb = os.path.join(CODEX_DIR, "05_Contour_Twist", "05_Contour_Twist_Mid_Shell_2Color_Assembly.glb")
    if os.path.exists(contour_glb):
        shutil.copy2(contour_glb, os.path.join(waist_options_dir, "05_Contour_Twist_Mid_Shell_2Color_Assembly.glb"))

    contour_3mf = os.path.join(CODEX_DIR, "05_Contour_Twist", "05_Contour_Twist_Mid_Shell_2Color_Assembly.3mf")
    if os.path.exists(contour_3mf):
        plates_dir = os.path.join(PACKAGE_DIR, "Plates_3MF")
        os.makedirs(plates_dir, exist_ok=True)
        shutil.copy2(contour_3mf, os.path.join(plates_dir, "05_Contour_Twist_Mid_Shell_2Color_Assembly.3mf"))


def build_all_shell_variant_glbs():
    print("=" * 80)
    print("GENERATING ASSEMBLED GLBS FOR ALL MID SHELL VARIANTS & CLEANING UNUSED GLBS")
    print("=" * 80)

    # 1. Copy STLs to package directories
    copy_shell_files_to_package()

    # 2. Clean up non-baseline variant cutaways and exploded GLBs
    cleanup_variant_glbs()

    # 3. Compute transforms
    T_outer, T_inner = get_canonical_transforms()

    # 4. Load common parts once
    print("\nLoading 33 common parts...")
    common_loaded = load_common_parts()
    print(f"Loaded {len(common_loaded)} common parts successfully.")

    # 5. Generate GLBs for each variant
    for var in VARIANTS:
        suffix = var["file_suffix"]
        title = var["title"]
        is_baseline = var.get("is_baseline", False)
        print(f"\n--- Generating GLBs for {title} ---")

        parts = load_variant_parts(var, common_loaded, T_outer, T_inner)

        assembled_file = os.path.join(PACKAGE_DIR, f"3D_Print_Custom_Hybrid_Grenade{suffix}_Assembled.glb")
        export_assembled_glb(parts, assembled_file)

        # Only generate Cutaway & Exploded for Baseline
        if is_baseline:
            cutaway_file = os.path.join(PACKAGE_DIR, f"3D_Print_Custom_Hybrid_Grenade{suffix}_Cutaway.glb")
            exploded_file = os.path.join(PACKAGE_DIR, f"3D_Print_Custom_Hybrid_Grenade{suffix}_Exploded.glb")
            export_cutaway_glb(parts, cutaway_file)
            export_exploded_glb(parts, exploded_file)

    print("\n" + "=" * 80)
    print("ALL GLB FILES SUCCESSFULLY UPDATED!")
    print("=" * 80)


if __name__ == "__main__":
    build_all_shell_variant_glbs()
