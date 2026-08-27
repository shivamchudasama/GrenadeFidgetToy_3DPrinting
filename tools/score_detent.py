"""Score every detent in Hybrid_Grenade_v1.1, so a change to one cannot quietly
break another.

Each of the toy's five motions is a follower riding a notched track.  The thing
that decides how a detent *feels* is the swept overlap between the two: how far
it rises (peak), and -- just as important -- whether it ever falls to nothing.
A detent whose trough is zero unloads completely at each click, so it holds the
part nowhere and a print a tenth of a millimetre loose has no click at all.

    python tools/score_detent.py            # all five motions
    python tools/score_detent.py axial      # just one

Everything is measured against All_Parts_Assembled_Coordinates, which is the
checked-in solved assembly, not a rebuild of it.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from package_paths import ASSEMBLED_DIR as PACKAGE_ASSEMBLED_DIR, ROOT_DIR
ASSEMBLED = PACKAGE_ASSEMBLED_DIR
ENGINE = "manifold"
T = trimesh.transformations

# The rack the middle rod and both side clamps carry, measured off the shipped
# STLs: crest |z| 6.8901, V-root |z| 5.7652, straight 40.63 deg flanks.
ROD_TOOTH_PITCH = 3.17733
RACK_FLANK_DEG = 40.63


def load(name):
    m = trimesh.load(os.path.join(ASSEMBLED, name), process=True)
    m.merge_vertices()
    trimesh.repair.fill_holes(m)
    trimesh.repair.fix_normals(m)
    return m


def _overlap(a, b):
    try:
        x = trimesh.boolean.intersection([a, b], engine=ENGINE)
    except Exception:
        return float("nan")
    if x is None or len(x.faces) == 0:
        return 0.0
    return abs(x.volume)


def sweep(moving, static, span, step, rotate=None, translate=None):
    """Swept overlap of `moving` against `static` over one detent period.

    `rotate` is (axis, centre) and `span`/`step` are degrees; `translate` is a
    direction and they are millimetres.
    """
    out = []
    for u in np.arange(0.0, span + 1e-9, step):
        if rotate is not None:
            axis, centre = rotate
            M = T.rotation_matrix(np.radians(u), axis, centre)
        else:
            M = T.translation_matrix(np.asarray(translate, dtype=float) * u)
        total = 0.0
        for part in moving:
            c = part.copy()
            c.apply_transform(M)
            for s in static:
                if (c.bounds[0] > s.bounds[1]).any() or (c.bounds[1] < s.bounds[0]).any():
                    continue
                total += _overlap(c, s)
        out.append(total)
    return np.asarray(out), np.arange(0.0, span + 1e-9, step)


def _axis_centre(mesh, axis_index):
    """Unit axis vector and the part's bbox centre, for a part turning about it."""
    axis = np.zeros(3)
    axis[axis_index] = 1.0
    return axis, mesh.bounds.mean(axis=0)


# ------------------------------------------------------------------ motions --
def motion_waist():
    """33-click rotary waist: the mid shell's 33-lobe bore over the spring arms."""
    spring = load("09_Custom_Mid_Shell_Spring_33.stl")
    shell = load("07_32_Mid_Shell_P02_Ratchet.stl")
    span = 360.0 / 33.0
    vals, us = sweep([shell], [spring], span, span / 24.0,
                     rotate=(np.array([0.0, 1.0, 0.0]), np.zeros(3)))
    return "waist twist (33 clicks/turn)", vals, us, "deg", span


def motion_rim_gear():
    """20-click rim gear: Spinner Lever 05 turning against its own detent spring."""
    gear = load("32_Spinner_Lever_05_Gear.stl")
    spring = load("33_Spinner_Lever_04_Spring.stl")
    axis, centre = _axis_centre(gear, 0)          # the gear spins about toy +x
    span = 360.0 / 20.0
    vals, us = sweep([gear], [spring], span, span / 24.0, rotate=(axis, centre))
    return "rim gear (20 clicks/turn)", vals, us, "deg", span


def motion_fold():
    """4-position fold: the handle hub's 12 notches over the hinge leaf."""
    leaf = load("28_09_Rod_Spring_Hinge.stl")
    pin = load("36_15_Handle_Rotating_Lock_D_Pin.stl")
    axis, centre = _axis_centre(pin, 0)           # hinge pin runs along toy +x
    halves = [load("29_Custom_Handle_Left.stl"), load("30_Custom_Handle_Right.stl")]
    span = 30.0
    vals, us = sweep(halves, [leaf], span, span / 24.0, rotate=(axis, centre))
    return "handle fold (12 notches, 30 deg)", vals, us, "deg", span


def _rod_members():
    return [load("23_Custom_Rod_Middle.stl"),
            load("22_Custom_Rod_Right.stl"),
            load("24_Custom_Rod_Left.stl")]


def _rod_followers():
    """Whatever is currently fitted in the barrel's three follower slots."""
    for names in (("15_Custom_Rod_C_Follower_01.stl",
                   "16_Custom_Rod_C_Follower_02.stl"),
                  ("15_Custom_Rod_Detent_Follower_01.stl",
                   "16_Custom_Rod_Detent_Follower_02.stl",
                   "17_Custom_Rod_Detent_Follower_03.stl"),
                  ("15_12_Internal_Barrel_Spring_01.stl",
                   "16_13_Internal_Barrel_Spring_02.stl",
                   "17_14_Internal_Barrel_Spring_03.stl")):
        if all(os.path.exists(os.path.join(ASSEMBLED, n)) for n in names):
            return [load(n) for n in names], names
    raise FileNotFoundError("no rod detent followers found in %s" % ASSEMBLED)


def motion_axial():
    """The up/down rod click: the rack running past the three barrel followers."""
    followers, _ = _rod_followers()
    span = ROD_TOOTH_PITCH
    vals, us = sweep(_rod_members(), followers, span, span / 24.0,
                     translate=np.array([0.0, 1.0, 0.0]))
    return "axial rod push/pull", vals, us, "mm", span


def axial_force_curve(followers=None, steps=33):
    """The axial force a thumb feels through one click, in newtons.

    Swept overlap says how much material two parts share; it does not say how
    hard the toy pushes back.  Force does, and it is what "the click feels
    weak" actually means.  For each rod position this takes the deepest the
    rack pushes a follower nose, turns that into a radial force through the
    follower's measured spring rate, and projects it along the rod through the
    rack's 40.63 degree flank.

    Returns (offsets_mm, axial_force_N).
    """
    import flexure_rate as FR

    if followers is None:
        followers = _rod_followers()[0]
    # The rate has to match the design that is fitted, including where it is
    # anchored.  build_rod_detent knows that for the part it builds; fall back
    # to the generic serpentine solver only for the older leaf followers.
    import build_rod_detent as BRD

    if len(followers) == len(BRD.OUTPUTS):
        res = BRD.arm_rate()
    else:
        res = FR.follower_rate(FR.follower_profile(followers[0]))
    rod = trimesh.util.concatenate(_rod_members())
    slope = np.tan(np.radians(RACK_FLANK_DEG))

    offsets = np.linspace(0.0, ROD_TOOTH_PITCH, steps)
    force = []
    for dy in offsets:
        moved = rod.copy()
        moved.apply_transform(T.translation_matrix([0.0, dy, 0.0]))
        pen = max(trimesh.proximity.ProximityQuery(moved).signed_distance(f.vertices).max()
                  for f in followers)
        force.append(len(followers) * res.k * max(float(pen), 0.0) * slope)
    return offsets, np.asarray(force)


MOTIONS = {
    "waist": motion_waist,
    "rim": motion_rim_gear,
    "fold": motion_fold,
    "axial": motion_axial,
}


def per_follower():
    """Which follower does how much of the axial work, and how close each sits."""
    followers, names = _rod_followers()
    members = _rod_members()
    rod = trimesh.util.concatenate(members)
    pq = trimesh.proximity.ProximityQuery(rod)
    print("\n  axial detent, follower by follower")
    print("    %-42s %9s %13s" % ("follower", "peak mm3", "at seat mm"))
    span = ROD_TOOTH_PITCH
    for f, n in zip(followers, names):
        vals, _ = sweep(members, [f], span, span / 24.0,
                        translate=np.array([0.0, 1.0, 0.0]))
        gap = -pq.signed_distance(f.vertices).max()
        note = "clear" if gap > 0 else "PRELOAD"
        print("    %-42s %9.3f %+9.4f %s" % (n, vals.max(), -gap, note))


def report(keys):
    print("=" * 78)
    print("DETENT SCORES -- %s" % ASSEMBLED)
    print("=" * 78)
    print("%-34s %9s %9s %8s %10s" % ("motion", "peak mm3", "trough", "ratio", "period"))
    for k in keys:
        label, vals, _us, unit, span = MOTIONS[k]()
        peak, trough = float(vals.max()), float(vals.min())
        ratio = "inf" if trough <= 1e-6 else "%.1f" % (peak / trough)
        print("%-34s %9.3f %9.3f %8s %7.3f %s"
              % (label, peak, trough, ratio, span, unit))
        if k == "axial":
            print("      %s" % "  ".join("%.2f" % v for v in vals))
    if "axial" in keys:
        per_follower()
        offs, force = axial_force_curve()
        dead = float(np.mean(force <= 1e-6))
        print()
        print("  axial detent, as force through one click")
        print("    peak %.2f N   held at the seat %.2f N   dead band %.0f%% of the pitch"
              % (force.max(), force.min(), 100 * dead))
        print("    " + "  ".join("%.1f" % f for f in force))
    print()
    print("Swept volume says how much two parts share; force says how hard the")
    print("toy pushes back, and that is what a weak click actually means.  A")
    print("force of 0.00 N at the seat is a dead band: nothing holds the part")
    print("between clicks, and print tolerance can erase the click entirely.")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a in MOTIONS]
    report(args or list(MOTIONS))
