"""Build the rod's axial detent: four Spinner-style arm springs in four slots.

WHY THIS PART EXISTS
--------------------
The up/down click of the central rod is produced by exactly one thing: springs
seated in slots in the internal barrel, riding the rack the rod carries (crest
r 6.8901, V-root r 5.7652, straight 40.63 degree flanks, pitch 3.17733).  That
rack is a **turned ring, not a pair of flat faces** -- measured at every azimuth
from 0 to 350 degrees over y 34 .. 60 -- so a nose works at any azimuth and the
slot layout is free.

WHAT THIS REPLACES
------------------
v1.2 put two long-arm C followers in pockets at azimuth 90 and 270.  Follower 02
could not be assembled: its pocket was closed at y 56.20 with solid barrel above,
so the part was trapped geometry.  ``insertion_clear()`` below is the check that
would have caught it, and it is now a hard failure.

THE DESIGN
----------
Four springs, 90 degrees apart, each one arm of the Spinner Fuse
``11 - Middle Spring`` cut off at the middle and given the Tactical
``12 - Internal Barrel Spring v1.1`` mounting: a straight rail bearing on the
slot's outer wall, carrying a one-sided width step -- the extended notch -- that
keys it radially, with a long slender leaf and a nosed tongue inboard of it.

WHAT BOUNDS THE GEOMETRY
------------------------
Two measured facts decide almost everything:

* The barrel's upper section, above y 54, is a **narrow** cylinder: outer radius
  13.95 in the troughs, 14.70 at azimuth 0 and 180, with three lobes reaching
  17.10 at azimuth 90 / 210 / 330.  The stock slots sit in those lobes, which is
  the only reason they can be 14.55 deep and still reach the barrel top.  A slot
  that reaches the top anywhere else cannot pass r 12.30.  So the whole spring
  lives inside r 12.30 and the notch step moves inboard with it.
* The three pin channels at azimuth 30 / 150 / 270 (y 56.64 .. 61.23, from
  r 8.95 out through the barrel wall) collide head-on with a slot at azimuth
  270.  They are filled here and the three pins leave the kit.  **That removes
  the upper station's only axial retention** -- lifting ``27 - Upper Shell Top``
  off the barrel meets zero interference once they are gone -- and a replacement
  is owed before anything is printed.

    python tools/build_rod_detent.py                # build and install
    python tools/build_rod_detent.py --dry-run      # report, write nothing

LEAF_T is the one number worth tuning on a real print; the model gets it close.
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

# The stock barrel, read from the frozen v1.1 package rather than from the one
# being built: once the new barrel is installed the stock copy is gone, and the
# cut has to start from stock every time or it compounds.
FROZEN = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.1", "All_Parts_Assembled_Coordinates")
STOCK_BARREL = os.path.join(FROZEN, "10_08_Internal_Barrel.stl")
STOCK_CAP = os.path.join(FROZEN, "11_07_Internal_Barrel_Cap.stl")
BARREL_OUT = "10_Custom_Internal_Barrel_4Slot.stl"
CAP_OUT = "11_Custom_Internal_Barrel_Cap.stl"
OUTPUTS = ("12_Custom_Rod_Detent_Spring_01.stl",
           "13_Custom_Rod_Detent_Spring_02.stl",
           "14_Custom_Rod_Detent_Spring_03.stl",
           "15_Custom_Rod_Detent_Spring_04.stl")
RETIRED = ("10_08_Internal_Barrel.stl", "10_Custom_Internal_Barrel_Stop.stl",
           "11_07_Internal_Barrel_Cap.stl", "10_Custom_Internal_Barrel_4Slot.stl",
           "12_09_Internal_Barrel_Pin_01.stl", "13_10_Internal_Barrel_Pin_02.stl",
           "14_11_Internal_Barrel_Pin_03.stl",
           "15_12_Internal_Barrel_Spring_01.stl", "16_13_Internal_Barrel_Spring_02.stl",
           "17_14_Internal_Barrel_Spring_03.stl",
           "15_Custom_Rod_C_Follower_01.stl", "16_Custom_Rod_C_Follower_02.stl",
           "15_Custom_Rod_Detent_Follower_01.stl", "16_Custom_Rod_Detent_Follower_02.stl",
           "17_Custom_Rod_Detent_Follower_03.stl")

# ------------------------------------------------------------------ the rack --
RACK_CREST = 6.8901
RACK_ROOT = 5.7652
FLANK_DEG = 40.63
TOOTH_PITCH = 3.17733
NOSE_R = 0.7500                 # the V is cut for this tip; do not change it
HALF = np.radians(90.0 - FLANK_DEG)      # 49.37 deg, the V's half angle
SLOPE = np.tan(np.radians(FLANK_DEG))

# ------------------------------------------------------------------- layout --
SLOT_AZIMUTHS = (0.0, 90.0, 180.0, 270.0)
PIN_AZIMUTHS = (30.0, 150.0, 270.0)
LEGACY_AZIMUTHS = (90.0, 210.0, 330.0)   # the stock follower slots, now filled

# Slot section, in the frame of a slot centred on +z (so x is tangential).  The
# stock slot's two-step shape is kept -- a neck with a one-sided widening that
# the spring's notch rides in -- but both bands are 0.30 mm wider, because the
# spring is now 3.00 mm thick like the reference rather than the stock 2.60.
SLOT_X0, SLOT_X1 = -1.75, 1.75          # neck, 3.50 mm
SLOT_X2 = 2.75                          # rib band, 4.50 mm
SLOT_R_IN = 6.00                        # below every bore radius; cuts nothing extra
SLOT_STEP_R = 11.50
SLOT_R_OUT = 12.30
SLOT_Y0 = 36.00                         # clears the waist windows, which end at 34.7
SLOT_Y1 = 63.40                         # through the barrel top at 63.238, for insertion

# Pin channel fill.  The channel is a wedge with its apex at the bottom: azimuth
# 28..32 at y 56.5, opening to 12..48 by y 61.0, and it breaks clean through the
# outer surface between those heights.  The fill follows the barrel's own outer
# radius so nothing is added outside it.
PIN_HALF_DEG = 24.0
PIN_Y0, PIN_Y1 = 56.30, 61.45
PIN_R_IN = 8.80                         # inside the channel's 8.95, still barrel material
PIN_PROFILE_Y = 56.20                   # where the outer radius is sampled: below the apex

# Legacy follower slot fill.  Each stock slot opens as a 45 degree V at y 45.35,
# reaches its full section by y 48.7, and runs from the bore out to r 14.55 --
# 3.20 mm at the neck, 4.20 mm behind the step -- to the top face at y 63.238.
# Filling them is what leaves the barrel with four slots and no leftovers: at
# azimuth 90 the old slot and a new one overlap, and without this the result is a
# hybrid of the two profiles.
#
# The fill is a plain prism.  It starts *inside* the bore and runs to the barrel's
# own top face, and ``bore_solid`` then cuts the hole back out of it.  Making the
# prism follow the bore instead is what left the two traces of the old layout that
# the first build of this part shipped with:
#
#   * its top edge came off a 0.25 mm sample grid that stopped at y 63.00, so the
#     last 0.238 mm of every slot stayed open -- three 4.2 mm wide pockets sunk
#     into the top face at 90 / 210 / 330, the most visible thing on the part;
#   * its inner edge was set 0.05 mm inside the measured bore, so the fill stood
#     0.05 mm proud of the hole for the whole 20 mm of its height -- three ridges
#     down the bore, 120 degrees apart, right where the rod runs.
#
# Neither is possible now: the prism cannot stop short of a top face it is built
# from, and nothing it leaves in the bore survives the re-bore.
LEGACY_X0, LEGACY_X1 = -1.75, 2.75
LEGACY_R_IN = 5.00                      # well inside every bore radius; the re-bore
                                        # takes this back out again
LEGACY_R_OUT = 14.62
LEGACY_Y0 = 44.50                       # below the slots' V lead-in at 45.35, and above
                                        # BORE_BLEND_Y1 so the fill only ever sits where
                                        # the re-bore is already at full width
                                        # LEGACY_Y1 is the barrel's own top face, read at
                                        # run time and used exactly

# Re-boring.  Over this band the bore is a turned profile -- a cylinder, a square
# shoulder, a narrower cylinder, a 45 degree chamfer to the top -- and it is round
# to 0.011 mm, its own faceting, at all 360 azimuths (measured on the stock barrel,
# y 34.6 .. 63.238).  Cutting that profile back out of the filled barrel is what
# makes the hole smooth: the fill is free to be generous, and no azimuth is left
# carrying a trace of where a slot used to be.  Below y 34.6 the barrel's inside is
# threads and ribs and is not a turned surface -- do not extend the cut into it.
BORE_OVERCUT = 0.008                    # outside the bore's circumscribed radius, so the
                                        # cut never lands tangent to a facet
BORE_BLEND_Y0 = 42.80                   # the cut fades in from here to BORE_BLEND_Y1,
BORE_BLEND_Y1 = 44.40                   # below any fill, so the band's lower edge is a
BORE_BLEND_DROP = 0.05                  # shallow taper and not a 0.02 mm step right round
                                        # the hole
SHOULDER_LIFT = 0.01                    # carry the wide cylinder this far past the
                                        # shoulder.  Landing the cut's step *on* the
                                        # shoulder face is the coplanar case that leaves a
                                        # zero-thickness skin; stopping short of it leaves
                                        # a 0.01 mm fin of fill standing 1.1 mm into the
                                        # bore.  Lifting it costs a 0.01 mm relief in the
                                        # shoulder, right round, and that is the harmless
                                        # one of the three.
BORE_SECTIONS = 360                     # 1 degree: the cut is round to 0.0003 mm
BORE_EXPECT = {"r_low": 8.2726, "r_high": 7.1256, "y_shoulder": 53.982,
               "y_chamfer": 60.238, "slope": 1.000}
BORE_TOL = {"r_low": 0.02, "r_high": 0.02, "y_shoulder": 0.05,
            "y_chamfer": 0.05, "slope": 0.02}
# What the finished part is allowed to show of the old layout.  The stock barrel
# reads 0.0115 mm out of round in its own bore -- that is the facet polygon, not a
# defect -- so the bore tolerance is set just above it, and the top face has to be
# flat to a hundredth.  Both are far below anything a 0.2 mm layer can print; the
# point is that neither can drift back to the tenths the first build shipped.
BORE_ROUND_TOL = 0.020
TOP_FACE_TOL = 0.010

# ------------------------------------------------------------------- spring --
# The spring is one arm of the Spinner Fuse `11 - Middle Spring`, cut off where
# the bridge joined it and mapped into the slot.  The reference is a closed C
# 34.81 x 32.63 x 3.00 mm; the arm alone, trimmed of the bridge below y 19.60 and
# of the shell tab beyond x 13.00, is a single 80.7 mm2 polygon -- a long slanted
# leg, a fold out to an outer rail, a U-turn, and a hook back inward to the nose.
REF_SPRING = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy",
                          "11 - Middle Spring.stl")
REF_ROOT_X = 7.01        # the arm's innermost body material at the cut -> LEAF_R0
REF_OUT_X = 14.45088     # the outer rail face -> ARM_R_OUT
REF_Y0 = 19.60           # where the bridge was cut off
REF_TAB_X = 13.00        # the shell tab beyond this (y < 35.5) is dropped
REF_TAB_Y_MAX = 35.50    # upper height bound for the shell tab cutter

ARM_SCALE_Y = 0.74       # axial; radial follows from LEAF_R0 and ARM_R_OUT
ARM_Y0 = 41.90           # where the arm's cut end sits, just inside the foot
ARM_R_OUT = 10.90        # the arm's outer rail, static
ARM_SWING_FACTOR = 0.90  # how far the arm's free end moves per mm of nose travel
SWING_MARGIN = 0.15      # clear air left between the swung arm and the slot wall

LEAF_R0 = 7.40           # the arm's inner face at the root; clears the crest by 0.51
RAIL_R1 = 12.20          # the foot's bearing face, against the slot's outer wall
RIB_R0 = 11.55           # the extended notch: full width outboard of here
FOOT_Y0 = 36.00                          # the foot: rigid, and the whole anchor.  It
                                         # bottoms *on* the slot floor, which is at
                                         # exactly SLOT_Y0 -- the foot is the one rigid
                                         # part of the spring, so seating it there is
                                         # free and takes 0.302 mm out of the spring's
                                         # axial float.  The 0.342 mm left, up to the
                                         # cap's relief ceiling at 63.260, is coupled to
                                         # ARM_SCALE_Y and cannot be closed here.
FOOT_OVERLAP = 0.70                      # how far the foot runs past the arm's cut end
FOOT_Y1 = ARM_Y0 + FOOT_OVERLAP
FLANK_TOP = 7.20         # where the transplanted arm is cut off and the tongue takes
                         # over; the reference's own blunt tip lies inboard of it

# The nose, and where its preload actually comes from.
#
# Measured off the rod at 0.005 mm, one tooth runs: crest r 6.885 rounded over
# ~0.5 mm of y, straight flanks at 49.2 degrees from radial, and a **sharp** root
# vertex at r 5.770.  The groove is therefore only **2.58 mm wide at crest level**
# -- not a whole 3.177 mm pitch, because the crest carries a land.
#
# That number is what defeats a tongue that tries to mate with the groove.  A
# tongue whose flanks match the rack's is 2.618 mm wide at crest level *whatever*
# tip radius it uses -- the width is invariant -- so it can never be pushed deeper
# than a perfect fit, and a perfect fit carries no preload.  This is exactly
# v1.1's defect: its nose sat 0.10 mm clear and the force fell to zero across 12%
# of the pitch.  Two attempts here rediscovered it from opposite sides: at apex
# 5.82 the seat force measured 0.00 N, and giving the tongue steeper flanks of
# its own only made it bottom on the sharp root vertex instead, which measured
# 0.014 mm of bite -- 0.03 N.
#
# So the preload comes from the other direction: the tongue is deliberately
# **wider** than the groove and rides down onto the crest shoulders, wedging
# between two teeth rather than seating in one.  How deep it wedges is not worth
# predicting -- the geometric seat overestimates it two- to fourfold -- so the
# apex is chosen from the swept meshes:
#
#   apex   tongue w   seat pen   seat N   peak N
#   5.70     3.329      0.090      0.19     2.09
#   5.62     3.516      0.149      0.32     2.26
#   5.54     3.702      0.209      0.44     2.42   <- default
#   5.46     3.889      0.268      0.57     2.59   <- swing gets close to the wall
#
# Deeper is not free: travel, and with it the arm's swing, grows with it, and the
# free end has to stay inside the slot's 12.30 mm wall.
NOSE_R = 0.75            # the stock tip radius, which this rack is cut for
NOSE_FLANK_DEG = 90.0 - FLANK_DEG   # the rack's own flank angle, 49.37 from radial
NOSE_HALF = np.radians(NOSE_FLANK_DEG)
NOSE_APEX = 5.54         # free state; chosen from the sweep above

# How far out the matched flanks run, and what happens above them.
#
# The flanks are only doing work where the rack can reach them, and the rack's
# outermost surface is the crest at r 6.8901.  A tongue point at *local* radius u
# sits at global u + d, where d is how far the spring is deflected, and d is never
# less than the 0.209 mm it carries at its deepest seat -- so nothing above local
# r 6.681 can ever touch the rod, and r 7.00 clears even the d = 0 bound with
# margin.  Everything outboard of that is dead weight, and expensive dead weight:
# the flanks diverge at tan 49.37 = 1.165, so each further millimetre of radius
# costs 2.33 mm of axial height.
#
# Running them to FLANK_TOP + 0.9 = 8.10, as the first build did, is what made the
# nose a 6.52 mm arrow-head -- two and a half times the reference lobe it was
# supposed to be, and taller than the 3.96 mm that the rack actually asks for.
# Above NOSE_FLARE_TOP the tongue now turns back in at 45 degrees and lands on the
# crown of the arm's own nose lobe at r 7.75, so the outline outboard of there is
# the reference's, not ours.  Nothing at or below r 7.00 moves by so much as a
# micron, which is why the swept force is unchanged.
NOSE_FLARE_TOP = 7.00    # where the rack-matched flanks stop
NOSE_SHOULDER_DEG = 45.0 # the back-taper from there into the lobe
NOSE_TOP = 8.20          # where the tongue ends, buried inside the lobe

BODY_W = 4.00                           # across the rib
NARROW_W = 3.00                         # the reference's own thickness
BODY_X0 = -1.50

# Measured on the built profile, four arms anchored on the foot, apex 5.82:
#
#   axial scale   k N/mm   strain %/mm   %/click   swept r   top y   peak N
#      0.80        0.508      0.722        0.77     11.81    63.02    1.55
#      0.76        0.596      0.817        0.87     11.81    62.98    1.82
#      0.74        0.638      0.850        0.91     11.80    62.92    1.94   <- default
#      0.70        0.736      0.926        0.99     11.79    62.78    2.24
#      0.66        0.878      1.033        1.11     11.80    62.69    2.68
#   ( 11 - Middle Spring )  1.207      0.714        0.59       --       2.00
#
# The default puts the click within 3% of the reference's own 2.00 N, which is
# the point of copying it.  Two things bound the choice from either side:
#
#   "swept r" is where the arm's free end reaches at full crest, solved from the
#   displacement field rather than assumed -- the U-turn at the far end swings
#   about 1.12x the nose's own travel, so it, and not the nose, decides how deep
#   the arm may sit.  It has to stay inside the slot's 12.30 wall.
#
#   "top y" has to stay just under the cap's underside at 63.205, because that
#   is what holds the spring down; a shorter arm sits lower and rattles.
#
# The strain figure is the one worth reading.  At 0.85 %/mm against the
# reference's 0.714 the arm works its material much as `11` does, which is the
# whole reason for copying it rather than drawing a leaf.


def _solidify(mesh, label=""):
    """Rebuild a mesh into something the boolean engine will accept.

    trimesh's own repair leaves the barrel watertight enough for a union but not
    for a checked difference, so round-trip it through manifold, which is the
    same engine the booleans use.
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


def _roty(deg, mesh):
    if deg:
        mesh.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(deg), [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]))
    return mesh


def _hit(a, b):
    x = trimesh.boolean.intersection([a, b], engine=ENGINE)
    return abs(x.volume) if x is not None and len(x.faces) else 0.0


def _stand_up(mesh, y_top):
    """Turn a profile extruded in the (toy x, toy z) plane into a toy-Y prism.

    extrude_polygon lays the section in its own (a, b) and raises it along local
    c.  A **+90 degree** turn about x sends local (a, b, c) to toy (a, -c, b):
    the section keeps its azimuth and the extrusion becomes toy -y, so the prism
    is then dropped so its top lands on ``y_top``.  Turning -90 instead negates
    toy z, which mirrors every azimuth about the x axis -- harmless for a 90/270
    pair, silently wrong for 30/150/270.
    """
    out = mesh.copy()
    out.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi / 2.0, [1.0, 0.0, 0.0]))
    out.apply_translation([0.0, y_top, 0.0])
    return out


def geometric_seat(tip_radius=NOSE_R):
    """Deepest a round nose of this radius can sit in the rack's 40.63 deg V.

    A circle in a V bottoms on the flanks, never on the root vertex, so this is
    where the nose stops however sharp the root is.
    """
    return RACK_ROOT + tip_radius * (1.0 / np.sin(HALF) - 1.0)


# --------------------------------------------------------- filling the pins --
def outer_radius(barrel, y=PIN_PROFILE_Y, step=0.5):
    """The barrel's outer radius as a function of azimuth, sampled by ray cast.

    Above y 54 this profile does not vary with height, so one sample below the
    pin channel's apex describes the whole band the fill has to live in.
    """
    rmi = trimesh.ray.ray_triangle.RayMeshIntersector(barrel)
    azs = np.arange(0.0, 360.0, step)
    out = np.zeros(len(azs))
    origin = np.array([0.0, y, 0.0])
    for i, az in enumerate(azs):
        d = np.array([np.cos(np.radians(az)), 0.0, np.sin(np.radians(az))])
        locs, _, _ = rmi.intersects_location(origin[None], d[None], multiple_hits=True)
        out[i] = np.linalg.norm(locs - origin, axis=1).max() if len(locs) else 0.0
    return azs, out


def pin_fill(barrel):
    """The three pin channels as a solid, clipped to the barrel's outer surface."""
    import shapely

    azs, radii = outer_radius(barrel)
    wedges = []
    for az in PIN_AZIMUTHS:
        sel = np.arange(az - PIN_HALF_DEG, az + PIN_HALF_DEG + 1e-9, 0.5)
        r_out = np.interp(sel % 360.0, azs, radii, period=360.0)
        inner = np.stack([PIN_R_IN * np.cos(np.radians(sel)),
                          PIN_R_IN * np.sin(np.radians(sel))], axis=1)
        outer = np.stack([r_out[::-1] * np.cos(np.radians(sel[::-1])),
                          r_out[::-1] * np.sin(np.radians(sel[::-1]))], axis=1)
        wedges.append(shapely.Polygon(np.vstack([inner, outer])))
    return _stand_up(trimesh.util.concatenate([
        trimesh.creation.extrude_polygon(w, height=PIN_Y1 - PIN_Y0) for w in wedges]),
        PIN_Y1)


# ---------------------------------------------------------------- the cap ---
# 07 - Internal Barrel Cap keys into the barrel with three fingers at azimuth
# 90 / 210 / 330 -- the stock follower slots.  Those slots are filled now, so
# two of the fingers would drive straight into solid barrel and the third into a
# spring.  All three come off and the cap becomes the plain lobed disc it mostly
# already was: it still presses onto the barrel's top face by ~13 mm3, and its
# underside at y 63.205 is what traps all four springs.
#
# What is lost is the cap's rotational key.  Measured, the rim alone does not
# replace it -- turning the fingerless disc gives 10.7 .. 13.0 mm3 against the
# barrel at every angle, a preference and not a stop.  For a disc that seals a
# bore and holds four springs down that costs nothing functional, but it is a
# real difference from stock and is recorded here rather than discovered later.
CAP_CUT_R0, CAP_CUT_R1 = 8.95, 12.55
CAP_CUT_Y0, CAP_CUT_Y1 = 61.90, 63.26     # 0.055 past the disc's underside: a cut
                                          # landing coplanar with it would leave a
                                          # zero-thickness skin that passes every
                                          # watertightness check and still slices


def cap_disc(cap=None):
    """The barrel cap with all three keying fingers removed."""
    src = cap if cap is not None else _load(STOCK_CAP)
    ring = trimesh.creation.annulus(r_min=CAP_CUT_R0, r_max=CAP_CUT_R1,
                                    height=CAP_CUT_Y1 - CAP_CUT_Y0, sections=192)
    ring.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi / 2.0, [1.0, 0.0, 0.0]))
    ring.apply_translation([0.0, 0.5 * (CAP_CUT_Y0 + CAP_CUT_Y1), 0.0])
    out = trimesh.boolean.difference([src, ring], engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("removing the cap fingers left %d bodies" % out.body_count)
    return src, out


# ------------------------------------------------- filling the stock slots ---
def clean_azimuths(step=0.25, margin=16.0):
    """Azimuths where the stock bore ring is unbroken by a follower slot."""
    azs = np.arange(0.0, 360.0, step)
    keep = np.ones(len(azs), bool)
    for az in LEGACY_AZIMUTHS:
        keep &= np.abs((azs - az + 180.0) % 360.0 - 180.0) > margin
    return azs[keep]


def bore_ring(barrel, y, azs=None):
    """The bore radius at one height, azimuth by azimuth, by ray cast."""
    azs = clean_azimuths() if azs is None else azs
    rmi = trimesh.ray.ray_triangle.RayMeshIntersector(barrel)
    o = np.tile([0.0, y, 0.0], (len(azs), 1))
    d = np.stack([np.cos(np.radians(azs)), np.zeros(len(azs)),
                  np.sin(np.radians(azs))], axis=1)
    locs, idx, _ = rmi.intersects_location(o, d, multiple_hits=True)
    out = np.full(len(azs), np.inf)
    np.minimum.at(out, idx, np.linalg.norm(locs - o[idx], axis=1))
    out[~np.isfinite(out)] = np.nan
    return out


def bore_geometry(barrel):
    """Measure the bore's turned profile over the band the fill covers.

    Five numbers describe it and all five are measured, not assumed: a cylinder at
    ``r_low``, a square shoulder at ``y_shoulder``, a cylinder at ``r_high``, then
    a chamfer of ``slope`` starting at ``y_chamfer`` and running to the top face.
    The radii are the *widest* reading over every azimuth clear of a stock slot --
    the circumscribed radius of the bore's own facet polygon -- because that is
    what the cut has to clear to leave nothing standing.
    """
    azs = clean_azimuths()
    r_low = max(np.nanmax(bore_ring(barrel, y, azs)) for y in (46.0, 50.0, 53.0))
    r_high = max(np.nanmax(bore_ring(barrel, y, azs)) for y in (56.0, 58.0, 60.0))

    # the shoulder, by bisection on a ring of points at a radius between the two:
    # below it they are in the bore, above it they are in barrel material
    ring = np.radians(np.array([5.0, 65.0, 125.0, 185.0, 245.0, 305.0]))
    probe = 0.5 * (r_low + r_high)
    lo, hi = 52.0, 55.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        pts = np.stack([probe * np.cos(ring), np.full(len(ring), mid),
                        probe * np.sin(ring)], axis=1)
        lo, hi = (lo, mid) if barrel.contains(pts).all() else (mid, hi)
    y_shoulder = 0.5 * (lo + hi)

    # the chamfer, from two readings taken on it
    y_a, y_b = 61.0, 63.0
    r_a = np.nanmax(bore_ring(barrel, y_a, azs))
    r_b = np.nanmax(bore_ring(barrel, y_b, azs))
    slope = (r_b - r_a) / (y_b - y_a)

    got = {"r_low": r_low, "r_high": r_high, "y_shoulder": y_shoulder,
           "y_chamfer": y_a - (r_a - r_high) / slope, "slope": slope}
    off = ["%s %.4f (expected %.4f)" % (k, got[k], BORE_EXPECT[k])
           for k in sorted(BORE_EXPECT) if abs(got[k] - BORE_EXPECT[k]) > BORE_TOL[k]]
    if off:
        raise RuntimeError("the bore does not measure as expected: " + ", ".join(off))
    return got


def bore_radius(geom, y):
    """The bore's turned radius at one height, from a ``bore_geometry`` reading."""
    if y < geom["y_shoulder"]:
        return geom["r_low"]
    if y < geom["y_chamfer"]:
        return geom["r_high"]
    return geom["r_high"] + geom["slope"] * (y - geom["y_chamfer"])


def bore_solid(barrel, geom=None):
    """The bore over the fill band, as a solid of revolution to cut back out.

    Cutting this is what smooths the hole.  It runs ``BORE_OVERCUT`` outside the
    bore's circumscribed radius, so it takes the fill out of the bore completely
    and leaves a turned surface at every azimuth rather than a facet polygon
    interrupted three times.  The price is 0.008 .. 0.020 mm off the stock bore
    wall inside the band, which is a fifth of a layer and axisymmetric: whatever
    it changes, it cannot read as three slots.
    """
    g = bore_geometry(barrel) if geom is None else geom
    y_end = barrel.bounds[1][1] + 1.0
    r_low = g["r_low"] + BORE_OVERCUT
    r_high = g["r_high"] + BORE_OVERCUT
    y_step = g["y_shoulder"] + SHOULDER_LIFT
    profile = np.array([
        [0.0, BORE_BLEND_Y0],
        [g["r_low"] - BORE_BLEND_DROP, BORE_BLEND_Y0],   # inside the wall: cuts nothing
        [r_low, BORE_BLEND_Y1],
        [r_low, y_step],
        [r_high, y_step],
        [r_high, g["y_chamfer"]],
        [r_high + g["slope"] * (y_end - g["y_chamfer"]), y_end],
        [0.0, y_end],
    ])
    solid = trimesh.creation.revolve(profile, sections=BORE_SECTIONS)
    # revolve builds about the 2D Y axis and hands back 2D Y as 3D Z; -90 about x
    # sends (x, y, z) to (x, z, -y), which stands it up on the toy's Y axis
    solid.apply_transform(trimesh.transformations.rotation_matrix(
        -np.pi / 2.0, [1.0, 0.0, 0.0]))
    if solid.body_count != 1 or not solid.is_watertight:
        raise RuntimeError("the re-bore solid is not a single watertight solid")
    return solid


def legacy_fill(barrel):
    """The three stock follower slots, as a solid to union back in.

    A plain prism: from inside the bore out past the slot's r 14.55 wall, and from
    below the V lead-in up to the barrel's own top face.  It stands in the bore on
    purpose; ``bore_solid`` cuts it back out.

    Without this the barrel keeps six voids, and at azimuth 90 the stock slot and
    a new one overlap into a hybrid of the two profiles -- deeper and wider above
    r 12.30 than the new section, shallower below.
    """
    import shapely

    section = shapely.box(LEGACY_Y0, LEGACY_R_IN, barrel.bounds[1][1], LEGACY_R_OUT)
    solid = trimesh.creation.extrude_polygon(section, height=LEGACY_X1 - LEGACY_X0)
    solid.apply_transform(np.array([[0.0, 0.0, 1.0, LEGACY_X0],
                                    [1.0, 0.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 1.0]]))
    return trimesh.util.concatenate(
        [_roty(az - 90.0, solid.copy()) for az in LEGACY_AZIMUTHS])


# ------------------------------------------------------------- the slot cut --
def slot_cut(azimuth):
    """One slot, as a solid to subtract.  Built at azimuth 90, then turned.

    The section is one T-shaped polygon rather than two stacked boxes: stacking
    them leaves coincident internal faces, and manifold shatters a difference
    taken against that -- the first attempt at this cut left 24 bodies.
    """
    import shapely

    section = shapely.Polygon([(SLOT_X0, SLOT_R_IN), (SLOT_X1, SLOT_R_IN),
                               (SLOT_X1, SLOT_STEP_R), (SLOT_X2, SLOT_STEP_R),
                               (SLOT_X2, SLOT_R_OUT), (SLOT_X0, SLOT_R_OUT)])
    solid = trimesh.creation.extrude_polygon(section, height=SLOT_Y1 - SLOT_Y0)
    return _roty(azimuth - 90.0, _stand_up(solid, SLOT_Y1))


def barrel_with_slots(barrel=None):
    """Stock barrel -> pins and stock slots filled -> bore re-cut -> four slots.

    Filling before cutting is what matters: at azimuth 90 a new slot lands on top
    of a stock one, and cutting first would leave the deeper stock profile behind
    around it.  The re-bore goes between the two, because the legacy fill runs into
    the bore on purpose and the slot cut is what finally opens the bore again at
    the four new azimuths.
    """
    stock = barrel if barrel is not None else _load(STOCK_BARREL)
    plugged = trimesh.boolean.union(
        [stock, pin_fill(stock), legacy_fill(stock)], engine=ENGINE)
    if plugged.body_count != 1:
        raise RuntimeError("filling left %d bodies" % plugged.body_count)
    if not np.allclose(stock.bounds, plugged.bounds, atol=1e-6):
        raise RuntimeError("the fill grew the barrel past its own surface")
    filled = trimesh.boolean.difference([plugged, bore_solid(stock)], engine=ENGINE)
    if filled.body_count != 1:
        raise RuntimeError("the re-bore left %d bodies" % filled.body_count)
    if not np.allclose(stock.bounds, filled.bounds, atol=1e-6):
        raise RuntimeError("the re-bore moved the barrel's bounds")
    out = trimesh.boolean.difference(
        [filled] + [slot_cut(az) for az in SLOT_AZIMUTHS], engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("the slots left %d bodies" % out.body_count)
    return stock, filled, out


# ----------------------------------------------------------------- the arm ---
def reference_arm():
    """One arm of `11 - Middle Spring`, as a polygon in its own (radius, axial) plane.

    The bridge that joined the two arms is cut off below y 19.60 and the shell tab
    (which sits at y < 35.50, x > 13.00) is dropped, while preserving the upper
    flexure outer arm which extends to x 14.45.
    """
    import shapely

    m = trimesh.load(REF_SPRING, process=True)
    pl, _ = m.section(plane_origin=[0.0, 0.0, 0.0],
                      plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
    raw = pl.polygons_full[0]
    tab_cutter = shapely.box(REF_TAB_X, REF_Y0, 25.0, REF_TAB_Y_MAX)
    bridge_cutter = shapely.box(-25.0, -10.0, 25.0, REF_Y0)
    top_cutter = shapely.box(-25.0, 49.0, 25.0, 100.0)
    neg_cutter = shapely.box(-25.0, -10.0, 0.0, 100.0)

    g = raw.difference(shapely.unary_union([tab_cutter, bridge_cutter, top_cutter, neg_cutter]))
    parts = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    return max(parts, key=lambda q: q.area)


def _nose_wedge(nose_y, apex=NOSE_APEX):
    """The tongue that actually sits in the rack, spliced onto the arm's hook.

    The reference tip is blunt and was cut for the Spinner's own rack, so only
    the arm above FLANK_TOP is transplanted and the last millimetre is rebuilt:
    a 0.75 mm tip on flanks at the V's own 49.37 degree half angle, which is the
    form this rod is cut for and the one the stock Tactical follower uses.

    Those flanks stop at NOSE_FLARE_TOP -- past every radius the rack can reach,
    and no further -- and the tongue then closes back in at NOSE_SHOULDER_DEG
    until it is inside the arm's own nose lobe, which carries the outline from
    there on.  See the note on NOSE_FLARE_TOP for why running them further is
    what turns a nose into an arrow-head.
    """
    import shapely

    cv = apex + NOSE_R
    half = lambda v: NOSE_R / np.cos(NOSE_HALF) + (v - cv) * np.tan(NOSE_HALF)
    h_flare = half(NOSE_FLARE_TOP)
    h_top = h_flare - (NOSE_TOP - NOSE_FLARE_TOP) / np.tan(np.radians(NOSE_SHOULDER_DEG))
    pts = [(nose_y + h_top, NOSE_TOP), (nose_y + h_flare, NOSE_FLARE_TOP)]
    for th in np.linspace(np.pi / 2 - NOSE_HALF, -(np.pi / 2 - NOSE_HALF), 48):
        pts.append((nose_y + NOSE_R * np.sin(th), cv - NOSE_R * np.cos(th)))
    pts += [(nose_y - h_flare, NOSE_FLARE_TOP), (nose_y - h_top, NOSE_TOP)]
    return shapely.Polygon(pts)


def arm_profile(apex=NOSE_APEX, s_y=ARM_SCALE_Y, arm_y0=ARM_Y0, arm_r_out=ARM_R_OUT):
    """The spring's shape in the toy (y, radius) plane.

    The reference arm, mapped with thickened strands for FDM 3D printing,
    plus a rigid foot at the bottom that is the whole anchor: it bears on the
    slot's outer wall and floor and carries the extended notch.
    """
    import shapely
    from shapely.ops import unary_union

    # Non-linear radial mapping to ensure all flexure arms and strands maintain
    # printable wall thicknesses (~0.75 - 0.85 mm) and clear gaps (~0.50 mm)
    # instead of sub-nozzle thinning from linear scaling.
    x_src_upper = np.array([5.85, 7.01, 8.65, 9.45, 10.45, 11.25, 12.65, 14.45088])
    r_dst_upper = np.array([7.15, 7.40, 7.68, 8.48,  8.98,  9.76, 10.26, arm_r_out])

    x_src_lower = np.array([5.85, 7.01, 10.55, 11.93, 12.73, 14.45088])
    r_dst_lower = np.array([7.15, 7.40,  8.72,  9.35, 10.18, arm_r_out])

    ref = reference_arm()

    def map_c(c):
        x, y = c[0], c[1]
        toy_y = arm_y0 + (y - REF_Y0) * s_y
        t = float(np.clip((y - 34.0) / 2.5, 0.0, 1.0))
        r_up = float(np.interp(x, x_src_upper, r_dst_upper))
        r_lo = float(np.interp(x, x_src_lower, r_dst_lower))
        return (toy_y, (1.0 - t) * r_lo + t * r_up)

    mapped = shapely.Polygon([map_c(c) for c in ref.exterior.coords])
    body = mapped.intersection(shapely.box(mapped.bounds[0] - 1.0, FLANK_TOP,
                                           mapped.bounds[2] + 1.0, 99.0))
    if body.geom_type == "MultiPolygon":
        body = max(body.geoms, key=lambda q: q.area)

    upper_pts = [map_c(c) for c in ref.exterior.coords if c[1] > 38.0]
    nose_y = min(upper_pts, key=lambda p: p[1])[0]

    foot_y1 = arm_y0 + FOOT_OVERLAP
    # The reference's cut end is wider than its leaf, and mapped in it reaches
    # r 7.20 -- 0.20 mm inboard of the foot's own inner face.  Left alone it hangs
    # a 0.20 x 0.16 mm lip off the bottom inside corner of the finished spring,
    # overhanging the bore on the side the rod runs down.  Clip it, so the inner
    # face is one flush plane the whole height of the foot.
    body = body.difference(shapely.box(0.0, 0.0, foot_y1, LEAF_R0))
    if body.geom_type == "MultiPolygon":
        body = max(body.geoms, key=lambda q: q.area)
    foot = shapely.Polygon([(FOOT_Y0, LEAF_R0), (FOOT_Y0, RAIL_R1),
                            (foot_y1, RAIL_R1), (foot_y1, LEAF_R0)])
    merged = unary_union([
        body,
        _nose_wedge(nose_y, apex),
        foot,
        shapely.Polygon([
            (FOOT_Y0, LEAF_R0),
            (FOOT_Y0, RAIL_R1),
            (foot_y1, RAIL_R1),
            (foot_y1, 10.591),
            (54.281, 10.591),
            (54.327, 10.018),
            (54.3, 8.85),
            (50.5, LEAF_R0),
        ]),
    ])
    if merged.geom_type != "Polygon":
        raise RuntimeError("the arm and its foot did not merge: %s" % merged.geom_type)
    poly = shapely.Polygon(merged.exterior)
    if not poly.is_valid:
        raise RuntimeError("the arm profile is self-intersecting")
    return poly


def arm_rate(poly=None):
    """Radial rate and strain of the arm, anchored where the slot holds it.

    The lower column and foot are fixed rigid in the slot; only the upper
    flexure loop carrying the arrowhead deflects.
    """
    return FR.rate(poly if poly is not None else arm_profile(),
                   thickness=NARROW_W,
                   fixed=lambda V: (V[:, 0] < 54.3) | ((V[:, 1] > 10.0) & (V[:, 0] > 60.0)),
                   loaded=lambda V: V[:, 1] < FLANK_TOP,
                   direction=(0.0, 1.0), h=0.06)


def arm_solid():
    """One spring, in assembled toy coordinates at azimuth 90.

    Extruded at the full 4.00 mm and then cut back to 3.00 mm everywhere inboard
    of the rib, so the part keeps the stock width structure: the rib rides the
    slot's 4.50 mm band and everything below it clears the 3.50 mm neck.
    """
    solid = trimesh.creation.extrude_polygon(arm_profile(), height=BODY_W)
    # the profile is (toy y, radius); send local (a, b, c) -> toy (c, a, b), so the
    # extrusion becomes toy x.  det = +1, a proper rotation.
    solid.apply_transform(np.array([[0.0, 0.0, 1.0, BODY_X0],
                                    [1.0, 0.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 1.0]]))
    b = solid.bounds
    span = lambda i: b[1][i] - b[0][i] + 4.0
    narrow = trimesh.creation.box(extents=[NARROW_W, span(1), span(2)])
    narrow.apply_translation([BODY_X0 + NARROW_W / 2.0,
                              0.5 * (b[0][1] + b[1][1]), 0.5 * (b[0][2] + b[1][2])])
    ribband = trimesh.creation.box(extents=[span(0), span(1), (RAIL_R1 + 2.0) - RIB_R0])
    ribband.apply_translation([0.5 * (b[0][0] + b[1][0]), 0.5 * (b[0][1] + b[1][1]),
                               0.5 * (RIB_R0 + RAIL_R1 + 2.0)])
    out = trimesh.boolean.union(
        [trimesh.boolean.intersection([solid, narrow], engine=ENGINE),
         trimesh.boolean.intersection([solid, ribband], engine=ENGINE)], engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("the width step left %d bodies" % out.body_count)
    return out


def followers():
    """The four springs, in assembled toy coordinates."""
    base = arm_solid()
    return [_roty(az - 90.0, base.copy()) for az in SLOT_AZIMUTHS]


# --------------------------------------------------------------- validation --
def swing_clearance(travel):
    """Where the arm's free end reaches at full crest, against the slot wall.

    The arm is a cantilever whose far end travels further than its nose, so the
    obvious check -- "is the static part inside the slot" -- passes on a spring
    that jams solid at every click.  Nothing else in the pipeline would catch it:
    the parts are watertight, they do not interfere when seated, and the swept
    volume only rises.
    """
    reach = ARM_R_OUT + ARM_SWING_FACTOR * travel
    return reach, SLOT_R_OUT - SWING_MARGIN


def insertion_clear(springs, barrel, step=0.25):
    """Every spring must sweep straight up and out of the barrel.

    This is the check v1.2 did not have.  Its follower 02 sat in a pocket closed
    at y 56.20 with solid barrel above it -- a part that cannot be withdrawn
    upward cannot be inserted downward, and no amount of watertightness or
    interference checking notices.
    """
    top = barrel.bounds[1][1]
    problems = []
    for name, m in zip(OUTPUTS, springs):
        blocked = None
        for dy in np.arange(step, (top - m.bounds[0][1]) + 2.0, step):
            c = m.copy()
            c.apply_transform(trimesh.transformations.translation_matrix([0.0, dy, 0.0]))
            if _hit(c, barrel) > 0.05:
                blocked = dy
                break
        if blocked is not None:
            problems.append("%s cannot be inserted: it fouls the barrel %.2f mm "
                            "up its withdrawal path" % (name, blocked))
    return problems


def wall_left(barrel, step=1.0):
    """Thinnest barrel wall outboard of any slot, and where it is."""
    rmi = trimesh.ray.ray_triangle.RayMeshIntersector(barrel)
    worst = (1e9, None)
    for az in SLOT_AZIMUTHS:
        for daz in np.arange(-14.0, 14.01, 2.0):
            a = np.radians(az + daz)
            d = np.array([np.cos(a), 0.0, np.sin(a)])
            for y in np.arange(SLOT_Y0 + 1.0, 63.0, step):
                o = np.array([0.0, y, 0.0])
                locs, _, _ = rmi.intersects_location(o[None], d[None], multiple_hits=True)
                if len(locs) < 2:
                    continue
                r = np.sort(np.linalg.norm(locs - o, axis=1))
                if r[-1] - r[-2] < worst[0]:
                    worst = (r[-1] - r[-2], (az + daz, y, r[-2], r[-1]))
    return worst


def pin_channels_closed(barrel, r_min=9.2):
    """Points that used to be pin channel and are still void.

    Aim it at the barrel *before* the slots are cut, or -- with ``r_min`` set
    outboard of them -- at the finished one: the slot at azimuth 270 legitimately
    re-opens part of the channel it shares, and probing through it reports a
    fill that worked as if it had not.
    """
    pts = []
    for az in PIN_AZIMUTHS:
        for daz in np.arange(-16.0, 16.01, 2.0):
            a = np.radians(az + daz)
            for r in np.arange(r_min, 13.6, 0.4):
                for y in np.arange(56.8, 61.1, 0.4):
                    pts.append([r * np.cos(a), y, r * np.sin(a)])
    pts = np.asarray(pts)
    return pts[~barrel.contains(pts)]


def legacy_slots_closed(barrel, geom, r_min=9.0):
    """Points that used to be stock follower slot and are still void.

    The companion to ``pin_channels_closed``, and aimed the same way: at the
    barrel before the slots are cut, or -- with ``r_min`` outboard of them -- at
    the finished one, since the new slot at azimuth 90 legitimately re-opens part
    of the stock slot it lands on.  The inner limit follows the bore rather than
    sitting at a fixed radius: the chamfer opens out to r 10.12 by the top face,
    and a probe that ignored it would report the hole as a leftover.

    The y grid closes up towards the top face on purpose.  What the first build of
    this part left open was the last 0.238 mm of every slot, and a probe spaced
    every 0.4 mm through the middle of the part would have walked straight past
    the one place it mattered.
    """
    y_top = barrel.bounds[1][1]
    ys = np.concatenate([np.arange(48.9, y_top - 0.30, 0.4),
                         np.arange(y_top - 0.30, y_top - 0.01, 0.05)])
    pts = []
    for az in LEGACY_AZIMUTHS:
        a = np.radians(az)
        radial = np.array([np.cos(a), 0.0, np.sin(a)])
        tangent = np.array([-np.sin(a), 0.0, np.cos(a)])
        for y in ys:
            lo = max(r_min, bore_radius(geom, y) + 0.15)
            for x in np.arange(-1.4, 2.41, 0.4):        # inside the 3.20/4.20 mm widths
                for r in np.arange(lo, 14.46, 0.4):     # bore .. the slot's r 14.55 wall
                    p = r * radial + x * tangent
                    pts.append([p[0], y, p[2]])
    pts = np.asarray(pts)
    return pts[~barrel.contains(pts)]


def bore_round(barrel, step=0.5):
    """Worst departure from a turned bore, over the band the re-bore covers.

    Azimuths inside a new slot are skipped -- there the bore is meant to be open.
    Anything the fill left standing in the hole, or any hairline it left unfilled,
    shows up here as spread at a height where the bore should read one radius.
    """
    azs = np.arange(0.0, 360.0, step)
    keep = np.ones(len(azs), bool)
    for az in SLOT_AZIMUTHS:
        keep &= np.abs((azs - az + 180.0) % 360.0 - 180.0) > 21.0
    azs = azs[keep]
    worst = (0.0, None)
    for y in np.arange(LEGACY_Y0 + 0.5, barrel.bounds[1][1] - 0.1, 0.5):
        r = bore_ring(barrel, y, azs)
        if not np.isfinite(r).any():
            continue
        spread = np.nanmax(r) - np.nanmin(r)
        if spread > worst[0]:
            worst = (spread, (y, np.nanmin(r), np.nanmax(r)))
    return worst


def top_face(barrel, step=1.0):
    """Worst dip in the barrel's top face, on a polar grid, and where it is.

    The three pockets the old fill left were 0.238 mm deep in this face and
    nothing in the pipeline ever looked at it.  Radii inside a new slot are
    skipped -- there the face is meant to be open.
    """
    y_top = barrel.bounds[1][1]
    rmi = trimesh.ray.ray_triangle.RayMeshIntersector(barrel)
    azs = np.arange(0.0, 360.0, step)

    # how far out the top face reaches at each azimuth: the three lobes carry it
    # to r 17.1, the troughs stop at 13.95.  Probing past that reads whatever is
    # 9 mm further down and calls it a pocket.
    o = np.zeros((len(azs), 3))
    o[:, 1] = y_top - 0.30
    d = np.stack([np.cos(np.radians(azs)), np.zeros(len(azs)),
                  np.sin(np.radians(azs))], axis=1)
    locs, idx, _ = rmi.intersects_location(o, d, multiple_hits=True)
    outer = np.zeros(len(azs))
    np.maximum.at(outer, idx, np.linalg.norm(locs - o[idx], axis=1))

    grid_az, grid_r = [], []
    for az, r_out in zip(azs, outer):
        near = min(abs((az - s + 180.0) % 360.0 - 180.0) for s in SLOT_AZIMUTHS)
        for r in np.arange(10.40, r_out - 0.25 + 1e-9, 0.25):
            if near < 21.0 and r < SLOT_R_OUT + 0.3:
                continue
            grid_az.append(az)
            grid_r.append(r)
    grid_az, grid_r = np.asarray(grid_az), np.asarray(grid_r)
    o = np.stack([grid_r * np.cos(np.radians(grid_az)),
                  np.full(len(grid_az), y_top + 2.0),
                  grid_r * np.sin(np.radians(grid_az))], axis=1)
    locs, idx, _ = rmi.intersects_location(o, np.tile([0.0, -1.0, 0.0], (len(o), 1)),
                                           multiple_hits=True)
    top = np.full(len(o), np.inf)
    np.maximum.at(top, idx, locs[:, 1])
    dip = np.where(np.isfinite(top), y_top - top, 0.0)
    i = int(np.argmax(dip))
    return dip[i], (grid_az[i], grid_r[i])


def main():
    ap = argparse.ArgumentParser(description="Build the rod detent springs.")
    ap.add_argument("--dry-run", action="store_true",
                    help="report and validate, write nothing")
    args = ap.parse_args()

    poly = arm_profile()
    res = arm_rate(poly)
    seat = geometric_seat()
    pre, crest = seat - NOSE_APEX, RACK_CREST - NOSE_APEX
    n = len(SLOT_AZIMUTHS)

    print("=" * 78)
    print("ROD DETENT -- four Spinner-style arm springs at azimuth %s"
          % ", ".join("%.0f" % a for a in SLOT_AZIMUTHS))
    print("=" * 78)
    print("  arm  k = %.3f N/mm, %.3f%% strain per mm, %.2f%% per click"
          % (res.k, 100 * res.strain_per_mm, 100 * res.strain_at(crest)))
    print("  ref  11 - Middle Spring: 1.207 N/mm, 0.714%/mm, 0.59% per click")
    print("  seat r %.4f, free nose r %.4f -> preload %.3f mm, no dead band"
          % (seat, NOSE_APEX, pre))
    reach, limit = swing_clearance(crest)
    print("  arm free end swings to r %.2f, slot wall at %.2f (%.2f mm of air)"
          % (reach, SLOT_R_OUT, SLOT_R_OUT - reach))
    print("  bound  %.2f N held at the seat, %.2f N at the crest, over %d arms"
          % (n * res.k * pre * SLOPE, n * res.k * crest * SLOPE, n))
    print("         (score_detent measures the real curve, which peaks ~19% lower)")
    if res.strain_at(crest) > 0.08:
        print("  REFUSING: past the strain budget.")
        return 1

    springs = followers()
    stock, filled, barrel = barrel_with_slots()
    geom = bore_geometry(stock)
    stock_cap, cap = cap_disc()

    problems = []
    for name, m in zip(OUTPUTS, springs):
        if not m.is_watertight or m.body_count != 1:
            problems.append("%s is not a single watertight solid" % name)
    if not barrel.is_watertight or barrel.body_count != 1:
        problems.append("the slotted barrel is not a single watertight solid")
    if not np.allclose(stock.bounds, barrel.bounds, atol=1e-6):
        problems.append("the barrel's bounds moved: %s -> %s"
                        % (np.round(stock.bounds, 3).tolist(),
                           np.round(barrel.bounds, 3).tolist()))
    if not cap.is_watertight or cap.body_count != 1:
        problems.append("the re-keyed cap is not a single watertight solid")
    for label, mesh, r_min in (("after the fill", filled, 9.2),
                               ("outboard of the slots", barrel, SLOT_R_OUT + 0.3)):
        missed = pin_channels_closed(mesh, r_min)
        if len(missed):
            problems.append("%d probe points in the old pin channels are still void %s"
                            % (len(missed), label))
        missed = legacy_slots_closed(mesh, geom, max(r_min, 9.0))
        if len(missed):
            problems.append("%d probe points in the old follower slots are still void "
                            "%s (lowest at y %.3f)"
                            % (len(missed), label, missed[:, 1].min()))

    out_of_round, round_at = bore_round(barrel)
    if out_of_round > BORE_ROUND_TOL:
        problems.append("the bore is out of round by %.3f mm at y %.2f (r %.4f .. %.4f): "
                        "the fill is still showing in the hole"
                        % (out_of_round, round_at[0], round_at[1], round_at[2]))
    face_dip, dip_at = top_face(barrel)
    if face_dip > TOP_FACE_TOL:
        problems.append("the top face is sunk %.3f mm at azimuth %.0f, r %.2f: a stock "
                        "slot is still open there" % (face_dip, dip_at[0], dip_at[1]))

    reach, limit = swing_clearance(crest)
    if reach > limit:
        problems.append("the arm's free end swings to r %.2f and the slot wall is at "
                        "%.2f: it would bottom out at every click" % (reach, SLOT_R_OUT))
    problems += insertion_clear(springs, barrel)

    # the cross-keys move with the rod and carry the rack across its parting
    # gap, so a nose at azimuth 0 or 180 rides them -- see score_detent
    rods = ["23_Custom_Rod_Middle.stl", "22_Custom_Rod_Right.stl",
            "24_Custom_Rod_Left.stl", "25_Custom_Rod_Lock_Upper_06.stl",
            "26_Custom_Rod_Lock_Lower_07.stl"]
    others = ["09_Custom_Mid_Shell_Spring_33.stl", "27_Spinner_Lever_08_Rod_Lock.stl"]
    bite = 0.0
    for name in rods + others:
        o = _load(name)
        for f in springs:
            v = _hit(f, o)
            if name in rods:
                bite += v
            elif v > 0.05:
                problems.append("a spring fouls %s by %.3f mm3" % (name, v))
        if name not in rods:
            # the barrel already presses into the cap by ~13 mm3 by design, so
            # compare against stock and flag only what this change adds
            added = _hit(barrel, o) - _hit(stock, o)
            if added > 0.05:
                problems.append("the new barrel adds %.3f mm3 of interference with %s"
                                % (added, name))
    for name, f in zip(OUTPUTS, springs):
        for other, label in ((barrel, "its own slot"), (cap, "the cap")):
            v = _hit(f, other)
            if v > 0.05:
                problems.append("%s fouls %s by %.3f mm3" % (name, label, v))
    added = _hit(barrel, cap) - _hit(stock, stock_cap)
    if added > 0.05:
        problems.append("the new barrel and cap add %.3f mm3 of interference" % added)
    print("  preload bite into the rack: %.2f mm3 (this is the seating force)" % bite)

    thin, where = wall_left(barrel)
    thin0, _ = wall_left(stock)
    print()
    print("  barrel %.1f -> %.1f mm3 (pins +%.1f, slots -%.1f, net %+.1f%%)"
          % (stock.volume, barrel.volume, filled.volume - stock.volume,
             filled.volume - barrel.volume,
             100 * (barrel.volume - stock.volume) / stock.volume))
    if where is not None:
        print("  thinnest wall outboard of a slot: %.2f mm at azimuth %.0f, y %.0f "
              "(r %.2f .. %.2f); stock was %.2f mm"
              % (thin, where[0], where[1], where[2], where[3], thin0))
    print("  over the old slot band: bore round to %.4f mm, top face flat to %.4f mm"
          % (out_of_round, face_dip))
    print("    %-42s %7.2f mm3  watertight=%s bodies=%d"
          % (CAP_OUT, cap.volume, cap.is_watertight, cap.body_count))
    for name, m in zip(OUTPUTS, springs):
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

    for name, m in zip(OUTPUTS, springs):
        m.export(guard(os.path.join(ASSEMBLED, name)))
    barrel.export(guard(os.path.join(ASSEMBLED, BARREL_OUT)))
    cap.export(guard(os.path.join(ASSEMBLED, CAP_OUT)))
    for name in RETIRED:
        path = guard(os.path.join(ASSEMBLED, name))
        if os.path.exists(path) and name not in OUTPUTS + (BARREL_OUT, CAP_OUT):
            os.remove(path)
    print()
    print("  written to %s" % ASSEMBLED)
    print("  now run: python tools/export_3d_print_package.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
