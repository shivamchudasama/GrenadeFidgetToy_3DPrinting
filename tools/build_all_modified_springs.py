import os
import sys
import numpy as np
import trimesh
import shapely
from shapely.ops import unary_union
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD
from build_v2_exact_springs import (
    extract_v2_reference_arm,
    _solidify,
    _to_bed_pose,
    _roty,
    ENGINE
)

print("=" * 80)
print("BUILDING ALL 4 RIGHT-ANGLED L-SHAPED SPRINGS (SPRINGS 12, 13, 14, 15)")
print("Target: Raised Foot ONLY (Height = 1.800 mm, Width = 3.750 mm); U-Spring Unraised (3.000 mm)")
print("=" * 80)

# Target dimensions matching Option 1 (Total Foot Width = 4.800 mm)
TOTAL_W = 4.800          # mm total extrusion width (body = 3.00 mm, step = 1.80 mm)
NARROW_W = 3.000         # mm arm body width
STEP_HEIGHT = 1.800      # mm vertical step height in Blender view
STEP_WIDTH = 2.600       # mm horizontal step width in Blender view (radial span)
RAIL_R1_NEW = 12.200     # mm outer radial limit (foot width = 12.200 - 7.400 = 4.800 mm)
R_RIB = RAIL_R1_NEW - STEP_WIDTH  # 12.200 - 2.600 = 9.600 mm
FOOT_Y0 = BRD.FOOT_Y0    # 36.00 mm
FOOT_Y1 = 42.60          # 42.60 mm (foot ends here, flexure arm begins)

# 1. Base 2D profile
ref_arm = extract_v2_reference_arm()
x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
r_dst = np.array([BRD.NOSE_APEX, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, BRD.ARM_R_OUT])

def map_c(c):
    x, y = c[0], c[1]
    toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y
    toy_r = float(np.interp(x, x_src, r_dst))
    return (toy_y, toy_r)

mapped = shapely.Polygon([map_c(c) for c in ref_arm.exterior.coords])
coords = list(mapped.exterior.coords)

# Outer waist curve
y_top_outer = 54.541
y_ctrl_out = np.array([42.60, 45.50, 48.00, 51.00, 53.50, y_top_outer])
r_ctrl_out = np.array([8.618, 8.850, 9.750, 10.650, 10.885, BRD.ARM_R_OUT])
cs_out = CubicSpline(y_ctrl_out, r_ctrl_out, bc_type=((1, 0.0), (1, 0.0)))
y_eval_out = np.linspace(42.60, y_top_outer, 60)
r_eval_out = cs_out(y_eval_out)

# Inner waist curve
y_top_inner = 55.709
y_ctrl_in = np.array([42.60, 46.00, 49.50, 53.00, y_top_inner])
r_ctrl_in = np.array([7.400, 7.500, 7.850, 8.550, 8.900])
cs_in = CubicSpline(y_ctrl_in, r_ctrl_in, bc_type=((1, 0.0), (1, 0.0)))
y_eval_in = np.linspace(42.60, y_top_inner, 60)
r_eval_in = cs_in(y_eval_in)

pts = []
pts.append((FOOT_Y0, BRD.LEAF_R0))
pts.append((FOOT_Y0, RAIL_R1_NEW))
pts.append((FOOT_Y1, RAIL_R1_NEW))
pts.append((FOOT_Y1, 8.618))
for y, r in zip(y_eval_out[1:], r_eval_out[1:]):
    pts.append((y, r))
for idx in range(232, 46, -1):
    pts.append(coords[idx])
for y, r in reversed(list(zip(y_eval_in[:-1], r_eval_in[:-1]))):
    pts.append((y, r))
pts.append((FOOT_Y1, BRD.LEAF_R0))
pts.append((FOOT_Y0, BRD.LEAF_R0))

poly_base = shapely.Polygon(pts)
nose_y_lower = 57.3959
wedge_lower = BRD._nose_wedge(nose_y_lower, apex=BRD.NOSE_APEX)
merged_single = unary_union([poly_base, wedge_lower])
if merged_single.geom_type == 'MultiPolygon':
    merged_single = max(merged_single.geoms, key=lambda q: q.area)
poly_single = shapely.Polygon(merged_single.exterior)

# Dual-head profile (Springs 13 and 15)
upper_loop_ref = ref_arm.intersection(shapely.box(0.0, 33.0, 20.0, 55.0))
pitch_shift = 3.0 * BRD.TOOTH_PITCH

def map_upper(c):
    x, y = c[0], c[1]
    toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y + pitch_shift
    toy_r = float(np.interp(x, x_src, r_dst))
    return (toy_y, toy_r)

mapped_upper = shapely.Polygon([map_upper(c) for c in upper_loop_ref.exterior.coords])
spine_bridge = shapely.Polygon([
    (60.00, 10.250),
    (60.00, BRD.ARM_R_OUT),
    (62.916 + pitch_shift, BRD.ARM_R_OUT),
    (62.916 + pitch_shift, 10.250),
    (60.00, 10.250)
])
nose_y_upper = 57.3959 + pitch_shift
wedge_upper = BRD._nose_wedge(nose_y_upper, apex=BRD.NOSE_APEX)

merged_dual = unary_union([poly_single, mapped_upper, spine_bridge, wedge_upper])
if merged_dual.geom_type == 'MultiPolygon':
    merged_dual = max(merged_dual.geoms, key=lambda q: q.area)
poly_dual = shapely.Polygon(merged_dual.exterior)

# 2. Extrude to 3D solid with right-angled L-shape ONLY ON FOOT
def profile_to_solid(poly, label):
    solid = trimesh.creation.extrude_polygon(poly, height=TOTAL_W)
    solid.apply_transform(np.array([[0.0, 0.0, 1.0, -1.50],
                                    [1.0, 0.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 1.0]]))
    b = solid.bounds
    span = lambda i: b[1][i] - b[0][i] + 4.0
    narrow = trimesh.creation.box(extents=[NARROW_W, span(1), span(2)])
    narrow.apply_translation([-1.50 + NARROW_W / 2.0,
                              0.5 * (b[0][1] + b[1][1]), 0.5 * (b[0][2] + b[1][2])])
    
    # FOOT-ONLY RIBBAND:
    foot_y_span = (FOOT_Y1 - FOOT_Y0) + 2.0
    foot_y_center = 0.5 * (FOOT_Y0 - 1.0 + FOOT_Y1 + 1.0)
    ribband = trimesh.creation.box(extents=[span(0), foot_y_span, (RAIL_R1_NEW + 2.0) - R_RIB])
    ribband.apply_translation([0.5 * (b[0][0] + b[1][0]), foot_y_center,
                               0.5 * (R_RIB + RAIL_R1_NEW + 2.0)])
    
    out = trimesh.boolean.union(
        [trimesh.boolean.intersection([solid, narrow], engine=ENGINE),
         trimesh.boolean.intersection([solid, ribband], engine=ENGINE)], engine=ENGINE)
    return _solidify(out, label)

s_single_base = profile_to_solid(poly_single, 'Single_Solid')

# 3. Assembled orientations (all 4 equal single-headed springs)
s_01 = _roty(-90.0, s_single_base.copy())       # az 0 deg (-X)
s_02 = s_single_base.copy()                    # az 90 deg (+Z)
s_03 = _roty(90.0, s_single_base.copy())        # az 180 deg (+X)
s_04 = _roty(180.0, s_single_base.copy())       # az 270 deg (-Z)

# 4. Bed poses
base_rot = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
b_01 = _to_bed_pose(s_01, base_rot, 90)
b_02 = _to_bed_pose(s_02, base_rot, 0)
b_03 = _to_bed_pose(s_03, base_rot, -90)
b_04 = _to_bed_pose(s_04, base_rot, -180)

# Align each bed pose to Z = 0
for b in [b_01, b_02, b_03, b_04]:
    min_z = b.bounds[0][2]
    b.apply_translation([0.0, 0.0, -min_z])

spring_defs = [
    ("12_Custom_Rod_Detent_Spring_01.stl", s_01, b_01, "Single"),
    ("13_Custom_Rod_Detent_Spring_02.stl", s_02, b_02, "Single"),
    ("14_Custom_Rod_Detent_Spring_03.stl", s_03, b_03, "Single"),
    ("15_Custom_Rod_Detent_Spring_04.stl", s_04, b_04, "Single"),
]

from package_paths import PACKAGE_DIR

sub_dir = os.path.join(PACKAGE_DIR, "03_Internal_Barrel_And_Upper_Station")
flat_dir = os.path.join(PACKAGE_DIR, "All_Parts_Flat_Bed_Oriented")
asy_dir = os.path.join(PACKAGE_DIR, "All_Parts_Assembled_Coordinates")

print("\n--- MEASURED RESULTS FOR ALL 4 SPRINGS ---")
for filename, s_asy, s_bed, stype in spring_defs:
    assert s_bed.is_watertight and s_bed.body_count == 1, f"{filename} is not watertight!"
    high_z = s_bed.vertices[s_bed.vertices[:, 2] > 3.05]
    step_h = s_bed.bounds[1][2] - 3.000
    step_w = high_z[:, 1].max() - high_z[:, 1].min()
    print(f"[{stype}] {filename}:")
    print(f"   Watertight: {s_bed.is_watertight}, Volume: {s_bed.volume:.2f} mm3")
    print(f"   Bed Z range: [{s_bed.bounds[0][2]:.3f}, {s_bed.bounds[1][2]:.3f}] mm")
    print(f"   Step Height (Vertical): {step_h:.3f} mm, Step Width (Horizontal): {step_w:.3f} mm")

    # Export to all 3 directories
    s_bed.export(os.path.join(sub_dir, filename))
    s_bed.export(os.path.join(flat_dir, filename))
    s_asy.export(os.path.join(asy_dir, filename))
    print(f"   -> Exported to subassembly, flat-bed, and assembled")

# 5. Build and export retention cap 11 (with 4 L-notch filler prongs)
print("\n--- BUILDING RETENTION CAP (11_Custom_Internal_Barrel_Cap.stl) ---")
_, cap_asy = BRD.cap_with_slot_fillers()
T_cap = np.eye(4)
T_cap[:3, :3] = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
cap_bed = cap_asy.copy()
cap_bed.apply_transform(T_cap)
center_xy = (cap_bed.bounds[0][:2] + cap_bed.bounds[1][:2]) / 2.0
cap_bed.apply_translation([-center_xy[0], -center_xy[1], -cap_bed.bounds[0][2]])

assert cap_asy.is_watertight and cap_asy.body_count == 1, "Cap is not watertight!"
print(f"Cap Watertight: {cap_asy.is_watertight}, Volume: {cap_asy.volume:.2f} mm3")
print(f"Cap Bed Z range: [{cap_bed.bounds[0][2]:.3f}, {cap_bed.bounds[1][2]:.3f}] mm")

cap_fn = "11_Custom_Internal_Barrel_Cap.stl"
cap_bed.export(os.path.join(sub_dir, cap_fn))
cap_bed.export(os.path.join(flat_dir, cap_fn))
cap_asy.export(os.path.join(asy_dir, cap_fn))
print(f"   -> Exported {cap_fn} to subassembly, flat-bed, and assembled")

print("\n[OK] All 4 springs and solid cap built and exported successfully!")
