"""Export every part of the Native Tactical/Spinner Hybrid Grenade Fidget Toy for 3D printing.

This package uses the original Tactical Internal Barrel & Upper Station mechanism
and the solid-yoke 3-piece rod assembly (joined by transverse 06 & 07 cross-keys and
08 bottom retainer, with NO upper wedge lock).

Output directory:
  3D_Print_Custom_Hybrid_Grenade/
    ├── 01_Base_And_Bottom_Shell/               (6 STLs)
    ├── 02_Waist_Mechanism/                     (3 STLs)
    ├── 03_Internal_Barrel_And_Upper_Station/   (10 STLs - 4-slot barrel & detent springs)
    ├── 04_Rod_Assembly_And_Locks/              (6 STLs - Solid Yoke Rod & Cross Keys)
    ├── 05_Folding_Head_And_Spinner/            (9 STLs - Folding Cheeks, Gear, Spinner Ring & Pins)
    ├── All_Parts_Flat_Bed_Oriented/            (pre-oriented flat on Z=0, centered at (0,0))
    ├── All_Parts_Assembled_Coordinates/        (exact global solved assembly space)
    ├── Plates_3MF/                             (Multi-part 3MF project plates)
    └── README_3D_PRINTING.md                   (Complete BOM & Assembly Manual)
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import numpy as np
import trimesh
import manifold3d

from package_paths import (ROOT_DIR, TOOLS_DIR, PACKAGE_DIR, ASSEMBLED_SUBDIR,
                           ASSEMBLED_DIR, guard)

OUTPUT_DIR = PACKAGE_DIR
ASSEMBLED_STLS_DIR = ASSEMBLED_DIR

# Rebuilt from scratch on every run.  ASSEMBLED_SUBDIR is deliberately absent:
# it is the input, and 02_Waist_Mechanism/Mid_Shell_Options plus the two other
# Mid_Shell_Options folders are refilled afterwards by build_shell_variants_glbs.
_DERIVED_SUBDIRS = [
    "01_Base_And_Bottom_Shell",
    "02_Waist_Mechanism",
    "03_Internal_Barrel_And_Upper_Station",
    "04_Rod_Assembly_And_Locks",
    "05_Folding_Head_And_Spinner",
    "All_Parts_Flat_Bed_Oriented",
    "Plates_3MF",
]

PARTS_MANIFEST = [
    # 01 - Base & Bottom Shell
    {
        "id": 1,
        "source_file": "04 - Bottom Shell 01.stl",
        "export_filename": "01_04_Bottom_Shell_01.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Olive Drab Green",
        "desc": "Outer bottom shell tier 1",
        "supports": "No",
    },
    {
        "id": 2,
        "source_file": "05 - Bottom Shell 02.stl",
        "export_filename": "02_05_Bottom_Shell_02.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Olive Drab Green",
        "desc": "Outer bottom shell tier 2",
        "supports": "No",
    },
    {
        "id": 3,
        "source_file": "06 - Bottom Shell 03.stl",
        "export_filename": "03_06_Bottom_Shell_03.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Olive Drab Green",
        "desc": "Outer bottom shell tier 3",
        "supports": "No",
    },
    {
        "id": 4,
        "source_file": "01 - Bottom Lock Shell.stl",
        "export_filename": "04_01_Bottom_Lock_Shell.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Black / Gunmetal",
        "desc": "Inner bottom retaining lock cylinder",
        "supports": "No",
    },
    {
        "id": 5,
        "source_file": "02 - Bottom Spring.stl",
        "export_filename": "05_02_Bottom_Spring.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Bottom compression flexure spring",
        "supports": "No",
    },
    {
        "id": 6,
        "source_file": "03 - Bottom Shell Spacer.stl",
        "export_filename": "06_03_Bottom_Shell_Spacer.stl",
        "subassembly": "01_Base_And_Bottom_Shell",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Black / Gunmetal",
        "desc": "Spacer ring sealing bottom spring pocket",
        "supports": "No",
    },

    # 02 - Waist Mechanism
    {
        "id": 7,
        "source_file": "32 - Mid Shell P02.stl",
        "export_filename": "07_32_Mid_Shell_P02_Ratchet.stl",
        "subassembly": "02_Waist_Mechanism",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Olive Drab Green",
        "desc": "Inner rotating 33-lobe waist ratchet ring",
        "supports": "No",
    },
    {
        "id": 8,
        "source_file": "33 - Mid Shell P01.stl",
        "export_filename": "08_33_Mid_Shell_P01_Outer.stl",
        "subassembly": "02_Waist_Mechanism",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Olive Drab Green",
        "desc": "Outer waist shell body with tactile ribs",
        "supports": "No",
    },
    {
        "id": 9,
        "source_file": "Custom_Mid_Shell_Spring_33.stl",
        "export_filename": "09_Custom_Mid_Shell_Spring_33.stl",
        "subassembly": "02_Waist_Mechanism",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "3-arm 33-click waist detent leaf spring",
        "supports": "No",
    },

    # 03 - Tactical Internal Barrel & Upper Station
    {
        "id": 10,
        "source_file": "Custom_Internal_Barrel_4Slot.stl",
        "export_filename": "10_Custom_Internal_Barrel_4Slot.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Black / Gunmetal",
        "desc": "Barrel spine: 4 spring slots at 0/90/180/270, pin channels filled",
        "supports": "No",
    },
    {
        "id": 11,
        "source_file": "11_Custom_Internal_Barrel_Cap.stl",
        "export_filename": "11_Custom_Internal_Barrel_Cap.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Black / Gunmetal",
        "desc": "Slotted barrel top cap with 3.60 mm pass-through channels at 90° and 270°",
        "supports": "No",
    },
    {
        "id": 12,
        "source_file": "12_Custom_Rod_Detent_Spring_01.stl",
        "export_filename": "12_Custom_Rod_Detent_Spring_01.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Single-headed axial rod detent spring 01 (az 0°), rides rod rack -- build_dual_headed_springs.py",
        "supports": "No",
    },
    {
        "id": 13,
        "source_file": "13_Custom_Rod_Detent_Spring_02.stl",
        "export_filename": "13_Custom_Rod_Detent_Spring_02.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Dual-headed axial rod detent spring 02 (az 90°), dual rack engagement -- build_dual_headed_springs.py",
        "supports": "No",
    },
    {
        "id": 14,
        "source_file": "14_Custom_Rod_Detent_Spring_03.stl",
        "export_filename": "14_Custom_Rod_Detent_Spring_03.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Single-headed axial rod detent spring 03 (az 180°), rides rod rack -- build_dual_headed_springs.py",
        "supports": "No",
    },
    {
        "id": 15,
        "source_file": "15_Custom_Rod_Detent_Spring_04.stl",
        "export_filename": "15_Custom_Rod_Detent_Spring_04.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Dual-headed axial rod detent spring 04 (az 270°), dual rack engagement -- build_dual_headed_springs.py",
        "supports": "No",
    },
    {
        "id": 18,
        "source_file": "27 - Upper Shell Top.stl",
        "export_filename": "18_27_Upper_Shell_Top.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Olive Drab Green",
        "desc": "Original Tactical upper top housing shell",
        "supports": "No",
    },
    {
        "id": 19,
        "source_file": "28 - Upper Shell Gear.stl",
        "export_filename": "19_28_Upper_Shell_Gear.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Silver / Gunmetal",
        "desc": "Original Tactical rotating upper knurled gear",
        "supports": "No",
    },
    {
        "id": 20,
        "source_file": "29 - Upper Shell Lock Ring.stl",
        "export_filename": "20_29_Upper_Shell_Lock_Ring.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_1_Base_And_Shells",
        "color": "Olive Drab Green",
        "desc": "Original upper shell lock ring",
        "supports": "No",
    },
    {
        "id": 21,
        "source_file": "30 - Upper Shell Rotating Spring.stl",
        "export_filename": "21_30_Upper_Shell_Rotating_Spring.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Original upper rotating clicker spring",
        "supports": "No",
    },

    # 04 - Rod Assembly & Locks (Solid Yoke, Full-Height Hex-Keyed Side Clamps, 06 & 07 Cross-keys, 08 Bottom Retainer)
    {
        "id": 22,
        "source_file": "Custom_Rod_Right.stl",
        "export_filename": "22_Custom_Rod_Right.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Black / Gunmetal",
        "desc": "Full-height right rod member with integral upper hexagonal key & right spring pod wall",
        "supports": "No",
    },
    {
        "id": 23,
        "source_file": "Custom_Rod_Middle.stl",
        "export_filename": "23_Custom_Rod_Middle.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Black / Gunmetal",
        "desc": "Full-depth middle rod with integral solid hinge yoke, enclosed spring pocket, and transverse key tunnels",
        "supports": "Minimal (under yoke)",
    },
    {
        "id": 24,
        "source_file": "Custom_Rod_Left.stl",
        "export_filename": "24_Custom_Rod_Left.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Black / Gunmetal",
        "desc": "Full-height left rod member with integral upper hexagonal key & left spring pod wall",
        "supports": "No",
    },
    {
        "id": 25,
        "source_file": "Custom_Rod_Lock_Upper_06.stl",
        "export_filename": "25_Custom_Rod_Lock_Upper_06.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Safety Orange / Red",
        "desc": "Upper transverse cross-key joining the 3 rod members",
        "supports": "No",
    },
    {
        "id": 26,
        "source_file": "Custom_Rod_Lock_Lower_07.stl",
        "export_filename": "26_Custom_Rod_Lock_Lower_07.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Safety Orange / Red",
        "desc": "Lower transverse cross-key joining the 3 rod members",
        "supports": "No",
    },
    {
        "id": 27,
        "source_file": "Spinner Lever 08 - Rod Lock.stl",
        "export_filename": "27_Spinner_Lever_08_Rod_Lock.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Black / Gunmetal",
        "desc": "Slotted bottom axial retainer disc locking onto middle rod taper",
        "supports": "No",
    },

    # 05 - Folding Head, Spinner & Pins
    {
        "id": 28,
        "source_file": "09 - Rod Spring.stl",
        "export_filename": "28_09_Rod_Spring_Hinge.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Safety Orange / PETG",
        "desc": "Hinge detent leaf spring providing 4 fold clicks (0°, 30°, 60°, 90°)",
        "supports": "No",
    },
    {
        "id": 29,
        "source_file": "Custom_Handle_Left.stl",
        "export_filename": "29_Custom_Handle_Left.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Olive Drab Green",
        "desc": "Left folding lever cheek with gear journal & ring socket",
        "supports": "No",
    },
    {
        "id": 30,
        "source_file": "Custom_Handle_Right.stl",
        "export_filename": "30_Custom_Handle_Right.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Olive Drab Green",
        "desc": "Right folding lever cheek",
        "supports": "No",
    },
    {
        "id": 31,
        "source_file": "Custom_Ring_Spinner.stl",
        "export_filename": "31_Custom_Ring_Spinner.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Silk PLA (Gold / Brass)",
        "desc": "Slimmed free-spinning center ring (360° continuous spin)",
        "supports": "No",
    },
    {
        "id": 32,
        "source_file": "Spinner Lever 05 - Gear.stl",
        "export_filename": "32_Spinner_Lever_05_Gear.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Silk PLA (Silver / Metallic)",
        "desc": "Outer rim clicker gear (20 clicks per revolution)",
        "supports": "No",
    },
    {
        "id": 33,
        "source_file": "Spinner Lever 04 - Spring.stl",
        "export_filename": "33_Spinner_Lever_04_Spring.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Safety Orange / PETG",
        "desc": "Leaf spring inside handle pod driving rim gear clicks",
        "supports": "No",
    },
    {
        "id": 34,
        "source_file": "Custom_16_Handle_Lock.stl",
        "export_filename": "34_Custom_16_Handle_Lock_Neck.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Safety Orange / Red",
        "desc": "Lock pin securing folding handle neck",
        "supports": "No",
    },
    {
        "id": 35,
        "source_file": "Custom_16_Handle_Lock_pod.stl",
        "export_filename": "35_Custom_16_Handle_Lock_Pod.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Safety Orange / Red",
        "desc": "Lock pin securing folding handle pod",
        "supports": "No",
    },
    {
        "id": 36,
        "source_file": "15 - Handle Rotating Lock.stl",
        "export_filename": "36_15_Handle_Rotating_Lock_D_Pin.stl",
        "subassembly": "05_Folding_Head_And_Spinner",
        "plate": "Plate_4_Head_And_Spinner",
        "color": "Safety Orange / Red",
        "desc": "Keyed D-pin locking hinge rotation to the upper rod yoke",
        "supports": "No",
    },
]


def _roty(deg):
    """Proper rotation about the toy's vertical axis."""
    t = np.radians(float(deg))
    c, sn = np.cos(t), np.sin(t)
    return np.array([[c, 0.0, sn], [0.0, 1.0, 0.0], [-sn, 0.0, c]])


# Flat-bed print pose, one entry per part.
#
# The assembled STLs are in toy coordinates -- Y up, axis at X = Z = 0 -- and
# most parts are seated at some azimuth about Y.  A flat-bed file has to undo
# that seating and stand the part on the plate with Z up, and *which* face goes
# down is a per-part decision, not one global rotation.  Centring on the bed
# alone (what this script used to do) leaves two thirds of the set standing on
# edge.
#
# Each entry is (base, y_degrees) and means R = base @ Ry(y_degrees): turn the
# part about Y to cancel its seating, then map toy axes onto plate axes.
# _center_on_bed() then drops it to Z = 0 and centres it in XY.
#
# Recovered by registering every assembled mesh onto its checked-in flat-bed
# twin (Kabsch over matched vertices).  All 36 reproduce to 2.4e-5 mm; 35 of
# them decompose to a whole number of degrees about Y.
BED_POSES = {
    "01_04_Bottom_Shell_01.stl": ([[1, 0, 0], [0, 0, -1], [0, 1, 0]], 24),
    "02_05_Bottom_Shell_02.stl": ([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], 60),
    "03_06_Bottom_Shell_03.stl": ([[-1, 0, 0], [0, 0, -1], [0, -1, 0]], 60),
    "04_01_Bottom_Lock_Shell.stl": ([[1, 0, 0], [0, 0, -1], [0, 1, 0]], 66),
    "05_02_Bottom_Spring.stl": ([[1, 0, 0], [0, 0, -1], [0, 1, 0]], 66),
    "06_03_Bottom_Shell_Spacer.stl": ([[1, 0, 0], [0, 0, -1], [0, 1, 0]], 66),
    "07_32_Mid_Shell_P02_Ratchet.stl": ([[1, 0, 0], [0, 0, -1], [0, 1, 0]], 38),
    "08_33_Mid_Shell_P01_Outer.stl": ([[0, 0, -1], [1, 0, 0], [0, -1, 0]], 2),
    "09_Custom_Mid_Shell_Spring_33.stl": ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 0),
    "10_Custom_Internal_Barrel_4Slot.stl": ([[1, 0, 0], [0, 0, 1], [0, -1, 0]], 0),
    "11_Custom_Internal_Barrel_Cap.stl": ([[0, 0, 1], [-1, 0, 0], [0, -1, 0]], 30),
    # the four springs are one solid at four azimuths, so they share a base and
    # differ only by the turn that cancels their seating
    # planar parts: lay the profile on the bed with the 3.75 mm width up the Z
    # axis, then cancel each one's seating with Ry(90 - azimuth)
    "12_Custom_Rod_Detent_Spring_01.stl": ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], 90),
    "13_Custom_Rod_Detent_Spring_02.stl": ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], 0),
    "14_Custom_Rod_Detent_Spring_03.stl": ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], -90),
    "15_Custom_Rod_Detent_Spring_04.stl": ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], -180),
    "18_27_Upper_Shell_Top.stl": ([[-1, 0, 0], [0, 0, -1], [0, -1, 0]], 60),
    "19_28_Upper_Shell_Gear.stl": ([[0, 0, 1], [1, 0, 0], [0, 1, 0]], 62),
    "20_29_Upper_Shell_Lock_Ring.stl": ([[1, 0, 0], [0, 0, 1], [0, -1, 0]], 60),
    "21_30_Upper_Shell_Rotating_Spring.stl": ([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], 30),
    "22_Custom_Rod_Right.stl": ([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], 0),
    "23_Custom_Rod_Middle.stl": ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 0),
    "24_Custom_Rod_Left.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    "25_Custom_Rod_Lock_Upper_06.stl": ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 0),
    "26_Custom_Rod_Lock_Lower_07.stl": ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 0),
    "27_Spinner_Lever_08_Rod_Lock.stl": ([[0, 0, 1], [1, 0, 0], [0, 1, 0]], 0),
    "28_09_Rod_Spring_Hinge.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    "29_Custom_Handle_Left.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    "30_Custom_Handle_Right.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    "31_Custom_Ring_Spinner.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    "32_Spinner_Lever_05_Gear.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    # compound head-module pose; no whole-degree Y decomposition
    "33_Spinner_Lever_04_Spring.stl": ([[-3.18962461979967e-10, 0.0697564853123495, -0.997564049450895], [-9.26299647068396e-11, 0.997564049450895, 0.0697564853123497], [1, 1.14654136882141e-10, -3.11724234885343e-10]], 0),
    "34_Custom_16_Handle_Lock_Neck.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    "35_Custom_16_Handle_Lock_Pod.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
    "36_15_Handle_Rotating_Lock_D_Pin.stl": ([[0, 0, -1], [0, 1, 0], [1, 0, 0]], 0),
}


def _to_bed_pose(mesh, export_filename):
    """Turn an assembled-coordinate part into its flat-bed print pose."""
    pose = BED_POSES.get(export_filename)
    if pose is None:
        raise KeyError(
            "no flat-bed pose recorded for %s -- add one to BED_POSES, or the "
            "part will be exported standing on edge" % export_filename)
    base, y_deg = pose
    T = np.eye(4)
    T[:3, :3] = np.asarray(base, dtype=float) @ _roty(y_deg)
    out = mesh.copy()
    out.apply_transform(T)
    return out


def _center_on_bed(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Center mesh in XY and set Z_min = 0 for clean build plate placement."""
    m = mesh.copy()
    center_xy = (m.bounds[0][:2] + m.bounds[1][:2]) / 2.0
    z_min = m.bounds[0][2]
    m.apply_translation([-center_xy[0], -center_xy[1], -z_min])
    return m


def _stl_safe(mesh: trimesh.Trimesh, label: str) -> trimesh.Trimesh:
    """Ensure watertight single-body mesh with manifold repair if needed."""
    payload = trimesh.exchange.stl.export_stl(mesh)
    candidate = trimesh.load_mesh(io.BytesIO(payload), file_type="stl", process=True)
    if candidate.is_watertight and candidate.body_count == 1:
        return candidate

    source = manifold3d.Mesh64(
        np.ascontiguousarray(candidate.vertices, dtype=np.float64),
        np.ascontiguousarray(candidate.faces, dtype=np.uint64),
        tolerance=1e-5,
    )
    source.merge()
    solid = manifold3d.Manifold(source)
    if solid.is_empty():
        raise RuntimeError("manifold STL repair failed for %s" % label)
    rebuilt = solid.to_mesh64()
    safe = trimesh.Trimesh(
        vertices=np.asarray(rebuilt.vert_properties)[:, :3],
        faces=np.asarray(rebuilt.tri_verts),
        process=False,
    )
    return safe


def export_complete_package():
    print(f"Cleaning and preparing output folder: {OUTPUT_DIR}")
    # All_Parts_Assembled_Coordinates is this script's *input*, not its output --
    # it is the checked-in solved assembly and lives inside OUTPUT_DIR.  Clearing
    # the whole tree deletes the sources before they are read back below.
    for sd in _DERIVED_SUBDIRS:
        path = guard(os.path.join(OUTPUT_DIR, sd))
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for sd in _DERIVED_SUBDIRS + [ASSEMBLED_SUBDIR]:
        os.makedirs(os.path.join(OUTPUT_DIR, sd), exist_ok=True)

    print(f"Processing {len(PARTS_MANIFEST)} native parts from {ASSEMBLED_STLS_DIR}...")
    flat_parts_by_plate = {}

    for item in PARTS_MANIFEST:
        src_path = os.path.join(ASSEMBLED_STLS_DIR, item["export_filename"])
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Source file missing: {src_path}")

        mesh = trimesh.load(src_path, force="mesh", process=True)
        mesh = _stl_safe(mesh, item["export_filename"])

        # 2. Bed-Oriented (print pose, centered XY, placed on Z=0)
        flat_mesh = _center_on_bed(_to_bed_pose(mesh, item["export_filename"]))
        flat_mesh = _stl_safe(flat_mesh, item["source_file"])

        # Export into category subassembly
        sub_path = guard(os.path.join(OUTPUT_DIR, item["subassembly"], item["export_filename"]))
        flat_mesh.export(sub_path)

        # Export into All_Parts_Flat_Bed_Oriented
        all_flat_path = guard(os.path.join(OUTPUT_DIR, "All_Parts_Flat_Bed_Oriented", item["export_filename"]))
        flat_mesh.export(all_flat_path)

        # Collect for 3MF build plates
        plate_name = item["plate"]
        if plate_name not in flat_parts_by_plate:
            flat_parts_by_plate[plate_name] = []
        flat_parts_by_plate[plate_name].append((item, flat_mesh))

    print("Generating Multi-Part 3MF Build Plates...")
    _export_3mf_plates(flat_parts_by_plate)

    print("Generating Assembled, Exploded & Cutaway GLB 3D Models...")
    try:
        import build_custom_hybrid_package_glbs as BGLB
        BGLB.build_all_glbs()
    except Exception as e:
        print(f"Warning: GLB generation error: {e}")

    print("Writing Comprehensive README_3D_PRINTING.md...")
    _write_readme()

    print("\n[SUCCESS] All %d parts and GLB models exported successfully!"
          % len(PARTS_MANIFEST))



def _export_3mf_plates(flat_parts_by_plate):
    plates_dir = guard(os.path.join(OUTPUT_DIR, "Plates_3MF"))

    # Individual Plate 3MFs
    for plate_name, part_tuples in flat_parts_by_plate.items():
        scene = trimesh.Scene()
        grid_cols = int(np.ceil(np.sqrt(len(part_tuples))))
        spacing = 50.0

        for idx, (item, mesh) in enumerate(part_tuples):
            m = mesh.copy()
            row = idx // grid_cols
            col = idx % grid_cols
            x_offset = (col - (grid_cols - 1) / 2.0) * spacing
            y_offset = (row - (len(part_tuples) // grid_cols) / 2.0) * spacing
            m.apply_translation([x_offset, y_offset, 0])
            m.metadata["name"] = item["source_file"].replace(".stl", "")
            scene.add_geometry(m, node_name=item["source_file"].replace(".stl", ""))

        plate_file = os.path.join(plates_dir, f"{plate_name}.3mf")
        scene.export(plate_file)

    # Full Set 36-Part Plate 3MF
    all_scene = trimesh.Scene()
    all_parts = []
    for part_tuples in flat_parts_by_plate.values():
        all_parts.extend(part_tuples)

    grid_cols = 6
    spacing = 45.0
    for idx, (item, mesh) in enumerate(all_parts):
        m = mesh.copy()
        row = idx // grid_cols
        col = idx % grid_cols
        x_offset = (col - (grid_cols - 1) / 2.0) * spacing
        y_offset = (row - (len(all_parts) // grid_cols) / 2.0) * spacing
        m.apply_translation([x_offset, y_offset, 0])
        m.metadata["name"] = item["source_file"].replace(".stl", "")
        all_scene.add_geometry(m, node_name=item["source_file"].replace(".stl", ""))

    full_file = os.path.join(plates_dir, "Custom_Hybrid_Grenade_Full_Set_Plate.3mf")
    all_scene.export(full_file)


def _write_readme():
    readme_path = guard(os.path.join(OUTPUT_DIR, "README_3D_PRINTING.md"))
    from package_paths import PACKAGE_NAME

    md_content = """# 🎯 Native Tactical/Spinner Hybrid Grenade Fidget Toy — 3D Printing & Assembly Guide
### Package {{PACKAGE}}

This directory contains the complete, production-ready 3D printing package for the **Native Tactical/Spinner Hybrid Grenade Fidget Toy**.

## What changed in v1.2

One change, to the **up/down click of the central rod** — and one thing it costs, recorded plainly below. Everything else — the 33-click waist, the 20-click rim gear, the 4-position fold, the spinner ring, all 8 mid shell options — is untouched and measures identically to v1.1.

### The rod detent is now four arms of `11 - Middle Spring`

The reference is the Spinner Fuse Grenade's `11 - Middle Spring`. Measured, what makes it good is **not** force — it peaks at 2.00 N, well under v1.1's 5.53 N — but how gently it works its material: **1.207 N/mm on 0.714% strain per millimetre of travel**, against the v1.1 leaf's 2.951 N/mm on 1.278%. Over the tens of thousands of clicks a fidget sees, that is the difference between a flexure that lasts and one that cracks.

That part is a closed C, 34.81 × 32.63 × 3.00 mm, and it cannot go in whole — the rod is inserted full depth through the barrel and there is nowhere for a closed C to sit. So it is **cut in half at the middle** and one arm is transplanted: the reference's own outline, trimmed of the bridge and of the shell tab, mapped into the slot at **0.53 radial / 0.74 axial** scale. It keeps the shape that matters — the long slanted leg, the fold out to an outer rail, the U-turn, and the hook back inward to the nose — and only the two ends are ours: a rigid foot where `11` had its bridge, carrying the **extended notch**, and a nose cut for this rod's rack.

| | v1.1 | v1.2 | `11 - Middle Spring` |
|---|---|---|---|
| architecture | 3 short leaves at 90/210/330 | **4 transplanted arms at 0/90/180/270** | 2 arms on one C |
| rate per arm | 2.951 N/mm | **0.631 N/mm** | 1.207 N/mm |
| strain per mm | 1.278 % | **0.831 %** | 0.714 % |
| **strain per click** | 1.11 % | **1.12 %** | 0.59 % |
| peak force | 5.53 N | **2.26 N** | 2.00 N |
| held at every click | 0.00 N | **0.45 N** | 0.00 N |
| dead band | 12% of pitch | **0%** | 3% |

In v1.1 the nose sat 0.10 mm *clear* of the rack at every click, so the force fell to exactly zero across the middle 12% of each tooth — nothing held the rod between clicks, and since 0.10 mm is inside normal print variation a given print could have had no click at all. That is gone. The fix is not obvious and is worth stating: the rack's groove is only **2.58 mm wide at crest level**, and a tongue whose flanks match the rack's is 2.618 mm wide there *whatever* tip radius it uses — so it can never be pushed deeper than a perfect fit, and a perfect fit carries no preload. This nose is deliberately **wider** than the groove and wedges down onto the crest shoulders instead, which is what gives it 0.45 N to hold with.

The rod's rack is a **turned ring**, the same at every azimuth, so all four arms bite equally. Print the springs in **PETG**, not PLA.

### What it cost: the barrel's other slots, the pins and the cap's keys

The barrel now carries **exactly four slots and nothing else**. Three sets of features had to go to get there:

- **The three pin channels at 30° / 150° / 270° are filled**, and parts `09/10/11 - Internal Barrel Pin` leave the kit. Four slots 90° apart cannot fit around three channels 120° apart — the nearest miss is 15°, and clearing one needs r ≥ 17.4 mm against the barrel's 16.22.
- **The three stock follower slots at 90° / 210° / 330° are filled too.** At azimuth 90 a new slot lands on an old one, and leaving it gave a hybrid of the two profiles — deeper and wider above r 12.30 than the new section, shallower below.
- **The cap loses all three keys**, because they keyed into those same slots. `11_Custom_Internal_Barrel_Cap` is the plain lobed disc that remains; it still presses onto the barrel's top face and its underside at y 63.205 is what holds all four springs down. Its rotational lock is gone — measured, the rim alone does not replace it.

> **The upper station is no longer retained axially.** Those pins were the only thing holding `27 - Upper Shell Top` down on the barrel — lift it and it now comes straight off, meeting zero interference. Rotation is unaffected: the barrel keys the shell with its own lobes. A replacement retention is still to be designed; do not print this package expecting a finished toy.

The slots keep the stock two-step section — a neck with a one-sided widening that the notch rides in — 0.30 mm wider than stock so the spring can be the reference's own 3.00 mm thickness, and they stop at r 12.30 instead of 14.55. They have to: above y 54 the barrel is a **narrow** cylinder, 13.95 in the troughs and 14.70 at 0° and 180°, with three lobes to 17.10 at 90° / 210° / 330° that were the only reason the stock slots could be as deep as they were. Filling and cutting together take the barrel from 19365 mm³ to 19022 mm³, a net 1.8%, and the thinnest wall left outboard of any slot is **1.50 mm** — thicker than the 0.49 mm the stock barrel already carries elsewhere. Nothing is cut through to the outside, so the journal the mid shell rides on is untouched.

**v1.1 and v1.2 barrels are not interchangeable**, and neither are the caps.

### Key Architectural Highlights
1. **Tactical Internal Spine**: The native `08 - Internal Barrel`, its three pin channels filled and four spring slots cut at 0° / 90° / 180° / 270°, carrying the 4 preloaded springs (`12/13/14/15`) that ride the rod's rack and are the whole of the axial click.
2. **Original Tactical Upper Station**: Retains `28 - Upper Shell Gear`, `27 - Upper Shell Top`, `29 - Lock Ring`, and `30 - Rotating Spring`.
3. **Solid-Yoke 3-Piece Rod**: Full-depth rod assembly with seamless integral yoke (`Custom_Rod_Middle`, `Custom_Rod_Right`, and `Custom_Rod_Left`) locked via transverse `06` and `07` cross-keys and retained axially by `Spinner Lever 08 - Rod Lock`. (No upper wedge lock and no unnecessary keyway holes).
4. **Folding Head & Spinner**: High-tactile folding lever mechanism with 4 detent positions (0°, 30°, 60°, 90°), free-spinning center ring (360°), and outer rim clicker gear (20 clicks/turn).

---

## 📦 Directory Structure

```text
3D_Print_Custom_Hybrid_Grenade/
├── 3D_Print_Custom_Hybrid_Grenade_Assembled.glb # Complete full 3D assembly (PBR materials & metadata)
├── 3D_Print_Custom_Hybrid_Grenade_Exploded.glb  # Fully parted exploded view showing all {{N_TOTAL}} internal parts
├── 3D_Print_Custom_Hybrid_Grenade_Cutaway.glb   # Coronal/sagittal cutaway revealing internal rack & springs
├── 01_Base_And_Bottom_Shell/               # {{N_01}} STLs: Bottom lock cylinder, spacer, flexure spring & 3 outer shell tiers
├── 02_Waist_Mechanism/                     # {{N_02}} STLs: 33-lobe ratchet ring, outer shell body & 3-arm detent spring
├── 03_Internal_Barrel_And_Upper_Station/   # {{N_03}} STLs: barrel (4 slots), cap, 4 rod detent springs, gear, top & lock ring
├── 04_Rod_Assembly_And_Locks/              # {{N_04}} STLs: Full-depth 3-part rod (solid yoke), 2 cross-keys & bottom axial retainer
├── 05_Folding_Head_And_Spinner/            # {{N_05}} STLs: Folding lever cheeks, center spinner ring, rim gear & clicker, hinge lock pins
├── All_Parts_Flat_Bed_Oriented/            # Every STL pre-oriented flat on Z=0 for instant drag-and-drop slicing
├── All_Parts_Assembled_Coordinates/        # Every STL in exact solved global assembly space
├── Plates_3MF/                             # Multi-part 3MF build plates arranged for Bambu Studio / OrcaSlicer / PrusaSlicer
└── README_3D_PRINTING.md                   # Complete BOM, slicer recommendations & step-by-step assembly manual
```

---

## 📋 Complete Bill of Materials (BOM) — {{N_TOTAL}} Parts Total

| Part # | Subassembly | Filename | Material / Recommended Color | Qty | Supports |
|:---|:---|:---|:---|:---:|:---:|
| **01** | Base & Bottom | `01_04_Bottom_Shell_01.stl` | PLA (Olive Drab Green) | 1 | No |
| **02** | Base & Bottom | `02_05_Bottom_Shell_02.stl` | PLA (Olive Drab Green) | 1 | No |
| **03** | Base & Bottom | `03_06_Bottom_Shell_03.stl` | PLA (Olive Drab Green) | 1 | No |
| **04** | Base & Bottom | `04_01_Bottom_Lock_Shell.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **05** | Base & Bottom | `05_02_Bottom_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **06** | Base & Bottom | `06_03_Bottom_Shell_Spacer.stl` | PLA (Gunmetal / Black) | 1 | No |
| **07** | Waist Mech | `07_32_Mid_Shell_P02_Ratchet.stl` | PLA (Olive Drab Green) | 1 | No |
| **08** | Waist Mech | `08_33_Mid_Shell_P01_Outer.stl` | PLA (Olive Drab Green) | 1 | No |
| **09** | Waist Mech | `09_Custom_Mid_Shell_Spring_33.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **10** | Upper Station | `10_Custom_Internal_Barrel_4Slot.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **11** | Upper Station | `11_Custom_Internal_Barrel_Cap.stl` | PLA (Gunmetal / Black) | 1 | No |
| **12** | Upper Station | `12_Custom_Rod_Detent_Spring_01.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **13** | Upper Station | `13_Custom_Rod_Detent_Spring_02.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **14** | Upper Station | `14_Custom_Rod_Detent_Spring_03.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **15** | Upper Station | `15_Custom_Rod_Detent_Spring_04.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **18** | Upper Station | `18_27_Upper_Shell_Top.stl` | PLA (Olive Drab Green) | 1 | No |
| **19** | Upper Station | `19_28_Upper_Shell_Gear.stl` | PLA (Silver / Gunmetal) | 1 | No |
| **20** | Upper Station | `20_29_Upper_Shell_Lock_Ring.stl` | PLA (Olive Drab Green) | 1 | No |
| **21** | Upper Station | `21_30_Upper_Shell_Rotating_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **22** | Rod Assembly | `22_Custom_Rod_Right.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **23** | Rod Assembly | `23_Custom_Rod_Middle.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | Minimal (under yoke) |
| **24** | Rod Assembly | `24_Custom_Rod_Left.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **25** | Rod Assembly | `25_Custom_Rod_Lock_Upper_06.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **26** | Rod Assembly | `26_Custom_Rod_Lock_Lower_07.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **27** | Rod Assembly | `27_Spinner_Lever_08_Rod_Lock.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **28** | Head & Spinner | `28_09_Rod_Spring_Hinge.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **29** | Head & Spinner | `29_Custom_Handle_Left.stl` | PLA (Olive Drab Green) | 1 | No |
| **30** | Head & Spinner | `30_Custom_Handle_Right.stl` | PLA (Olive Drab Green) | 1 | No |
| **31** | Head & Spinner | `31_Custom_Ring_Spinner.stl` | Silk PLA (Gold / Brass) | 1 | No |
| **32** | Head & Spinner | `32_Spinner_Lever_05_Gear.stl` | Silk PLA (Silver / Metallic) | 1 | No |
| **33** | Head & Spinner | `33_Spinner_Lever_04_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **34** | Head & Spinner | `34_Custom_16_Handle_Lock_Neck.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **35** | Head & Spinner | `35_Custom_16_Handle_Lock_Pod.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **36** | Head & Spinner | `36_15_Handle_Rotating_Lock_D_Pin.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |

---

## ⚙️ Recommended Slicer Settings

- **Layer Height**: `0.16 mm` (recommended) or `0.20 mm`.
- **Wall Loops / Perimeters**: `4` walls for all structural parts, gears, and springs.
- **Top / Bottom Shells**: `5` top layers, `4` bottom layers.
- **Infill**: `25% - 30% Gyroid` or `Cubic`.
- **Supports**: Disabled on every part but one (only minimal support under the central rod's hinge yoke overhang).

---

## 🔧 Step-by-Step Assembly Instructions

### Stage 1: Bottom Lock & Lower Outer Shells
1. Drop `05_02_Bottom_Spring.stl` into the cavity of `04_01_Bottom_Lock_Shell.stl`.
2. Press `06_03_Bottom_Shell_Spacer.stl` on top to seal the bottom spring chamber.
3. Slide this sub-assembly into `01_04_Bottom_Shell_01.stl`.
4. Stack `02_05_Bottom_Shell_02.stl` over the shoulder, then seat `03_06_Bottom_Shell_03.stl` on top.

### Stage 2: Waist Mechanism & 33-Lobe Clicker
1. Insert `09_Custom_Mid_Shell_Spring_33.stl` through the 3 lower windows of `10_Custom_Internal_Barrel_4Slot.stl`.
2. Slide `07_32_Mid_Shell_P02_Ratchet.stl` onto the barrel until its internal lobes engage the 3 spring arms.
3. Place `08_33_Mid_Shell_P01_Outer.stl` over the ratchet ring.

### Stage 3: Rod Detent Springs & Upper Station
1. Drop the 4 detent springs (`12`, `13`, `14`, `15`) into the barrel's four slots at 0 deg / 90 deg / 180 deg / 270 deg, **from the open top**. They are identical parts; the rib on the foot faces the same way in all four, and it catches the step in the slot so the spring cannot work its way inward. They are preloaded — the noses stand proud of where the rack will hold them, so the rod snaps past them on the way in.
2. Seal the top of the barrel with `11_Custom_Internal_Barrel_Cap.stl`. It is a plain disc with no keys, so it drops on either way round; its underside traps all four springs.
3. Slide `19_28_Upper_Shell_Gear.stl` over the upper barrel station.
4. Install `21_30_Upper_Shell_Rotating_Spring.stl` and `20_29_Upper_Shell_Lock_Ring.stl`.
5. Seat `18_27_Upper_Shell_Top.stl` over the upper station to close the main body. **It is not retained** — the three pins that used to hold it down are gone, so it will lift straight off until a replacement is designed.

### Stage 4: Unified Full-Height Rod Assembly & Enclosed Hinge Spring
1. Insert narrowed `28_09_Rod_Spring_Hinge.stl` into the central spring channel of `23_Custom_Rod_Middle.stl`.
2. Place full-height `22_Custom_Rod_Right.stl` and `24_Custom_Rod_Left.stl` on the right and left sides of `23_Custom_Rod_Middle.stl`, fully enclosing the hinge spring inside the symmetric pod halves and forming the upper hexagonal keying prism.
3. Insert `25_Custom_Rod_Lock_Upper_06.stl` through the upper cross-tunnel.
4. Insert `26_Custom_Rod_Lock_Lower_07.stl` through the lower cross-tunnel.
5. Slide the assembled 3-piece rod down through the central bore of the body and through `21_30_Upper_Shell_Rotating_Spring.stl` (the hexagonal upper section positively locks to the rotating spring's bore).
6. Press `27_Spinner_Lever_08_Rod_Lock.stl` onto the bottom tapered wedge to retain the rod axially.

### Stage 5: Folding Head, Rim Gear & Center Spinner
1. Place `33_Spinner_Lever_04_Spring.stl` inside the handle pod pocket.
2. Mount `32_Spinner_Lever_05_Gear.stl` and `31_Custom_Ring_Spinner.stl` onto the journal tube of `29_Custom_Handle_Left.stl`.
3. Close with `30_Custom_Handle_Right.stl`.
4. Secure the handle cheeks with `34_Custom_16_Handle_Lock_Neck.stl` and `35_Custom_16_Handle_Lock_Pod.stl`.
5. Mount the assembled folding head onto the rod's upper hinge yoke and insert `36_15_Handle_Rotating_Lock_D_Pin.stl` to complete the toy!
"""
    # Counts come from the manifest rather than from prose, because prose drifts:
    # the v1.2 README shipped claiming 36 parts when the kit held 35.
    counts = {"{{N_TOTAL}}": str(len(PARTS_MANIFEST))}
    for sub in _DERIVED_SUBDIRS[:5]:
        counts["{{N_%s}}" % sub[:2]] = str(
            sum(1 for i in PARTS_MANIFEST if i["subassembly"] == sub))
    md_content = md_content.replace("{{PACKAGE}}", PACKAGE_NAME)
    for key, value in counts.items():
        md_content = md_content.replace(key, value)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(md_content)


if __name__ == "__main__":
    export_complete_package()
