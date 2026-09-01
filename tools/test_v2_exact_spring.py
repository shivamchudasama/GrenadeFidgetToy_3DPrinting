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

print(f"ref_v2 bounds: {ref_v2.bounds}, area: {ref_v2.area:.3f}")

# Let's test a clean, precise mapping of ref_v2 into the slot
# Reference v2 key features:
# x in [5.8532, 14.4509]
# y in [19.6000, 48.0000]
# Nose apex at x=5.8532, y=40.5404
# Ascending beam outer x=11.2509, inner x=10.4509
# Descending beam outer x=9.4509, inner x=8.6509
# Outer rail inner x=12.6509, outer x=14.4509

# Target in toy slot:
# Axial: s_y = 0.74, arm_y0 = 41.90 -> y_toy = 41.90 + (y - 19.60) * 0.74
# Nose lands at y_toy = 41.90 + (40.5404 - 19.60) * 0.74 = 57.396 mm (matches tooth at 57.407 mm!)
# Loop top lands at y_toy = 41.90 + (48.00 - 19.60) * 0.74 = 62.916 mm (fits under cap at 63.24 mm!)

# Radial mapping:
# We want to preserve the exact geometric features and wall thicknesses
# Let's test mapping from x_src -> r_dst:
x_src = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
r_dst = np.array([5.5400, 7.0000, 7.6800, 8.3500,  8.5500,  9.3000,  9.8500, 10.9000])

# Let's also test a direct linear/affine or proportional radial map:
# If r_dst = 5.54 + (x - 5.8532) * (10.90 - 5.54) / (14.4509 - 5.8532)
# Scale factor = (10.90 - 5.54) / (14.4509 - 5.8532) = 5.36 / 8.5977 = 0.6234
# Let's check strand widths under both mappings:
print("\nStrand widths under piecewise mapping:")
print(f"  Descending beam: {r_dst[3] - r_dst[2]:.3f} mm")
print(f"  Inner loop gap:  {r_dst[4] - r_dst[3]:.3f} mm")
print(f"  Ascending beam:  {r_dst[5] - r_dst[4]:.3f} mm")
print(f"  Outer slot gap:  {r_dst[6] - r_dst[5]:.3f} mm")
print(f"  Outer spine:     {r_dst[7] - r_dst[6]:.3f} mm")

# Let's map ref_v2 directly using this mapping (or piece-wise continuous mapping)
def map_v2_point(p):
    x, y = p[0], p[1]
    toy_y = 41.90 + (y - 19.60) * 0.74
    # Smooth radial interpolation
    toy_r = float(np.interp(x, x_src, r_dst))
    return (toy_y, toy_r)

mapped_pts = [map_v2_point(c) for c in ref_v2.exterior.coords]
poly_v2_mapped = shapely.Polygon(mapped_pts)

print(f"\nMapped v2 body bounds (Y_toy, R): {poly_v2_mapped.bounds}, area: {poly_v2_mapped.area:.3f}")
