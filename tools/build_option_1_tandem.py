"""Build Option 1: Internal Tandem Dual-Head Springs Sub-Assembly.

Architecture:
- 100% inside internal barrel chassis slot (Y = 36.00 to 63.24 mm).
- Upper Nose at Y = 57.3959 mm (matches Tooth 9 at resting state ΔY = 0).
- Lower Nose at Y = 47.8639 mm (3 * pitch = 9.532 mm lower, matches Tooth 6 at ΔY = 0).
- Both heads engage simultaneously at ΔY = 0, delivering heavy synchronous 2x click force.
- Solid retention cap 11 (zero pass-through cutouts needed).
- Zero interference with 21_30 Upper Shell Rotating Spring (0.000 mm3 clash).

Outputs:
  - Hybrid_Grenade_v1.2/Derivatives/Option_1_Internal_Tandem/
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
    ENGINE,
)

V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
ASY_DIR = os.path.join(V12_DIR, "All_Parts_Assembled_Coordinates")
OUTPUT_DIR = os.path.join(V12_DIR, "Derivatives", "Option_1_Internal_Tandem")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_tandem_polygon() -> shapely.Polygon:
    """Create 2D profile for internal tandem dual-head spring."""
    pitch = BRD.TOOTH_PITCH  # 3.17733 mm
    y_lower_nose = 57.3959 - 3.0 * pitch  # 47.8639 mm

    # Upper nose is at Y = 57.3959 mm in poly_single
    # Graft lower nose wedge
    wedge_lower = BRD._nose_wedge(y_lower_nose, apex=BRD.NOSE_APEX)

    # Stalk connecting lower nose back into the inner flexure spine
    stalk = shapely.Polygon([
        (y_lower_nose - 1.25, 7.35),
        (y_lower_nose + 1.25, 7.35),
        (y_lower_nose + 1.25, 8.45),
        (y_lower_nose - 1.25, 8.45),
    ])

    merged = unary_union([poly_single, stalk, wedge_lower])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
    return shapely.Polygon(merged.exterior)


def build_solid_cap() -> trimesh.Trimesh:
    """Build clean solid retention cap disc (without pass-through slots)."""
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

    m_top = manifold3d.Manifold(manifold3d.Mesh64(np.ascontiguousarray(barrel_top.vertices, dtype=np.float64), np.ascontiguousarray(barrel_top.faces, dtype=np.uint64)))
    m_hole = manifold3d.Manifold(manifold3d.Mesh64(np.ascontiguousarray(rod_hole.vertices, dtype=np.float64), np.ascontiguousarray(rod_hole.faces, dtype=np.uint64)))
    m_diff = m_top - m_hole

    rebuilt = m_diff.to_mesh64()
    solid_disc = trimesh.Trimesh(
        vertices=np.asarray(rebuilt.vert_properties)[:, :3],
        faces=np.asarray(rebuilt.tri_verts),
        process=False,
    )
    return _solidify(solid_disc, "Solid_Cap_11")


def main():
    print("=" * 80)
    print("BUILDING OPTION 1: INTERNAL TANDEM DUAL-HEAD SPRINGS SUB-ASSEMBLY")
    print("=" * 80)

    # 1. 2D Profile
    poly_tandem = build_tandem_polygon()
    print(f"[1/5] Synthesized Tandem 2D Polygon: Area = {poly_tandem.area:.2f} mm2")

    # 2. 3D Solids
    s_tandem_base = profile_to_solid(poly_tandem, "Tandem_Dual_Solid")
    s_single_base = profile_to_solid(poly_single, "Single_Solid")
    print(f"[2/5] Extruded watertight solid: Volume = {s_tandem_base.volume:.2f} mm3")

    # 3. Assembled Orientations
    s12_asy = _roty(-90.0, s_single_base.copy())  # az 0 deg (-X)
    s13_asy = s_tandem_base.copy()               # az 90 deg (+Z)
    s14_asy = _roty(90.0, s_single_base.copy())   # az 180 deg (+X)
    s15_asy = _roty(180.0, s_tandem_base.copy())  # az 270 deg (-Z)

    # 4. Bed Poses (flat on Z = 0)
    base_rot = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    s12_bed = _to_bed_pose(s12_asy, base_rot, 90)
    s13_bed = _to_bed_pose(s13_asy, base_rot, 0)
    s14_bed = _to_bed_pose(s14_asy, base_rot, -90)
    s15_bed = _to_bed_pose(s15_asy, base_rot, -180)

    for b in [s12_bed, s13_bed, s14_bed, s15_bed]:
        min_z = b.bounds[0][2]
        b.apply_translation([0.0, 0.0, -min_z])

    # 5. Cap 11
    cap_solid = build_solid_cap()

    # Load barrel 10
    barrel_mesh = trimesh.load(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), process=True)

    print("\n[3/5] Exporting Option 1 STLs...")
    # Flat-bed STLs
    s12_bed.export(os.path.join(OUTPUT_DIR, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_bed.export(os.path.join(OUTPUT_DIR, "13_Custom_Rod_Detent_Spring_02_Tandem.stl"))
    s14_bed.export(os.path.join(OUTPUT_DIR, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_bed.export(os.path.join(OUTPUT_DIR, "15_Custom_Rod_Detent_Spring_04_Tandem.stl"))
    cap_solid.export(os.path.join(OUTPUT_DIR, "11_Custom_Internal_Barrel_Cap_Solid.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(OUTPUT_DIR, "10_Custom_Internal_Barrel_4Slot.stl"))

    # Assembled STLs (subfolder)
    asy_sub = os.path.join(OUTPUT_DIR, "Assembled_Coordinates")
    os.makedirs(asy_sub, exist_ok=True)
    s12_asy.export(os.path.join(asy_sub, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_asy.export(os.path.join(asy_sub, "13_Custom_Rod_Detent_Spring_02_Tandem.stl"))
    s14_asy.export(os.path.join(asy_sub, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_asy.export(os.path.join(asy_sub, "15_Custom_Rod_Detent_Spring_04_Tandem.stl"))
    cap_solid.export(os.path.join(asy_sub, "11_Custom_Internal_Barrel_Cap_Solid.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(asy_sub, "10_Custom_Internal_Barrel_4Slot.stl"))

    print("\n[4/5] Exporting Option 1 Assembled and Exploded GLBs...")
    parts_info = [
        {"name": "10_Custom_Internal_Barrel_4Slot", "mesh": barrel_mesh, "color": (55, 65, 75), "disp": [0.0, 0.0, 0.0]},
        {"name": "11_Custom_Internal_Barrel_Cap_Solid", "mesh": cap_solid, "color": (160, 170, 180), "disp": [0.0, 18.0, 0.0]},
        {"name": "12_Custom_Rod_Detent_Spring_01", "mesh": s12_asy, "color": (249, 115, 22), "disp": [-20.0, 0.0, 0.0]},
        {"name": "13_Custom_Rod_Detent_Spring_02_Tandem", "mesh": s13_asy, "color": (236, 72, 153), "disp": [0.0, 0.0, 20.0]},
        {"name": "14_Custom_Rod_Detent_Spring_03", "mesh": s14_asy, "color": (249, 115, 22), "disp": [20.0, 0.0, 0.0]},
        {"name": "15_Custom_Rod_Detent_Spring_04_Tandem", "mesh": s15_asy, "color": (236, 72, 153), "disp": [0.0, 0.0, -20.0]},
    ]

    scene_asy = trimesh.Scene()
    scene_exp = trimesh.Scene()

    for p in parts_info:
        # Assembled
        m = p["mesh"].copy()
        r, g, b = p["color"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        mat = trimesh.visual.material.PBRMaterial(baseColorFactor=color_norm, metallicFactor=0.35, roughnessFactor=0.45)
        m.visual = trimesh.visual.TextureVisuals(material=mat)
        scene_asy.add_geometry(m, node_name=p["name"], geom_name=p["name"])

        # Exploded
        m_exp = p["mesh"].copy()
        m_exp.apply_translation(p["disp"])
        mat_exp = trimesh.visual.material.PBRMaterial(baseColorFactor=color_norm, metallicFactor=0.35, roughnessFactor=0.45)
        m_exp.visual = trimesh.visual.TextureVisuals(material=mat_exp)
        scene_exp.add_geometry(m_exp, node_name=f"{p['name']} (Exploded)", geom_name=f"{p['name']}_exp")

    out_glb_asy = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option1.glb")
    out_glb_exp = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option1_Exploded.glb")
    scene_asy.export(out_glb_asy)
    scene_exp.export(out_glb_exp)

    # 3MF
    out_3mf = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option1.3mf")
    scene_asy.export(out_3mf)

    print(f"\n[5/5] Checking Clash with Upper Shell Rotating Spring 21_30...")
    s21 = trimesh.load(os.path.join(ASY_DIR, "21_30_Upper_Shell_Rotating_Spring.stl"), process=True)
    m21 = manifold3d.Manifold(manifold3d.Mesh64(np.ascontiguousarray(s21.vertices, dtype=np.float64), np.ascontiguousarray(s21.faces, dtype=np.uint64)))
    m13 = manifold3d.Manifold(manifold3d.Mesh64(np.ascontiguousarray(s13_asy.vertices, dtype=np.float64), np.ascontiguousarray(s13_asy.faces, dtype=np.uint64)))
    clash_vol = (m13 ^ m21).volume()
    print(f"  -> S13 Tandem vs 21_30 Clash Volume: {clash_vol:.4f} mm3 (Expected 0.0000)")

    print("\n" + "=" * 80)
    print(f"[SUCCESS] OPTION 1 BUILT IN {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
