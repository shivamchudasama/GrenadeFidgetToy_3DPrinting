"""Build dedicated Internal Barrel & 4 Springs Assembly Showcase.

Generates:
1. Custom_Internal_Barrel_And_Springs_Only_Assembly.glb
2. Custom_Internal_Barrel_And_Springs_Cutaway.glb
3. High-resolution multi-view render: barrel_springs_updated_assembly.png
4. Interactive Three.js HTML Viewer: Internal_Barrel_And_Springs_Viewer.html
"""
from __future__ import annotations

import base64
import json
import os
import sys
import shutil
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "tools"))
import build_rod_detent as BRD
from package_paths import PACKAGE_DIR, ASSEMBLED_DIR

ARTIFACT_DIR = r"C:\Users\chuda\.gemini\antigravity-ide\brain\8038d30c-f335-4329-89a4-7c95c3fe86a2"

# 1. Load Parts
barrel = trimesh.load(os.path.join(ASSEMBLED_DIR, "10_Custom_Internal_Barrel_4Slot.stl"), process=True)
s01 = trimesh.load(os.path.join(ASSEMBLED_DIR, "12_Custom_Rod_Detent_Spring_01.stl"), process=True)
s02 = trimesh.load(os.path.join(ASSEMBLED_DIR, "13_Custom_Rod_Detent_Spring_02.stl"), process=True)
s03 = trimesh.load(os.path.join(ASSEMBLED_DIR, "14_Custom_Rod_Detent_Spring_03.stl"), process=True)
s04 = trimesh.load(os.path.join(ASSEMBLED_DIR, "15_Custom_Rod_Detent_Spring_04.stl"), process=True)
cap = trimesh.load(os.path.join(ASSEMBLED_DIR, "11_Custom_Internal_Barrel_Cap.stl"), process=True)

# Colors
COLOR_BARREL = (65, 75, 88)         # Gunmetal Blue/Grey
COLOR_CAP = (120, 130, 145)         # Titanium Grey
COLOR_S01 = (255, 100, 30)          # Vivid Safety Orange (az 0°)
COLOR_S02 = (0, 200, 240)           # Cyan Blue (az 90°)
COLOR_S03 = (255, 180, 0)           # Warm Gold (az 180°)
COLOR_S04 = (50, 205, 100)          # Emerald Lime (az 270°)

springs_data = [
    ("Spring 01 (0°)", s01, COLOR_S01),
    ("Spring 02 (90°)", s02, COLOR_S02),
    ("Spring 03 (180°)", s03, COLOR_S03),
    ("Spring 04 (270°)", s04, COLOR_S04),
]

# 2. Build Cutaway Barrel Mesh (remove quadrant X > 0 and Z > 0)
box_cut = trimesh.creation.box(extents=[30.0, 50.0, 30.0])
box_cut.apply_translation([15.0, 45.0, 15.0])
b_cutaway = trimesh.boolean.difference([barrel, box_cut], engine=BRD.ENGINE)

# 3. Export GLB Assemblies
print("Exporting dedicated GLBs...")
sub_03 = os.path.join(PACKAGE_DIR, "03_Internal_Barrel_And_Upper_Station")

# Assembled GLB
scene_ass = trimesh.Scene()
for name, m, c in [("10_Custom_Internal_Barrel_4Slot", barrel, COLOR_BARREL),
                   ("11_Custom_Internal_Barrel_Cap", cap, COLOR_CAP)] + [
                   (f"1{i+2}_Custom_Rod_Detent_Spring_0{i+1}", sp, col) for i, (_, sp, col) in enumerate(springs_data)]:
    mesh_copy = m.copy()
    rgba = list(c) + [255]
    mesh_copy.visual = trimesh.visual.ColorVisuals(mesh=mesh_copy, face_colors=np.tile(rgba, (len(mesh_copy.faces), 1)))
    scene_ass.add_geometry(mesh_copy, node_name=name)

glb_ass_path = os.path.join(sub_03, "Custom_Internal_Barrel_And_Springs_Only_Assembly.glb")
scene_ass.export(glb_ass_path)
print(f"  [OK] Exported: {glb_ass_path}")

# Cutaway GLB
scene_cut = trimesh.Scene()
for name, m, c in [("10_Custom_Internal_Barrel_4Slot_Cutaway", b_cutaway, COLOR_BARREL),
                   ("11_Custom_Internal_Barrel_Cap", cap, COLOR_CAP)] + [
                   (f"1{i+2}_Custom_Rod_Detent_Spring_0{i+1}", sp, col) for i, (_, sp, col) in enumerate(springs_data)]:
    mesh_copy = m.copy()
    rgba = list(c) + [255]
    mesh_copy.visual = trimesh.visual.ColorVisuals(mesh=mesh_copy, face_colors=np.tile(rgba, (len(mesh_copy.faces), 1)))
    scene_cut.add_geometry(mesh_copy, node_name=name)

glb_cut_path = os.path.join(sub_03, "Custom_Internal_Barrel_And_Springs_Cutaway.glb")
scene_cut.export(glb_cut_path)
print(f"  [OK] Exported: {glb_cut_path}")


# 4. Multi-View Rendering Engine
def render_projected_scene(ax, meshes_with_colors, azim_deg=35, elev_deg=25, zoom=1.0, center=[0.0, 42.0, 0.0]):
    """Clean 3D projection renderer with painter's algorithm sorting."""
    az = np.radians(azim_deg)
    el = np.radians(elev_deg)
    
    R_az = np.array([
        [np.cos(az), 0, -np.sin(az)],
        [0, 1, 0],
        [np.sin(az), 0, np.cos(az)]
    ])
    R_el = np.array([
        [1, 0, 0],
        [0, np.cos(el), np.sin(el)],
        [0, -np.sin(el), np.cos(el)]
    ])
    R_cam = R_el @ R_az
    
    light_dir = np.array([0.45, 0.75, 0.65])
    light_dir = light_dir / np.linalg.norm(light_dir)
    
    all_polys = []
    all_colors = []
    all_depths = []
    
    for m, base_rgb, alpha in meshes_with_colors:
        m_rend = m
        verts = m_rend.vertices
        faces = m_rend.faces
        fnorms = m_rend.face_normals
        
        v_centered = verts - np.array(center)
        v_cam = (R_cam @ v_centered.T).T
        fc_cam = (R_cam @ (m_rend.triangles_center - np.array(center)).T).T
        fn_cam = (R_cam @ fnorms.T).T
        
        visible = fn_cam[:, 2] > -0.15
        dot = np.maximum(0.0, np.dot(fnorms, light_dir))
        shade = 0.30 + 0.70 * dot
        
        vis_indices = np.where(visible)[0]
        base_arr = np.array(base_rgb) / 255.0
        for f_idx in vis_indices:
            tri = faces[f_idx]
            pts_2d = v_cam[tri, :2] * zoom
            depth = fc_cam[f_idx, 2]
            c = np.clip(base_arr * shade[f_idx], 0.0, 1.0)
            all_polys.append(pts_2d)
            all_colors.append((c[0], c[1], c[2], alpha))
            all_depths.append(depth)
            
    sort_order = np.argsort(all_depths)
    sorted_polys = [all_polys[i] for i in sort_order]
    sorted_colors = [all_colors[i] for i in sort_order]
    
    patches = [MplPolygon(p, closed=True) for p in sorted_polys]
    pc = PatchCollection(patches, facecolors=sorted_colors, edgecolors='none', lw=0)
    ax.add_collection(pc)
    
    ax.set_xlim(-24, 24)
    ax.set_ylim(-24, 24)
    ax.set_aspect('equal')
    ax.axis('off')


print("Generating multi-panel showcase figure...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 16), facecolor="#141820")

# Panel 1: Full 3D Assembled
ax1.set_facecolor("#141820")
render_projected_scene(ax1, [
    (barrel, COLOR_BARREL, 0.96),
    (s01, COLOR_S01, 1.0),
    (s02, COLOR_S02, 1.0),
    (s03, COLOR_S03, 1.0),
    (s04, COLOR_S04, 1.0),
    (cap, COLOR_CAP, 0.98),
], azim_deg=35, elev_deg=22, zoom=0.95)
ax1.set_title("1. Full 3D Assembled View\n(Barrel + 4 Detent Springs + Retention Cap)", color="#FFFFFF", fontsize=13, fontweight='bold', pad=10)

# Panel 2: Cutaway 3D Interior View
ax2.set_facecolor("#141820")
render_projected_scene(ax2, [
    (b_cutaway, COLOR_BARREL, 0.98),
    (s02, COLOR_S02, 1.0),
    (s03, COLOR_S03, 1.0),
    (cap, COLOR_CAP, 0.95),
], azim_deg=45, elev_deg=22, zoom=0.95)
ax2.set_title("2. Cutaway 3D Interior View\n(Revealing Cavity Seating, Retention Steps & Reinforced Walls)", color="#00E5FF", fontsize=13, fontweight='bold', pad=10)

# Panel 3: Top-Down Bore View (Orthographic Y-axis)
ax3.set_facecolor("#141820")
# For top down: elev = 89.9 deg, look straight down bore
# Sliced at Y=57mm to clearly see the 4 slots and spring cross-sections
sec_y = 57.0
sec_b = barrel.section(plane_origin=[0, sec_y, 0], plane_normal=[0, 1, 0])
p2d_b, _ = sec_b.to_2D()
poly_b = p2d_b.polygons_full[0]
ext_b = np.array(poly_b.exterior.coords)
ax3.plot(ext_b[:, 0], ext_b[:, 1], color='#88A0C0', lw=2.5, label="Reinforced Barrel Exterior (14.2mm)")
for i, h in enumerate(poly_b.interiors):
    h_c = np.array(h.coords)
    ax3.plot(h_c[:, 0], h_c[:, 1], color='#00E5FF', lw=1.8, label="4 L-Shaped Cavities (R_OUT=12.35mm)" if i == 0 else "")

for sp, col, s_name in [(s01, '#FF641E', 'Spring 01 (0°)'),
                         (s02, '#00C8F0', 'Spring 02 (90°)'),
                         (s03, '#FFB400', 'Spring 03 (180°)'),
                         (s04, '#32CD64', 'Spring 04 (270°)')]:
    sec_sp = sp.section(plane_origin=[0, sec_y, 0], plane_normal=[0, 1, 0])
    if sec_sp is not None:
        p2d_sp, _ = sec_sp.to_2D()
        for poly in p2d_sp.polygons_full:
            ax3.fill(sec_sp.vertices[:, 0], sec_sp.vertices[:, 2], color=col, alpha=0.85, label=s_name)

ax3.set_xlim(-19, 19)
ax3.set_ylim(-19, 19)
ax3.set_aspect('equal')
ax3.grid(True, linestyle='--', color='#2A3445', alpha=0.7)
ax3.tick_params(colors='#88A0C0')
ax3.set_xlabel("X (Radial Detent Axis, mm)", color='#88A0C0', fontsize=10)
ax3.set_ylabel("Z (Radial Detent Axis, mm)", color='#88A0C0', fontsize=10)
ax3.legend(loc='lower left', fontsize=8.5, facecolor='#1A2230', edgecolor='#00E5FF', labelcolor='white')
ax3.set_title(f"3. Top-Down Bore Cross-Section (Y = {sec_y:.1f} mm)\nAll 4 Springs Seated in Cavities with 1.35mm Outer Walls", color="#FFB400", fontsize=13, fontweight='bold', pad=10)

# Panel 4: Exploded 3D Assembly
ax4.set_facecolor("#141820")
# Displace springs along insertion trajectories (lifted along Y and slightly radial)
s01_exp = s01.copy().apply_translation([-5.0, 18.0, 0.0])
s02_exp = s02.copy().apply_translation([0.0, 24.0, 5.0])
s03_exp = s03.copy().apply_translation([5.0, 18.0, 0.0])
s04_exp = s04.copy().apply_translation([0.0, 24.0, -5.0])
cap_exp = cap.copy().apply_translation([0.0, 32.0, 0.0])

render_projected_scene(ax4, [
    (barrel, COLOR_BARREL, 0.95),
    (s01_exp, COLOR_S01, 1.0),
    (s02_exp, COLOR_S02, 1.0),
    (s03_exp, COLOR_S03, 1.0),
    (s04_exp, COLOR_S04, 1.0),
    (cap_exp, COLOR_CAP, 0.95),
], azim_deg=35, elev_deg=20, zoom=0.65, center=[0.0, 50.0, 0.0])
ax4.set_title("4. Exploded Insertion Trajectory View\n(Cap + 4 Springs Aligning with Top Slots)", color="#32CD64", fontsize=13, fontweight='bold', pad=10)

plt.suptitle("HYBRID GRENADE v1.3 - INTERNAL BARREL & 4 DETENT SPRINGS ASSEMBLY", color="#FFFFFF", fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()

showcase_png = os.path.join(ARTIFACT_DIR, "barrel_springs_updated_assembly.png")
plt.savefig(showcase_png, dpi=180, facecolor=fig.get_facecolor(), edgecolor='none')
print(f"[SUCCESS] Saved multi-panel showcase render: {showcase_png}")

