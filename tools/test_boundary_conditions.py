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

from test_strand_tuning import build_v2_optimized_profiles

ps, pd = build_v2_optimized_profiles(strand_w=0.75)

# For the lower head: fixed at foot (Y < 42.6, R > 11.0)
res_lo = FR.rate(ps, thickness=3.00,
                 fixed=lambda V: (V[:, 0] < 42.6) & (V[:, 1] > 11.0),
                 loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] < 60.0),
                 direction=(0.0, 1.0), h=0.07)

# For the upper head of the dual spring:
# The outer spine passes through the slotted cap at Y = 63.24, where the cap slot wall laterally supports the outer spine!
# So for the upper head deflection, the outer spine is supported at Y in [62.0, 64.0] (the cap)!
res_hi_supported = FR.rate(pd, thickness=3.00,
                           fixed=lambda V: ((V[:, 0] < 42.6) & (V[:, 1] > 11.0)) | ((V[:, 0] > 62.0) & (V[:, 0] < 64.5) & (V[:, 1] > 10.0)),
                           loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] > 64.0),
                           direction=(0.0, 1.0), h=0.07)

print(f"Lower Head (Free cantilever): k = {res_lo.k:.4f} N/mm, strain/mm = {res_lo.strain_per_mm*100:.3f}%/mm")
print(f"Upper Head (Cap-supported):   k = {res_hi_supported.k:.4f} N/mm, strain/mm = {res_hi_supported.strain_per_mm*100:.3f}%/mm")
