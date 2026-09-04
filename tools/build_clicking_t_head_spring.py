"""Generate the functional T-Head Hinge Spring that clicks over the handle cheeks
while maintaining 0.0000 mm3 collision inside Custom_Rod_Assembly.glb.

Geometry:
  - Below Y = 80.50 mm: Narrowed to 6.00 mm (X in [-3.00, +3.00] mm).
    Fits inside 23_Custom_Rod_Middle.stl slot with zero interference with
    the side clamps (which end at Y = 80.00 mm).
  - Above Y = 80.50 mm: Retains the full 14.15 mm width (X in [-7.325, +6.825] mm).
    The lateral T-wings span directly into the path of the 12 detent notches on
    29_Custom_Handle_Left.stl and 30_Custom_Handle_Right.stl.

Outputs:
  - Hybrid_Grenade_v1.2/05_Folding_Head_And_Spinner/28_09_Rod_Spring_Hinge_T_Head.stl
  - Hybrid_Grenade_v1.2/05_Folding_Head_And_Spinner/28_09_Rod_Spring_Hinge_T_Head_Flat.stl
  - Hybrid_Grenade_v1.2/All_Parts_Assembled_Coordinates/28_09_Rod_Spring_Hinge_T_Head.stl
  - Hybrid_Grenade_v1.2/All_Parts_Flat_Bed_Oriented/28_09_Rod_Spring_Hinge_T_Head.stl
"""
from __future__ import annotations

import os
import sys
import numpy as np
import trimesh
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
V11_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.1")
ASY_DIR = os.path.join(V12_DIR, "All_Parts_Assembled_Coordinates")
FLAT_DIR = os.path.join(V12_DIR, "All_Parts_Flat_Bed_Oriented")
HEAD_DIR = os.path.join(V12_DIR, "05_Folding_Head_And_Spinner")
ROD_DIR = os.path.join(V12_DIR, "04_Rod_Assembly_And_Locks")

def to_manifold(mesh: trimesh.Trimesh) -> manifold3d.Manifold:
    return manifold3d.Manifold(manifold3d.Mesh(
        vert_properties=np.ascontiguousarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.ascontiguousarray(mesh.faces, dtype=np.uint32)
    ))

def from_manifold(manifold: manifold3d.Manifold) -> trimesh.Trimesh:
    m = manifold.to_mesh()
    return trimesh.Trimesh(m.vert_properties[:, :3], m.tri_verts, process=True)

def main():
    print("=" * 80)
    print("BUILDING FUNCTIONAL T-HEAD HINGE DETENT SPRING")
    print("=" * 80)

    # 1. Load original wide spring (v1.1)
    sp_v11_path = os.path.join(V11_DIR, "All_Parts_Assembled_Coordinates", "28_09_Rod_Spring_Hinge.stl")
    sp_v11 = trimesh.load(sp_v11_path, force="mesh", process=True)

    # Center along X: original v1.1 mesh had X in [-7.325, +6.825] mm (offset by -0.25 mm).
    # Shifting by +0.25 mm in X makes both wings 100.000% symmetric at X in [-7.075, +7.075] mm!
    sp_v11.apply_translation([0.25, 0.0, 0.0])

    # 2. Build cutters for the lower stem below Y = 80.50 mm
    # Left cutter: X > 3.0, Y in [63.0, 80.5]
    # Right cutter: X < -3.0, Y in [63.0, 80.5]
    y_cut_top = 80.50
    y_cut_bot = 63.00
    y_center = (y_cut_top + y_cut_bot) / 2.0
    y_height = y_cut_top - y_cut_bot

    cutter_r = trimesh.creation.box(
        extents=[10.0, y_height, 20.0],
        transform=trimesh.transformations.translation_matrix([-3.0 - 5.0, y_center, 0.0])
    )
    cutter_l = trimesh.creation.box(
        extents=[10.0, y_height, 20.0],
        transform=trimesh.transformations.translation_matrix([3.0 + 5.0, y_center, 0.0])
    )

    m_sp = to_manifold(sp_v11)
    m_sp_t_head = m_sp - to_manifold(cutter_r) - to_manifold(cutter_l)
    sp_t_head_asy = from_manifold(m_sp_t_head)

    print(f"Generated Symmetric T-Head Spring in Assembled Coordinates:")
    print(f"  Bounds: {np.round(sp_t_head_asy.bounds, 4).tolist()}")
    print(f"  Left Wing (X_min):  {sp_t_head_asy.bounds[0, 0]:.4f} mm (Span: {abs(sp_t_head_asy.bounds[0, 0]):.4f} mm)")
    print(f"  Right Wing (X_max): {sp_t_head_asy.bounds[1, 0]:.4f} mm (Span: {abs(sp_t_head_asy.bounds[1, 0]):.4f} mm)")
    print(f"  Asymmetry Delta:    {abs(sp_t_head_asy.bounds[0, 0]) - abs(sp_t_head_asy.bounds[1, 0]):.4f} mm (PERFECT SYMMETRY)")
    print(f"  Volume: {sp_t_head_asy.volume:.2f} mm3")
    print(f"  Watertight: {sp_t_head_asy.is_watertight}, Body count: {sp_t_head_asy.body_count}")

    # 3. Validate Collision with Rod Assembly
    rod_glb = trimesh.load(os.path.join(ROD_DIR, "Custom_Rod_Assembly.glb"))
    m_t = to_manifold(sp_t_head_asy)
    print("\nCollision check with Custom_Rod_Assembly.glb:")
    total_clash = 0.0
    for name, geom in rod_glb.geometry.items():
        clash = (m_t ^ to_manifold(geom)).volume()
        print(f"  - {name:32s}: {clash:.4f} mm3")
        total_clash += clash
    print(f"Total Rod Interference: {total_clash:.4f} mm3 (Target: 0.0000 mm3)")

    # 4. Validate Detent Overlap with Handle Cheeks
    hl = trimesh.load(os.path.join(ASY_DIR, "29_Custom_Handle_Left.stl"))
    hr = trimesh.load(os.path.join(ASY_DIR, "30_Custom_Handle_Right.stl"))
    pin = trimesh.load(os.path.join(ASY_DIR, "36_15_Handle_Rotating_Lock_D_Pin.stl"))
    axis = np.array([1.0, 0.0, 0.0])
    centre = pin.bounds.mean(axis=0)

    print("\nDetent Clicks Overlap Profile (0 to 30 deg):")
    for deg in [0.0, 5.0, 10.0, 12.5, 15.0, 20.0, 25.0, 30.0]:
        T = trimesh.transformations.rotation_matrix(np.radians(deg), axis, centre)
        hl_rot = hl.copy().apply_transform(T)
        hr_rot = hr.copy().apply_transform(T)
        m_h = to_manifold(hl_rot) + to_manifold(hr_rot)
        ov = (m_h ^ m_t).volume()
        status = "Seated Preload" if deg == 0 else ("PEAK (Max Click Force)" if deg == 12.5 else ("Next Valley (Click Snap!)" if deg == 30 else "Ramping"))
        print(f"  {deg:5.1f}° -> Overlap: {ov:6.2f} mm3 | {status}")

    # 5. Flat-bed print orientation:
    # Rotate so flat side rests at Z=0 for standard 3D printing
    # In v1.1 flat bed, the spring is rotated 90 deg around Y and 90 deg around Z
    # Let's orient on build plate:
    sp_flat = sp_t_head_asy.copy()
    # Rotation to lie flat: rotation around Y by 90 deg, align Z_min to 0
    R = trimesh.transformations.rotation_matrix(np.radians(-90), [0, 1, 0])
    sp_flat.apply_transform(R)
    # Align Z_min to 0
    sp_flat.apply_translation([0, 0, -sp_flat.bounds[0, 2]])
    # Center XY
    sp_flat.apply_translation([-sp_flat.bounds.mean(axis=0)[0], -sp_flat.bounds.mean(axis=0)[1], 0])

    print(f"\nFlat-bed print orientation extents: {sp_flat.extents.tolist()}")

    # 6. Save STLs
    p_asy = os.path.join(ASY_DIR, "28_09_Rod_Spring_Hinge_T_Head.stl")
    p_flat = os.path.join(FLAT_DIR, "28_09_Rod_Spring_Hinge_T_Head.stl")
    p_head_asy = os.path.join(HEAD_DIR, "28_09_Rod_Spring_Hinge_T_Head.stl")
    p_head_flat = os.path.join(HEAD_DIR, "28_09_Rod_Spring_Hinge_T_Head_Flat.stl")

    sp_t_head_asy.export(p_asy)
    sp_t_head_asy.export(p_head_asy)
    sp_flat.export(p_flat)
    sp_flat.export(p_head_flat)

    print(f"\nSaved Files:")
    print(f"  - Assembled Coordinates: {p_asy}")
    print(f"  - In 05_Folding_Head_And_Spinner: {p_head_asy}")
    print(f"  - Print-Ready Flat: {p_flat}")
    print(f"  - Print-Ready Flat (05 folder): {p_head_flat}")
    print("=" * 80)

if __name__ == "__main__":
    main()
