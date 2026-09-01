import os
import sys
import trimesh
import numpy as np
import shapely
from shapely.ops import unary_union
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

import build_rod_detent as BRD
import build_dual_headed_springs as BDHS
from test_smooth_organic import build_smooth_organic_profile

# 1. Previous notched profile
p_old = BDHS.build_v2_single_profile()
# 2. Smooth organic profile
p_new = build_smooth_organic_profile()

fig, axes = plt.subplots(1, 2, figsize=(10, 16))

# Plot Old (matches user screenshot orientation where -R is on the left)
y_o, r_o = p_old.exterior.xy
axes[0].plot([-r for r in r_o], y_o, color='#cc2222', linewidth=2.5)
axes[0].fill([-r for r in r_o], y_o, color='#999999', alpha=0.9)
# Draw red box around the notch
rect_old = plt.Rectangle((-11.2, 42.0), 2.0, 10.0, fill=False, edgecolor='red', linewidth=3, linestyle='--')
axes[0].add_patch(rect_old)
axes[0].set_aspect('equal')
axes[0].grid(True, color='#444444', linestyle=':')
axes[0].set_facecolor('#222222')
axes[0].set_title("PREVIOUS (With Irregularity Notch)", color='white', fontsize=12, pad=10)
axes[0].tick_params(colors='white')

# Plot New Smooth
y_n, r_n = p_new.exterior.xy
axes[1].plot([-r for r in r_n], y_n, color='#22cc66', linewidth=2.5)
axes[1].fill([-r for r in r_n], y_n, color='#999999', alpha=0.9)
# Draw green box around the smoothed region
rect_new = plt.Rectangle((-12.3, 42.0), 3.2, 10.0, fill=False, edgecolor='#22cc66', linewidth=3, linestyle='-')
axes[1].add_patch(rect_new)
axes[1].set_aspect('equal')
axes[1].grid(True, color='#444444', linestyle=':')
axes[1].set_facecolor('#222222')
axes[1].set_title("NEW (Smooth C² Continuous Curve)", color='white', fontsize=12, pad=10)
axes[1].tick_params(colors='white')

fig.patch.set_facecolor('#181818')
plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "smooth_curve_comparison.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved smooth_curve_comparison.png")
