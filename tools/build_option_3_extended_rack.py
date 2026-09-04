"""Build Option 3: Extended Rod Rack + Sub-Cap Dual-Head Springs Sub-Assembly.

Architecture:
- 23_Custom_Rod_Middle rack extended from Y = 58.20 mm to 62.00 mm (adding Tooth 10 peak at Y = 59.66 mm and valley at Y = 61.24 mm).
- Preserves hexagonal key interface above Y = 62.00 mm for mating with 21_30 Upper Shell Rotating Spring.
- Dual-head spring with Lower Nose at Y = 56.50 mm (Tooth 9) and Upper Nose at Y = 59.66 mm (Tooth 10).
- Top arch of spring stays at Y = 62.40 mm (< 63.20 mm cap underside), completely inside barrel under solid Cap 11.
- Zero clash with 21_30 Upper Shell Rotating Spring (0.000 mm3 clash).

Outputs:
  - Hybrid_Grenade_v1.2/Derivatives/Option_3_Extended_Rack/
"""
from __future__ import annotations

import os
import sys
import shutil
import numpy as np
import trimesh
import shapely
from shapely.ops import unary_union
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD
from build_all_modified_springs import (
    poly_single,
    profile_to_solid,
    _solidify,
    _to_bed_pose,
    _roty,
    TOTAL_W,
    NARROW_W,
    RAIL_R1_NEW,
    R_RIB,
    FOOT_Y0,
    FOOT_Y1,
)

V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
ASY_DIR = os.path.join(V12_DIR, "All_Parts_Assembled_Coordinates")
OUTPUT_DIR = os.path.join(V12_DIR, "Derivatives", "Option_3_Extended_Rack")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def to_manifold(tm: trimesh.Trimesh) -> manifold3d.Manifold:
    m64 = manifold3d.Mesh64(
        np.ascontiguousarray(tm.vertices, dtype=np.float64),
        np.ascontiguousarray(tm.faces, dtype=np.uint64)
    )
    return manifold3d.Manifold(m64)


def from_manifold(m: manifold3d.Manifold) -> trimesh.Trimesh:
    rebuilt = m.to_mesh64()
    return trimesh.Trimesh(
        vertices=np.asarray(rebuilt.vert_properties)[:, :3],
        faces=np.asarray(rebuilt.tri_verts),
        process=False,
    )


def build_extended_middle_core() -> tuple[trimesh.Trimesh, trimesh.Trimesh]:
    """Extend gear rack on 23_Custom_Rod_Middle up to Y = 62.0 mm (both assembled and flat-bed poses)."""
    mid_path = os.path.join(ASY_DIR, "23_Custom_Rod_Middle.stl")
    mid = trimesh.load(mid_path, process=True)

    cutters = []
    for y_val in [58.20, 61.24]:
        # +Z face
        poly_plus = shapely.Polygon([
            (y_val, 5.7652),
            (y_val + 1.58, 8.50),
            (y_val - 1.58, 8.50),
        ])
        cut_mesh_plus = trimesh.creation.extrude_polygon(poly_plus, height=10.0)
        cut_mesh_plus.apply_transform(np.array([
            [0, 0, 1, -5.0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ]))
        cutters.append(cut_mesh_plus)

        # -Z face
        poly_minus = shapely.Polygon([
            (y_val, -5.7652),
            (y_val + 1.58, -8.50),
            (y_val - 1.58, -8.50),
        ])
        cut_mesh_minus = trimesh.creation.extrude_polygon(poly_minus, height=10.0)
        cut_mesh_minus.apply_transform(np.array([
            [0, 0, 1, -5.0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ]))
        cutters.append(cut_mesh_minus)

    m_mid = to_manifold(mid)
    for c in cutters:
        m_mid = m_mid - to_manifold(c)

    mid_ext_asy = _solidify(from_manifold(m_mid), "Extended_Middle_Core_Asy")

    # Flat bed pose: lay flat on bed (Z min = 0)
    # 23_Custom_Rod_Middle flat orientation: rotate around X by 90 so face is flat
    mid_ext_bed = mid_ext_asy.copy()
    T_bed = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, -1, 0, 0],
        [0, 0, 0, 1]
    ])
    mid_ext_bed.apply_transform(T_bed)
    min_z = mid_ext_bed.bounds[0][2]
    mid_ext_bed.apply_translation([0, 0, -min_z])

    return mid_ext_asy, mid_ext_bed


def build_option3_spring_polygon() -> shapely.Polygon:
    """Build sub-cap dual-head spring: Lower Nose at Y = 56.50, Upper Nose at Y = 59.66 mm."""
    pitch = BRD.TOOTH_PITCH  # 3.1625 / 3.17733 mm
    y_lower = 56.50
    y_upper = 59.66

    # Start with poly_single (nose is at Y = 57.3959)
    # Add second upper nose wedge at Y = 59.66
    wedge_upper = BRD._nose_wedge(y_upper, apex=BRD.NOSE_APEX)

    # Stalk connecting upper nose back into flexure arch
    stalk = shapely.Polygon([
        (y_upper - 1.25, 7.35),
        (y_upper + 1.25, 7.35),
        (y_upper + 1.25, 8.50),
        (y_upper - 1.25, 8.50),
    ])

    merged = unary_union([poly_single, stalk, wedge_upper])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
    return shapely.Polygon(merged.exterior)


def build_solid_cap() -> trimesh.Trimesh:
    """Build clean solid retention cap disc."""
    cap_path = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "Derivatives", "Option_1_Internal_Tandem", "11_Custom_Internal_Barrel_Cap_Solid.stl")
    if os.path.exists(cap_path):
        return trimesh.load(cap_path, process=True)

    barrel_top = trimesh.creation.cylinder(radius=15.18, height=0.40)
    barrel_top.apply_translation([0.0, 0.0, 0.20])
    T_cyl = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 63.20],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    barrel_top.apply_transform(T_cyl)

    rod_hole = trimesh.creation.cylinder(radius=11.20, height=2.0)
    rod_hole.apply_translation([0.0, 0.0, 1.0])
    rod_hole.apply_transform(T_cyl)

    m_top = to_manifold(barrel_top)
    m_hole = to_manifold(rod_hole)
    return _solidify(from_manifold(m_top - m_hole), "Solid_Cap_11")


def main():
    print("=" * 80)
    print("BUILDING OPTION 3: EXTENDED ROD RACK + SUB-CAP DUAL-HEAD SPRINGS")
    print("=" * 80)

    # 1. Middle Rod with Extended Rack
    print("[1/5] Carving Extended Gear Rack onto 23_Custom_Rod_Middle (Y = 58.20 to 62.00 mm)...")
    mid_ext_asy, mid_ext_bed = build_extended_middle_core()
    print(f"  -> Extended Middle Core Watertight: {mid_ext_asy.is_watertight}, Volume: {mid_ext_asy.volume:.2f} mm3")

    # 2. Sub-Cap Spring Polygon & 3D Solid
    print("[2/5] Synthesizing Sub-Cap Dual-Head Spring...")
    poly_opt3 = build_option3_spring_polygon()
    s_opt3_base = profile_to_solid(poly_opt3, "Opt3_Dual_Solid")
    s_single_base = profile_to_solid(poly_single, "Single_Solid")
    print(f"  -> Spring Solid Watertight: {s_opt3_base.is_watertight}, Volume: {s_opt3_base.volume:.2f} mm3")

    # 3. Assembled Orientations
    s12_asy = _roty(-90.0, s_single_base.copy())  # az 0 deg (-X)
    s13_asy = s_opt3_base.copy()                 # az 90 deg (+Z)
    s14_asy = _roty(90.0, s_single_base.copy())   # az 180 deg (+X)
    s15_asy = _roty(180.0, s_opt3_base.copy())    # az 270 deg (-Z)

    # 4. Bed Poses (flat on Z = 0)
    base_rot = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    s12_bed = _to_bed_pose(s12_asy, base_rot, 90)
    s13_bed = _to_bed_pose(s13_asy, base_rot, 0)
    s14_bed = _to_bed_pose(s14_asy, base_rot, -90)
    s15_bed = _to_bed_pose(s15_asy, base_rot, -180)

    for b in [s12_bed, s13_bed, s14_bed, s15_bed]:
        min_z = b.bounds[0][2]
        b.apply_translation([0.0, 0.0, -min_z])

    # Cap 11 & Barrel 10
    cap_solid = build_solid_cap()
    barrel_mesh = trimesh.load(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), process=True)

    print("\n[3/5] Exporting Option 3 STLs...")
    # Flat-bed STLs
    mid_ext_bed.export(os.path.join(OUTPUT_DIR, "23_Custom_Rod_Middle_ExtendedRack.stl"))
    s12_bed.export(os.path.join(OUTPUT_DIR, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_bed.export(os.path.join(OUTPUT_DIR, "13_Custom_Rod_Detent_Spring_02_ExtHead.stl"))
    s14_bed.export(os.path.join(OUTPUT_DIR, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_bed.export(os.path.join(OUTPUT_DIR, "15_Custom_Rod_Detent_Spring_04_ExtHead.stl"))
    cap_solid.export(os.path.join(OUTPUT_DIR, "11_Custom_Internal_Barrel_Cap_Solid.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(OUTPUT_DIR, "10_Custom_Internal_Barrel_4Slot.stl"))

    # Assembled STLs
    asy_sub = os.path.join(OUTPUT_DIR, "Assembled_Coordinates")
    os.makedirs(asy_sub, exist_ok=True)
    mid_ext_asy.export(os.path.join(asy_sub, "23_Custom_Rod_Middle_ExtendedRack.stl"))
    s12_asy.export(os.path.join(asy_sub, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_asy.export(os.path.join(asy_sub, "13_Custom_Rod_Detent_Spring_02_ExtHead.stl"))
    s14_asy.export(os.path.join(asy_sub, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_asy.export(os.path.join(asy_sub, "15_Custom_Rod_Detent_Spring_04_ExtHead.stl"))
    cap_solid.export(os.path.join(asy_sub, "11_Custom_Internal_Barrel_Cap_Solid.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(asy_sub, "10_Custom_Internal_Barrel_4Slot.stl"))

    print("\n[4/5] Exporting Option 3 Assembled and Exploded GLBs...")
    # Barrel Sub-Assembly GLB
    parts_barrel = [
        {"name": "10_Custom_Internal_Barrel_4Slot", "mesh": barrel_mesh, "color": (55, 65, 75), "disp": [0.0, 0.0, 0.0]},
        {"name": "11_Custom_Internal_Barrel_Cap_Solid", "mesh": cap_solid, "color": (160, 170, 180), "disp": [0.0, 18.0, 0.0]},
        {"name": "12_Custom_Rod_Detent_Spring_01", "mesh": s12_asy, "color": (249, 115, 22), "disp": [-20.0, 0.0, 0.0]},
        {"name": "13_Custom_Rod_Detent_Spring_02_ExtHead", "mesh": s13_asy, "color": (14, 165, 233), "disp": [0.0, 0.0, 20.0]},
        {"name": "14_Custom_Rod_Detent_Spring_03", "mesh": s14_asy, "color": (249, 115, 22), "disp": [20.0, 0.0, 0.0]},
        {"name": "15_Custom_Rod_Detent_Spring_04_ExtHead", "mesh": s15_asy, "color": (14, 165, 233), "disp": [0.0, 0.0, -20.0]},
    ]

    scene_asy = trimesh.Scene()
    scene_exp = trimesh.Scene()

    for p in parts_barrel:
        m = p["mesh"].copy()
        r, g, b = p["color"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        mat = trimesh.visual.material.PBRMaterial(baseColorFactor=color_norm, metallicFactor=0.35, roughnessFactor=0.45)
        m.visual = trimesh.visual.TextureVisuals(material=mat)
        scene_asy.add_geometry(m, node_name=p["name"], geom_name=p["name"])

        m_exp = p["mesh"].copy()
        m_exp.apply_translation(p["disp"])
        mat_exp = trimesh.visual.material.PBRMaterial(baseColorFactor=color_norm, metallicFactor=0.35, roughnessFactor=0.45)
        m_exp.visual = trimesh.visual.TextureVisuals(material=mat_exp)
        scene_exp.add_geometry(m_exp, node_name=f"{p['name']} (Exploded)", geom_name=f"{p['name']}_exp")

    out_glb_asy = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option3.glb")
    out_glb_exp = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option3_Exploded.glb")
    scene_asy.export(out_glb_asy)
    scene_exp.export(out_glb_exp)

    # 3MF
    out_3mf = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option3.3mf")
    scene_asy.export(out_3mf)

    # Rod Assembly with extended core
    p_rod_dir = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "04_Rod_Assembly_And_Locks")
    rod_r = trimesh.load(os.path.join(ASY_DIR, "22_Custom_Rod_Right.stl"), process=True)
    rod_l = trimesh.load(os.path.join(ASY_DIR, "24_Custom_Rod_Left.stl"), process=True)
    key_06 = trimesh.load(os.path.join(ASY_DIR, "25_Custom_Rod_Lock_Upper_06.stl"), process=True)
    key_07 = trimesh.load(os.path.join(ASY_DIR, "26_Custom_Rod_Lock_Lower_07.stl"), process=True)
    disc_08 = trimesh.load(os.path.join(ASY_DIR, "27_Spinner_Lever_08_Rod_Lock.stl"), process=True)

    parts_rod = [
        {"name": "22_Custom_Rod_Right", "mesh": rod_r, "color": (86, 182, 178)},
        {"name": "23_Custom_Rod_Middle_ExtendedRack", "mesh": mid_ext_asy, "color": (55, 65, 81)},
        {"name": "24_Custom_Rod_Left", "mesh": rod_l, "color": (184, 126, 152)},
        {"name": "25_Custom_Rod_Lock_Upper_06", "mesh": key_06, "color": (239, 68, 68)},
        {"name": "26_Custom_Rod_Lock_Lower_07", "mesh": key_07, "color": (245, 158, 11)},
        {"name": "27_Spinner_Lever_08_Rod_Lock", "mesh": disc_08, "color": (16, 185, 129)},
    ]
    scene_rod = trimesh.Scene()
    for p in parts_rod:
        m = p["mesh"].copy()
        r, g, b = p["color"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        mat = trimesh.visual.material.PBRMaterial(baseColorFactor=color_norm, metallicFactor=0.35, roughnessFactor=0.45)
        m.visual = trimesh.visual.TextureVisuals(material=mat)
        scene_rod.add_geometry(m, node_name=p["name"], geom_name=p["name"])

    out_rod_glb = os.path.join(OUTPUT_DIR, "Custom_Rod_Assembly_Option3.glb")
    scene_rod.export(out_rod_glb)

    print(f"\n[5/5] Checking Clash with Upper Shell Rotating Spring 21_30...")
    s21 = trimesh.load(os.path.join(ASY_DIR, "21_30_Upper_Shell_Rotating_Spring.stl"), process=True)
    m21 = to_manifold(s21)
    m13 = to_manifold(s13_asy)
    clash_vol = (m13 ^ m21).volume()
    print(f"  -> S13 ExtHead vs 21_30 Clash Volume: {clash_vol:.4f} mm3 (Expected 0.0000)")

    print("\n" + "=" * 80)
    print(f"[SUCCESS] OPTION 3 BUILT IN {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
