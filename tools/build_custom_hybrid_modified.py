"""Build the updated Compact Tactical/Spinner Hybrid Grenade assembly using modified parts.

Loads updated components directly from:
  Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/

Outputs:
  - Derivatives/custom/Custom_Hybrid_Grenade_Modified_assembled.glb
  - Derivatives/custom/Custom_Hybrid_Grenade_Modified_exploded.glb
  - Derivatives/custom/Custom_Hybrid_Grenade_Modified_assembled.3mf
  - Derivatives/custom/Custom_Hybrid_Grenade_Modified_exploded.3mf
  - Derivatives/custom/Custom_Hybrid_Grenade_Modified.stl
  - Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/Custom_Hybrid_Grenade_Modified_assembled.glb
  - Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click_Modified/Custom_Hybrid_Grenade_Modified_exploded.glb
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import assembly as A
import build_custom_hybrid as BCH
import custom
import fidget

MOD_DIR = os.path.join(
    ROOT_DIR, "Derivatives", "custom", "Complete_STL_Set", "Custom_Hybrid_Grenade_Modified"
)
CUSTOM_DIR = os.path.join(ROOT_DIR, "Derivatives", "custom")
STL_SHELL_SEPARATION = 1e-4

# Distinct, vibrant, harmonious PBR color palette for all 32 parts
PART_COLORS = {
    # Base Stack (Bottom to Mid)
    "04 - Bottom Shell 01": (214, 93, 84),              # Coral Red
    "05 - Bottom Shell 02": (93, 150, 209),             # Slate Blue
    "06 - Bottom Shell 03": (122, 181, 102),            # Olive Green
    "01 - Bottom Lock Shell": (228, 169, 73),           # Amber Gold
    "02 - Bottom Spring": (150, 120, 196),              # Purple
    "03 - Bottom Shell Spacer": (86, 182, 178),         # Teal
    "32 - Mid Shell P02": (219, 124, 171),              # Rose / Magenta
    "33 - Mid Shell P01": (160, 168, 74),               # Khaki / Lime
    "20 - Mid Shell Spring": (110, 132, 203),           # Cobalt Blue
    # Internal Barrel & Upper Shell
    "08 - Internal Barrel (Compact Hybrid)": (206, 140, 90),           # Terracotta
    "07 - Internal Barrel Cap": (178, 152, 88),                        # Gold Ochre
    "28 - Upper Shell Gear (32-Click Hybrid)": (139, 175, 198),        # Sky Blue
    "29 - Upper Shell Lock Ring": (203, 116, 102),                     # Rust Orange
    "30 - Upper Shell Rotating Spring": (114, 169, 180),                # Aquamarine
    "27 - Upper Shell Top (Compact Chamber)": (171, 138, 180),         # Lavender
    # Clean Functional Rod Assembly with Dual Cross-Springs (from build_custom_rod_with_springs)
    "Custom Rod Middle (Linear Track)": (86, 182, 178),                # Cyan / Teal
    "11 - Middle Spring (Z-Axis Detent)": (98, 176, 140),              # Mint Green
    "12 - Optional Middle Spring (X-Axis Detent)": (196, 104, 133),     # Berry Pink
    "Custom Rod Right (Side Clamp)": (148, 176, 120),                  # Sage Green
    "Custom Rod Left (Side Clamp)": (184, 126, 152),                   # Mauve
    "Custom Rod Upper Right": (95, 143, 166),                          # Deep Teal
    "Custom Rod Upper Left": (212, 158, 120),                          # Warm Apricot
    "08 - Rod Lock (Key)": (214, 93, 84),                              # Coral Red
    "09 - Rod Spring": (228, 169, 73),                                 # Amber Gold
    # Modified Head Components
    "Custom Handle Left": (93, 150, 209),                              # Slate Blue
    "Custom Handle Right": (110, 132, 203),                            # Cobalt Blue
    "Custom Ring Spinner": (122, 181, 102),                            # Olive Green
    "Spinner Lever 05 - Gear": (219, 124, 171),                        # Rose / Magenta
    "Spinner Lever 04 - Spring": (206, 140, 90),                       # Terracotta Orange
    "Custom 16 Handle Lock (Neck)": (150, 120, 196),                    # Purple
    "Custom 16 Handle Lock (Pod)": (184, 126, 152),                     # Mauve
    "15 - Handle Rotating Lock": (160, 168, 74),                       # Lime / Khaki
}


def build_modified_hybrid_items() -> list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]:
    """Assemble all 32 components using the latest rod, cross-springs, and modified head parts."""
    import build_custom_rod_with_springs as BRS

    # 1. Base items (without duplicate Middle Spring detents)
    base_raw = BCH.build_base()
    base = [(n, m) for n, m in base_raw if "Middle Spring" not in n]

    # 2. Rod and dual cross-detent items from BRS
    rod_items_raw = BRS.build_functional_rod_with_cross_springs_items()
    rod = [(n, m) for n, m, _ in rod_items_raw]

    # 3. Head parts
    left = trimesh.load(os.path.join(MOD_DIR, "Custom_Handle_Left.stl"))
    right = trimesh.load(os.path.join(MOD_DIR, "Custom_Handle_Right.stl"))
    ring = trimesh.load(os.path.join(MOD_DIR, "Custom_Ring_Spinner.stl"))
    neck_lock = trimesh.load(os.path.join(MOD_DIR, "Custom_16_Handle_Lock.stl"))
    pod_lock = trimesh.load(os.path.join(MOD_DIR, "Custom_16_Handle_Lock_pod.stl"))
    rot_lock = trimesh.load(os.path.join(MOD_DIR, "15 - Handle Rotating Lock.stl"))

    gear_p = custom.gear_posed()
    spring_p = custom.gear_spring_arm()

    head_raw = [
        ("Custom Handle Left", left),
        ("Custom Handle Right", right),
        ("Custom Ring Spinner", ring),
        ("Spinner Lever 05 - Gear", gear_p),
        ("Spinner Lever 04 - Spring", spring_p),
        ("Custom 16 Handle Lock (Neck)", neck_lock),
        ("Custom 16 Handle Lock (Pod)", pod_lock),
        ("15 - Handle Rotating Lock", rot_lock),
    ]

    # Transform head from Head frame to Assembled Grenade frame
    M = custom.module_transform()
    head = []
    for name, mesh in head_raw:
        m = mesh.copy()
        m.apply_transform(M)
        head.append((name, m))

    all_raw = base + rod + head
    items = []
    for name, m in all_raw:
        color = PART_COLORS.get(name, (180, 180, 180))
        items.append((name, m, color))

    return items


def compute_hybrid_exploded_displacements(items: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]) -> np.ndarray:
    """Compute clear, structured exploded displacements for the full Hybrid Grenade."""
    n = len(items)
    disp = np.zeros((n, 3))
    idx = {name: i for i, (name, _, _) in enumerate(items)}

    # Bottom stack (displace downwards in -Y)
    disp[idx["04 - Bottom Shell 01"]] = [0.0, -42.0, 0.0]
    disp[idx["05 - Bottom Shell 02"]] = [0.0, -30.0, 0.0]
    disp[idx["06 - Bottom Shell 03"]] = [0.0, -18.0, 0.0]
    disp[idx["01 - Bottom Lock Shell"]] = [0.0, -32.0, 0.0]
    disp[idx["02 - Bottom Spring"]] = [0.0, -22.0, 0.0]
    disp[idx["03 - Bottom Shell Spacer"]] = [0.0, -12.0, 0.0]

    # Mid Shell & Waist Detent (radial X / Z spread)
    disp[idx["32 - Mid Shell P02"]] = [28.0, 0.0, 0.0]
    disp[idx["33 - Mid Shell P01"]] = [-28.0, 0.0, 0.0]
    disp[idx["20 - Mid Shell Spring"]] = [0.0, 0.0, 26.0]

    # Barrel remains reference anchor
    disp[idx["08 - Internal Barrel (Compact Hybrid)"]] = [0.0, 0.0, 0.0]

    # Upper Station (displace upwards in +Y)
    disp[idx["07 - Internal Barrel Cap"]] = [0.0, 16.0, 0.0]
    disp[idx["29 - Upper Shell Lock Ring"]] = [0.0, 20.0, 0.0]
    disp[idx["28 - Upper Shell Gear (32-Click Hybrid)"]] = [0.0, 26.0, 0.0]
    disp[idx["30 - Upper Shell Rotating Spring"]] = [0.0, 36.0, 0.0]
    disp[idx["27 - Upper Shell Top (Compact Chamber)"]] = [0.0, 48.0, 0.0]

    # Rod Members & Cross Springs (lifted out of the barrel to expose the full rod & both holes)
    rod_lift = 45.0
    disp[idx["Custom Rod Middle (Linear Track)"]] = [0.0, rod_lift, 0.0]
    disp[idx["11 - Middle Spring (Z-Axis Detent)"]] = [0.0, rod_lift, 32.0]
    disp[idx["12 - Optional Middle Spring (X-Axis Detent)"]] = [32.0, rod_lift, 0.0]
    disp[idx["Custom Rod Right (Side Clamp)"]] = [22.0, rod_lift, 0.0]
    disp[idx["Custom Rod Left (Side Clamp)"]] = [-22.0, rod_lift, 0.0]
    disp[idx["Custom Rod Upper Right"]] = [16.0, rod_lift + 14.0, 0.0]
    disp[idx["Custom Rod Upper Left"]] = [-16.0, rod_lift + 14.0, 0.0]
    disp[idx["08 - Rod Lock (Key)"]] = [0.0, rod_lift, -26.0]
    disp[idx["09 - Rod Spring"]] = [0.0, rod_lift + 28.0, 0.0]

    # Head Components (lifted above rod and parted along X / Z)
    head_lift = rod_lift + 30.0
    disp[idx["15 - Handle Rotating Lock"]] = [36.0, head_lift + 10.0, 0.0]
    disp[idx["Custom Handle Left"]] = [-30.0, head_lift + 10.0, 0.0]
    disp[idx["Custom Handle Right"]] = [30.0, head_lift + 10.0, 0.0]
    disp[idx["Custom Ring Spinner"]] = [0.0, head_lift + 10.0, -32.0]
    disp[idx["Spinner Lever 05 - Gear"]] = [0.0, head_lift + 10.0, -20.0]
    disp[idx["Spinner Lever 04 - Spring"]] = [0.0, head_lift + 10.0, -8.0]
    disp[idx["Custom 16 Handle Lock (Neck)"]] = [36.0, head_lift + 10.0, -14.0]
    disp[idx["Custom 16 Handle Lock (Pod)"]] = [36.0, head_lift + 10.0, -28.0]

    return disp



def colourize_3mf(path: str, coloured: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]) -> int:
    """Inject BaseMaterials palette into exported 3MF archive."""
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
    material_id = max(
        [int(child.get("id")) for child in resources if child.get("id")], default=0
    ) + 1
    materials = ET.Element(q("basematerials"), {"id": str(material_id)})
    resources.insert(0, materials)
    for obj in objects:
        name = obj.get("name")
        if name not in colours:
            continue
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
        prefix="hybrid_mod_", suffix=".tmp", dir=os.path.dirname(path), delete=False
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


def build_and_export_all():
    """Build all models, validate, report metrics, and export files."""
    items = build_modified_hybrid_items()

    print(f"Loaded {len(items)} components for Custom Hybrid Grenade (Modified).")

    # Validate watertightness & single-body
    bad = [
        (name, m.is_watertight, m.body_count)
        for name, m, _ in items
        if not m.is_watertight or m.body_count != 1
    ]
    if bad:
        raise RuntimeError(f"Non-watertight or multi-body parts: {bad}")

    # Build Assembled Scene
    assembled = A.scene(items)

    # Build Exploded Scene
    displacements = compute_hybrid_exploded_displacements(items)
    exploded = A.scene(items, displacements)

    # Build Merged STL
    centre = (len(items) - 1) / 2.0
    shells = []
    for index, (name, mesh, _) in enumerate(items):
        shell = BCH._stl_safe_mesh(mesh, name)
        delta = (index - centre) * STL_SHELL_SEPARATION
        shell.apply_translation([delta, 0.317 * delta, 0.173 * delta])
        shells.append(shell)
    flattened = trimesh.util.concatenate(shells)

    # Targets to save
    export_dirs = [CUSTOM_DIR, MOD_DIR]

    for export_dir in export_dirs:
        stem = "Custom_Hybrid_Grenade_Modified"

        # 1. Assembled GLB
        glb_ass_path = os.path.join(export_dir, f"{stem}_assembled.glb")
        with open(glb_ass_path, "wb") as f:
            f.write(trimesh.exchange.gltf.export_glb(assembled))
        print(f"Saved: {glb_ass_path} ({os.path.getsize(glb_ass_path):,} bytes)")

        # 2. Exploded GLB
        glb_exp_path = os.path.join(export_dir, f"{stem}_exploded.glb")
        with open(glb_exp_path, "wb") as f:
            f.write(trimesh.exchange.gltf.export_glb(exploded))
        print(f"Saved: {glb_exp_path} ({os.path.getsize(glb_exp_path):,} bytes)")

        # 3. Assembled 3MF
        path_3mf_ass = os.path.join(export_dir, f"{stem}_assembled.3mf")
        with open(path_3mf_ass, "wb") as f:
            f.write(trimesh.exchange.threemf.export_3MF(assembled))
        colourize_3mf(path_3mf_ass, items)
        print(f"Saved: {path_3mf_ass} ({os.path.getsize(path_3mf_ass):,} bytes)")

        # 4. Exploded 3MF
        path_3mf_exp = os.path.join(export_dir, f"{stem}_exploded.3mf")
        with open(path_3mf_exp, "wb") as f:
            f.write(trimesh.exchange.threemf.export_3MF(exploded))
        colourize_3mf(path_3mf_exp, items)
        print(f"Saved: {path_3mf_exp} ({os.path.getsize(path_3mf_exp):,} bytes)")

        # 5. Merged STL
        stl_path = os.path.join(export_dir, f"{stem}.stl")
        with open(stl_path, "wb") as f:
            f.write(trimesh.exchange.stl.export_stl(flattened))
    # Export individual redesigned STLs to MOD_DIR
    by_item_name = {name: mesh for name, mesh, _ in items}
    mod_stl_map = {
        "Hybrid_08_Internal_Barrel.stl": by_item_name["08 - Internal Barrel (Compact Hybrid)"],
        "Hybrid_11_Middle_Spring.stl": by_item_name["11 - Middle Spring (Z-Axis Detent)"],
        "Hybrid_12_Optional_Middle_Spring.stl": by_item_name["12 - Optional Middle Spring (X-Axis Detent)"],
        "Hybrid_27_Upper_Shell_Top_Chamber.stl": by_item_name["27 - Upper Shell Top (Compact Chamber)"],
        "Hybrid_28_Upper_Shell_Gear_32_Click.stl": by_item_name["28 - Upper Shell Gear (32-Click Hybrid)"],
    }
    for fname, mesh in mod_stl_map.items():
        out_stl = os.path.join(MOD_DIR, fname)
        with open(out_stl, "wb") as f:
            f.write(trimesh.exchange.stl.export_stl(BCH._stl_safe_mesh(mesh, fname)))
        print(f"Saved Individual STL: {out_stl} ({os.path.getsize(out_stl):,} bytes)")

    # Bounds & Envelopes
    bounds = np.array([m.bounds for _, m, _ in items])
    envelope = bounds[:, 1].max(axis=0) - bounds[:, 0].min(axis=0)
    print("\n--- HYBRID GRENADE (MODIFIED) VALIDATION REPORT ---")
    print(f"  Total Part Count:         {len(items)} components")
    print(f"  Watertight Solids:        {len(items)} / {len(items)} (100% Watertight)")
    print(f"  Total Envelope (XYZ mm):  {np.round(envelope, 2).tolist()}")
    print(f"  Fits in Box (42x122x73):  {(envelope <= np.array([42.0, 122.0, 73.0]) + 1e-4).all()}")

    # Pairwise interference
    bad = A.interference([(name, m) for name, m, _ in items], min_mm3=0.001)
    print(f"  Pairwise Interferences:   {len(bad)} pairs detected")
    for v, a, b in bad:
        print(f"    {v:8.4f} mm3  |  {a} / {b}")


if __name__ == "__main__":
    build_and_export_all()
