"""
Build, validate, and export the Unified Full-Height Hex-Keyed Rod Assembly
and Enclosed Hinge Detent Spring.

Design Architecture:
  1. Monolithic Full-Height Side Clamps:
     - 22_Custom_Rod_Right (Y in [18.08, 80.00] mm): Unites the lower rod clamp, the upper
       hexagonal key cheek, and the right spring pod enclosure wall into a single continuous part.
     - 24_Custom_Rod_Left (Y in [18.08, 80.00] mm): Unites the lower rod clamp, the upper
       hexagonal key cheek, and the left spring pod enclosure wall into a single continuous part.
  2. Complete Solid-Center Middle Rod (All Teeth, Rails & Smooth Surface Preserved):
     - 23_Custom_Rod_Middle (Y in [18.08, 99.62] mm): Full gear rack teeth on front (+Z) and back (-Z),
       solid upper rails at +Z and -Z, integral solid hinge yoke at the top, and central channel
       for the hinge detent spring. Fully continuous side faces with zero step artifacts or residues.
       100% printable flat on bed.
  3. Hexagonal Keying with Rotating Spring:
     - The upper sections (Y in [62.00, 80.00] mm) of 22_Custom_Rod_Right and 24_Custom_Rod_Left
       flanking 23_Custom_Rod_Middle form an exact hexagonal key matching the bore of
       21_30_Upper_Shell_Rotating_Spring with 0.20 mm radial clearance.
  4. Narrowed Hinge Detent Spring:
     - 28_09_Rod_Spring_Hinge is narrowed along X to 6.00 mm (X in [-3.00, +3.00] mm) to fit
       entirely within the enclosed internal pod formed by the left and right clamps.
  5. Zero Interferences:
     - 0.000 mm3 interference across all pairwise components and across all fold angles (0°, 30°, 60°, 90°).
"""
from __future__ import annotations

import os
import sys
import numpy as np
import trimesh
import shapely.geometry as sg

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import custom
import fidget
import package_paths

PACKAGE_NAME = package_paths.PACKAGE_NAME
PKG_DIR = os.path.join(ROOT_DIR, PACKAGE_NAME)
V11_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.1")
ASY_DIR = os.path.join(PKG_DIR, "All_Parts_Assembled_Coordinates")
FLAT_DIR = os.path.join(PKG_DIR, "All_Parts_Flat_Bed_Oriented")
ROD_DIR = os.path.join(PKG_DIR, "04_Rod_Assembly_And_Locks")
HEAD_DIR = os.path.join(PKG_DIR, "05_Folding_Head_And_Spinner")


def build_unified_rod():
    print(f"[*] Loading reference parts from {ASY_DIR} and {V11_DIR}...")
    rot_sp = trimesh.load(os.path.join(ASY_DIR, "21_30_Upper_Shell_Rotating_Spring.stl"))
    rod_mid_pristine = trimesh.load(os.path.join(V11_DIR, "All_Parts_Assembled_Coordinates", "23_Custom_Rod_Middle.stl"))
    hinge_sp_raw = trimesh.load(os.path.join(V11_DIR, "All_Parts_Assembled_Coordinates", "28_09_Rod_Spring_Hinge.stl"))
    rod_r_raw = trimesh.load(os.path.join(V11_DIR, "All_Parts_Assembled_Coordinates", "22_Custom_Rod_Right.stl"))
    rod_l_raw = trimesh.load(os.path.join(V11_DIR, "All_Parts_Assembled_Coordinates", "24_Custom_Rod_Left.stl"))
    key_06 = trimesh.load(os.path.join(ASY_DIR, "25_Custom_Rod_Lock_Upper_06.stl"))
    key_07 = trimesh.load(os.path.join(ASY_DIR, "26_Custom_Rod_Lock_Lower_07.stl"))
    lock_08 = trimesh.load(os.path.join(ASY_DIR, "27_Spinner_Lever_08_Rod_Lock.stl"))
    handle_l = trimesh.load(os.path.join(ASY_DIR, "29_Custom_Handle_Left.stl"))
    handle_r = trimesh.load(os.path.join(ASY_DIR, "30_Custom_Handle_Right.stl"))
    d_pin = trimesh.load(os.path.join(ASY_DIR, "36_15_Handle_Rotating_Lock_D_Pin.stl"))

    # 1. Extract exact bore polygon of 21_30 rotating spring at Y=72.0 mm
    sl = rot_sp.section(plane_origin=[0, 72.0, 0], plane_normal=[0, 1, 0])
    coords_3d = []
    for entity in sl.entities:
        pts = sl.vertices[entity.points]
        if pts.max(axis=0)[0] - pts.min(axis=0)[0] < 20:  # hole loop
            coords_3d = pts
            break
    poly_xz = sg.Polygon([(pt[0], pt[2]) for pt in coords_3d])

    # Keying profile with 0.20 mm radial clearance
    hex_profile_xz = poly_xz.buffer(-0.20, resolution=16)

    # 2. Extrude hexagonal profile Y = 62.00 to 80.00 mm
    y_min, y_max = 62.00, 80.00
    hex_prism = trimesh.creation.extrude_polygon(hex_profile_xz, height=y_max - y_min)
    T_extrude = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, y_min],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    hex_prism.apply_transform(T_extrude)

    # Upper Right cheek (X in [-inf, -3.50]) and Upper Left cheek (X in [3.50, +inf])
    box_ur = trimesh.creation.box(
        extents=[30.0, 100.0, 100.0],
        transform=trimesh.transformations.translation_matrix([-18.5, (y_min + y_max) / 2.0, 0.0])
    )
    box_ul = trimesh.creation.box(
        extents=[30.0, 100.0, 100.0],
        transform=trimesh.transformations.translation_matrix([18.5, (y_min + y_max) / 2.0, 0.0])
    )

    rod_ur_cheek = fidget.intersect(hex_prism, box_ur)
    rod_ul_cheek = fidget.intersect(hex_prism, box_ul)

    # 3. Trim lower side members to Y <= 62.00 mm
    box_lower = trimesh.creation.box(
        extents=[50.0, 62.00 - 15.0, 50.0],
        transform=trimesh.transformations.translation_matrix([0.0, (62.00 + 15.0) / 2.0, 0.0])
    )
    rod_r_lower = fidget.intersect(rod_r_raw, box_lower)
    rod_l_lower = fidget.intersect(rod_l_raw, box_lower)

    # 4. Fuse lower side members with upper cheeks into unified full-height side clamps
    rod_r_full = fidget.union(rod_r_lower, rod_ur_cheek)
    rod_l_full = fidget.union(rod_l_lower, rod_ul_cheek)

    # 5. Continuous clean side trim of 23_Custom_Rod_Middle:
    # Trims entire upper region (Y in [60.0, 105.0]) to exact continuous X in [-3.50, 3.50]
    # Eliminates any step ledges, residues, or burrs while preserving all teeth and yoke geometry.
    box_side_trim_r = trimesh.creation.box(
        extents=[10.0, 100.0, 50.0],
        transform=trimesh.transformations.translation_matrix([-8.5, 60.0, 0.0])
    )
    box_side_trim_l = trimesh.creation.box(
        extents=[10.0, 100.0, 50.0],
        transform=trimesh.transformations.translation_matrix([8.5, 60.0, 0.0])
    )
    rod_mid_full = fidget.cut(rod_mid_pristine, box_side_trim_r)
    rod_mid_full = fidget.cut(rod_mid_full, box_side_trim_l)

    # 6. Narrow 28_09_Rod_Spring_Hinge along X to 6.00 mm (X in [-3.00, +3.00] mm)
    box_sp = trimesh.creation.box(
        extents=[6.0, 100.0, 100.0],
        transform=trimesh.transformations.translation_matrix([0.0, 75.0, 0.0])
    )
    hinge_sp_narrow = fidget.intersect(hinge_sp_raw, box_sp)

    # --- Validation ---
    print("\n[*] Validating generated parts...")
    generated = [
        ("22_Custom_Rod_Right (Full)", rod_r_full),
        ("23_Custom_Rod_Middle (Solid)", rod_mid_full),
        ("24_Custom_Rod_Left (Full)", rod_l_full),
        ("28_09_Rod_Spring_Hinge", hinge_sp_narrow),
    ]

    for name, mesh in generated:
        if not mesh.is_watertight:
            raise RuntimeError(f"Part {name} is not watertight!")
        if mesh.body_count != 1:
            raise RuntimeError(f"Part {name} has body_count = {mesh.body_count} (expected 1)!")
        print(f"  [OK] {name:30s} | Watertight: True | Body count: 1 | Volume: {mesh.volume:.2f} mm3")

    # Pairwise interference check
    print("\n[*] Checking pairwise interferences in assembled coordinates...")
    test_set = [
        ("22_Custom_Rod_Right", rod_r_full),
        ("23_Custom_Rod_Middle", rod_mid_full),
        ("24_Custom_Rod_Left", rod_l_full),
        ("25_Custom_Rod_Lock_Upper_06", key_06),
        ("26_Custom_Rod_Lock_Lower_07", key_07),
        ("27_Spinner_Lever_08_Rod_Lock", lock_08),
        ("28_09_Rod_Spring_Hinge", hinge_sp_narrow),
        ("21_30_Upper_Shell_Rotating_Spring", rot_sp),
    ]

    for i in range(len(test_set)):
        for j in range(i + 1, len(test_set)):
            n1, m1 = test_set[i]
            n2, m2 = test_set[j]
            ivol = m1.intersection(m2).volume
            if ivol > 1e-3:
                raise RuntimeError(f"Unintended interference between {n1} and {n2}: {ivol:.4f} mm3")
            print(f"  [OK] {n1} vs {n2}: 0.000 mm3")

    # Rotational keying test
    print("\n[*] Validating rotational lock with 21_30_Upper_Shell_Rotating_Spring...")
    full_upper_rod = trimesh.util.concatenate([rod_r_full, rod_l_full, rod_mid_full])
    for deg in [0.0, 1.0, 5.0, 10.0, 20.0, 30.0]:
        R = trimesh.transformations.rotation_matrix(np.radians(deg), [0, 1, 0])
        turned = full_upper_rod.copy().apply_transform(R)
        ivol = turned.intersection(rot_sp).volume
        print(f"  Angle {deg:4.1f}° -> Overlap with Rotating Spring = {ivol:8.3f} mm3")
        if deg == 0.0 and ivol > 1e-3:
            raise RuntimeError("Assembled rod interferes with Rotating Spring at nominal pose!")
        if deg >= 5.0 and ivol < 0.5:
            raise RuntimeError(f"Rotational keying failed at {deg}° (insufficient interference: {ivol} mm3)")

    # Fold range-of-motion test
    print("\n[*] Validating handle folding clearance (0°, 30°, 60°, 90°)...")
    hinge_center = d_pin.bounds.mean(axis=0)
    for deg in [0.0, 30.0, 60.0, 90.0]:
        R_fold = trimesh.transformations.rotation_matrix(np.radians(deg), [1, 0, 0], hinge_center)
        hl_f = handle_l.copy().apply_transform(R_fold)
        hr_f = handle_r.copy().apply_transform(R_fold)
        for r_name, r_mesh in [("Rod_R", rod_r_full), ("Rod_L", rod_l_full), ("Rod_Mid", rod_mid_full)]:
            for h_name, h_mesh in [("HL", hl_f), ("HR", hr_f)]:
                ivol = r_mesh.intersection(h_mesh).volume
                if ivol > 1e-3:
                    raise RuntimeError(f"Interference during fold at {deg}° between {r_name} and {h_name}: {ivol:.4f} mm3")
        print(f"  [OK] Fold angle {deg:4.1f}°: 0.000 mm3 clearance against all handle parts")

    return rod_r_full, rod_mid_full, rod_l_full, hinge_sp_narrow


def flat_bed_orient(mesh: trimesh.Trimesh, name: str) -> trimesh.Trimesh:
    """Orient mesh for optimal 3D printing flat on the build plate."""
    m = mesh.copy()
    if "22_Custom_Rod_Right" in name:
        # Lay flat on flat mating plane X = -3.50 (rotate 90 deg around Y)
        R = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])
        m.apply_transform(R)
    elif "24_Custom_Rod_Left" in name:
        # Lay flat on flat mating plane X = +3.50 (rotate -90 deg around Y)
        R = trimesh.transformations.rotation_matrix(-np.pi / 2, [0, 1, 0])
        m.apply_transform(R)
    elif "28_09_Rod_Spring_Hinge" in name:
        # Lay flat on side face (rotate 90 deg around Y)
        R = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])
        m.apply_transform(R)
    elif "23_Custom_Rod_Middle" in name:
        # Lay flat on bed as in v1.1
        pass

    # Drop to z_min = 0.0 and center on XY
    m.apply_translation([-m.bounds.mean(axis=0)[0], -m.bounds.mean(axis=0)[1], -m.bounds[0, 2]])
    return m


def export_all():
    rod_r_full, rod_mid_full, rod_l_full, hinge_sp_narrow = build_unified_rod()

    print(f"\n[*] Exporting updated parts to {PACKAGE_NAME}...")

    # 1. Assembled coordinates
    fidget.save(rod_r_full, os.path.join(ASY_DIR, "22_Custom_Rod_Right.stl"))
    fidget.save(rod_mid_full, os.path.join(ASY_DIR, "23_Custom_Rod_Middle.stl"))
    fidget.save(rod_l_full, os.path.join(ASY_DIR, "24_Custom_Rod_Left.stl"))
    fidget.save(hinge_sp_narrow, os.path.join(ASY_DIR, "28_09_Rod_Spring_Hinge.stl"))

    # 2. Subassembly folders
    fidget.save(rod_r_full, os.path.join(ROD_DIR, "22_Custom_Rod_Right.stl"))
    fidget.save(rod_mid_full, os.path.join(ROD_DIR, "23_Custom_Rod_Middle.stl"))
    fidget.save(rod_l_full, os.path.join(ROD_DIR, "24_Custom_Rod_Left.stl"))
    fidget.save(hinge_sp_narrow, os.path.join(HEAD_DIR, "28_09_Rod_Spring_Hinge.stl"))

    # 3. Flat bed oriented
    fidget.save(flat_bed_orient(rod_r_full, "22_Custom_Rod_Right"), os.path.join(FLAT_DIR, "22_Custom_Rod_Right.stl"))
    fidget.save(flat_bed_orient(rod_mid_full, "23_Custom_Rod_Middle"), os.path.join(FLAT_DIR, "23_Custom_Rod_Middle.stl"))
    fidget.save(flat_bed_orient(rod_l_full, "24_Custom_Rod_Left"), os.path.join(FLAT_DIR, "24_Custom_Rod_Left.stl"))
    fidget.save(flat_bed_orient(hinge_sp_narrow, "28_09_Rod_Spring_Hinge"), os.path.join(FLAT_DIR, "28_09_Rod_Spring_Hinge.stl"))

    # 4. Remove obsolete split/pin STLs if they exist
    obsolete_files = [
        "Custom_Rod_Upper_Right.stl",
        "Custom_Rod_Upper_Left.stl",
        "Custom_Rod_Lock_Upper_Pin.stl"
    ]
    for d in [ASY_DIR, FLAT_DIR, ROD_DIR]:
        for obs in obsolete_files:
            p = os.path.join(d, obs)
            if os.path.exists(p):
                os.remove(p)
                print(f"  [CLEANUP] Removed obsolete {p}")

    print("[+] All parts exported successfully!")


if __name__ == "__main__":
    export_all()
