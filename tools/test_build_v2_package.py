import os
import sys
import shutil
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

def build_v2_single_profile(r_nose=BRD.NOSE_APEX, s_y=BRD.ARM_SCALE_Y, arm_y0=BRD.ARM_Y0, arm_r_out=BRD.ARM_R_OUT):
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([r_nose, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, arm_r_out])

    def map_c(c):
        x, y = c[0], c[1]
        toy_y = arm_y0 + (y - 19.60) * s_y
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped = shapely.Polygon([map_c(c) for c in ref_v2.exterior.coords])
    
    # Foot anchor
    foot_y1 = arm_y0 + BRD.FOOT_OVERLAP
    foot_poly = shapely.Polygon([
        (BRD.FOOT_Y0, BRD.LEAF_R0),
        (BRD.FOOT_Y0, BRD.RAIL_R1),
        (foot_y1, BRD.RAIL_R1),
        (foot_y1, 9.851),
        (47.00, 9.851),
        (47.00, BRD.LEAF_R0),
        (BRD.FOOT_Y0, BRD.LEAF_R0)
    ])
    
    merged = unary_union([mapped, foot_poly])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
    
    # Clip inner bore face below foot_y1
    merged = merged.difference(shapely.box(0.0, 0.0, foot_y1, BRD.LEAF_R0))
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
        
    return shapely.Polygon(merged.exterior)

def build_v2_dual_profile():
    poly_single = build_v2_single_profile()
    
    # Upper head geometry: duplicate the exact v2 upper flexure loop & teardrop head,
    # shifted axially by 3 * TOOTH_PITCH = 9.532 mm (from nose at 57.407 mm to 66.939 mm)
    # The upper flexure loop in v2 starts at y >= 33.0 in ref_v2 coords
    upper_loop_ref = ref_v2.intersection(shapely.box(0.0, 33.0, 20.0, 55.0))
    
    x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
    r_dst = np.array([BRD.NOSE_APEX, 7.0000, 7.6000, 8.3500,  8.9000,  9.6500, 10.2500, BRD.ARM_R_OUT])

    pitch_shift = 3.0 * BRD.TOOTH_PITCH # 9.53199 mm
    
    def map_upper(c):
        x, y = c[0], c[1]
        toy_y = BRD.ARM_Y0 + (y - 19.60) * BRD.ARM_SCALE_Y + pitch_shift
        toy_r = float(np.interp(x, x_src, r_dst))
        return (toy_y, toy_r)

    mapped_upper = shapely.Polygon([map_upper(c) for c in upper_loop_ref.exterior.coords])
    
    # Connect outer spine between lower and upper loop
    # Spine runs from y = 60.0 to y = 62.916 + pitch_shift = 72.448 mm at r in [9.851, 10.900]
    spine_bridge = shapely.Polygon([
        (58.00, 9.851),
        (58.00, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, BRD.ARM_R_OUT),
        (62.916 + pitch_shift, 9.851),
        (58.00, 9.851)
    ])
    
    merged = unary_union([poly_single, mapped_upper, spine_bridge])
    if merged.geom_type == 'MultiPolygon':
        merged = max(merged.geoms, key=lambda q: q.area)
        
    return shapely.Polygon(merged.exterior)

p_s = build_v2_single_profile()
p_d = build_v2_dual_profile()

print(f"Single Profile: Bounds={p_s.bounds}, Area={p_s.area:.3f} mm2")
print(f"Dual Profile:   Bounds={p_d.bounds}, Area={p_d.area:.3f} mm2")

# Plot both profiles to visually inspect
fig, axes = plt.subplots(1, 2, figsize=(12, 10))

for ax, poly, title in [(axes[0], p_s, "V2 Single-Headed Spring"), (axes[1], p_d, "V2 Dual-Headed Spring")]:
    x, y = poly.exterior.xy
    ax.fill(y, x, color='#888888', edgecolor='black', linewidth=1.5)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel("Toy Y (axial) [mm]")
    ax.set_ylabel("Radius R [mm]")
    ax.set_title(title)

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "v2_spring_profiles_test.png"), dpi=200)
print("Saved v2_spring_profiles_test.png")
