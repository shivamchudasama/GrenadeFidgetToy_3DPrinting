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

# Legacy follower slot fill.  The stock slots run y 47 .. 63.24 from the bore out
# to r 14.55, 3.20 mm at the neck and 4.20 mm behind the step.  Filling them is
# what leaves the barrel with four slots and no leftovers -- at azimuth 90 the
# old slot and a new one overlap, and without this the result is a hybrid of the
# two profiles.  The fill runs to the bore, which is not a constant radius, so
# its inner edge is measured rather than assumed.
LEGACY_X0, LEGACY_X1 = -1.75, 2.75
LEGACY_R_OUT = 14.62
LEGACY_Y0 = 43.00                       # the stock slots start at 47; this clears them
                                        # LEGACY_Y1 is the barrel's own top face, read at
                                        # run time: a fill that overshoots it by even
                                        # 0.06 mm moves the part's bounds
BORE_MARGIN = 0.05                      # start just inside the bore, so no hairline is left

# ------------------------------------------------------------------- spring --
# The spring is one arm of the Spinner Fuse `11 - Middle Spring`, cut off where
# the bridge joined it and mapped into the slot.  The reference is a closed C
# 34.81 x 32.63 x 3.00 mm; the arm alone, trimmed of the bridge below y 19.60 and
# of the shell tab beyond x 13.00, is a single 80.7 mm2 polygon -- a long slanted
# leg, a fold out to an outer rail, a U-turn, and a hook back inward to the nose.
REF_SPRING = os.path.join(ROOT_DIR, "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy",
                          "11 - Middle Spring.stl")
REF_ROOT_X = 7.01        # the arm's innermost body material at the cut -> LEAF_R0
REF_OUT_X = 13.00        # the outer rail face -> ARM_R_OUT
REF_Y0 = 19.60           # where the bridge was cut off
REF_TAB_X = 13.00        # the shell tab beyond this is dropped: no room for it

ARM_SCALE_Y = 0.74       # axial; radial follows from LEAF_R0 and ARM_R_OUT (0.534)
ARM_Y0 = 41.90           # where the arm's cut end sits, just inside the foot
ARM_R_OUT = 10.60        # the arm's outer rail, static
ARM_SWING_FACTOR = 1.12  # how far the arm's free end moves per mm of nose travel,
                         # solved from the displacement field: the U-turn at the far
                         # end swings *more* than the nose does, so it, and not the
                         # nose, is what decides how deep the arm may sit
SWING_MARGIN = 0.15      # clear air left between the swung arm and the slot wall

LEAF_R0 = 7.40           # the arm's inner face at the root; clears the crest by 0.51
RAIL_R1 = 12.20          # the foot's bearing face, against the slot's outer wall
RIB_R0 = 11.55           # the extended notch: full width outboard of here
FOOT_Y0 = 36.30                          # the foot: rigid, and the whole anchor
FOOT_OVERLAP = 0.70                      # how far the foot runs past the arm's cut end
FOOT_Y1 = ARM_Y0 + FOOT_OVERLAP
FLANK_TOP = 7.20         # where the tongue's flanks stop, as on the stock nose

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
def bore_profile(barrel, az=45.0, step=0.25):
    """The barrel's bore radius against height, measured at a slot-free azimuth.

    The bore is not one radius: 8.27 up to y 53.5, 7.12 from 54 to 60, then a
    chamfer out to 9.89 at the top.  A fill that assumed a constant radius would
    either leave the old slot open along its inner edge or plug the bore.
    """
    rs = np.arange(SLOT_R_IN, 11.0, 0.01)
    a = np.radians(az)
    ys = np.arange(LEGACY_Y0 - 1.0, barrel.bounds[1][1] + 1.0 + 1e-9, step)
    out = []
    for y in ys:
        pts = np.stack([rs * np.cos(a), np.full_like(rs, y), rs * np.sin(a)], axis=1)
        hit = np.flatnonzero(barrel.contains(pts))
        out.append(rs[hit[0]] if len(hit) else 11.0)
    return ys, np.asarray(out)


def legacy_fill(barrel):
    """The three stock follower slots, as a solid to union back in.

    Without this the barrel keeps six voids, and at azimuth 90 the stock slot and
    a new one overlap into a hybrid of the two profiles -- deeper and wider above
    r 12.30 than the new section, shallower below.
    """
    import shapely

    ys, rb = bore_profile(barrel)
    keep = (ys >= LEGACY_Y0) & (ys <= barrel.bounds[1][1])
    ys, rb = ys[keep], rb[keep] - BORE_MARGIN
    section = shapely.Polygon(list(zip(ys, rb)) +
                              [(ys[-1], LEGACY_R_OUT), (ys[0], LEGACY_R_OUT)])
    if not section.is_valid:
        raise RuntimeError("the legacy fill section is self-intersecting")
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
    """Stock barrel -> pin channels and stock slots filled -> four slots cut.

    Filling before cutting is what matters: at azimuth 90 a new slot lands on top
    of a stock one, and cutting first would leave the deeper stock profile behind
    around it.
    """
    stock = barrel if barrel is not None else _load(STOCK_BARREL)
    filled = trimesh.boolean.union(
        [stock, pin_fill(stock), legacy_fill(stock)], engine=ENGINE)
    if filled.body_count != 1:
        raise RuntimeError("filling left %d bodies" % filled.body_count)
    if not np.allclose(stock.bounds, filled.bounds, atol=1e-6):
        raise RuntimeError("the fill grew the barrel past its own surface")
    out = trimesh.boolean.difference(
        [filled] + [slot_cut(az) for az in SLOT_AZIMUTHS], engine=ENGINE)
    if out.body_count != 1:
        raise RuntimeError("the slots left %d bodies" % out.body_count)
    return stock, filled, out


# ----------------------------------------------------------------- the arm ---
def reference_arm():
    """One arm of `11 - Middle Spring`, as a polygon in its own (radius, axial) plane.

    The bridge that joined the two arms is cut off at y 19.60 and the shell tab
    beyond x 13.00 goes with it -- there is no room for either in a barrel slot,
    and the bridge is exactly the part the arm is "cut from the middle" at.
    """
    import shapely

    m = trimesh.load(REF_SPRING, process=True)
    pl, _ = m.section(plane_origin=[0.0, 0.0, 0.0],
                      plane_normal=[0.0, 0.0, 1.0]).to_2D(to_2D=np.eye(4))
    g = pl.polygons_full[0].intersection(shapely.box(0.0, REF_Y0, REF_TAB_X, 49.0))
    parts = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    return max(parts, key=lambda q: q.area)


def _nose_wedge(nose_y, apex=NOSE_APEX):
    """The tongue that actually sits in the rack, spliced onto the arm's hook.

    The reference tip is blunt and was cut for the Spinner's own rack, so only
    the arm above FLANK_TOP is transplanted and the last millimetre is rebuilt:
    a 0.75 mm tip on flanks at the V's own 49.37 degree half angle, which is the
    form this rod is cut for and the one the stock Tactical follower uses.
    """
    import shapely

    cv = apex + NOSE_R
    half = lambda v: NOSE_R / np.cos(NOSE_HALF) + (v - cv) * np.tan(NOSE_HALF)
    top = FLANK_TOP + 0.9
    pts = [(nose_y + half(top), top), (nose_y + half(FLANK_TOP), FLANK_TOP)]
    for th in np.linspace(np.pi / 2 - NOSE_HALF, -(np.pi / 2 - NOSE_HALF), 48):
        pts.append((nose_y + NOSE_R * np.sin(th), cv - NOSE_R * np.cos(th)))
    pts += [(nose_y - half(FLANK_TOP), FLANK_TOP), (nose_y - half(top), top)]
    return shapely.Polygon(pts)


def arm_profile(apex=NOSE_APEX, s_y=ARM_SCALE_Y, arm_y0=ARM_Y0, arm_r_out=ARM_R_OUT):
    """The spring's shape in the toy (y, radius) plane.

    The reference arm, mapped in, plus a rigid foot at the bottom that is the
    whole anchor: it bears on the slot's outer wall and floor and carries the
    extended notch.  `11` anchors its arm the same way -- on the bridge, at the
    arm's root -- which is why the arm hangs free above it and stays soft.
    """
    import shapely
    from shapely.ops import unary_union

    s_r = (arm_r_out - LEAF_R0) / (REF_OUT_X - REF_ROOT_X)
    to_toy = lambda c: (arm_y0 + (c[1] - REF_Y0) * s_y,
                        LEAF_R0 + (c[0] - REF_ROOT_X) * s_r)
    mapped = shapely.Polygon([to_toy(c) for c in reference_arm().exterior.coords])
    body = mapped.intersection(shapely.box(mapped.bounds[0] - 1.0, FLANK_TOP,
                                           mapped.bounds[2] + 1.0, 99.0))
    if body.geom_type == "MultiPolygon":
        body = max(body.geoms, key=lambda q: q.area)
    nose_y = min(mapped.exterior.coords, key=lambda c: c[1])[0]
    foot_y1 = arm_y0 + FOOT_OVERLAP
    foot = shapely.Polygon([(FOOT_Y0, LEAF_R0), (FOOT_Y0, RAIL_R1),
                            (foot_y1, RAIL_R1), (foot_y1, LEAF_R0)])
    merged = unary_union([body, _nose_wedge(nose_y, apex), foot])
    if merged.geom_type != "Polygon":
        raise RuntimeError("the arm and its foot did not merge: %s" % merged.geom_type)
    poly = shapely.Polygon(merged.exterior)
    if not poly.is_valid:
        raise RuntimeError("the arm profile is self-intersecting")
    return poly


def arm_rate(poly=None):
    """Radial rate and strain of the arm, anchored where the slot holds it.

    Only the foot is fixed.  Anchoring the whole outer edge -- right for a leaf
    that beds along a wall, wrong for this -- reads it three times too stiff,
    because it takes the arm's free outer rail for a support.
    """
    return FR.rate(poly if poly is not None else arm_profile(),
                   thickness=NARROW_W,
                   fixed=lambda V: (V[:, 1] > RAIL_R1 - 0.05) & (V[:, 0] < FOOT_Y1 + 0.05),
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
    if res.strain_at(crest) > FR.STRAIN_BUDGET:
        print("  REFUSING: past the strain budget.")
        return 1

    springs = followers()
    stock, filled, barrel = barrel_with_slots()
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
