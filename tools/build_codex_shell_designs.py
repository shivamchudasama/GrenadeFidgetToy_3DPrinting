"""Build five coordinated cosmetic shell sets for the Tactical Fidget Fuse.

The upstream STLs are print meshes rather than CAD.  These variants therefore
decorate only outward-facing exterior vertices and leave all inward-facing
snap, bearing, and spring interfaces byte-for-byte positioned.  Every output is
centred on X/Y and kept at Z=0 in the upstream print orientation.

Usage:
    python tools/build_codex_shell_designs.py

Output:
    Derivatives/Codex_Shell_Designs/<design>/*.stl
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
import os
from pathlib import Path

from manifold3d import Error, Manifold, Mesh
import numpy as np
import trimesh

import fidget


OUTPUT_SUBDIR = "Codex_Shell_Designs"
MANIFEST_NAME = "manifest.json"


@dataclass(frozen=True)
class PartSpec:
    label: str
    source: str
    # Cosmetic bands as (z_min, z_max, finished outer radius), in print pose.
    zones: tuple[tuple[float, float, float], ...]


PARTS = (
    PartSpec("Bottom_Shell", "04 - Bottom Shell 01", ((3.60, 9.50, 19.35),)),
    PartSpec("Mid_Shell", "Mid Shell Solid Color", ((2.60, 32.20, 20.00),)),
    # The 18.5 mm upper neck is an external functional interface, so only the
    # broad 40 mm skirt receives decoration.
    PartSpec("Upper_Shell_Top", "27 - Upper Shell Top", ((4.10, 11.35, 19.70),)),
)


DESIGNS = (
    ("01_Diamond_Grip", "Crossed 45-degree grip grooves", 0.62),
    ("02_Spiral_Ribs", "Eight sweeping helical grip channels", 0.68),
    ("03_Dragon_Scales", "Layered scalloped scale lines", 0.56),
    ("04_Dimple_Field", "Staggered tactile dimples", 0.72),
    ("05_Armor_Panels", "Staggered plate seams and recessed bolt marks", 0.60),
)


def _smoothstep(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def _line_profile(phase: np.ndarray, half_width: float) -> np.ndarray:
    """Smooth groove centred on every integer multiple of 2*pi."""
    distance = np.abs(np.arctan2(np.sin(phase), np.cos(phase)))
    return _smoothstep(1.0 - distance / half_width)


def _periodic_distance(value: np.ndarray, period: float) -> np.ndarray:
    """Unsigned distance to the nearest multiple of ``period``."""
    return np.abs((value + period / 2.0) % period - period / 2.0)


def diamond_grip(theta: np.ndarray, z: np.ndarray, radius: float) -> np.ndarray:
    del radius
    turns = 9
    pitch = 8.5
    forward = _line_profile(turns * theta + 2.0 * np.pi * z / pitch, 0.33)
    reverse = _line_profile(turns * theta - 2.0 * np.pi * z / pitch, 0.33)
    return np.maximum(forward, reverse)


def spiral_ribs(theta: np.ndarray, z: np.ndarray, radius: float) -> np.ndarray:
    del radius
    phase = 8 * theta - 2.0 * np.pi * z / 18.0
    core = _line_profile(phase, 0.52)
    # A broad shoulder makes the ribs tactile instead of knife-edged.
    shoulder = 0.32 * _line_profile(phase, 0.92)
    return np.maximum(core, shoulder)


def dragon_scales(theta: np.ndarray, z: np.ndarray, radius: float) -> np.ndarray:
    del radius
    pitch = 5.4
    amplitude = 1.75
    z0 = float(z.min()) - pitch
    z1 = float(z.max()) + pitch
    values = np.zeros_like(z)
    for row in range(int(math.floor((z1 - z0) / pitch)) + 1):
        baseline = z0 + row * pitch
        phase = 10 * theta + (row % 2) * np.pi
        curve = baseline + amplitude * (0.5 - 0.5 * np.cos(phase))
        values = np.maximum(values, _smoothstep(1.0 - np.abs(z - curve) / 0.52))
    return values


def dimple_field(theta: np.ndarray, z: np.ndarray, radius: float) -> np.ndarray:
    rows = 6.0
    angular_count = 12
    z0 = float(z.min()) - rows
    z1 = float(z.max()) + rows
    values = np.zeros_like(z)
    for row in range(int(math.floor((z1 - z0) / rows)) + 1):
        centre_z = z0 + row * rows
        offset = (row % 2) * np.pi
        phase = angular_count * theta + offset
        angular_distance = np.abs(np.arctan2(np.sin(phase), np.cos(phase)))
        arc_distance = radius * angular_distance / angular_count
        distance_sq = (arc_distance / 2.15) ** 2 + ((z - centre_z) / 2.05) ** 2
        pocket = np.where(distance_sq < 1.0, (1.0 - distance_sq) ** 2, 0.0)
        values = np.maximum(values, pocket)
    return values


def armor_panels(theta: np.ndarray, z: np.ndarray, radius: float) -> np.ndarray:
    del radius
    height = 8.0
    row = np.floor((z - float(z.min())) / height).astype(int)
    horizontal = _smoothstep(1.0 - _periodic_distance(z - float(z.min()), height) / 0.58)
    vertical_phase = 10 * theta + (row % 2) * np.pi
    vertical = _line_profile(vertical_phase, 0.27)
    # Hide the row-to-row phase jump inside each horizontal seam.
    vertical *= _smoothstep(_periodic_distance(z - float(z.min()), height) / 1.15)

    bolt_phase = 10 * theta + (row % 2) * np.pi - np.pi
    bolt_arc = np.abs(np.arctan2(np.sin(bolt_phase), np.cos(bolt_phase))) / 10.0
    bolt_z = _periodic_distance(z - float(z.min()) - height / 2.0, height)
    bolt_dist_sq = (bolt_arc / 0.075) ** 2 + (bolt_z / 0.78) ** 2
    bolts = np.where(bolt_dist_sq < 1.0, (1.0 - bolt_dist_sq) ** 2, 0.0)
    return np.maximum.reduce((horizontal, vertical, 0.78 * bolts))


PATTERNS = {
    "01_Diamond_Grip": diamond_grip,
    "02_Spiral_Ribs": spiral_ribs,
    "03_Dragon_Scales": dragon_scales,
    "04_Dimple_Field": dimple_field,
    "05_Armor_Panels": armor_panels,
}


def _prepare(spec: PartSpec) -> trimesh.Trimesh:
    mesh = fidget.load(spec.source, product="tactical").copy()
    centre_xy = mesh.bounds[:, :2].mean(axis=0)
    z_min = float(mesh.bounds[0, 2])
    mesh.apply_translation((-centre_xy[0], -centre_xy[1], -z_min))
    return mesh


def _radial_cage(height: float, z0: float, z1: float, radius: float) -> trimesh.Trimesh:
    """Solid of revolution which trims one band and leaves its ends untouched."""
    transition = min(0.75, (z1 - z0) / 4.0)
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
    return trimesh.creation.revolve(profile, sections=192)


def smooth_exterior(mesh: trimesh.Trimesh, spec: PartSpec) -> trimesh.Trimesh:
    """Remove existing raised decoration inside the explicitly safe bands."""
    result = mesh.copy()
    height = float(mesh.extents[2])
    for z0, z1, radius in spec.zones:
        result = fidget.intersect(result, _radial_cage(height, z0, z1, radius))
    if not result.is_watertight or result.body_count != 1:
        raise ValueError("failed to make a clean exterior base for %s" % spec.label)
    return result


def _texture_cutter(z0: float, z1: float, radius: float, pattern, depth: float):
    """A closed annular CSG cutter with a pattern-shaped inner surface."""
    # Around a 40 mm shell this is ~0.39 mm circumferential spacing, matching a
    # common FDM nozzle and keeping diagonal/curved groove edges visually clean.
    theta_count = 320
    z_count = max(24, int(math.ceil((z1 - z0) / 0.28)) + 1)
    theta = np.arange(theta_count, dtype=float) * (2.0 * np.pi / theta_count)
    z = np.linspace(z0, z1, z_count)
    tt, zz = np.meshgrid(theta, z)
    texture = np.clip(pattern(tt.ravel(), zz.ravel(), radius), 0.0, 1.0).reshape(tt.shape)
    edge_gate = (
        _smoothstep((zz - z0) / 0.55)
        * _smoothstep((z1 - zz) / 0.55)
    )
    texture *= edge_gate

    # At texture=0 the cutter starts 0.06 mm outside the finished skin. At
    # texture=1 it enters by depth-0.06, giving a robust boolean without a
    # coincident-surface ambiguity.
    inner_radius = radius + 0.06 - depth * texture
    outer_radius = np.full_like(inner_radius, radius + 1.50)

    vertices = []
    for radii in (inner_radius, outer_radius):
        vertices.append(np.column_stack((
            (radii * np.cos(tt)).ravel(),
            (radii * np.sin(tt)).ravel(),
            zz.ravel(),
        )))
    vertices = np.vstack(vertices)
    layer_size = theta_count * z_count

    def idx(side: int, row: int, column: int) -> int:
        return side * layer_size + row * theta_count + column % theta_count

    faces = []
    for row in range(z_count - 1):
        for column in range(theta_count):
            nxt = column + 1
            # Inner wall: winding faces the annular material (radially inward).
            i00, i01 = idx(0, row, column), idx(0, row, nxt)
            i10, i11 = idx(0, row + 1, column), idx(0, row + 1, nxt)
            faces.extend(((i00, i11, i01), (i00, i10, i11)))
            # Outer wall: winding faces radially outward.
            o00, o01 = idx(1, row, column), idx(1, row, nxt)
            o10, o11 = idx(1, row + 1, column), idx(1, row + 1, nxt)
            faces.extend(((o00, o01, o11), (o00, o11, o10)))

    for column in range(theta_count):
        nxt = column + 1
        # Bottom and top annular caps.
        ib, ibn = idx(0, 0, column), idx(0, 0, nxt)
        ob, obn = idx(1, 0, column), idx(1, 0, nxt)
        faces.extend(((ib, ibn, obn), (ib, obn, ob)))
        it, itn = idx(0, z_count - 1, column), idx(0, z_count - 1, nxt)
        ot, otn = idx(1, z_count - 1, column), idx(1, z_count - 1, nxt)
        faces.extend(((it, otn, itn), (it, ot, otn)))

    cutter = trimesh.Trimesh(np.asarray(vertices), np.asarray(faces), process=True)
    if not cutter.is_watertight or not cutter.is_winding_consistent:
        raise ValueError("generated texture cutter is not a valid closed solid")
    return cutter


def decorate(mesh: trimesh.Trimesh, spec: PartSpec, pattern, depth: float):
    """Recess a true manifold pattern into each safe exterior zone."""
    result = mesh.copy()
    cutter_triangles = 0
    for z0, z1, radius in spec.zones:
        cutter = _texture_cutter(z0, z1, radius, pattern, depth)
        cutter_triangles += len(cutter.faces)
        result = fidget.cut(result, cutter)
        if result.body_count != 1:
            components = result.split(only_watertight=False)
            components.sort(key=lambda item: abs(float(item.volume)), reverse=True)
            debris = components[1:]
            if any(abs(float(item.volume)) > 1e-6 or len(item.faces) > 4 for item in debris):
                raise ValueError(
                    "%s texture cut created %d material bodies"
                    % (spec.label, result.body_count)
                )
            # Manifold can occasionally return a four-triangle, zero-volume
            # coincident sliver. It is not printable material; remove it now.
            result = components[0]
    # Trimesh's manifold adapter can retain coincident seam vertices as
    # separate indexed vertices. STL has no vertex index, so a reload welds
    # those coordinates and exposes non-manifold 4-way edges. A round trip
    # through manifold3d's canonical mesh removes those redundant seams before
    # serialization, making the on-disk STL independently watertight too.
    canonical = Manifold(Mesh(
        vert_properties=np.asarray(result.vertices, dtype=np.float32),
        tri_verts=np.asarray(result.faces, dtype=np.uint32),
    )).to_mesh()
    canonical_vertices = np.asarray(canonical.vert_properties)[:, :3].copy()
    canonical_faces = np.asarray(canonical.tri_verts)

    # A boolean can end with two closed surface sheets touching at exactly one
    # coordinate. Indexed meshes keep those vertices separate, while STL reload
    # welding would turn the contact into a non-manifold 4-way edge. Separate
    # only such duplicate-coordinate vertices by 0.00008 mm along their own
    # normals: far below printer resolution, but explicit in float32 STL.
    raw = trimesh.Trimesh(canonical_vertices, canonical_faces, process=False)
    _, inverse, counts = np.unique(
        canonical_vertices, axis=0, return_inverse=True, return_counts=True
    )
    for group in np.flatnonzero(counts > 1):
        indices = np.flatnonzero(inverse == group)
        for order, vertex_index in enumerate(indices[1:], start=1):
            canonical_vertices[vertex_index] += (
                raw.vertex_normals[vertex_index] * 8e-5 * order
            )
    result = trimesh.Trimesh(canonical_vertices, canonical_faces, process=True)
    return result, {
        "maximum_recess_mm": depth - 0.06,
        "cosmetic_zones_mm": [list(zone) for zone in spec.zones],
        "cutter_triangles": int(cutter_triangles),
    }


def validate(mesh: trimesh.Trimesh, source: trimesh.Trimesh, spec: PartSpec, depth: float) -> dict:
    manifold = Manifold(Mesh(
        vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.asarray(mesh.faces, dtype=np.uint32),
    ))
    status = manifold.status()
    source_radius = np.linalg.norm(source.vertices[:, :2], axis=1)
    affected = np.zeros(len(source.vertices), dtype=bool)
    for z0, z1, radius in spec.zones:
        affected |= (
            (source.vertices[:, 2] >= z0 - 0.76)
            & (source.vertices[:, 2] <= z1 + 0.76)
            & (source_radius >= radius - depth - 0.08)
        )
    protected_points = source.vertices[~affected]
    _, protected_distance, _ = trimesh.proximity.closest_point(mesh, protected_points)

    checks = {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "body_count": int(mesh.body_count),
        "manifold_status": str(status).replace("Error.", ""),
        "triangles": int(len(mesh.faces)),
        "volume_mm3": round(float(mesh.volume), 3),
        "volume_change_mm3": round(float(mesh.volume - source.volume), 3),
        "bounds_mm": np.round(mesh.extents, 3).tolist(),
        "z_min_mm": round(float(mesh.bounds[0, 2]), 6),
        "protected_source_vertices_checked": int(len(protected_points)),
        "maximum_protected_surface_drift_mm": float(protected_distance.max(initial=0.0)),
    }
    if not checks["watertight"]:
        raise ValueError("decorated mesh is not watertight")
    if not checks["winding_consistent"]:
        raise ValueError("decorated mesh has inconsistent winding")
    if checks["body_count"] != 1:
        raise ValueError("decorated mesh has %d bodies" % checks["body_count"])
    if status != Error.NoError:
        raise ValueError("manifold3d rejected decorated mesh: %s" % status)
    if abs(checks["z_min_mm"]) > 1e-5:
        raise ValueError("decorated mesh moved off the print bed")
    if checks["maximum_protected_surface_drift_mm"] > 1e-4:
        raise ValueError(
            "protected surface moved by %.6f mm"
            % checks["maximum_protected_surface_drift_mm"]
        )
    return checks


def write_preview(mesh_paths: list[str], destination: Path) -> bool:
    """Render a small assembled-style PNG when the optional VTK stack exists."""
    try:
        import vtk
    except ImportError:
        print("VTK is unavailable; skipped preview %s" % destination.name)
        return False

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.035, 0.045, 0.055)
    renderer.SetBackground2(0.13, 0.15, 0.16)
    renderer.GradientBackgroundOn()

    # Bottom, mid, and upper parts are shown in assembly order with small gaps.
    z_offsets = (0.0, 14.3, 51.2)
    colours = ((0.28, 0.39, 0.19), (0.34, 0.47, 0.22), (0.28, 0.39, 0.19))
    for path, offset, colour in zip(mesh_paths, z_offsets, colours):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(path)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetPosition(0.0, 0.0, offset)
        actor.GetProperty().SetColor(*colour)
        actor.GetProperty().SetInterpolationToPhong()
        actor.GetProperty().SetSpecular(0.22)
        actor.GetProperty().SetSpecularPower(24.0)
        renderer.AddActor(actor)

    key = vtk.vtkLight()
    key.SetLightTypeToSceneLight()
    key.SetPosition(65.0, -85.0, 105.0)
    key.SetFocalPoint(0.0, 0.0, 35.0)
    key.SetIntensity(1.0)
    renderer.AddLight(key)
    fill = vtk.vtkLight()
    fill.SetLightTypeToSceneLight()
    fill.SetPosition(-60.0, 35.0, 55.0)
    fill.SetFocalPoint(0.0, 0.0, 35.0)
    fill.SetIntensity(0.55)
    renderer.AddLight(fill)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(96.0, -118.0, 82.0)
    camera.SetFocalPoint(0.0, 0.0, 36.0)
    camera.SetViewUp(0.0, 0.0, 1.0)
    camera.SetViewAngle(27.0)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetMultiSamples(8)
    window.SetSize(720, 900)
    window.AddRenderer(renderer)
    window.Render()

    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetScale(1)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(destination))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    print("wrote %s" % destination.relative_to(fidget.ROOT))
    return True


def main() -> None:
    sources = {spec.label: _prepare(spec) for spec in PARTS}
    bases = {spec.label: smooth_exterior(sources[spec.label], spec) for spec in PARTS}
    manifest = {
        "description": "Five coordinated cosmetic shell sets for the Tactical Fidget Fuse",
        "coordinate_system": "centred X/Y; upstream print orientation; Z minimum = 0",
        "interface_policy": (
            "Only outward-facing exterior vertices are recessed. Inward-facing mating "
            "surfaces and protected top/bottom interface bands are unchanged."
        ),
        "designs": {},
    }

    for design_name, description, depth in DESIGNS:
        pattern = PATTERNS[design_name]
        preview_paths = []
        design_record = {
            "description": description,
            "nominal_maximum_recess_mm": depth,
            "parts": {},
        }
        for spec in PARTS:
            source = sources[spec.label]
            decorated, stats = decorate(bases[spec.label], spec, pattern, depth)
            checks = validate(decorated, source, spec, depth)
            filename = f"{design_name}_{spec.label}.stl"
            destination = fidget.save(
                decorated,
                filename,
                subdir=os.path.join(OUTPUT_SUBDIR, design_name),
            )
            preview_paths.append(destination)
            design_record["parts"][spec.label] = {
                "file": os.path.relpath(destination, fidget.ROOT).replace(os.sep, "/"),
                "source": spec.source,
                **stats,
                **checks,
            }
        preview_path = Path(fidget.DERIVATIVES) / OUTPUT_SUBDIR / design_name / "preview.png"
        if write_preview(preview_paths, preview_path):
            design_record["preview"] = str(preview_path.relative_to(fidget.ROOT)).replace(os.sep, "/")
        manifest["designs"][design_name] = design_record

    output_dir = Path(fidget.DERIVATIVES) / OUTPUT_SUBDIR
    manifest_path = output_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("wrote %s" % manifest_path.relative_to(fidget.ROOT))
    print("validated %d printable STL files" % (len(DESIGNS) * len(PARTS)))


if __name__ == "__main__":
    main()
