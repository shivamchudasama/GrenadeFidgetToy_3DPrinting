import os
import sys
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))

import flexure_rate as FR
from test_waist_curves import build_curvy_v2_profile

for factor in [0.0, 0.8, 1.0, 1.2, 1.5]:
    poly = build_curvy_v2_profile(waist_bulge_factor=factor)
    res = FR.rate(poly, thickness=3.00,
                  fixed=lambda V: (V[:, 0] < 42.6) & (V[:, 1] > 11.0),
                  loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] < 60.0),
                  direction=(0.0, 1.0), h=0.06)
    print(f"Waist curve factor = {factor:.1f}: k = {res.k:.4f} N/mm, strain = {res.strain_per_mm*100:.3f}%/mm, Area = {poly.area:.2f} mm2")
