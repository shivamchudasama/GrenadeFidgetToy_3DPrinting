"""Build the rod's axial detent follower.

WHY THIS PART EXISTS
--------------------
The up/down click of the central rod is produced by exactly one thing: three
followers seated in slots in ``08 - Internal Barrel`` at azimuth 90 / 210 / 330,
riding the sawtooth rack that the middle rod and both side clamps carry (crest
|z| 6.8901, V-root |z| 5.7652, straight 40.63 degree flanks, pitch 3.17733).
The barrel pins ``09/10/11`` sit 1.47-3.33 mm clear of the rod and take no part,
whatever the older notes say; nor does ``09_Custom_Mid_Shell_Spring_33``, which
clears the rod by 1.158 mm and is a rotary detent only.

The stock follower, ``12 - Internal Barrel Spring v1.1``, has a real defect: its
nose sits 0.10 mm CLEAR of the rack at every detent position.  Measured as
force, the click is a symmetric triangle peaking at 5.5 N in the middle of a
tooth and falling to *exactly zero* across the middle 12% of the pitch.  Around
every click there is a dead band where nothing holds the rod at all -- it coasts
the last fifth of a millimetre -- and since 0.10 mm is well inside print
variation, a given print can have no click whatsoever.

WHAT THIS CHANGES
-----------------
One thing: the nose tip is extended PRELOAD deeper, so contact is never lost.

The tip is a clean 0.7500 mm radius centred at (y 55.013, z 6.772), 2.60 mm
across.  Sweeping that circle PRELOAD further in leaves a capsule -- same tip
radius, so the way it sits in the rack's 40.63 degree V is unchanged and still
predictable, and the serpentine arm behind it is untouched, so its measured
rate still applies.

Moving the *whole* leaf inward instead does not work, and the reason is worth
recording: the follower is not one prismatic slab.  Its nose is 2.60 mm wide to
clear the narrow part of the barrel slot (3.14 mm) while the body behind it is
the full 3.75 mm, and those width steps line up with radial steps in the slot.
Shift the leaf bodily and its shoulders plough into the slot walls -- 2.8 mm3 of
interference at r 9.3 .. 12.8, which is exactly where that transition sits.

    python tools/build_rod_detent.py                # build and install
    python tools/build_rod_detent.py --dry-run      # report, write nothing
    python tools/build_rod_detent.py --preload 0.35 # a deeper bite
    python tools/build_rod_detent.py --sweep        # feel vs preload

Preload is the one number worth tuning on a real print; the model gets it
close, a thumb settles it.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import flexure_rate as FR
from package_paths import ASSEMBLED_DIR as PACKAGE_ASSEMBLED_DIR, guard

ROOT_DIR = os.path.dirname(TOOLS_DIR)
ASSEMBLED = PACKAGE_ASSEMBLED_DIR
ENGINE = "manifold"

# The stock follower, read from the pristine product folder rather than from
# the package: once the new part is installed the package copy is gone, and
# this file is the true origin anyway.  It already ships in toy assembly
# coordinates, so it needs no posing.
SOURCE = os.path.join(ROOT_DIR, "Fidget Fuse Tactical 7-in-1 Snap-Fit Fidget Toy",
                      "12 - Internal Barrel Spring v1.1.stl")
OUTPUTS = ("15_Custom_Rod_C_Follower_01.stl",
           "16_Custom_Rod_C_Follower_02.stl")
RETIRED = ("15_12_Internal_Barrel_Spring_01.stl",
           "16_13_Internal_Barrel_Spring_02.stl",
           "17_14_Internal_Barrel_Spring_03.stl",
           "15_Custom_Rod_Detent_Follower_01.stl",
           "16_Custom_Rod_Detent_Follower_02.stl",
           "17_Custom_Rod_Detent_Follower_03.stl")

# How much deeper the free-state nose sits.  Measured across both knobs, with
# 11 - Middle Spring and the v1.1 stock leaf as the two reference points:
#
#   thin  preload      k     peak    seat   dead   strain    median
#    (mm)    (mm)   N/mm       N       N      %   /click     strand
#    0.00    0.00   2.951    5.53    0.00    12    1.11%     0.800   v1.1 stock
#    0.00    0.45   2.943    8.13    1.74     0    1.64%     0.800   v1.2 first cut
#    0.15    0.15   1.239    2.71    0.03     0    0.94%     0.700
#    0.15    0.30   1.300    3.22    0.40     0    1.15%     0.700   <- default
#    0.15    0.45   1.316    3.63    0.78     0    1.30%     0.700
#   ( 11 - Middle Spring )  1.207    2.00    0.00     3    0.59%     ~1.0
#
# The default matches 11's rate to 7.7% and sits in its force class, while
# holding 0.40 N at every seat where 11 releases entirely for 3% of its pitch.
# Raising preload buys seating force and costs strain; the first cut at 0.45
# with no thinning was firm but worked the flexure harder than the stock part.
PRELOAD = 0.30

# How much to thin the serpentine strands, per side.
#
# The Spinner Fuse's `11 - Middle Spring` is the reference for how an axial
# detent should feel, and the measurable thing that makes it what it is is not
# force -- it is only 2.00 N peak against our 8.15 N -- but how gently it works
# its material: 1.207 N/mm on 0.714% strain per mm of travel, against this
# leaf's 2.951 N/mm on 1.278%.  Over the tens of thousands of clicks a fidget
# sees, that is the difference between a flexure that lasts and one that cracks.
#
# It buys that with size: a 32.6 x 34.8 mm open C with two long arms.  That
# cannot be transplanted.  The Tactical's follower slot is 17.5 x 8.4 mm, and
# the waist ring -- the only comparable envelope in the toy -- is chopped into
# 120 degree sectors by its own three outward arms, leaving ~55 degrees of
# usable wrap, far too short.  Compliance per unit strain scales with envelope,
# and the envelope is not there.
#
# So the same characteristics are reached the other way: a shorter path made
# thinner instead of a longer path left thick.  Both lower t/L^2.  Measured on
# the profile:
#
#   thin (mm)     k N/mm    strain %/mm      vs 11 - Middle Spring
#     0.00         2.951        1.278        stock, 2.4x stiffer
#     0.15         1.249        0.925        <- matches k to 3.5%
#     0.20         0.906        0.840
#     0.25         0.621        0.725        matches strain, too soft
#     ( 11 )       1.207        0.714
#
# 0.15 takes the strand from ~1.20 mm to ~0.90 mm, which is exactly two 0.45 mm
# perimeters -- still solidly printable.
THIN = 0.15

# Measured off the shipped rack and follower.  Toy coordinates, mm.
RACK_CREST = 6.8901
RACK_ROOT = 5.7652
FLANK_DEG = 40.63
TOOTH_PITCH = 3.17733

NOSE_Z = 6.0222         # free-state nose apex of the stock follower
NOSE_Y = 55.0130        # tip centre, along the rod
NOSE_R = 0.7500         # tip radius (measured to within 0.0003 mm)
NOSE_X0 = -1.2500       # the nose is narrower than the body, to clear the slot
NOSE_X1 = 1.3500
SEAT_Z = 14.451         # the straight back wall that bears on the barrel
BODY_W = 3.75

# Follower 01 faces the middle rod; the other two face the side clamps.
AZIMUTHS = (0.0, 120.0, 240.0)

# ---------------------------------------------------------------- up-stop ---
# The rod had no upward stop at all: swept to +24 mm it met nothing, so it
# could simply be pulled out of the toy and the click count was undefined.
#
# The stop is a pair of inward lands in the barrel that the retainer's own rim
# catches.  Growing the retainer instead does not work: above it the spacer
# bore is 8.30 mm from Y 16 to 27 and the first thing narrower is the waist
# spring's 7.915 mm bore, so a collar would have to live inside a 0.385 mm
# window -- inside FDM variation, so a given print would either bind in the
# spacer or slip past the spring.
#
# The lands sit at azimuth 90 and 270, where the rod presents only its rack
# crest (6.890) rather than a side clamp (7.857).  Half-width is 12 degrees
# because the rod's surface climbs away from those azimuths -- 7.044 at 78
# degrees -- and the land has to stay clear of it all the way across.
BARREL = "10_08_Internal_Barrel.stl"
BARREL_OUT = "10_Custom_Internal_Barrel_Stop.stl"
STOP_R = 7.40           # land inner radius; rod clears by 0.356 .. 0.510 mm
STOP_R_OUT = 10.50      # far enough out to merge into the barrel wall
STOP_HALF_DEG = 12.0
STOP_Y0 = 34.20         # clears the waist spring's top (33.75) by 0.45 mm
STOP_Y1 = 35.40
STOP_AZIMUTHS = (90.0, 270.0)
RETAINER = "27_Spinner_Lever_08_Rod_Lock.stl"


def _solidify(mesh, label=""):
    """Rebuild a mesh into something the boolean engine will accept.

    trimesh's own repair leaves the barrel watertight enough for a union but
    not for a checked difference, so round-trip it through manifold, which is
    the same engine the booleans use.
    """
    if mesh.is_watertight and mesh.body_count == 1:
        return mesh
    import manifold3d

    src = manifold3d.Mesh64(np.ascontiguousarray(mesh.vertices, dtype=np.float64),
                            np.ascontiguousarray(mesh.faces, dtype=np.uint64),
                            tolerance=1e-5)
    src.merge()
    solid = manifold3d.Manifold(src)
    if solid.is_empty():
        raise RuntimeError("could not solidify %s" % (label or "mesh"))
    rebuilt = solid.to_mesh64()
    return trimesh.Trimesh(vertices=np.asarray(rebuilt.vert_properties)[:, :3],
                           faces=np.asarray(rebuilt.tri_verts), process=False)


def _load(name):
    path = name if os.path.isabs(name) else os.path.join(ASSEMBLED, name)
    m = trimesh.load(path, process=True)
    m.merge_vertices()
    trimesh.repair.fill_holes(m)
    trimesh.repair.fix_normals(m)
    return _solidify(m, os.path.basename(str(name)))


def thinned_solid(mesh, thin):
    """Thin the serpentine strands without moving the envelope.

    The thinning is done on the 2D profile and intersected back in 3D, so the
    part keeps its width structure -- the nose stays 2.60 mm across to clear
    the barrel slot while the body behind it stays 3.75 mm.  The back wall is
    then restored, because it is the rigid seat that bears on the barrel, not
    part of the flexure, and thinning it would only lose preload.
    """
    if thin <= 0:
        return mesh.copy()
    import flexure_rate as _FR
    import shapely

    profile = _FR.follower_profile(mesh)
    slim = profile.buffer(-thin, join_style=2, mitre_limit=2.0)
    if slim.is_empty or slim.geom_type != "Polygon":
        raise RuntimeError(
            "thinning by %.3f severs the serpentine (%s)"
            % (thin, "empty" if slim.is_empty else slim.geom_type))

    keep = trimesh.creation.extrude_polygon(slim, height=BODY_W + 1.0)
    # extrude_polygon lays the profile in its own (a, b) and raises it along
    # local z.  The profile is (toy y, toy z), so send local (a, b, c) to toy
    # (c, a, b): the extrusion becomes toy x.  det = +1, a proper rotation.
    keep.apply_transform(np.array([[0.0, 0.0, 1.0, NOSE_X0 - 0.5],
                                   [1.0, 0.0, 0.0, 0.0],
                                   [0.0, 1.0, 0.0, 0.0],
                                   [0.0, 0.0, 0.0, 1.0]]))

    out = trimesh.boolean.intersection([mesh, keep], engine=ENGINE)
    lo = SEAT_Z - thin - 0.10
    b = mesh.bounds
    slab = trimesh.creation.box(extents=[b[1][0] - b[0][0] + 2.0,
                                         b[1][1] - b[0][1] + 2.0,
                                         (SEAT_Z + 1.0) - lo])
    slab.apply_translation([(b[0][0] + b[1][0]) / 2.0,
                            (b[0][1] + b[1][1]) / 2.0,
                            (lo + SEAT_Z + 1.0) / 2.0])
    back = trimesh.boolean.intersection([mesh, slab], engine=ENGINE)
    out = trimesh.boolean.union([out, back], engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("thinning by %.3f left %d bodies" % (thin, out.body_count))
    return out


def preloaded_solid(mesh, preload):
    """Extend the nose tip ``preload`` deeper, leaving everything else alone."""
    if preload <= 0:
        return mesh.copy()
    tip = trimesh.creation.cylinder(radius=NOSE_R, height=NOSE_X1 - NOSE_X0,
                                    sections=96)
    # cylinder() stands along z; lay it along toy x, on the tip's own axis
    tip.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi / 2.0, [0.0, 1.0, 0.0]))
    tip.apply_translation([(NOSE_X0 + NOSE_X1) / 2.0, NOSE_Y,
                           NOSE_Z + NOSE_R - preload])
    out = trimesh.boolean.union([mesh, tip], engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("preload %.3f left %d bodies" % (preload, out.body_count))
    return out


def build_followers(preload=PRELOAD, thin=THIN):
    """The three followers, in assembled toy coordinates."""
    base = preloaded_solid(thinned_solid(_load(SOURCE), thin), preload)
    out = []
    for az in AZIMUTHS:
        m = base.copy()
        if az:
            m.apply_transform(trimesh.transformations.rotation_matrix(
                np.radians(az), [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]))
        out.append(m)
    return out


def _stop_lands():
    """The two inward lands, as a solid in toy coordinates."""
    import shapely

    wedges = []
    for az in STOP_AZIMUTHS:
        a0, a1 = np.radians(az - STOP_HALF_DEG), np.radians(az + STOP_HALF_DEG)
        ts = np.linspace(a0, a1, 24)
        inner = np.stack([STOP_R * np.cos(ts), STOP_R * np.sin(ts)], axis=1)
        outer = np.stack([STOP_R_OUT * np.cos(ts[::-1]),
                          STOP_R_OUT * np.sin(ts[::-1])], axis=1)
        wedges.append(shapely.Polygon(np.vstack([inner, outer])))
    solid = trimesh.util.concatenate([
        trimesh.creation.extrude_polygon(w, height=STOP_Y1 - STOP_Y0)
        for w in wedges])
    # the polygon is (toy x, toy z) and extrude_polygon raises it along its own
    # z; a -90 degree turn about x sends that to toy y.  Proper rotation, and
    # negating toy z maps the 90/270 pair onto itself, so the sectors land where
    # they are meant to.
    solid.apply_transform(trimesh.transformations.rotation_matrix(
        -np.pi / 2.0, [1.0, 0.0, 0.0]))
    solid.apply_translation([0.0, STOP_Y0, 0.0])
    return solid


def _barrel_source():
    """Whichever barrel is installed -- stock, or one already carrying lands.

    Unioning the lands onto a barrel that already has them is a no-op, so this
    stays safe to re-run.
    """
    for name in (BARREL, BARREL_OUT):
        if os.path.exists(os.path.join(ASSEMBLED, name)):
            return name
    raise FileNotFoundError("no internal barrel in %s" % ASSEMBLED)


def barrel_with_stop():
    """08 - Internal Barrel with the two up-stop lands added."""
    barrel = _load(_barrel_source())
    out = trimesh.boolean.union([barrel, _stop_lands()], engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("stop lands left %d bodies" % out.body_count)
    return barrel, out


def stop_travel(barrel_stop):
    """Where the retainer actually stops, swept rather than assumed."""
    retainer = _load(RETAINER)
    rods = [_load(n) for n in ("23_Custom_Rod_Middle.stl",
                               "22_Custom_Rod_Right.stl",
                               "24_Custom_Rod_Left.stl")]
    moving = [retainer] + rods
    stop = None
    for dy in np.arange(0.25, 20.01, 0.25):
        M = trimesh.transformations.translation_matrix([0.0, dy, 0.0])
        total = 0.0
        for part in moving:
            c = part.copy()
            c.apply_transform(M)
            try:
                hit = trimesh.boolean.intersection([c, barrel_stop], engine=ENGINE)
                total += abs(hit.volume) if hit is not None and len(hit.faces) else 0.0
            except Exception:
                pass
        if total > 0.05:
            stop = dy
            break
    return stop


def _geometric_seat(tip_radius=NOSE_R):
    """Deepest a round nose of this radius can sit in the rack's 40.63 deg V."""
    half = np.radians(90.0 - FLANK_DEG)
    return RACK_ROOT + tip_radius * (1.0 / np.sin(half) - 1.0)


def predict(preload, res):
    """Geometric upper bound on the seat and crest forces, in newtons."""
    nose = NOSE_Z - preload
    seat_defl = max(_geometric_seat() - nose, 0.0)
    crest_defl = RACK_CREST - nose
    slope = np.tan(np.radians(FLANK_DEG))
    return {
        "nose_z": nose,
        "seat_axial": 3 * res.k * seat_defl * slope,
        "peak_axial": 3 * res.k * crest_defl * slope,
        "strain": res.strain_at(crest_defl),
    }


def measure(followers):
    """The real force curve, swept against the real rack.

    predict() assumes the nose is pushed the full crest height; in practice it
    rides the flank and peaks about 19% lower.  This sweeps the actual meshes,
    so it is the number to trust.
    """
    import score_detent as SD

    _offsets, force = SD.axial_force_curve(followers)
    return {
        "peak_axial": float(force.max()),
        "seat_axial": float(force.min()),
        "dead_fraction": float(np.mean(force <= 1e-6)),
        "curve": force,
    }


def sweep_report(res):
    print("  Geometric upper bound; --dry-run sweeps the real meshes.")
    print("  preload   nose z   hold at seat   peak force   peak strain")
    print("     (mm)     (mm)          (N)          (N)           (%)")
    for p in (0.0, 0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50):
        d = predict(p, res)
        flag = ""
        if d["strain"] > FR.STRAIN_BUDGET:
            flag = "  <- over strain budget"
        elif d["seat_axial"] <= 0.01:
            flag = "  <- still a dead band at the seat"
        print("    %5.2f   %6.3f   %10.2f   %10.2f   %11.2f%s"
              % (p, d["nose_z"], d["seat_axial"], d["peak_axial"],
                 100 * d["strain"], flag))


def validate(followers, preload):
    """Everything that must hold before these are printable."""
    problems = []
    barrel = _load(_barrel_source())
    for name, m in zip(OUTPUTS, followers):
        if not m.is_watertight:
            problems.append("%s is not watertight" % name)
        if m.body_count != 1:
            problems.append("%s has %d bodies" % (name, m.body_count))
        try:
            hit = trimesh.boolean.intersection([m, barrel], engine=ENGINE)
            v = abs(hit.volume) if hit is not None and len(hit.faces) else 0.0
        except Exception as exc:                    # pragma: no cover
            problems.append("%s vs barrel boolean failed: %s" % (name, exc))
            v = 0.0
        if v > 0.05:
            problems.append("%s fouls the barrel by %.3f mm3" % (name, v))

    b = followers[0].bounds
    for label, got, want in (("nose", b[0][2], NOSE_Z - preload),
                             ("barrel seat", b[1][2], SEAT_Z),
                             ("width", b[1][0] - b[0][0], BODY_W)):
        if abs(got - want) > 2e-3:
            problems.append("%s is %.4f, must be %.4f" % (label, got, want))
    return problems


def main():
    ap = argparse.ArgumentParser(description="Build the rod detent followers.")
    ap.add_argument("--dry-run", action="store_true",
                    help="report and validate, write nothing")
    args = ap.parse_args()

    poly = long_arm_profile()
    res = FR.rate(poly, thickness=ARM_W,
                  fixed=lambda V: V[:, 0] < FOOT_Y1 - 0.05,
                  loaded=lambda V: V[:, 1] < ARM_NOSE_R + 0.35,
                  direction=(0.0, 1.0), h=0.08)
    crest = RACK_CREST - ARM_NOSE_R

    print("=" * 78)
    print("ROD DETENT -- long-arm C followers, azimuth 90 and 270")
    print("=" * 78)
    print("  arm  k = %.3f N/mm, %.3f%% strain per mm, %.2f%% per click"
          % (res.k, 100 * res.strain_per_mm, 100 * res.strain_at(crest)))
    print("  ref  11 - Middle Spring: 1.207 N/mm, 0.714%/mm, 0.59% per click")
    if res.strain_at(crest) > FR.STRAIN_BUDGET:
        print("  REFUSING: past the strain budget.")
        return 1

    followers = long_arm_follower()
    stock, barrel = barrel_with_arm_pockets()
    problems = []
    for name, m in zip(OUTPUTS, followers):
        if not m.is_watertight or m.body_count != 1:
            problems.append("%s is not a single watertight solid" % name)
    if not barrel.is_watertight or barrel.body_count != 1:
        problems.append("the pocketed barrel is not a single watertight solid")
    if not np.allclose(stock.bounds, barrel.bounds, atol=1e-6):
        problems.append("the pockets broke through the barrel's outer surface")

    rods = ["23_Custom_Rod_Middle.stl", "22_Custom_Rod_Right.stl",
            "24_Custom_Rod_Left.stl"]
    others = ["09_Custom_Mid_Shell_Spring_33.stl", "11_07_Internal_Barrel_Cap.stl",
              "12_09_Internal_Barrel_Pin_01.stl", "13_10_Internal_Barrel_Pin_02.stl",
              "14_11_Internal_Barrel_Pin_03.stl", RETAINER]
    bite = 0.0
    for n in rods + others:
        o = _load(n)
        for f in followers:
            hit = trimesh.boolean.intersection([f, o], engine=ENGINE)
            v = abs(hit.volume) if hit is not None and len(hit.faces) else 0.0
            if n in rods:
                bite += v
            elif v > 0.05:
                problems.append("a follower fouls %s by %.3f mm3" % (n, v))
        # The barrel already presses into the cap by ~13 mm3 by design, so
        # compare against the stock barrel and flag only what the pockets add.
        def _hit(a, b):
            x = trimesh.boolean.intersection([a, b], engine=ENGINE)
            return abs(x.volume) if x is not None and len(x.faces) else 0.0
        if n not in rods:
            added = _hit(barrel, o) - _hit(stock, o)
            if added > 0.05:
                problems.append("the pockets add %.3f mm3 of interference with %s"
                                % (added, n))
    print("  preload bite into the rack: %.2f mm3 (this is the seating force)" % bite)

    print()
    print("  barrel %.1f -> %.1f mm3 (-%.1f, %.1f%% of it), outer surface intact"
          % (stock.volume, barrel.volume, stock.volume - barrel.volume,
             100 * (stock.volume - barrel.volume) / stock.volume))
    for name, m in zip(OUTPUTS, followers):
        print("    %-42s %7.2f mm3  watertight=%s bodies=%d"
              % (name, m.volume, m.is_watertight, m.body_count))
    if problems:
        print()
        for p in problems:
            print("  FAIL: %s" % p)
        return 1
    print("  all checks passed")

    if args.dry_run:
        print()
        print("  --dry-run: nothing written")
        return 0

    for name, m in zip(OUTPUTS, followers):
        m.export(guard(os.path.join(ASSEMBLED, name)))
    barrel.export(guard(os.path.join(ASSEMBLED, BARREL_OUT)))
    for name in RETIRED:
        path = guard(os.path.join(ASSEMBLED, name))
        if os.path.exists(path) and name not in OUTPUTS and name != BARREL_OUT:
            os.remove(path)
    print()
    print("  written to %s" % ASSEMBLED)
    print("  now run: python tools/export_3d_print_package.py")
    return 0




# ---------------------------------------------------- the long-arm C spring --
# Opening the barrel changes what is possible.  The Spinner Fuse's
# 11 - Middle Spring works because it is a C with two long opposed arms, and
# the Tactical could not host one while its barrel was solid.  Cutting two
# axial pockets at azimuth 90 and 270 -- the middle rod's two rack faces, which
# are opposed, so the pair loads the rod with no net side force -- gives the
# arms somewhere to live.
#
# The barrel can afford it.  Over y 36 .. 47 its wall is a uniform 7.96 mm
# thick with no window, slot or channel anywhere in it; the pockets stop at
# r 12.60 and leave 3.62 mm of wall, still more than the 3.05 mm the barrel
# already carries at its waist.  Nothing is cut through to the outside, so the
# journal the mid shell rides on is untouched.
#
# Why two parts and not one C: a single bridged part cannot be got in.  Below,
# the rod and the spacer leave 0.44 mm at every azimuth; above, the rod's yoke
# and the cap bore leave 0.04 mm.  Two opposed halves keep the mechanics -- long
# arm, opposed pair, continuous preload -- and still drop into their slots.
ARM_AZIMUTHS = (90.0, 270.0)
POCKET_X0, POCKET_X1 = -1.60, 1.55      # matches the existing slot's 3.15 mm
POCKET_R_IN, POCKET_R_OUT = 7.00, 12.60
POCKET_Y0 = 35.50                        # clears the up-stop lands (34.2..35.4)
POCKET_Y1_OPEN = 62.50                   # az 90: no pin channel above
POCKET_Y1_PIN = 56.20                    # az 270: stop below the pin at 56.64

ARM_W = 3.00            # along toy x, the flexure's width -- 11's own 3.0 mm
FOOT_Y0, FOOT_Y1 = 35.60, 37.00
FOOT_R_IN, FOOT_R_OUT = 7.40, 12.40
ARM_Y1 = 53.50
ARM_R_IN, ARM_R_OUT = 7.60, 9.20         # 1.60 mm radial: sets rate and strain
NOSE_TIP_Y = 54.20
ARM_NOSE_R = 5.60       # free-state tip; the rack forces it out to ~6.00,
                        # so it is preloaded 0.40 mm and never loses contact

# Measured on the built pair, swept against the real rack:
#
#   nose r   preload   k N/mm   peak N   seat N   dead   strain/click
#     5.90     0.103    1.005     1.34     0.00     6%      0.82%
#     5.70     0.303    1.005     1.60     0.17     0%      0.99%
#     5.60     0.403    1.005     1.73     0.30     0%      1.07%   <- default
#     5.50     0.503    1.004     1.86     0.43     0%      1.16%
#   ( 11 - Middle Spring )        2.00     0.00     3%      0.59%


def long_arm_profile():
    """The C follower's profile in the toy (y, z) plane, for the az 90 side.

    A foot that keys into the pocket, a long slender arm, and a tongue at the
    free end tipped with the same 0.75 mm radius the rack's 40.63 degree V is
    cut for.  The arm's 1.60 mm radial thickness is what sets both the rate and
    the strain; its length is bounded below by the up-stop lands and above by
    the pin channel at azimuth 270.
    """
    import shapely

    cy, cz = NOSE_TIP_Y, ARM_NOSE_R + NOSE_R
    pts = [(FOOT_Y0, FOOT_R_IN),
           (FOOT_Y0, FOOT_R_OUT),
           (FOOT_Y1, FOOT_R_OUT),
           (FOOT_Y1, ARM_R_OUT),
           (cy + NOSE_R, ARM_R_OUT),
           (cy + NOSE_R, cz)]
    # clockwise round the tip, from the front face to the back face
    for a in np.linspace(0.0, -np.pi, 40)[1:]:
        pts.append((cy + NOSE_R * np.cos(a), cz + NOSE_R * np.sin(a)))
    pts += [(cy - NOSE_R, ARM_R_IN),
            (FOOT_Y1, ARM_R_IN),
            (FOOT_Y1, FOOT_R_IN)]
    poly = shapely.Polygon(pts)
    if not poly.is_valid:
        raise RuntimeError("long-arm profile is self-intersecting")
    return poly


def arm_rate():
    """Radial rate and strain of the C arm, held by its foot.

    The generic serpentine solver in flexure_rate anchors on the part's outer
    face, which is right for a leaf reacting on the barrel behind it and wrong
    for this: the C arm is held by its foot low down and its outer face is free
    to move.  Anchoring the wrong end reads about 35% soft.
    """
    return FR.rate(long_arm_profile(), thickness=ARM_W,
                   fixed=lambda V: V[:, 0] < FOOT_Y1 - 0.05,
                   loaded=lambda V: V[:, 1] < ARM_NOSE_R + 0.35,
                   direction=(0.0, 1.0), h=0.08)


def long_arm_follower():
    """The two opposed C followers, in assembled toy coordinates."""
    poly = long_arm_profile()
    solid = trimesh.creation.extrude_polygon(poly, height=ARM_W)
    # profile is (toy y, toy z); send local (a, b, c) -> toy (c, a, b)
    x0 = 0.5 * (POCKET_X0 + POCKET_X1) - ARM_W / 2.0
    solid.apply_transform(np.array([[0.0, 0.0, 1.0, x0],
                                    [1.0, 0.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 1.0]]))
    out = []
    for az in ARM_AZIMUTHS:
        m = solid.copy()
        if az != 90.0:
            m.apply_transform(trimesh.transformations.rotation_matrix(
                np.radians(az - 90.0), [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]))
        out.append(m)
    return out


def barrel_with_arm_pockets(barrel=None):
    """The barrel with the two axial arm pockets cut."""
    bar = barrel if barrel is not None else _load(_barrel_source())
    cuts = []
    for az, y1 in zip(ARM_AZIMUTHS, (POCKET_Y1_OPEN, POCKET_Y1_PIN)):
        box = trimesh.creation.box(extents=[POCKET_X1 - POCKET_X0,
                                            y1 - POCKET_Y0,
                                            POCKET_R_OUT - POCKET_R_IN])
        box.apply_translation([0.5 * (POCKET_X0 + POCKET_X1),
                               0.5 * (POCKET_Y0 + y1),
                               0.5 * (POCKET_R_IN + POCKET_R_OUT)])
        if az != 90.0:
            box.apply_transform(trimesh.transformations.rotation_matrix(
                np.radians(az - 90.0), [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]))
        cuts.append(box)
    out = trimesh.boolean.difference([bar] + cuts, engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("arm pockets left %d bodies" % out.body_count)
    return bar, out


if __name__ == "__main__":
    raise SystemExit(main())
