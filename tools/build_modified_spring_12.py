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
print("BUILDING RIGHT-ANGLED L-SHAPED 12_Custom_Rod_Detent_Spring_01.stl")
print("Target: Raised Foot ONLY (Height = 1.800 mm, Width = 3.750 mm); U-Spring Unraised (3.000 mm)")
print("=" * 80)

# Target dimensions matching Image 2 in Blender view
TOTAL_W = 4.800          # mm total extrusion width (body = 3.00 mm, step = 1.80 mm)
NARROW_W = 3.000         # mm arm body width
STEP_HEIGHT = 1.800      # mm vertical step height in Blender view
STEP_WIDTH = 3.750       # mm horizontal step width in Blender view (radial span)
RAIL_R1_NEW = 13.350     # mm outer radial limit
R_RIB = RAIL_R1_NEW - STEP_WIDTH  # 13.350 - 3.750 = 9.600 mm
FOOT_Y0 = BRD.FOOT_Y0    # 36.00 mm
FOOT_Y1 = 42.60          # 42.60 mm (foot ends here, flexure arm begins)

# 1. Build base 2D profile
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

# 2. Extrude to 3D solid with right-angled L-shape ONLY ON FOOT
solid = trimesh.creation.extrude_polygon(poly_single, height=TOTAL_W)
solid.apply_transform(np.array([[0.0, 0.0, 1.0, -1.50],
                                [1.0, 0.0, 0.0, 0.0],
                                [0.0, 1.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0]]))

b = solid.bounds
span = lambda i: b[1][i] - b[0][i] + 4.0

# Narrow body: X in [-1.50, +1.50] (width 3.00 mm) everywhere along the whole spring
narrow = trimesh.creation.box(extents=[NARROW_W, span(1), span(2)])
narrow.apply_translation([-1.50 + NARROW_W / 2.0, 0.5 * (b[0][1] + b[1][1]), 0.5 * (b[0][2] + b[1][2])])

# Raised rib: ONLY IN FOOT REGION (Y in [FOOT_Y0 - 1.0, FOOT_Y1]), NOT IN U-SPRING ARM
foot_y_span = (FOOT_Y1 - FOOT_Y0) + 2.0
foot_y_center = 0.5 * (FOOT_Y0 - 1.0 + FOOT_Y1 + 1.0)
ribband = trimesh.creation.box(extents=[span(0), foot_y_span, (RAIL_R1_NEW + 2.0) - R_RIB])
ribband.apply_translation([0.5 * (b[0][0] + b[1][0]), foot_y_center,
                           0.5 * (R_RIB + RAIL_R1_NEW + 2.0)])

out = trimesh.boolean.union(
    [trimesh.boolean.intersection([solid, narrow], engine=ENGINE),
     trimesh.boolean.intersection([solid, ribband], engine=ENGINE)], engine=ENGINE)
s_01_base = _solidify(out, "Modified_Spring_12_Solid")

# 3. Assembled orientation (azimuth 0 deg, -X)
s_01_asy = _roty(-90.0, s_01_base.copy())

# 4. Flat bed pose (bottom face at Z = 0)
base_rot = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
s_01_bed = _to_bed_pose(s_01_asy, base_rot, 90)
s_01_bed.apply_translation([0, 0, -s_01_bed.bounds[0][2]])

print("\n--- MEASURED RESULTS ---")
print(f"Watertight: {s_01_bed.is_watertight}, Volume: {s_01_bed.volume:.2f} mm3")
print(f"Bed Z range: [{s_01_bed.bounds[0][2]:.3f}, {s_01_bed.bounds[1][2]:.3f}] mm (Span: {s_01_bed.extents[2]:.3f} mm)")

# Verify width at foot vs arm
for y in [38.0, 42.0, 44.0, 50.0, 55.0]:
    sec = s_01_asy.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    if sec is not None:
        pts = sec.vertices
        w = pts[:, 2].max() - pts[:, 2].min()
        region = "FOOT" if y <= 42.60 else "U-SPRING ARM"
        print(f"   [{region}] Y = {y:4.1f} mm: Width = {w:.3f} mm")

# Export
sub_dir = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "03_Internal_Barrel_And_Upper_Station")
flat_dir = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Flat_Bed_Oriented")
asy_dir = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2", "All_Parts_Assembled_Coordinates")

fn = "12_Custom_Rod_Detent_Spring_01.stl"
s_01_bed.export(os.path.join(sub_dir, fn))
s_01_bed.export(os.path.join(flat_dir, fn))
s_01_asy.export(os.path.join(asy_dir, fn))
print(f"[SUCCESS] Exported {fn} to subassembly, flat-bed, and assembled directories.")
