"""Build the Concave Upper Station and Lowered Rod & Head Assembly for Hybrid Grenade.

This script implements Proposal 1:
1. Adds a conical concave dish to 18_27_Upper_Shell_Top.stl (mouth r=12.00 at Y=74.65,
   funneling down to r=9.20 at Y=68.00, providing a 3.51 mm wide flat top contact rim with 303 mm2 area).
2. Trims 21_30_Upper_Shell_Rotating_Spring.stl above Y=67.20 mm so it sits beneath the dish floor
   while preserving its 3 detent click arms at Y=64.00..66.50 mm.
3. Trims 22_Custom_Rod_Right.stl and 24_Custom_Rod_Left.stl above Y=67.20 mm, preserving full
   hexagonal keying inside the trimmed rotating spring.
4. Compacts 28_09_Rod_Spring_Hinge_T_Head.stl to Y in [59.50, 74.19] mm (height 14.69 mm).
5. Lowers the yoke of 23_Custom_Rod_Middle.stl by dy = -11.46 mm (pin at Y=81.00 mm, ears to Y=88.16 mm),
   with the internal spring pocket cut cleanly above upper key 06.
6. Translates the entire 8-piece folding head assembly downward by dy = -11.46 mm so the handle
   cheeks nest 4.98 mm below the outer top rim into the concave dish with zero neck gap.

All output lands in All_Parts_Assembled_Coordinates/ protected by package_paths.guard().
"""
from __future__ import annotations

import os
import sys
import numpy as np
import trimesh
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import package_paths
import custom

DY = -11.46172105985224  # exact shift to place hinge pin at Y = 81.0000 mm

P_SHIFT = 3.17733  # exact shift = 1 rod tooth pitch to preserve rack tooth phasing

ASY_DIR = package_paths.ASSEMBLED_DIR
V12_ASY_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Assembled_Coordinates")


def to_manifold(tm: trimesh.Trimesh) -> manifold3d.Manifold:
    props = np.ascontiguousarray(tm.vertices, dtype=np.float32)
    tris = np.ascontiguousarray(tm.faces, dtype=np.uint32)
    return manifold3d.Manifold(manifold3d.Mesh(vert_properties=props, tri_verts=tris))


def to_trimesh(m: manifold3d.Manifold) -> trimesh.Trimesh:
    mesh = m.to_mesh()
    return trimesh.Trimesh(
        vertices=mesh.vert_properties[:, :3],
        faces=mesh.tri_verts,
        process=True
    )


def build_concave_shell_top(n_teeth: int = 18) -> trimesh.Trimesh:
    print(f"  [*] Building 18_27_Upper_Shell_Top with concave conical dish ({n_teeth}-tooth ratchet)...")
    path = os.path.join(V12_ASY_DIR, "18_27_Upper_Shell_Top.stl")
    shell_orig = trimesh.load(path)
    m_shell = to_manifold(shell_orig)

    # 1. Plane cut at y_top = 74.65 mm to create a true flat top rim and provide clearance under folded lever
    y_top = 74.65
    r_mouth = 12.00
    r_floor = 9.20

    # Solidify upper bore between Y=68.20 and y_top (radius 13.80 mm)
    collar_h = y_top - 68.20
    m_collar = manifold3d.Manifold.cylinder(
        height=collar_h, radius_low=13.80, radius_high=13.80, circular_segments=128
    ).rotate([-90, 0, 0]).translate([0.0, 68.20, 0.0])

    # Plane cut above y_top
    m_top_cut = manifold3d.Manifold.cube(
        [100.0, 20.0, 100.0], center=True
    ).translate([0.0, y_top + 10.0, 0.0])
    m_solidified = (m_shell + m_collar) - m_top_cut

    # 2. Conical dish cutter from Y=68.00 (r=9.20) to y_top (r=12.00)
    cone_h = y_top - 68.00
    m_cone = manifold3d.Manifold.cylinder(
        height=cone_h + 1.0, radius_low=r_floor, radius_high=r_mouth + (r_mouth - r_floor) / cone_h * 1.0, circular_segments=128
    ).rotate([-90, 0, 0]).translate([0.0, 68.00, 0.0])

    # Through-bore from Y=67.00 to 68.00 of radius 9.20 mm
    m_bore = manifold3d.Manifold.cylinder(
        height=2.0, radius_low=r_floor, radius_high=r_floor, circular_segments=128
    ).rotate([-90, 0, 0]).translate([0.0, 67.00, 0.0])

    m_dish_cut = m_solidified - (m_cone + m_bore)

    if n_teeth == 18:
        # Solidify tooth chamber between Y=63.75 and 66.80 mm
        m_fill = manifold3d.Manifold.cylinder(
            height=3.05, radius_low=17.50, radius_high=17.50, circular_segments=128
        ).rotate([-90, 0, 0]).translate([0.0, 63.75, 0.0])
        m_solid_teeth = m_dish_cut + m_fill

        # 18-tooth directional ratchet cutter (20° pitch)
        import shapely.geometry as sg
        th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
        pitch = 2 * np.pi / 18.0
        u = np.mod(th, pitch) / pitch
        th_ramp = 0.80
        r_cut = np.where(
            u < th_ramp,
            17.45 - (17.45 - 16.30) * (u / th_ramp) ** 0.80,
            16.30 + (17.45 - 16.30) * ((u - th_ramp) / (1.0 - th_ramp))
        )
        poly_pts = np.column_stack([r_cut * np.cos(th), r_cut * np.sin(th)])
        poly_cutter = sg.Polygon(poly_pts)
        tm_cut = trimesh.creation.extrude_polygon(poly_cutter, height=3.20)
        V = tm_cut.vertices
        V_new = np.column_stack([V[:, 0], 63.70 + V[:, 2], V[:, 1]])
        F_new = tm_cut.faces[:, [0, 2, 1]]
        tm_cut_3d = trimesh.Trimesh(vertices=V_new, faces=F_new, process=True)
        m_cut = to_manifold(tm_cut_3d)

        m_res = m_solid_teeth - m_cut
    else:
        m_res = m_dish_cut

    res = to_trimesh(m_res)
    assert res.is_watertight, "18_27_Upper_Shell_Top is not watertight!"
    assert len(res.split(only_watertight=False)) == 1, "18_27_Upper_Shell_Top is multi-body!"
    return res


def build_trimmed_rotating_spring():
    print("  [*] Building definitive One-Way Ratchet 21_30_Upper_Shell_Rotating_Spring...")
    import build_modified_rotating_spring as BRS
    mesh, _ = BRS.build_smooth_solid_click_rotating_spring()
    return mesh


def build_trimmed_rod_clamp(filename: str):
    print(f"  [*] Trimming {filename} above Y=67.20 mm and shifting Key 06 pocket down by {P_SHIFT:.2f} mm...")
    path = os.path.join(V12_ASY_DIR, filename)
    rod_orig = trimesh.load(path)
    m_rod = to_manifold(rod_orig)

    m_box = manifold3d.Manifold.cube(
        [60.0, 30.0, 60.0], center=True
    ).translate([0.0, 67.20 + 15.0, 0.0])
    m_trimmed = m_rod - m_box

    # Shift Key 06 pocket down by P_SHIFT:
    # In v1.2, pocket is at Y in [48.6536, 58.1858], Z in [-1.08, 1.08]
    # 1. Fill old upper pocket slice [58.1858 - P_SHIFT, 58.1858] using solid periodic rod slice from [45.4763, 48.6536] translated by 3 * P_SHIFT
    x_center = -5.0 if "Right" in filename else 5.0
    box_fill_src = manifold3d.Manifold.cube([20.0, P_SHIFT, 20.0], center=True).translate([x_center, 45.4763 + P_SHIFT / 2.0, 0.0])
    m_fill = (m_trimmed ^ box_fill_src).translate([0.0, 3 * P_SHIFT, 0.0])
    # 2. Cut new pocket at Y in [48.6536 - P_SHIFT, 58.1858 - P_SHIFT]
    cutter_new = manifold3d.Manifold.cube([20.0, 9.5322, 2.16], center=True).translate([x_center, 58.1858 - P_SHIFT - 9.5322 / 2.0, 0.0])

    m_res = (m_trimmed + m_fill) - cutter_new
    res = to_trimesh(m_res)
    assert res.is_watertight, f"{filename} is not watertight!"
    assert len(res.split(only_watertight=False)) == 1, f"{filename} is multi-body!"
    return res


def build_shifted_rod_lock_upper():
    print(f"  [*] Building shifted 25_Custom_Rod_Lock_Upper_06 (down by {P_SHIFT:.2f} mm)...")
    path = os.path.join(V12_ASY_DIR, "25_Custom_Rod_Lock_Upper_06.stl")
    key_orig = trimesh.load(path)
    key_orig.apply_translation([0.0, -P_SHIFT, 0.0])
    assert key_orig.is_watertight, "25_Custom_Rod_Lock_Upper_06 is not watertight!"
    assert len(key_orig.split(only_watertight=False)) == 1, "25_Custom_Rod_Lock_Upper_06 is multi-body!"
    return key_orig


def build_compact_hinge_spring():
    y_floor = 59.50 - P_SHIFT
    print(f"  [*] Building compact 28_09_Rod_Spring_Hinge_T_Head (Y={y_floor:.2f}..74.19 mm)...")
    path = os.path.join(V12_ASY_DIR, "28_09_Rod_Spring_Hinge_T_Head.stl")
    sp_orig = trimesh.load(path)
    m_sp = to_manifold(sp_orig)

    # 1. T-head translated by DY (kept at nominal cam engagement height)
    box_head = manifold3d.Manifold.cube(
        [50.0, 20.0, 50.0], center=True
    ).translate([0.0, 89.5, 0.0])
    m_head = (m_sp ^ box_head).translate([0.0, DY, 0.0])

    # 2. Base foot: Y in [y_floor, y_floor + 3.0]
    m_foot = manifold3d.Manifold.cube(
        [6.00, 3.00, 7.24], center=True
    ).translate([0.0, y_floor + 1.50, -0.05])

    # 3. Flexure section: scaled to span Y in [y_floor + 3.0, 68.04]
    box_flex = manifold3d.Manifold.cube(
        [50.0, 9.5, 50.0], center=True
    ).translate([0.0, 74.75, 0.0])
    m_flex = m_sp ^ box_flex
    bb_flex = m_flex.bounding_box()
    h_orig_flex = bb_flex[4] - bb_flex[1]
    scale_y = (68.04 - (y_floor + 3.0)) / h_orig_flex
    m_flex_scaled = m_flex.translate([0.0, -bb_flex[1], 0.0]).scale([1.0, scale_y, 1.0]).translate([0.0, y_floor + 3.0, 0.0])

    m_res = m_foot + m_flex_scaled + m_head
    res = to_trimesh(m_res)
    assert res.is_watertight, "28_09_Rod_Spring_Hinge_T_Head is not watertight!"
    assert len(res.split(only_watertight=False)) == 1, "28_09_Rod_Spring_Hinge_T_Head is multi-body!"
    return res


def build_lowered_rod_middle():
    y_floor = 59.50 - P_SHIFT
    y_roof_base = 74.50 - P_SHIFT
    print(f"  [*] Building lowered 23_Custom_Rod_Middle with shifted spring slot & Key 06 (roof apex at {y_roof_base + 3.75:.2f} mm)...")
    # Load from pristine frozen v1.2
    v12_rod_path = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Assembled_Coordinates", "23_Custom_Rod_Middle.stl")
    rod_orig = trimesh.load(v12_rod_path)
    m_rod = to_manifold(rod_orig)

    # In v1.2, the yoke ears were above Y = 78.00 mm (pin at Y = 92.46 mm).
    # Shifting the upper yoke by DY = -11.4617 mm places the pin at Y = 81.0000 mm.
    # The upper yoke lands at Y >= (78.00 + DY) = 66.5383 mm.
    y_join = 78.00 + DY

    # Lower body: Y <= y_join from v1.2 (preserves lower gear rack, keys 06 and 07, and hex profile)
    m_low_box = manifold3d.Manifold.cube(
        [50.0, 100.0, 50.0], center=True
    ).translate([0.0, y_join - 50.0, 0.0])
    m_lower = m_rod ^ m_low_box

    # Shift Key 06 transverse pocket on m_lower:
    box_fill_src = manifold3d.Manifold.cube([10.0, P_SHIFT, 20.0], center=True).translate([0.0, 45.4763 + P_SHIFT / 2.0, 0.0])
    m_fill = (m_lower ^ box_fill_src).translate([0.0, 3 * P_SHIFT, 0.0])
    cutter_new = manifold3d.Manifold.cube([10.0, 9.5322, 2.16], center=True).translate([0.0, 58.1858 - P_SHIFT - 9.5322 / 2.0, 0.0])
    m_lower_shifted = (m_lower + m_fill) - cutter_new

    # Upper yoke: Y >= 78.00 from v1.2 translated downward by DY
    m_up_box = manifold3d.Manifold.cube(
        [50.0, 100.0, 50.0], center=True
    ).translate([0.0, 78.00 + 50.0, 0.0])
    m_upper = (m_rod ^ m_up_box).translate([0.0, DY, 0.0])

    m_joined = m_lower_shifted + m_upper

    # Cut the spring slot:
    # 1. Full through-slot from Y = y_floor to Y = y_roof_base
    # Width in X: 15.0 mm (wider than 7.0 mm rod, completely open on left +X and right -X sides)
    # Width in Z: 7.50 mm (Z in [-3.75, +3.75] mm, gives 0.26 mm clearance around 7.24 mm spring foot)
    slot_h = y_roof_base - y_floor
    m_box_slot = manifold3d.Manifold.cube(
        [15.0, slot_h, 7.50], center=True
    ).translate([0.0, (y_floor + y_roof_base) / 2.0, 0.0])

    # 2. 45° inverted chevron/arch roof cutter for support-free 3D printing:
    # A cube rotated 45° around X has diagonal 7.50 mm in Z (L = 7.50 / sqrt(2) = 5.3033 mm)
    # Centered at Y = y_roof_base, Z = 0.0 mm.
    # It cuts a 45.0° self-supporting arch rising from Z = ±3.75 mm at Y = y_roof_base to the apex at Y = y_roof_base + 3.75 mm.
    L = 7.50 / np.sqrt(2.0)
    m_roof = manifold3d.Manifold.cube(
        [15.0, L, L], center=True
    ).rotate([45, 0, 0]).translate([0.0, y_roof_base, 0.0])

    m_final = m_joined - (m_box_slot + m_roof)

    res = to_trimesh(m_final)
    assert res.is_watertight, "23_Custom_Rod_Middle is not watertight!"
    assert len(res.split(only_watertight=False)) == 1, "23_Custom_Rod_Middle is multi-body!"
    return res


def lower_head_assembly():
    print(f"  [*] Lowering all 8 head parts by {DY:.2f} mm...")
    head_files = [
        "29_Custom_Handle_Left.stl",
        "30_Custom_Handle_Right.stl",
        "31_Custom_Ring_Spinner.stl",
        "32_Spinner_Lever_05_Gear.stl",
        "33_Spinner_Lever_04_Spring.stl",
        "34_Custom_16_Handle_Lock_Neck.stl",
        "35_Custom_16_Handle_Lock_Pod.stl",
        "36_15_Handle_Rotating_Lock_D_Pin.stl",
    ]
    lowered = {}
    for hf in head_files:
        path = os.path.join(V12_ASY_DIR, hf)
        tm = trimesh.load(path)
        tm.apply_translation([0.0, DY, 0.0])
        assert tm.is_watertight, f"{hf} is not watertight!"
        lowered[hf] = tm
    return lowered


def main():
    print("=" * 70)
    print("BUILD CONCAVE UPPER STATION & LOWERED ROD/HEAD (PROPOSAL 1)")
    print(f"Package: {package_paths.PACKAGE_NAME}")
    print(f"Hinge Pin Delta Y: {DY:.4f} mm -> New Hinge Pin Y = 81.0000 mm")
    print(f"Rack Tooth Pitch Shift: {P_SHIFT:.4f} mm downward for Key 06 & Spring Cavity")
    print("=" * 70)

    # 1. Build modified parts
    shell_top = build_concave_shell_top()
    rot_spring = build_trimmed_rotating_spring()
    rod_r = build_trimmed_rod_clamp("22_Custom_Rod_Right.stl")
    rod_l = build_trimmed_rod_clamp("24_Custom_Rod_Left.stl")
    rod_k6 = build_shifted_rod_lock_upper()
    hinge_spring = build_compact_hinge_spring()
    rod_m = build_lowered_rod_middle()
    head_parts = lower_head_assembly()

    # 2. Save all modified parts into All_Parts_Assembled_Coordinates/ and subassemblies
    print("\n[*] Saving updated parts to All_Parts_Assembled_Coordinates/...")
    shell_top.export(package_paths.guard(os.path.join(ASY_DIR, "18_27_Upper_Shell_Top.stl")))
    rot_spring.export(package_paths.guard(os.path.join(ASY_DIR, "21_30_Upper_Shell_Rotating_Spring.stl")))
    rod_r.export(package_paths.guard(os.path.join(ASY_DIR, "22_Custom_Rod_Right.stl")))
    rod_m.export(package_paths.guard(os.path.join(ASY_DIR, "23_Custom_Rod_Middle.stl")))
    rod_l.export(package_paths.guard(os.path.join(ASY_DIR, "24_Custom_Rod_Left.stl")))
    rod_k6.export(package_paths.guard(os.path.join(ASY_DIR, "25_Custom_Rod_Lock_Upper_06.stl")))
    hinge_spring.export(package_paths.guard(os.path.join(ASY_DIR, "28_09_Rod_Spring_Hinge_T_Head.stl")))

    for name, tm in head_parts.items():
        tm.export(package_paths.guard(os.path.join(ASY_DIR, name)))

    print("[+] All parts successfully saved and verified watertight!")


if __name__ == "__main__":
    main()
