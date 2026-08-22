"""Build five professional shell families for the Tactical Fidget Fuse.

This set uses analytic-looking features: smooth swept ribs, continuous orbit
bands, thread-cut grip rails, and a softly lobed contour sleeve.  It
deliberately does not reuse the height-field groove method of the earlier shell
set, which has since been removed.

All mechanical surfaces come from the upstream meshes.  Existing decoration is
removed only inside explicit exterior cosmetic bands; snap fits, bores, ledges,
the upper functional neck, and top/bottom interfaces remain unchanged.

Usage:
    python tools/build_professional_shell_designs.py

Output:
    Derivatives/Codex_Professional_Shell_Designs/
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import tempfile
import zipfile

from lxml import etree
from manifold3d import Error, Manifold, Mesh
import numpy as np
from shapely.geometry import LineString
import trimesh

import assembly as A
import fidget


OUTPUT_SUBDIR = "Codex_Professional_Shell_Designs"


@dataclass(frozen=True)
class PartSpec:
    label: str
    source: str
    # Exterior-only design bands: z minimum, z maximum, finished base radius.
    zones: tuple[tuple[float, float, float], ...]


PARTS = (
    PartSpec("Bottom_Shell", "04 - Bottom Shell 01", ((3.65, 9.35, 19.35),)),
    PartSpec("Mid_Shell", "Mid Shell Solid Color", ((1.25, 33.55, 20.00),)),
    # The upper 18.5 mm neck is functional and is intentionally left pristine.
    PartSpec("Upper_Shell_Top", "27 - Upper Shell Top", ((4.10, 11.30, 19.70),)),
)

# Contour Twist uses the upstream two-colour mid-shell pair instead of the
# one-piece solid shell used by the other professional families.  P01 is the
# outer cosmetic shell and P02 is the backing colour visible through its cuts.
CONTOUR_OUTER_SPEC = PartSpec(
    "Mid_Shell_Outer",
    "33 - Mid Shell P01",
    ((1.25, 33.55, 20.00),),
)
CONTOUR_INNER_SPEC = PartSpec(
    "Mid_Shell_Inner",
    "32 - Mid Shell P02",
    (),
)
CONTOUR_INNER_CLOCKING_DEGREES = 6.0


DESIGNS = (
    ("01_AeroFlow", "Long, softly swept ergonomic ribs"),
    ("02_Vector_Chevron", "Sculpted continuous chevrons with rounded shoulders"),
    ("03_Orbit", "Staggered raised traction pods with rounded edges"),
    (
        "04_Ergo_Scoops",
        "Vertical grip rails interrupted by multi-start helical thread cuts",
    ),
    ("05_Contour_Twist", "Deep twisted torque flutes with narrow crests"),
)

# Dense enough that a fingertip always meets a raised feature while spinning
# the roughly 40 mm diameter shells.  Sixteen features gives about 7.9 mm
# centre-to-centre spacing without making the existing rounded ribs overlap.
AEROFLOW_GRIP_COUNT = 16
VECTOR_CHEVRON_GRIP_COUNT = 16

# Furnished cosmetic skins use sub-0.2 mm sampling in both surface directions.
# This is intentionally limited to designs 01-04; Contour Twist already has a
# clean finished surface and remains at its established tessellation.
FURNISHED_THETA_STEPS = 720
FURNISHED_Z_SPACING = 0.14


def _prepare_with_matrix(spec: PartSpec) -> tuple[trimesh.Trimesh, np.ndarray]:
    mesh = fidget.load(spec.source, product="tactical").copy()
    centre_xy = mesh.bounds[:, :2].mean(axis=0)
    translation = (-centre_xy[0], -centre_xy[1], -mesh.bounds[0, 2])
    matrix = trimesh.transformations.translation_matrix(translation)
    mesh.apply_transform(matrix)
    return mesh, matrix


def _prepare(spec: PartSpec) -> trimesh.Trimesh:
    mesh, _ = _prepare_with_matrix(spec)
    return mesh


def _prepare_contour_pair():
    """Prepare both print-oriented parts and their exact assembly transforms."""
    rows = {row["part"]: row for row in A.poses("tactical")["parts"]}
    specs = (CONTOUR_OUTER_SPEC, CONTOUR_INNER_SPEC)
    prepared = {}
    transforms = {}

    # Tactical toy coordinates use +Y as the shell axis.  Map that axis to +Z
    # while retaining a right-handed coordinate system for clean mesh winding.
    axis_to_z = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ])
    assembled = []
    for spec in specs:
        mesh, print_matrix = _prepare_with_matrix(spec)
        pose = np.asarray(rows[spec.source]["matrix"], dtype=float)
        transform = axis_to_z @ pose @ np.linalg.inv(print_matrix)
        placed = mesh.copy()
        placed.apply_transform(transform)
        prepared[spec.label] = mesh
        transforms[spec.label] = transform
        assembled.append(placed)

    # The two upstream body poses were solved independently and leave the
    # P01/P02 keys interfering.  Rotating P02 by +6 degrees seats the three
    # repeated notch groups cleanly; +126 and +246 degrees are equivalent.
    clocking = trimesh.transformations.rotation_matrix(
        math.radians(CONTOUR_INNER_CLOCKING_DEGREES),
        (0.0, 0.0, 1.0),
    )
    transforms[CONTOUR_INNER_SPEC.label] = (
        clocking @ transforms[CONTOUR_INNER_SPEC.label]
    )
    assembled[1].apply_transform(clocking)

    bounds = np.asarray([mesh.bounds for mesh in assembled])
    lower = bounds[:, 0].min(axis=0)
    upper = bounds[:, 1].max(axis=0)
    normalise = trimesh.transformations.translation_matrix((
        -(lower[0] + upper[0]) / 2.0,
        -(lower[1] + upper[1]) / 2.0,
        -lower[2],
    ))
    for label in transforms:
        transforms[label] = normalise @ transforms[label]
    return prepared, transforms


def _radial_cage(height: float, z0: float, z1: float, radius: float) -> trimesh.Trimesh:
    """Smooth one cosmetic band while leaving both interface ends untouched."""
    transition = min(0.70, (z1 - z0) / 4.0)
    keep_radius = radius + 8.0
    profile = np.array([
        [0.0, 0.0],
        [keep_radius, 0.0],
        [keep_radius, max(0.0, z0 - transition)],
        [radius, z0],
        [radius, z1],
        [keep_radius, min(height, z1 + transition)],
        [keep_radius, height],
        [0.0, height],
        [0.0, 0.0],
    ])
    return trimesh.creation.revolve(profile, sections=256)


def _smooth_base(mesh: trimesh.Trimesh, spec: PartSpec) -> trimesh.Trimesh:
    result = mesh.copy()
    for z0, z1, radius in spec.zones:
        result = fidget.intersect(
            result,
            _radial_cage(float(mesh.extents[2]), z0, z1, radius),
        )
    if not result.is_watertight or result.body_count != 1:
        raise ValueError("failed to produce smooth base for %s" % spec.label)
    return result


def _open_swept_rib(
    radius: float,
    z0: float,
    z1: float,
    theta_path,
    width_mm: float,
    relief_mm: float,
    embed_mm: float = 0.28,
    path_steps: int | None = None,
    width_steps: int = 15,
) -> trimesh.Trimesh:
    """Create a closed, rounded rib swept over a cylindrical surface."""
    length = z1 - z0
    path_steps = path_steps or max(48, int(math.ceil(length / 0.34)) + 1)
    t = np.linspace(0.0, 1.0, path_steps)
    across = np.linspace(-1.0, 1.0, width_steps)
    tt, aa = np.meshgrid(t, across, indexing="ij")
    centre_theta = theta_path(tt)
    theta = centre_theta + aa * (width_mm / radius)
    z = z0 + tt * length

    cross_dome = np.cos(aa * np.pi / 2.0) ** 1.45
    end_dome = np.sin(tt * np.pi) ** 0.72
    outer_radius = radius + 0.018 + relief_mm * cross_dome * end_dome
    inner_radius = np.full_like(outer_radius, radius - embed_mm)

    vertices = []
    for rr in (outer_radius, inner_radius):
        vertices.append(np.column_stack((
            (rr * np.cos(theta)).ravel(),
            (rr * np.sin(theta)).ravel(),
            z.ravel(),
        )))
    vertices = np.vstack(vertices)
    sheet_size = path_steps * width_steps

    def idx(sheet: int, row: int, column: int) -> int:
        return sheet * sheet_size + row * width_steps + column

    faces = []
    for row in range(path_steps - 1):
        for column in range(width_steps - 1):
            o00, o01 = idx(0, row, column), idx(0, row, column + 1)
            o10, o11 = idx(0, row + 1, column), idx(0, row + 1, column + 1)
            faces.extend(((o00, o10, o11), (o00, o11, o01)))
            i00, i01 = idx(1, row, column), idx(1, row, column + 1)
            i10, i11 = idx(1, row + 1, column), idx(1, row + 1, column + 1)
            faces.extend(((i00, i11, i10), (i00, i01, i11)))

    for row in range(path_steps - 1):
        # The two long sides.
        for column in (0, width_steps - 1):
            o0, o1 = idx(0, row, column), idx(0, row + 1, column)
            i0, i1 = idx(1, row, column), idx(1, row + 1, column)
            if column == 0:
                faces.extend(((o0, i1, o1), (o0, i0, i1)))
            else:
                faces.extend(((o0, o1, i1), (o0, i1, i0)))

    for row in (0, path_steps - 1):
        # Rounded profile collapses toward the base at each end; this cap closes
        # the embedded part of the solid cleanly below the parent shell skin.
        for column in range(width_steps - 1):
            o0, o1 = idx(0, row, column), idx(0, row, column + 1)
            i0, i1 = idx(1, row, column), idx(1, row, column + 1)
            if row == 0:
                faces.extend(((o0, o1, i1), (o0, i1, i0)))
            else:
                faces.extend(((o0, i1, o1), (o0, i0, i1)))

    rib = trimesh.Trimesh(np.asarray(vertices), np.asarray(faces), process=True)
    if not rib.is_watertight:
        raise ValueError("open swept rib is not watertight")
    if rib.volume < 0.0:
        rib.invert()
    return rib


def _closed_wave_band(
    radius: float,
    centre_z: float,
    half_width: float,
    amplitude: float,
    wave_count: int,
    phase: float,
    relief_mm: float,
    embed_mm: float = 0.25,
) -> trimesh.Trimesh:
    """Create a continuous sinusoidal orbit band around the shell."""
    theta_steps = 320
    across_steps = 15
    theta = np.arange(theta_steps, dtype=float) * (2.0 * np.pi / theta_steps)
    across = np.linspace(-1.0, 1.0, across_steps)
    tt, aa = np.meshgrid(theta, across, indexing="ij")
    centre = centre_z + amplitude * np.sin(wave_count * tt + phase)
    z = centre + aa * half_width
    cross_dome = np.cos(aa * np.pi / 2.0) ** 1.55
    outer_radius = radius + 0.018 + relief_mm * cross_dome
    inner_radius = np.full_like(outer_radius, radius - embed_mm)

    vertices = []
    for rr in (outer_radius, inner_radius):
        vertices.append(np.column_stack((
            (rr * np.cos(tt)).ravel(),
            (rr * np.sin(tt)).ravel(),
            z.ravel(),
        )))
    vertices = np.vstack(vertices)
    sheet_size = theta_steps * across_steps

    def idx(sheet: int, row: int, column: int) -> int:
        return sheet * sheet_size + (row % theta_steps) * across_steps + column

    faces = []
    for row in range(theta_steps):
        nxt = row + 1
        for column in range(across_steps - 1):
            o00, o01 = idx(0, row, column), idx(0, row, column + 1)
            o10, o11 = idx(0, nxt, column), idx(0, nxt, column + 1)
            faces.extend(((o00, o10, o11), (o00, o11, o01)))
            i00, i01 = idx(1, row, column), idx(1, row, column + 1)
            i10, i11 = idx(1, nxt, column), idx(1, nxt, column + 1)
            faces.extend(((i00, i11, i10), (i00, i01, i11)))

        for column in (0, across_steps - 1):
            o0, o1 = idx(0, row, column), idx(0, nxt, column)
            i0, i1 = idx(1, row, column), idx(1, nxt, column)
            if column == 0:
                faces.extend(((o0, i1, o1), (o0, i0, i1)))
            else:
                faces.extend(((o0, o1, i1), (o0, i1, i0)))

    band = trimesh.Trimesh(np.asarray(vertices), np.asarray(faces), process=True)
    if not band.is_watertight:
        raise ValueError("closed orbit band is not watertight")
    return band


def _ellipsoid_scoop(
    radius: float,
    theta: float,
    centre_z: float,
    radial_axis: float,
    tangent_axis: float,
    axial_axis: float,
    depth: float,
    tilt: float,
) -> trimesh.Trimesh:
    """Smooth tilted ellipsoid positioned as a shallow cylindrical recess."""
    sphere = trimesh.creation.icosphere(subdivisions=4, radius=1.0)
    er = np.array([math.cos(theta), math.sin(theta), 0.0])
    et = np.array([-math.sin(theta), math.cos(theta), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    long_axis = math.sin(tilt) * et + math.cos(tilt) * ez
    cross_axis = math.cos(tilt) * et - math.sin(tilt) * ez
    local = sphere.vertices.copy()
    world = (
        np.outer(local[:, 0] * radial_axis, er)
        + np.outer(local[:, 1] * tangent_axis, cross_axis)
        + np.outer(local[:, 2] * axial_axis, long_axis)
    )
    world += np.array([
        (radius + radial_axis - depth) * math.cos(theta),
        (radius + radial_axis - depth) * math.sin(theta),
        centre_z,
    ])
    sphere.vertices = world
    return sphere


def _contour_sleeve(
    radius: float,
    z0: float,
    z1: float,
    lobe_count: int,
    twist: float,
    relief_mm: float,
    embed_mm: float = 0.24,
) -> trimesh.Trimesh:
    """A continuous soft-lobed sleeve with restrained axial twist."""
    theta_steps = 320
    z_steps = max(34, int(math.ceil((z1 - z0) / 0.35)) + 1)
    theta = np.arange(theta_steps, dtype=float) * (2.0 * np.pi / theta_steps)
    z = np.linspace(z0, z1, z_steps)
    tt, zz = np.meshgrid(theta, z)
    progress = (zz - z0) / (z1 - z0)
    lobe = (0.5 + 0.5 * np.cos(lobe_count * tt - twist * (progress - 0.5))) ** 1.8
    end_dome = np.sin(np.pi * progress) ** 0.65
    outer_radius = radius + 0.018 + relief_mm * lobe * end_dome
    inner_radius = np.full_like(outer_radius, radius - embed_mm)

    vertices = []
    for rr in (outer_radius, inner_radius):
        vertices.append(np.column_stack((
            (rr * np.cos(tt)).ravel(),
            (rr * np.sin(tt)).ravel(),
            zz.ravel(),
        )))
    vertices = np.vstack(vertices)
    sheet_size = theta_steps * z_steps

    def idx(sheet: int, row: int, column: int) -> int:
        return sheet * sheet_size + row * theta_steps + column % theta_steps

    faces = []
    for row in range(z_steps - 1):
        for column in range(theta_steps):
            nxt = column + 1
            o00, o01 = idx(0, row, column), idx(0, row, nxt)
            o10, o11 = idx(0, row + 1, column), idx(0, row + 1, nxt)
            faces.extend(((o00, o01, o11), (o00, o11, o10)))
            i00, i01 = idx(1, row, column), idx(1, row, nxt)
            i10, i11 = idx(1, row + 1, column), idx(1, row + 1, nxt)
            faces.extend(((i00, i11, i01), (i00, i10, i11)))

    for column in range(theta_steps):
        nxt = column + 1
        ib, ibn = idx(1, 0, column), idx(1, 0, nxt)
        ob, obn = idx(0, 0, column), idx(0, 0, nxt)
        faces.extend(((ib, ibn, obn), (ib, obn, ob)))
        it, itn = idx(1, z_steps - 1, column), idx(1, z_steps - 1, nxt)
        ot, otn = idx(0, z_steps - 1, column), idx(0, z_steps - 1, nxt)
        faces.extend(((it, otn, itn), (it, ot, otn)))

    sleeve = trimesh.Trimesh(np.asarray(vertices), np.asarray(faces), process=True)
    if not sleeve.is_watertight:
        raise ValueError("contour sleeve is not watertight")
    return sleeve


def _union_features(base: trimesh.Trimesh, features: list[trimesh.Trimesh]):
    result = fidget.union(base, *features)
    return result, len(features)


def _trim_base(mesh: trimesh.Trimesh, spec: PartSpec, depth: float) -> trimesh.Trimesh:
    """Trim only the exterior band so one continuous designed skin can replace it."""
    result = mesh.copy()
    for z0, z1, radius in spec.zones:
        result = fidget.intersect(
            result,
            _radial_cage(float(mesh.extents[2]), z0, z1, radius - depth),
        )
    return result


def _surface_sleeve(
    radius: float,
    z0: float,
    z1: float,
    height_function,
    inner_offset: float,
    theta_steps: int = 480,
    z_spacing: float = 0.24,
) -> trimesh.Trimesh:
    """One continuous high-resolution skin, avoiding fragmented feature seams."""
    theta_steps = int(theta_steps)
    z_steps = max(42, int(math.ceil((z1 - z0) / z_spacing)) + 1)
    theta = np.arange(theta_steps, dtype=float) * (2.0 * np.pi / theta_steps)
    z = np.linspace(z0, z1, z_steps)
    tt, zz = np.meshgrid(theta, z)
    progress = (zz - z0) / (z1 - z0)
    height = height_function(tt, zz, progress)
    outer_radius = radius + height
    inner_radius = np.full_like(outer_radius, radius - inner_offset)

    vertices = []
    for rr in (outer_radius, inner_radius):
        vertices.append(np.column_stack((
            (rr * np.cos(tt)).ravel(),
            (rr * np.sin(tt)).ravel(),
            zz.ravel(),
        )))
    vertices = np.vstack(vertices)
    sheet_size = theta_steps * z_steps

    def idx(sheet: int, row: int, column: int) -> int:
        return sheet * sheet_size + row * theta_steps + column % theta_steps

    faces = []
    for row in range(z_steps - 1):
        for column in range(theta_steps):
            nxt = column + 1
            o00, o01 = idx(0, row, column), idx(0, row, nxt)
            o10, o11 = idx(0, row + 1, column), idx(0, row + 1, nxt)
            faces.extend(((o00, o01, o11), (o00, o11, o10)))
            i00, i01 = idx(1, row, column), idx(1, row, nxt)
            i10, i11 = idx(1, row + 1, column), idx(1, row + 1, nxt)
            faces.extend(((i00, i11, i01), (i00, i10, i11)))

    for column in range(theta_steps):
        nxt = column + 1
        ib, ibn = idx(1, 0, column), idx(1, 0, nxt)
        ob, obn = idx(0, 0, column), idx(0, 0, nxt)
        faces.extend(((ib, ibn, obn), (ib, obn, ob)))
        it, itn = idx(1, z_steps - 1, column), idx(1, z_steps - 1, nxt)
        ot, otn = idx(0, z_steps - 1, column), idx(0, z_steps - 1, nxt)
        faces.extend(((it, otn, itn), (it, ot, otn)))

    sleeve = trimesh.Trimesh(np.asarray(vertices), np.asarray(faces), process=True)
    if not sleeve.is_volume:
        raise ValueError("continuous designed sleeve is not a closed volume")
    return sleeve


def _wrap_angle(angle: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(angle), np.cos(angle))


def _smootherstep(value: np.ndarray) -> np.ndarray:
    """C2-continuous 0..1 blend for printable, reflection-clean fillets."""
    value = np.clip(value, 0.0, 1.0)
    return value ** 3 * (value * (value * 6.0 - 15.0) + 10.0)


def build_aeroflow(source: trimesh.Trimesh, spec: PartSpec):
    base = _trim_base(source, spec, depth=0.24)
    sleeves = []
    for z0, z1, radius in spec.zones:
        tall = spec.label == "Mid_Shell"
        count = AEROFLOW_GRIP_COUNT
        half_width = 1.55 if tall else 1.25
        relief = 0.84 if tall else 0.58
        twist = 0.30 if tall else 0.10
        wave = 0.045 if tall else 0.018

        def height(theta, z, progress):
            del z
            end = _smootherstep(np.sin(np.pi * progress))
            value = np.zeros_like(theta)
            for index in range(count):
                centre = (
                    2.0 * np.pi * index / count
                    + twist * (progress - 0.5)
                    + wave * np.sin(2.0 * np.pi * (progress - 0.5))
                )
                arc = np.abs(_wrap_angle(theta - centre)) * radius
                dome = _smootherstep(1.0 - arc / half_width)
                value = np.maximum(value, relief * dome * end)
            return value

        sleeves.append(_surface_sleeve(
            radius,
            z0,
            z1,
            height,
            inner_offset=0.50,
            theta_steps=FURNISHED_THETA_STEPS,
            z_spacing=FURNISHED_Z_SPACING,
        ))
    result = fidget.union(base, *sleeves)
    return result, {
        "feature_type": "continuous swept-rib skin",
        "feature_count": count,
        "surface_finish": "high-resolution C2-continuous rib fillets",
        "cosmetic_theta_samples": FURNISHED_THETA_STEPS,
        "maximum_cosmetic_axial_spacing_mm": FURNISHED_Z_SPACING,
    }


def build_vector_chevron(source: trimesh.Trimesh, spec: PartSpec):
    base = _trim_base(source, spec, depth=0.24)
    sleeves = []
    for z0, z1, radius in spec.zones:
        tall = spec.label == "Mid_Shell"
        count = VECTOR_CHEVRON_GRIP_COUNT
        half_width = 1.35 if tall else 1.08
        relief = 0.76 if tall else 0.52
        spread = 0.20 if tall else 0.070

        def height(theta, z, progress):
            del z
            end = _smootherstep(np.sin(np.pi * progress))
            centred = 2.0 * progress - 1.0
            soft_v = np.sqrt(centred * centred + 0.038) - math.sqrt(0.038)
            value = np.zeros_like(theta)
            for index in range(count):
                centre = 2.0 * np.pi * index / count + spread * soft_v
                arc = np.abs(_wrap_angle(theta - centre)) * radius
                dome = _smootherstep(1.0 - arc / half_width)
                value = np.maximum(value, relief * dome * end)
            return value

        sleeves.append(_surface_sleeve(
            radius,
            z0,
            z1,
            height,
            inner_offset=0.50,
            theta_steps=FURNISHED_THETA_STEPS,
            z_spacing=FURNISHED_Z_SPACING,
        ))
    result = fidget.union(base, *sleeves)
    return result, {
        "feature_type": "continuous rounded-chevron skin",
        "feature_count": count,
        "surface_finish": "high-resolution C2-continuous chevron fillets",
        "cosmetic_theta_samples": FURNISHED_THETA_STEPS,
        "maximum_cosmetic_axial_spacing_mm": FURNISHED_Z_SPACING,
    }


def build_orbit(source: trimesh.Trimesh, spec: PartSpec):
    """A staggered pod tread with edges that resist tangential finger motion."""
    base = _trim_base(source, spec, depth=0.32)
    sleeves = []
    total_pads = 0
    row_count = 0
    for z0, z1, radius in spec.zones:
        tall = spec.label == "Mid_Shell"
        if tall:
            row_centres = np.linspace(z0 + 2.8, z1 - 2.8, 7)
            tangent_half_width, axial_half_height, relief = 2.35, 1.65, 0.78
        else:
            row_centres = np.linspace(z0 + 1.45, z1 - 1.45, 2)
            tangent_half_width, axial_half_height, relief = 2.05, 1.30, 0.62
        pads_per_row = 12
        row_count = len(row_centres)
        total_pads += row_count * pads_per_row

        def height(theta, z, progress):
            # Adjacent rows are offset by half a pitch, so every finger contact
            # finds a pod edge instead of a smooth circumferential lane.
            value = np.zeros_like(theta)
            for row_index, centre_z in enumerate(row_centres):
                row_phase = (row_index % 2) * np.pi / pads_per_row
                for pad_index in range(pads_per_row):
                    centre_theta = 2.0 * np.pi * pad_index / pads_per_row + row_phase
                    arc = np.abs(_wrap_angle(theta - centre_theta)) * radius
                    dz = np.abs(z - float(centre_z))
                    distance = (
                        (arc / tangent_half_width) ** 2.8
                        + (dz / axial_half_height) ** 2.8
                    )
                    dome = _smootherstep(1.0 - distance)
                    value = np.maximum(value, relief * dome)
            end = _smootherstep(np.sin(np.pi * progress))
            return value * end

        sleeves.append(_surface_sleeve(
            radius,
            z0,
            z1,
            height,
            inner_offset=0.58,
            theta_steps=FURNISHED_THETA_STEPS,
            z_spacing=FURNISHED_Z_SPACING,
        ))
    result = fidget.union(base, *sleeves)
    return result, {
        "feature_type": "staggered rounded traction-pod skin",
        "feature_count": total_pads,
        "traction_row_count": row_count,
        "surface_finish": "high-resolution C2-continuous pod fillets",
        "cosmetic_theta_samples": FURNISHED_THETA_STEPS,
        "maximum_cosmetic_axial_spacing_mm": FURNISHED_Z_SPACING,
    }


def build_ergo_scoops(source: trimesh.Trimesh, spec: PartSpec):
    """Vertical grip rails cross-cut by a right-hand multi-start thread.

    The rails supply the primary axial structure and broad tangential drive
    faces.  A continuous V-profile helix then cuts fully through every rail and
    just into the base skin.  This turns each rail into a sequence of tactile
    blocks while keeping the design visually ordered and easy to print.
    """
    base = _trim_base(source, spec, depth=0.40)
    sleeves = []
    for z0, z1, radius in spec.zones:
        tall = spec.label == "Mid_Shell"
        rail_count = 12
        thread_start_count = 4
        # The broad cutting line is paired with enough pitch to leave a
        # substantial finished rail block between passes.  The previous 6.4 mm
        # pitch left only tiny tabs and made the surface look unfinished.
        thread_pitch = 9.20
        thread_lead = thread_start_count * thread_pitch
        thread_phase = thread_pitch * 0.25
        if tall:
            rail_half_width = 1.78
            rail_relief = 0.92
            groove_half_width = 2.56
            groove_edge_bevel = 0.75
            groove_recess = 0.15
        else:
            rail_half_width = 1.55
            rail_relief = 0.70
            groove_half_width = 2.24
            groove_edge_bevel = 0.65
            groove_recess = 0.12

        def height(theta, z, progress):
            del progress
            rail = np.zeros_like(theta)
            for rail_index in range(rail_count):
                centre_theta = 2.0 * np.pi * rail_index / rail_count
                arc = np.abs(_wrap_angle(theta - centre_theta)) * radius

                # Broad chamfered shoulders and a restrained crown make the
                # rails look machined while preserving a positive drive face.
                shoulder = np.clip(
                    (rail_half_width - arc) / (rail_half_width * 0.44),
                    0.0,
                    1.0,
                )
                shoulder = (
                    shoulder ** 3
                    * (shoulder * (shoulder * 6.0 - 15.0) + 10.0)
                )
                crown = np.clip(
                    1.0 - arc / (rail_half_width * 0.76),
                    0.0,
                    1.0,
                ) ** 1.80
                profile = 0.84 * shoulder + 0.16 * crown
                rail = np.maximum(rail, rail_relief * profile)

            # Four interleaved right-hand starts.  Because lead is exactly four
            # pitches, the field closes perfectly at the theta seam.  This is
            # a genuinely wide cutting line, not a wide V-shaped falloff: most
            # of the band stays at full cutting depth and only its outer edge
            # receives a short printable bevel.
            unwrapped_z = (
                z - z0 - thread_phase
                - thread_lead * theta / (2.0 * np.pi)
            )
            thread_offset = (
                np.mod(unwrapped_z + thread_pitch / 2.0, thread_pitch)
                - thread_pitch / 2.0
            )
            groove_distance = np.abs(thread_offset)
            groove = np.clip(
                (groove_half_width - groove_distance) / groove_edge_bevel,
                0.0,
                1.0,
            )
            groove = groove ** 3 * (groove * (groove * 6.0 - 15.0) + 10.0)
            threaded_rail = rail - groove * (rail + groove_recess)

            # Blend into the untouched interface zones over a printable 0.7 mm
            # transition, leaving the central rail and thread geometry crisp.
            edge_distance = np.minimum(z - z0, z1 - z)
            end_blend = np.clip(edge_distance / 0.70, 0.0, 1.0)
            end_blend = (
                end_blend ** 3
                * (end_blend * (end_blend * 6.0 - 15.0) + 10.0)
            )
            return threaded_rail * end_blend

        sleeves.append(_surface_sleeve(
            radius,
            z0,
            z1,
            height,
            inner_offset=0.62,
            # Roughly 0.17 mm circumferential and 0.14 mm axial sampling on the
            # 40 mm shell removes visible STL stepping from the compound
            # rail/thread fillets without altering protected source geometry.
            theta_steps=FURNISHED_THETA_STEPS,
            z_spacing=FURNISHED_Z_SPACING,
        ))
    result = fidget.union(base, *sleeves)
    return result, {
        "feature_type": "vertical chamfered grip rails cross-cut by a multi-start thread",
        "feature_count": rail_count,
        "vertical_rail_count": rail_count,
        "rail_relief_mm": rail_relief,
        "thread_handedness": "right-hand",
        "thread_start_count": thread_start_count,
        "thread_pitch_mm": thread_pitch,
        "thread_lead_mm": thread_lead,
        "thread_groove_width_mm": 2.0 * groove_half_width,
        "thread_full_depth_width_mm": 2.0 * (
            groove_half_width - groove_edge_bevel
        ),
        "thread_edge_bevel_mm": groove_edge_bevel,
        "thread_base_recess_mm": groove_recess,
    }


def build_contour_twist(source: trimesh.Trimesh, spec: PartSpec):
    base = _trim_base(source, spec, depth=0.58)
    sleeves = []
    for z0, z1, radius in spec.zones:
        tall = spec.label.startswith("Mid_Shell")
        lobe_count = 6 if tall else 8
        twist = 1.60 if tall else 0.50
        relief = 1.50 if tall else 0.95
        recess = 0.44 if tall else 0.32

        def height(theta, z, progress):
            del z
            wave = np.cos(lobe_count * theta - twist * (progress - 0.5))
            # Narrow positive crests and broad recessed valleys make the
            # tangential faces substantially steeper than the old soft lobes.
            ridge = (0.5 + 0.5 * wave) ** 2.85
            valley = (0.5 - 0.5 * wave) ** 1.45
            end = np.sin(np.pi * progress) ** 0.58
            return (relief * ridge - recess * valley) * end

        sleeves.append(_surface_sleeve(radius, z0, z1, height, inner_offset=0.86))
    result = fidget.union(base, *sleeves)
    return result, {
        "feature_type": "deep torque-flute skin with narrow crests",
        "feature_count": lobe_count,
        "crest_relief_mm": relief,
        "valley_recess_mm": recess,
        "crest_to_valley_mm": relief + recess,
    }


def _radial_capsule_cutter(
    radius: float,
    theta: float,
    centre_z: float,
    length: float,
    width: float,
    tilt: float,
) -> trimesh.Trimesh:
    """A rounded slot prism crossing the full outer-shell wall radially."""
    line_half_length = (length - width) / 2.0
    tangent_run = math.sin(tilt) * line_half_length
    axial_run = math.cos(tilt) * line_half_length
    outline = LineString((
        (-tangent_run, -axial_run),
        (tangent_run, axial_run),
    )).buffer(width / 2.0, resolution=16)
    radial_start = radius - 3.20
    radial_depth = 6.40
    cutter = trimesh.creation.extrude_polygon(outline, height=radial_depth)

    er = np.array([math.cos(theta), math.sin(theta), 0.0])
    et = np.array([-math.sin(theta), math.cos(theta), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    transform = np.eye(4)
    transform[:3, 0] = et
    transform[:3, 1] = ez
    transform[:3, 2] = er
    transform[:3, 3] = er * radial_start + ez * centre_z
    cutter.apply_transform(transform)
    return cutter


def build_contour_twist_outer(source: trimesh.Trimesh, spec: PartSpec):
    """Contour the P01 outer shell and open six valleys to the P02 colour."""
    designed, feature_info = build_contour_twist(source, spec)
    z0, z1, radius = spec.zones[0]
    lobe_count = 6
    twist = 1.60
    slot_length = 19.0
    slot_width = 3.0
    # Follow the twist direction through each recessed flute.  Six restrained
    # windows expose plenty of the backing colour while leaving wide structural
    # webs and both original end-locking regions intact.
    slot_tilt = math.atan(
        radius * twist * (slot_length / (z1 - z0)) / (lobe_count * slot_length)
    )
    cutters = [
        _radial_capsule_cutter(
            radius,
            (math.pi + 2.0 * math.pi * index) / lobe_count,
            (z0 + z1) / 2.0,
            slot_length,
            slot_width,
            slot_tilt,
        )
        for index in range(lobe_count)
    ]
    result = fidget.cut(designed, *cutters)
    return result, {
        **feature_info,
        "reveal_window_type": "rounded diagonal valley slots",
        "reveal_window_count": lobe_count,
        "reveal_window_size_mm": [slot_width, slot_length],
        "assembly_role": "outer contour shell",
    }


BUILDERS = {
    "01_AeroFlow": build_aeroflow,
    "02_Vector_Chevron": build_vector_chevron,
    "03_Orbit": build_orbit,
    "04_Ergo_Scoops": build_ergo_scoops,
    "05_Contour_Twist": build_contour_twist,
}


def _canonical_stl_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Canonicalize boolean seams and make single-point contacts STL-safe."""
    manifold = Manifold(Mesh(
        vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.asarray(mesh.faces, dtype=np.uint32),
    ))
    if manifold.status() != Error.NoError:
        raise ValueError("manifold3d rejected design: %s" % manifold.status())
    canonical = manifold.to_mesh()
    vertices = np.asarray(canonical.vert_properties)[:, :3].copy()
    faces = np.asarray(canonical.tri_verts)

    raw = trimesh.Trimesh(vertices, faces, process=False)
    _, inverse, counts = np.unique(vertices, axis=0, return_inverse=True, return_counts=True)
    for group in np.flatnonzero(counts > 1):
        indices = np.flatnonzero(inverse == group)
        for order, vertex_index in enumerate(indices[1:], start=1):
            vertices[vertex_index] += raw.vertex_normals[vertex_index] * 8e-5 * order
    return trimesh.Trimesh(vertices, faces, process=True)


def _validate(
    mesh: trimesh.Trimesh,
    source: trimesh.Trimesh,
    spec: PartSpec,
    affected_radius_margin: float = 1.40,
) -> dict:
    source_radius = np.linalg.norm(source.vertices[:, :2], axis=1)
    affected = np.zeros(len(source.vertices), dtype=bool)
    for z0, z1, radius in spec.zones:
        affected |= (
            (source.vertices[:, 2] >= z0 - 0.71)
            & (source.vertices[:, 2] <= z1 + 0.71)
            & (source_radius >= radius - affected_radius_margin)
        )
    protected = source.vertices[~affected]
    _, distance, _ = trimesh.proximity.closest_point(mesh, protected)

    manifold = Manifold(Mesh(
        vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.asarray(mesh.faces, dtype=np.uint32),
    ))
    result = {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "body_count": int(mesh.body_count),
        "manifold_status": str(manifold.status()).replace("Error.", ""),
        "triangles": int(len(mesh.faces)),
        "volume_mm3": round(float(mesh.volume), 3),
        "bounds_mm": np.round(mesh.extents, 3).tolist(),
        "z_min_mm": round(float(mesh.bounds[0, 2]), 6),
        "protected_source_vertices_checked": int(len(protected)),
        "maximum_protected_surface_drift_mm": float(distance.max(initial=0.0)),
    }
    if not result["watertight"] or not result["winding_consistent"]:
        raise ValueError("%s is not a closed consistently-wound mesh" % spec.label)
    if result["body_count"] != 1:
        raise ValueError("%s has %d material bodies" % (spec.label, result["body_count"]))
    if manifold.status() != Error.NoError:
        raise ValueError("%s failed manifold validation" % spec.label)
    if abs(result["z_min_mm"]) > 1e-5:
        raise ValueError("%s moved off the print bed" % spec.label)
    if result["maximum_protected_surface_drift_mm"] > 1e-4:
        raise ValueError(
            "%s protected geometry drifted %.6f mm"
            % (spec.label, result["maximum_protected_surface_drift_mm"])
        )
    return result


def _render_preview(
    items,
    destination: Path,
    camera_position=(96.0, -120.0, 80.0),
    focal_point=(0.0, 0.0, 35.0),
    image_size=(760, 920),
) -> bool:
    try:
        import vtk
    except ImportError:
        return False

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.025, 0.032, 0.040)
    renderer.SetBackground2(0.115, 0.130, 0.145)
    renderer.GradientBackgroundOn()
    for path, position, colour in items:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(path))
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(reader.GetOutputPort())
        normals.SetFeatureAngle(48.0)
        normals.SplittingOff()
        normals.ConsistencyOn()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetPosition(*position)
        actor.GetProperty().SetColor(*colour)
        actor.GetProperty().SetInterpolationToPhong()
        actor.GetProperty().SetSpecular(0.30)
        actor.GetProperty().SetSpecularPower(30.0)
        renderer.AddActor(actor)

    for position, intensity in (((70, -90, 110), 1.0), ((-65, 30, 55), 0.48)):
        light = vtk.vtkLight()
        light.SetLightTypeToSceneLight()
        light.SetPosition(*position)
        light.SetFocalPoint(*focal_point)
        light.SetIntensity(intensity)
        renderer.AddLight(light)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(*camera_position)
    camera.SetFocalPoint(*focal_point)
    camera.SetViewUp(0.0, 0.0, 1.0)
    camera.SetViewAngle(27.0)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetMultiSamples(8)
    window.SetSize(*image_size)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(destination))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    return True


def _write_preview(mesh_paths: list[str], destination: Path) -> bool:
    offsets = (0.0, 14.1, 51.0)
    colours = ((0.19, 0.28, 0.36), (0.24, 0.38, 0.49), (0.19, 0.28, 0.36))
    items = [
        (path, (0.0, 0.0, offset), colour)
        for path, offset, colour in zip(mesh_paths, offsets, colours)
    ]
    return _render_preview(items, destination)


def _write_mesh_preview(
    mesh_items,
    destination: Path,
    camera_position=(96.0, -120.0, 80.0),
    focal_point=(0.0, 0.0, 35.0),
    image_size=(760, 920),
) -> bool:
    with tempfile.TemporaryDirectory() as temp:
        stl_items = []
        for index, (_, mesh, colour) in enumerate(mesh_items):
            path = Path(temp) / ("preview_%02d.stl" % index)
            mesh.export(path)
            stl_items.append((path, (0.0, 0.0, 0.0), colour))
        return _render_preview(
            stl_items,
            destination,
            camera_position=camera_position,
            focal_point=focal_point,
            image_size=image_size,
        )


def _coloured_scene(mesh_items) -> trimesh.Scene:
    scene = trimesh.Scene()
    for name, mesh, colour in mesh_items:
        geometry = mesh.copy()
        rgba = np.asarray([*(round(channel * 255) for channel in colour), 255], dtype=np.uint8)
        geometry.visual.face_colors = np.tile(rgba, (len(geometry.faces), 1))
        scene.add_geometry(geometry, node_name=name, geom_name=name)
    return scene


def _inject_3mf_base_materials(path: str, materials: dict[str, tuple[str, str]]) -> None:
    """Add portable object-level display materials omitted by trimesh's exporter."""
    model_path = "3D/3dmodel.model"
    with zipfile.ZipFile(path, "r") as archive:
        members = {name: archive.read(name) for name in archive.namelist()}

    core = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    root = etree.fromstring(members[model_path])
    resources = root.find("{%s}resources" % core)
    if resources is None:
        raise ValueError("3MF has no resources element")
    resource_ids = [
        int(element.get("id"))
        for element in resources
        if element.get("id") is not None
    ]
    material_id = str(max(resource_ids, default=0) + 1)
    base_materials = etree.Element("{%s}basematerials" % core, id=material_id)
    material_indices = {}
    for index, (object_name, (material_name, display_colour)) in enumerate(materials.items()):
        etree.SubElement(
            base_materials,
            "{%s}base" % core,
            name=material_name,
            displaycolor=display_colour,
        )
        material_indices[object_name] = index
    resources.insert(0, base_materials)

    matched = set()
    for object_element in resources.findall("{%s}object" % core):
        name = object_element.get("name")
        if name in material_indices:
            object_element.set("pid", material_id)
            object_element.set("pindex", str(material_indices[name]))
            matched.add(name)
    missing = set(materials) - matched
    if missing:
        raise ValueError("3MF material targets were not found: %s" % sorted(missing))

    members[model_path] = etree.tostring(
        root,
        xml_declaration=True,
        encoding="utf-8",
    )
    destination = Path(path)
    temporary = destination.with_suffix(".materials.tmp")
    with zipfile.ZipFile(
        temporary,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=5,
    ) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    os.replace(temporary, destination)


def main() -> None:
    sources = {spec.label: _prepare(spec) for spec in PARTS}
    contour_sources, contour_transforms = _prepare_contour_pair()
    manifest = {
        "description": "Professional ergonomic, unique, and modern Tactical shell designs",
        "generation": 9,
        "design_method": (
            "Analytic swept skins, staggered traction pods, thread-cut grip rails, and torque flutes; "
            "no procedural height-field grooves"
        ),
        "coordinate_system": "centred X/Y; upstream print orientation; Z minimum = 0",
        "designs": {},
    }
    validated_stl_count = 0

    for design_name, description in DESIGNS:
        builder = BUILDERS[design_name]
        record = {"description": description, "parts": {}}
        paths = []
        designed_meshes = {}
        contour_assembly_meshes = None
        for spec in PARTS:
            if design_name == "05_Contour_Twist" and spec.label == "Mid_Shell":
                outer_source = contour_sources[CONTOUR_OUTER_SPEC.label]
                outer, feature_info = build_contour_twist_outer(
                    outer_source.copy(),
                    CONTOUR_OUTER_SPEC,
                )
                outer = _canonical_stl_mesh(outer)
                outer_checks = _validate(
                    outer,
                    outer_source,
                    CONTOUR_OUTER_SPEC,
                    # The reveal windows intentionally pass through the P01
                    # wall, while the protected axial locking ends remain out
                    # of the cosmetic band and are still checked exactly.
                    affected_radius_margin=2.50,
                )
                outer_name = f"{design_name}_Mid_Shell_Outer.stl"
                outer_path = fidget.save(
                    outer,
                    outer_name,
                    subdir=os.path.join(OUTPUT_SUBDIR, design_name),
                )
                validated_stl_count += 1
                record["parts"][CONTOUR_OUTER_SPEC.label] = {
                    "file": os.path.relpath(outer_path, fidget.ROOT).replace(os.sep, "/"),
                    "source": CONTOUR_OUTER_SPEC.source,
                    "cosmetic_zones_mm": [list(zone) for zone in CONTOUR_OUTER_SPEC.zones],
                    **feature_info,
                    **outer_checks,
                }

                inner_source = contour_sources[CONTOUR_INNER_SPEC.label]
                inner = _canonical_stl_mesh(inner_source.copy())
                inner_checks = _validate(inner, inner_source, CONTOUR_INNER_SPEC)
                inner_name = f"{design_name}_Mid_Shell_Inner.stl"
                inner_path = fidget.save(
                    inner,
                    inner_name,
                    subdir=os.path.join(OUTPUT_SUBDIR, design_name),
                )
                validated_stl_count += 1
                record["parts"][CONTOUR_INNER_SPEC.label] = {
                    "file": os.path.relpath(inner_path, fidget.ROOT).replace(os.sep, "/"),
                    "source": CONTOUR_INNER_SPEC.source,
                    "cosmetic_zones_mm": [],
                    "feature_type": "unmodified nested backing shell",
                    "feature_count": 1,
                    "assembly_role": "contrasting reveal colour",
                    **inner_checks,
                }

                assembled_outer = outer.copy()
                assembled_outer.apply_transform(contour_transforms[CONTOUR_OUTER_SPEC.label])
                assembled_inner = inner.copy()
                assembled_inner.apply_transform(contour_transforms[CONTOUR_INNER_SPEC.label])
                designed_overlap = fidget.intersect(assembled_outer, assembled_inner)
                original_outer = outer_source.copy()
                original_outer.apply_transform(contour_transforms[CONTOUR_OUTER_SPEC.label])
                original_inner = inner_source.copy()
                original_inner.apply_transform(contour_transforms[CONTOUR_INNER_SPEC.label])
                original_overlap = fidget.intersect(original_outer, original_inner)
                original_overlap_volume = float(original_overlap.volume)
                designed_overlap_volume = float(designed_overlap.volume)
                contour_assembly_meshes = (assembled_outer, assembled_inner)
                record["assembly"] = {
                    "type": "original P01/P02 nested snap-fit",
                    "outer_part": CONTOUR_OUTER_SPEC.label,
                    "inner_part": CONTOUR_INNER_SPEC.label,
                    "outer_is_axially_flipped_for_assembly": True,
                    "inner_clocking_correction_degrees": CONTOUR_INNER_CLOCKING_DEGREES,
                    "equivalent_clocking_period_degrees": 120.0,
                    "original_nested_overlap_mm3": round(original_overlap_volume, 6),
                    "designed_nested_overlap_mm3": round(designed_overlap_volume, 6),
                    "nested_overlap_change_mm3": round(
                        designed_overlap_volume - original_overlap_volume,
                        6,
                    ),
                }
                continue

            designed, feature_info = builder(sources[spec.label].copy(), spec)
            designed = _canonical_stl_mesh(designed)
            checks = _validate(designed, sources[spec.label], spec)
            filename = f"{design_name}_{spec.label}.stl"
            path = fidget.save(
                designed,
                filename,
                subdir=os.path.join(OUTPUT_SUBDIR, design_name),
            )
            validated_stl_count += 1
            paths.append(path)
            designed_meshes[spec.label] = designed
            record["parts"][spec.label] = {
                "file": os.path.relpath(path, fidget.ROOT).replace(os.sep, "/"),
                "source": spec.source,
                "cosmetic_zones_mm": [list(zone) for zone in spec.zones],
                **feature_info,
                **checks,
            }

        output_dir = Path(fidget.DERIVATIVES) / OUTPUT_SUBDIR / design_name
        preview = output_dir / "preview.png"
        if design_name == "05_Contour_Twist":
            if contour_assembly_meshes is None:
                raise ValueError("Contour Twist two-piece mid-shell was not built")
            assembled_outer, assembled_inner = contour_assembly_meshes
            bottom_colour = (0.30, 0.43, 0.23)
            outer_colour = (0.24, 0.38, 0.49)
            accent_colour = (0.94, 0.31, 0.055)
            upper_colour = (0.48, 0.25, 0.50)

            bottom = designed_meshes["Bottom_Shell"].copy()
            outer_for_preview = assembled_outer.copy()
            outer_for_preview.apply_translation((0.0, 0.0, 14.1))
            inner_for_preview = assembled_inner.copy()
            inner_for_preview.apply_translation((0.0, 0.0, 14.1))
            upper = designed_meshes["Upper_Shell_Top"].copy()
            upper.apply_translation((0.0, 0.0, 51.0))
            presentation = (
                ("Bottom_Shell", bottom, bottom_colour),
                ("Mid_Shell_Inner", inner_for_preview, accent_colour),
                ("Mid_Shell_Outer", outer_for_preview, outer_colour),
                ("Upper_Shell_Top", upper, upper_colour),
            )
            if _write_mesh_preview(presentation, preview):
                record["preview"] = str(preview.relative_to(fidget.ROOT)).replace(os.sep, "/")
                print("wrote %s" % preview.relative_to(fidget.ROOT))

            closeup = output_dir / "two_colour_mid_shell_preview.png"
            mid_shell_items = (
                ("Mid_Shell_Inner", assembled_inner, accent_colour),
                ("Mid_Shell_Outer", assembled_outer, outer_colour),
            )
            if _write_mesh_preview(
                mid_shell_items,
                closeup,
                camera_position=(72.0, -90.0, 48.0),
                focal_point=(0.0, 0.0, 17.0),
                image_size=(760, 760),
            ):
                record["assembly"]["preview"] = str(
                    closeup.relative_to(fidget.ROOT)
                ).replace(os.sep, "/")
                print("wrote %s" % closeup.relative_to(fidget.ROOT))

            assembly_name = f"{design_name}_Mid_Shell_2Color_Assembly.3mf"
            assembly_scene = _coloured_scene(mid_shell_items)
            assembly_path = fidget.save(
                assembly_scene,
                assembly_name,
                subdir=os.path.join(OUTPUT_SUBDIR, design_name),
            )
            material_intent = {
                "Mid_Shell_Inner": ("Contrasting reveal colour", "#F04F0EFF"),
                "Mid_Shell_Outer": ("Main contour shell colour", "#3D617DFF"),
            }
            _inject_3mf_base_materials(assembly_path, material_intent)
            record["assembly"]["file"] = os.path.relpath(
                assembly_path,
                fidget.ROOT,
            ).replace(os.sep, "/")
            record["assembly"]["materials"] = {
                name: {"name": material[0], "display_colour": material[1]}
                for name, material in material_intent.items()
            }

            glb_name = f"{design_name}_Mid_Shell_2Color_Assembly.glb"
            glb_path = fidget.save(
                assembly_scene,
                glb_name,
                subdir=os.path.join(OUTPUT_SUBDIR, design_name),
            )
            record["assembly"]["visual_reference_file"] = os.path.relpath(
                glb_path,
                fidget.ROOT,
            ).replace(os.sep, "/")

            full_glb_name = f"{design_name}_Full_Shell_Assembly.glb"
            full_glb_path = fidget.save(
                _coloured_scene(presentation),
                full_glb_name,
                subdir=os.path.join(OUTPUT_SUBDIR, design_name),
            )
            record["assembly"]["full_shell_glb"] = os.path.relpath(
                full_glb_path,
                fidget.ROOT,
            ).replace(os.sep, "/")
            record["assembly"]["full_shell_glb_part_colours"] = {
                "Bottom_Shell": "#4C6E3BFF",
                "Mid_Shell_Inner": "#F04F0EFF",
                "Mid_Shell_Outer": "#3D617DFF",
                "Upper_Shell_Top": "#7A4080FF",
            }

            obsolete = output_dir / f"{design_name}_Mid_Shell.stl"
            if obsolete.exists():
                obsolete.unlink()
                print("removed obsolete %s" % obsolete.relative_to(fidget.ROOT))
        elif _write_preview(paths, preview):
            record["preview"] = str(preview.relative_to(fidget.ROOT)).replace(os.sep, "/")
            print("wrote %s" % preview.relative_to(fidget.ROOT))
        manifest["designs"][design_name] = record

    output = Path(fidget.DERIVATIVES) / OUTPUT_SUBDIR
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("wrote %s" % manifest_path.relative_to(fidget.ROOT))
    print("validated %d professional STL files" % validated_stl_count)


if __name__ == "__main__":
    main()
