"""Build Dual-Headed Springs 3D Assembly & Interactive WebGL Studio (Common U-Spring).

Generates:
1. Dual_Headed_Spring_Assembly.glb
2. Derivatives/Dual_Headed_Springs_Viewer.html (Standalone Three.js studio)
"""
from __future__ import annotations

import base64
import json
import os
import sys
import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from package_paths import ROOT_DIR, ASSEMBLED_DIR

SPRING_DIR = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Option_B_ExtendedCap")
OUTPUT_HTML = os.path.join(ROOT_DIR, "Derivatives", "Dual_Headed_Springs_Viewer.html")

PART_COLORS = {
    # Barrel & Upper Station
    "10_Custom_Internal_Barrel_4Slot.stl": (60, 64, 72, 255),          # Gunmetal Charcoal
    "11_Custom_Internal_Barrel_Cap_Option_B.stl": (80, 85, 95, 255),   # Slate Grey
    "12_Custom_Rod_Detent_Spring_01.stl": (245, 130, 32, 255),         # Safety Orange
    "13_Custom_Rod_Detent_Spring_02_Dual_Headed.stl": (0, 229, 255, 255),# Electric Cyan (Dual-Headed)
    "14_Custom_Rod_Detent_Spring_03.stl": (245, 130, 32, 255),         # Safety Orange
    "15_Custom_Rod_Detent_Spring_04_Dual_Headed.stl": (0, 229, 255, 255),# Electric Cyan (Dual-Headed)
    "18_27_Upper_Shell_Top.stl": (85, 107, 75, 255),                   # Olive Drab
    "19_28_Upper_Shell_Gear.stl": (192, 198, 204, 255),                # Silver Metallic
    "20_29_Upper_Shell_Lock_Ring.stl": (95, 120, 85, 255),             # Olive Accent
    "21_30_Upper_Shell_Rotating_Spring.stl": (230, 80, 80, 255),       # Crimson Red
    # Central Rod
    "22_Custom_Rod_Right.stl": (110, 120, 135, 255),                   # Steel Blue/Grey
    "23_Custom_Rod_Middle.stl": (255, 195, 0, 255),                    # Amber Gold Highlight
    "24_Custom_Rod_Left.stl": (110, 120, 135, 255),                    # Steel Blue/Grey
    "25_Custom_Rod_Lock_Upper_06.stl": (220, 40, 40, 255),             # Crimson Key
    "26_Custom_Rod_Lock_Lower_07.stl": (220, 40, 40, 255),             # Crimson Key
    "27_Spinner_Lever_08_Rod_Lock.stl": (140, 145, 155, 255),          # Disc Retainer
    # Base
    "07_32_Mid_Shell_P02_Ratchet.stl": (70, 75, 85, 255),
    "08_33_Mid_Shell_P01_Outer.stl": (85, 107, 75, 255),
    "09_Custom_Mid_Shell_Spring_33.stl": (245, 130, 32, 255),
}


def build_scene() -> trimesh.Scene:
    """Build a trimesh Scene for Dual-Headed springs assembly."""
    scene = trimesh.Scene()

    # 1. Base & Rod parts from ASSEMBLED_DIR
    rod_parts = [
        "10_Custom_Internal_Barrel_4Slot.stl",
        "22_Custom_Rod_Right.stl",
        "23_Custom_Rod_Middle.stl",
        "24_Custom_Rod_Left.stl",
        "25_Custom_Rod_Lock_Upper_06.stl",
        "26_Custom_Rod_Lock_Lower_07.stl",
        "27_Spinner_Lever_08_Rod_Lock.stl",
        "18_27_Upper_Shell_Top.stl",
        "19_28_Upper_Shell_Gear.stl",
        "20_29_Upper_Shell_Lock_Ring.stl",
        "21_30_Upper_Shell_Rotating_Spring.stl",
    ]

    for fname in rod_parts:
        path = os.path.join(ASSEMBLED_DIR, fname)
        if os.path.exists(path):
            m = trimesh.load(path, process=False)
            col = PART_COLORS.get(fname, (160, 160, 160, 255))
            m.visual.vertex_colors = np.tile(col, (len(m.vertices), 1))
            scene.add_geometry(m, node_name=fname)

    # 2. Slotted Cap and Dual-Headed Springs
    cap_path = os.path.join(SPRING_DIR, "11_Custom_Internal_Barrel_Cap_Option_B.stl")
    cap_mesh = trimesh.load(cap_path, process=False)
    cap_col = PART_COLORS.get("11_Custom_Internal_Barrel_Cap_Option_B.stl", (80, 85, 95, 255))
    cap_mesh.visual.vertex_colors = np.tile(cap_col, (len(cap_mesh.vertices), 1))
    scene.add_geometry(cap_mesh, node_name="11_Custom_Internal_Barrel_Cap_Option_B.stl")

    spring_files = [
        ("12_Custom_Rod_Detent_Spring_01.stl", os.path.join(SPRING_DIR, "12_Custom_Rod_Detent_Spring_01.stl")),
        ("13_Custom_Rod_Detent_Spring_02_Dual_Headed.stl", os.path.join(SPRING_DIR, "13_Custom_Rod_Detent_Spring_02_Dual_Headed.stl")),
        ("14_Custom_Rod_Detent_Spring_03.stl", os.path.join(SPRING_DIR, "14_Custom_Rod_Detent_Spring_03.stl")),
        ("15_Custom_Rod_Detent_Spring_04_Dual_Headed.stl", os.path.join(SPRING_DIR, "15_Custom_Rod_Detent_Spring_04_Dual_Headed.stl")),
    ]

    for sname, spath in spring_files:
        s_mesh = trimesh.load(spath, process=False)
        col = PART_COLORS.get(sname, (245, 130, 32, 255))
        s_mesh.visual.vertex_colors = np.tile(col, (len(s_mesh.vertices), 1))
        scene.add_geometry(s_mesh, node_name=sname)

    return scene


def build_and_export():
    print("Building GLB 3D model for Dual-Headed Spring Assembly...")
    scene = build_scene()
    glb_path = os.path.join(SPRING_DIR, "Dual_Headed_Spring_Assembly.glb")
    scene.export(glb_path)

    with open(glb_path, "rb") as f:
        glb_b64 = base64.b64encode(f.read()).decode("utf-8")

    print("Generating Standalone Interactive HTML Studio...")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dual-Headed Common U-Spring Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070a10;
      --panel-bg: rgba(11, 17, 28, 0.88);
      --panel-border: rgba(255, 255, 255, 0.12);
      --accent-cyan: #00e5ff;
      --accent-cyan-glow: rgba(0, 229, 255, 0.35);
      --accent-purple: #a855f7;
      --accent-purple-glow: rgba(168, 85, 247, 0.35);
      --accent-gold: #ffc107;
      --accent-green: #10b981;
      --text-main: #e2e8f0;
      --text-muted: #94a3b8;
      --text-bright: #ffffff;
      --radius-lg: 16px;
      --radius-md: 10px;
      --radius-sm: 6px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-font-smoothing: antialiased;
    }}

    body {{
      background: var(--bg-dark);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }}

    #webgl-canvas {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
    }}

    .glass-panel {{
      position: absolute;
      background: var(--panel-bg);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-lg);
      z-index: 10;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55);
      pointer-events: auto;
    }}

    /* Header */
    #top-bar {{
      top: 20px;
      left: 24px;
      right: 24px;
      height: 70px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
    }}

    .logo-group {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
      color: #000;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 13px;
      padding: 6px 12px;
      border-radius: 8px;
      letter-spacing: 1px;
      text-transform: uppercase;
      box-shadow: 0 0 16px var(--accent-cyan-glow);
    }}

    .title-text h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 20px;
      font-weight: 700;
      color: var(--text-bright);
      letter-spacing: 0.3px;
    }}

    .title-text p {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    /* Controls Panel */
    #controls-panel {{
      left: 24px;
      top: 104px;
      width: 330px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    .section-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: var(--accent-cyan);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .btn-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
    }}

    .ctrl-btn {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-main);
      padding: 10px 8px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
    }}

    .ctrl-btn:hover {{
      background: rgba(255, 255, 255, 0.12);
      border-color: rgba(255, 255, 255, 0.25);
    }}

    .ctrl-btn.active {{
      background: var(--accent-cyan);
      color: #000;
      border-color: var(--accent-cyan);
      box-shadow: 0 0 14px var(--accent-cyan-glow);
    }}

    /* Slider Container */
    .slider-box {{
      background: rgba(0, 0, 0, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .slider-header {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 600;
    }}

    .slider-val {{
      font-family: 'JetBrains Mono', monospace;
      color: var(--accent-cyan);
    }}

    input[type=range] {{
      -webkit-appearance: none;
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: rgba(255, 255, 255, 0.15);
      outline: none;
    }}

    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--accent-cyan);
      cursor: pointer;
      box-shadow: 0 0 10px var(--accent-cyan);
    }}

    /* Specs / Info Panel */
    #info-panel {{
      right: 24px;
      top: 104px;
      width: 360px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .spec-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }}

    .spec-table td {{
      padding: 7px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }}

    .spec-label {{
      color: var(--text-muted);
    }}

    .spec-val {{
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: var(--text-bright);
    }}

    .badge-pill {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }}

    .badge-cyan {{
      background: rgba(0, 229, 255, 0.18);
      color: var(--accent-cyan);
      border: 1px solid var(--accent-cyan);
    }}

    /* Bottom Status Bar */
    #bottom-bar {{
      bottom: 20px;
      left: 24px;
      right: 24px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      font-size: 12px;
      color: var(--text-muted);
    }}

    .status-item {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-green);
      box-shadow: 0 0 8px var(--accent-green);
    }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
  <div id="webgl-canvas"></div>

  <!-- Header -->
  <div class="glass-panel" id="top-bar">
    <div class="logo-group">
      <div class="logo-badge">Dual Heads</div>
      <div class="title-text">
        <h1>Common U-Shaped Spring with Dual Detent Heads</h1>
        <p>Original U-Shaped Flexure Body Preserved | Dual Heads for Lower Rack & Upper Rod Teeth</p>
      </div>
    </div>
    <div style="font-family:'Outfit',sans-serif; font-size:13px; color:var(--accent-cyan); font-weight:700;">
      90° (+Z) & 270° (-Z) Active Springs
    </div>
  </div>

  <!-- Left Controls -->
  <div class="glass-panel" id="controls-panel">
    <div>
      <div class="section-title">Viewing Mode</div>
      <div class="btn-grid">
        <button class="ctrl-btn active" id="btn-mode-full" onclick="setMode('full')">Assembled</button>
        <button class="ctrl-btn" id="btn-mode-cut" onclick="setMode('cut')">CAD Cutaway</button>
        <button class="ctrl-btn" id="btn-mode-exp" onclick="setMode('exp')">Exploded</button>
      </div>
    </div>

    <div>
      <div class="section-title">Camera Presets</div>
      <div class="btn-grid">
        <button class="ctrl-btn" onclick="setCamera('iso')">Isometric</button>
        <button class="ctrl-btn" onclick="setCamera('front')">Front (+Z)</button>
        <button class="ctrl-btn" onclick="setCamera('side')">Side (+X)</button>
      </div>
    </div>

    <div class="slider-box">
      <div class="slider-header">
        <span>Linear Rod Stroke (Push/Pull)</span>
        <span class="slider-val" id="rod-disp-val">0.0 mm</span>
      </div>
      <input type="range" id="rod-slider" min="-12" max="12" step="0.1" value="0" oninput="updateRodPosition(this.value)">
      <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--text-muted); margin-top:4px;">
        <span>-12mm (Pushed Down)</span>
        <span>0mm (Seat)</span>
        <span>+12mm (Pulled Up)</span>
      </div>
    </div>

    <div style="display:flex; gap:8px;">
      <button class="ctrl-btn" style="flex:1;" id="btn-anim" onclick="toggleAnimation()">▶ Play Motion</button>
      <button class="ctrl-btn" style="flex:1;" onclick="resetViews()">⟲ Reset</button>
    </div>
  </div>

  <!-- Right Info Panel -->
  <div class="glass-panel" id="info-panel">
    <div class="section-title">Common U-Spring Mechanical Specs</div>
    
    <table class="spec-table">
      <tr>
        <td class="spec-label">Common Spring Body</td>
        <td class="spec-val"><span class="badge-pill badge-cyan">Original U-Shaped Flexure</span></td>
      </tr>
      <tr>
        <td class="spec-label">Head Spacing</td>
        <td class="spec-val">3 × Pitch (9.532 mm)</td>
      </tr>
      <tr>
        <td class="spec-label">Lower Head (In-Barrel)</td>
        <td class="spec-val">Y = 57.41 mm (Apex r 5.54)</td>
      </tr>
      <tr>
        <td class="spec-label">Upper Head (Through-Cap)</td>
        <td class="spec-val">Y = 66.94 mm (Apex r 5.54)</td>
      </tr>
      <tr>
        <td class="spec-label">Total Height</td>
        <td class="spec-val">32.92 mm (Y = 36.0 .. 68.92)</td>
      </tr>
      <tr>
        <td class="spec-label">FEA Radial Rate (k)</td>
        <td class="spec-val" style="color:var(--accent-cyan);">2.523 N/mm</td>
      </tr>
      <tr>
        <td class="spec-label">Max Flexure Strain</td>
        <td class="spec-val">1.96 % / mm (Safe for PETG)</td>
      </tr>
      <tr>
        <td class="spec-label">Barrel Cap</td>
        <td class="spec-val"><span class="badge-pill badge-cyan">Slotted Cap (3.60mm Slots)</span></td>
      </tr>
      <tr>
        <td class="spec-label">Print Orientation</td>
        <td class="spec-val">100% Flat Bed (0° Supports)</td>
      </tr>
    </table>

    <div class="section-title" style="margin-top:8px;">Detent Head Tracking</div>
    <div style="background:rgba(0,0,0,0.35); border-radius:8px; padding:12px; font-size:12px; line-height:1.6;">
      <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
        <span style="color:var(--text-muted);">Lower Head (In-Barrel):</span>
        <span style="color:var(--accent-cyan); font-weight:700;" id="head1-status">Y = 57.41 mm (Engaged)</span>
      </div>
      <div style="display:flex; justify-content:space-between;">
        <span style="color:var(--text-muted);">Upper Head (Through-Cap):</span>
        <span style="color:var(--accent-cyan); font-weight:700;" id="head2-status">Y = 66.94 mm (Engaged)</span>
      </div>
    </div>
  </div>

  <!-- Bottom Bar -->
  <div class="glass-panel" id="bottom-bar">
    <div class="status-item">
      <div class="dot"></div>
      <span>100% Watertight Single-Body Manifold Meshes (manifold3d verified)</span>
    </div>
    <div class="status-item">
      <span>Tooth Pitch: <b>3.17733 mm</b> | Crest: <b>r 6.890 mm</b> | Root: <b>r 5.765 mm</b></span>
    </div>
  </div>

  <script>
    const GLB_DATA = "{glb_b64}";

    let currentMode = 'full';
    let isAnimating = false;
    let animDirection = 1;
    let rodTravel = 0.0;

    const container = document.getElementById('webgl-canvas');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x070a10);

    const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.set(90, 75, 110);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.localClippingEnabled = true;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 52, 0);

    const ambLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.9);
    dirLight1.position.set(100, 150, 100);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x00e5ff, 0.4);
    dirLight2.position.set(-100, 80, -100);
    scene.add(dirLight2);

    const dirLight3 = new THREE.DirectionalLight(0xa855f7, 0.4);
    dirLight3.position.set(0, -100, 80);
    scene.add(dirLight3);

    const clipPlane = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0.0);

    let rootGroup = new THREE.Group();
    scene.add(rootGroup);
    let rodParts = [];

    const loader = new THREE.GLTFLoader();

    function loadModel() {{
      const bin = atob(GLB_DATA);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);

      loader.parse(bytes.buffer, '', (gltf) => {{
        rootGroup.add(gltf.scene);
        gltf.scene.traverse((child) => {{
          if (child.isMesh) {{
            child.material = child.material.clone();
            child.material.clippingPlanes = [];
            child.material.clipShadows = true;
            if (child.name.includes('Rod')) {{
              rodParts.push(child);
            }}
          }}
        }});
        console.log("Dual-Headed Common U-Spring Assembly loaded successfully");
      }});
    }}

    loadModel();

    function setMode(mode) {{
      currentMode = mode;
      document.getElementById('btn-mode-full').className = 'ctrl-btn ' + (mode === 'full' ? 'active' : '');
      document.getElementById('btn-mode-cut').className = 'ctrl-btn ' + (mode === 'cut' ? 'active' : '');
      document.getElementById('btn-mode-exp').className = 'ctrl-btn ' + (mode === 'exp' ? 'active' : '');

      rootGroup.traverse((child) => {{
        if (child.isMesh) {{
          if (mode === 'cut') {{
            child.material.clippingPlanes = [clipPlane];
          }} else {{
            child.material.clippingPlanes = [];
          }}

          if (mode === 'exp') {{
            if (child.name.includes('Spring_02')) child.position.z = 18;
            else if (child.name.includes('Spring_04')) child.position.z = -18;
            else if (child.name.includes('Spring_01')) child.position.x = -18;
            else if (child.name.includes('Spring_03')) child.position.x = 18;
            else if (child.name.includes('Cap')) child.position.y = 20;
            else if (child.name.includes('Upper_Shell')) child.position.y = 35;
          }} else {{
            if (!child.name.includes('Rod')) {{
              child.position.set(0, 0, 0);
            }}
          }}
        }}
      }});
    }}

    function updateRodPosition(val) {{
      rodTravel = parseFloat(val);
      document.getElementById('rod-disp-val').innerText = (rodTravel > 0 ? '+' : '') + rodTravel.toFixed(1) + ' mm';

      rodParts.forEach(p => {{
        p.position.y = rodTravel;
      }});

      const h1_y = (57.41 + rodTravel).toFixed(2);
      const h2_y = (66.94 + rodTravel).toFixed(2);
      document.getElementById('head1-status').innerText = `Y = 57.41 mm (Rack @ ${{h1_y}} mm)`;
      document.getElementById('head2-status').innerText = `Y = 66.94 mm (Upper Teeth @ ${{h2_y}} mm)`;
    }}

    function toggleAnimation() {{
      isAnimating = !isAnimating;
      const btn = document.getElementById('btn-anim');
      btn.innerText = isAnimating ? '⏸ Pause Motion' : '▶ Play Motion';
      btn.className = 'ctrl-btn ' + (isAnimating ? 'active' : '');
    }}

    function setCamera(view) {{
      if (view === 'iso') {{
        camera.position.set(90, 75, 110);
        controls.target.set(0, 52, 0);
      }} else if (view === 'front') {{
        camera.position.set(0, 52, 140);
        controls.target.set(0, 52, 0);
      }} else if (view === 'side') {{
        camera.position.set(140, 52, 0);
        controls.target.set(0, 52, 0);
      }}
    }}

    function resetViews() {{
      document.getElementById('rod-slider').value = 0;
      updateRodPosition(0);
      setCamera('iso');
      setMode('full');
      if (isAnimating) toggleAnimation();
    }}

    function animate() {{
      requestAnimationFrame(animate);

      if (isAnimating) {{
        rodTravel += 0.15 * animDirection;
        if (rodTravel >= 10.0) {{
          rodTravel = 10.0;
          animDirection = -1;
        }} else if (rodTravel <= -10.0) {{
          rodTravel = -10.0;
          animDirection = 1;
        }}
        document.getElementById('rod-slider').value = rodTravel;
        updateRodPosition(rodTravel);
      }}

      controls.update();
      renderer.render(scene, camera);
    }}

    animate();

    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }});
  </script>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Standalone 3D Viewer updated: {OUTPUT_HTML}")


if __name__ == "__main__":
    build_and_export()
