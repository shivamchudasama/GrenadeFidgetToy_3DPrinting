"""Geometry for the custom build -- the five new parts of CUSTOM_DESIGN.md.

Everything here is CSG on upstream meshes plus extruded shapely profiles. No
part is modelled from scratch; each is an upstream part with material added or
removed, so the upstream fits that were never in question stay untouched.

The head work all happens in **Spinner Fuse coordinates**, where the handle's
wheel axis is at (28.790, 69.040) running along +z. Moving the finished head
into toy coordinates is assembly's job, not this module's.

    import custom
    ring  = custom.ring_spinner_slim()
    left  = custom.handle_half("13 - Handle Left")
    right = custom.handle_half("14 - Handle Right")
"""
from __future__ import annotations

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import fidget

ENGINE = fidget.ENGINE

# --------------------------------------------------------------------------
# the head interface schedule -- CUSTOM_DESIGN.md section 4.2
# --------------------------------------------------------------------------

HEAD_C = np.array([28.790, 69.040])   # wheel axis, spinner coords, along +z

RING_SLIM_R = 11.05     # turn 17 - Ring Spinner's mid bulge down to this
BORE_R      = 11.30     # housing bore under the journal
JOURNAL_R   = 12.525    # what the gear rides on

GEAR_BORE_R = 12.757    # measured, D25.514
GEAR_ROOT_R = 16.810
GEAR_TIP_R  = 18.000
GEAR_HT     = 4.300     # half of the 8.60 thickness

SLOT_HZ     = 4.600     # gear slot half-height
SLOT_R_OUT  = 18.300    # gear slot outer radius

FLANGE_Z0, FLANGE_Z1 = 4.600, 6.100
FLANGE_R    = 15.000    # above the gear bore, below the root circle

# Everything the handle carried within r 18 of the wheel axis is now inside the
# gear's tooth annulus, so all four captive locks move out to one radius.
# (name, degrees about the wheel axis, radius upstream, radius here)
# The last field is where the tie-back shoulder starts. The three stapler pins
# land in open air past the head rim and need a shoulder reaching in to r 12.5;
# 16 - Handle Lock sits over the arm, which already ties it back, and a shoulder
# there would dip into 01 - Upper Shell's dome by 18.5 mm3.
RELOCATE = (
    ("18 - Handle Stapler Lock",  45.00, 14.650, 20.500, 12.500),
    ("19 - Handle Stapler Lock", 105.00, 14.650, 20.500, 12.500),
    ("20 - Handle Stapler Lock", 345.00, 14.650, 20.500, 12.500),
    ("16 - Handle Lock",         222.85, 15.362, 20.500, 18.400),
)
PIN_HALF_DEG = 12.0
LUG_R0, LUG_R1 = 18.400, 22.900

PAWL_TH_ANCHOR = 200.0  # degrees, where the leaf is rooted
PAWL_TH_FREE   = 140.0  # its free end
PAWL_TH_NOSE   = 152.0
PAWL_R_BACK    = 19.600 # outer edge of the leaf
PAWL_R_REST    = 18.400 # inner edge away from the nose
PAWL_R_NOSE    = 17.580 # measured engagement radius, DESIGN of the Tactical pair
PAWL_NOSE_HALF = 6.0    # degrees each side of the nose
PAWL_GAP       = 0.150  # keeps the two half-pawls off the z=0 split

HALVES = {
    "13 - Handle Left":  (-9.500, 0.0),
    "14 - Handle Right": (0.0, 9.500),
}


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------

def _extrude(poly, z0, z1, at=HEAD_C):
    """A shapely polygon in the head's local xy, extruded z0..z1."""
    m = trimesh.creation.extrude_polygon(poly, height=float(z1 - z0))
    m.apply_translation([at[0], at[1], float(z0)])
    return m


def _ring(r_in, r_out, res=96):
    outer = Point(0, 0).buffer(r_out, resolution=res)
    if r_in <= 0:
        return outer
    return outer.difference(Point(0, 0).buffer(r_in, resolution=res))


def _sector(r_in, r_out, th0, th1, steps=48):
    """Annular sector polygon, degrees, ccw from th0 to th1."""
    t = np.radians(np.linspace(th0, th1, steps))
    pts = [(r_out * np.cos(a), r_out * np.sin(a)) for a in t]
    pts += [(r_in * np.cos(a), r_in * np.sin(a)) for a in t[::-1]]
    return Polygon(pts)


def annulus(r_in, r_out, z0, z1, at=HEAD_C):
    return _extrude(_ring(r_in, r_out), z0, z1, at)


def disc(r, z0, z1, at=HEAD_C):
    return _extrude(_ring(0, r), z0, z1, at)


def _cut(m, *tools):
    return trimesh.boolean.difference([m] + list(tools), engine=ENGINE)


def _add(m, *tools):
    return trimesh.boolean.union([m] + list(tools), engine=ENGINE)


def dilate(m, d=0.15):
    """Cheap axis-wise dilation -- enough for a printed clearance pocket."""
    parts = [m]
    for ax in range(3):
        for s in (+d, -d):
            c = m.copy()
            t = np.zeros(3)
            t[ax] = s
            c.apply_translation(t)
            parts.append(c)
    return trimesh.boolean.union(parts, engine=ENGINE)


# --------------------------------------------------------------------------
# N5 -- the ring spinner, slimmed
# --------------------------------------------------------------------------

def ring_spinner_slim():
    """17 - Ring Spinner with its mid-plane bulge turned down to D22.10.

    Only the bulge goes: the part is already inside RING_SLIM_R everywhere past
    |z| ~ 3.05, so the +-9.2 retaining lips, which grip at r 9.71 against the
    ring's D21.24 ends, are never touched.
    """
    m = fidget.load("17 - Ring Spinner", product="spinner")
    z0, z1 = m.bounds[0][2] - 1.0, m.bounds[1][2] + 1.0
    keep = disc(RING_SLIM_R, z0, z1)
    out = trimesh.boolean.intersection([m, keep], engine=ENGINE)
    out.metadata["fidget_source"] = "17 - Ring Spinner.stl"
    return out


# --------------------------------------------------------------------------
# N3 / N4 -- the handle halves
# --------------------------------------------------------------------------

def _pawl_polygon():
    """The detent leaf: a tangential cantilever with a nose at PAWL_R_NOSE.

    Reproduces the engagement the Tactical already uses -- 4 - Spring meets
    5 - Gear v1.1 at r 17.58 against a root of 16.81 and a tip of 18.00, so the
    nose rides the tooth tips with 0.42 mm of engagement, 20 clicks a turn.
    """
    th = np.linspace(PAWL_TH_ANCHOR, PAWL_TH_FREE, 160)
    d = np.abs(th - PAWL_TH_NOSE)
    # inner edge sits back at PAWL_R_REST and dips to the nose over +-PAWL_NOSE_HALF
    r_in = np.where(
        d >= PAWL_NOSE_HALF,
        PAWL_R_REST,
        PAWL_R_NOSE + (PAWL_R_REST - PAWL_R_NOSE) * (d / PAWL_NOSE_HALF),
    )
    t = np.radians(th)
    leaf = Polygon(
        [(PAWL_R_BACK * np.cos(a), PAWL_R_BACK * np.sin(a)) for a in t]
        + [(ri * np.cos(a), ri * np.sin(a)) for ri, a in zip(r_in[::-1], t[::-1])]
    )
    anchor = _sector(PAWL_R_REST, 22.50, PAWL_TH_ANCHOR - 4.0, PAWL_TH_ANCHOR + 12.0)
    return unary_union([leaf.buffer(0), anchor])


def _lug_solids(z_lo, z_hi, sign):
    """Buttressed bosses carrying the relocated stapler-lock pins.

    Each lug is a shoulder spanning r 12.5..22.9 outside the gear slot, plus a
    narrower block beside the gear at r >= LUG_R0, so the pin lands clear of the
    gear tip while still tying back into the head rim.
    """
    out = []
    for _, a, _, _, sh in RELOCATE:
        sec_full = _sector(sh, LUG_R1, a - PIN_HALF_DEG, a + PIN_HALF_DEG)
        # Shoulders only, and only OUTSIDE the gear's own band. Carrying the lug
        # through |z| <= SLOT_HZ put 4 x 24 deg of solid material out at r 22.9,
        # nearly 5 mm proud of a tooth tip at 18.00, which shrouds the wheel and
        # is exactly what makes it unrollable from outside. The pins bridge the
        # gap bare, seated in a blind pocket in each half like a hinge pin.
        if sign > 0:
            out.append(_extrude(sec_full, SLOT_HZ, z_hi - 0.10))
        else:
            out.append(_extrude(sec_full, z_lo + 0.10, -SLOT_HZ))
    return out


def _relocated(name, a, r_old, r_new):
    m = fidget.load(name, product="spinner")
    d = r_new - r_old
    m.apply_translation([d * np.cos(np.radians(a)), d * np.sin(np.radians(a)), 0.0])
    return m


def relocated_pins():
    """The four captive locks, moved out clear of the gear."""
    return [(n, _relocated(n, a, r0, r1)) for n, a, r0, r1, _ in RELOCATE]


def _pin_pockets(sign):
    """Clearance pockets for the relocated locks, on this half only.

    Each pocket is cut from the lock's own mesh rather than a stand-in cylinder:
    18/19/20 are congruent but arrive at three different plate rotations, and
    16 - Handle Lock is a different shape again.
    """
    pockets = []
    for n, a, r0, r1, _ in RELOCATE:
        p = dilate(_relocated(n, a, r0, r1), 0.15)
        box = trimesh.creation.box(extents=[80, 80, 20])
        box.apply_translation([HEAD_C[0], HEAD_C[1], sign * 10.0])
        pockets.append(trimesh.boolean.intersection([p, box], engine=ENGINE))
    return pockets


_GUARD = None


def module_guard():
    """A cut tool keeping the handle out of the parts it has to swing past.

    The lugs and the pawl push material outward from the head, and the head sits
    right above 01 - Upper Shell's dome, so an outer corner can end up inside it.
    Upstream 13/14 clear 01 by 0.217 mm and 04 entirely, so subtracting a
    dilated copy of both removes only material this module added -- it cannot
    eat into the handle as it shipped.
    """
    global _GUARD
    if _GUARD is None:
        parts = [fidget.load(n, product="spinner")
                 for n in ("01 - Upper Shell", "04 - Middle Spinner Shell")]
        _GUARD = dilate(trimesh.boolean.union(parts, engine=ENGINE), 0.20)
    return _GUARD

def handle_half(name, pawl=True):
    """A handle half reworked to carry the gear on the head's outer rim."""
    z_lo, z_hi = HALVES[name]
    sign = 1.0 if z_hi > 0 else -1.0
    m = fidget.load(name, product="spinner")

    fz0, fz1 = (0.0, FLANGE_Z1) if sign > 0 else (-FLANGE_Z1, 0.0)

    # 1. fill the bore back in under the journal, and form the journal itself
    m = _add(m, annulus(BORE_R, JOURNAL_R, fz0, fz1))

    # 2. turn the rim down and open the slot the gear sweeps through
    m = _cut(m, annulus(JOURNAL_R, SLOT_R_OUT, -SLOT_HZ, SLOT_HZ))

    # 3. retaining flanges, split so the gear is captured when the halves close
    gz0, gz1 = (FLANGE_Z0, FLANGE_Z1) if sign > 0 else (-FLANGE_Z1, -FLANGE_Z0)
    m = _add(m, annulus(JOURNAL_R, FLANGE_R, gz0, gz1))

    # 4. plug the vacated pin pockets left behind outside the slot
    plugs = []
    for n, a, r0, _, _ in RELOCATE:
        c = HEAD_C + r0 * np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])
        pz0, pz1 = (SLOT_HZ, 9.40) if sign > 0 else (-9.40, -SLOT_HZ)
        plugs.append(disc(3.80, pz0, pz1, at=c))
    m = _add(m, *plugs)

    # 5. lugs for the relocated pins, then their pockets
    m = _add(m, *_lug_solids(z_lo, z_hi, sign))
    m = _cut(m, *_pin_pockets(sign))

    # 6. the detent leaf, one half-pawl per handle half
    if pawl:
        pz0, pz1 = ((PAWL_GAP, GEAR_HT) if sign > 0 else (-GEAR_HT, -PAWL_GAP))
        m = _add(m, _extrude(_pawl_polygon(), pz0, pz1))

    # 7. keep everything added above out of the module's swept envelope
    m = _cut(m, module_guard())

    m.metadata["fidget_source"] = name + ".stl"
    return m


# --------------------------------------------------------------------------
# the parts that ride on the head
# --------------------------------------------------------------------------

def gear_posed():
    """Spinner Lever 05 - Gear moved from its print plate onto the head axis.

    Its own axis is exactly its bbox centre -- the teeth are concentric there to
    an order-1 amplitude of 0.000 -- and its thickness axis is already z.
    """
    g = fidget.load("Spinner Lever 05 - Gear", product="tactical")
    c = g.bounds.mean(axis=0)
    g.apply_translation([HEAD_C[0] - c[0], HEAD_C[1] - c[1], -c[2]])
    return g


def head_items(spring_pawl=True):
    """[(name, mesh)] for the finished head, in Spinner Fuse coordinates."""
    items = [
        ("Custom Handle Left",  handle_half("13 - Handle Left", spring_pawl)),
        ("Custom Handle Right", handle_half("14 - Handle Right", spring_pawl)),
        ("Custom Ring Spinner", ring_spinner_slim()),
        ("Spinner Lever 05 - Gear", gear_posed()),
    ]
    items += relocated_pins()
    return items


# --------------------------------------------------------------------------
# the Spinner Fuse click module -- all of it already in assembly coordinates
# --------------------------------------------------------------------------

CLICK_MODULE = [
    "01 - Upper Shell",              # the neck: D32.50 journal, 4 windows
    "04 - Middle Spinner Shell",     # the 32-tooth ratchet ring
    "05 - Rod Middle Right",
    "06 - Rod Middle Left",
    "07 - Rod Middle Linear Track",  # the middle spring keys to this
    "08 - Rod Lock",
    "09 - Rod Spring",
    "10 - Bottom Spring",
]

MIDDLE_SPRINGS = ("11 - Middle Spring",
                  "11 - Middle Spring v2",
                  "12 - Optional Middle Spring")

HANDLE_MOUNT = ["15 - Handle Rotating Lock"]   # 16 is relocated, see RELOCATE


def middle_spring(which):
    """A middle spring in assembly coordinates.

    12 - Optional Middle Spring is the one Spinner Fuse file shipped in plate
    coordinates. Its bbox matches 11 - Middle Spring's exactly, but dropping it
    on that bbox as-shipped drives it 51.7 mm3 into 07 / 09 / 01. Turning it
    180 degrees about its own normal first brings that to 0.01 mm3, and puts
    its engaging arm at y ~ 29.4 against 11's y ~ 30 -- the same seat and the
    same engagement height, so the two really are alternates.

    A proper rotation, not a mirror: the mirrored candidates score identically
    only because the plate is symmetric, and mirroring a printed part is how
    DESIGN.md section 7 item 2 says these searches go wrong.
    """
    m = fidget.load(which, product="spinner")
    if which.startswith("12"):
        m.apply_transform(trimesh.transformations.rotation_matrix(
            np.pi, [0, 0, 1]))
        ref = fidget.load("11 - Middle Spring", product="spinner")
        m.apply_translation(ref.bounds[0] - m.bounds[0])
    return m


def click_items(spring="11 - Middle Spring"):
    """[(name, mesh)] for the rotary click module, Spinner Fuse coordinates."""
    items = [(n, fidget.load(n, product="spinner")) for n in CLICK_MODULE]
    items.append((spring, middle_spring(spring)))
    return items


def upper_items(spring="11 - Middle Spring"):
    """The whole thing above the Tactical body: click module plus the head."""
    items = click_items(spring)
    items += [(n, fidget.load(n, product="spinner")) for n in HANDLE_MOUNT]
    items += head_items()
    return items


# --------------------------------------------------------------------------
# placing the module on the Tactical body
# --------------------------------------------------------------------------

MODULE_ROT  = 90.0     # degrees about Y -- see module_transform()
MODULE_LIFT = 73.35    # mm; contact is at 72.85, plus the 0.5 house clearance

BASE_SHELL = "03 - Bottom Clicker Shell"   # the module's own foot


def module_transform():
    """Spinner Fuse coordinates -> Tactical toy coordinates.

    The 90 degree turn about Y aligns the module's rod-middle slot with
    3 - Rod Middle v1.1, whose 7.00 x 16.02 section is the other half of the
    through-rod. Turning the module rather than the rod matters: the rod's
    azimuth is only defined mod 60 degrees against the body's 3-fold barrel
    (DESIGN.md section 2.4), and 90 degrees is not a symmetry of that, so
    rotating the rod would walk it off the clearance well it sits in.

    The lift is measured, not assumed: 03 - Bottom Clicker Shell's D31.4 bore
    drops over the r 15.66 taper at the top of 27 - Upper Shell Top, and
    interference against the whole body reaches 0.000 mm3 at dy 72.85.
    """
    R = trimesh.transformations.rotation_matrix(np.radians(MODULE_ROT), [0, 1, 0])
    Tr = trimesh.transformations.translation_matrix([0.0, MODULE_LIFT, 0.0])
    return Tr @ R


DROP_DEFAULT = ("10 - Bottom Spring",)


def module_items(spring="11 - Middle Spring", drop=DROP_DEFAULT):
    """Everything above the Tactical body, in toy coordinates."""
    M = module_transform()
    items = upper_items(spring)
    items.append((BASE_SHELL, fidget.load(BASE_SHELL, product="spinner")))
    out = []
    for n, m in items:
        if n in drop:
            continue
        c = m.copy()
        c.apply_transform(M)
        out.append((n, c))
    return out


def custom_rod():
    """N2 -- the through-rod, one piece from the Tactical rod lock to the module.

    Lower half is 3 - Rod Middle v1.1 exactly as the pose record places it, so
    the tapered lock tab and the 3.000 mm serrations that drive the body's
    linear click through the 15.84 mm square bore of 20 - Mid Shell Spring are
    untouched. Above the body it grows a prism on the rod's own section, ending
    in a flat platform at the foot of 05 / 06.

    The platform is deliberately not a spigot. A spigot up into the slot between
    05 and 06 would have to share that slot with the middle spring, whose frame
    fills it below 07's foot -- 151 mm3 of interference, and the middle spring is
    the one part of this build that cannot move, because it *is* the click. The
    load path does not need one: pressing the handle drives the stack down onto
    the platform, and the body's own 02 - Bottom Spring pushes it back up, so the
    joint is in compression both ways.
    """
    import assembly as A
    rows = {r["part"]: r for r in A.poses("tactical")["parts"]}
    rod = A.posed(rows["3 - Rod Middle v1.1"])
    (x0, y0, z0), (x1, y1, z1) = rod.bounds

    side = fidget.load("05 - Rod Middle Right", product="spinner")
    side.apply_transform(module_transform())
    y_side = side.bounds[0][1]      # 05/06 seat on the platform

    prism = trimesh.creation.box(extents=[x1 - x0, y_side - (y1 - 1.2), z1 - z0])
    prism.apply_translation([(x0 + x1) / 2, (y1 - 1.2 + y_side) / 2, (z0 + z1) / 2])

    out = trimesh.boolean.union([rod, prism], engine=ENGINE)
    out.metadata["fidget_source"] = "3 - Rod Middle v1.1.stl"
    return out


def full_items(spring="11 - Middle Spring", mid_shell="2pc", drop=DROP_DEFAULT):
    """The whole custom toy: Tactical common body, through-rod, module."""
    import assembly as A
    from build_tactical_body import ORDER, VARIANTS
    sel = VARIANTS["Tactical_Body_MidShell_" + {"2pc": "2pc", "solid": "Solid",
                                               "hex": "Hex"}[mid_shell]]
    items = A.items_from_poses("tactical", groups=["common"], order=ORDER, **sel)
    items.append(("Custom Rod", custom_rod()))
    items.append(("Spinner Lever 08 - Rod Lock",
                  A.posed({r["part"]: r for r in A.poses("tactical")["parts"]}
                          ["Spinner Lever 08 - Rod Lock"])))
    items += module_items(spring, drop=drop)
    return items

# ==========================================================================
# The clicking waist -- the mechanism built INTO the Tactical base
# ==========================================================================
#
# The Tactical base already has this mechanism, and nothing in DESIGN.md or
# CLAUDE.md records it. 08 - Internal Barrel carries three windows at
# 30 / 150 / 270 deg; 20 - Mid Shell Spring pushes three arms out through them
# to r 17.20; the mid shell's bore is a 33-lobe ratchet at r 16.43 .. 17.53.
# Swept, the mid shell against the spring gives 6.43 -> 0.00 -> 6.43 mm3 every
# 10.909 deg, i.e. 360/33. It is the Spinner Fuse's machine, one lobe different
# and 0.13 mm shallower.
#
# So the waist is not a transplant and nothing gets stacked on the body. The
# station exists; this deepens it, and optionally swaps 04 - Middle Spinner
# Shell in as the visible band.

WAIST_DY    = 3.50     # clears 06 - Bottom Shell 03; ratchet band lands at y 30.00
WAIST_REACH = 17.40    # the Spinner Fuse reach, vs the base's own 17.20
SPRING_DY   = 0.25     # the most the spring can rise before it fouls the barrel
NOSE_HALF   = 2.5      # a nose must fit INSIDE a notch, not span it
TRIM_R      = 16.30    # everything else pulled back inside the crest circle
NOSE_R0     = 16.10

# Three noses seat together only if their spacings are whole notch counts.
# On 04's 32 notches (11.25 deg) that is 11 + 10 + 11, and the resulting angles
# land inside the existing barrel windows AND on the existing spring arms -- so
# 04 and the barrel are both left exactly as they ship.
NOSE_ANGLES_32 = (30.00, 153.75, 266.25)
NOSE_ANGLES_33 = (30.00, 150.00, 270.00)   # the base mid shell, evenly spaced


def _yring(r_in, r_out, y0, y1, th0=None, th1=None, res=96):
    """An annulus (or sector) about the TOY axis, extruded along Y.

    Angles are **toy** angles, theta = atan2(z, x) -- the frame every
    measurement in DESIGN.md uses. Extrude-then-rotate maps a polygon angle phi
    to toy angle -phi, so the sector is built negated. Getting this wrong cuts
    on the opposite side, which looks like a boolean that did nothing when it
    lands on a feature that is already there.
    """
    if th0 is None:
        poly = _ring(r_in, r_out, res)
    else:
        poly = _sector(r_in, r_out, -th1, -th0)
    m = trimesh.creation.extrude_polygon(poly, height=float(y1 - y0))
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    m.apply_translation([0.0, float(y0), 0.0])
    return m


def waist_spring(reach=WAIST_REACH, angles=NOSE_ANGLES_32, dy=SPRING_DY):
    """20 - Mid Shell Spring with deeper, narrower noses.

    Two changes, both minimal. The upstream arm tip is ~11 deg wide, a whole
    notch pitch, so it can never drop into a notch -- swept, the overlap bottoms
    out at 9.2 mm3 instead of releasing. Every tip is therefore pulled back
    inside the crest circle and a 5 deg nose put back on each arm. The noses
    then reach 17.40 rather than 17.20, the reach measured on 11 - Middle Spring
    and 12 - Optional Middle Spring, which deepens engagement against a 16.50
    crest from 0.70 mm to 0.90 mm.

    Nothing is rotated or grafted. An earlier attempt moved a leaf 180 deg to
    build a two-fold detent and drove it 93.5 mm3 into the barrel: this base is
    3-fold everywhere -- windows, a 3-lobed bore, 33 mid-shell lobes -- and a
    two-fold detent fights all of it.
    """
    import assembly as A
    rows = {r["part"]: r for r in A.poses("tactical")["parts"]}
    base = A.posed(rows["20 - Mid Shell Spring"])
    y0, y1 = base.bounds[0][1], base.bounds[1][1]

    out = trimesh.boolean.difference(
        [base, _yring(TRIM_R, 25.0, y0 - 1, y1 + 1)], engine=ENGINE)
    noses = [_yring(NOSE_R0, reach, y0 + 0.35, y1 - 0.35, a - NOSE_HALF, a + NOSE_HALF)
             for a in angles]
    out = trimesh.boolean.union([out] + noses, engine=ENGINE)
    out.apply_translation([0.0, dy, 0.0])
    out.metadata["fidget_source"] = "20 - Mid Shell Spring.stl"
    return out


def waist_ring(dy=WAIST_DY):
    """04 - Middle Spinner Shell, unmodified, riding on the Tactical barrel.

    Its bore is r 16.49 and 08 - Internal Barrel's outer is a clean cylinder at
    r 16.21..16.22, so the journal clearance is 0.27 mm against the Spinner
    Fuse's own 0.25. Its OD is r 21.00 against the mid shell's 20.82, so it sits
    flush in the body's silhouette. Not one triangle of it changes.
    """
    m = fidget.load("04 - Middle Spinner Shell", product="spinner")
    m.apply_translation([0.0, dy, 0.0])
    return m


def trimmed_mid_shell(name, dy=WAIST_DY):
    """A mid shell cut back to sit above the ratchet ring."""
    import assembly as A
    rows = {r["part"]: r for r in A.poses("tactical")["parts"]}
    m = A.posed(rows[name])
    top = waist_ring(dy).bounds[1][1] + 0.50
    out = trimesh.boolean.difference(
        [m, _yring(0.0, 30.0, m.bounds[0][1] - 1.0, top)], engine=ENGINE)
    out.metadata["fidget_source"] = name + ".stl"
    return out


MID_SHELLS = ("32 - Mid Shell P02", "33 - Mid Shell P01",
              "Mid Shell Solid Color", "Hex Mid Shell Solid Color")


def waist_items(mid_shell="2pc", ring=True):
    """The Tactical common body with the clicking waist built in.

    ring=True  swaps 04 - Middle Spinner Shell in as the visible twist band and
               trims the mid shell to sit above it.
    ring=False leaves the body looking exactly as it ships and simply deepens
               the detent it already has, against its own 33 lobes.
    """
    import assembly as A
    from build_tactical_body import ORDER, VARIANTS
    sel = VARIANTS["Tactical_Body_MidShell_" + {"2pc": "2pc", "solid": "Solid",
                                                "hex": "Hex"}[mid_shell]]
    base = A.items_from_poses("tactical", groups=["common"], order=ORDER, **sel)
    out = []
    for n, m in base:
        if n == "20 - Mid Shell Spring":
            m = (waist_spring() if ring
                 else waist_spring(angles=NOSE_ANGLES_33, dy=0.0))
        elif ring and n in MID_SHELLS:
            m = trimmed_mid_shell(n)
        out.append((n, m))
    if ring:
        out.append(("04 - Middle Spinner Shell", waist_ring()))
    return out
