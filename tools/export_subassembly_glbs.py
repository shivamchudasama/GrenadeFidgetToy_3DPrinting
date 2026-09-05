"""Export the 5 subassembly GLBs for the current package.

Generates:
  - 01_Base_And_Bottom_Shell/Custom_Base_And_Bottom_Shell_Assembly.glb
  - 02_Waist_Mechanism/Custom_Waist_Assembly.glb
  - 03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_And_Upper_Station_Assembly.glb
  - 04_Rod_Assembly_And_Locks/Custom_Rod_Assembly.glb
  - 05_Folding_Head_And_Spinner/Custom_Head_Assembly.glb
"""
from __future__ import annotations

import os
import sys
import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import package_paths

PKG_DIR = package_paths.PACKAGE_DIR
ASY_DIR = package_paths.ASSEMBLED_DIR

SUBASSEMBLIES = {
    "01_Base_And_Bottom_Shell": {
        "out_glb": "Custom_Base_And_Bottom_Shell_Assembly.glb",
        "parts": [
            ("01_04_Bottom_Shell_01.stl", (122, 181, 102, 255)),
            ("02_05_Bottom_Shell_02.stl", (122, 181, 102, 255)),
            ("03_06_Bottom_Shell_03.stl", (122, 181, 102, 255)),
            ("04_01_Bottom_Lock_Shell.stl", (60, 70, 80, 255)),
            ("05_02_Bottom_Spring.stl", (255, 110, 30, 255)),
            ("06_03_Bottom_Shell_Spacer.stl", (60, 70, 80, 255)),
        ]
    },
    "02_Waist_Mechanism": {
        "out_glb": "Custom_Waist_Assembly.glb",
        "parts": [
            ("07_32_Mid_Shell_P02_Ratchet.stl", (240, 90, 20, 255)),
            ("08_33_Mid_Shell_P01_Outer.stl", (122, 181, 102, 255)),
            ("09_Custom_Mid_Shell_Spring_33.stl", (255, 110, 30, 255)),
        ]
    },
    "03_Internal_Barrel_And_Upper_Station": {
        "out_glb": "Custom_Internal_Barrel_And_Upper_Station_Assembly.glb",
        "parts": [
            ("10_Custom_Internal_Barrel_4Slot.stl", (55, 65, 75, 255)),
            ("11_Custom_Internal_Barrel_Cap.stl", (70, 80, 90, 255)),
            ("12_Custom_Rod_Detent_Spring_01.stl", (255, 110, 30, 255)),
            ("13_Custom_Rod_Detent_Spring_02.stl", (255, 110, 30, 255)),
            ("14_Custom_Rod_Detent_Spring_03.stl", (255, 110, 30, 255)),
            ("15_Custom_Rod_Detent_Spring_04.stl", (255, 110, 30, 255)),
            ("16_Custom_Internal_Barrel_Pin_01.stl", (60, 70, 80, 255)),
            ("17_Custom_Internal_Barrel_Pin_02.stl", (60, 70, 80, 255)),
            ("16_Custom_Internal_Barrel_Pin_03.stl", (60, 70, 80, 255)),
            ("17_Custom_Internal_Barrel_Pin_04.stl", (60, 70, 80, 255)),
            ("18_27_Upper_Shell_Top.stl", (122, 181, 102, 255)),
            ("19_28_Upper_Shell_Gear.stl", (180, 185, 190, 255)),
            ("20_29_Upper_Shell_Lock_Ring.stl", (122, 181, 102, 255)),
            ("21_30_Upper_Shell_Rotating_Spring.stl", (255, 110, 30, 255)),
        ]
    },
    "04_Rod_Assembly_And_Locks": {
        "out_glb": "Custom_Rod_Assembly.glb",
        "parts": [
            ("22_Custom_Rod_Right.stl", (70, 80, 90, 255)),
            ("23_Custom_Rod_Middle.stl", (55, 65, 75, 255)),
            ("24_Custom_Rod_Left.stl", (70, 80, 90, 255)),
            ("25_Custom_Rod_Lock_Upper_06.stl", (255, 110, 30, 255)),
            ("26_Custom_Rod_Lock_Lower_07.stl", (255, 110, 30, 255)),
            ("27_Spinner_Lever_08_Rod_Lock.stl", (60, 70, 80, 255)),
        ]
    },
    "05_Folding_Head_And_Spinner": {
        "out_glb": "Custom_Head_Assembly.glb",
        "parts": [
            ("28_09_Rod_Spring_Hinge_T_Head.stl", (255, 110, 30, 255)),
            ("29_Custom_Handle_Left.stl", (122, 181, 102, 255)),
            ("30_Custom_Handle_Right.stl", (122, 181, 102, 255)),
            ("31_Custom_Ring_Spinner.stl", (220, 180, 50, 255)),
            ("32_Spinner_Lever_05_Gear.stl", (200, 205, 210, 255)),
            ("33_Spinner_Lever_04_Spring.stl", (255, 110, 30, 255)),
            ("34_Custom_16_Handle_Lock_Neck.stl", (255, 110, 30, 255)),
            ("35_Custom_16_Handle_Lock_Pod.stl", (255, 110, 30, 255)),
            ("36_15_Handle_Rotating_Lock_D_Pin.stl", (255, 110, 30, 255)),
        ]
    },
}


def main():
    print(f"[*] Exporting 5 subassembly GLBs for {package_paths.PACKAGE_NAME}...")
    for subdir, data in SUBASSEMBLIES.items():
        sub_dir_path = os.path.join(PKG_DIR, subdir)
        os.makedirs(sub_dir_path, exist_ok=True)
        out_path = package_paths.guard(os.path.join(sub_dir_path, data["out_glb"]))

        scene = trimesh.Scene()
        for filename, rgba in data["parts"]:
            stl_path = os.path.join(ASY_DIR, filename)
            if not os.path.exists(stl_path):
                print(f"  [!] Missing {stl_path}, skipping...")
                continue
            mesh = trimesh.load(stl_path)
            mesh.visual = trimesh.visual.ColorVisuals(mesh=mesh, vertex_colors=rgba)
            name = os.path.splitext(filename)[0]
            scene.add_geometry(mesh, node_name=name, geom_name=name)

        glb_data = scene.export(file_type="glb")
        with open(out_path, "wb") as f:
            f.write(glb_data)
        print(f"  [+] Exported -> {out_path} ({len(glb_data):,} bytes)")

    print("[SUCCESS] All 5 subassembly GLBs exported successfully!")


if __name__ == "__main__":
    main()
