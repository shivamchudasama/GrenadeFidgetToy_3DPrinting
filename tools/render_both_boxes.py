import os
import sys
import trimesh
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

from test_perfect_smooth import build_perfect_smooth_v2_profile
import build_dual_headed_springs as BDHS

p_old = BDHS.build_v2_single_profile()
p_new = build_perfect_smooth_v2_profile()

fig, axes = plt.subplots(1, 2, figsize=(10, 16))

# Plot Old (matches user screenshot orientation: -R on horizontal axis, Y on vertical)
y_o, r_o = p_old.exterior.xy
axes[0].plot([-r for r in r_o], y_o, color='#cc2222', linewidth=2)
axes[0].fill([-r for r in r_o], y_o, color='#999999', alpha=0.9)
# Draw red boxes on old
rect1_o = plt.Rectangle((-11.5, 51.0), 1.6, 6.0, fill=False, edgecolor='red', linewidth=3, linestyle='--')
rect2_o = plt.Rectangle((-7.6, 36.0), 0.7, 10.0, fill=False, edgecolor='red', linewidth=3, linestyle='--')
axes[0].add_patch(rect1_o)
axes[0].add_patch(rect2_o)
axes[0].set_aspect('equal')
axes[0].grid(True, color='#444444', linestyle=':')
axes[0].set_facecolor('#222222')
axes[0].set_title("PREVIOUS (With Both Irregularities)", color='white', pad=10)
axes[0].tick_params(colors='white')

# Plot New (Smooth)
y_n, r_n = p_new.exterior.xy
axes[1].plot([-r for r in r_n], y_n, color='#22cc66', linewidth=2)
axes[1].fill([-r for r in r_n], y_n, color='#999999', alpha=0.9)
# Draw green boxes on new
rect1_n = plt.Rectangle((-11.5, 51.0), 1.6, 6.0, fill=False, edgecolor='#22cc66', linewidth=3, linestyle='-')
rect2_n = plt.Rectangle((-7.6, 36.0), 0.7, 10.0, fill=False, edgecolor='#22cc66', linewidth=3, linestyle='-')
axes[1].add_patch(rect1_n)
axes[1].add_patch(rect2_n)
axes[1].set_aspect('equal')
axes[1].grid(True, color='#444444', linestyle=':')
axes[1].set_facecolor('#222222')
axes[1].set_title("REFINED (Both Irregularities Removed)", color='white', pad=10)
axes[1].tick_params(colors='white')

fig.patch.set_facecolor('#181818')
plt.tight_layout()
plt.savefig(os.path.join(ROOT_DIR, "tools", "compare_both_boxes.png"), dpi=200, facecolor=fig.get_facecolor())
print("Saved compare_both_boxes.png")
