"""Render multi-angle high-resolution preview images of the Modified Custom Head Assembly.

Generates:
  1. Head_Assembly_Isometric.png - Full assembled isometric view with color-coded parts
  2. Head_Assembly_Face_View.png - Top-down planar view showing pristine cheeks, lock holes & ring
  3. Head_Assembly_Exploded.png - Exploded view showing part relationships and lock pins
  4. Head_Assembly_Cheek_Profile.png - Close up profile showing pristine turned circular cheeks
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import build_modified_head_assembly as BHA

ARTIFACT_DIR = r"C:\Users\chuda\.gemini\antigravity-ide\brain\d6fdce15-0e77-454d-b4d6-d3348962fcde"


def render_scene_3d(items, filename, title, elev=28, azim=45, zoom_factor=1.0, exploded=False, disp=None, center_offset=(0, 0, 0)):
    fig = plt.figure(figsize=(12, 10), facecolor='#0d1117')
    ax = fig.add_subplot(111, projection='3d', facecolor='#0d1117')
    ax.set_box_aspect([1, 1.2, 0.8])
    
    all_verts = []
    
    # Lighting direction
    light_dir = np.array([0.4, 0.6, 1.0])
    light_dir = light_dir / np.linalg.norm(light_dir)

    for i, (name, mesh, color) in enumerate(items):
        m = mesh.copy()
        if exploded and disp is not None:
            m.apply_translation(disp[i])
            
        v = m.vertices
        f = m.faces
        all_verts.append(v)
        
        # Compute face normals and directional shading
        fn = m.face_normals
        diffuse = np.clip(np.dot(fn, light_dir), 0.20, 1.0)
        
        base_c = np.array(color) / 255.0
        face_colors = base_c[None, :] * (0.35 + 0.65 * diffuse[:, None])
        face_colors = np.clip(face_colors, 0.0, 1.0)
        face_colors = np.column_stack([face_colors, np.full(len(f), 0.98)])
        
        poly = Poly3DCollection(v[f], facecolors=face_colors, edgecolors='none', linewidths=0.05, alpha=0.98)
        ax.add_collection3d(poly)

    all_v = np.vstack(all_verts)
    min_b = all_v.min(axis=0)
    max_b = all_v.max(axis=0)
    center = (min_b + max_b) / 2.0 + np.array(center_offset)
    span = (max_b - min_b).max() / 2.0 / zoom_factor

    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)

    ax.view_init(elev=elev, azim=azim)
    ax.axis('off')

    plt.title(title, color='#f0f6fc', fontsize=14, fontweight='bold', pad=12)
    plt.tight_layout()

    out_path = os.path.join(ARTIFACT_DIR, filename)
    plt.savefig(out_path, dpi=160, bbox_inches='tight', facecolor='#0d1117', edgecolor='none')
    plt.close()
    print(f"Saved: {out_path}")
    return out_path


def main():
    print("Rendering High-Resolution Assembly Previews...")
    items = BHA.get_modified_head_items()
    disp = BHA.compute_exploded_displacements(items)

    # 1. Assembled Isometric View
    render_scene_3d(
        items,
        "Head_Assembly_Isometric.png",
        "Modified Custom Head — Enclosed Pod & Clean Surfaces (Isometric)",
        elev=32, azim=-60, zoom_factor=1.0, exploded=False
    )

    # 2. Planar Face View (Looking straight down Z axis)
    render_scene_3d(
        items,
        "Head_Assembly_Face_View.png",
        "Face View: Seamless Enclosed Pod Merged With Circular Clicker Head",
        elev=89, azim=-90, zoom_factor=1.05, exploded=False
    )

    # 3. Exploded Isometric View
    render_scene_3d(
        items,
        "Head_Assembly_Exploded.png",
        "Modified Custom Head — Exploded Assembly Diagram (11 Parts)",
        elev=30, azim=-55, zoom_factor=0.88, exploded=True, disp=disp
    )

    # 4. Angled Profile View
    render_scene_3d(
        items,
        "Head_Assembly_Cheek_Profile.png",
        "Profile View: Continuous Turned Cheeks & 20-Tooth Ratchet Gear",
        elev=20, azim=-30, zoom_factor=1.1, exploded=False
    )

    # 5. Close-up on the Enclosed Pod & Head Merge
    render_scene_3d(
        items,
        "Head_Assembly_Pod_Merge_Closeup.png",
        "Close-Up: Continuous Top/Bottom Cheeks Enclosing Spring & Gear",
        elev=45, azim=-65, zoom_factor=1.55, exploded=False, center_offset=[0, 8, 0]
    )


if __name__ == "__main__":
    main()
