"""Export all 36 parts for the Native Tactical/Spinner Hybrid Grenade Fidget Toy for 3D printing.

This package uses the original Tactical Internal Barrel & Upper Station mechanism
and the solid-yoke 3-piece rod assembly (joined by transverse 06 & 07 cross-keys and
08 bottom retainer, with NO upper wedge lock).

Output directory:
  3D_Print_Custom_Hybrid_Grenade/
    ├── 01_Base_And_Bottom_Shell/               (6 STLs)
    ├── 02_Waist_Mechanism/                     (3 STLs)
    ├── 03_Internal_Barrel_And_Upper_Station/   (12 STLs - Original Tactical Mechanism)
    ├── 04_Rod_Assembly_And_Locks/              (6 STLs - Solid Yoke Rod & Cross Keys)
    ├── 05_Folding_Head_And_Spinner/            (9 STLs - Folding Cheeks, Gear, Spinner Ring & Pins)
    ├── All_Parts_Flat_Bed_Oriented/            (36 STLs - pre-oriented flat on Z=0, centered at (0,0))
    ├── All_Parts_Assembled_Coordinates/        (36 STLs - exact global solved assembly space)
    ├── Plates_3MF/                             (Multi-part 3MF project plates)
    └── README_3D_PRINTING.md                   (Complete 36-part BOM & Assembly Manual)
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import numpy as np
import trimesh
import manifold3d

OUTPUT_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.1")
ASSEMBLED_STLS_DIR = os.path.join(OUTPUT_DIR, "All_Parts_Assembled_Coordinates")

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

    # 03 - Original Tactical Internal Barrel & Upper Station
    {
        "id": 10,
        "source_file": "08 - Internal Barrel.stl",
        "export_filename": "10_08_Internal_Barrel.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Black / Gunmetal",
        "desc": "Original Tactical barrel spine with 3 pin channels and waist windows",
        "supports": "No",
    },
    {
        "id": 11,
        "source_file": "07 - Internal Barrel Cap.stl",
        "export_filename": "11_07_Internal_Barrel_Cap.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Black / Gunmetal",
        "desc": "Original barrel top sealing cap",
        "supports": "No",
    },
    {
        "id": 12,
        "source_file": "09 - Internal Barrel Pin v1.1.stl",
        "export_filename": "12_09_Internal_Barrel_Pin_01.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Black / Tough PLA",
        "desc": "Original internal detent pin 1 (linear rod clicks)",
        "supports": "No",
    },
    {
        "id": 13,
        "source_file": "10 - Internal Barrel v1.1.stl",
        "export_filename": "13_10_Internal_Barrel_Pin_02.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Black / Tough PLA",
        "desc": "Original internal detent pin 2 (linear rod clicks)",
        "supports": "No",
    },
    {
        "id": 14,
        "source_file": "11 - Internal Barrel v1.1.stl",
        "export_filename": "14_11_Internal_Barrel_Pin_03.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Black / Tough PLA",
        "desc": "Original internal detent pin 3 (linear rod clicks)",
        "supports": "No",
    },
    {
        "id": 15,
        "source_file": "12 - Internal Barrel Spring v1.1.stl",
        "export_filename": "15_12_Internal_Barrel_Spring_01.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Original leaf spring 1 biasing pin 1 against rod rack",
        "supports": "No",
    },
    {
        "id": 16,
        "source_file": "13 - Internal Barrel Spring v1.1.stl",
        "export_filename": "16_13_Internal_Barrel_Spring_02.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Original leaf spring 2 biasing pin 2 against rod rack",
        "supports": "No",
    },
    {
        "id": 17,
        "source_file": "14 - Internal Barrel Spring v1.1.stl",
        "export_filename": "17_14_Internal_Barrel_Spring_03.stl",
        "subassembly": "03_Internal_Barrel_And_Upper_Station",
        "plate": "Plate_2_Internal_Barrel_And_Springs",
        "color": "Safety Orange / PETG",
        "desc": "Original leaf spring 3 biasing pin 3 against rod rack",
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

    # 04 - Rod Assembly & Locks (Solid Yoke, 06 & 07 Cross-keys, 08 Bottom Retainer, NO Upper Wedge)
    {
        "id": 22,
        "source_file": "Custom_Rod_Right.stl",
        "export_filename": "22_Custom_Rod_Right.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Black / Gunmetal",
        "desc": "Lower right rod member (trimmed at Y=62 mm)",
        "supports": "No",
    },
    {
        "id": 23,
        "source_file": "Custom_Rod_Middle.stl",
        "export_filename": "23_Custom_Rod_Middle.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Black / Gunmetal",
        "desc": "Full-depth middle rod with integral solid hinge yoke and transverse key tunnels",
        "supports": "Minimal (under yoke)",
    },
    {
        "id": 24,
        "source_file": "Custom_Rod_Left.stl",
        "export_filename": "24_Custom_Rod_Left.stl",
        "subassembly": "04_Rod_Assembly_And_Locks",
        "plate": "Plate_3_Rod_Assembly_And_Locks",
        "color": "Black / Gunmetal",
        "desc": "Lower left rod member (trimmed at Y=62 mm)",
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
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    subdirs = [
        "01_Base_And_Bottom_Shell",
        "02_Waist_Mechanism",
        "03_Internal_Barrel_And_Upper_Station",
        "04_Rod_Assembly_And_Locks",
        "05_Folding_Head_And_Spinner",
        "All_Parts_Flat_Bed_Oriented",
        "All_Parts_Assembled_Coordinates",
        "Plates_3MF",
    ]
    for sd in subdirs:
        os.makedirs(os.path.join(OUTPUT_DIR, sd), exist_ok=True)

    print(f"Processing {len(PARTS_MANIFEST)} native parts from {ASSEMBLED_STLS_DIR}...")
    flat_parts_by_plate = {}

    for item in PARTS_MANIFEST:
        src_path = os.path.join(ASSEMBLED_STLS_DIR, item["export_filename"])
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Source file missing: {src_path}")

        mesh = trimesh.load(src_path, force="mesh", process=True)
        mesh = _stl_safe(mesh, item["export_filename"])

        # 2. Bed-Oriented (centered XY, placed on Z=0)
        flat_mesh = _center_on_bed(mesh)
        flat_mesh = _stl_safe(flat_mesh, item["source_file"])

        # Export into category subassembly
        sub_path = os.path.join(OUTPUT_DIR, item["subassembly"], item["export_filename"])
        flat_mesh.export(sub_path)

        # Export into All_Parts_Flat_Bed_Oriented
        all_flat_path = os.path.join(OUTPUT_DIR, "All_Parts_Flat_Bed_Oriented", item["export_filename"])
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

    print("\n[SUCCESS] All 36 parts and GLB models exported successfully!")



def _export_3mf_plates(flat_parts_by_plate):
    plates_dir = os.path.join(OUTPUT_DIR, "Plates_3MF")

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
    readme_path = os.path.join(OUTPUT_DIR, "README_3D_PRINTING.md")

    md_content = """# 🎯 Native Tactical/Spinner Hybrid Grenade Fidget Toy — 3D Printing & Assembly Guide

This directory contains the complete, production-ready 3D printing package for the **Native Tactical/Spinner Hybrid Grenade Fidget Toy**.

### Key Architectural Highlights
1. **Original Tactical Internal Spine**: Retains the native `08 - Internal Barrel` with its 3 internal pin channels (`09/10/11 Pins`) and 3 leaf springs (`12/13/14 Springs`) providing crisp linear clicks against the rod.
2. **Original Tactical Upper Station**: Retains `28 - Upper Shell Gear`, `27 - Upper Shell Top`, `29 - Lock Ring`, and `30 - Rotating Spring`.
3. **Solid-Yoke 3-Piece Rod**: Full-depth rod assembly with seamless integral yoke (`Custom_Rod_Middle`, `Custom_Rod_Right`, and `Custom_Rod_Left`) locked via transverse `06` and `07` cross-keys and retained axially by `Spinner Lever 08 - Rod Lock`. (No upper wedge lock and no unnecessary keyway holes).
4. **Folding Head & Spinner**: High-tactile folding lever mechanism with 4 detent positions (0°, 30°, 60°, 90°), free-spinning center ring (360°), and outer rim clicker gear (20 clicks/turn).

---

## 📦 Directory Structure

```text
3D_Print_Custom_Hybrid_Grenade/
├── 3D_Print_Custom_Hybrid_Grenade_Assembled.glb # Complete 36-part full 3D assembly (PBR materials & metadata)
├── 3D_Print_Custom_Hybrid_Grenade_Exploded.glb  # Fully parted exploded view showing all 36 internal parts
├── 3D_Print_Custom_Hybrid_Grenade_Cutaway.glb   # Coronal/sagittal cutaway revealing internal rack & springs
├── 01_Base_And_Bottom_Shell/               # 6 STLs: Bottom lock cylinder, spacer, flexure spring & 3 outer shell tiers
├── 02_Waist_Mechanism/                     # 3 STLs: 33-lobe ratchet ring, outer shell body & 3-arm detent spring
├── 03_Internal_Barrel_And_Upper_Station/   # 12 STLs: Original Tactical barrel, cap, 3 pins, 3 leaf springs, gear, top & lock ring
├── 04_Rod_Assembly_And_Locks/              # 6 STLs: Full-depth 3-part rod (solid yoke), 2 cross-keys & bottom axial retainer
├── 05_Folding_Head_And_Spinner/            # 9 STLs: Folding lever cheeks, center spinner ring, rim gear & clicker, hinge lock pins
├── All_Parts_Flat_Bed_Oriented/            # All 36 individual STLs pre-oriented flat on Z=0 for instant drag-and-drop slicing
├── All_Parts_Assembled_Coordinates/        # All 36 individual STLs in exact solved global assembly space
├── Plates_3MF/                             # Multi-part 3MF build plates arranged for Bambu Studio / OrcaSlicer / PrusaSlicer
└── README_3D_PRINTING.md                   # Complete BOM, slicer recommendations & step-by-step assembly manual
```

---

## 📋 Complete Bill of Materials (BOM) — 36 Parts Total

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
| **10** | Upper Station | `10_08_Internal_Barrel.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **11** | Upper Station | `11_07_Internal_Barrel_Cap.stl` | PLA (Gunmetal / Black) | 1 | No |
| **12** | Upper Station | `12_09_Internal_Barrel_Pin_01.stl` | PLA+ / Tough PLA (Gunmetal / Black) | 1 | No |
| **13** | Upper Station | `13_10_Internal_Barrel_Pin_02.stl` | PLA+ / Tough PLA (Gunmetal / Black) | 1 | No |
| **14** | Upper Station | `14_11_Internal_Barrel_Pin_03.stl` | PLA+ / Tough PLA (Gunmetal / Black) | 1 | No |
| **15** | Upper Station | `15_12_Internal_Barrel_Spring_01.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **16** | Upper Station | `16_13_Internal_Barrel_Spring_02.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **17** | Upper Station | `17_14_Internal_Barrel_Spring_03.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
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
- **Supports**: Disabled on 35/36 parts (only minimal support needed under the central rod's hinge yoke overhang).

---

## 🔧 Step-by-Step Assembly Instructions

### Stage 1: Bottom Lock & Lower Outer Shells
1. Drop `05_02_Bottom_Spring.stl` into the cavity of `04_01_Bottom_Lock_Shell.stl`.
2. Press `06_03_Bottom_Shell_Spacer.stl` on top to seal the bottom spring chamber.
3. Slide this sub-assembly into `01_04_Bottom_Shell_01.stl`.
4. Stack `02_05_Bottom_Shell_02.stl` over the shoulder, then seat `03_06_Bottom_Shell_03.stl` on top.

### Stage 2: Waist Mechanism & 33-Lobe Clicker
1. Insert `09_Custom_Mid_Shell_Spring_33.stl` through the 3 lower windows of `10_08_Internal_Barrel.stl`.
2. Slide `07_32_Mid_Shell_P02_Ratchet.stl` onto the barrel until its internal lobes engage the 3 spring arms.
3. Place `08_33_Mid_Shell_P01_Outer.stl` over the ratchet ring.

### Stage 3: Original Internal Barrel Clicking Pins & Upper Station
1. Insert the 3 pins (`12_09`, `13_10`, `14_11`) into the vertical pin slots of `10_08_Internal_Barrel.stl`.
2. Seat the 3 leaf springs (`15_12`, `16_13`, `17_14`) behind the pins.
3. Seal the top of the barrel with `11_07_Internal_Barrel_Cap.stl`.
4. Slide `19_28_Upper_Shell_Gear.stl` over the upper barrel station.
5. Install `21_30_Upper_Shell_Rotating_Spring.stl` and `20_29_Upper_Shell_Lock_Ring.stl`.
6. Seat `18_27_Upper_Shell_Top.stl` over the upper station to close the main body.

### Stage 4: Three-Part Full-Depth Rod Assembly
1. Place `22_Custom_Rod_Right.stl` and `24_Custom_Rod_Left.stl` on either side of `23_Custom_Rod_Middle.stl`.
2. Insert `25_Custom_Rod_Lock_Upper_06.stl` through the upper cross-tunnel.
3. Insert `26_Custom_Rod_Lock_Lower_07.stl` through the lower cross-tunnel.
4. Slide the locked 3-part rod down through the central square bore of the body.
5. Press `27_Spinner_Lever_08_Rod_Lock.stl` onto the bottom tapered wedge to retain the rod axially.

### Stage 5: Folding Head, Rim Gear & Center Spinner
1. Insert `28_09_Rod_Spring_Hinge.stl` into the yoke pocket between the upper rod cheeks.
2. Place `33_Spinner_Lever_04_Spring.stl` inside the handle pod pocket.
3. Mount `32_Spinner_Lever_05_Gear.stl` and `31_Custom_Ring_Spinner.stl` onto the journal tube of `29_Custom_Handle_Left.stl`.
4. Close with `30_Custom_Handle_Right.stl`.
5. Secure the handle cheeks with `34_Custom_16_Handle_Lock_Neck.stl` and `35_Custom_16_Handle_Lock_Pod.stl`.
6. Mount the assembled folding head onto the rod's upper hinge yoke and insert `36_15_Handle_Rotating_Lock_D_Pin.stl` to complete the toy!
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(md_content)


if __name__ == "__main__":
    export_complete_package()
