"""Worked example: modify a part and write the result to Derivatives/.

Copy this file, change the middle section, run it. The pattern is always the
same -- load, build CSG tools in the part's own coordinates, cut/union, check,
save.

    python tools/example_modify.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fidget  # noqa: E402


def main():
    # 1. load ------------------------------------------------------------
    # Parts sit at their original plate coordinates, not the origin, so build
    # tools relative to the part's own bounds rather than to (0, 0, 0).
    part = fidget.load("15 - Handle Rotating Lock", product="spinner")
    lo, hi = part.bounds
    cx, cy, cz = part.bounds.mean(axis=0)
    print("loaded %s  %s tri  bbox %s"
          % (part.metadata["fidget_source"], format(len(part.faces), ","),
             (hi - lo).round(3)))

    # 2. modify ----------------------------------------------------------
    # A lanyard hole through the part, 2 mm in from the +X face.
    hole = fidget.cylinder(d=2.0, h=(hi[2] - lo[2]) + 4, at=(hi[0] - 2.0, cy, cz))
    out = fidget.cut(part, hole)

    # 3. check -----------------------------------------------------------
    # body_count matters: a cut that severs the part leaves two solids and
    # will slice as two objects. Watertight alone does not catch that.
    print("result: %s tri  watertight=%s  bodies=%d  volume %.1f -> %.1f mm3"
          % (format(len(out.faces), ","), out.is_watertight, out.body_count,
             part.volume, out.volume))
    if out.body_count > 1:
        print("   WARNING: cut split the part into %d bodies" % out.body_count)

    # 4. save ------------------------------------------------------------
    fidget.save(out, "15 - Handle Rotating Lock - lanyard.stl", subdir="spinner")


if __name__ == "__main__":
    main()
