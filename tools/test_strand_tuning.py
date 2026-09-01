import os
import sys
import trimesh
import numpy as np
import shapely
from shapely.ops import unary_union
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))
import flexure_rate as FR
import build_rod_detent as BRD

v2_path = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy", "11 - Middle Spring v2.stl")
m_v2 = trimesh.load(v2_path, process=True)
pl_v2, _ = m_v2.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
poly_v2 = pl_v2.polygons_full[0]

# Left arm mirrored to positive X
poly_left = poly_v2.intersection(shapely.box(-25.0, 15.0, 0.0, 55.0))
coords = np.array(poly_left.exterior.coords)
coords_mirrored = np.column_stack([-coords[:, 0], coords[:, 1]])
ref_v2 = shapely.Polygon(coords_mirrored).difference(shapely.box(-10.0, -10.0, 30.0, 19.60))
if ref_v2.geom_type == 'MultiPolygon':
    ref_v2 = max(ref_v2.geoms, key=lambda q: q.area)

def build_v2_optimized_profiles(strand_w=0.80, gap_w=0.60, outer_spine_w=1.20):
    # Parameterized mapping that preserves the exact v2 curve shapes while tuning strand width
    # In ref_v2:
    # x_src: nose(5.8532), flank(7.1240), desc_in(8.6509), desc_out(9.4509), asc_in(10.4509), asc_out(11.2509), spine_in(12.6509), spine_out(14.4509)
    # Target radii:
    r_nose = 5.54
    r_flank = 7.00
    r_desc_in = 7.55
    r_desc_out = r_desc_in + strand_w
    r_asc_in = r_desc_out + gap_w
    r_asc_out = r_asc_in + strand_w
    r_spine_in = r_asc_out + 0.60
    r_spine_out = 10.90
    
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([r_nose, r_flank, r_desc_in, r_desc_out, r_asc_in, r_asc_out, r_spine_in, r_spine_out])
    
    def map_c(c):
        x, y = c[0], c[1]
        toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped_lower = shapely.Polygon([map_c(c) for c in ref_v2.exterior.coords])
    
    # Rigid foot
    foot_y1 = BRD.ARM_Y0 + BRD.FOOT_OVERLAP
    foot_poly = shapely.Polygon([
        (BRD.FOOT_Y0, BRD.LEAF_R0),
        (BRD.FOOT_Y0, BRD.RAIL_R1),
        (foot_y1, BRD.RAIL_R1),
        (foot_y1, 9.851),
        (47.00, 9.851),
        (47.00, BRD.LEAF_R0),
        (BRD.FOOT_Y0, BRD.LEAF_R0)
    ])
    
    merged_s = unary_union([mapped_lower, foot_poly])
    if merged_s.geom_type == 'MultiPolygon':
        merged_s = max(merged_s.geoms, key=lambda q: q.area)
    merged_s = merged_s.difference(shapely.box(0.0, 0.0, foot_y1, BRD.LEAF_R0))
    if merged_s.geom_type == 'MultiPolygon':
        merged_s = max(merged_s.geoms, key=lambda q: q.area)
    poly_single = shapely.Polygon(merged_s.exterior)
    
    # Dual Head:
    pitch_shift = 3.0 * BRD.TOOTH_PITCH # 9.53199 mm
    upper_loop_ref = ref_v2.intersection(shapely.box(0.0, 33.0, 20.0, 55.0))
    
    def map_upper(c):
        x, y = c[0], c[1]
        toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y + pitch_shift
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped_upper = shapely.Polygon([map_upper(c) for c in upper_loop_ref.exterior.coords])
    
    # Solid outer spine running continuously from lower body to upper loop
    spine_bridge = shapely.Polygon([
        (56.00, r_spine_in),
        (56.00, r_spine_out),
        (62.916 + pitch_shift, r_spine_out),
        (62.916 + pitch_shift, r_spine_in),
        (56.00, r_spine_in)
    ])
    
    merged_d = unary_union([poly_single, mapped_upper, spine_bridge])
    if merged_d.geom_type == 'MultiPolygon':
        merged_d = max(merged_d.geoms, key=lambda q: q.area)
    poly_dual = shapely.Polygon(merged_d.exterior)
    
    return poly_single, poly_dual

for strand_w in [0.70, 0.75, 0.80, 0.85]:
    ps, pd = build_v2_optimized_profiles(strand_w=strand_w)
    res_lo = FR.rate(ps, thickness=3.00,
                     fixed=lambda V: (V[:, 0] < 43.0) & (V[:, 1] > 11.0),
                     loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] < 60.0),
                     direction=(0.0, 1.0), h=0.07)
    res_hi = FR.rate(pd, thickness=3.00,
                     fixed=lambda V: (V[:, 0] < 43.0) & (V[:, 1] > 11.0),
                     loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] > 64.0),
                     direction=(0.0, 1.0), h=0.07)
    print(f"Strand w={strand_w:.2f}mm -> Lower: k={res_lo.k:.3f} N/mm, strain={res_lo.strain_per_mm*100:.3f}%/mm | Upper: k={res_hi.k:.3f} N/mm, strain={res_hi.strain_per_mm*100:.3f}%/mm")
