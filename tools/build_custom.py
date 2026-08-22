"""Build the custom toy of CUSTOM_DESIGN.md.

Phases, each checkable on its own:

    python tools/build_custom.py waist    # the clicking waist, built into the base
    python tools/build_custom.py head     # the handle head, gear on the outer rim
    python tools/build_custom.py parts    # the changed parts as printable STLs
    python tools/build_custom.py          # everything

Output lands in Derivatives/custom/.
"""
from __future__ import annotations

import sys

import numpy as np
import trimesh

import assembly as A
import custom
import fidget

SUBDIR = "custom"
T = trimesh.transformations


def _report(stem, items):
    bb = np.array([m.bounds for _, m in items])
    bad = A.interference(items)
    print("%-38s %2d parts  %s mm  interference %d pairs (max %.2f mm3)" % (
        stem, len(items), np.round(bb[:, 1].max(0) - bb[:, 0].min(0), 1),
        len(bad), bad[0][0] if bad else 0.0), flush=True)
    for v, a, b in bad[:5]:
        print("      %8.2f mm3  %s / %s" % (v, a, b))
    return bad


def _sweep(moving, static, axis, centre, span, step):
    out = []
    for deg in np.arange(0.0, span + 1e-9, step):
        m = moving.copy()
        m.apply_transform(T.rotation_matrix(np.radians(deg), axis, centre))
        out.append(trimesh.boolean.intersection(
            [m, static], engine=fidget.ENGINE).volume)
    return np.array(out)


# ---------------------------------------------------------------- phase 1 ---
def build_waist(ring=True, mid_shell="2pc"):
    """The Tactical base with the rotary click built into it -- not stacked on."""
    items = custom.waist_items(mid_shell=mid_shell, ring=ring)
    stem = "Custom_Waist_%s_%s" % ("Ring" if ring else "Native", mid_shell)
    _report(stem, items)

    d = dict(items)
    spring = d["20 - Mid Shell Spring"]
    if ring:
        band, teeth = d["04 - Middle Spinner Shell"], 32
    else:
        band, teeth = d["32 - Mid Shell P02"], 33
    pitch = 360.0 / teeth
    s = _sweep(band, spring, [0, 1, 0], [0, 0, 0], pitch, pitch / 22.0)
    print("      detent over one %.3f deg notch: %.2f .. %.2f mm3 -> %d clicks/turn"
          "  (stock base: 0.00 .. 6.43)" % (pitch, s.min(), s.max(), teeth))

    coloured = A.coloured(items)
    return A.write(coloured, A.explode(coloured), stem, SUBDIR)


# ---------------------------------------------------------------- phase 2 ---
def build_head():
    """The handle head: the gear on the outer rim, ring spinner still inside."""
    items = custom.head_items()
    _report("Custom_Head", items)

    d = dict(items)
    g = d["Spinner Lever 05 - Gear"]
    static = trimesh.util.concatenate(
        [m for n, m in items if n != "Spinner Lever 05 - Gear"])
    C = custom.HEAD_C
    s = _sweep(g, static, [0, 0, 1], [C[0], C[1], 0], 18.0, 1.0)
    print("      detent over one 18 deg tooth pitch: %.2f .. %.2f mm3, %d of 19 free"
          " -> 20 clicks/turn" % (s.min(), s.max(), int((s < 1e-6).sum())))

    # how much of the rim can a thumb actually reach?
    n = 720
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    o = np.column_stack([np.full(n, C[0]), np.full(n, C[1]), np.zeros(n)])
    dirs = np.column_stack([np.cos(th), np.sin(th), np.zeros(n)])
    loc, idx, _ = static.ray.intersects_location(o, dirs, multiple_hits=True)
    rad = np.linalg.norm(loc[:, :2] - C, axis=1)
    ro = np.zeros(n)
    for k, v in zip(idx, rad):
        ro[k] = max(ro[k], v)
    open_deg = (ro <= custom.GEAR_TIP_R).mean() * 360
    print("      rim standing proud of the handle over %.0f of 360 deg (%.0f%%)"
          % (open_deg, open_deg / 3.6))

    coloured = A.coloured(items)
    return A.write(coloured, A.explode(coloured, axis=2, margin=6.0, gap=3.0),
                   "Custom_Head", SUBDIR)


# ---------------------------------------------------------------- printing --
def build_parts():
    """Every part this build changes, as its own STL."""
    made = {
        "Custom_Mid_Shell_Spring_32": custom.waist_spring(),
        "Custom_Mid_Shell_Spring_33": custom.waist_spring(
            angles=custom.NOSE_ANGLES_33, dy=0.0),
        "Custom_Mid_Shell_P02":       custom.trimmed_mid_shell("32 - Mid Shell P02"),
        "Custom_Mid_Shell_P01":       custom.trimmed_mid_shell("33 - Mid Shell P01"),
        "Custom_Handle_Left":         custom.handle_half("13 - Handle Left"),
        "Custom_Handle_Right":        custom.handle_half("14 - Handle Right"),
        "Custom_Ring_Spinner":        custom.ring_spinner_slim(),
    }
    made.update({"Custom_" + A.slug(n): m for n, m in custom.relocated_pins()})
    out = []
    for name, m in made.items():
        if not m.is_watertight or m.body_count != 1:
            raise SystemExit("%s is not a single watertight body "
                             "(watertight=%s bodies=%d)"
                             % (name, m.is_watertight, m.body_count))
        out.append(fidget.save(m, name + ".stl", subdir=SUBDIR + "/Parts"))
    return out


def main(argv):
    what = argv[1] if len(argv) > 1 else "all"
    if what in ("waist", "all"):
        build_waist(ring=True)
        build_waist(ring=False)
    if what in ("head", "all"):
        build_head()
    if what in ("parts", "all"):
        build_parts()


if __name__ == "__main__":
    main(sys.argv)
