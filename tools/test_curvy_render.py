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

def build_curvy_v2_single_profile(curve_boost: float = 0.85):
    """Build single spring profile with enhanced curvy S-shape on the inner waist."""
    def map_pt(p):
        r, y = p[0], p[1]
        toy_y = map_axial(y)

        # Upper feature targets
        x_src_up = np.array([5.8532, 7.1240, 8.6509, 9.4509, 10.4509, 11.2509, 12.6509, 14.4509])
        r_dst_up = np.array([BRD.NOSE_APEX, 7.0000, 7.6000, 8.3500, 9.1500, 9.6500, 10.2500, BRD.ARM_R_OUT])

        x_src_lo = np.array([7.384, 9.950])
        r_dst_lo = np.array([7.400, 12.200])

        t = float(np.clip((y - 25.0) / 9.0, 0.0, 1.0))
        r_up = float(np.interp(r, x_src_up, r_dst_up))
        r_lo = float(np.interp(r, x_src_lo, r_dst_lo))

        toy_r = (1.0 - t) * r_lo + t * r_up

        # Smooth organic curvature boost on the inner waist (y in [26.0, 38.0] in v2 -> toy_y in [46.0, 55.0])
        if 26.0 <= y <= 38.0 and r <= 10.5:
            u_curve = np.sin((y - 26.0) / (38.0 - 26.0) * np.pi)
            toy_r += curve_boost * 0.40 * u_curve

        return (toy_y, toy_r)

    mapped_pts = [map_pt(c) for c in ref_arm_cut.exterior.coords]
    poly = shapely.Polygon(mapped_pts)
    return shapely.Polygon(poly.exterior)

p_curvy = build_curvy_v2_single_profile(curve_boost=0.85)

fig, ax = plt.subplots(figsize=(6, 14))
py, pr = p_curvy.exterior.xy
ax.plot([-r for r in pr], py, color='#22cc66', linewidth=2)
ax.fill([-r for r in pr], py, color='#999999', alpha=0.9)

# Highlight the waist area
rect = plt.Rectangle((-9.8, 44.0), 2.8, 12.0, fill=False, edgecolor='#22cc66', linewidth=2.5, linestyle='-')
ax.add_patch(rect)

ax.set_aspect('equal')
ax.grid(True, color='#444444')
ax.set_facecolor('#222222')
fig.patch.set_facecolor('#181818')
ax.set_title("Curvy V2 Spring Profile", color='white', pad=10)
ax.tick_params(colors='white')

plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "curvy_v2_spring_render.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved curvy_v2_spring_render.png")
