"""Build, validate, and export the Custom Rod Assembly.

This script manages the 10 interlocking components that form the complete Custom Rod:
  1. Custom Rod Middle
  2. Custom Rod Right
  3. Custom Rod Left
  4. Custom Rod Upper Right
  5. Custom Rod Upper Left
  6. Spinner Lever 06 - Rod Lock (Upper transverse key)
  7. Spinner Lever 07 - Rod Lock (Lower transverse key)
  8. Custom Rod Upper Lock (Top yoke key wedge)
  9. Spinner Lever 08 - Rod Lock (Bottom retaining washer disc)
  10. 09 - Rod Spring (Hinge detent leaf spring)

Outputs:
  - Derivatives/custom/Custom_Rod_assembled.glb
  - Derivatives/custom/Custom_Rod_exploded.glb
  - Derivatives/custom/Custom_Rod_assembled.3mf
  - Derivatives/custom/Custom_Rod_exploded.3mf
  - Derivatives/custom/Custom_Rod.stl
  - Derivatives/custom/Custom_Rod_assembly_viewer.html
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

# Distinct, aesthetic color palette for the 10 rod components
ROD_PART_COLORS = {
    "Custom Rod Middle": (86, 182, 178),            # Cyan / Teal
    "Custom Rod Right": (148, 176, 120),            # Sage Green
    "Custom Rod Left": (184, 126, 152),             # Mauve
    "Custom Rod Upper Right": (95, 143, 166),       # Deep Teal
    "Custom Rod Upper Left": (212, 158, 120),       # Warm Apricot
    "Spinner Lever 06 - Rod Lock": (214, 93, 84),   # Coral Red
    "Spinner Lever 07 - Rod Lock": (131, 151, 132), # Slate Green
    "Custom Rod Upper Lock": (176, 110, 120),       # Dusty Rose
    "Spinner Lever 08 - Rod Lock": (120, 166, 158), # Seafoam
    "09 - Rod Spring": (228, 169, 73),              # Amber Gold
}


def build_custom_rod_items() -> list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]:
    """Assemble all 10 components of the custom rod with correct poses and colors."""
    members = dict(BCH._custom_rod_parts_cached())
    upper = dict(BCH._custom_rod_upper_cached())
    locks = dict(BCH._custom_rod_locks_cached())

    # 09 - Rod Spring positioned inside the upper linear track
    spring_raw = fidget.load("09 - Rod Spring", product="spinner")
    spring_posed = spring_raw.copy()
    spring_posed.apply_transform(custom.module_transform())

    # Spinner Lever 08 - Rod Lock (axial retaining disc at the bottom)
    l08_entry = [
        r for r in A.poses("tactical")["parts"]
        if r["part"] == "Spinner Lever 08 - Rod Lock"
    ][0]
    l08_posed = A.posed(l08_entry, "tactical")

    raw_items = [
        (BCH.ROD_MIDDLE, members[BCH.ROD_MIDDLE].copy()),
        (BCH.ROD_RIGHT, members[BCH.ROD_RIGHT].copy()),
        (BCH.ROD_LEFT, members[BCH.ROD_LEFT].copy()),
        (BCH.ROD_UPPER_RIGHT, upper[BCH.ROD_UPPER_RIGHT].copy()),
        (BCH.ROD_UPPER_LEFT, upper[BCH.ROD_UPPER_LEFT].copy()),
        (BCH.ROD_LOCK_UPPER, locks[BCH.ROD_LOCK_UPPER].copy()),
        (BCH.ROD_LOCK_LOWER, locks[BCH.ROD_LOCK_LOWER].copy()),
        (BCH.ROD_YOKE_LOCK, locks[BCH.ROD_YOKE_LOCK].copy()),
        ("Spinner Lever 08 - Rod Lock", l08_posed),
        ("09 - Rod Spring", spring_posed),
    ]

    items = []
    for name, mesh in raw_items:
        color = ROD_PART_COLORS.get(name, (180, 180, 180))
        items.append((name, mesh, color))

    return items


def compute_rod_exploded_displacements(
    items: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]]
) -> np.ndarray:
    """Compute clear, functional exploded displacements for all 10 rod parts."""
    n = len(items)
    disp = np.zeros((n, 3))
    idx = {name: i for i, (name, _, _) in enumerate(items)}

    # Middle Rod remains as anchor
    disp[idx["Custom Rod Middle"]] = [0.0, 0.0, 0.0]

    # Lower side plates pull outwards in -X / +X
    disp[idx["Custom Rod Right"]] = [-18.0, 0.0, 0.0]
    disp[idx["Custom Rod Left"]] = [18.0, 0.0, 0.0]

    # Upper yoke caps pull outwards and slightly upwards
    disp[idx["Custom Rod Upper Right"]] = [14.0, 12.0, 0.0]
    disp[idx["Custom Rod Upper Left"]] = [-14.0, 12.0, 0.0]

    # Transverse locks pull out along Z (or -Z)
    disp[idx["Spinner Lever 06 - Rod Lock"]] = [0.0, 0.0, 18.0]
    disp[idx["Spinner Lever 07 - Rod Lock"]] = [0.0, 0.0, -18.0]

    # Upper yoke lock pulls out forward
    disp[idx["Custom Rod Upper Lock"]] = [0.0, 8.0, 14.0]

    # Bottom axial lock pulls straight down along -Y
    disp[idx["Spinner Lever 08 - Rod Lock"]] = [0.0, -22.0, 0.0]

    # Top detent spring pulls straight up along +Y
    disp[idx["09 - Rod Spring"]] = [0.0, 24.0, 0.0]

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
        prefix="rod_mod_", suffix=".tmp", dir=os.path.dirname(path), delete=False
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


def build_interactive_rod_viewer(
    items: list[tuple[str, trimesh.Trimesh, tuple[int, int, int]]],
    displacements: np.ndarray,
    glb_assembled_bytes: bytes,
    output_html_path: str,
):
    """Generate standalone self-contained 3D HTML viewer for the Custom Rod assembly."""
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
  <title>Custom Rod Assembly (10 Parts) - Interactive 3D Viewer</title>
  <style>
    :root {{
      --bg-gradient: radial-gradient(circle at 50% 30%, #161b26 0%, #0a0c10 100%);
      --panel-bg: rgba(22, 27, 34, 0.92);
      --panel-border: rgba(255, 255, 255, 0.14);
      --accent: #58a6ff;
      --accent-glow: rgba(88, 166, 255, 0.4);
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
      max-width: 460px;
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
      gap: 20px;
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
      width: 180px;
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
      width: 340px;
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
    <p>Loading Custom Rod 3D Assembly...</p>
  </div>

  <div class="header">
    <h1>Custom Rod Assembly <span class="badge">10 Parts / 0 Overlap</span></h1>
    <p>3-Member Full-Depth Rod &bull; Split Upper Hinge Yoke &bull; 3 Transverse Retention Keys &bull; Detent Spring &bull; Bottom Retention Disc</p>
  </div>

  <div id="canvas-container"></div>

  <div class="control-bar">
    <div class="slider-group">
      <label for="explode-slider">Explode</label>
      <input type="range" id="explode-slider" min="0" max="1" step="0.005" value="0">
    </div>
    <button class="btn" id="btn-animate">Play Animation</button>
    <button class="btn" id="btn-wireframe">Wireframe</button>
    <button class="btn" id="btn-reset">Reset View</button>
  </div>

  <div class="sidebar">
    <div class="sidebar-header">
      <h2>Rod Components (10)</h2>
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
      camera.position.set(60, 80, 120);

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
      controls.target.set(0, 55, 0);

      // Lighting
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
      scene.add(ambientLight);

      const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.5);
      dirLight1.position.set(100, 150, 100);
      dirLight1.castShadow = true;
      scene.add(dirLight1);

      const dirLight2 = new THREE.DirectionalLight(0x58a6ff, 0.8);
      dirLight2.position.set(-100, 50, -100);
      scene.add(dirLight2);

      const pointLight = new THREE.PointLight(0xffffff, 0.6);
      pointLight.position.set(0, -50, 50);
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
              // PBR material
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
        const item = document.createElement('div');
        item.className = 'part-item';
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
      const itemEl = document.getElementById(`item-${{name.replace(/[^a-zA-Z0-9]/g, '_')}}`);
      if (itemEl) itemEl.classList.add('selected');

      const mesh = meshesMap.get(name);
      if (!mesh) return;

      if (selectedMesh === mesh) {{
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
          m.material.opacity = 0.25;
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

      document.getElementById('btn-wireframe').onclick = function() {{
        isWireframe = !isWireframe;
        this.classList.toggle('active', isWireframe);
        meshesMap.forEach(m => m.material.wireframe = isWireframe);
      }};

      document.getElementById('btn-reset').onclick = function() {{
        controls.reset();
        camera.position.set(60, 80, 120);
        controls.target.set(0, 55, 0);
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
    """Build Custom Rod Assembly, validate 0-interference, and export all assets."""
    items = build_custom_rod_items()
    print(f"\n==========================================")
    print(f"CUSTOM ROD ASSEMBLY BUILD & VALIDATION (10 PARTS)")
    print(f"==========================================")
    print(f"Loaded {len(items)} parts for the Custom Rod assembly.\n")

    # 1. Watertightness check
    bad = [
        (name, m.is_watertight, m.body_count)
        for name, m, _ in items
        if not m.is_watertight or m.body_count != 1
    ]
    if bad:
        raise RuntimeError(f"Non-watertight or multi-body parts: {bad}")
    print("  [PASS] All 10 parts are 100% Watertight Single Solids.")

    # 2. Pairwise interference check
    bad_inter = A.interference([(name, m) for name, m, _ in items], min_mm3=0.001)
    if bad_inter:
        print(f"  [FAIL] {len(bad_inter)} interferences found:")
        for v, a, b in bad_inter:
            print(f"    {v:.4f} mm3 | {a} vs {b}")
        raise RuntimeError("Interference detected in Custom Rod assembly!")
    print("  [PASS] Zero pairwise interference detected (0.000 mm³ overlap across all pairs).")

    # 3. Assemble and Explode scenes
    assembled = A.scene(items)
    displacements = compute_rod_exploded_displacements(items)
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
        stem = "Custom_Rod"

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

    # 6. Interactive 3D HTML Viewers
    viewer_paths = [
        os.path.join(CUSTOM_DIR, "Custom_Rod_assembly_viewer.html"),
        os.path.join(MOD_DIR, "Custom_Rod_assembly_viewer.html"),
    ]
    for vp in viewer_paths:
        build_interactive_rod_viewer(items, displacements, glb_assembled_bytes, vp)

    # 7. Print Bounds & Metrology
    bounds = np.array([m.bounds for _, m, _ in items])
    envelope = bounds[:, 1].max(axis=0) - bounds[:, 0].min(axis=0)
    print("\n--- CUSTOM ROD METROLOGY ---")
    print(f"  Total Part Count:       {len(items)} components")
    print(f"  Bounding Envelope:      X={envelope[0]:.2f} mm, Y={envelope[1]:.2f} mm, Z={envelope[2]:.2f} mm")
    print(f"  Total Solid Volume:     {sum(m.volume for _, m, _ in items):.1f} mm³")
    print("==========================================\n")


if __name__ == "__main__":
    build_and_export_all()
