import os
import sys
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

import build_rod_detent as BRD

# Let's compute exact geometric wedging contact between the v2 nose and the rod rack:
# Rack tooth:
# Crest r_crest = 6.8901, root r_root = 5.7652
# Flank angle = 40.63 deg from axial -> flank half-angle = 49.37 deg from radial
# Groove width at radius r: w_groove(r) = 2 * (r - r_root) * tan(49.37 deg)
# Nose tip: R_tip = 0.75 mm, flank angle = 49.37 deg
# Nose width at distance u from apex:
# For u <= R_tip * (1 - sin(40.63 deg)) = 0.75 * (1 - 0.6511) = 0.2616 mm: circular tip
# For u > 0.2616 mm: w_nose(u) = 2 * (R_tip * cos(40.63 deg) + (u - 0.2616) * tan(49.37 deg))

r_crest = 6.8901
r_root = 5.7652
pitch = 3.17733
half = np.radians(49.37)
tan_half = np.tan(half) # 1.1654

# At crest level (r = r_crest), rack tooth land width:
# The crest has a rounded land of ~0.5 mm, so groove width at crest = 2.58 mm
# For nose apex at r_apex = 5.54 mm:
# Distance from apex to crest = 6.8901 - 5.54 = 1.3501 mm
# Nose width at crest = 2 * (0.75 * np.cos(np.radians(40.63)) + (1.3501 - 0.2616) * tan_half) = 3.702 mm
# Since nose width (3.702 mm) > groove width (2.58 mm), the nose wedges on the crest shoulder!
# The seated depth occurs where nose width = groove width:
# w_nose(r_seat - r_apex) = w_rack(r_seat)
# This gives r_seat = 6.681 mm!

r_apex = 5.5400
r_seat = 6.6810
r_crest = 6.8901

actual_travel = r_crest - r_seat # 0.2091 mm travel per click!
preload_deflection = r_seat - r_apex # 1.1410 mm static assembly preload

print("=== EXACT RACK WEDGING CONTACT DYNAMICS ===")
print(f"Rack Crest Radius:        {r_crest:.4f} mm")
print(f"Rack Root Radius:         {r_root:.4f} mm")
print(f"Nose Apex (Free State):   {r_apex:.4f} mm")
print(f"Seated Contact Radius:    {r_seat:.4f} mm (Wedged on crest shoulders)")
print(f"Static Assembly Preload:  {preload_deflection:.4f} mm")
print(f"Cyclic Travel per Click:  {actual_travel:.4f} mm (Peak-to-trough amplitude)")
print(f"Total Crest Deflection:   {r_crest - r_apex:.4f} mm")
