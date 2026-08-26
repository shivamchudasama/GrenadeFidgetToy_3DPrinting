"""Build, validate, and export the Clean Functional Custom Rod Assembly WITH Dual Cross-Springs (11 & 12).

Custom_Rod_Upper_Lock has been removed and the transverse hole filled in:
  - Custom Rod Middle
  - Custom Rod Upper Left
  - Custom Rod Upper Right

This 9-component assembly includes:
  1. Custom Rod Middle (Linear Track with solid linear gear teeth on Z = +-6.89mm, solid upper yoke)
  2. 11 - Middle Spring (Primary detent along Z-axis: inner teeth engage the rod's linear gear rack;
     outer lobes engage the rotary ratchet)
  3. 12 - Optional Middle Spring (Secondary detent along X-axis, 90 deg apart: quadruples rotary detent clicks)
  4. Custom Rod Right (Side clamp plate)
  5. Custom Rod Left (Side clamp plate)
  6. Custom Rod Upper Right (Upper yoke cap, solid, no keyway hole)
  7. Custom Rod Upper Left (Upper yoke cap, solid, no keyway hole)
  8. 08 - Rod Lock (Transverse retention key)
  9. 09 - Rod Spring (Upper hinge leaf detent spring)

Outputs:
  - Derivatives/custom/Custom_Rod_With_Springs_assembled.glb
  - Derivatives/custom/Custom_Rod_With_Springs_exploded.glb
  - Derivatives/custom/Custom_Rod_With_Springs_assembled.3mf
  - Derivatives/custom/Custom_Rod_With_Springs_exploded.3mf
  - Derivatives/custom/Custom_Rod_With_Springs.stl
  - Derivatives/custom/Custom_Rod_With_Springs_assembly_viewer.html
"""
from __future__ import annotations

import base64
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

CUSTOM_DIR = os.path.join(ROOT_DIR, "Derivatives", "custom")
MOD_DIR = os.path.join(
    ROOT_DIR, "Derivatives", "custom", "Complete_STL_Set", "Custom_Hybrid_Grenade_Modified"
)
STL_SHELL_SEPARATION = 1e-4

# Distinct, harmonious color palette for the 9 cross-spring rod components
ROD_SPRING_COLORS = {
    "Custom Rod Middle (Linear Track)": (86, 182, 178),           # Cyan / Teal
    "11 - Middle Spring (Z-Axis Detent)": (98, 176, 140),         # Mint Green (Z-axis leaf arms)
    "12 - Optional Middle Spring (X-Axis Detent)": (196, 104, 133), # Berry Pink (X-axis leaf arms, 90 deg apart)
    "Custom Rod Right (Side Clamp)": (148, 176, 120),             # Sage Green
    "Custom Rod Left (Side Clamp)": (184, 126, 152),              # Mauve
    "Custom Rod Upper Right": (95, 143, 166),                     # Deep Teal (Solid, no hole)
    "Custom Rod Upper Left": (212, 158, 120),                     # Warm Apricot (Solid, no hole)
    "08 - Rod Lock (Key)": (214, 93, 84),                         # Coral Red
    "09 - Rod Spring": (228, 169, 73),                            # Amber Gold
}


def build_functional_rod_with_cross_springs_items() -> list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]:
    """Assemble all 9 components with filled upper yoke (no Upper Lock keyway)."""
    rot90_y = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])
    trim_lower = trimesh.creation.box(
        extents=[80.0, 200.0, 80.0],
        transform=trimesh.transformations.translation_matrix([0.0, 62.0 - 100.0, 0.0])
    )

    # 1. Base Spinner Fuse 07 Linear Track trimmed below Y=62.0, with lower relic hole (Y=58.13) filled perfectly planar
    sp_07 = fidget.load("07 - Rod Middle Linear Track", product="spinner")
    r_07 = sp_07.copy().apply_transform(rot90_y)
    r_07_lower = fidget.intersect(r_07, trim_lower)
    box_m = trimesh.creation.box(
        extents=[3.75, 6.0, 6.0],
        transform=trimesh.transformations.translation_matrix([0.0, 58.0, 0.0])
    )
    r_07_solid = fidget.union(r_07_lower, box_m)

    # 2. Upper hinge yoke track without lock hole
    source_track = fidget.load(custom.YOKE_SRC[2], product="spinner")
    track_solid = fidget.intersect(source_track, custom._yoke_keep(0.0))
    track_solid.apply_transform(custom.module_transform())

    # Union into complete custom rod middle (seamless lower track, no unused lower hole, only active upper hinge hole)
    c_mid_linear = fidget.union(r_07_solid, track_solid)

    # 3. 09 - Rod Spring (hinge leaf spring)
    spring_raw = fidget.load("09 - Rod Spring", product="spinner")
    spring_posed = spring_raw.copy()
    spring_posed.apply_transform(custom.module_transform())

    # 4. Upper caps without lock hole
    source_right = fidget.load(custom.YOKE_SRC[0], product="spinner")
    source_left = fidget.load(custom.YOKE_SRC[1], product="spinner")
    u_right_solid = fidget.intersect(source_right, custom._yoke_keep(0.5)).apply_transform(custom.module_transform())
    u_left_solid = fidget.intersect(source_left, custom._yoke_keep(0.5)).apply_transform(custom.module_transform())

    # 5. Side clamp plates below Y=62.0, with lower relic hole pockets (Y=58.13) filled perfectly planar (zero residue)
    sp_05 = fidget.load("05 - Rod Middle Right", product="spinner")
    sp_06 = fidget.load("06 - Rod Middle Left", product="spinner")
    r_05 = sp_05.copy().apply_transform(rot90_y)
    r_06 = sp_06.copy().apply_transform(rot90_y)
    side_right = fidget.intersect(r_05, trim_lower)
    side_left = fidget.intersect(r_06, trim_lower)
    box_r = trimesh.creation.box(
        extents=[3.575 - 1.875, 6.0, 6.0],
        transform=trimesh.transformations.translation_matrix([(1.875 + 3.575)/2, 58.0, 0.0])
    )
    box_l = trimesh.creation.box(
        extents=[3.575 - 1.875, 6.0, 6.0],
        transform=trimesh.transformations.translation_matrix([(-1.875 - 3.575)/2, 58.0, 0.0])
    )
    side_right_solid = fidget.union(side_right, box_r)
    side_left_solid = fidget.union(side_left, box_l)

    # 6. Lower transverse key: 08 - Rod Lock
    sp_08 = fidget.load("08 - Rod Lock", product="spinner")
    r_08 = sp_08.copy().apply_transform(rot90_y)

    # 7. Restored pristine 11 - Middle Spring (along Z-axis)
    s11_raw = fidget.load("11 - Middle Spring", product="spinner")
    s11_z = s11_raw.copy().apply_transform(rot90_y)

    # 8. Restored pristine 12 - Optional Middle Spring (along X-axis, 90 deg apart)
    s12_raw = fidget.load("12 - Optional Middle Spring", product="spinner")
    s12_x = s12_raw.copy()
    s12_x.apply_translation(-s12_x.bounds.mean(axis=0))
    rot180_z = trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1])
    s12_x.apply_transform(rot180_z)
    s12_x.apply_translation(s11_raw.bounds.mean(axis=0))

    raw_items = [
        ("Custom Rod Middle (Linear Track)", c_mid_linear),
        ("11 - Middle Spring (Z-Axis Detent)", s11_z),
        ("12 - Optional Middle Spring (X-Axis Detent)", s12_x),
        ("Custom Rod Right (Side Clamp)", side_right_solid),
        ("Custom Rod Left (Side Clamp)", side_left_solid),
        ("Custom Rod Upper Right", u_right_solid),
        ("Custom Rod Upper Left", u_left_solid),
        ("08 - Rod Lock (Key)", r_08),
        ("09 - Rod Spring", spring_posed),
    ]

    items = []
    for name, mesh in raw_items:
        color = ROD_SPRING_COLORS.get(name, (180, 180, 180))
        items.append((name, mesh, color))

    return items


def compute_functional_rod_displacements(
    items: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]
) -> np.ndarray:
    """Compute exploded displacements separating the 90-deg cross-springs and rod clamps."""
    n = len(items)
    disp = np.zeros((n, 3))
    idx = {name: i for i, (name, _, _) in enumerate(items)}

    # Middle Rod remains as anchor
    disp[idx["Custom Rod Middle (Linear Track)"]] = [0.0, 0.0, 0.0]

    # Lower side clamp plates pull outwards in -X / +X
    disp[idx["Custom Rod Right (Side Clamp)"]] = [24.0, 0.0, 0.0]
    disp[idx["Custom Rod Left (Side Clamp)"]] = [-24.0, 0.0, 0.0]

    # Upper yoke caps pull outwards and upwards
    disp[idx["Custom Rod Upper Right"]] = [16.0, 14.0, 0.0]
    disp[idx["Custom Rod Upper Left"]] = [-16.0, 14.0, 0.0]

    # Transverse rod lock key pulls out along -Z
    disp[idx["08 - Rod Lock (Key)"]] = [0.0, 0.0, -24.0]

    # Top hinge spring pulls up along +Y
    disp[idx["09 - Rod Spring"]] = [0.0, 26.0, 0.0]

    # 11 - Middle Spring pulls forward along +Z
    disp[idx["11 - Middle Spring (Z-Axis Detent)"]] = [0.0, 0.0, 30.0]

    # 12 - Optional Middle Spring pulls out along -X (or +X)
    disp[idx["12 - Optional Middle Spring (X-Axis Detent)"]] = [30.0, 0.0, 0.0]

    return disp


def colourize_3mf(
    path: str, coloured: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]
) -> int:
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
        prefix="rod_cross_spring_mod_", suffix=".tmp", dir=os.path.dirname(path), delete=False
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


def build_interactive_rod_spring_viewer(
    items: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]],
    displacements: np.ndarray,
    glb_assembled_bytes: bytes,
    output_html_path: str,
):
    """Generate standalone self-contained 3D HTML viewer for the Clean Dual Cross-Springs assembly."""
    glb_b64 = base64.b64encode(glb_assembled_bytes).decode("ascii")

    parts_meta = []
    for (name, m, color), disp in zip(items, displacements):
        vol = m.volume
        bb = m.bounds
        ext = bb[1] - bb[0]
        parts_meta.append({
            "name": name,
            "color": list(color),
            "volume_mm3": round(float(vol), 1),
            "extents_mm": [round(float(x), 2) for x in ext],
            "bounds_min": [round(float(x), 2) for x in bb[0]],
            "bounds_max": [round(float(x), 2) for x in bb[1]],
            "disp": [round(float(d), 2) for d in disp],
        })

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Clean Custom Rod with Dual Cross-Springs (90° Apart) - 3D Viewer</title>
  <style>
    :root {{
      --bg-gradient: radial-gradient(circle at 50% 30%, #161b26 0%, #0a0c10 100%);
      --panel-bg: rgba(22, 27, 34, 0.92);
      --panel-border: rgba(255, 255, 255, 0.14);
      --accent: #58a6ff;
      --accent-glow: rgba(88, 166, 255, 0.4);
      --spring-accent: #3fb950;
      --spring-opt: #f778ba;
      --text-main: #f0f6fc;
      --text-muted: #8b949e;
      --card-bg: rgba(13, 17, 23, 0.85);
      --success: #3fb950;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg-gradient);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
    }}

    #canvas-container {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
    }}

    /* Floating Header */
    .header {{
      position: absolute;
      top: 20px;
      left: 24px;
      z-index: 10;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      padding: 16px 22px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
      max-width: 520px;
    }}

    .header h1 {{
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #fff;
    }}

    .badge {{
      background: rgba(63, 185, 80, 0.2);
      border: 1px solid var(--success);
      color: var(--success);
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 20px;
      text-transform: uppercase;
      font-weight: 600;
    }}

    .header p {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 6px;
      line-height: 1.4;
    }}

    /* Bottom Control Bar */
    .control-bar {{
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 40px;
      padding: 10px 24px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
    }}

    .slider-group {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .slider-group label {{
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--accent);
    }}

    input[type=range] {{
      -webkit-appearance: none;
      width: 170px;
      height: 6px;
      border-radius: 3px;
      background: rgba(255, 255, 255, 0.2);
      outline: none;
    }}

    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--accent);
      cursor: pointer;
      box-shadow: 0 0 10px var(--accent-glow);
      transition: transform 0.1s;
    }}

    input[type=range]::-webkit-slider-thumb:hover {{
      transform: scale(1.2);
    }}

    .btn {{
      background: var(--card-bg);
      border: 1px solid var(--panel-border);
      color: var(--text-main);
      padding: 8px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .btn:hover {{
      background: rgba(88, 166, 255, 0.2);
      border-color: var(--accent);
      color: #fff;
    }}

    .btn.active {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}

    /* Sidebar: Parts List & Inspector */
    .sidebar {{
      position: absolute;
      top: 20px;
      right: 24px;
      width: 360px;
      max-height: calc(100vh - 40px);
      z-index: 10;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
      overflow: hidden;
    }}

    .sidebar-header {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--panel-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .sidebar-header h2 {{
      font-size: 14px;
      font-weight: 700;
      color: #fff;
    }}

    .parts-scroll {{
      overflow-y: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .parts-scroll::-webkit-scrollbar {{
      width: 5px;
    }}
    .parts-scroll::-webkit-scrollbar-thumb {{
      background: rgba(255, 255, 255, 0.2);
      border-radius: 3px;
    }}

    .part-item {{
      background: var(--card-bg);
      border: 1px solid var(--panel-border);
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .part-item:hover {{
      border-color: var(--accent);
      transform: translateY(-1px);
    }}

    .part-item.selected {{
      border-color: var(--accent);
      background: rgba(88, 166, 255, 0.15);
      box-shadow: 0 0 12px rgba(88, 166, 255, 0.25);
    }}

    .part-item.spring-z {{
      border-color: var(--spring-accent);
      background: rgba(63, 185, 80, 0.12);
    }}

    .part-item.spring-x {{
      border-color: var(--spring-opt);
      background: rgba(247, 120, 186, 0.12);
    }}

    .part-header {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .color-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      flex-shrink: 0;
      border: 1px solid rgba(255, 255, 255, 0.4);
    }}

    .part-name {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .part-details {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 6px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px;
    }}

    /* Loading Overlay */
    #loading {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #0d1117;
      z-index: 100;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: opacity 0.5s;
    }}

    .spinner {{
      width: 48px;
      height: 48px;
      border: 4px solid rgba(88, 166, 255, 0.2);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 1s infinite linear;
    }}

    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}

    #loading p {{
      margin-top: 16px;
      font-size: 14px;
      color: var(--text-muted);
      letter-spacing: 0.5px;
    }}
  </style>
  <script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
  <script src="https://unpkg.com/three@0.160.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://unpkg.com/three@0.160.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>

  <div id="loading">
    <div class="spinner"></div>
    <p>Loading Clean Dual Cross-Spring Rod Assembly...</p>
  </div>

  <div class="header">
    <h1>Clean Custom Rod with Dual Cross-Springs <span class="badge">90° Cross / Solid Yoke</span></h1>
    <p>Cleaned yoke architecture (Upper Lock removed, solid walls). Dual 3D-printable leaf springs (11 along Z-axis & 12 along X-axis). Inner teeth engage linear gear track; 4-way outer lobes engage rotary ratchet.</p>
  </div>

  <div id="canvas-container"></div>

  <div class="control-bar">
    <div class="slider-group">
      <label for="explode-slider">Explode</label>
      <input type="range" id="explode-slider" min="0" max="1" step="0.005" value="0">
    </div>
    <button class="btn" id="btn-animate">Play Animation</button>
    <button class="btn" id="btn-focus-11">Focus 11 (Z)</button>
    <button class="btn" id="btn-focus-12">Focus 12 (X)</button>
    <button class="btn" id="btn-wireframe">Wireframe</button>
    <button class="btn" id="btn-reset">Reset View</button>
  </div>

  <div class="sidebar">
    <div class="sidebar-header">
      <h2>Assembly Components (9)</h2>
      <span class="badge" style="background:rgba(88,166,255,0.2); color:var(--accent); border-color:var(--accent);">100% Watertight</span>
    </div>
    <div class="parts-scroll" id="parts-list"></div>
  </div>

  <script>
    const PARTS_DATA = {json.dumps(parts_meta)};
    const GLB_B64 = "{glb_b64}";

    let scene, camera, renderer, controls;
    let meshesMap = new Map();
    let selectedMesh = null;
    let isWireframe = false;
    let isAnimating = false;
    let animDir = 1;

    function init() {{
      const container = document.getElementById('canvas-container');
      scene = new THREE.Scene();

      camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
      camera.position.set(55, 60, 110);

      renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.2;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      container.appendChild(renderer.domElement);

      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.target.set(0, 50, 0);

      // Lighting
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
      scene.add(ambientLight);

      const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.6);
      dirLight1.position.set(100, 150, 100);
      dirLight1.castShadow = true;
      scene.add(dirLight1);

      const dirLight2 = new THREE.DirectionalLight(0x58a6ff, 0.9);
      dirLight2.position.set(-100, 50, -100);
      scene.add(dirLight2);

      const pointLight = new THREE.PointLight(0xffffff, 0.6);
      pointLight.position.set(0, -40, 50);
      scene.add(pointLight);

      // Ground shadow plane
      const planeGeo = new THREE.PlaneGeometry(300, 300);
      const planeMat = new THREE.ShadowMaterial({{ opacity: 0.25 }});
      const plane = new THREE.Mesh(planeGeo, planeMat);
      plane.rotation.x = -Math.PI / 2;
      plane.position.y = 10;
      plane.receiveShadow = true;
      scene.add(plane);

      loadModel();
      buildPartsList();
      setupEvents();
      animate();
    }}

    function loadModel() {{
      const loader = new THREE.GLTFLoader();
      const binary = atob(GLB_B64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {{
        bytes[i] = binary.charCodeAt(i);
      }}

      loader.parse(bytes.buffer, '', (gltf) => {{
        gltf.scene.traverse((child) => {{
          if (child.isMesh) {{
            child.castShadow = true;
            child.receiveShadow = true;
            child.userData.origPos = child.position.clone();

            const pData = PARTS_DATA.find(p => p.name === child.name);
            if (pData) {{
              child.userData.disp = new THREE.Vector3(...pData.disp);
              child.userData.color = pData.color;
              child.material = new THREE.MeshStandardMaterial({{
                color: new THREE.Color(`rgb(${{pData.color.join(',')}})`),
                roughness: 0.35,
                metalness: 0.15,
              }});
            }}
            meshesMap.set(child.name, child);
          }}
        }});
        scene.add(gltf.scene);
        document.getElementById('loading').style.opacity = 0;
        setTimeout(() => document.getElementById('loading').style.display = 'none', 500);
      }});
    }}

    function buildPartsList() {{
      const container = document.getElementById('parts-list');
      PARTS_DATA.forEach(part => {{
        const isSpring11 = part.name.includes("11 - Middle Spring");
        const isSpring12 = part.name.includes("12 - Optional Middle Spring");
        let cls = 'part-item';
        if (isSpring11) cls += ' spring-z';
        if (isSpring12) cls += ' spring-x';

        const item = document.createElement('div');
        item.className = cls;
        item.id = `item-${{part.name.replace(/[^a-zA-Z0-9]/g, '_')}}`;
        item.innerHTML = `
          <div class="part-header">
            <div class="color-dot" style="background: rgb(${{part.color.join(',')}})"></div>
            <div class="part-name" title="${{part.name}}">${{part.name}}</div>
          </div>
          <div class="part-details">
            <span>Vol: ${{part.volume_mm3}} mm³</span>
            <span>Dim: ${{part.extents_mm.join(' × ')}}</span>
          </div>
        `;
        item.onclick = () => selectPart(part.name);
        container.appendChild(item);
      }});
    }}

    function selectPart(name) {{
      document.querySelectorAll('.part-item').forEach(el => el.classList.remove('selected'));
      const itemEl = document.getElementById(`item-${{name ? name.replace(/[^a-zA-Z0-9]/g, '_') : ''}}`);
      if (itemEl) itemEl.classList.add('selected');

      const mesh = name ? meshesMap.get(name) : null;
      if (!mesh || selectedMesh === mesh) {{
        // Deselect
        selectedMesh = null;
        meshesMap.forEach(m => {{
          m.material.opacity = 1.0;
          m.material.transparent = false;
        }});
        if (itemEl) itemEl.classList.remove('selected');
        return;
      }}

      selectedMesh = mesh;
      meshesMap.forEach(m => {{
        if (m === mesh) {{
          m.material.opacity = 1.0;
          m.material.transparent = false;
        }} else {{
          m.material.opacity = 0.22;
          m.material.transparent = true;
        }}
      }});
    }}

    function updateExplode(factor) {{
      meshesMap.forEach((mesh) => {{
        if (mesh.userData.disp) {{
          mesh.position.copy(mesh.userData.origPos).addScaledVector(mesh.userData.disp, factor);
        }}
      }});
    }}

    function setupEvents() {{
      const slider = document.getElementById('explode-slider');
      slider.oninput = (e) => {{
        isAnimating = false;
        document.getElementById('btn-animate').classList.remove('active');
        updateExplode(parseFloat(e.target.value));
      }};

      document.getElementById('btn-animate').onclick = function() {{
        isAnimating = !isAnimating;
        this.classList.toggle('active', isAnimating);
      }};

      document.getElementById('btn-focus-11').onclick = function() {{
        selectPart("11 - Middle Spring (Z-Axis Detent)");
      }};

      document.getElementById('btn-focus-12').onclick = function() {{
        selectPart("12 - Optional Middle Spring (X-Axis Detent)");
      }};

      document.getElementById('btn-wireframe').onclick = function() {{
        isWireframe = !isWireframe;
        this.classList.toggle('active', isWireframe);
        meshesMap.forEach(m => m.material.wireframe = isWireframe);
      }};

      document.getElementById('btn-reset').onclick = function() {{
        controls.reset();
        camera.position.set(55, 60, 110);
        controls.target.set(0, 50, 0);
        slider.value = 0;
        updateExplode(0);
        isAnimating = false;
        document.getElementById('btn-animate').classList.remove('active');
        selectPart(null);
      }};

      window.onresize = () => {{
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      }};
    }}

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();

      if (isAnimating) {{
        const slider = document.getElementById('explode-slider');
        let val = parseFloat(slider.value) + 0.008 * animDir;
        if (val >= 1) {{
          val = 1;
          animDir = -1;
        }} else if (val <= 0) {{
          val = 0;
          animDir = 1;
        }}
        slider.value = val;
        updateExplode(val);
      }}

      renderer.render(scene, camera);
    }}

    init();
  </script>
</body>
</html>"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated Interactive Viewer: {output_html_path} ({len(html_content):,} chars)")


def build_and_export_all():
    """Build Clean Dual Cross-Spring Custom Rod assembly, validate 0-interference, and export all assets."""
    items = build_functional_rod_with_cross_springs_items()
    print(f"\n===========================================================")
    print(f"CLEAN CUSTOM ROD WITH DUAL CROSS-SPRINGS (UPPER LOCK REMOVED)")
    print(f"===========================================================")
    print(f"Loaded {len(items)} parts for the Clean Cross-Springs assembly.\n")

    # 1. Watertightness check
    bad = [
        (name, m.is_watertight, m.body_count)
        for name, m, _ in items
        if not m.is_watertight or m.body_count != 1
    ]
    if bad:
        raise RuntimeError(f"Non-watertight or multi-body parts: {bad}")
    print("  [PASS] All 9 parts are 100% Watertight Single Solids (Upper Lock hole filled).")

    # 2. Pairwise interference check
    bad_inter = A.interference([(name, m) for name, m, _ in items], min_mm3=0.001)
    if bad_inter:
        print(f"  [FAIL] {len(bad_inter)} interferences found:")
        for v, a, b in bad_inter:
            print(f"    {v:.4f} mm3 | {a} vs {b}")
        raise RuntimeError("Interference detected in Cross-Springs assembly!")
    print("  [PASS] Zero pairwise interference detected (0.000 mm³ overlap across all 9 parts at rest).")

    # 3. Assemble and Explode scenes
    assembled = A.scene(items)
    displacements = compute_functional_rod_displacements(items)
    exploded = A.scene(items, displacements)

    # 4. Merged STL
    centre = (len(items) - 1) / 2.0
    shells = []
    for index, (name, mesh, _) in enumerate(items):
        shell = BCH._stl_safe_mesh(mesh, name)
        delta = (index - centre) * STL_SHELL_SEPARATION
        shell.apply_translation([delta, 0.317 * delta, 0.173 * delta])
        shells.append(shell)
    flattened = trimesh.util.concatenate(shells)

    # 5. Export 3MF, GLB, and STL
    export_dirs = [CUSTOM_DIR, MOD_DIR]
    glb_assembled_bytes = None

    for export_dir in export_dirs:
        stem = "Custom_Rod_With_Springs"

        # Assembled GLB
        glb_ass_path = os.path.join(export_dir, f"{stem}_assembled.glb")
        glb_data = trimesh.exchange.gltf.export_glb(assembled)
        if glb_assembled_bytes is None:
            glb_assembled_bytes = glb_data
        with open(glb_ass_path, "wb") as f:
            f.write(glb_data)
        print(f"  Saved: {glb_ass_path} ({os.path.getsize(glb_ass_path):,} bytes)")

        # Exploded GLB
        glb_exp_path = os.path.join(export_dir, f"{stem}_exploded.glb")
        with open(glb_exp_path, "wb") as f:
            f.write(trimesh.exchange.gltf.export_glb(exploded))
        print(f"  Saved: {glb_exp_path} ({os.path.getsize(glb_exp_path):,} bytes)")

        # Assembled 3MF
        path_3mf_ass = os.path.join(export_dir, f"{stem}_assembled.3mf")
        with open(path_3mf_ass, "wb") as f:
            f.write(trimesh.exchange.threemf.export_3MF(assembled))
        colourize_3mf(path_3mf_ass, items)
        print(f"  Saved: {path_3mf_ass} ({os.path.getsize(path_3mf_ass):,} bytes)")

        # Exploded 3MF
        path_3mf_exp = os.path.join(export_dir, f"{stem}_exploded.3mf")
        with open(path_3mf_exp, "wb") as f:
            f.write(trimesh.exchange.threemf.export_3MF(exploded))
        colourize_3mf(path_3mf_exp, items)
        print(f"  Saved: {path_3mf_exp} ({os.path.getsize(path_3mf_exp):,} bytes)")

        # Merged STL
        stl_path = os.path.join(export_dir, f"{stem}.stl")
        with open(stl_path, "wb") as f:
            f.write(trimesh.exchange.stl.export_stl(flattened))
        print(f"  Saved: {stl_path} ({os.path.getsize(stl_path):,} bytes)")

    # 6. Export individual printable parts to MOD_DIR (and remove old Custom_Rod_Upper_Lock.stl)
    by_item_name = {name: mesh for name, mesh, _ in items}
    mod_stl_map = {
        "Custom_Rod_Middle.stl": by_item_name["Custom Rod Middle (Linear Track)"],
        "Custom_Rod_Right.stl": by_item_name["Custom Rod Right (Side Clamp)"],
        "Custom_Rod_Left.stl": by_item_name["Custom Rod Left (Side Clamp)"],
        "Custom_Rod_Upper_Right.stl": by_item_name["Custom Rod Upper Right"],
        "Custom_Rod_Upper_Left.stl": by_item_name["Custom Rod Upper Left"],
        "11 - Middle Spring.stl": by_item_name["11 - Middle Spring (Z-Axis Detent)"],
        "Hybrid_11_Middle_Spring.stl": by_item_name["11 - Middle Spring (Z-Axis Detent)"],
        "12 - Optional Middle Spring.stl": by_item_name["12 - Optional Middle Spring (X-Axis Detent)"],
        "Hybrid_12_Optional_Middle_Spring.stl": by_item_name["12 - Optional Middle Spring (X-Axis Detent)"],
        "08 - Rod Lock.stl": by_item_name["08 - Rod Lock (Key)"],
        "09 - Rod Spring.stl": by_item_name["09 - Rod Spring"],
    }
    for fname, mesh in mod_stl_map.items():
        out_stl = os.path.join(MOD_DIR, fname)
        with open(out_stl, "wb") as f:
            f.write(trimesh.exchange.stl.export_stl(BCH._stl_safe_mesh(mesh, fname)))
        print(f"  Saved Individual STL: {out_stl} ({os.path.getsize(out_stl):,} bytes)")

    # Remove obsolete Custom_Rod_Upper_Lock.stl if present
    for d in [CUSTOM_DIR, MOD_DIR]:
        old_lock_path = os.path.join(d, "Custom_Rod_Upper_Lock.stl")
        if os.path.exists(old_lock_path):
            os.remove(old_lock_path)
            print(f"  Removed obsolete key: {old_lock_path}")

    # 7. Interactive 3D HTML Viewers
    viewer_paths = [
        os.path.join(CUSTOM_DIR, "Custom_Rod_With_Springs_assembly_viewer.html"),
        os.path.join(MOD_DIR, "Custom_Rod_With_Springs_assembly_viewer.html"),
    ]
    for vp in viewer_paths:
        build_interactive_rod_spring_viewer(items, displacements, glb_assembled_bytes, vp)

    # 8. Print Bounds & Metrology
    bounds = np.array([m.bounds for _, m, _ in items])
    envelope = bounds[:, 1].max(axis=0) - bounds[:, 0].min(axis=0)
    print("\n--- CLEAN CROSS-SPRINGS ROD METROLOGY ---")
    print(f"  Total Part Count:       {len(items)} components (Upper Lock eliminated)")
    print(f"  Bounding Envelope:      X={envelope[0]:.2f} mm, Y={envelope[1]:.2f} mm, Z={envelope[2]:.2f} mm")
    print(f"  Total Solid Volume:     {sum(m.volume for _, m, _ in items):.1f} mm³")
    print("===========================================================\n")


if __name__ == "__main__":
    build_and_export_all()
