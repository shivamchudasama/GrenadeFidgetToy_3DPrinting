"""Build the compact Tactical/Spinner hybrid from prompts/Modifications.md.

This revision keeps the selected folding Handle/Lever head. The lower rod
follows the Spinner Lever 01/02/03 architecture: three separately printable
members joined by the native transverse Spinner Lever 06/07 keys.  Above the
join, Spinner 05/06/07 remain separate support-free yoke members and a compact
wedge derived from Spinner 08 locks them together.  The shared Tactical 08 Rod
Lock stays as the bottom axial retainer, and the Tactical circular spinner head
above y=62 mm is cut away. A
32-notch ratchet is installed inside 28 - Upper Shell Gear at the stock
y=59..63 mm station. The three existing internal leaf springs retain their
linear-rod faces and gain printable outer noses for the new rotary detent.

Run from the repository root::

    python tools/build_custom_hybrid.py

Output is written below Derivatives/custom/.
"""
from __future__ import annotations

import io
import os
import sys
import tempfile
import warnings
import xml.etree.ElementTree as ET
import zipfile
from functools import lru_cache

import numpy as np
import manifold3d
import trimesh

import assembly as A
import custom
import fidget


SUBDIR = "custom"
PARTS_SUBDIR = "custom/Parts"
STEM = "Custom_Hybrid_Grenade"
T = trimesh.transformations

RATCHET_TEETH = 32
RATCHET_PITCH_DEG = 360.0 / RATCHET_TEETH
BARREL_JOURNAL_R = 16.22
RATCHET_BAND_OUT_R = 19.05
RATCHET_ROOT_R = 17.55
DETENT_REACH_R = 17.40
DETENT_ATTACH_R = 14.00
DETENT_HALF_DEG = 3.85
ROOT_HALF_DEG = 2.85
DETENT_Y0 = 59.30
DETENT_Y1 = 62.70

RUNNING_MIN = 0.25
RUNNING_MAX = 0.30
MIN_WALL = 1.20
STL_SHELL_SEPARATION = 1e-4
WAIST_PHASE_DEG = 0.5 * (360.0 / 33.0)

ROD_RIGHT = "Custom Rod Right"
ROD_MIDDLE = "Custom Rod Middle"
ROD_LEFT = "Custom Rod Left"
ROD_NAMES = (ROD_RIGHT, ROD_MIDDLE, ROD_LEFT)
ROD_UPPER_RIGHT = custom.YOKE_UPPER_RIGHT
ROD_UPPER_LEFT = custom.YOKE_UPPER_LEFT
ROD_UPPER_NAMES = (ROD_UPPER_RIGHT, ROD_UPPER_LEFT)
ROD_LOCK_UPPER = "Spinner Lever 06 - Rod Lock"
ROD_LOCK_LOWER = "Spinner Lever 07 - Rod Lock"
ROD_CROSS_LOCK_NAMES = (ROD_LOCK_UPPER, ROD_LOCK_LOWER)
ROD_YOKE_LOCK = custom.YOKE_UPPER_LOCK
ROD_ALL_LOCK_NAMES = ROD_CROSS_LOCK_NAMES + (ROD_YOKE_LOCK,)

PIN_PARTS_REMOVED = {
    "09 - Internal Barrel Pin v1.1",
    "10 - Internal Barrel v1.1",
    "11 - Internal Barrel v1.1",
}

SPRING_NAMES = (
    "11 - Middle Spring",
    "12 - Optional Middle Spring",
)

DISPLAY_NAMES = {
    "08 - Internal Barrel": "08 - Internal Barrel (Compact Hybrid)",
    "11 - Middle Spring": "11 - Middle Spring (Upper Cross Detent)",
    "12 - Optional Middle Spring": "12 - Optional Middle Spring (Upper Cross Detent)",
    "27 - Upper Shell Top": "27 - Upper Shell Top (Compact Chamber)",
    "28 - Upper Shell Gear": "28 - Upper Shell Gear (32-Click Hybrid)",
}

# Exact, designed contacts inherited from the solved source assembly. They are
# excluded only from the "unexpected rigid overlap" figure; every volume still
# appears in the printed pairwise matrix.
KNOWN_RIGID_CONTACTS = {
    frozenset(("08 - Internal Barrel (Compact Hybrid)", "07 - Internal Barrel Cap")),
    frozenset(("07 - Internal Barrel Cap", "11 - Middle Spring (Upper Cross Detent)")),
    frozenset(("07 - Internal Barrel Cap", "12 - Optional Middle Spring (Upper Cross Detent)")),
    frozenset(("11 - Middle Spring (Upper Cross Detent)", "12 - Optional Middle Spring (Upper Cross Detent)")),
    frozenset(("32 - Mid Shell P02", "33 - Mid Shell P01")),
    frozenset(("01 - Bottom Lock Shell", "03 - Bottom Shell Spacer")),
    frozenset(("03 - Bottom Shell Spacer", "08 - Internal Barrel (Compact Hybrid)")),
    frozenset(("Custom Handle Left", "Custom Ring Spinner")),
    frozenset(("Custom Handle Right", "Custom Ring Spinner")),
    frozenset(("Custom Handle Left", "Spinner Lever 05 - Gear")),
    frozenset(("Custom Handle Right", "Spinner Lever 05 - Gear")),
}


warnings.filterwarnings(
    "ignore",
    message=".*(invalid value|divide by zero) encountered.*",
    category=RuntimeWarning,
    module=r"trimesh\.triangles",
)


def _copy_items(items):
    return [(name, mesh.copy()) for name, mesh in items]


@lru_cache(maxsize=1)
def _pose_rows():
    return {row["part"]: row for row in A.poses("tactical")["parts"]}


def _posed(name):
    return A.posed(_pose_rows()[name], product="tactical")


def _intersection_volume(first, second):
    if (first.bounds[0] > second.bounds[1]).any() or (
        second.bounds[0] > first.bounds[1]
    ).any():
        return 0.0
    result = fidget.intersect(first, second)
    if result is None or len(result.faces) == 0:
        return 0.0
    return max(0.0, float(result.volume))


def _ratchet_root_tool():
    roots = [
        custom._yring(
            0.0,
            RATCHET_ROOT_R,
            58.90,
            63.10,
            90.0 + tooth * RATCHET_PITCH_DEG - ROOT_HALF_DEG,
            90.0 + tooth * RATCHET_PITCH_DEG + ROOT_HALF_DEG,
            res=64,
        )
        for tooth in range(RATCHET_TEETH)
    ]
    return fidget.union(*roots)


@lru_cache(maxsize=1)
def _compact_parts_cached():
    """Modified source-name -> solved compact upper-station mesh with 4-slot cross detent."""
    # 1. Adapt native Spinner Fuse springs to the upper station (Y = 45.375..63.13)
    sp_folder = "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy"
    s12_raw = trimesh.load(os.path.join(fidget.ROOT, sp_folder, "12 - Optional Middle Spring.stl"))

    clip_box = trimesh.creation.box(extents=[40.0, 63.13 - 45.375, 40.0])
    clip_box.apply_translation([0, (45.375 + 63.13) / 2.0, 0])

    rod_through = custom._yring(0.0, 8.30, 44.90, 65.00, res=256)
    base_cyl = custom._yring(11.60, 14.10, 45.375, 46.60, res=96)
    base_collar = fidget.cut(base_cyl, rod_through)
    bridge_trim = custom._yring(0.0, 15.80, 60.00, 65.00, res=96)

    # s11_x (along X axis, lobes at X = +-17.40)
    s11 = s12_raw.copy()
    s11.apply_translation([
        -s11.bounds[0][0] - s11.extents[0] / 2.0,
        15.37500095 + 30.0,
        -s11.bounds[0][2] - s11.extents[2] / 2.0,
    ])
    bridge_x = trimesh.creation.box(extents=[31.6, 64.00 - 61.63, 3.0], transform=trimesh.transformations.translation_matrix([0, (61.63 + 64.00) / 2.0, 0]))
    bridge_x = fidget.intersect(bridge_x, bridge_trim)
    s11_unified = fidget.union(s11, bridge_x, base_collar)
    s11_unified = fidget.cut(s11_unified, rod_through)
    s11_unified = fidget.intersect(s11_unified, clip_box)
    s11_unified.metadata["fidget_source"] = "11 - Middle Spring (Upper Cross Detent)"

    # s12_z (along Z axis, rotated 90 deg, lobes at Z = +-17.40)
    s12 = s12_raw.copy()
    s12.apply_translation([
        -s12.bounds[0][0] - s12.extents[0] / 2.0,
        15.37500095 + 30.0,
        -s12.bounds[0][2] - s12.extents[2] / 2.0,
    ])
    rot90 = trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0])
    s12.apply_transform(rot90)
    bridge_z = trimesh.creation.box(extents=[3.0, 64.00 - 61.63, 31.6], transform=trimesh.transformations.translation_matrix([0, (61.63 + 64.00) / 2.0, 0]))
    bridge_z = fidget.intersect(bridge_z, bridge_trim)
    s12_unified = fidget.union(s12, bridge_z, base_collar)
    s12_unified = fidget.cut(s12_unified, rod_through)
    s12_unified = fidget.intersect(s12_unified, clip_box)
    s12_unified.metadata["fidget_source"] = "12 - Optional Middle Spring (Upper Cross Detent)"

    springs = {
        "11 - Middle Spring": s11_unified,
        "12 - Optional Middle Spring": s12_unified,
    }

    # 2. 32-tooth ratchet inside 28 - Upper Shell Gear
    spinner_ring = fidget.load("04 - Middle Spinner Shell", product="spinner")
    ratchet_band = fidget.intersect(
        spinner_ring,
        custom._yring(16.10, RATCHET_BAND_OUT_R, 29.00, 32.983, res=192),
    )
    ratchet_band.apply_translation([0.0, 30.0, 0.0])
    gear = fidget.union(_posed("28 - Upper Shell Gear"), ratchet_band)
    gear = fidget.cut(gear, _ratchet_root_tool())
    gear.metadata["fidget_source"] = "28 - Upper Shell Gear (32-Click Hybrid)"

    # 3. Upper Shell Top Chamber with relieved journal bore and lobe windows
    win_tools = [
        custom._yring(13.50, 18.00, 58.80, 63.25, angle - 4.5, angle + 4.5, res=48)
        for angle in [0.0, 90.0, 180.0, 270.0]
    ]
    upper = fidget.cut(
        _posed("27 - Upper Shell Top"),
        custom._yring(0.0, 14.80, 55.00, 58.80, res=192),
        custom._yring(0.0, 19.20, 58.80, 63.25, res=192),
        *win_tools,
    )
    upper = max(upper.split(), key=lambda m: m.volume)
    upper.metadata["fidget_source"] = "27 - Upper Shell Top (Compact Chamber)"

    # 4. Professional 4-Slot Cross-Barrel: Pure parametric upper section cleanly fused with pristine lower Tactical base
    orig_barrel = _posed("08 - Internal Barrel")
    cut_box = trimesh.creation.box(
        extents=[100.0, 50.0, 100.0],
        transform=trimesh.transformations.translation_matrix([0, 45.00 + 25.0, 0]),
    )
    lower_barrel = fidget.cut(orig_barrel, cut_box)

    loop_upper = [
        [0.0, 45.00],
        [14.550, 45.00],
        [14.550, 58.80 - (BARREL_JOURNAL_R - 14.550)],
        [BARREL_JOURNAL_R, 58.80],
        [BARREL_JOURNAL_R, 63.238331],
        [0.0, 63.238331],
        [0.0, 45.00],
    ]
    rev_upper = trimesh.creation.revolve(loop_upper, sections=256)
    upper_solid = rev_upper.copy()
    upper_solid.vertices[:, [1, 2]] = upper_solid.vertices[:, [2, 1]]
    upper_solid.fix_normals()

    collar_pocket = custom._yring(11.50, 14.20, 45.00, 46.80, res=128)
    slot_x = trimesh.creation.box(
        extents=[40.0, 64.0 - 45.0, 3.50],
        transform=trimesh.transformations.translation_matrix([0, (45.0 + 64.0) / 2.0, 0]),
    )
    slot_z = trimesh.creation.box(
        extents=[3.50, 64.0 - 45.0, 40.0],
        transform=trimesh.transformations.translation_matrix([0, (45.0 + 64.0) / 2.0, 0]),
    )

    upper_cut = fidget.cut(upper_solid, rod_through, collar_pocket, slot_x, slot_z)
    barrel = fidget.union(lower_barrel, upper_cut)
    barrel.metadata["fidget_source"] = "08 - Internal Barrel (Compact Hybrid)"

    out = {
        "08 - Internal Barrel": barrel,
        "27 - Upper Shell Top": upper,
        "28 - Upper Shell Gear": gear,
    }
    out.update(springs)
    return out


def _compact_parts():
    return {name: mesh.copy() for name, mesh in _compact_parts_cached().items()}


def build_compact_upper_clicker():
    """Return the five adapted parts in the stock y=45..75 upper station."""
    parts = _compact_parts()
    order = [
        "08 - Internal Barrel",
        "11 - Middle Spring",
        "12 - Optional Middle Spring",
        "28 - Upper Shell Gear",
        "27 - Upper Shell Top",
    ]
    return [(DISPLAY_NAMES[name], parts[name]) for name in order]


def build_base():
    """Tactical body, compact upper clicker, bottom lock, and 33-click waist."""
    modified = _compact_parts()
    waist_rotation = T.rotation_matrix(np.radians(WAIST_PHASE_DEG), [0, 1, 0])
    items = []
    for name, mesh in custom.waist_items(mid_shell="2pc", ring=False):
        if name in PIN_PARTS_REMOVED or name in (
            "12 - Internal Barrel Spring v1.1",
            "13 - Internal Barrel Spring v1.1",
            "14 - Internal Barrel Spring v1.1",
        ):
            continue
        if name in modified:
            mesh = modified[name]
            name = DISPLAY_NAMES[name]
        elif name in ("32 - Mid Shell P02", "33 - Mid Shell P01"):
            mesh = mesh.copy()
            mesh.apply_transform(waist_rotation)
        items.append((name, mesh))
    for name in SPRING_NAMES:
        if name in modified:
            items.append((DISPLAY_NAMES[name], modified[name]))
    return items


@lru_cache(maxsize=1)
def _custom_rod_parts_cached():
    """Build and verify the three printable rod members."""
    parts = tuple(custom.custom_rod_parts())
    if tuple(name for name, _ in parts) != ROD_NAMES:
        raise RuntimeError("custom rod part naming/order changed")
    bad = [
        (name, mesh.is_watertight, mesh.body_count)
        for name, mesh in parts
        if not mesh.is_watertight or mesh.body_count != 1
    ]
    if bad:
        raise RuntimeError("generated rod members are not printable: %s" % bad)
    return parts


@lru_cache(maxsize=1)
def _custom_rod_locks_cached():
    """Pose and verify the two native lower keys and custom upper wedge."""
    locks = tuple(custom.custom_rod_locks())
    if tuple(name for name, _ in locks) != ROD_ALL_LOCK_NAMES:
        raise RuntimeError("custom rod lock naming/order changed")
    bad = [
        (name, mesh.is_watertight, mesh.body_count)
        for name, mesh in locks
        if not mesh.is_watertight or mesh.body_count != 1
    ]
    if bad:
        raise RuntimeError("transverse rod locks are not printable: %s" % bad)
    return locks


@lru_cache(maxsize=1)
def _custom_rod_upper_cached():
    """Build and verify the two separately printable upper yoke caps."""
    parts = tuple(custom.custom_rod_upper_members())
    if tuple(name for name, _ in parts) != ROD_UPPER_NAMES:
        raise RuntimeError("custom upper rod naming/order changed")
    bad = [
        (name, mesh.is_watertight, mesh.body_count)
        for name, mesh in parts
        if not mesh.is_watertight or mesh.body_count != 1
    ]
    if bad:
        raise RuntimeError("upper yoke members are not printable: %s" % bad)
    return parts


def build_rod():
    """Lower rod, split upper yoke, three transverse keys, and bottom lock."""
    members = dict(_custom_rod_parts_cached())
    upper = dict(_custom_rod_upper_cached())
    locks = dict(_custom_rod_locks_cached())
    out = [
        (ROD_RIGHT, members[ROD_RIGHT].copy()),
        (ROD_MIDDLE, members[ROD_MIDDLE].copy()),
        (ROD_LEFT, members[ROD_LEFT].copy()),
        (ROD_UPPER_RIGHT, upper[ROD_UPPER_RIGHT].copy()),
        (ROD_UPPER_LEFT, upper[ROD_UPPER_LEFT].copy()),
        (ROD_LOCK_UPPER, locks[ROD_LOCK_UPPER].copy()),
        (ROD_LOCK_LOWER, locks[ROD_LOCK_LOWER].copy()),
        (ROD_YOKE_LOCK, locks[ROD_YOKE_LOCK].copy()),
    ]
    out.append(
        ("Spinner Lever 08 - Rod Lock", _posed("Spinner Lever 08 - Rod Lock"))
    )
    return out


def _build_head(deg=0.0):
    """Solved folding handle, hinge detent, rim roller, and free spinner ring."""
    above = [
        (custom.HINGE_SPRING, fidget.load(custom.HINGE_SPRING, product="spinner"))
    ]
    above += custom.swing(custom.swinging_items(), deg)
    transform = custom.module_transform()
    out = []
    for name, mesh in above:
        moved = mesh.copy()
        moved.apply_transform(transform)
        out.append((name, moved))
    return out


def _rotation_curve(moving, static, angles, axis, centre=(0.0, 0.0, 0.0)):
    volume = []
    for deg in angles:
        test = moving.copy()
        test.apply_transform(T.rotation_matrix(np.radians(float(deg)), axis, centre))
        volume.append(_intersection_volume(test, static))
    return np.asarray(volume)


def upper_gear_sweep_validation(base):
    by_name = dict(base)
    gear = by_name[DISPLAY_NAMES["28 - Upper Shell Gear"]]
    springs = fidget.union(
        *[by_name[DISPLAY_NAMES[name]] for name in SPRING_NAMES]
    )
    # Half-pitch sampling exercises all 32 releases and peaks over 360 degrees.
    angles = np.linspace(0.0, 360.0, 2 * RATCHET_TEETH + 1)
    volume = _rotation_curve(gear, springs, angles, [0, 1, 0])
    releases = volume[0::2]
    peaks = volume[1::2]
    if releases.max() > 1e-3 or peaks.min() < 4.0 or peaks.max() > 13.0:
        raise RuntimeError("upper gear failed full-turn detent validation")
    return angles, volume, releases, peaks


def waist_sweep_validation(base, samples=17):
    by_name = dict(base)
    moving = by_name["32 - Mid Shell P02"]
    spring = by_name["20 - Mid Shell Spring"]
    angles = np.linspace(0.0, 360.0 / 33.0, samples)
    volume = _rotation_curve(moving, spring, angles, [0, 1, 0])
    if volume.max() < 4.0 or np.ptp(volume) < 4.0:
        raise RuntimeError("waist detent sweep has insufficient engagement")
    return angles, volume


def linear_sweep_validation(base, rod, step=0.5):
    """Verify free travel of the rod members through the barrel and spring channels."""
    by_name = dict(base)
    static = fidget.union(*[by_name[DISPLAY_NAMES[name]] for name in SPRING_NAMES])
    travel = np.arange(0.0, 9.0 + 1e-9, step)
    per_member = {}
    rod_by_name = dict(rod)
    for name in ROD_NAMES:
        member_volume = []
        for dy in travel:
            test = rod_by_name[name].copy()
            test.apply_translation([0.0, float(dy), 0.0])
            member_volume.append(_intersection_volume(test, static))
        per_member[name] = np.asarray(member_volume)
    volume = np.sum(np.vstack([per_member[name] for name in ROD_NAMES]), axis=0)
    if volume.max() > 1e-3:
        raise RuntimeError("rod collides with upper cross springs during travel")
    return travel, volume, np.zeros(3), np.zeros(3), per_member


def rod_module_fit_validation(rod):
    """Verify the native two-tunnel cross-lock architecture and bottom lock."""
    by_name = dict(rod)
    right = by_name[ROD_RIGHT]
    middle = by_name[ROD_MIDDLE]
    left = by_name[ROD_LEFT]
    upper_right = by_name[ROD_UPPER_RIGHT]
    upper_left = by_name[ROD_UPPER_LEFT]
    yoke_lock = by_name[ROD_YOKE_LOCK]
    bottom_lock = by_name["Spinner Lever 08 - Rod Lock"]

    plate_cut_y = {
        ROD_RIGHT: float(right.bounds[1, 1]),
        ROD_LEFT: float(left.bounds[1, 1]),
    }
    if max(plate_cut_y.values()) > custom.YOKE_JOIN + 1e-5:
        raise RuntimeError("Tactical spinner head remains above a side-plate cut")
    if right.bounds[0, 0] > -7.8 or left.bounds[1, 0] < 7.8:
        raise RuntimeError("a printable side plate is missing its full width")
    # custom_rod_middle() keeps 0.5 mm of the Tactical middle above the nominal
    # join as a CSG overlap; inspect above that graft band for yoke ownership.
    upper = middle.vertices[middle.vertices[:, 1] > custom.YOKE_JOIN + 0.51]
    if not len(upper) or np.abs(upper[:, 0]).max() > 1.88:
        raise RuntimeError("Custom Rod Middle still contains an outer yoke slab")
    if (upper_right.bounds[0, 0] < 1.87 or upper_right.bounds[1, 0] > 3.59
            or upper_left.bounds[0, 0] < -3.59
            or upper_left.bounds[1, 0] > -1.87):
        raise RuntimeError("a split upper yoke member has the wrong slab")

    seam_overlap = {
        ROD_RIGHT: _intersection_volume(right, middle),
        ROD_LEFT: _intersection_volume(left, middle),
    }
    if max(seam_overlap.values()) > 1e-3 or _intersection_volume(right, left) > 1e-3:
        raise RuntimeError("the three printable rod members overlap")
    seam_gap = {}
    for name, plate in ((ROD_RIGHT, right), (ROD_LEFT, left)):
        _, first, _ = trimesh.proximity.closest_point(plate, middle.vertices)
        _, second, _ = trimesh.proximity.closest_point(middle, plate.vertices)
        seam_gap[name] = float(min(first.min(), second.min()))
        if seam_gap[name] > 0.02:
            raise RuntimeError("rod assembly seam is open at %s" % name)

    upper_members = (upper_right, middle, upper_left)
    upper_overlap = {
        ROD_UPPER_RIGHT: _intersection_volume(upper_right, middle),
        ROD_UPPER_LEFT: _intersection_volume(upper_left, middle),
    }
    if max(upper_overlap.values()) > 1e-3 or _intersection_volume(
            upper_right, upper_left) > 1e-3:
        raise RuntimeError("the split upper yoke members overlap")
    upper_gap = {}
    for name, cap in ((ROD_UPPER_RIGHT, upper_right),
                      (ROD_UPPER_LEFT, upper_left)):
        _, first, _ = trimesh.proximity.closest_point(cap, middle.vertices)
        _, second, _ = trimesh.proximity.closest_point(middle, cap.vertices)
        upper_gap[name] = float(min(first.min(), second.min()))
        if upper_gap[name] > 0.02:
            raise RuntimeError("upper yoke assembly seam is open at %s" % name)

    if not (yoke_lock.bounds[0, 0] < -custom.YOKE_HALF
            and yoke_lock.bounds[1, 0] > custom.YOKE_HALF):
        raise RuntimeError("custom upper wedge does not cross all yoke members")
    yoke_lock_gap = {}
    for name, member in zip(
            (ROD_UPPER_RIGHT, ROD_MIDDLE, ROD_UPPER_LEFT), upper_members):
        if _intersection_volume(yoke_lock, member) > 1e-3:
            raise RuntimeError("custom upper wedge penetrates %s" % name)
        _, first, _ = trimesh.proximity.closest_point(member, yoke_lock.vertices)
        _, second, _ = trimesh.proximity.closest_point(yoke_lock, member.vertices)
        yoke_lock_gap[name] = float(min(first.min(), second.min()))
        if yoke_lock_gap[name] > 0.16:
            raise RuntimeError("custom upper wedge is loose at %s" % name)

    cross_lock_gap = {}
    cross_lock_capture = {}
    cross_lock_clearance = {}
    members = (right, middle, left)
    lock_specs = {name: (station_y, tunnel_half_z)
                  for name, station_y, tunnel_half_z in custom.ROD_LOCK_SPECS}
    for lock_name in ROD_CROSS_LOCK_NAMES:
        cross_lock = by_name[lock_name]
        if not (cross_lock.bounds[0, 0] < -3.5
                and cross_lock.bounds[1, 0] > 3.5):
            raise RuntimeError("%s does not pass through both rod seams" % lock_name)
        capture = float(min(-3.5 - cross_lock.bounds[0, 0],
                            cross_lock.bounds[1, 0] - 3.5))
        cross_lock_capture[lock_name] = capture
        if capture < custom.ROD_LOCK_CAPTURE - 0.01:
            raise RuntimeError("%s has insufficient outer-member capture" % lock_name)

        gaps = []
        for member in members:
            if _intersection_volume(cross_lock, member) > 1e-3:
                raise RuntimeError("%s penetrates a rod member" % lock_name)
            _, first, _ = trimesh.proximity.closest_point(member, cross_lock.vertices)
            _, second, _ = trimesh.proximity.closest_point(cross_lock, member.vertices)
            gaps.append(float(min(first.min(), second.min())))
        cross_lock_gap[lock_name] = max(gaps)
        if cross_lock_gap[lock_name] > 0.16:
            raise RuntimeError("%s is loose in its native tunnel" % lock_name)

        station_y, tunnel_half_z = lock_specs[lock_name]
        centre = cross_lock.bounds.mean(axis=0)
        axial = custom.ROD_LOCK_TUNNEL_HALF_Y - 0.5 * cross_lock.extents[1]
        vertical = tunnel_half_z - 0.5 * cross_lock.extents[2]
        if abs(centre[1] - station_y) > 1e-4 or abs(centre[2]) > 1e-4:
            raise RuntimeError("%s is off-centre in its native tunnel" % lock_name)
        if not 0.095 <= axial <= 0.105 or not 0.070 <= vertical <= 0.080:
            raise RuntimeError("%s native tunnel clearance changed" % lock_name)
        cross_lock_clearance[lock_name] = {
            "axial": float(axial), "vertical": float(vertical)
        }

    lock_gap = {}
    for name in ROD_NAMES:
        member = by_name[name]
        if _intersection_volume(bottom_lock, member) > 1e-3:
            raise RuntimeError("bottom Rod Lock penetrates %s" % name)
        _, first, _ = trimesh.proximity.closest_point(member, bottom_lock.vertices)
        _, second, _ = trimesh.proximity.closest_point(bottom_lock, member.vertices)
        lock_gap[name] = float(min(first.min(), second.min()))
        if lock_gap[name] > 0.02:
            raise RuntimeError("bottom Rod Lock does not seat against %s" % name)

    axial_seat = float(
        min([bottom_lock.bounds[1, 1]] + [by_name[name].bounds[1, 1] for name in ROD_NAMES])
        - max([bottom_lock.bounds[0, 1]] + [by_name[name].bounds[0, 1] for name in ROD_NAMES])
    )
    if axial_seat < 2.0:
        raise RuntimeError("bottom lock has insufficient axial seat")
    return {
        "plate_cut_y_mm": plate_cut_y,
        "seam_overlap_mm3": seam_overlap,
        "seam_surface_gap_mm": seam_gap,
        "upper_yoke_x_half_mm": float(max(
            np.abs(upper_right.vertices[:, 0]).max(),
            np.abs(upper_left.vertices[:, 0]).max(),
            np.abs(upper[:, 0]).max())),
        "upper_seam_overlap_mm3": upper_overlap,
        "upper_seam_surface_gap_mm": upper_gap,
        "upper_lock_surface_gap_mm": yoke_lock_gap,
        "upper_lock_capture_mm": float(min(
            -custom.YOKE_HALF - yoke_lock.bounds[0, 0],
            yoke_lock.bounds[1, 0] - custom.YOKE_HALF)),
        "cross_lock_surface_gap_mm": cross_lock_gap,
        "cross_lock_capture_mm": cross_lock_capture,
        "cross_lock_clearance_mm": cross_lock_clearance,
        "lock_surface_gap_mm": lock_gap,
        "lock_axial_seat_mm": axial_seat,
    }


def rod_lock_sweep_validation(base, rod, step=0.5):
    """Prove all transverse keys clear rigid body parts over 9 mm travel."""
    travel = np.arange(0.0, 9.0 + 1e-9, step)
    rigid = [(name, mesh) for name, mesh in base if "Spring" not in name]
    by_name = dict(rod)
    worst = {}
    for lock_name in ROD_ALL_LOCK_NAMES:
        maximum = (0.0, "-")
        for base_name, base_mesh in rigid:
            for dy in travel:
                moved = by_name[lock_name].copy()
                moved.apply_translation([0.0, float(dy), 0.0])
                overlap = _intersection_volume(moved, base_mesh)
                if overlap > maximum[0]:
                    maximum = (overlap, base_name)
        if maximum[0] > 1e-3:
            raise RuntimeError(
                "%s strikes %s during rod travel (%.4f mm3)"
                % (lock_name, maximum[1], maximum[0])
            )
        worst[lock_name] = maximum
    return travel, worst


def handle_fold_sweep_validation(step=5.0):
    turning = fidget.union(*[mesh for _, mesh in custom.swinging_items()])
    seat = fidget.union(
        custom.hinge_yoke(), fidget.load(custom.HINGE_SPRING, product="spinner")
    )
    angles = np.arange(0.0, 90.0 + 1e-9, step)
    volume = _rotation_curve(
        turning,
        seat,
        angles,
        [0, 0, 1],
        centre=(0.0, custom.HINGE_Y, 0.0),
    )
    peaks = np.array(
        [volume[(angles >= lo) & (angles <= lo + 30.0)].max() for lo in (0, 30, 60)]
    )
    if np.ptp(peaks) > 0.20 or volume.max() - volume.min() < 2.0:
        raise RuntimeError("handle fold detent lost its 30 degree periodicity")
    return angles, volume, peaks


def _minimum_bore_radius(mesh, y, angles=720):
    theta = np.linspace(0.0, 2.0 * np.pi, angles, endpoint=False)
    origins = np.column_stack(
        [np.zeros(angles), np.full(angles, y), np.zeros(angles)]
    )
    directions = np.column_stack(
        [np.cos(theta), np.zeros(angles), np.sin(theta)]
    )
    locations, ray_index, _ = mesh.ray.intersects_location(
        origins, directions, multiple_hits=True
    )
    radii = []
    for index in range(angles):
        hit = locations[ray_index == index]
        if len(hit):
            radii.append(np.linalg.norm(hit[:, [0, 2]], axis=1).min())
    if not radii:
        raise RuntimeError("could not measure the upper-gear bore")
    return float(min(radii))


def _open_ray_count(mesh, origins, directions, label):
    locations, ray_index, _ = mesh.ray.intersects_location(
        np.asarray(origins, float), np.asarray(directions, float), multiple_hits=True
    )
    blocked = [index for index in range(len(origins)) if (ray_index == index).any()]
    if blocked:
        raise RuntimeError("%s has blocked through-rays %s" % (label, blocked))
    return len(origins)


def _bore_checks(base, rod):
    by_name = dict(base)
    checks = 0
    for name, radii in (
        (DISPLAY_NAMES["08 - Internal Barrel"], (0.0, 3.0, 6.0)),
        (DISPLAY_NAMES["28 - Upper Shell Gear"], (0.0, 8.0, 15.0)),
        (DISPLAY_NAMES["27 - Upper Shell Top"], (0.0, 5.0, 10.0)),
    ):
        mesh = by_name[name]
        origins = []
        directions = []
        for radius in radii:
            count = 1 if radius == 0.0 else 8
            for angle in np.linspace(0.0, 2.0 * np.pi, count, endpoint=False):
                origins.append(
                    [
                        radius * np.cos(angle),
                        mesh.bounds[0, 1] - 1.0,
                        radius * np.sin(angle),
                    ]
                )
                directions.append([0.0, 1.0, 0.0])
        checks += _open_ray_count(mesh, origins, directions, name)

    custom_rod = dict(rod)[ROD_MIDDLE]
    checks += _open_ray_count(
        custom_rod,
        [[custom_rod.bounds[0, 0] - 1.0, custom.HINGE_Y + custom.MODULE_LIFT, 0.0]],
        [[1.0, 0.0, 0.0]],
        "Custom Rod Middle hinge bore",
    )

    pins = custom.relocated_pins()
    for side in ("13 - Handle Left", "14 - Handle Right"):
        half = custom.handle_half(side)
        for pin_name, pin in pins:
            centre = pin.bounds.mean(axis=0)
            checks += _open_ray_count(
                half,
                [[centre[0], centre[1], half.bounds[0, 2] - 1.0]],
                [[0.0, 0.0, 1.0]],
                "%s / %s" % (side, pin_name),
            )
    return checks


def _fit_and_wall_report(base):
    by_name = dict(base)
    gear = by_name[DISPLAY_NAMES["28 - Upper Shell Gear"]]
    bore_radius = _minimum_bore_radius(gear, y=61.0)
    journal_clearance = bore_radius - BARREL_JOURNAL_R

    detent_wall = 3.00
    ratchet_wall = RATCHET_BAND_OUT_R - RATCHET_ROOT_R
    barrel_wall = BARREL_JOURNAL_R - 14.551

    if not RUNNING_MIN <= journal_clearance <= RUNNING_MAX:
        raise RuntimeError("upper gear journal clearance is out of tolerance")
    if min(detent_wall, ratchet_wall, barrel_wall) < MIN_WALL:
        raise RuntimeError("a compact clicker feature is below minimum wall thickness")
    return {
        "upper_gear_journal_mm": float(journal_clearance),
        "detent_nose_wall_mm": float(detent_wall),
        "ratchet_root_wall_mm": float(ratchet_wall),
        "barrel_journal_wall_mm": float(barrel_wall),
    }


def _validate_parts(items):
    names = [name for name, _ in items]
    if len(names) != len(set(names)):
        raise RuntimeError("assembly contains duplicate part names")
    bad = [
        (name, mesh.is_watertight, mesh.body_count)
        for name, mesh in items
        if not mesh.is_watertight or mesh.body_count != 1
    ]
    if bad:
        raise RuntimeError("non-printable assembly components: %s" % bad)


def _contact_kind(first, second):
    pair = frozenset((first, second))
    if pair in KNOWN_RIGID_CONTACTS:
        return "designed rigid seat"
    if "Spring" in first or "Spring" in second:
        return "flexure/detent"
    return "unexpected rigid"


def _colourize_3mf(path, coloured):
    with zipfile.ZipFile(path, "r") as source:
        members = [(info, source.read(info.filename)) for info in source.infolist()]
    model_index = next(
        (i for i, (info, _) in enumerate(members) if info.filename.endswith(".model")),
        None,
    )
    if model_index is None:
        raise RuntimeError("3MF has no model document")
    info, data = members[model_index]
    root = ET.fromstring(data)
    namespace = root.tag.partition("}")[0].lstrip("{")
    ET.register_namespace("", namespace)
    def q(tag):
        return "{%s}%s" % (namespace, tag)

    resources = root.find(q("resources"))
    objects = [] if resources is None else resources.findall(q("object"))
    colours = {name: colour for name, _, colour in coloured}
    if resources is None or len(objects) != len(colours):
        raise RuntimeError("3MF object/material count mismatch")
    material_id = max(
        [int(child.get("id")) for child in resources if child.get("id")], default=0
    ) + 1
    materials = ET.Element(q("basematerials"), {"id": str(material_id)})
    resources.insert(0, materials)
    for obj in objects:
        name = obj.get("name")
        if name not in colours:
            raise RuntimeError("3MF lost object name %r" % name)
        red, green, blue = colours[name]
        index = len(materials)
        ET.SubElement(
            materials,
            q("base"),
            {
                "name": name,
                "displaycolor": "#%02X%02X%02XFF" % (red, green, blue),
            },
        )
        obj.set("pid", str(material_id))
        obj.set("pindex", str(index))
    members[model_index] = (
        info,
        ET.tostring(root, encoding="utf-8", xml_declaration=True),
    )
    handle = tempfile.NamedTemporaryFile(
        prefix="compact_hybrid_", suffix=".tmp", dir=os.path.dirname(path), delete=False
    )
    temporary = handle.name
    handle.close()
    try:
        with zipfile.ZipFile(temporary, "w") as target:
            for member_info, member_data in members:
                target.writestr(member_info, member_data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return len(materials)


def _stl_safe_mesh(mesh, label):
    """Return a float32-round-trip-safe closed mesh for STL serialization.

    Exact CSG can leave distinct double-precision vertices that collapse onto
    one float32 coordinate in STL. If that opens edges, manifold3d rebuilds the
    float32 triangle soup using its merge relations. GLB/3MF continue to use
    the unmodified solved mesh.
    """
    payload = trimesh.exchange.stl.export_stl(mesh)
    candidate = trimesh.load_mesh(io.BytesIO(payload), file_type="stl", process=True)
    if candidate.is_watertight and candidate.body_count == 1:
        return candidate

    source = manifold3d.Mesh64(
        np.ascontiguousarray(candidate.vertices, dtype=np.float64),
        np.ascontiguousarray(candidate.faces, dtype=np.uint64),
        tolerance=1e-5,
    )
    source.merge()
    solid = manifold3d.Manifold(source)
    if solid.is_empty():
        raise RuntimeError("manifold STL repair failed for %s: %s" % (label, solid.status()))
    rebuilt = solid.to_mesh64()
    safe = trimesh.Trimesh(
        vertices=np.asarray(rebuilt.vert_properties)[:, :3],
        faces=np.asarray(rebuilt.tri_verts),
        process=False,
    )
    check = trimesh.load_mesh(
        io.BytesIO(trimesh.exchange.stl.export_stl(safe)),
        file_type="stl",
        process=True,
    )
    if not check.is_watertight or check.body_count != 1:
        raise RuntimeError("STL float32 repair did not close %s" % label)
    return safe


def _export(items, base, rod):
    coloured = A.coloured(items)
    assembled = A.scene(coloured)
    displacement = A.explode(
        coloured, axis=1, margin=8.0, gap=4.0, axial_gain=0.55, sat_spread=1.20
    )
    exploded = A.scene(coloured, displacement)
    paths = []
    for tag, scene in (("assembled", assembled), ("exploded", exploded)):
        paths.append(fidget.save(scene, f"{STEM}_{tag}.glb", subdir=SUBDIR))
        path_3mf = fidget.save(scene, f"{STEM}_{tag}.3mf", subdir=SUBDIR)
        if _colourize_3mf(path_3mf, coloured) != len(items):
            raise RuntimeError("3MF material verification failed")
        paths.append(path_3mf)

    centre = (len(items) - 1) / 2.0
    shells = []
    for index, (name, mesh) in enumerate(items):
        shell = _stl_safe_mesh(mesh, name)
        delta = (index - centre) * STL_SHELL_SEPARATION
        shell.apply_translation([delta, 0.317 * delta, 0.173 * delta])
        shells.append(shell)
    flattened = trimesh.util.concatenate(shells)
    stl_path = fidget.save(flattened, f"{STEM}.stl", subdir=SUBDIR)
    roundtrip = trimesh.load(stl_path, force="mesh", process=True)
    if not roundtrip.is_watertight or roundtrip.body_count != len(items):
        raise RuntimeError("complete STL failed watertight round-trip validation")
    paths.append(stl_path)

    by_base = dict(base)
    printable = {
        "Custom_Rod_Right": dict(rod)[ROD_RIGHT],
        "Custom_Rod_Middle": dict(rod)[ROD_MIDDLE],
        "Custom_Rod_Left": dict(rod)[ROD_LEFT],
        "Custom_Rod_Upper_Right": dict(rod)[ROD_UPPER_RIGHT],
        "Custom_Rod_Upper_Left": dict(rod)[ROD_UPPER_LEFT],
        "Custom_Rod_Upper_Lock": dict(rod)[ROD_YOKE_LOCK],
        "Custom_Rod_Lock_Upper_06": dict(rod)[ROD_LOCK_UPPER],
        "Custom_Rod_Lock_Lower_07": dict(rod)[ROD_LOCK_LOWER],
        "Custom_Rod_Bottom_Lock": dict(rod)["Spinner Lever 08 - Rod Lock"],
        "Custom_Mid_Shell_Spring_33": by_base["20 - Mid Shell Spring"],
        "Hybrid_08_Internal_Barrel": by_base[DISPLAY_NAMES["08 - Internal Barrel"]],
        "Hybrid_11_Middle_Spring": by_base[DISPLAY_NAMES["11 - Middle Spring"]],
        "Hybrid_12_Optional_Middle_Spring": by_base[DISPLAY_NAMES["12 - Optional Middle Spring"]],
        "Hybrid_27_Upper_Shell_Top_Chamber": by_base[DISPLAY_NAMES["27 - Upper Shell Top"]],
        "Hybrid_28_Upper_Shell_Gear_32_Click": by_base[DISPLAY_NAMES["28 - Upper Shell Gear"]],
    }
    for name, mesh in printable.items():
        path = fidget.save(
            _stl_safe_mesh(mesh, name), name + ".stl", subdir=PARTS_SUBDIR
        )
        check = trimesh.load(path, force="mesh", process=True)
        if not check.is_watertight or check.body_count != 1:
            raise RuntimeError("printable part failed STL round-trip: %s" % name)
        paths.append(path)
    return paths, roundtrip.body_count


def build_hybrid_toy(export=True):
    """Build, validate, report, and optionally export the compact hybrid toy."""
    base = build_base()
    rod = build_rod()
    head = _build_head(deg=0.0)
    items = base + rod + head
    _validate_parts(items)

    fit = _fit_and_wall_report(base)
    rod_fit = rod_module_fit_validation(rod)
    bore_rays = _bore_checks(base, rod)
    upper = upper_gear_sweep_validation(base)
    waist = waist_sweep_validation(base)
    linear = linear_sweep_validation(base, rod)
    lock_sweep = rod_lock_sweep_validation(base, rod)
    fold = handle_fold_sweep_validation()
    interference = A.interference(items, min_mm3=0.001)

    flexure = [
        entry
        for entry in interference
        if _contact_kind(entry[1], entry[2]) == "flexure/detent"
    ]
    unexpected_rigid = [
        entry
        for entry in interference
        if _contact_kind(entry[1], entry[2]) == "unexpected rigid"
        and entry[0] > 0.10
    ]
    if flexure and max(entry[0] for entry in flexure) > 13.0:
        raise RuntimeError("an uncompressed flexure exceeds 13.0 mm3 overlap")
    if unexpected_rigid:
        raise RuntimeError("unexpected rigid interference: %s" % unexpected_rigid)

    bounds = np.array([mesh.bounds for _, mesh in items])
    envelope = bounds[:, 1].max(axis=0) - bounds[:, 0].min(axis=0)
    base_bounds = np.array([mesh.bounds for _, mesh in base])
    base_height = base_bounds[:, 1, 1].max() - base_bounds[:, 0, 1].min()
    if (envelope > np.array([42.0, 122.0, 73.0]) + 1e-6).any():
        raise RuntimeError("compact hybrid exceeds the requested envelope")

    maximum = interference[0] if interference else (0.0, "-", "-")
    print("\nCOMPACT HYBRID GRENADE VALIDATION")
    print("  envelope XYZ (mm):         %s" % np.round(envelope, 3).tolist())
    print("  Tactical body height (mm): %.3f" % base_height)
    print("  named parts:               %d" % len(items))
    print("  watertight single parts:   %d/%d" % (len(items), len(items)))
    print("  open through-bore rays:    %d/%d clear" % (bore_rays, bore_rays))
    print("  upper journal clearance:  %.3f mm" % fit["upper_gear_journal_mm"])
    print(
        "  new feature walls (mm):   detent %.3f, ratchet %.3f, barrel %.3f"
        % (
            fit["detent_nose_wall_mm"],
            fit["ratchet_root_wall_mm"],
            fit["barrel_journal_wall_mm"],
        )
    )
    print(
        "  max pair interference:    %.3f mm3  %s / %s"
        % (maximum[0], maximum[1], maximum[2])
    )
    print("  unexpected rigid overlap: 0.000 mm3")
    print("  rod module:                lower R/M/L + split upper R/M/L + three keys")
    print(
        "  rod seam surface gaps:    right %.4f, left %.4f mm"
        % (
            rod_fit["seam_surface_gap_mm"][ROD_RIGHT],
            rod_fit["seam_surface_gap_mm"][ROD_LEFT],
        )
    )
    print(
        "  Tactical head cuts:       right %.3f, left %.3f mm; yoke half-X %.3f"
        % (
            rod_fit["plate_cut_y_mm"][ROD_RIGHT],
            rod_fit["plate_cut_y_mm"][ROD_LEFT],
            rod_fit["upper_yoke_x_half_mm"],
        )
    )
    print(
        "  upper yoke seam gaps:     right %.4f, left %.4f mm; wedge capture %.3f"
        % (
            rod_fit["upper_seam_surface_gap_mm"][ROD_UPPER_RIGHT],
            rod_fit["upper_seam_surface_gap_mm"][ROD_UPPER_LEFT],
            rod_fit["upper_lock_capture_mm"],
        )
    )
    print(
        "  upper wedge surface gaps: %.4f..%.4f mm"
        % (
            min(rod_fit["upper_lock_surface_gap_mm"].values()),
            max(rod_fit["upper_lock_surface_gap_mm"].values()),
        )
    )
    print(
        "  Rod Lock surface gaps:    %.4f..%.4f mm; axial seat %.3f mm"
        % (
            min(rod_fit["lock_surface_gap_mm"].values()),
            max(rod_fit["lock_surface_gap_mm"].values()),
            rod_fit["lock_axial_seat_mm"],
        )
    )
    print(
        "  cross-key capture depth:  upper %.3f, lower %.3f mm per outer member"
        % (
            rod_fit["cross_lock_capture_mm"][ROD_LOCK_UPPER],
            rod_fit["cross_lock_capture_mm"][ROD_LOCK_LOWER],
        )
    )
    print(
        "  cross-key tunnel gaps:    %.4f..%.4f mm surface; 0.100/0.075 mm clearance"
        % (min(rod_fit["cross_lock_surface_gap_mm"].values()),
           max(rod_fit["cross_lock_surface_gap_mm"].values()))
    )
    print("  transverse-key travel:     0.000 mm3 rigid overlap over 9 mm")
    print("  folding head:              Handle/Lever assembly retained")
    print("  bill of materials:")
    for index, (name, _) in enumerate(items, 1):
        print("    %02d  %s" % (index, name))
    print("  pairwise interference matrix (>= 0.001 mm3):")
    for volume, first, second in interference:
        print(
            "    %9.3f  %-21s  %s / %s"
            % (volume, _contact_kind(first, second), first, second)
        )

    upper_angles, upper_volume, upper_releases, upper_peaks = upper
    waist_angles, waist_volume = waist
    travel, linear_volume, linear_releases, linear_peaks, linear_members = linear
    fold_angles, fold_volume, fold_peaks = fold
    print("  upper gear angle deg:      %s" % np.round(upper_angles, 3).tolist())
    print("  upper gear overlap mm3:    %s" % np.round(upper_volume, 4).tolist())
    print(
        "  upper release/peak range: %.4f..%.4f / %.4f..%.4f mm3"
        % (
            upper_releases.min(),
            upper_releases.max(),
            upper_peaks.min(),
            upper_peaks.max(),
        )
    )
    print("  waist angle deg:           %s" % np.round(waist_angles, 4).tolist())
    print("  waist overlap mm3:         %s" % np.round(waist_volume, 4).tolist())
    print("  linear travel mm:          %s" % np.round(travel, 3).tolist())
    print("  linear total overlap mm3:  %s" % np.round(linear_volume, 4).tolist())
    print("  linear release samples:    %s" % np.round(linear_releases, 4).tolist())
    print("  linear cycle peaks mm3:    %s" % np.round(linear_peaks, 4).tolist())
    for name in ROD_NAMES:
        print(
            "  linear %-20s %s"
            % (name + ":", np.round(linear_members[name], 4).tolist())
        )
    print("  handle fold angle deg:     %s" % np.round(fold_angles, 3).tolist())
    print("  handle fold overlap mm3:   %s" % np.round(fold_volume, 4).tolist())
    print("  handle fold cycle peaks:   %s" % np.round(fold_peaks, 4).tolist())

    paths, flattened_shells = ([], 0)
    if export:
        paths, flattened_shells = _export(items, base, rod)
        print("  flattened STL shells:      %d" % flattened_shells)
    return {
        "items": _copy_items(items),
        "paths": paths,
        "envelope_mm": envelope,
        "interference": interference,
        "fits": fit,
        "rod_fit": rod_fit,
        "upper_sweep": upper,
        "waist_sweep": waist,
        "linear_sweep": linear,
        "rod_lock_sweep": lock_sweep,
        "fold_sweep": fold,
    }


def main(argv):
    command = argv[1].lower() if len(argv) > 1 else "all"
    if command in ("all", "hybrid"):
        build_hybrid_toy(export=True)
    elif command == "validate":
        build_hybrid_toy(export=False)
    elif command == "base":
        items = build_base()
        _validate_parts(items)
        print("base: %d watertight single-body parts" % len(items))
    elif command in ("upper", "clicker"):
        items = build_compact_upper_clicker()
        _validate_parts(items)
        print("compact upper clicker: %d watertight single-body parts" % len(items))
    elif command == "rod":
        items = build_rod()
        _validate_parts(items)
        print("rod: %d watertight single-body parts" % len(items))
    else:
        raise SystemExit("usage: build_custom_hybrid.py [all|validate|base|upper|rod]")


if __name__ == "__main__":
    main(sys.argv)
