"""Build Dual-Headed Rod Detent Springs (Exact V2 Middle Spring Geometry).

Architecture:
-------------
* Sourced directly from '11 - Middle Spring v2.stl' preserving the exact
  cantilever flexure stalk, 180° hairpin U-turn arch, bulbous teardrop head,
  and diamond detent nose facets.
* Common U-Shaped Spring: Single-headed spring (y = 36.00 .. 62.92 mm, with lower nose at y = 57.41 mm).
* Upper Detent Head: Extends smoothly upward from the common spring's outer flexure rail through the cap
  to y = 72.45 mm, presenting the second detent nose at y = 66.94 mm (3 * pitch = 9.532 mm above lower nose)
  to engage the upper exposed teeth of Custom Rod Middle in exact synchronization.
* Modified Slotted Cap: 11_Custom_Internal_Barrel_Cap_Option_B.stl with 3.60 mm pass-through slots at 90° and 270°.

Exports both assembled coordinates and flat-bed oriented print files.
"""
from __future__ import annotations

import os
import sys
import shutil
import numpy as np
import shapely
from shapely.ops import unary_union
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD
import flexure_rate as FR
from package_paths import ROOT_DIR, ASSEMBLED_DIR

ENGINE = "manifold"
OUTPUT_DIR = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap")
V2_SPRING_PATH = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")


def _solidify(mesh: trimesh.Trimesh, label: str = "") -> trimesh.Trimesh:
    """Repair and ensure manifold watertightness using manifold3d."""
    if mesh.is_watertight and mesh.body_count == 1:
        return mesh
    import manifold3d

    src = manifold3d.Mesh64(
        np.ascontiguousarray(mesh.vertices, dtype=np.float64),
        np.ascontiguousarray(mesh.faces, dtype=np.uint64),
        tolerance=1e-5,
    )
    src.merge()
    solid = manifold3d.Manifold(src)
    if solid.is_empty():
        raise RuntimeError(f"Could not solidify {label}")
    rebuilt = solid.to_mesh64()
    return trimesh.Trimesh(
        vertices=np.asarray(rebuilt.vert_properties)[:, :3],
        faces=np.asarray(rebuilt.tri_verts),
        process=False,
    )


def _roty(deg: float, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Rotate mesh about Y axis in degrees."""
    if deg:
        mesh.apply_transform(
            trimesh.transformations.rotation_matrix(
                np.radians(deg), [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]
            )
        )
    return mesh


def _to_bed_pose(mesh: trimesh.Trimesh, base_rot: list, y_deg: float) -> trimesh.Trimesh:
    """Orient mesh flat on bed with Z min = 0."""
    T = np.eye(4)
    Ry = trimesh.transformations.rotation_matrix(np.radians(y_deg), [0.0, 1.0, 0.0])[:3, :3]
    T[:3, :3] = np.asarray(base_rot, dtype=float) @ Ry
    out = mesh.copy()
    out.apply_transform(T)
    b = out.bounds
    cx = 0.5 * (b[0][0] + b[1][0])
    cy = 0.5 * (b[0][1] + b[1][1])
    out.apply_translation([-cx, -cy, -b[0][2]])
    return out


def extract_v2_reference_arm() -> shapely.Polygon:
    """Extract pristine 2D arm polygon from '11 - Middle Spring v2.stl'."""
    m_v2 = trimesh.load(V2_SPRING_PATH, process=True)
    pl, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
    poly_full = pl.polygons_full[0]

    # Left arm (x <= 0) mirrored to positive radius (x >= 0)
    left_part = poly_full.intersection(shapely.box(-30.0, 15.0, 0.0, 55.0))
    coords = np.array(left_part.exterior.coords)
    coords_mirrored = np.column_stack([-coords[:, 0], coords[:, 1]])
    arm = shapely.Polygon(coords_mirrored).difference(shapely.box(-10.0, -10.0, 30.0, 19.60))
    if arm.geom_type == 'MultiPolygon':
        arm = max(arm.geoms, key=lambda q: q.area)
    return shapely.Polygon(arm.exterior)


def build_v2_single_profile(r_nose: float = BRD.NOSE_APEX,
                            s_y: float = BRD.ARM_SCALE_Y,
                            arm_y0: float = BRD.ARM_Y0,
                            arm_r_out: float = BRD.ARM_R_OUT) -> shapely.Polygon:
    """Construct single-headed spring 2D profile using exact v2 middle spring geometry with smooth organic curves on both waist edges."""
    from scipy.interpolate import CubicSpline

    ref_arm = extract_v2_reference_arm()

    # Precise radial anchors preserving v2 geometry with print-safe 0.75-0.80mm walls & 0.55mm gaps
    # v2 source features: nose(5.8532), flank(7.1240), desc_in(8.6509), desc_out(9.4509), asc_in(10.4509), asc_out(11.2509), spine_in(12.6509), spine_out(14.4509)
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([r_nose, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, arm_r_out])

    def map_c(c):
        x, y = c[0], c[1]
        toy_y = arm_y0 + (y - 19.60) * s_y
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped = shapely.Polygon([map_c(c) for c in ref_arm.exterior.coords])
    coords = list(mapped.exterior.coords)

    # 1. Outer waist curve: smooth transition from (y=42.60, r=8.618, dr/dy=0) to (y=54.541, r=10.900, dr/dy=0)
    foot_y1 = arm_y0 + BRD.FOOT_OVERLAP  # 42.60 mm
    y_top_outer = 54.541
    y_ctrl_out = np.array([42.60, 45.50, 48.00, 51.00, 53.50, y_top_outer])
    r_ctrl_out = np.array([8.618, 8.850, 9.750, 10.650, 10.885, arm_r_out])
    cs_out = CubicSpline(y_ctrl_out, r_ctrl_out, bc_type=((1, 0.0), (1, 0.0)))
    y_eval_out = np.linspace(42.60, y_top_outer, 60)
    r_eval_out = cs_out(y_eval_out)

    # 2. Inner waist curve: smooth transition from (y=42.60, r=7.400, dr/dy=0) to (y=55.709, r=8.900, dr/dy=0)
    y_top_inner = 55.709
    y_ctrl_in = np.array([42.60, 46.00, 49.50, 53.00, y_top_inner])
    r_ctrl_in = np.array([7.400, 7.500, 7.850, 8.550, 8.900])
    cs_in = CubicSpline(y_ctrl_in, r_ctrl_in, bc_type=((1, 0.0), (1, 0.0)))
    y_eval_in = np.linspace(42.60, y_top_inner, 60)
    r_eval_in = cs_in(y_eval_in)

    pts = []
    # Rigid foot base
    pts.append((BRD.FOOT_Y0, BRD.LEAF_R0))  # (36.00, 7.400)
    pts.append((BRD.FOOT_Y0, BRD.RAIL_R1))  # (36.00, 12.200)
    pts.append((42.60, BRD.RAIL_R1))        # (42.60, 12.200)
    pts.append((42.60, 8.618))              # (42.60, 8.618)

    # Outer curve going UP
    for y, r in zip(y_eval_out[1:], r_eval_out[1:]):
        pts.append((y, r))

    # Upper pristine head / flexure loop from mapped
    for idx in range(232, 46, -1):
        pts.append(coords[idx])

    # Inner curve going DOWN from 55.709 to 42.60
    for y, r in reversed(list(zip(y_eval_in[:-1], r_eval_in[:-1]))):
        pts.append((y, r))

    # Close at foot
    pts.append((42.60, BRD.LEAF_R0))
    pts.append((BRD.FOOT_Y0, BRD.LEAF_R0))

    poly_base = shapely.Polygon(pts)

    # Graft rack-matched detent nose with 49.37° flanks (98.74° included) and smooth 0.75mm radius tip
    nose_y_lower = 57.3959
    wedge_lower = BRD._nose_wedge(nose_y_lower, apex=r_nose)
    merged = unary_union([poly_base, wedge_lower])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
    return shapely.Polygon(merged.exterior)


def build_v2_dual_head_profile() -> shapely.Polygon:
    """Construct dual-headed spring 2D profile replicating the exact v2 upper flexure loop with rack-matched detent noses."""
    poly_single = build_v2_single_profile()
    ref_arm = extract_v2_reference_arm()

    # Upper flexure loop in v2 starts at y >= 33.0 in ref_arm coords
    upper_loop_ref = ref_arm.intersection(shapely.box(0.0, 33.0, 20.0, 55.0))

    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([BRD.NOSE_APEX, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, BRD.ARM_R_OUT])

    pitch_shift = 3.0 * BRD.TOOTH_PITCH  # 9.53199 mm -> upper nose at y = 66.939 mm

    def map_upper(c):
        x, y = c[0], c[1]
        toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y + pitch_shift
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped_upper = shapely.Polygon([map_upper(c) for c in upper_loop_ref.exterior.coords])

    # Clean solid outer spine connecting lower body to upper loop through the cap
    spine_bridge = shapely.Polygon([
        (60.00, 10.250),
        (60.00, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, 10.250),
        (60.00, 10.250)
    ])

    # Upper rack-matched detent nose wedge
    nose_y_upper = 57.3959 + pitch_shift
    wedge_upper = BRD._nose_wedge(nose_y_upper, apex=BRD.NOSE_APEX)

    merged = unary_union([poly_single, mapped_upper, spine_bridge, wedge_upper])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)

    return shapely.Polygon(merged.exterior)


def _profile_to_solid(poly: shapely.Polygon, label: str = "") -> trimesh.Trimesh:
    """Extrude 2D (toy_y, toy_r) profile into 3D solid with notch rib step."""
    solid = trimesh.creation.extrude_polygon(poly, height=BRD.BODY_W)
    solid.apply_transform(np.array([[0.0, 0.0, 1.0, BRD.BODY_X0],
                                    [1.0, 0.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 1.0]]))
    b = solid.bounds
    span = lambda i: b[1][i] - b[0][i] + 4.0
    narrow = trimesh.creation.box(extents=[BRD.NARROW_W, span(1), span(2)])
    narrow.apply_translation([BRD.BODY_X0 + BRD.NARROW_W / 2.0,
                              0.5 * (b[0][1] + b[1][1]), 0.5 * (b[0][2] + b[1][2])])
    ribband = trimesh.creation.box(extents=[span(0), span(1), (BRD.RAIL_R1 + 2.0) - BRD.RIB_R0])
    ribband.apply_translation([0.5 * (b[0][0] + b[1][0]), 0.5 * (b[0][1] + b[1][1]),
                               0.5 * (BRD.RIB_R0 + BRD.RAIL_R1 + 2.0)])
    out = trimesh.boolean.union(
        [trimesh.boolean.intersection([solid, narrow], engine=ENGINE),
         trimesh.boolean.intersection([solid, ribband], engine=ENGINE)], engine=ENGINE)
    return _solidify(out, label)


def build_v2_single_head_solid() -> trimesh.Trimesh:
    """Build single-headed spring solid in 90 deg azimuth orientation."""
    poly = build_v2_single_profile()
    return _profile_to_solid(poly, "V2_Single_Head_Spring_Solid")


def build_v2_dual_head_solid() -> trimesh.Trimesh:
    """Build dual-headed spring solid in 90 deg azimuth orientation."""
    poly = build_v2_dual_head_profile()
    return _profile_to_solid(poly, "V2_Dual_Head_Spring_Solid")


def build_slotted_cap() -> trimesh.Trimesh:
    """Construct modified barrel cap with 90° and 270° pass-through slots."""
    stock_cap_path = os.path.join(ASSEMBLED_DIR, "11_Custom_Internal_Barrel_Cap.stl")
    cap = trimesh.load(stock_cap_path, process=True)

    # Cut 3.60 mm wide slots along Z = 7.0 .. 12.5 and Z = -12.5 .. -7.0
    slot_box = trimesh.creation.box(extents=[3.60, 2.0, 26.0])
    slot_box.apply_translation([0.0, 63.40, 0.0])

    # Keep center hub solid (radius < 7.0)
    center_plug = trimesh.creation.cylinder(radius=7.0, height=3.0)
    center_plug.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [1.0, 0.0, 0.0]))
    center_plug.apply_translation([0.0, 63.40, 0.0])

    cutter = trimesh.boolean.difference([slot_box, center_plug], engine=ENGINE)
    slotted_cap = trimesh.boolean.difference([cap, cutter], engine=ENGINE)
    return _solidify(slotted_cap, "11_Custom_Internal_Barrel_Cap_Option_B")


def export_package():
    print("=" * 75)
    print("BUILDING DUAL-HEADED SPRINGS (EXACT V2 MIDDLE SPRING GEOMETRY)")
    print("=" * 75)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Flat_Bed_Oriented"), exist_ok=True)

    # 1. Build solids
    s_single_base = build_v2_single_head_solid()
    s_dual_base = build_v2_dual_head_solid()
    slotted_cap = build_slotted_cap()

    # 2. Assembled orientations
    s_01 = _roty(-90.0, s_single_base.copy())        # 0° (-X)
    s_02 = s_dual_base.copy()                       # 90° (+Z)
    s_03 = _roty(90.0, s_single_base.copy())         # 180° (+X)
    s_04 = _roty(180.0, s_dual_base.copy())         # 270° (-Z)

    # 3. Export Assembled
    slotted_cap.export(os.path.join(OUTPUT_DIR, "11_Custom_Internal_Barrel_Cap_Option_B.stl"))
    s_01.export(os.path.join(OUTPUT_DIR, "12_Custom_Rod_Detent_Spring_01.stl"))
    s_02.export(os.path.join(OUTPUT_DIR, "13_Custom_Rod_Detent_Spring_02_Dual_Headed.stl"))
    s_03.export(os.path.join(OUTPUT_DIR, "14_Custom_Rod_Detent_Spring_03.stl"))
    s_04.export(os.path.join(OUTPUT_DIR, "15_Custom_Rod_Detent_Spring_04_Dual_Headed.stl"))

    # 4. Export Flat-Bed
    base_rot = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    _to_bed_pose(s_01, base_rot, 90).export(os.path.join(OUTPUT_DIR, "Flat_Bed_Oriented", "12_Custom_Rod_Detent_Spring_01.stl"))
    _to_bed_pose(s_02, base_rot, 0).export(os.path.join(OUTPUT_DIR, "Flat_Bed_Oriented", "13_Custom_Rod_Detent_Spring_02_Dual_Headed.stl"))
    _to_bed_pose(s_03, base_rot, -90).export(os.path.join(OUTPUT_DIR, "Flat_Bed_Oriented", "14_Custom_Rod_Detent_Spring_03.stl"))
    _to_bed_pose(s_04, base_rot, -180).export(os.path.join(OUTPUT_DIR, "Flat_Bed_Oriented", "15_Custom_Rod_Detent_Spring_04_Dual_Headed.stl"))
    _to_bed_pose(slotted_cap, [[1, 0, 0], [0, 0, 1], [0, -1, 0]], 0).export(
        os.path.join(OUTPUT_DIR, "Flat_Bed_Oriented", "11_Custom_Internal_Barrel_Cap_Option_B.stl")
    )
    print(f"[OK] Exact V2 Spring Package exported to: {OUTPUT_DIR}")


if __name__ == "__main__":
    export_package()
