import os
import sys
import numpy as np
import shapely
from shapely.ops import unary_union
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

from test_pure_v2_mapping import ref_arm_cut, map_axial
import build_rod_detent as BRD

def build_curvy_v2_profile(waist_bulge_factor=1.0):
    # Map coordinates preserving and enhancing the inner waist S-curve
    def map_pt(p):
        r, y = p[0], p[1]
        toy_y = map_axial(y)

        # Upper feature targets
        x_src_up = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
        
        # When r is around the inner waist (r in [7.384, 10.4509] at y in [25.0, 38.0]):
        # We allow r_dst to reach higher values to give a much more pronounced, curvy S-shape!
        r_waist_peak = 8.55 + 0.65 * waist_bulge_factor # e.g. 9.20 mm
        r_dst_up = np.array([BRD.NOSE_APEX, 7.0000, 7.6000, 8.3500, r_waist_peak, 9.6500, 10.2500, BRD.ARM_R_OUT])

        x_src_lo = np.array([7.384, 9.950])
        r_dst_lo = np.array([7.400, 12.200])

        t = float(np.clip((y - 24.0) / 10.0, 0.0, 1.0))
        r_up = float(np.interp(r, x_src_up, r_dst_up))
        r_lo = float(np.interp(r, x_src_lo, r_dst_lo))

        toy_r = (1.0 - t) * r_lo + t * r_up
        
        # Extra organic curvature enhancement on the inner waist (y in [30.0, 38.0] in v2 -> toy_y in [46.0, 55.0])
        # If the point is on the inner face (r < 10.5 in v2):
        if 26.0 <= y <= 38.5 and r <= 10.5:
            u_curve = np.sin((y - 26.0) / (38.5 - 26.0) * np.pi)
            toy_r += 0.45 * waist_bulge_factor * u_curve

        return (toy_y, toy_r)

    mapped_pts = [map_pt(c) for c in ref_arm_cut.exterior.coords]
    poly = shapely.Polygon(mapped_pts)
    return shapely.Polygon(poly.exterior)

# Generate 3 variations of curvature
p_base = build_curvy_v2_profile(waist_bulge_factor=0.0) # previous
p_curve1 = build_curvy_v2_profile(waist_bulge_factor=1.0) # curvy +1
p_curve2 = build_curvy_v2_profile(waist_bulge_factor=1.5) # curvy +1.5

fig, axes = plt.subplots(1, 3, figsize=(15, 14))

for ax, poly, title in [(axes[0], p_base, "Previous (Flatter Waist)"),
                        (axes[1], p_curve1, "Option 1: Enhanced Organic Curve"),
                        (axes[2], p_curve2, "Option 2: Pronounced Deep Curve")]:
    py, pr = poly.exterior.xy
    ax.plot([-r for r in pr], py, color='#22cc66', linewidth=2)
    ax.fill([-r for r in pr], py, color='#999999', alpha=0.9)
    
    # Highlight the waist box
    rect = plt.Rectangle((-9.5, 45.0), 2.5, 11.0, fill=False, edgecolor='red', linewidth=2.5, linestyle='--')
    ax.add_patch(rect)
    
    ax.set_aspect('equal')
    ax.grid(True, color='#444444')
    ax.set_facecolor('#222222')
    ax.set_title(title, color='white', pad=10)
    ax.tick_params(colors='white')

fig.patch.set_facecolor('#181818')
plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "compare_waist_curves.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved compare_waist_curves.png")
