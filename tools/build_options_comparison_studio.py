"""Build Interactive Multi-Option Comparison Studio for Hybrid Grenade v1.2.

Generates:
  Hybrid_Grenade_v1.2/Options_Comparison_Studio.html

Standalone Three.js WebGL application featuring:
  - Option 1: Internal Tandem Dual-Head (Synchronous Dual-Snap, 100% Inside Barrel)
  - Option 2: Twin Parallel Leaves (18 Alternating Micro-Clicks, 100% Inside Barrel)
  - Option 3: Extended Rod Rack + Sub-Cap Dual Springs
  - Option 4: Extended Spring to Top Tooth (User Modality, Extends to Y=72mm, Rests at Tooth 9)
  - Baseline Original: Flawed single-click design for direct before/after contrast
  - Optional 21_30 Upper Shell Rotating Spring ghost overlay toggle to directly inspect clash/clearance
  - Operational reciprocating stroke slider (ΔY = 0 to 24 mm)
  - Procedural Web Audio API click synthesis
  - Real-time click counter & tooth engagement readout
  - Internal barrel transparency slider (0% to 100%)
  - XZ cross-section clipping plane toggle
"""
from __future__ import annotations

import base64
import json
import os
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
DERIV_DIR = os.path.join(V12_DIR, "Derivatives")

rod_std_path = os.path.join(V12_DIR, "04_Rod_Assembly_And_Locks", "Custom_Rod_Assembly.glb")
rod_opt3_path = os.path.join(DERIV_DIR, "Option_3_Extended_Rack", "Custom_Rod_Assembly_Option3.glb")
opt1_path = os.path.join(DERIV_DIR, "Option_1_Internal_Tandem", "Custom_Internal_Barrel_Assembly_Option1.glb")
opt2_path = os.path.join(DERIV_DIR, "Option_2_Twin_Parallel", "Custom_Internal_Barrel_Assembly_Option2.glb")
opt3_path = os.path.join(DERIV_DIR, "Option_3_Extended_Rack", "Custom_Internal_Barrel_Assembly_Option3.glb")
opt4_path = os.path.join(DERIV_DIR, "Option_4_Extended_Top_Tooth", "Custom_Internal_Barrel_Assembly_Option4.glb")
base_path = os.path.join(V12_DIR, "03_Internal_Barrel_And_Upper_Station", "Custom_Internal_Barrel_Assembly.glb")
s21_ghost_path = os.path.join(DERIV_DIR, "21_30_Rotating_Spring_Ghost.glb")

output_html = os.path.join(V12_DIR, "Options_Comparison_Studio.html")


def read_b64(p: str) -> str:
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def main():
    print("=" * 80)
    print("BUILDING MULTI-OPTION CONTINUOUS CLICK COMPARISON STUDIO HTML")
    print("=" * 80)

    print("[1/3] Reading and encoding 3D models into base64...")
    b64_rod_std = read_b64(rod_std_path)
    b64_rod_opt3 = read_b64(rod_opt3_path)
    b64_opt1 = read_b64(opt1_path)
    b64_opt2 = read_b64(opt2_path)
    b64_opt3 = read_b64(opt3_path)
    b64_opt4 = read_b64(opt4_path)
    b64_base = read_b64(base_path)
    b64_s21 = read_b64(s21_ghost_path)

    print("[2/3] Constructing HTML application...")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hybrid Grenade v1.2 — Continuous Click Comparison Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070a12;
      --panel-bg: rgba(13, 19, 32, 0.94);
      --panel-border: rgba(255, 255, 255, 0.12);
      --accent-cyan: #00e5ff;
      --accent-glow: rgba(0, 229, 255, 0.35);
      --accent-purple: #a855f7;
      --accent-orange: #f97316;
      --accent-gold: #eab308;
      --accent-green: #10b981;
      --accent-rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      user-select: none;
    }}
    body {{
      background: radial-gradient(circle at 50% 35%, #151f32 0%, #060911 100%);
      color: var(--text-main);
      overflow: hidden;
      width: 100vw;
      height: 100vh;
      display: flex;
    }}
    #canvas-container {{
      flex: 1;
      height: 100%;
      position: relative;
    }}
    #sidebar {{
      width: 490px;
      height: 100%;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      border-left: 1px solid var(--panel-border);
      display: flex;
      flex-direction: column;
      padding: 24px;
      gap: 14px;
      overflow-y: auto;
      z-index: 10;
      box-shadow: -8px 0 32px rgba(0,0,0,0.6);
    }}
    h1 {{
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      background: rgba(0, 229, 255, 0.15);
      color: var(--accent-cyan);
      border: 1px solid rgba(0, 229, 255, 0.3);
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .subtitle {{
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.4;
    }}
    .option-tabs {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .tab-btn {{
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid var(--panel-border);
      color: var(--text-muted);
      padding: 9px 12px;
      border-radius: 10px;
      font-size: 0.76rem;
      font-weight: 600;
      cursor: pointer;
      text-align: left;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.2s;
    }}
    .tab-btn:hover {{
      background: rgba(51, 65, 85, 0.9);
      color: #fff;
    }}
    .tab-btn.active {{
      background: rgba(0, 229, 255, 0.12);
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
      box-shadow: 0 0 16px rgba(0, 229, 255, 0.2);
    }}
    .tab-btn.active-gold {{
      background: rgba(234, 179, 8, 0.12) !important;
      border-color: var(--accent-gold) !important;
      color: var(--accent-gold) !important;
      box-shadow: 0 0 16px rgba(234, 179, 8, 0.2) !important;
    }}
    .tab-btn .tab-title {{
      font-weight: 700;
      font-size: 0.82rem;
      color: #fff;
    }}
    .tab-btn.active .tab-title {{
      color: inherit;
    }}
    .tab-tag {{
      font-size: 0.68rem;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.08);
      font-weight: 700;
    }}
    .control-card {{
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .slider-row {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .slider-label {{
      display: flex;
      justify-content: space-between;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-main);
    }}
    input[type=range] {{
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: #334155;
      outline: none;
      -webkit-appearance: none;
    }}
    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--accent-cyan);
      cursor: pointer;
      box-shadow: 0 0 10px var(--accent-glow);
    }}
    .btn-group {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
    }}
    button.action-btn {{
      background: rgba(51, 65, 85, 0.8);
      color: #fff;
      border: 1px solid var(--panel-border);
      padding: 7px;
      border-radius: 8px;
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    button.action-btn:hover {{
      background: var(--accent-cyan);
      color: #090d16;
    }}
    .info-card {{
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid var(--panel-border);
      border-radius: 10px;
      padding: 14px;
      font-size: 0.78rem;
      line-height: 1.5;
    }}
    .info-title {{
      font-size: 0.86rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .click-stats {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-top: 6px;
    }}
    .stat-box {{
      background: rgba(2, 6, 23, 0.6);
      border: 1px solid var(--panel-border);
      border-radius: 8px;
      padding: 8px 10px;
      text-align: center;
    }}
    .stat-val {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--accent-cyan);
    }}
    .stat-label {{
      font-size: 0.68rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    #toolbar {{
      position: absolute;
      bottom: 24px;
      left: 24px;
      display: flex;
      gap: 8px;
      z-index: 5;
      background: rgba(13, 19, 32, 0.88);
      backdrop-filter: blur(14px);
      padding: 8px 14px;
      border-radius: 12px;
      border: 1px solid var(--panel-border);
    }}
    .hud-overlay {{
      position: absolute;
      top: 24px;
      left: 24px;
      background: rgba(13, 19, 32, 0.88);
      backdrop-filter: blur(14px);
      padding: 12px 16px;
      border-radius: 12px;
      border: 1px solid var(--panel-border);
      pointer-events: none;
    }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
  <div id="canvas-container">
    <div class="hud-overlay">
      <div style="font-weight: 800; font-size: 0.92rem; color: var(--accent-cyan); margin-bottom: 3px;" id="hud-title">Option 1: Internal Tandem Dual-Head</div>
      <div style="color: var(--text-muted); font-size: 0.74rem;">Left Drag: Rotate • Right Drag: Pan • Scroll: Zoom</div>
    </div>
    <div id="toolbar">
      <button class="action-btn" id="btn-reset">Reset View</button>
      <button class="action-btn" id="btn-clip">Toggle XZ Clip Cut</button>
      <button class="action-btn" id="btn-ghost">Toggle 21_30 Rotating Spring</button>
      <button class="action-btn" id="btn-rotate">Auto Rotate</button>
      <button class="action-btn" id="btn-audio">🔊 Audio: ON</button>
    </div>
  </div>

  <div id="sidebar">
    <div>
      <h1>Continuous Click Studio <span class="badge">4 Options</span></h1>
      <p class="subtitle" style="margin-top: 4px;">Evaluate all design modalities to achieve continuous clicking across the middle rod teeth throughout the entire stroke.</p>
    </div>

    <!-- Option Selector Tabs -->
    <div class="option-tabs">
      <div class="tab-btn active" id="tab-opt1" onclick="switchOption('opt1')">
        <div>
          <div class="tab-title">Option 1: Internal Tandem</div>
          <div style="font-size: 0.72rem;">Both heads inside barrel slot • Synchronous 2x Snap</div>
        </div>
        <span class="tab-tag" style="color: var(--accent-cyan);">0.0 mm³ clash</span>
      </div>

      <div class="tab-btn" id="tab-opt2" onclick="switchOption('opt2')">
        <div>
          <div class="tab-title">Option 2: Twin Parallel Leaves</div>
          <div style="font-size: 0.72rem;">Side-by-side twin flexures • 18 Alternating Micro-Clicks</div>
        </div>
        <span class="tab-tag" style="color: var(--accent-purple);">0.0 mm³ clash</span>
      </div>

      <div class="tab-btn" id="tab-opt3" onclick="switchOption('opt3')">
        <div>
          <div class="tab-title">Option 3: Extended Rod Rack</div>
          <div style="font-size: 0.72rem;">Teeth carved up to Y=62mm • Sub-cap dual springs</div>
        </div>
        <span class="tab-tag" style="color: var(--accent-orange);">0.0 mm³ clash</span>
      </div>

      <div class="tab-btn" id="tab-opt4" onclick="switchOption('opt4')">
        <div>
          <div class="tab-title" style="color: #fde047;">Option 4: Ext to Top Tooth (User Modality)</div>
          <div style="font-size: 0.72rem;">Extends through Cap to Y=72mm • Rests at Tooth 9</div>
        </div>
        <span class="tab-tag" style="color: var(--accent-gold);">71.1 mm³ clash</span>
      </div>

      <div class="tab-btn" id="tab-base" onclick="switchOption('base')">
        <div>
          <div class="tab-title" style="color: #f87171;">Baseline (Flawed Original)</div>
          <div style="font-size: 0.72rem;">Head stranded at Y=66.9mm • Only 1 click on insertion</div>
        </div>
        <span class="tab-tag" style="color: var(--accent-rose);">41.0 mm³ clash</span>
      </div>
    </div>

    <!-- Kinematic Reciprocating Stroke -->
    <div class="control-card">
      <div class="slider-row">
        <div class="slider-label">
          <span>Operational Rod Stroke (ΔY)</span>
          <span id="stroke-val" style="color: var(--accent-cyan); font-family: 'JetBrains Mono'; font-weight: 700;">0.0 mm (Resting)</span>
        </div>
        <input type="range" id="slider-stroke" min="0" max="24" step="0.2" value="0">
      </div>
      <div class="btn-group">
        <button class="action-btn" onclick="setStroke(0)">Resting (0mm)</button>
        <button class="action-btn" onclick="setStroke(12)">Mid (12mm)</button>
        <button class="action-btn" onclick="setStroke(24)">Full (24mm)</button>
      </div>
      <div class="click-stats">
        <div class="stat-box">
          <div class="stat-val" id="click-counter">0</div>
          <div class="stat-label">Clicks Felt So Far</div>
        </div>
        <div class="stat-box">
          <div class="stat-val" id="rate-val">Synchronous</div>
          <div class="stat-label">Click Mode</div>
        </div>
      </div>
    </div>

    <!-- Barrel Opacity -->
    <div class="control-card">
      <div class="slider-row">
        <div class="slider-label">
          <span>Internal Barrel Chassis Opacity</span>
          <span id="trans-val" style="color: var(--accent-cyan);">35%</span>
        </div>
        <input type="range" id="slider-trans" min="0" max="100" value="35">
      </div>
    </div>

    <!-- Dynamic Option Technical Info -->
    <div class="info-card" id="option-details">
      <div class="info-title">Option 1: Internal Tandem Dual-Head</div>
      <ul style="padding-left: 18px; display: flex; flex-direction: column; gap: 5px;">
        <li><strong>Heads:</strong> Upper at Y = 56.50 mm (Tooth 9), Lower at Y = 47.01 mm (Tooth 6).</li>
        <li><strong>Resting State:</strong> Both heads sit in tooth valleys simultaneously at ΔY=0.</li>
        <li><strong>Tactile Snap:</strong> Synchronous double-click (2x tactile click force).</li>
        <li><strong>Upper Station Clash:</strong> 0.0000 mm³ (100% inside barrel slot).</li>
      </ul>
    </div>
  </div>

  <script>
    const B64_ROD_STD = "{b64_rod_std}";
    const B64_ROD_OPT3 = "{b64_rod_opt3}";
    const B64_OPT1 = "{b64_opt1}";
    const B64_OPT2 = "{b64_opt2}";
    const B64_OPT3 = "{b64_opt3}";
    const B64_OPT4 = "{b64_opt4}";
    const B64_BASE = "{b64_base}";
    const B64_S21 = "{b64_s21}";

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x070a12);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(65, 75, 100);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3;
    renderer.localClippingEnabled = true;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 54, 0);

    // Studio Lighting
    const amb = new THREE.AmbientLight(0xffffff, 0.95);
    scene.add(amb);
    const dir1 = new THREE.DirectionalLight(0xffffff, 1.4);
    dir1.position.set(60, 100, 70);
    scene.add(dir1);
    const dir2 = new THREE.DirectionalLight(0x00e5ff, 0.6);
    dir2.position.set(-60, -20, -50);
    scene.add(dir2);
    const dir3 = new THREE.DirectionalLight(0xffeedd, 0.7);
    dir3.position.set(0, 80, -80);
    scene.add(dir3);

    const grid = new THREE.GridHelper(140, 28, 0x334155, 0x1e293b);
    grid.position.y = 15;
    scene.add(grid);

    // Audio Synthesis Context
    let audioCtx = null;
    let audioEnabled = true;
    function initAudio() {{
      if (!audioCtx) {{
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }}
    }}
    function playClickSound(freq, pitchMultiplier) {{
      if (!audioEnabled) return;
      initAudio();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq * pitchMultiplier, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(110, audioCtx.currentTime + 0.035);
      gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.035);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.04);
    }}

    // Model Groups
    const groupRod = new THREE.Group();
    const groupBarrel = new THREE.Group();
    const groupGhost21 = new THREE.Group();
    scene.add(groupRod);
    scene.add(groupBarrel);
    scene.add(groupGhost21);

    const clipPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0);
    let isClipping = false;
    let showGhost21 = true;

    let currentOption = 'opt1';
    let currentStroke = 0;
    let barrelChassisMeshes = [];
    let lastClickIdx = -1;

    const loader = new THREE.GLTFLoader();

    function parseGLB(b64, cb) {{
      const binStr = atob(b64);
      const u8 = new Uint8Array(binStr.length);
      for (let i = 0; i < binStr.length; i++) u8[i] = binStr.charCodeAt(i);
      loader.parse(u8.buffer, '', (gltf) => cb(gltf.scene));
    }}

    // Pre-parse assets
    const assets = {{}};
    parseGLB(B64_ROD_STD, (s) => assets.rod_std = s);
    parseGLB(B64_ROD_OPT3, (s) => assets.rod_opt3 = s);
    parseGLB(B64_OPT1, (s) => assets.opt1 = s);
    parseGLB(B64_OPT2, (s) => assets.opt2 = s);
    parseGLB(B64_OPT3, (s) => assets.opt3 = s);
    parseGLB(B64_OPT4, (s) => assets.opt4 = s);
    parseGLB(B64_BASE, (s) => assets.base = s);
    parseGLB(B64_S21, (s) => {{
      assets.s21_ghost = s;
      groupGhost21.add(s.clone());
    }});

    function applyBarrelOpacity(val) {{
      const opacity = val / 100.0;
      const isTrans = val < 99.5;
      barrelChassisMeshes.forEach(mesh => {{
        if (mesh && mesh.material) {{
          mesh.material.transparent = isTrans;
          mesh.material.opacity = opacity;
          mesh.material.depthWrite = !isTrans;
          mesh.material.roughness = isTrans ? 0.25 : 0.45;
          mesh.material.needsUpdate = true;
        }}
      }});
    }}

    function switchOption(opt) {{
      currentOption = opt;
      document.querySelectorAll('.tab-btn').forEach(b => {{
        b.classList.remove('active');
        b.classList.remove('active-gold');
      }});
      const activeTab = document.getElementById('tab-' + opt);
      if (activeTab) {{
        if (opt === 'opt4') activeTab.classList.add('active-gold');
        else activeTab.classList.add('active');
      }}

      // Clear groups
      while(groupRod.children.length > 0) groupRod.remove(groupRod.children[0]);
      while(groupBarrel.children.length > 0) groupBarrel.remove(groupBarrel.children[0]);

      const rodMesh = (opt === 'opt3' ? assets.rod_opt3 : assets.rod_std).clone();
      const barrelMesh = assets[opt].clone();

      groupRod.add(rodMesh);
      groupBarrel.add(barrelMesh);

      barrelChassisMeshes = [];
      barrelMesh.traverse((c) => {{
        if (c.isMesh) {{
          const n = (c.name || '') + ' ' + (c.parent ? c.parent.name : '');
          if (n.includes('10') || n.includes('Chassis') || (n.includes('Barrel') && !n.includes('Cap') && !n.includes('Spring') && !n.includes('Pin'))) {{
            c.material = c.material.clone();
            barrelChassisMeshes.push(c);
          }}
        }}
      }});

      applyBarrelOpacity(parseFloat(document.getElementById('slider-trans').value));
      updateHUD();
      updateClickAnalysis(currentStroke);
    }}

    function updateHUD() {{
      const hudTitle = document.getElementById('hud-title');
      const details = document.getElementById('option-details');
      const rateVal = document.getElementById('rate-val');

      if (currentOption === 'opt1') {{
        hudTitle.textContent = 'Option 1: Internal Tandem Dual-Head';
        hudTitle.style.color = 'var(--accent-cyan)';
        rateVal.textContent = 'Synchronous';
        details.innerHTML = `
          <div class="info-title" style="color: var(--accent-cyan);">Option 1: Internal Tandem Dual-Head</div>
          <ul style="padding-left: 18px; display: flex; flex-direction: column; gap: 5px;">
            <li><strong>Architecture:</strong> Vertical tandem dual heads housed 100% inside barrel slot.</li>
            <li><strong>Heads:</strong> Upper at Y=56.50 mm (Tooth 9), Lower at Y=47.01 mm (Tooth 6).</li>
            <li><strong>Resting State:</strong> Both heads sit in tooth valleys simultaneously at ΔY=0.</li>
            <li><strong>Tactile Snap:</strong> Synchronous double-click with 2x click force.</li>
            <li><strong>Clash Volume:</strong> <strong>0.0000 mm³ (PASS)</strong> — Solid disc Cap 11, zero clash with 21_30.</li>
          </ul>
        `;
      }} else if (currentOption === 'opt2') {{
        hudTitle.textContent = 'Option 2: Twin Parallel Leaf Cantilevers';
        hudTitle.style.color = 'var(--accent-purple)';
        rateVal.textContent = '18 Alternating';
        details.innerHTML = `
          <div class="info-title" style="color: var(--accent-purple);">Option 2: Twin Parallel Leaves (Half-Pitch)</div>
          <ul style="padding-left: 18px; display: flex; flex-direction: column; gap: 5px;">
            <li><strong>Architecture:</strong> Twin side-by-side flexures offset by 1.58 mm (half-pitch).</li>
            <li><strong>Action:</strong> Alternating ratchet clicks every 1.58 mm of travel.</li>
            <li><strong>Click Frequency:</strong> 18 crisp micro-clicks across full stroke (2x frequency).</li>
            <li><strong>Clash Volume:</strong> <strong>0.0000 mm³ (PASS)</strong> — Solid disc Cap 11, zero clash with 21_30.</li>
          </ul>
        `;
      }} else if (currentOption === 'opt3') {{
        hudTitle.textContent = 'Option 3: Extended Rod Rack + Sub-Cap Springs';
        hudTitle.style.color = 'var(--accent-orange)';
        rateVal.textContent = 'Extended Rack';
        details.innerHTML = `
          <div class="info-title" style="color: var(--accent-orange);">Option 3: Extended Rod Rack + Sub-Cap Springs</div>
          <ul style="padding-left: 18px; display: flex; flex-direction: column; gap: 5px;">
            <li><strong>Middle Rod:</strong> Gear rack carved upward from Y=58.20 to 62.00 mm (Tooth 10 added).</li>
            <li><strong>Dual Spring:</strong> Upper head at Y=59.66 mm, staying safely under Cap 11 (Y=63.2 mm).</li>
            <li><strong>Hex Keying:</strong> Preserves upper hex key interface with 21_30 rotating spring.</li>
            <li><strong>Clash Volume:</strong> <strong>0.0000 mm³ (PASS)</strong>.</li>
          </ul>
        `;
      }} else if (currentOption === 'opt4') {{
        hudTitle.textContent = 'Option 4: Extended Spring to Top Tooth (User Modality)';
        hudTitle.style.color = 'var(--accent-gold)';
        rateVal.textContent = 'Continuous Clicks';
        details.innerHTML = `
          <div class="info-title" style="color: var(--accent-gold);">Option 4: Extended Spring to Top Tooth (User Modality)</div>
          <ul style="padding-left: 18px; display: flex; flex-direction: column; gap: 5px;">
            <li><strong>Architecture:</strong> Springs 13 & 15 extend through slotted Cap 11 up to Y = 72.45 mm.</li>
            <li><strong>Top Tooth Engagement:</strong> Detent head rests at Y = 56.50 mm (Tooth 9) at resting position (ΔY=0).</li>
            <li><strong>Kinematic Performance:</strong> Clicks continuously for <strong>EVERY single tooth</strong> (Teeth 9 down to 1) throughout reciprocating stroke.</li>
            <li><strong>Upper Station Clash:</strong> <strong style="color: #f87171;">71.05 mm³ CLASH with 21_30</strong> (The upper extension penetrates into the rotating spring's envelope. Toggle the 21_30 button to inspect!).</li>
          </ul>
        `;
      }} else {{
        hudTitle.textContent = 'Baseline: Flawed Single-Click Design';
        hudTitle.style.color = 'var(--accent-rose)';
        rateVal.textContent = '1 Single Click';
        details.innerHTML = `
          <div class="info-title" style="color: var(--accent-rose);">Baseline Original Design</div>
          <ul style="padding-left: 18px; display: flex; flex-direction: column; gap: 5px;">
            <li><strong>Flaw:</strong> Upper head placed at Y=66.93 mm (10.43 mm north of teeth).</li>
            <li><strong>Behavior:</strong> Clicks only once on Tooth 1 during insertion; 0 clicks in stroke.</li>
            <li><strong>Upper Station Clash:</strong> <strong style="color: #f87171;">41.03 mm³ CLASH with 21_30</strong>.</li>
          </ul>
        `;
      }}
    }}

    function updateClickAnalysis(dy) {{
      const counterEl = document.getElementById('click-counter');
      const pitch = 3.1625;
      let clicks = 0;

      if (currentOption === 'opt1') {{
        clicks = Math.floor(dy / pitch) * 2;
      }} else if (currentOption === 'opt2') {{
        clicks = Math.floor(dy / (pitch / 2.0));
      }} else if (currentOption === 'opt3') {{
        clicks = Math.floor(dy / pitch) * 2;
      }} else if (currentOption === 'opt4') {{
        // Clicks for every single tooth continuously!
        clicks = Math.floor(dy / pitch) * 2;
      }} else {{
        clicks = dy >= 10.43 ? 1 : 0;
      }}

      counterEl.textContent = clicks;

      const clickIdx = currentOption === 'opt2' ? Math.floor(dy / (pitch / 2.0)) : Math.floor(dy / pitch);
      if (clickIdx !== lastClickIdx && clickIdx >= 0) {{
        lastClickIdx = clickIdx;
        const freq = currentOption === 'opt2' ? 620 : (currentOption === 'opt4' ? 480 : (currentOption === 'opt1' ? 440 : 500));
        playClickSound(freq, 1.0);
      }}
    }}

    const sliderStroke = document.getElementById('slider-stroke');
    const strokeVal = document.getElementById('stroke-val');
    sliderStroke.addEventListener('input', (e) => {{
      const dy = parseFloat(e.target.value);
      setStroke(dy);
    }});

    function setStroke(dy) {{
      sliderStroke.value = dy;
      currentStroke = dy;
      strokeVal.textContent = dy.toFixed(1) + ' mm' + (dy === 0 ? ' (Resting)' : '');
      groupRod.position.y = dy;
      updateClickAnalysis(dy);
    }}

    const sliderTrans = document.getElementById('slider-trans');
    const transVal = document.getElementById('trans-val');
    sliderTrans.addEventListener('input', (e) => {{
      const val = parseFloat(e.target.value);
      transVal.textContent = Math.round(val) + '%';
      applyBarrelOpacity(val);
    }});

    document.getElementById('btn-reset').addEventListener('click', () => {{
      camera.position.set(65, 75, 100);
      controls.target.set(0, 54, 0);
      setStroke(0);
    }});

    document.getElementById('btn-clip').addEventListener('click', () => {{
      isClipping = !isClipping;
      renderer.clippingPlanes = isClipping ? [clipPlane] : [];
    }});

    document.getElementById('btn-ghost').addEventListener('click', () => {{
      showGhost21 = !showGhost21;
      groupGhost21.visible = showGhost21;
    }});

    let autoRotate = false;
    document.getElementById('btn-rotate').addEventListener('click', () => {{
      autoRotate = !autoRotate;
      controls.autoRotate = autoRotate;
      controls.autoRotateSpeed = 2.0;
    }});

    document.getElementById('btn-audio').addEventListener('click', (e) => {{
      audioEnabled = !audioEnabled;
      e.target.textContent = audioEnabled ? '🔊 Audio: ON' : '🔇 Audio: OFF';
    }});

    setTimeout(() => {{
      switchOption('opt4'); // Default to Option 4 so user sees their requested modality immediately!
    }}, 400);

    window.addEventListener('resize', () => {{
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    }});

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }}
    animate();
  </script>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[3/3] Exported Studio HTML: {output_html} ({os.path.getsize(output_html):,} bytes)")
    print("=" * 80)
    print("[SUCCESS] ALL 4 OPTIONS AND COMPARISON STUDIO READY")
    print("=" * 80)


if __name__ == "__main__":
    main()
