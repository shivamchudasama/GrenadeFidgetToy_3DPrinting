"""Build the custom toy of CUSTOM_DESIGN.md.

Phases, each checkable on its own:

    python tools/build_custom.py waist    # the clicking waist, built into the base
    python tools/build_custom.py head     # the folding handle head, on its hinge
    python tools/build_custom.py toy      # the whole toy, head folded and stowed
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
    """The head: gear on the outer rim, ring inside it, and the 90 degree fold."""
    items = custom.head_items()
    stem = "Custom_Head"
    _report(stem, items)

    d = dict(items)

    # 1. the gear on the rim, against the spring in the pod.
    # Only what turns with the handle counts here: the yoke sits 30 mm away at
    # the hinge, so letting it into `static` would have rays that pass clean
    # over the gear score as shrouded rim.
    g = d["Spinner Lever 05 - Gear"]
    static = trimesh.util.concatenate(
        [m for n, m in custom.swinging_items()
         if n != "Spinner Lever 05 - Gear"])
    C = custom.HEAD_C
    s = _sweep(g, static, [0, 0, 1], [C[0], C[1], 0], 18.0, 1.0)
    print("      gear detent over one 18 deg tooth pitch: %.2f .. %.2f mm3,"
          " %d of 19 free -> 20 clicks/turn" % (s.min(), s.max(),
                                                int((s < 1e-6).sum())))

    # How much of the rim can a thumb actually reach? Sampled off the z = 0
    # split plane, and at more than one height: the pawl this replaced was two
    # half-leaves with a 0.30 mm slit down the middle, so a ray cast at z = 0
    # went straight through it and scored 48 deg of shrouded rim as open.
    n = 720
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ro = np.zeros(n)
    for zc in (-2.0, 2.0):
        o = np.column_stack([np.full(n, C[0]), np.full(n, C[1]), np.full(n, zc)])
        dirs = np.column_stack([np.cos(th), np.sin(th), np.zeros(n)])
        loc, idx, _ = static.ray.intersects_location(o, dirs, multiple_hits=True)
        rad = np.linalg.norm(loc[:, :2] - C, axis=1)
        for k, v in zip(idx, rad):
            ro[k] = max(ro[k], v)
    open_deg = (ro <= custom.GEAR_TIP_R).mean() * 360
    print("      rim standing proud of the handle over %.0f of 360 deg (%.0f%%)"
          % (open_deg, open_deg / 3.6))

    # 2. the fold, against the leaf spring seated in the yoke
    turning = trimesh.boolean.union(
        [m for _, m in custom.swinging_items()], engine=fidget.ENGINE)
    seat = trimesh.boolean.union(
        [d["Custom Hinge Yoke"], d[custom.HINGE_SPRING]], engine=fidget.ENGINE)
    s = _sweep(turning, seat, [0, 0, 1], [0.0, custom.HINGE_Y, 0.0], 90.0, 2.5)
    print("      fold detent over 0 .. 90 deg: %.2f .. %.2f mm3 on a 30.0 deg"
          " pitch -> 12 clicks/turn, 3 over the fold" % (s.min(), s.max()))

    coloured = A.coloured(items)
    return A.write(coloured, A.explode(coloured, axis=2, margin=6.0, gap=3.0),
                   stem, SUBDIR)


# ---------------------------------------------------------------- phase 3 ---
def build_toy(ring=True, mid_shell="2pc"):
    """The whole thing: clicking waist, rod with the yoke on it, folding head."""
    items = custom.toy_items(mid_shell=mid_shell, ring=ring, deg=0.0)
    stem = "Custom_Toy_%s_%s" % ("Ring" if ring else "Native", mid_shell)
    _report(stem, items)

    # Union, not concatenate: several of these pairs overlap by design -- the
    # fold detent, the gear pawl -- and manifold answers 0.00 for everything
    # when it is handed a self-intersecting mesh, which reads as a pass.
    d = dict(items)
    body = trimesh.boolean.union(
        [m for _, m in custom.waist_items(mid_shell=mid_shell, ring=ring)],
        engine=fidget.ENGINE)

    # the fold has to clear the body, not just the yoke
    M = custom.module_transform()
    turning = trimesh.boolean.union(
        [m for _, m in custom.swinging_items()], engine=fidget.ENGINE)
    turning.apply_transform(M)
    axis = M[:3, :3] @ np.array([0.0, 0.0, 1.0])
    centre = (M @ np.array([0.0, custom.HINGE_Y, 0.0, 1.0]))[:3]
    s = _sweep(turning, body, axis, centre, 90.0, 2.5)
    print("      head against the body over the fold: %.2f .. %.2f mm3"
          % (s.min(), s.max()))

    # and the rod still clicks on its way up, carrying all of it
    moving = trimesh.boolean.union(
        [d["Custom Rod"], d["Spinner Lever 08 - Rod Lock"], turning],
        engine=fidget.ENGINE)
    trav = []
    for dy in np.arange(0.0, 9.01, 0.5):
        m = moving.copy()
        m.apply_translation([0.0, dy, 0.0])
        trav.append(trimesh.boolean.intersection(
            [m, body], engine=fidget.ENGINE).volume)
    trav = np.array(trav)
    print("      linear click over 9 mm of rod travel: %.2f .. %.2f mm3 on the"
          " 3.000 mm serration pitch" % (trav.min(), trav.max()))

    coloured = A.coloured(items)
    return A.write(coloured, A.explode(coloured), stem, SUBDIR)


# ---------------------------------------------------------------- printing --
def _blocked_bores(half, pins):
    """Pin axes that are not actually bored through this half.

    A ray straight down a finished bore hits nothing at all. This catches the
    failure that volume tests cannot: a **zero-thickness skin** left across the
    hole where a cut tool's face landed coplanar with the mating face. It has
    no volume, so interference reads 0.000 and containment reads empty, but a
    slicer closes the hole on it.
    """
    bad = []
    for n, pin in pins:
        # only the full-width pins are meant to go through: 18/19/20 - Handle
        # Stapler Lock are 13.8 mm in a 19.0 mm handle and are blind by design
        if pin.bounds[1][2] - pin.bounds[0][2] < 18.9:
            continue
        c = pin.bounds.mean(axis=0)
        loc, _, _ = half.ray.intersects_location(
            np.array([[c[0], c[1], -60.0]]), np.array([[0.0, 0.0, 1.0]]),
            multiple_hits=True)
        if len(loc):
            bad.append((n, np.round(np.sort(loc[:, 2]), 3).tolist()))
    return bad


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
        "Custom_Rod":                 custom.custom_rod(),
    }
    made.update({"Custom_" + A.slug(n): m for n, m in custom.relocated_pins()})
    pins = custom.relocated_pins()
    for side in ("13 - Handle Left", "14 - Handle Right"):
        bad = _blocked_bores(custom.handle_half(side), pins)
        if bad:
            raise SystemExit("%s: bore not open -- %s" % (side, bad))
    print("      bores open in both halves (%d pins)" % len(pins))

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
    if what in ("toy", "all"):
        build_toy(ring=True)
        build_toy(ring=False)
    if what in ("parts", "all"):
        build_parts()


if __name__ == "__main__":
    main(sys.argv)
