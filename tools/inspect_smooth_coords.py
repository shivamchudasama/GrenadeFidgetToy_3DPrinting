import os
import sys
import numpy as np
import shapely
import matplotlib.pyplot as plt

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

from test_smooth_spine import build_smooth_v2_single_profile

poly = build_smooth_v2_single_profile()
coords = np.array(poly.exterior.coords)

# Let's inspect points on the outer edge (where R is large, between Y=36 and Y=63)
# In (Y, R) coordinates:
# Let's sort points by Y
print("Points count:", len(coords))
outer_pts = coords[(coords[:, 1] > 9.0)]
# Sort by Y
outer_pts = outer_pts[np.argsort(outer_pts[:, 0])]

print("\n--- Outer Edge Points (Y, R) ---")
for y, r in outer_pts:
    print(f"  Y = {y:7.3f} mm, R = {r:7.3f} mm")
