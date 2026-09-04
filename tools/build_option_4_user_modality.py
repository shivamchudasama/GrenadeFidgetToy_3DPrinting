"""Build Option 4: Extended Spring to Top Tooth (User Requested Modality).

Modality Concept:
- Extends Springs 13 and 15 upward through Cap 11 (reaching Y = 72.45 mm).
- Positions the primary detent head at Y = 56.50 mm so that at neutral/resting state (ΔY = 0),
  it rests directly at the top-most tooth (Tooth 9) of 23_Custom_Rod_Middle.
- As the rod moves through its operational reciprocating stroke (ΔY = 0 to 24 mm),
  every single tooth (Teeth 9 down to 1) passes through the detent head, clicking for every tooth.
- Includes full geometric capture of the upper extension through Cap 11 and visual analysis of
  the upper station interface with 21_30 Upper Shell Rotating Spring.

Outputs:
  - Hybrid_Grenade_v1.2/Derivatives/Option_4_Extended_Top_Tooth/
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
OUTPUT_DIR = os.path.join(V12_DIR, "Derivatives", "Option_4_Extended_Top_Tooth")
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


def build_option4_polygon() -> shapely.Polygon:
    """Create 2D profile for extended spring resting at the top-most tooth."""
    pitch = BRD.TOOTH_PITCH  # 3.17733 mm
    y_top_tooth = 56.50      # Tooth 9 peak / valley
    y_lower_tooth = 47.01    # Tooth 6 (3 pitches below)

    # 1. Extended spine rising up to Y = 72.448 mm
    pitch_shift = 3.0 * pitch  # 9.532 mm
    spine_bridge = shapely.Polygon([
        (60.00, 10.250),
        (60.00, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, 10.250),
        (60.00, 10.250)
    ])

    # 2. Upper arch
    upper_arch = shapely.Polygon([
        (69.00, 7.80),
        (69.00, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, 7.80),
    ])

    # 3. Descending inner flexure reaching down to Y = 56.50 mm (top-most tooth)
    descender = shapely.Polygon([
        (y_top_tooth, 7.35),
        (y_top_tooth, 8.80),
        (70.00, 8.80),
        (70.00, 7.35),
    ])

    # 4. Detent nose wedges:
    # Primary head at top-most tooth Y = 56.50 mm
    wedge_top = BRD._nose_wedge(y_top_tooth, apex=BRD.NOSE_APEX)
    # Secondary tandem head at Tooth 6 Y = 47.01 mm
    wedge_lower = BRD._nose_wedge(y_lower_tooth, apex=BRD.NOSE_APEX)
    stalk_lower = shapely.Polygon([(45.8, 7.35), (48.2, 7.35), (48.2, 8.45), (45.8, 8.45)])

    merged = unary_union([poly_single, spine_bridge, upper_arch, descender, wedge_top, wedge_lower, stalk_lower])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
    return shapely.Polygon(merged.exterior)


def main():
    print("=" * 80)
    print("BUILDING OPTION 4: EXTENDED SPRING TO TOP TOOTH (USER MODALITY)")
    print("=" * 80)

    # 1. 2D Polygon
    print("[1/5] Synthesizing Extended Top-Tooth 2D Polygon...")
    poly_opt4 = build_option4_polygon()
    print(f"  -> Polygon Valid: {poly_opt4.is_valid}, Area: {poly_opt4.area:.2f} mm2, Bounds: {poly_opt4.bounds}")

    # 2. 3D Solid
    print("[2/5] Extruding 3D watertight solid...")
    s_opt4_base = profile_to_solid(poly_opt4, "Opt4_ExtTopTooth_Solid")
    s_single_base = profile_to_solid(poly_single, "Single_Solid")
    print(f"  -> Solid Watertight: {s_opt4_base.is_watertight}, Volume: {s_opt4_base.volume:.2f} mm3")

    # 3. Assembled Orientations
    s12_asy = _roty(-90.0, s_single_base.copy())  # az 0 deg (-X)
    s13_asy = s_opt4_base.copy()                 # az 90 deg (+Z)
    s14_asy = _roty(90.0, s_single_base.copy())   # az 180 deg (+X)
    s15_asy = _roty(180.0, s_opt4_base.copy())    # az 270 deg (-Z)

    # 4. Bed Poses (flat on Z = 0)
    base_rot = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    s12_bed = _to_bed_pose(s12_asy, base_rot, 90)
    s13_bed = _to_bed_pose(s13_asy, base_rot, 0)
    s14_bed = _to_bed_pose(s14_asy, base_rot, -90)
    s15_bed = _to_bed_pose(s15_asy, base_rot, -180)

    for b in [s12_bed, s13_bed, s14_bed, s15_bed]:
        min_z = b.bounds[0][2]
        b.apply_translation([0.0, 0.0, -min_z])

    # Cap 11 (Slotted version so the extended spring can pass through)
    cap_slotted = trimesh.load(os.path.join(ASY_DIR, "11_Custom_Internal_Barrel_Cap.stl"), process=True)
    barrel_mesh = trimesh.load(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), process=True)

    print("\n[3/5] Exporting Option 4 STLs...")
    # Flat-bed STLs
    s12_bed.export(os.path.join(OUTPUT_DIR, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_bed.export(os.path.join(OUTPUT_DIR, "13_Custom_Rod_Detent_Spring_02_ExtTopTooth.stl"))
    s14_bed.export(os.path.join(OUTPUT_DIR, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_bed.export(os.path.join(OUTPUT_DIR, "15_Custom_Rod_Detent_Spring_04_ExtTopTooth.stl"))
    cap_slotted.export(os.path.join(OUTPUT_DIR, "11_Custom_Internal_Barrel_Cap_Slotted.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(OUTPUT_DIR, "10_Custom_Internal_Barrel_4Slot.stl"))

    # Assembled STLs
    asy_sub = os.path.join(OUTPUT_DIR, "Assembled_Coordinates")
    os.makedirs(asy_sub, exist_ok=True)
    s12_asy.export(os.path.join(asy_sub, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_asy.export(os.path.join(asy_sub, "13_Custom_Rod_Detent_Spring_02_ExtTopTooth.stl"))
    s14_asy.export(os.path.join(asy_sub, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_asy.export(os.path.join(asy_sub, "15_Custom_Rod_Detent_Spring_04_ExtTopTooth.stl"))
    cap_slotted.export(os.path.join(asy_sub, "11_Custom_Internal_Barrel_Cap_Slotted.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(asy_sub, "10_Custom_Internal_Barrel_4Slot.stl"))

    print("\n[4/5] Exporting Option 4 Assembled and Exploded GLBs...")
    parts_info = [
        {"name": "10_Custom_Internal_Barrel_4Slot", "mesh": barrel_mesh, "color": (55, 65, 75), "disp": [0.0, 0.0, 0.0]},
        {"name": "11_Custom_Internal_Barrel_Cap_Slotted", "mesh": cap_slotted, "color": (160, 170, 180), "disp": [0.0, 18.0, 0.0]},
        {"name": "12_Custom_Rod_Detent_Spring_01", "mesh": s12_asy, "color": (249, 115, 22), "disp": [-20.0, 0.0, 0.0]},
        {"name": "13_Custom_Rod_Detent_Spring_02_ExtTopTooth", "mesh": s13_asy, "color": (234, 179, 8), "disp": [0.0, 0.0, 20.0]},  # Gold/Amber
        {"name": "14_Custom_Rod_Detent_Spring_03", "mesh": s14_asy, "color": (249, 115, 22), "disp": [20.0, 0.0, 0.0]},
        {"name": "15_Custom_Rod_Detent_Spring_04_ExtTopTooth", "mesh": s15_asy, "color": (234, 179, 8), "disp": [0.0, 0.0, -20.0]},
    ]

    scene_asy = trimesh.Scene()
    scene_exp = trimesh.Scene()

    for p in parts_info:
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

    out_glb_asy = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option4.glb")
    out_glb_exp = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option4_Exploded.glb")
    scene_asy.export(out_glb_asy)
    scene_exp.export(out_glb_exp)

    # 3MF
    out_3mf = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option4.3mf")
    scene_asy.export(out_3mf)

    print(f"\n[5/5] Measuring Clash with Upper Shell Rotating Spring 21_30...")
    s21 = trimesh.load(os.path.join(ASY_DIR, "21_30_Upper_Shell_Rotating_Spring.stl"), process=True)
    m21 = to_manifold(s21)
    m13 = to_manifold(s13_asy)
    clash_vol = (m13 ^ m21).volume()
    print(f"  -> S13 ExtTopTooth vs 21_30 Clash Volume: {clash_vol:.4f} mm3")

    print("\n" + "=" * 80)
    print(f"[SUCCESS] OPTION 4 BUILT IN {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
