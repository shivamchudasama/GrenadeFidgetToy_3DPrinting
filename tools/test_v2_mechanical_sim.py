import os
import sys
import trimesh
import numpy as np
import shapely

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))
import flexure_rate as FR
import build_rod_detent as BRD
from test_build_v2_package import build_v2_single_profile, build_v2_dual_profile

poly_s = build_v2_single_profile()
poly_d = build_v2_dual_profile()

print("=== FEA & Mechanical Analysis of v2 Springs ===")

# Lower Head Rate (Single Spring or Lower Head of Dual Spring)
res_lo = FR.rate(poly_s, thickness=3.00,
                 fixed=lambda V: (V[:, 0] < 43.0) & (V[:, 1] > 11.0),
                 loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] < 60.0),
                 direction=(0.0, 1.0), h=0.06)

print(f"\n[Lower Head / Single Spring]")
print(f"  Rate k:           {res_lo.k:.4f} N/mm")
print(f"  Peak Strain/mm:   {res_lo.strain_per_mm * 100:.3f} %/mm")
print(f"  Deflection:       {6.8901 - 5.5400:.3f} mm")
print(f"  Peak Radial Force:{res_lo.k * (6.8901 - 5.5400):.3f} N")
print(f"  Peak Strain @max: {res_lo.strain_at(6.8901 - 5.5400) * 100:.3f}% (Budget: 2.50%)")

# Upper Head Rate (Dual Spring)
res_hi = FR.rate(poly_d, thickness=3.00,
                 fixed=lambda V: (V[:, 0] < 43.0) & (V[:, 1] > 11.0),
                 loaded=lambda V: (V[:, 1] < 7.20) & (V[:, 0] > 64.0),
                 direction=(0.0, 1.0), h=0.06)

print(f"\n[Upper Head of Dual Spring]")
print(f"  Rate k:           {res_hi.k:.4f} N/mm")
print(f"  Peak Strain/mm:   {res_hi.strain_per_mm * 100:.3f} %/mm")
print(f"  Deflection:       {6.8901 - 5.5400:.3f} mm")
print(f"  Peak Radial Force:{res_hi.k * (6.8901 - 5.5400):.3f} N")
print(f"  Peak Strain @max: {res_hi.strain_at(6.8901 - 5.5400) * 100:.3f}% (Budget: 2.50%)")

# Total System Click Forces:
# Hybrid Grenade has 4 spring positions (0°, 90°, 180°, 270°).
# In Option B:
# Positions 0° & 180° have single-headed springs (2 lower heads).
# Positions 90° & 270° have dual-headed springs (2 lower heads + 2 upper heads = 4 heads).
# Total heads engaging the rack = 2 + 4 = 6 heads!
f_rad_total_peak = 4.0 * res_lo.k * (6.8901 - 5.5400) + 2.0 * res_hi.k * (6.8901 - 5.5400)
# Dynamic axial detent force with 40.63 deg flank and friction mu ~ 0.12
theta = np.radians(40.63)
mu = 0.12
f_ax_total_peak = f_rad_total_peak * (np.tan(theta) + mu) / (1.0 - mu * np.tan(theta))
print(f"\n[Complete 4-Slot Assembly (2 Single + 2 Dual = 6 Detent Heads)]")
print(f"  Total Peak Radial Force: {f_rad_total_peak:.3f} N")
print(f"  Total Peak Axial Detent Force (Thumb Feel): {f_ax_total_peak:.3f} N")
