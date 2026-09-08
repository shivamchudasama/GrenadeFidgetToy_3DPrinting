"""Build and export B3D Labs Branded Custom Handles (Left & Right) for Hybrid Grenade v1.3.

This script generates separate branded handle models without overwriting the originals:
  - 29_Custom_Handle_Left_Branded.stl
  - 30_Custom_Handle_Right_Branded.stl
  - 29_Custom_Handle_Left_Logo_Inlay.stl  (Optional multi-material inlay)
  - 30_Custom_Handle_Right_Logo_Inlay.stl (Optional multi-material inlay)

Outputs are created in:
  1. Hybrid_Grenade_v1.3/05_Folding_Head_And_Spinner/
  2. Hybrid_Grenade_v1.3/All_Parts_Flat_Bed_Oriented/
  3. Hybrid_Grenade_v1.3/All_Parts_Assembled_Coordinates/
  4. Branding_Visualization/
"""
from __future__ import annotations

import os
import sys
import shutil
import numpy as np
import trimesh
from shapely import affinity
import shapely.geometry.polygon
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import export_3d_print_package as E3D

PKG_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.3")
SUB_DIR = os.path.join(PKG_DIR, "05_Folding_Head_And_Spinner")
BED_DIR = os.path.join(PKG_DIR, "All_Parts_Flat_Bed_Oriented")
ASY_DIR = os.path.join(PKG_DIR, "All_Parts_Assembled_Coordinates")
VIS_DIR = os.path.join(ROOT_DIR, "Branding_Visualization")

SVG_PATH = os.path.join(ROOT_DIR, "B3D_Labs.svg")

# Target dimensions on the handle cheek:
LOGO_WIDTH = 12.00  # mm
LOGO_DEPTH = 0.60   # mm deboss depth (3 layers at 0.20 mm)
TARGET_Z = -30.54   # mm center along lever arm
TARGET_Y = 65.00    # mm center along lever height


def to_manifold(tm: trimesh.Trimesh) -> manifold3d.Manifold:
    props = np.ascontiguousarray(tm.vertices, dtype=np.float32)
    tris = np.ascontiguousarray(tm.faces, dtype=np.uint32)
    return manifold3d.Manifold(manifold3d.Mesh(vert_properties=props, tri_verts=tris))


def to_trimesh(m: manifold3d.Manifold) -> trimesh.Trimesh:
    mesh = m.to_mesh()
    return trimesh.Trimesh(
        vertices=mesh.vert_properties[:, :3],
        faces=mesh.tri_verts,
        process=True
    )


def build_branded_handles():
    print("=" * 70)
    print("  BUILDING B3D LABS BRANDED HANDLES (HYBRID GRENADE v1.3)")
    print("=" * 70)

    # 1. Load SVG Logo Polygon
    p = trimesh.load(SVG_PATH)
    poly = p.polygons_full[0]
    poly_bounds = poly.bounds
    svg_w = poly_bounds[2] - poly_bounds[0]
    svg_h = poly_bounds[3] - poly_bounds[1]
    scale = LOGO_WIDTH / svg_w
    logo_h = svg_h * scale
    print(f"  [*] Logo SVG native bounds: {svg_w:.1f} x {svg_h:.1f}")
    print(f"  [*] Scaled logo: {LOGO_WIDTH:.2f} mm wide x {logo_h:.2f} mm high")

    svg_cx = (poly_bounds[0] + poly_bounds[2]) / 2.0
    svg_cy = (poly_bounds[1] + poly_bounds[3]) / 2.0

    # 2. Right Cheek Polygon:
    # Mirrored so that the B-like shape comes on the right:
    poly_r = affinity.translate(poly, -svg_cx, -svg_cy)
    poly_r = affinity.scale(poly_r, xfact=-scale, yfact=-scale, origin=(0, 0))
    poly_r = affinity.translate(poly_r, TARGET_Z, TARGET_Y)
    poly_r = shapely.geometry.polygon.orient(poly_r, sign=1.0)  # Ensure standard CCW

    # 3. Left Cheek Polygon:
    # Restored to original orientation as requested (xfact=scale):
    poly_l = affinity.translate(poly, -svg_cx, -svg_cy)
    poly_l = affinity.scale(poly_l, xfact=scale, yfact=-scale, origin=(0, 0))
    poly_l = affinity.translate(poly_l, TARGET_Z, TARGET_Y)
    poly_l = shapely.geometry.polygon.orient(poly_l, sign=1.0)  # Ensure standard CCW

    # 4. Load original assembled handles (UNMODIFIED)
    hr_asy_path = os.path.join(ASY_DIR, "30_Custom_Handle_Right.stl")
    hl_asy_path = os.path.join(ASY_DIR, "29_Custom_Handle_Left.stl")
    hr_orig = trimesh.load(hr_asy_path)
    hl_orig = trimesh.load(hl_asy_path)

    # 5. Create 3D Cutters & Inlays:
    # Right Cutter (oversized by 0.10 mm to punch cleanly through surface):
    cutter_r_2d = trimesh.creation.extrude_polygon(poly_r, height=LOGO_DEPTH + 0.15)
    v_cr = np.column_stack([(9.50 - LOGO_DEPTH) + cutter_r_2d.vertices[:, 2], cutter_r_2d.vertices[:, 1], cutter_r_2d.vertices[:, 0]])
    cutter_r = trimesh.Trimesh(vertices=v_cr, faces=cutter_r_2d.faces[:, ::-1], process=True)

    # Right Inlay: X in [9.50 - LOGO_DEPTH, 9.50]
    inlay_r_2d = trimesh.creation.extrude_polygon(poly_r, height=LOGO_DEPTH)
    v_ir = np.column_stack([(9.50 - LOGO_DEPTH) + inlay_r_2d.vertices[:, 2], inlay_r_2d.vertices[:, 1], inlay_r_2d.vertices[:, 0]])
    inlay_r_asy = trimesh.Trimesh(vertices=v_ir, faces=inlay_r_2d.faces[:, ::-1], process=True)

    # Left Cutter:
    cutter_l_2d = trimesh.creation.extrude_polygon(poly_l, height=LOGO_DEPTH + 0.15)
    v_cl = np.column_stack([(-9.50 + LOGO_DEPTH) - cutter_l_2d.vertices[:, 2], cutter_l_2d.vertices[:, 1], cutter_l_2d.vertices[:, 0]])
    cutter_l = trimesh.Trimesh(vertices=v_cl, faces=cutter_l_2d.faces.copy(), process=True)

    # Left Inlay: X in [-9.50, -9.50 + LOGO_DEPTH]
    inlay_l_2d = trimesh.creation.extrude_polygon(poly_l, height=LOGO_DEPTH)
    v_il = np.column_stack([(-9.50 + LOGO_DEPTH) - inlay_l_2d.vertices[:, 2], inlay_l_2d.vertices[:, 1], inlay_l_2d.vertices[:, 0]])
    inlay_l_asy = trimesh.Trimesh(vertices=v_il, faces=inlay_l_2d.faces.copy(), process=True)

    # 6. Execute Boolean Deboss with Manifold3D
    print("  [*] Performing boolean deboss via manifold3d...")
    m_hr = to_manifold(hr_orig)
    m_hl = to_manifold(hl_orig)
    m_cr = to_manifold(cutter_r)
    m_cl = to_manifold(cutter_l)

    m_hr_branded = m_hr - m_cr
    m_hl_branded = m_hl - m_cl

    hr_branded_asy = to_trimesh(m_hr_branded)
    hl_branded_asy = to_trimesh(m_hl_branded)

    print(f"  [+] Right Branded Handle: watertight={hr_branded_asy.is_volume}, {len(hr_branded_asy.faces)} faces")
    print(f"  [+] Left Branded Handle:  watertight={hl_branded_asy.is_volume}, {len(hl_branded_asy.faces)} faces")

    # 7. Compute Flat-Bed Oriented Versions with STL safety
    print("  [*] Computing flat-bed oriented poses with STL safety repair...")
    hr_branded_bed = E3D._stl_safe(E3D._center_on_bed(E3D._to_bed_pose(hr_branded_asy, "30_Custom_Handle_Right.stl")), "hr_branded")
    hl_branded_bed = E3D._stl_safe(E3D._center_on_bed(E3D._to_bed_pose(hl_branded_asy, "29_Custom_Handle_Left.stl")), "hl_branded")

    inlay_r_bed = E3D._stl_safe(E3D._center_on_bed(E3D._to_bed_pose(inlay_r_asy, "30_Custom_Handle_Right.stl")), "inlay_r")
    inlay_l_bed = E3D._stl_safe(E3D._center_on_bed(E3D._to_bed_pose(inlay_l_asy, "29_Custom_Handle_Left.stl")), "inlay_l")

    # 8. Export Separate Files (Original files are NEVER overwritten)
    export_jobs = [
        # Assembled Coordinates
        (hr_branded_asy, os.path.join(ASY_DIR, "30_Custom_Handle_Right_Branded.stl")),
        (hl_branded_asy, os.path.join(ASY_DIR, "29_Custom_Handle_Left_Branded.stl")),
        (inlay_r_asy, os.path.join(ASY_DIR, "30_Custom_Handle_Right_Logo_Inlay.stl")),
        (inlay_l_asy, os.path.join(ASY_DIR, "29_Custom_Handle_Left_Logo_Inlay.stl")),

        # Flat Bed Oriented Coordinates
        (hr_branded_bed, os.path.join(BED_DIR, "30_Custom_Handle_Right_Branded.stl")),
        (hl_branded_bed, os.path.join(BED_DIR, "29_Custom_Handle_Left_Branded.stl")),
        (inlay_r_bed, os.path.join(BED_DIR, "30_Custom_Handle_Right_Logo_Inlay.stl")),
        (inlay_l_bed, os.path.join(BED_DIR, "29_Custom_Handle_Left_Logo_Inlay.stl")),

        # Subassembly 05 Directory (Flat Bed Oriented for Slicing)
        (hr_branded_bed, os.path.join(SUB_DIR, "30_Custom_Handle_Right_Branded.stl")),
        (hl_branded_bed, os.path.join(SUB_DIR, "29_Custom_Handle_Left_Branded.stl")),
        (inlay_r_bed, os.path.join(SUB_DIR, "30_Custom_Handle_Right_Logo_Inlay.stl")),
        (inlay_l_bed, os.path.join(SUB_DIR, "29_Custom_Handle_Left_Logo_Inlay.stl")),

        # Branding Visualization Directory (Convenience folder)
        (hr_branded_bed, os.path.join(VIS_DIR, "30_Custom_Handle_Right_Branded.stl")),
        (hl_branded_bed, os.path.join(VIS_DIR, "29_Custom_Handle_Left_Branded.stl")),
        (inlay_r_bed, os.path.join(VIS_DIR, "30_Custom_Handle_Right_Logo_Inlay.stl")),
        (inlay_l_bed, os.path.join(VIS_DIR, "29_Custom_Handle_Left_Logo_Inlay.stl")),
    ]

    for mesh, path in export_jobs:
        mesh.export(path)
        print(f"  [SAVED] {path}")

    # 9. Render Side-by-Side Visual Verification Image
    render_verification_image(hl_branded_asy, hr_branded_asy, inlay_l_asy, inlay_r_asy, hl_branded_bed, hr_branded_bed, inlay_l_bed, inlay_r_bed)


def render_verification_image(hl_asy, hr_asy, inlay_l_asy, inlay_r_asy, hl_bed, hr_bed, inlay_l_bed, inlay_r_bed):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPoly
    from matplotlib.collections import PatchCollection

    print("  [*] Rendering side-by-side verification image...")

    def render_first_layer(ax, items, title, xlim=(-35, 35), ylim=(-35, 35)):
        all_tri_2d = []
        all_dists = []
        all_colors = []
        for m, col, depth_bias in items:
            v = m.vertices
            f = m.faces
            fn = m.face_normals
            # Looking from bottom up (outer branded cheek normal points -Z in bed pose)
            facing = -fn[:, 2]
            base_c = np.array(col) / 255.0
            diffuse = np.clip(0.42 + 0.58 * np.dot(fn, [0.3, 0.4, -0.8]), 0.22, 1.0)
            fc = base_c[None, :] * diffuse[:, None]
            for i, tri in enumerate(f):
                if facing[i] < -0.05:
                    continue
                tri_2d = v[tri, :2]
                z_center = -v[tri, 2].mean() + depth_bias
                all_tri_2d.append(tri_2d)
                all_dists.append(z_center)
                all_colors.append(fc[i])
        
        order = np.argsort(np.array(all_dists))
        patches = [MplPoly(all_tri_2d[i], closed=True) for i in order]
        p_coll = PatchCollection(patches, facecolors=[all_colors[i] for i in order], edgecolors='none', linewidths=0.0)
        ax.add_collection(p_coll)
        ax.set_aspect('equal')
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.axis('off')
        ax.set_title(title, color='#f8fafc', fontsize=13, weight='bold', pad=14)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8), facecolor='#0b0f19')

    render_first_layer(axes[0], [(hl_bed, [122, 181, 102], 0.0), (inlay_l_bed, [255, 110, 20], 0.05)],
                       'Left Handle (`29_Custom_Handle_Left_Branded.stl`)\nPrinted Face View [Spine on Left | B-Like Shape on Right]')
    render_first_layer(axes[1], [(hr_bed, [122, 181, 102], 0.0), (inlay_r_bed, [255, 110, 20], 0.05)],
                       'Right Handle (`30_Custom_Handle_Right_Branded.stl`)\nPrinted Face View [Spine on Left | B-Like Shape on Right]')

    plt.tight_layout()
    verif_vis = os.path.join(VIS_DIR, 'Branded_Handles_Left_And_Right_Verification.png')
    verif_root = os.path.join(ROOT_DIR, 'Branded_Handles_Left_And_Right_Verification.png')
    plt.savefig(verif_vis, dpi=180, facecolor='#0b0f19', bbox_inches='tight')
    shutil.copy2(verif_vis, verif_root)
    print(f"  [SAVED] Verification image: {verif_vis} and {verif_root}")


if __name__ == "__main__":
    build_branded_handles()
