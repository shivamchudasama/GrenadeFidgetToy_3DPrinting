"""
Build and standardize the 2-Piece Split Mid Shell Architecture across all options in Hybrid_Grenade_v1.3.

Converts all mid shells (01 AeroFlow, 02 Vector Chevron, 03 Orbit,
04 Ergo Scoops, 05 Contour Twist, 06 Hex Tactical, 07 Classic Solid Tactical) into standardized
2-piece assemblies matching Baseline (P01 Outer + P02 Ratchet):
  - Inner Ratchet Core (07_..._Inner.stl / 07_32_Mid_Shell_P02_Ratchet.stl): PETG for high click endurance against the waist spring
  - Outer Shell Sleeve (08_..._Outer.stl): PLA Matte for aesthetic custom finishes, with through-window openings
    exposing the contrasting inner ratchet in a striking two-colour design.

Outputs are saved to:
  - 02_Waist_Mechanism/Mid_Shell_Options/
  - All_Parts_Flat_Bed_Oriented/Mid_Shell_Options/
  - All_Parts_Assembled_Coordinates/Mid_Shell_Options/
  - Plates_3MF/
"""

import math
import os
import shutil
import sys
import numpy as np
from shapely.geometry import LineString, Polygon, box
import scipy.sparse as sp
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import assembly as A
import build_shell_variants_glbs as B
import fidget

REPO_ROOT = os.path.dirname(TOOLS_DIR)
PACKAGE_DIR = os.path.join(REPO_ROOT, "Hybrid_Grenade_v1.3")
V12_DIR = os.path.join(REPO_ROOT, "Hybrid_Grenade_v1.2")
WAIST_DIR = os.path.join(PACKAGE_DIR, "02_Waist_Mechanism")
OPTIONS_DIR = os.path.join(WAIST_DIR, "Mid_Shell_Options")
FLAT_DIR = os.path.join(PACKAGE_DIR, "All_Parts_Flat_Bed_Oriented", "Mid_Shell_Options")
ASSEM_DIR = os.path.join(PACKAGE_DIR, "All_Parts_Assembled_Coordinates", "Mid_Shell_Options")
PLATES_DIR = os.path.join(PACKAGE_DIR, "Plates_3MF")

# Color palette for 2-color assembly scenes (RGB 0.0 .. 1.0)
PETG_INNER_COLOUR = (0.94, 0.35, 0.08)    # Safety Orange PETG
PLA_OUTER_COLOUR = (0.28, 0.36, 0.28)     # Tactical Olive PLA Matte


def create_bore_cutter(p01_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Extract and build the certified Manifold boolean cutter from P01."""
    # 1. Flange pass-through bore (Z = 0.4 mm)
    sl_flange = p01_mesh.section(plane_origin=[0, 0, 0.4], plane_normal=[0, 0, 1])
    poly_flange = Polygon(sl_flange.to_2D()[0].polygons_full[0].interiors[0].coords)

    # 2. 3-Pocket anti-rotation keyway zone (Z = 1.8 mm)
    sl_pocket = p01_mesh.section(plane_origin=[0, 0, 1.8], plane_normal=[0, 0, 1])
    poly_pocket = Polygon(sl_pocket.to_2D()[0].polygons_full[0].interiors[0].coords)

    # 3. Main cylindrical bore (Z = 34.5 mm)
    sl_bore = p01_mesh.section(plane_origin=[0, 0, 34.5], plane_normal=[0, 0, 1])
    poly_bore = Polygon(sl_bore.to_2D()[0].polygons_full[0].interiors[0].coords)

    m_flange = trimesh.creation.extrude_polygon(poly_flange, height=1.8).apply_translation([0, 0, -1.0])
    m_pocket = trimesh.creation.extrude_polygon(poly_pocket, height=2.2).apply_translation([0, 0, 0.8])
    m_bore = trimesh.creation.extrude_polygon(poly_bore, height=33.0).apply_translation([0, 0, 3.0])

    cutter = fidget.union(m_flange, m_pocket, m_bore)
    assert cutter.is_watertight, "Bore cutter must be watertight"
    return cutter


def make_radial_capsule_cutter(
    theta_center: float,
    z0: float,
    z1: float,
    width: float,
    radius: float = 19.5,
    radial_in: float = 16.0,
    radial_out: float = 23.0,
) -> trimesh.Trimesh:
    """Build a straight vertical capsule cutter at theta_center."""
    pts = [(0.0, z0), (0.0, z1)]
    ls = LineString(pts)
    poly = ls.buffer(width / 2.0, resolution=12)
    cutter2d = trimesh.creation.extrude_polygon(poly, height=(radial_out - radial_in))

    er = np.array([math.cos(theta_center), math.sin(theta_center), 0.0])
    et = np.array([-math.sin(theta_center), math.cos(theta_center), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    transform = np.eye(4)
    transform[:3, 0] = et
    transform[:3, 1] = ez
    transform[:3, 2] = er
    transform[:3, 3] = er * radial_in
    cutter2d.apply_transform(transform)
    return cutter2d


def make_swept_path_cutter(
    theta_center: float,
    z_vals: np.ndarray,
    d_theta: np.ndarray,
    width: float,
    radius: float = 19.5,
    radial_in: float = 15.0,
    radial_out: float = 23.5,
) -> trimesh.Trimesh:
    """Build a swept curved capsule cutter following d_theta along z_vals."""
    tangent_offsets = radius * d_theta
    pts = list(zip(tangent_offsets, z_vals))
    ls = LineString(pts)
    poly = ls.buffer(width / 2.0, resolution=12)
    cutter2d = trimesh.creation.extrude_polygon(poly, height=(radial_out - radial_in))

    er = np.array([math.cos(theta_center), math.sin(theta_center), 0.0])
    et = np.array([-math.sin(theta_center), math.cos(theta_center), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    transform = np.eye(4)
    transform[:3, 0] = et
    transform[:3, 1] = ez
    transform[:3, 2] = er
    transform[:3, 3] = er * radial_in
    cutter2d.apply_transform(transform)
    return cutter2d


def make_hex_cutter(
    theta_center: float,
    z_center: float,
    hex_radius: float = 2.85,
    radial_in: float = 15.0,
    radial_out: float = 23.5,
) -> trimesh.Trimesh:
    """Build a regular hexagonal prism cutter extruded radially, oriented point-to-point along Z."""
    angles = np.radians([90, 150, 210, 270, 330, 30])
    poly_pts = [(hex_radius * np.cos(a), z_center + hex_radius * np.sin(a)) for a in angles]
    poly = Polygon(poly_pts)
    cutter2d = trimesh.creation.extrude_polygon(poly, height=(radial_out - radial_in))

    er = np.array([math.cos(theta_center), math.sin(theta_center), 0.0])
    et = np.array([-math.sin(theta_center), math.cos(theta_center), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    transform = np.eye(4)
    transform[:3, 0] = et
    transform[:3, 1] = ez
    transform[:3, 2] = er
    transform[:3, 3] = er * radial_in
    cutter2d.apply_transform(transform)
    return cutter2d


def make_stadium_dot_cutter(
    theta_center: float,
    z_center: float,
    width: float = 2.095,
    height: float = 1.468,
    corner_radius: float = 0.50,
    radial_in: float = 15.0,
    radial_out: float = 23.5,
    resolution: int = 16,
) -> trimesh.Trimesh:
    """Build a rounded-rectangle / stadium cutter matching 50% scale of the original Orbit dots."""
    dx = (width / 2.0) - corner_radius
    dy = (height / 2.0) - corner_radius
    poly = box(-dx, z_center - dy, dx, z_center + dy).buffer(corner_radius, resolution=resolution)
    cutter2d = trimesh.creation.extrude_polygon(poly, height=(radial_out - radial_in))

    er = np.array([math.cos(theta_center), math.sin(theta_center), 0.0])
    et = np.array([-math.sin(theta_center), math.cos(theta_center), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    transform = np.eye(4)
    transform[:3, 0] = et
    transform[:3, 1] = ez
    transform[:3, 2] = er
    transform[:3, 3] = er * radial_in
    cutter2d.apply_transform(transform)
    return cutter2d


def smoothen_orbit_mesh(flipped_mesh: trimesh.Trimesh, iterations: int = 25) -> trimesh.Trimesh:
    """Apply continuous Taubin smoothing to the outer pods of the Orbit shell to remove facet pixelation."""
    v = flipped_mesh.vertices.copy()
    r = np.hypot(v[:, 0], v[:, 1])
    z = v[:, 2]

    edges = flipped_mesh.edges_unique
    n_verts = len(v)
    adj = sp.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(n_verts, n_verts))
    adj = adj + adj.T
    deg = np.array(adj.sum(axis=1)).flatten()
    deg[deg == 0] = 1.0
    inv_deg = sp.diags(1.0 / deg)

    # Outer surface with pods (avoid modifying top and bottom rims at z<3.0 and z>31.8)
    mask = (r > 19.90) & (z > 3.0) & (z < 31.8)
    lamb = 0.5
    nu = -0.53

    v_curr = v.copy()
    for _ in range(iterations):
        neighbor_avg = inv_deg.dot(adj.dot(v_curr))
        v_curr[mask] += lamb * (neighbor_avg - v_curr)[mask]
        neighbor_avg = inv_deg.dot(adj.dot(v_curr))
        v_curr[mask] += nu * (neighbor_avg - v_curr)[mask]

    # Project any vertices on the base cylinder that drifted inward back to r = 20.00 mm
    r_curr = np.hypot(v_curr[:, 0], v_curr[:, 1])
    below_base = mask & (r_curr < 20.00)
    scale = 20.00 / np.maximum(r_curr[below_base], 1e-6)
    v_curr[below_base, 0] *= scale
    v_curr[below_base, 1] *= scale

    return trimesh.Trimesh(vertices=v_curr, faces=flipped_mesh.faces)


def generate_window_cutters(variant_id: str) -> list[trimesh.Trimesh]:
    """Generate aesthetic through-window cutters for each shell variant."""
    cutters = []

    if variant_id == "01":
        # 01_AeroFlow: 16 swept ribbon slots following inter-rib aerodynamic valleys
        count = 16
        z0, z1 = 4.5, 30.3
        width = 1.8
        radius = 19.5
        z_vals = np.linspace(z0, z1, 35)
        prog = (33.55 - z_vals) / 32.30
        d_theta = -(0.30 * (prog - 0.5) + 0.045 * np.sin(2.0 * np.pi * (prog - 0.5)))
        for k in range(count):
            theta_center = (k + 0.5) * 2.0 * np.pi / count
            cutters.append(make_swept_path_cutter(theta_center, z_vals, d_theta, width, radius))

    elif variant_id == "02":
        # 02_Vector_Chevron: 16 chevron-angled slots following the continuous V-angle
        count = 16
        z0, z1 = 4.5, 30.3
        width = 1.8
        radius = 19.5
        z_vals = np.linspace(z0, z1, 45)
        prog = (33.55 - z_vals) / 32.30
        centred = 2.0 * prog - 1.0
        soft_v = np.sqrt(centred * centred + 0.038) - math.sqrt(0.038)
        d_theta = -0.20 * soft_v
        for k in range(count):
            theta_center = (k + 0.5) * 2.0 * np.pi / count
            cutters.append(make_swept_path_cutter(theta_center, z_vals, d_theta, width, radius))

    elif variant_id == "03":
        # 03_Orbit: 60 equal-shaped, 50%-sized rounded-rectangle / stadium dot cutouts
        # Original dots: width = 4.19 mm, height = 2.94 mm, corner radius = 1.0 mm.
        # 50%-sized cutouts: width = 2.095 mm, height = 1.468 mm, corner radius = 0.50 mm.
        # 5 tiers of 12 cutouts placed in the checkerboard gaps between original dots (+0.05 deg coplanarity offset):
        tiers = [
            (8.56, 0.05),    # Tier 1
            (12.91, 15.05),  # Tier 2
            (17.45, 0.05),   # Tier 3 (Middle)
            (21.81, 15.05),  # Tier 4
            (26.30, 0.05),   # Tier 5
        ]
        for z_c, th_base_deg in tiers:
            th_base = np.radians(th_base_deg)
            for k in range(12):
                th_k = th_base + k * (2.0 * np.pi / 12.0)
                cutters.append(make_stadium_dot_cutter(th_k, z_c, width=2.095, height=1.468, corner_radius=0.50))

    elif variant_id == "04":
        # 04_Ergo_Scoops: 12 vertical capsule slots between rails (+0.2 deg offset to break vertex coplanarity)
        count = 12
        z0, z1 = 4.8, 30.0
        width = 2.0
        for k in range(count):
            theta_center = (k + 0.5) * 2.0 * np.pi / count + math.radians(0.2)
            cutters.append(make_radial_capsule_cutter(theta_center, z0, z1, width))

    elif variant_id == "05":
        # 05_Contour_Twist: already has 6 twisted capsule windows baked in
        pass

    elif variant_id == "06":
        # 06_Hex_Tactical: 39 concentric hex cutouts at centers of 3-tiered convex honeycomb
        tier_specs = [
            (8.74, np.radians(6.923)),    # Tier 1 Lower
            (17.40, np.radians(20.769)),  # Tier 2 Middle (centered in convex diamond)
            (26.06, np.radians(6.923)),   # Tier 3 Upper
        ]
        for z_c, th_base in tier_specs:
            for k in range(13):
                th_k = th_base + k * (2.0 * np.pi / 13.0)
                cutters.append(make_hex_cutter(th_k, z_c, hex_radius=2.85))

    elif variant_id == "07":
        # 07_Classic_Solid_Tactical: 16 tilted ribbon cutouts tracking inter-rib valleys
        z0, z1 = 4.2, 30.6
        width = 1.8
        z_vals = np.linspace(z0, z1, 35)
        slope_rad_per_mm = 0.01293  # 0.741 deg/mm rib tilt slope
        d_theta = slope_rad_per_mm * (z_vals - 17.4)

        # 16 valleys at Z = 17.4 mm
        th_valleys = [
            -172.10, -150.24, -128.36, -106.60, -84.52, -62.80, -29.76, -7.90,
             13.91,   35.68,   57.42,   79.14,  100.86, 122.58, 144.32, 166.09
        ]
        for k in range(16):
            th_k = np.radians(th_valleys[k])
            cutters.append(make_swept_path_cutter(th_k, z_vals, d_theta, width))

    return cutters


def export_2color_assembly_glb(inner_assem: trimesh.Trimesh, outer_assem: trimesh.Trimesh, glb_path: str):
    """Export an assembled 2-color mid shell reference GLB in assembly coordinates."""
    scene = trimesh.Scene()

    # Inner ratchet (PETG)
    m_inner = inner_assem.copy()
    rgba_inner = np.asarray([*(round(c * 255) for c in PETG_INNER_COLOUR), 255], dtype=np.uint8)
    m_inner.visual = trimesh.visual.ColorVisuals(mesh=m_inner, face_colors=np.tile(rgba_inner, (len(m_inner.faces), 1)))
    m_inner.visual.material = trimesh.visual.material.PBRMaterial(
        name="Inner_Ratchet_PETG_PBR",
        baseColorFactor=[*PETG_INNER_COLOUR, 1.0],
        metallicFactor=0.1,
        roughnessFactor=0.4,
    )
    scene.add_geometry(m_inner, node_name="Inner_Ratchet_PETG", geom_name="Inner_Ratchet_PETG")

    # Outer shell (PLA Matte)
    m_outer = outer_assem.copy()
    rgba_outer = np.asarray([*(round(c * 255) for c in PLA_OUTER_COLOUR), 255], dtype=np.uint8)
    m_outer.visual = trimesh.visual.ColorVisuals(mesh=m_outer, face_colors=np.tile(rgba_outer, (len(m_outer.faces), 1)))
    m_outer.visual.material = trimesh.visual.material.PBRMaterial(
        name="Outer_Shell_PLA_Matte_PBR",
        baseColorFactor=[*PLA_OUTER_COLOUR, 1.0],
        metallicFactor=0.05,
        roughnessFactor=0.7,
    )
    scene.add_geometry(m_outer, node_name="Outer_Shell_PLA_Matte", geom_name="Outer_Shell_PLA_Matte")

    glb_bytes = scene.export(file_type="glb")
    with open(glb_path, "wb") as f:
        f.write(glb_bytes)


def export_2color_assembly_3mf(inner_flat: trimesh.Trimesh, outer_flat: trimesh.Trimesh, threemf_path: str):
    """Export a 2-color printable plate containing both pieces flat on the print bed."""
    scene = trimesh.Scene()

    # Offset outer and inner slightly on plate so they don't overlap on the bed
    m_outer = outer_flat.copy().apply_translation([-25.0, 0.0, 0.0])
    m_inner = inner_flat.copy().apply_translation([25.0, 0.0, 0.0])

    rgba_outer = np.asarray([*(round(c * 255) for c in PLA_OUTER_COLOUR), 255], dtype=np.uint8)
    m_outer.visual = trimesh.visual.ColorVisuals(mesh=m_outer, face_colors=np.tile(rgba_outer, (len(m_outer.faces), 1)))

    rgba_inner = np.asarray([*(round(c * 255) for c in PETG_INNER_COLOUR), 255], dtype=np.uint8)
    m_inner.visual = trimesh.visual.ColorVisuals(mesh=m_inner, face_colors=np.tile(rgba_inner, (len(m_inner.faces), 1)))

    scene.add_geometry(m_outer, node_name="Outer_Shell_PLA_Matte", geom_name="Outer_Shell_PLA_Matte")
    scene.add_geometry(m_inner, node_name="Inner_Ratchet_PETG", geom_name="Inner_Ratchet_PETG")

    threemf_bytes = scene.export(file_type="3mf")
    with open(threemf_path, "wb") as f:
        f.write(threemf_bytes)


def main():
    print("=" * 70)
    print("BUILDING 2-PIECE SPLIT ARCHITECTURE WITH WINDOWS FOR ALL MID SHELLS")
    print("=" * 70)

    # 1. Load P01 reference and build the certified boolean bore cutter
    p01_path = os.path.join(WAIST_DIR, "08_33_Mid_Shell_P01_Outer.stl")
    p02_path = os.path.join(WAIST_DIR, "07_32_Mid_Shell_P02_Ratchet.stl")
    assert os.path.exists(p01_path), f"Missing reference: {p01_path}"
    assert os.path.exists(p02_path), f"Missing reference: {p02_path}"

    p01 = trimesh.load(p01_path)
    p02 = trimesh.load(p02_path)
    print(f"Loaded reference P01: {p01.volume:.2f} mm³, P02: {p02.volume:.2f} mm³")

    cutter = create_bore_cutter(p01)
    print(f"Constructed certified bore cutter: volume = {cutter.volume:.2f} mm³")

    # Transforms
    T_outer, T_inner_raw = B.get_canonical_transforms()
    T_inner_seated = T_inner_raw

    # Flip matrix to convert monolithic shells to P01 flat-bed print orientation
    R_x = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    T_z = trimesh.transformations.translation_matrix([0, 0, 34.79966736])
    flip_matrix = T_z @ R_x

    variants = [
        {
            "id": "01",
            "name": "01_AeroFlow",
            "title": "AeroFlow",
            "source_old": "08_Mid_Shell_Option_01_AeroFlow.stl",
            "outer_new": "08_Mid_Shell_Option_01_AeroFlow_Outer.stl",
            "is_already_split": False,
        },
        {
            "id": "02",
            "name": "02_Vector_Chevron",
            "title": "Vector Chevron",
            "source_old": "08_Mid_Shell_Option_02_Vector_Chevron.stl",
            "outer_new": "08_Mid_Shell_Option_02_Vector_Chevron_Outer.stl",
            "is_already_split": False,
        },
        {
            "id": "03",
            "name": "03_Orbit",
            "title": "Orbit",
            "source_old": "08_Mid_Shell_Option_03_Orbit.stl",
            "outer_new": "08_Mid_Shell_Option_03_Orbit_Outer.stl",
            "is_already_split": False,
        },
        {
            "id": "04",
            "name": "04_Ergo_Scoops",
            "title": "Ergo Scoops",
            "source_old": "08_Mid_Shell_Option_04_Ergo_Scoops.stl",
            "outer_new": "08_Mid_Shell_Option_04_Ergo_Scoops_Outer.stl",
            "is_already_split": False,
        },
        {
            "id": "05",
            "name": "05_Contour_Twist",
            "title": "Contour Twist",
            "source_old": "08_Mid_Shell_Option_05_Contour_Twist_Outer.stl",
            "outer_new": "08_Mid_Shell_Option_05_Contour_Twist_Outer.stl",
            "is_already_split": True,
        },
        {
            "id": "06",
            "name": "06_Hex_Tactical",
            "title": "Hex Tactical",
            "source_old": "08_Mid_Shell_Option_06_Hex_Tactical.stl",
            "outer_new": "08_Mid_Shell_Option_06_Hex_Tactical_Outer.stl",
            "is_already_split": False,
        },
        {
            "id": "07",
            "name": "07_Classic_Solid_Tactical",
            "title": "Classic Solid Tactical",
            "source_old": "08_Mid_Shell_Option_07_Classic_Solid_Tactical.stl",
            "outer_new": "08_Mid_Shell_Option_07_Classic_Solid_Tactical_Outer.stl",
            "is_already_split": False,
        },
    ]

    # Clean up redundant duplicate inner shell files from all directories
    for d in [OPTIONS_DIR, FLAT_DIR, ASSEM_DIR]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.startswith("07_Mid_Shell_Option_") and f.endswith("_Inner.stl"):
                    p = os.path.join(d, f)
                    try:
                        os.remove(p)
                        print(f"Removed redundant inner file: {os.path.basename(p)}")
                    except Exception as e:
                        print(f"Error removing {p}: {e}")

    for var in variants:
        v_name = var["name"]
        print(f"\n--- Processing Variant {var['id']}: {var['title']} ---")

        if var["is_already_split"]:
            # Load from v1.2 or OPTIONS_DIR
            candidate_v12 = os.path.join(V12_DIR, "02_Waist_Mechanism", "Mid_Shell_Options", var["outer_new"])
            if os.path.exists(candidate_v12):
                outer_flat = trimesh.load(candidate_v12)
            else:
                outer_flat = trimesh.load(os.path.join(OPTIONS_DIR, var["outer_new"]))
            inner_flat = p02.copy()
        else:
            # Check pristine solid source in v1.2, then OPTIONS_DIR
            src_path = os.path.join(V12_DIR, "02_Waist_Mechanism", "Mid_Shell_Options", var["source_old"])
            if not os.path.exists(src_path):
                src_path = os.path.join(OPTIONS_DIR, var["source_old"])
            if not os.path.exists(src_path):
                src_path = os.path.join(OPTIONS_DIR, var["outer_new"])

            assert os.path.exists(src_path), f"Source shell not found: {src_path}"
            raw_solid = trimesh.load(src_path)

            # Check if raw_solid needs flipping: if ratchet teeth at Z=0, flip it
            z0_verts = raw_solid.vertices[np.abs(raw_solid.vertices[:, 2] - 0.0) < 0.01]
            r0 = np.hypot(z0_verts[:, 0], z0_verts[:, 1])
            if r0.min() < 17.5:
                # Ratchet teeth are at Z=0; flip so top rim is at Z=0
                flipped = raw_solid.copy().apply_transform(flip_matrix)
            else:
                flipped = raw_solid.copy()

            if var["id"] == "03":
                print("  Applying continuous Taubin smoothing to Orbit pods to remove facet pixelation...")
                flipped = smoothen_orbit_mesh(flipped)

            # Generate aesthetic through-window cutters for this variant
            win_cutters = generate_window_cutters(var["id"])
            print(f"  Generated {len(win_cutters)} window cutters for {var['title']}")

            # Perform boolean cut with certified bore cutter and window cutters
            all_cutters = [cutter] + win_cutters
            outer_flat = fidget.cut(flipped, *all_cutters)
            inner_flat = p02.copy()

        # Validate Outer Shell
        assert outer_flat.is_watertight, f"Variant {v_name} outer shell must be watertight"
        assert len(outer_flat.split()) == 1, f"Variant {v_name} outer shell must be single body"
        assert abs(outer_flat.bounds[1, 2] - 34.80) < 0.05, f"Variant {v_name} height mismatch"
        assert outer_flat.euler_number < 0, f"Variant {v_name} must have through-windows (Euler={outer_flat.euler_number})"

        print(f"  Outer Shell: volume = {outer_flat.volume:.2f} mm³, watertight = True, bodies = 1, Euler = {outer_flat.euler_number}")

        # Assembled coordinates
        outer_assem = outer_flat.copy().apply_transform(T_outer)
        inner_assem = inner_flat.copy().apply_transform(T_inner_seated)

        # Interference check between outer and inner in assembled coordinates
        inter = fidget.intersect(outer_assem, inner_assem)
        inter_vol = inter.volume if inter else 0.0
        print(f"  Pairwise Interference (Outer vs Master Inner): {inter_vol:.4f} mm³")
        assert inter_vol < 0.20, f"Excessive interference ({inter_vol:.4f} mm³) in variant {v_name}"

        # 1. Save to 02_Waist_Mechanism/Mid_Shell_Options/
        dest_outer_waist = os.path.join(OPTIONS_DIR, var["outer_new"])
        outer_flat.export(dest_outer_waist)

        # 2. Save to All_Parts_Flat_Bed_Oriented/Mid_Shell_Options/
        dest_outer_flat = os.path.join(FLAT_DIR, var["outer_new"])
        outer_flat.export(dest_outer_flat)

        # 3. Save to All_Parts_Assembled_Coordinates/Mid_Shell_Options/
        dest_outer_assem = os.path.join(ASSEM_DIR, var["outer_new"])
        outer_assem.export(dest_outer_assem)

        # 4. Remove obsolete monolithic files if they differ from outer_new
        if var["source_old"] and var["source_old"] != var["outer_new"]:
            for d in [OPTIONS_DIR, FLAT_DIR, ASSEM_DIR]:
                old_f = os.path.join(d, var["source_old"])
                if os.path.exists(old_f):
                    try:
                        os.remove(old_f)
                        print(f"  Cleaned up monolithic file: {os.path.basename(old_f)}")
                    except Exception as e:
                        print(f"  Warning cleaning {old_f}: {e}")

        # 5. Generate 2-Color Assembly GLB & 3MF Plate
        glb_name = f"{var['name']}_Mid_Shell_2Color_Assembly.glb"
        glb_path = os.path.join(OPTIONS_DIR, glb_name)
        export_2color_assembly_glb(inner_assem, outer_assem, glb_path)
        print(f"  Exported 2-Color Assembly GLB: {glb_name}")

        threemf_name = f"{var['name']}_Mid_Shell_2Color_Assembly.3mf"
        threemf_path = os.path.join(PLATES_DIR, threemf_name)
        export_2color_assembly_3mf(inner_flat, outer_flat, threemf_path)
        print(f"  Exported 2-Color Assembly 3MF: {threemf_name}")

    print("\n" + "=" * 70)
    print("SPLIT MID SHELL BUILD COMPLETE — ALL 7 VARIANTS STANDARDIZED WITH WINDOWS")
    print("=" * 70)


if __name__ == "__main__":
    main()
