"""Geometry for the custom build -- the reworked parts of CUSTOM_DESIGN.md.

Everything here is CSG on upstream meshes plus extruded shapely profiles. No
part is modelled from scratch; each is an upstream part with material added or
removed, so the upstream fits that were never in question stay untouched.

Two coordinate frames, and mixing them is the mistake to watch for:

    head    Spinner Fuse coordinates. The handle's wheel axis is at
            (28.790, 69.040) along +z and the fold hinge is at (0, 58.120),
            also along +z. handle_half(), ring_spinner_slim(), gear_posed(),
            hinge_yoke() and swing() all work here.
    toy     Tactical coordinates, from the pose record. waist_*(),
            custom_rod_parts() and toy_items() work here.

module_transform() is the only bridge -- 90 degrees about Y, then lift.

    import custom
    ring  = custom.ring_spinner_slim()               # head
    left  = custom.handle_half("13 - Handle Left")   # head
    rods  = custom.custom_rod_parts()                # toy, lower R/M/L
    caps  = custom.custom_rod_upper_members()        # toy, split upper R/L
    items = custom.toy_items(ring=True, deg=0.0)     # toy, the lot
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon

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
# gear's tooth annulus, so all four captive locks have to move out past it.
# (name, degrees upstream, radius upstream, degrees here, radius here, shoulder)
# The last field is where the tie-back shoulder starts, and it is only used by
# the finned head. The three stapler pins land in open air past the head rim and
# need a shoulder reaching in to r 12.5; 16 - Handle Lock sits over the arm,
# which already ties it back, and a shoulder there would dip into
# 01 - Upper Shell's dome by 18.5 mm3.
#
# 16 - Handle Lock moves along its own height, not radially out from the wheel.
# Pushed straight out to r 20.5 it landed 3.5 mm BELOW where it sits upstream,
# and that shows: it is the pin you see beside the fold hinge, and the handle
# stops matching 13/14 exactly where the fold happens. Sliding it in along
# y = 58.59 instead keeps that profile and still clears the gear -- the pin is
# D5.29, so its centre has to stand at least 18.00 + 2.65 + 0.30 = 20.95 from
# the wheel axis, which at that height means x <= 10.63.
# [M] 16 - Handle Lock is not a dowel. Its section is a blade: 3.00 mm across
# its narrow axis and 6.00 across the other, with the narrow one lying at 50 deg
# in the part's own frame -- which is why it looked tilted wherever it was
# dropped. Turning it costs nothing, it is a printed pin, and it buys back
# 2.3 mm wherever the narrow axis is the direction that is short of room.
# [M] 16 - Handle Lock is not a dowel. Its section is a blade: 3.00 mm across
# its narrow axis and 6.00 across the other, with the narrow one lying at 50 deg
# in the part's own frame -- which is why it looked tilted wherever it was
# dropped. Turning it costs nothing, it is a printed pin, and it buys back
# 2.3 mm wherever the narrow axis is the direction that is short of room.
LOCK_NARROW_DEG = 50.0

# The head carries no pins at all, so the only locks left are two copies of
# 16 - Handle Lock: one closing the neck, one closing the pod.
#
# [D] Nothing else can be there. A lock pin is D4.31 and has to cross z = 0 to
# hold the halves together, and between r 12.5 and r 18.3 the halves never meet
# -- that band is the gear's. A head pin therefore stands at r 20.5 and anything
# holding it reaches 22.9, which is 4.9 mm proud of a tooth tip at 18.00 and
# buries the wheel. The Tactical does not pin its own head either: 1/2 - Rod
# Right/Left v1.1 are clamped along their whole length by the rod between them,
# and the head is a cantilever off that. This handle is built the same way.
#
# [D] 18/19/20 - Handle Stapler Lock are unused. They are 13.8 mm long in a
# handle 19.0 mm wide, so they only ever sit in a BLIND pocket -- there is no
# way to get one into the pod once the halves are closed, and no way to press it
# home before they are. Their upstream pockets are plugged; see PLUG_AT.
#
# (name, degrees upstream, radius upstream, degrees here, radius here,
#  spin about its own axis)
LOCKS = (
    # Shifted slightly downward in Y (x=12.00, y=56.80) to guarantee >= 1.62 mm
    # wall thickness against the gear slot, hinge cavity, and bottom flank.
    ("16 - Handle Lock",       222.85, 15.362, 216.092, 20.778, -17.5),
    # Through the pod's tail. [M] The spin was swept, not guessed: the pocket is
    # boxed in by the slot's FLAT end face inboard and the pod's ROUND cap
    # outboard, and over all 360 deg the shortest tail is at 44 -- flat edge to
    # the flat end, round edge nested into the cap. 224, its opposite, costs
    # 0.8 mm more.
    ("16 - Handle Lock (pod)", 222.85, 15.362, 274.000, 38.060,  44.0),
)

# The four pockets the upstream handle carries for locks that have moved or are
# no longer used. All four are plugged. (degrees, radius, both about HEAD_C)
PLUG_AT = ((45.00, 14.650), (105.00, 14.650), (345.00, 14.650),
           (222.85, 15.362))


CHEEK_R_IN  = 11.900    # inside the journal wall, clear of the ring at 11.05
CHEEK_R0    = 16.300    # at |z| = SLOT_HZ -- 1.70 mm inside the tooth tip
CHEEK_R1    = 14.200    # at |z| = CHEEK_Z1
CHEEK_Z1    = 9.400

# The gear's detent is Spinner Lever 04 - Spring itself, unmodified, pointing at
# the gear down a pod on the arm -- CUSTOM_DESIGN.md section 4.3. It is a
# separate printed spring; nothing sprung is moulded into the handle.
ARM_SPRING    = "Spinner Lever 04 - Spring"
ARM_SPRING_TH = 274.0   # see _arm_boss(): outboard of the arm, clear of the body
ARM_SPRING_R  = 17.580  # nose apex: the upstream pair's own engagement radius
ARM_SPRING_W  = 11.700  # the part's width across the arm
ARM_SPRING_HZ = 4.350   # half its 8.70 thickness
ARM_BOSS_HALF = 8.000   # half width of the housing -- the arm measures 4.4 .. 6.2
ARM_CLR       = 0.250

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


def _solid_only(m):
    """Drop the zero-volume shells a boolean leaves on a coincident face.

    Clipping a part on a plane its own mating face already lies in gives
    manifold two coplanar faces to reconcile, and it sheds **zero-thickness
    shells** where it cannot -- the failure CUSTOM_DESIGN.md section 4.6
    describes. The split plane here *is* 13 - Handle Left's mating face, so the
    cut that hands its shank to 14 always sheds a few, around the neck at
    r 15.8 .. 21.0 where 13 stops dead on z = 0. They have no volume and no
    thickness, but they are separate bodies, and a half that reports
    body_count 3 is not printable.

    Only volumeless shells go. A genuinely severed part still arrives as two
    real bodies and still fails the check in build_parts().
    """
    parts = [c for c in m.split(only_watertight=False) if abs(c.volume) > 1e-6]
    return parts[0] if len(parts) == 1 else trimesh.util.concatenate(parts)


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

def gear_spring_arm():
    """Variant B -- the upstream part, unmodified, laid down the handle's arm.

    Spinner Lever 04 - Spring is 11.70 x 17.99 x 8.70: a foot, a serpentine and
    a rounded nose that pushes along its own length, the nose apex sitting at
    the middle of the 11.70 edge. So it has to point *at* the gear axis, and it
    needs 17.99 mm of radial room. The only direction with anything like that
    is straight down the arm -- ARM_SPRING_TH is the arm's own centreline seen
    from the gear axis -- and even there the handle only reaches r 27.9, so the
    arm has to be thickened to house it (_arm_boss).

    Placed by its nose: the apex lands at ARM_SPRING_R, the same 17.580 the
    v1.1 pair engages at, and the part is centred on z = 0 so it shares the
    gear's own 8.60 mm band.
    """
    m = fidget.load(ARM_SPRING, product="tactical")
    m.apply_translation(-m.bounds[0])
    m.apply_translation([0.0, 0.0, -(m.bounds[1][2]) / 2.0])

    # local +y is the nose direction; turn it to point back at the gear axis
    m.apply_transform(trimesh.transformations.rotation_matrix(
        np.radians(ARM_SPRING_TH + 90.0), [0, 0, 1]))

    a = np.radians(ARM_SPRING_TH)
    target = HEAD_C + ARM_SPRING_R * np.array([np.cos(a), np.sin(a)])
    apex = m.vertices[np.argmax(m.vertices @ np.array([-np.cos(a), -np.sin(a), 0.0]))]
    m.apply_translation([target[0] - apex[0], target[1] - apex[1], 0.0])
    m.metadata["fidget_source"] = ARM_SPRING + ".stl"
    return m


def _arm_axis():
    a = np.radians(ARM_SPRING_TH)
    rad = np.array([np.cos(a), np.sin(a)])          # gear axis -> down the arm
    return rad, np.array([-rad[1], rad[0]])         # radial, tangential


def _arm_rect(r0, r1, half_w, z0, z1):
    """A box lying along the arm, given as a radius span about the gear axis."""
    rad, tan = _arm_axis()
    A, B = r0 * rad, r1 * rad
    poly = Polygon([tuple(A + half_w * tan), tuple(B + half_w * tan),
                    tuple(B - half_w * tan), tuple(A - half_w * tan)])
    return _extrude(poly, z0, z1)


ARM_BOSS_Z     = 9.500  # the lever's own half width -- measured, see below
ARM_POD_FILLET = 0.800  # round-over onto the flat face
ARM_POD_RINGS  = 72     # sections it is lofted through
ARM_POD_SIDES  = 96     # points round each section
ARM_POD_TAIL   = 16.400 # how far past the nose the pod's line runs

# The region the two halves part on. Wider than the pod, and ended square --
# see _pod_footprint(), which is where the numbers are argued.
SPLIT_HALF     = 12.000 # half width across the pod's line
SPLIT_END      = ARM_SPRING_R + ARM_POD_TAIL + ARM_BOSS_HALF  # 41.98, the pod's far point


def _pod_half_width(z):
    """The pod's half width at height z: flat flanks, filleted onto the face.

    **[M] The pod is exactly as wide as the lever, and that is a printing
    constraint, not a styling one.** 13 - Handle Left's arm measures
    z -9.50 .. +9.50 all the way down, constant over y 24 .. 48. A pod any
    narrower sits in a groove between the lever's two faces, and that groove is
    an undercut: printed outer-face-down -- the orientation the spring slot and
    every pin pocket need, because it is the one that leaves them opening
    upward -- the pod's flank has to grow out over thin air.

    Flush and flat, it does not. The flanks come off the bed vertically and the
    only departure is an ARM_POD_FILLET round-over onto the face itself, which
    is the same edge break the lever already carries.
    """
    a = abs(z)
    flat = ARM_BOSS_Z - ARM_POD_FILLET
    if a <= flat:
        return ARM_BOSS_HALF
    t = min((a - flat) / ARM_POD_FILLET, 1.0)
    return ARM_BOSS_HALF - ARM_POD_FILLET * (1.0 - np.sqrt(max(1.0 - t * t, 0.0)))


def _stadium_ring(r0, r1, w, n=ARM_POD_SIDES):
    """One section of the pod: a stadium of half width w about the arm's line.

    Parametrised by a single angle so every section has the same point count in
    the same order, which is what lets them be lofted rather than stacked. The
    two semicircular ends come from cos >= 0 and cos < 0, and the jump between
    them at +-90 deg is the straight flank.
    """
    rad, tan = _arm_axis()
    A, B = r0 * rad, r1 * rad
    th = 2.0 * np.pi * np.arange(n) / n
    c = np.where((np.cos(th) >= 0)[:, None], B[None, :], A[None, :])
    return c + w * (np.cos(th)[:, None] * rad[None, :]
                    + np.sin(th)[:, None] * tan[None, :])


def _loft(rings, z):
    """Close a stack of equal-length rings into one watertight solid."""
    n = len(rings[0])
    verts = [np.column_stack([r, np.full(n, zz)]) for r, zz in zip(rings, z)]
    verts = np.vstack(verts)
    faces = []
    for k in range(len(rings) - 1):
        lo, hi = k * n, (k + 1) * n
        for i in range(n):
            j = (i + 1) % n
            faces.append([lo + i, hi + i, hi + j])
            faces.append([lo + i, hi + j, lo + j])
    c0 = len(verts)
    verts = np.vstack([verts, [[rings[0][:, 0].mean(), rings[0][:, 1].mean(), z[0]]]])
    for i in range(n):
        faces.append([c0, (i + 1) % n, i])
    c1 = len(verts)
    verts = np.vstack([verts, [[rings[-1][:, 0].mean(), rings[-1][:, 1].mean(), z[-1]]]])
    base = (len(rings) - 1) * n
    for i in range(n):
        faces.append([c1, base + i, base + (i + 1) % n])
    m = trimesh.Trimesh(np.asarray(verts, float), np.asarray(faces, int),
                        process=True)
    m.fix_normals()
    m.apply_translation([HEAD_C[0], HEAD_C[1], 0.0])
    return m


def _arm_pod():
    """The spring's housing: one lofted surface, merging smoothly into the head journal.

    Sections are spaced on sin(u) rather than evenly in z, so they crowd at the
    ends, which is exactly where _pod_half_width() puts its fillet.
    Extended inboard to r0 = 12.00 mm (reaching JOURNAL_R = 12.525 mm) so the solid
    cheeks (|z| >= 4.60 mm) span continuously from the ring bore across the spring pocket.
    """
    r0, r1 = 12.00, ARM_SPRING_R + ARM_POD_TAIL
    u = np.linspace(-np.pi / 2, np.pi / 2, ARM_POD_RINGS)
    z = ARM_BOSS_Z * np.sin(u)
    rings = [_stadium_ring(r0, r1, _pod_half_width(zz)) for zz in z]
    pod = _loft(rings, z)
    # Trim only inside the bore void to keep the inner bore clear
    return trimesh.boolean.difference(
        [pod, disc(JOURNAL_R - 0.2, -20.0, 20.0)], engine=ENGINE)


def _pod_footprint():
    """The region the halves part on: the pod's run, widened to take the arm."""
    return trimesh.boolean.difference(
        [_arm_rect(11.80, SPLIT_END, SPLIT_HALF, -20.0, 20.0),
         disc(JOURNAL_R - 0.2, -21.0, 21.0)],
        engine=ENGINE)


def _zbox(z0, z1):
    b = trimesh.creation.box(extents=[200.0, 200.0, z1 - z0])
    b.apply_translation([HEAD_C[0], HEAD_C[1], (z0 + z1) / 2.0])
    return b


def _arm_boss():
    """The material variant B adds so the arm can hold the spring.

    Measured: the arm is 4.4 .. 6.2 mm thick across its 19 mm width and the
    spring wants 11.70 plus walls, so the lever gets that much fatter -- which
    is the cost of using the part as it ships. The pod itself is lofted, not
    stacked -- see _arm_pod() -- so its flank is one continuous curved surface,
    and it splits on the handle's own parting plane so neither half encloses
    the pocket.

    **Which way it fattens is not free.** Down the arm's own centreline, at
    258.4 deg from the gear axis, the housing reaches inboard to head x 16.8;
    the body's silhouette is r 20.81 and head x is toy radius at z = 0, so that
    buried the spring 70.9 mm3 into 27 - Upper Shell Top and the handle another
    38.1. Leaning the spring out to 274 deg keeps the whole housing outboard of
    the arm's inner face with ~2 mm to spare, and the bulge lands on the face
    of the lever you hold rather than the face that lies against the body.
    """
    return _arm_pod()


def _arm_spring_cuts():
    """The spring's pocket: open radially into the gear slot, blind past it.

    Upstream retention, unchanged -- Spinner Lever 04 - Spring drops into a
    slot in its rod middle and the gear caps it. Here it slides in from the
    gear side and the gear does the same job.
    """
    return [_arm_rect(ARM_SPRING_R - 0.28, ARM_SPRING_R + 18.30,
                      ARM_SPRING_W / 2.0 + ARM_CLR,
                      -ARM_SPRING_HZ - ARM_CLR, ARM_SPRING_HZ + ARM_CLR)]


def _cheek_profile(steps=40):
    """(r, z) points down the cheek's outer face, smooth end to end.

    A smoothstep rather than a chamfer or a stack of rings: the toy has no
    stepped contours anywhere on it, and neither should this.
    """
    z = np.linspace(SLOT_HZ, CHEEK_Z1, steps)
    t = (z - SLOT_HZ) / (CHEEK_Z1 - SLOT_HZ)
    r = CHEEK_R0 - (CHEEK_R0 - CHEEK_R1) * t * t * (3.0 - 2.0 * t)
    return np.column_stack([r, z])


def _round_cheek(sign):
    """One turned cheek: a disc that tapers away from the gear, no pins in it.

    Sits entirely inside the tooth circle -- r 16.30 falling to 14.20 against a
    tip at 18.00 -- so the gear stands proud of the handle round its whole
    circumference and a thumb reaches it from any direction.
    """
    prof = _cheek_profile()
    loop = np.vstack([[[CHEEK_R_IN, SLOT_HZ]], prof,
                      [[CHEEK_R_IN, CHEEK_Z1]], [[CHEEK_R_IN, SLOT_HZ]]])
    m = trimesh.creation.revolve(loop, sections=128)
    if sign < 0:
        m.apply_transform(trimesh.transformations.reflection_matrix(
            [0, 0, 0], [0, 0, 1]))
    m.apply_translation([HEAD_C[0], HEAD_C[1], 0.0])
    return [m]


def _relocated(name, th_old, r_old, th_new, r_new, spin=0.0):
    # "16 - Handle Lock (pod)" is a second copy of the same printed part
    m = fidget.load(name.split(" (")[0], product="spinner")
    if spin:
        c = m.bounds.mean(axis=0)
        m.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(spin), [0, 0, 1], [c[0], c[1], 0.0]))
    a0, a1 = np.radians(th_old), np.radians(th_new)
    d = (r_new * np.array([np.cos(a1), np.sin(a1)])
         - r_old * np.array([np.cos(a0), np.sin(a0)]))
    m.apply_translation([d[0], d[1], 0.0])
    return m


def relocated_pins():
    """The two locks that close the handle, in head coordinates."""
    return [(n, _relocated(n, t0, r0, t1, r1, sp))
            for n, t0, r0, t1, r1, sp in LOCKS]


def _pin_pockets():
    """Clearance pockets for the relocated locks, on this half only.

    Each pocket is cut from the lock's own mesh rather than a stand-in cylinder:
    18/19/20 are congruent but arrive at three different plate rotations, and
    16 - Handle Lock is a different shape again.

    **The pocket is not clipped to this half's side of z = 0, and must not be.**
    Clipping it there gives the cut tool a face exactly coplanar with the
    handle's own mating face, and the boolean leaves a **zero-thickness skin
    across the bore**. It has no volume, so an interference test reads 0.000 and
    a containment probe reads empty -- but it is a real face, a slicer closes
    the hole on it, and the pin cannot be pushed through. It cost two rounds of
    "the hole is not thorough" before a ray cast down the axis found two hits at
    z = 0.0000 and nothing else.

    Cutting the whole pin from both halves is safe: neither half has material on
    the other's side of the parting plane anywhere a pin sits, so the extra cut
    removes nothing -- measured, the half's volume is unchanged to 0.1 mm3.
    """
    return [dilate(_relocated(n, t0, r0, t1, r1, sp), 0.15)
            for n, t0, r0, t1, r1, sp in LOCKS]


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

def clean_bore_void(sign: float) -> trimesh.Trimesh:
    """Revolved clean void of the inner bore to clear any plug intrusion."""
    z_pts = np.linspace(0.0, 9.50, 64)
    r_pts = []
    for z in z_pts:
        if z <= FLANGE_Z1:
            r_pts.append(BORE_R)
        elif z <= 8.50:
            t = (z - FLANGE_Z1) / (8.50 - FLANGE_Z1)
            r_pts.append(BORE_R - (BORE_R - 10.80) * t)
        else:
            r_pts.append(9.70)
    r_pts = np.array(r_pts)
    prof = np.column_stack([r_pts, z_pts])
    loop = np.vstack([
        [[0.0, 0.0]],
        prof,
        [[0.0, 9.50]],
        [[0.0, 0.0]],
    ])
    m = trimesh.creation.revolve(loop, sections=128)
    if sign < 0:
        m.apply_transform(trimesh.transformations.reflection_matrix([0, 0, 0], [0, 0, 1]))
    m.apply_translation([HEAD_C[0], HEAD_C[1], 0.0])
    return m


def handle_half(name):
    """A handle half reworked to carry the gear on the head's outer rim.

    It carries no sprung feature of its own: the gear's detent is a separate
    printed spring in the pod (_arm_pod), and the fold's is 09 - Rod Spring in
    the yoke.
    """
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
    for a, r0 in PLUG_AT:
        c = HEAD_C + r0 * np.array([np.cos(np.radians(a)), np.sin(np.radians(a))])
        pz0, pz1 = (SLOT_HZ, 9.40) if sign > 0 else (-9.40, -SLOT_HZ)
        plugs.append(disc(3.80, pz0, pz1, at=c))
    m = _add(m, *plugs)

    # 5. the turned cheeks the gear runs between
    m = _add(m, *_round_cheek(sign))

    # 5b. cut clean inner bore void to ensure zero plug intrusion into the spinner ring bore
    m = _cut(m, clean_bore_void(sign))

    # 6. house the gear's detent spring -- a pocket, never a sprung feature.
    # Split the pod on the handle's own parting plane, so neither half encloses
    # the spring's pocket and both print open-faced. The arm below y 47.5 is
    # 13 - Handle Left's alone, so inside the split region 13 gives up
    # everything above z = 0 and 14 takes it -- the pod's shell and the arm
    # underneath it together, or 14's share would float. The region is wider
    # than the pod and ended square; _pod_footprint() has the reason.
    pod, prism = _arm_pod(), _pod_footprint()
    if sign < 0:
        m = _cut(m, trimesh.boolean.intersection(
            [prism, _zbox(0.0, 20.0)], engine=ENGINE))
        m = _add(m, trimesh.boolean.intersection(
            [pod, _zbox(-20.0, 0.0)], engine=ENGINE))
    else:
        arm = fidget.load("13 - Handle Left", product="spinner")
        share = _solid_only(trimesh.boolean.intersection(
            [arm, prism, _zbox(0.0, 20.0)], engine=ENGINE))
        m = _add(m, share, trimesh.boolean.intersection(
            [pod, _zbox(0.0, 20.0)], engine=ENGINE))
    m = _cut(m, *_arm_spring_cuts())

    # 7. pockets for the pins, cut last -- the pod is added after the seats
    # are, and it fills the tail pin's pocket straight back in if this runs
    # before it. That reads as a 38.9 mm3 pin-in-handle overlap.
    m = _cut(m, *_pin_pockets())

    # 8. keep everything added above out of the module's swept envelope
    m = _cut(m, module_guard())

    m.metadata["fidget_source"] = name + ".stl"
    return m


# --------------------------------------------------------------------------
# the parts that ride on the head
# --------------------------------------------------------------------------

def gear_clean():
    """Spinner Lever 05 - Gear with inner slot removed, restoring axisymmetric journal bore.

    The upstream Tactical part carried an asymmetrical inner cutout spanning ~114 deg
    to clear legacy fixed handle pins. With those pins eliminated and relocated to the neck
    and pod, the inner bearing bore is restored to a uniform 360 deg cylindrical journal
    (r = 12.765 mm) with matching 45 deg retaining chamfers (r = 13.765 mm at z = +-4.30 mm).
    """
    g = fidget.load("Spinner Lever 05 - Gear", product="tactical")
    c = g.bounds.mean(axis=0)
    g_c = g.copy()
    g_c.apply_translation(-c)

    # 1. Clean bore void tool extending well beyond top and bottom
    z_void = np.array([-8.00, -4.30, -3.30, 3.30, 4.30, 8.00])
    r_void = np.array([13.7652, 13.7652, 12.7652, 12.7652, 13.7652, 13.7652])
    pts_2d = np.column_stack([r_void, z_void])
    loop_void = np.vstack([
        [[0.0, z_void[0]]],
        pts_2d,
        [[0.0, z_void[-1]]],
        [[0.0, z_void[0]]],
    ])
    clean_void = trimesh.creation.revolve(loop_void, sections=128)

    # 2. Filler cylinder bounded safely inside teeth (R=15.0 mm < teeth root at 16.14 mm)
    filler = fidget.cylinder(d=30.0, h=12.0, at=(0, 0, 0))

    # 3. Union gear with filler, cut void, and trim top/bottom planes
    merged = trimesh.boolean.union([g_c, filler], engine=ENGINE)
    hollow = trimesh.boolean.difference([merged, clean_void], engine=ENGINE)

    box_top = trimesh.creation.box(extents=[100.0, 100.0, 10.0])
    box_top.apply_translation([0, 0, 4.300 + 5.0])
    box_bot = trimesh.creation.box(extents=[100.0, 100.0, 10.0])
    box_bot.apply_translation([0, 0, -4.300 - 5.0])

    cg = trimesh.boolean.difference([hollow, box_top, box_bot], engine=ENGINE)
    cg.apply_translation(c)
    cg.metadata["fidget_source"] = "Spinner Lever 05 - Gear.stl"
    return cg


def gear_posed():
    """Spinner Lever 05 - Gear (cleaned bore) moved from its print plate onto the head axis.

    Its own axis is exactly its bbox centre -- the teeth are concentric there to
    an order-1 amplitude of 0.000 -- and its thickness axis is already z.
    """
    g = gear_clean()
    c = g.bounds.mean(axis=0)
    g.apply_translation([HEAD_C[0] - c[0], HEAD_C[1] - c[1], -c[2]])
    return g


# --------------------------------------------------------------------------
# N6 -- the 90 degree hinge, transplanted from the Spinner Fuse rod stack
# --------------------------------------------------------------------------
#
# The third action the handle has to carry is the one it already had upstream:
# fold it 90 degrees up or down and it clicks every 30. Nothing about that
# mechanism is invented here -- all four of its pieces already exist:
#
#   13/14 - Handle Left/Right   a D-bore at (0, 58.12) through each cheek, and
#                               a hub scalloped with 12 notches, r 6.97 crest /
#                               7.75 root, over 180 .. 285 deg of arc
#   15 - Handle Rotating Lock   the pin: a D3.90 shaft flatted 1.00 mm off the
#                               axis, with a D4.98 head over z 6.5 .. 9.5
#   09 - Rod Spring             a serpentine leaf whose nose stands at r 6.47
#                               below the axis and drops into each notch
#   05/06/07 - Rod Middle *     the yoke: the pin bore, and the slot the leaf
#                               stands in
#
# handle_half() never touches any of that -- every cut it makes is around
# HEAD_C, 30.5 mm away -- so the scallops arrive intact. The yoke keeps the
# donor's three printable slabs; only a common trim and transverse key are new.
#
# The scalloped arc is exactly the swing: with the leaf fixed at 270 deg, a
# handle turned 0 .. 90 presents 270 .. 180 deg of its own hub, and 180 .. 285
# is where the notches are. 12 notches at 30 deg pitch, so 90 degrees is three
# clicks.

HINGE_Y = 58.120        # head coords: the pin axis, running along +z
HINGE_PIN = "15 - Handle Rotating Lock"
HINGE_SPRING = "09 - Rod Spring"

YOKE_SRC = ("05 - Rod Middle Right", "06 - Rod Middle Left",
            "07 - Rod Middle Linear Track")
YOKE_HALF = 3.580       # half thickness along the pin -- upstream's own 7.16
YOKE_JOIN = 62.000      # toy y where the yoke meets the rod

# Keep the donor's three-member yoke instead of fusing 05/06/07 into the
# Custom Rod Middle.  The two outer members are only 1.705 mm thick after the
# yoke is narrowed to fit between the handle bosses, so they remain separate
# printable caps; trying to graft either one to a Tactical side plate would
# create an 0.080 mm neck at x=+-3.5, far below one extrusion width.
YOKE_UPPER_RIGHT = "Custom Rod Upper Right"
YOKE_UPPER_LEFT = "Custom Rod Upper Left"
YOKE_UPPER_LOCK = "Custom Rod Upper Lock"

# A compact version of Spinner 08 - Rod Lock crosses all three yoke members in
# the solid floor just above YOKE_JOIN.  It retains the donor's curved wedge
# profile, shortened to the 7.16 mm custom stack and narrowed so it stays in
# the rail beside (not under) 09 - Rod Spring.  Coordinates are in the Spinner
# source frame; module_transform() places the finished key in the toy.
YOKE_LOCK_SOURCE = "08 - Rod Lock"
YOKE_LOCK_CENTRE = np.array([-5.300, 29.300, 0.0])
YOKE_LOCK_SIZE = np.array([2.000, 1.300, 8.000])
YOKE_LOCK_CLEARANCE = 0.150

# Spinner Lever 01/02/03 establish the intended three-member rod architecture.
# Their v1.1 successors retain the same two aligned transverse lock tunnels,
# while matching the live v1.1 body and 7 mm middle-rod generation used here.
# Keep 1/2 below YOKE_JOIN as separate side members and replace only the old
# spinner head above that plane with the chosen folding Handle/Lever yoke.
ROD_PLATE_SRC = ("1 - Rod Right v1.1", "2 - Rod Left v1.1")
ROD_LOCK_SPECS = (
    # source lock, tunnel centre Y, tunnel half-height Z
    ("Spinner Lever 06 - Rod Lock", 53.41978, 1.075),
    ("Spinner Lever 07 - Rod Lock", 28.41978, 1.100),
)
# Source lock X/Y/Z -> toy -Y/+X/+Z.  This proper rotation makes the donor's
# 13.776 mm dimension span all three rod members and its 9.332 mm dimension
# run along the tunnel.  The resulting clearances are 0.10 mm at each tunnel
# end and 0.075 mm above/below both locks.
ROD_LOCK_ROTATION = np.array(
    [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
)
ROD_LOCK_CAPTURE = 3.3878
ROD_LOCK_TUNNEL_HALF_Y = 4.7660
ROD_TOOTH_PITCH = 3.17733


def _yoke_keep(join_offset=0.0):
    """Common trim volume for the three Spinner yoke members."""
    keep = trimesh.creation.box(extents=[80.0, 200.0, 2 * YOKE_HALF])
    keep.apply_translation(
        [0.0, 100.0 + YOKE_JOIN - MODULE_LIFT + float(join_offset), 0.0])
    return keep


def _scaled_yoke_lock(extra=0.0):
    """The adapted Spinner 08 wedge in head coordinates.

    ``extra`` grows every bounding dimension by that amount.  The enlarged
    copy is used only as the CSG tunnel tool; the printable key stays at the
    nominal dimensions in YOKE_LOCK_SIZE.
    """
    lock = fidget.load(YOKE_LOCK_SOURCE, product="spinner")
    source_size = lock.extents.copy()
    lock.apply_translation(-lock.bounds.mean(axis=0))
    target = YOKE_LOCK_SIZE + float(extra)
    scale = np.eye(4)
    scale[0, 0], scale[1, 1], scale[2, 2] = target / source_size
    lock.apply_transform(scale)
    lock.apply_translation(YOKE_LOCK_CENTRE)
    lock.metadata["fidget_source"] = YOKE_LOCK_SOURCE + ".stl (scaled wedge)"
    return lock


@lru_cache(maxsize=1)
def _hinge_yoke_parts_cached():
    """The separately printable 05/06/07 members in head coordinates."""
    tunnel = _scaled_yoke_lock(extra=2.0 * YOKE_LOCK_CLEARANCE)
    parts = []
    for index, name in enumerate(YOKE_SRC):
        source = fidget.load(name, product="spinner")
        # The lower Tactical middle intentionally extends 0.5 mm above the
        # nominal graft plane for a robust union with 07.  Start the separate
        # outer caps above that private overlap so they never penetrate it.
        member = trimesh.boolean.intersection(
            [source, _yoke_keep(0.5 if index < 2 else 0.0)], engine=ENGINE)
        member = trimesh.boolean.difference([member, tunnel], engine=ENGINE)
        member.metadata["fidget_source"] = name + ".stl (trimmed, keyed)"
        parts.append(member)
    return tuple(parts)


def hinge_yoke_parts():
    """Right, left and linear-track yoke members in head coordinates."""
    return [mesh.copy() for mesh in _hinge_yoke_parts_cached()]


def hinge_yoke_lock():
    """Printable adapted Spinner 08 wedge in head coordinates."""
    return _scaled_yoke_lock()


def hinge_yoke():
    """The keyed three-member yoke union, for clearance/sweep validation.

    The printable output is deliberately *not* this union: hinge_yoke_parts()
    exposes the separate right, left and linear-track slabs.  This combined
    solid is retained for fold sweeps and legacy head previews.

    Each member already carries the pin bore and, below it, the slot the leaf
    spring stands in. Two common trims are made:

    **Thickness.** Trimmed to +-3.580 along the pin, which is what the stack
    measures at the hinge anyway; below the hinge it fattens to +-6.66 and
    lower still to +-9.82, and none of that fits either between the handle's
    hub bosses (they start at 4.17) or down the body's bore.

    **Length.** Cut so that YOKE_JOIN lands inside the rod's solid section.
    3 - Rod Middle v1.1 is one polygon from y 58.5 to 63.0 and forks into two
    rails above 63.5, so the graft is made into solid material.

    The leaf is 14.14 mm along the pin against the yoke's 7.16, so its ends
    stand proud and bear on the two hub bosses. That is upstream's arrangement,
    not a consequence of the trim -- upstream it stands 0.41 mm proud of a
    13.32 mm stack, and the bearing surfaces are the same either way.
    """
    out = trimesh.boolean.union(hinge_yoke_parts(), engine=ENGINE)
    out.metadata["fidget_source"] = "05/06/07 - Rod Middle.stl (split/keyed)"
    return out


def swinging_items():
    """The parts that turn with the handle, in head coordinates.

    Everything except the hinge yoke and its leaf: the two halves, the ring,
    the gear, the gear's own detent spring, the two locks that close the
    handle, and the hinge pin -- which is keyed to the handle by its flat and
    turns with it inside the yoke's round bore.
    """
    items = [
        ("Custom Handle Left",  handle_half("13 - Handle Left")),
        ("Custom Handle Right", handle_half("14 - Handle Right")),
        ("Custom Ring Spinner", ring_spinner_slim()),
        ("Spinner Lever 05 - Gear", gear_posed()),
        (ARM_SPRING, gear_spring_arm()),
    ]
    items += relocated_pins()
    items.append((HINGE_PIN, fidget.load(HINGE_PIN, product="spinner")))
    return items


def head_items(hinge=True):
    """[(name, mesh)] for the finished head, in Spinner Fuse coordinates.

    hinge=False drops the yoke and its leaf, leaving only what swings -- which
    is what the toy build wants, because there the yoke is part of the rod.
    """
    items = swinging_items()
    if hinge:
        items = [("Custom Hinge Yoke", hinge_yoke()),
                 (YOKE_UPPER_LOCK, hinge_yoke_lock()),
                 (HINGE_SPRING, fidget.load(HINGE_SPRING, product="spinner"))
                 ] + items
    return items


def swing(items, deg):
    """items turned `deg` about the hinge axis, in head coordinates."""
    R = trimesh.transformations.rotation_matrix(
        np.radians(deg), [0, 0, 1], [0.0, HINGE_Y, 0.0])
    out = []
    for n, m in items:
        c = m.copy()
        c.apply_transform(R)
        out.append((n, c))
    return out


# --------------------------------------------------------------------------
# putting the head on the Tactical base
# --------------------------------------------------------------------------

MODULE_ROT = 90.0       # degrees about Y -- see module_transform()
MODULE_LIFT = 34.000    # head y + this = toy y


def module_transform():
    """Head (Spinner Fuse) coordinates -> Tactical toy coordinates.

    **The turn.** 90 degrees about Y sends the head's +z, the pin axis, to the
    toy's +x. That is the direction the rod is *thin* in -- 7.00 mm against
    16.02 -- so the yoke slides between the handle's hub bosses at |x| 4.17
    with no change of section, and the leaf, 14.14 mm along the pin, ends up
    spanning the direction the rod is wide. Turned the other way the leaf would
    have to fit through 7.00 mm, and nothing works.

    **The lift.** Two measured bounds, 3 mm apart, and the upper one wins:

      >= 31.0   below that the leaf's foot fouls the body's bore. Above the
                barrel cap that bore is a clean cylinder -- the largest that
                fits is r 8.35 over y 62 .. 64 and r 8.19 from there to the
                top -- and the foot's corner sits at r 8.21.
      >  32.04  below that the yoke's own floor, the material that closes the
                bottom of the leaf's slot, rises above YOKE_JOIN, gets cut off
                with the graft, and the leaf drops straight out. Floor
                thickness is exactly MODULE_LIFT - 32.04.

    34.000 leaves 1.96 mm of floor, clears the body top by 4.65 mm, and puts
    the toy at 126.3 mm tall against the stock Tactical spinner 7-in-1's 116.7.
    """
    R = trimesh.transformations.rotation_matrix(np.radians(MODULE_ROT), [0, 1, 0])
    Tr = trimesh.transformations.translation_matrix([0.0, MODULE_LIFT, 0.0])
    return Tr @ R


def rod_side_plates():
    """Return the v1.1 right/left members trimmed below the custom yoke.

    Cutting at YOKE_JOIN removes the Tactical spinner ring and its two tall
    supports. The lower members retain the two native cross-lock pockets copied
    from Spinner Lever 01/02 and meet the middle at x=-3.5 and x=+3.5.
    """
    import assembly as A

    rows = {r["part"]: r for r in A.poses("tactical")["parts"]}
    keep = trimesh.creation.box(extents=[80.0, 200.0, 80.0])
    keep.apply_translation([0.0, YOKE_JOIN - 100.0, 0.0])
    plates = []
    for name in ROD_PLATE_SRC:
        source = A.posed(rows[name], product="tactical")
        plate = trimesh.boolean.intersection([source, keep], engine=ENGINE)
        plate.metadata["fidget_source"] = "%s (lower plate only)" % name
        plates.append(plate)
    return plates


def custom_rod_middle():
    """The printable middle rod with only the donor linear-track member.

    Below YOKE_JOIN this is 3 - Rod Middle v1.1 unchanged, including both
    through-lock tunnels. Above it, the old two rails are replaced by donor
    07 - Rod Middle Linear Track. Donor 05/06 are separate upper caps and are
    retained by the adapted 08 wedge plus the existing hinge pin.

    The bottom lock tab, cross-lock tunnels and yoke positions are unchanged.
    """
    import assembly as A
    rows = {r["part"]: r for r in A.poses("tactical")["parts"]}
    rod = A.posed(rows["3 - Rod Middle v1.1"], product="tactical")

    lop = trimesh.creation.box(extents=[80.0, 200.0, 80.0])
    lop.apply_translation([0.0, 100.0 + YOKE_JOIN + 0.5, 0.0])
    rod = trimesh.boolean.difference([rod, lop], engine=ENGINE)

    track = hinge_yoke_parts()[2]
    track.apply_transform(module_transform())
    out = trimesh.boolean.union([rod, track], engine=ENGINE)
    out.metadata["fidget_source"] = (
        "3 - Rod Middle v1.1 + 07 - Rod Middle Linear Track")
    return out


def custom_rod_upper_parts():
    """The two separately printable outer yoke caps in toy coordinates."""
    source_parts = hinge_yoke_parts()
    transform = module_transform()
    out = []
    for name, member in zip(
            (YOKE_UPPER_RIGHT, YOKE_UPPER_LEFT), source_parts[:2]):
        member.apply_transform(transform)
        out.append((name, member))
    return out


def custom_rod_upper_lock():
    """The adapted Spinner 08 key in assembled toy coordinates."""
    lock = hinge_yoke_lock()
    lock.apply_transform(module_transform())
    lock.metadata["fidget_source"] = YOKE_LOCK_SOURCE + ".stl (custom upper key)"
    return lock


def _placed_rod_lock(source_name, station_y):
    """Seat an unmodified Spinner Lever 06/07 key in its native tunnel."""
    lock = fidget.load(source_name, product="tactical")
    lock.apply_translation(-lock.bounds.mean(axis=0))
    transform = np.eye(4)
    transform[:3, :3] = ROD_LOCK_ROTATION
    transform[:3, 3] = [0.0, station_y, 0.0]
    lock.apply_transform(transform)
    lock.metadata["fidget_source"] = "%s (native transverse seat)" % source_name
    return lock


@lru_cache(maxsize=1)
def _custom_rod_module_cached():
    """Build lower rod members, split upper caps, and all transverse keys."""
    right, left = rod_side_plates()
    middle = custom_rod_middle()
    members = [("Custom Rod Right", right),
               ("Custom Rod Middle", middle),
               ("Custom Rod Left", left)]
    upper = custom_rod_upper_parts()
    locks = [(name, _placed_rod_lock(name, station_y))
             for name, station_y, _ in ROD_LOCK_SPECS]
    locks.append((YOKE_UPPER_LOCK, custom_rod_upper_lock()))
    return tuple(members), tuple(upper), tuple(locks)


def custom_rod_parts():
    """The three lower rod members in assembled coordinates.

    Spinner Lever 06/07 pass transversely through both native tunnels and seat
    in both outer members, matching the Spinner Lever 01/02/03 architecture.
    Spinner Lever 08 remains the separate bottom axial retainer. The middle
    carries only the upper linear-track slab; custom_rod_upper_members()
    supplies the two removable upper caps.
    """
    members, _, _ = _custom_rod_module_cached()
    return [(name, mesh.copy()) for name, mesh in members]


def custom_rod_upper_members():
    """The donor 05/06 outer yoke members in assembled toy coordinates."""
    _, upper, _ = _custom_rod_module_cached()
    return [(name, mesh.copy()) for name, mesh in upper]


def custom_rod_locks():
    """The two lower native keys plus the custom upper wedge."""
    _, _, locks = _custom_rod_module_cached()
    return [(name, mesh.copy()) for name, mesh in locks]


def toy_items(mid_shell="2pc", ring=True, deg=0.0):
    """The whole custom toy: clicking waist, rod with the yoke, folding head.

    deg folds the handle -- 0 is stowed alongside the body, 90 is up.
    """
    import assembly as A
    rows = {r["part"]: r for r in A.poses("tactical")["parts"]}
    items = waist_items(mid_shell=mid_shell, ring=ring)
    items.extend(custom_rod_parts())
    items.extend(custom_rod_upper_members())
    items.extend(custom_rod_locks())
    items.append(("Spinner Lever 08 - Rod Lock",
                  A.posed(rows["Spinner Lever 08 - Rod Lock"])))

    M = module_transform()
    above = [(HINGE_SPRING, fidget.load(HINGE_SPRING, product="spinner"))]
    above += swing(swinging_items(), deg)
    for n, m in above:
        c = m.copy()
        c.apply_transform(M)
        items.append((n, c))
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
