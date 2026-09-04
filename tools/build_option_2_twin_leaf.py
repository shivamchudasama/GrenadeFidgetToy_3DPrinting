"""Build Option 2: Twin Parallel Leaf Cantilever Springs Sub-Assembly.

Architecture:
- 100% inside internal barrel chassis slot (Y = 36.00 to 63.24 mm).
- Full 4.80 mm width stepped foot (Y in [36.00, 42.60] mm) anchored into L-slot.
- Flexure body split into two parallel cantilever leaves:
  * Leaf 1 (Left, 1.25 mm width): Nose at Y = 57.3959 mm (synchronous with Tooth 9).
  * Central clearance gap: 0.50 mm (prevents rubbing / friction).
  * Leaf 2 (Right, 1.25 mm width): Nose at Y = 55.8072 mm (half-pitch offset ΔY = 1.588 mm).
- Alternating click action: produces 18 crisp micro-clicks across stroke (2x click frequency).
- Solid retention cap 11 (zero pass-through cutouts needed).
- Zero interference with 21_30 Upper Shell Rotating Spring (0.000 mm3 clash).

Outputs:
  - Hybrid_Grenade_v1.2/Derivatives/Option_2_Twin_Parallel/
"""
from __future__ import annotations

import os
import sys
import shutil
import numpy as np
import trimesh
import shapely
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD
from build_all_modified_springs import (
    poly_single,
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
OUTPUT_DIR = os.path.join(V12_DIR, "Derivatives", "Option_2_Twin_Parallel")
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


def build_half_pitch_polygon() -> shapely.Polygon:
    """Create 2D profile for Leaf 2 with nose shifted by half pitch down."""
    half_pitch = 0.5 * BRD.TOOTH_PITCH  # 1.588665 mm
    coords = np.array(poly_single.exterior.coords)
    coords2 = []
    for y, r in coords:
        if y > 45.0:
            factor = min(1.0, (y - 45.0) / 6.0)
            coords2.append((y - half_pitch * factor, r))
        else:
            coords2.append((y, r))
    poly_leaf2 = shapely.Polygon(coords2)
    return poly_leaf2


def build_twin_leaf_solid() -> trimesh.Trimesh:
    """Create watertight 3D solid for twin parallel leaf spring."""
    poly_leaf1 = poly_single
    poly_leaf2 = build_half_pitch_polygon()

    # Leaf 1: X in [-1.50, -0.25] (width 1.25 mm)
    solid1 = trimesh.creation.extrude_polygon(poly_leaf1, height=1.25)
    solid1.apply_transform(np.array([
        [0.0, 0.0, 1.0, -1.50],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]))

    # Leaf 2: X in [0.25, 1.50] (width 1.25 mm)
    solid2 = trimesh.creation.extrude_polygon(poly_leaf2, height=1.25)
    solid2.apply_transform(np.array([
        [0.0, 0.0, 1.0, 0.25],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]))

    # Common Foot bridging both leaves at Y in [36.0, 42.6]
    foot_poly = shapely.Polygon([
        (FOOT_Y0, BRD.LEAF_R0),
        (FOOT_Y0, RAIL_R1_NEW),
        (FOOT_Y1, RAIL_R1_NEW),
        (FOOT_Y1, BRD.LEAF_R0)
    ])
    foot_block = trimesh.creation.extrude_polygon(foot_poly, height=TOTAL_W)
    foot_block.apply_transform(np.array([
        [0.0, 0.0, 1.0, -1.50],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]))

    # Cut stepped profile onto foot: narrow at front, step at rear (R >= R_RIB)
    narrow_cutter = trimesh.creation.box(extents=[NARROW_W, 10.0, 20.0])
    narrow_cutter.apply_translation([0.0, 39.3, 10.0])
    step_cutter = trimesh.creation.box(extents=[TOTAL_W, 10.0, (RAIL_R1_NEW + 2.0) - R_RIB])
    step_cutter.apply_translation([0.9, 39.3, 0.5 * (R_RIB + RAIL_R1_NEW + 2.0)])

    mf = to_manifold(foot_block)
    mnf = to_manifold(narrow_cutter)
    msf = to_manifold(step_cutter)
    foot_clean = (mf ^ mnf) + (mf ^ msf)

    m1 = to_manifold(solid1)
    m2 = to_manifold(solid2)
    twin_m = foot_clean + m1 + m2

    twin_tm = from_manifold(twin_m)
    return _solidify(twin_tm, "Twin_Leaf_Solid")


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
    print("BUILDING OPTION 2: TWIN PARALLEL LEAF SPRINGS (HALF-PITCH OFFSET)")
    print("=" * 80)

    # 1. 3D Twin Leaf Solid
    print("[1/5] Synthesizing Twin Leaf Parallel 3D Solid...")
    s_twin_base = build_twin_leaf_solid()
    print(f"  -> Twin Solid Watertight: {s_twin_base.is_watertight}, Volume: {s_twin_base.volume:.2f} mm3")

    # Single spring for 12 & 14
    from build_all_modified_springs import profile_to_solid
    s_single_base = profile_to_solid(poly_single, "Single_Solid")

    # 2. Assembled Orientations
    s12_asy = _roty(-90.0, s_single_base.copy())  # az 0 deg (-X)
    s13_asy = s_twin_base.copy()                 # az 90 deg (+Z)
    s14_asy = _roty(90.0, s_single_base.copy())   # az 180 deg (+X)
    s15_asy = _roty(180.0, s_twin_base.copy())    # az 270 deg (-Z)

    # 3. Bed Poses (flat on Z = 0)
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

    print("\n[2/5] Exporting Option 2 Flat-Bed STLs...")
    s12_bed.export(os.path.join(OUTPUT_DIR, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_bed.export(os.path.join(OUTPUT_DIR, "13_Custom_Rod_Detent_Spring_02_TwinLeaf.stl"))
    s14_bed.export(os.path.join(OUTPUT_DIR, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_bed.export(os.path.join(OUTPUT_DIR, "15_Custom_Rod_Detent_Spring_04_TwinLeaf.stl"))
    cap_solid.export(os.path.join(OUTPUT_DIR, "11_Custom_Internal_Barrel_Cap_Solid.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(OUTPUT_DIR, "10_Custom_Internal_Barrel_4Slot.stl"))

    # Assembled STLs
    asy_sub = os.path.join(OUTPUT_DIR, "Assembled_Coordinates")
    os.makedirs(asy_sub, exist_ok=True)
    s12_asy.export(os.path.join(asy_sub, "12_Custom_Rod_Detent_Spring_01.stl"))
    s13_asy.export(os.path.join(asy_sub, "13_Custom_Rod_Detent_Spring_02_TwinLeaf.stl"))
    s14_asy.export(os.path.join(asy_sub, "14_Custom_Rod_Detent_Spring_03.stl"))
    s15_asy.export(os.path.join(asy_sub, "15_Custom_Rod_Detent_Spring_04_TwinLeaf.stl"))
    cap_solid.export(os.path.join(asy_sub, "11_Custom_Internal_Barrel_Cap_Solid.stl"))
    shutil.copy2(os.path.join(ASY_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), os.path.join(asy_sub, "10_Custom_Internal_Barrel_4Slot.stl"))

    print("\n[3/5] Exporting Option 2 Assembled and Exploded GLBs...")
    parts_info = [
        {"name": "10_Custom_Internal_Barrel_4Slot", "mesh": barrel_mesh, "color": (55, 65, 75), "disp": [0.0, 0.0, 0.0]},
        {"name": "11_Custom_Internal_Barrel_Cap_Solid", "mesh": cap_solid, "color": (160, 170, 180), "disp": [0.0, 18.0, 0.0]},
        {"name": "12_Custom_Rod_Detent_Spring_01", "mesh": s12_asy, "color": (249, 115, 22), "disp": [-20.0, 0.0, 0.0]},
        {"name": "13_Custom_Rod_Detent_Spring_02_TwinLeaf", "mesh": s13_asy, "color": (168, 85, 247), "disp": [0.0, 0.0, 20.0]},
        {"name": "14_Custom_Rod_Detent_Spring_03", "mesh": s14_asy, "color": (249, 115, 22), "disp": [20.0, 0.0, 0.0]},
        {"name": "15_Custom_Rod_Detent_Spring_04_TwinLeaf", "mesh": s15_asy, "color": (168, 85, 247), "disp": [0.0, 0.0, -20.0]},
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

    out_glb_asy = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option2.glb")
    out_glb_exp = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option2_Exploded.glb")
    scene_asy.export(out_glb_asy)
    scene_exp.export(out_glb_exp)

    # 3MF
    out_3mf = os.path.join(OUTPUT_DIR, "Custom_Internal_Barrel_Assembly_Option2.3mf")
    scene_asy.export(out_3mf)

    print(f"\n[4/5] Checking Clash with Upper Shell Rotating Spring 21_30...")
    s21 = trimesh.load(os.path.join(ASY_DIR, "21_30_Upper_Shell_Rotating_Spring.stl"), process=True)
    m21 = to_manifold(s21)
    m13 = to_manifold(s13_asy)
    clash_vol = (m13 ^ m21).volume()
    print(f"  -> S13 TwinLeaf vs 21_30 Clash Volume: {clash_vol:.4f} mm3 (Expected 0.0000)")

    print("\n" + "=" * 80)
    print(f"[SUCCESS] OPTION 2 BUILT IN {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
