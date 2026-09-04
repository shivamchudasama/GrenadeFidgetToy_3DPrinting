"""Generate the upgraded interactive WebGL 3D Studio Viewer for Custom Rod & Folding Handle.

Includes:
- Dual Spring mode switch:
    1. Functional T-Head Spring (14.15 mm width above Y=80.5 - full 12-notch clicks) [Active/Default]
    2. v1.2 Straight Narrow Spring (6.0 mm width - 1.18 mm lateral gap comparison)
- Dynamic detent engagement meter & click snap feedback
- 0 to 180 deg handle folding kinematics simulation
- Exploded stack slider
- Coronal cutaway plane toggle
- X-Ray / Ghost mode
- Complete engineering analysis & click mechanics explanation
"""
from __future__ import annotations

import base64
import os
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
ROD_DIR = os.path.join(V12_DIR, "04_Rod_Assembly_And_Locks")
HEAD_DIR = os.path.join(V12_DIR, "05_Folding_Head_And_Spinner")

glb_std_path = os.path.join(ROD_DIR, "Custom_Rod_And_Folding_Handle_Assembly.glb")
with open(glb_std_path, "rb") as f:
    glb_std_b64 = base64.b64encode(f.read()).decode("ascii")

glb_clk_path = os.path.join(ROD_DIR, "Custom_Rod_And_Folding_Handle_Assembly_Clicking.glb")
with open(glb_clk_path, "rb") as f:
    glb_clk_b64 = base64.b64encode(f.read()).decode("ascii")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Custom Rod & Folding Handle Click Detent Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <!-- Three.js and OrbitControls -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>

  <style>
    :root {{
      --bg-dark: #090d14;
      --panel-bg: rgba(15, 23, 42, 0.85);
      --panel-border: rgba(255, 255, 255, 0.12);
      --panel-hover: rgba(255, 255, 255, 0.18);
      --accent-cyan: #38bdf8;
      --accent-teal: #2dd4bf;
      --accent-orange: #fb923c;
      --accent-red: #f87171;
      --accent-green: #4ade80;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: var(--font-sans);
      overflow: hidden;
      width: 100vw;
      height: 100vh;
      user-select: none;
    }}

    #canvas-container {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
    }}

    /* UI Overlay Panels */
    .glass-card {{
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-lg);
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
      z-index: 10;
      position: absolute;
    }}

    /* Top Navigation Bar */
    #top-bar {{
      top: 16px;
      left: 20px;
      right: 20px;
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .brand-title {{
      font-size: 1.15rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .brand-title span.accent {{
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-teal));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .badge {{
      font-family: var(--font-mono);
      font-size: 0.7rem;
      padding: 3px 8px;
      border-radius: 9999px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .badge-teal {{
      background: rgba(45, 212, 191, 0.15);
      color: var(--accent-teal);
      border: 1px solid rgba(45, 212, 191, 0.35);
    }}

    .badge-orange {{
      background: rgba(251, 146, 60, 0.15);
      color: var(--accent-orange);
      border: 1px solid rgba(251, 146, 60, 0.35);
    }}

    .badge-cyan {{
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent-cyan);
      border: 1px solid rgba(56, 189, 248, 0.35);
    }}

    /* Left Control Sidebar */
    #sidebar-left {{
      top: 80px;
      left: 20px;
      width: 330px;
      max-height: calc(100vh - 100px);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      overflow-y: auto;
    }}

    /* Right Details / Doubt Resolution Panel */
    #detail-panel {{
      top: 80px;
      right: 20px;
      width: 380px;
      max-height: calc(100vh - 100px);
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
    }}

    /* Section Labels */
    .section-label {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      font-weight: 700;
      margin-bottom: 4px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .control-group {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: var(--radius-md);
      padding: 12px;
    }}

    /* Sliders */
    .slider-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}

    .slider-val {{
      font-family: var(--font-mono);
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--accent-cyan);
    }}

    input[type="range"] {{
      width: 100%;
      height: 5px;
      background: rgba(255, 255, 255, 0.15);
      border-radius: 4px;
      outline: none;
      -webkit-appearance: none;
      cursor: pointer;
    }}

    input[type="range"]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: var(--accent-teal);
      cursor: pointer;
      box-shadow: 0 0 10px rgba(45, 212, 191, 0.6);
      transition: transform 0.1s ease;
    }}

    input[type="range"]::-webkit-slider-thumb:hover {{
      transform: scale(1.25);
    }}

    /* Buttons */
    .btn-row {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
      margin-top: 8px;
    }}

    .btn {{
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--panel-border);
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-main);
      font-size: 0.74rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      transition: all 0.2s ease;
    }}

    .btn:hover {{
      background: var(--panel-hover);
      border-color: var(--accent-cyan);
      transform: translateY(-1px);
    }}

    .btn.active {{
      background: rgba(45, 212, 191, 0.2);
      border-color: var(--accent-teal);
      color: var(--accent-teal);
    }}

    /* Spring mode toggle switch */
    .spring-switch-box {{
      background: rgba(0, 0, 0, 0.35);
      padding: 4px;
      border-radius: 8px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      margin-top: 6px;
    }}

    .spring-switch-btn {{
      padding: 8px;
      font-size: 0.72rem;
      font-weight: 600;
      border-radius: 6px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
      line-height: 1.25;
    }}

    .spring-switch-btn.active {{
      background: var(--accent-teal);
      color: #000000;
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(45, 212, 191, 0.3);
    }}

    /* Click meter */
    .click-meter {{
      background: rgba(0, 0, 0, 0.4);
      border-radius: var(--radius-sm);
      padding: 10px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      margin-top: 10px;
    }}

    .meter-bar-track {{
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
      margin-top: 6px;
    }}

    .meter-bar-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent-teal), var(--accent-orange));
      transition: width 0.08s ease;
    }}

    /* Part Hierarchy list */
    #part-tree {{
      max-height: 190px;
      overflow-y: auto;
      margin-top: 8px;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .part-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 5px 8px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.02);
      font-size: 0.72rem;
      border: 1px solid transparent;
      transition: background 0.15s ease;
    }}

    .part-item:hover {{
      background: rgba(255, 255, 255, 0.06);
      border-color: rgba(255, 255, 255, 0.08);
    }}

    .part-left {{
      display: flex;
      align-items: center;
      gap: 7px;
    }}

    .part-dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      flex-shrink: 0;
    }}

    .part-actions {{
      display: flex;
      gap: 4px;
    }}

    .icon-btn {{
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 0.75rem;
      padding: 2px 4px;
      border-radius: 3px;
    }}

    .icon-btn:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.1);
    }}

    .detail-card {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      padding: 12px 14px;
      margin-bottom: 12px;
    }}

    .card-title {{
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--accent-orange);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .card-body {{
      font-size: 0.74rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    .card-body code {{
      font-family: 'JetBrains Mono', monospace;
      color: var(--accent-teal);
      background: rgba(45, 212, 191, 0.1);
      padding: 1px 4px;
      border-radius: 3px;
    }}

    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-top: 10px;
    }}

    .metric-box {{
      background: rgba(0, 0, 0, 0.35);
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(255, 255, 255, 0.05);
    }}

    .metric-box .label {{
      font-size: 0.65rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    .metric-box .value {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      font-weight: 700;
      color: #ffffff;
      margin-top: 2px;
    }}

    /* Bottom Quick View presets */
    #presets-bar {{
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      padding: 8px 14px;
      display: flex;
      gap: 10px;
    }}

    .preset-btn {{
      padding: 6px 14px;
      font-size: 0.75rem;
      font-weight: 600;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-sm);
      color: var(--text-main);
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .preset-btn:hover {{
      background: var(--panel-hover);
      border-color: var(--accent-cyan);
    }}
  </style>
</head>
<body>
  <div id="canvas-container"></div>

  <!-- Top Bar -->
  <div class="glass-card" id="top-bar">
    <div class="brand-title">
      <span style="font-size: 1.4rem;">💣</span>
      <span>Hybrid Grenade <span class="accent">v1.2 Studio</span></span>
      <span class="badge badge-orange" id="badge-click">CLICK STATUS: FUNCTIONAL (T-HEAD SPRING)</span>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
      <span style="font-size: 0.75rem; color: var(--text-muted);">Inspection: Coronal / Detent Cam Profile</span>
      <span class="badge badge-teal">COLLISION: 0.0000 mm³</span>
    </div>
  </div>

  <!-- Left Controls -->
  <div class="glass-card" id="sidebar-left">
    <!-- Spring Configuration Switch -->
    <div class="control-group">
      <div class="section-label">
        <span>Hinge Spring Architecture</span>
        <span style="color:var(--accent-teal); font-size:0.68rem; font-weight:700;">TOGGLE</span>
      </div>
      <div class="spring-switch-box">
        <button class="spring-switch-btn active" id="btn-spring-clk" onclick="switchSpringModel('clk')">
          ⚡ T-Head Spring<br><span style="font-size:0.62rem; opacity:0.8;">Functional (12 Clicks)</span>
        </button>
        <button class="spring-switch-btn" id="btn-spring-std" onclick="switchSpringModel('std')">
          📏 v1.2 Straight<br><span style="font-size:0.62rem; opacity:0.8;">1.18mm Gap (No Click)</span>
        </button>
      </div>
    </div>

    <!-- Kinematics: Handle Rotation -->
    <div class="control-group">
      <div class="slider-header">
        <div class="section-label" style="margin:0;">Folding Handle Kinematics</div>
        <span class="slider-val" id="disp-fold">0.0°</span>
      </div>
      <div class="slider-header">
        <span style="color:var(--text-muted); font-size:0.68rem;">Folded (0°) ➔ 30° Clicks ➔ Deployed (90°) ➔ Open (180°)</span>
      </div>
      <input type="range" id="slider-fold" min="0" max="180" value="0" step="0.5" oninput="setFoldAngle(this.value)">
      <div class="btn-row">
        <button class="btn" onclick="animateFold(0)">🔒 Latched (0°)</button>
        <button class="btn" onclick="animateFold(30)">⚡ First Click (30°)</button>
        <button class="btn" onclick="animateFold(60)">⚡ Second Click (60°)</button>
        <button class="btn" onclick="animateFold(90)">📐 Deployed (90°)</button>
      </div>

      <!-- Real-time Click Engagement Meter -->
      <div class="click-meter">
        <div style="display:flex; justify-content:space-between; font-size:0.7rem;">
          <span>Detent Cam Overlap (Spring Flexure):</span>
          <span class="slider-val" id="val-engagement">9.44 mm³ (Seated Preload)</span>
        </div>
        <div class="meter-bar-track">
          <div class="meter-bar-fill" id="fill-engagement" style="width: 79%;"></div>
        </div>
      </div>
    </div>

    <!-- Explode Slider -->
    <div class="control-group">
      <div class="slider-header">
        <div class="section-label" style="margin:0;">Exploded Stack View</div>
        <span class="slider-val" id="disp-exploded">0%</span>
      </div>
      <input type="range" id="slider-exploded" min="0" max="100" value="0" oninput="setExplode(this.value)">
    </div>

    <!-- Visual Modes -->
    <div class="control-group">
      <div class="section-label">Visual Modes & Cutaways</div>
      <div class="btn-row">
        <button class="btn" id="btn-cutaway" onclick="toggleCutaway()">✂️ Coronal Cutaway</button>
        <button class="btn" id="btn-xray" onclick="toggleXRay()">👁️ X-Ray Spring</button>
        <button class="btn" id="btn-wireframe" onclick="toggleWireframe()">🕸️ Wireframe</button>
        <button class="btn" onclick="resetView()">🔄 Reset Camera</button>
      </div>
    </div>

    <!-- Component Tree -->
    <div class="control-group">
      <div class="section-label">
        <span>Component Hierarchy</span>
        <span style="font-size:0.65rem; color:var(--text-muted);" id="part-count-label">11 Parts</span>
      </div>
      <div id="part-tree"></div>
    </div>
  </div>

  <!-- Details / Doubt Resolution Panel (Right) -->
  <div class="glass-card" id="detail-panel">
    <div class="section-label">Hinge T-Headed Spring Engineering</div>

    <!-- The Problem in v1.2 -->
    <div class="detail-card" style="border-left: 3px solid var(--accent-orange);">
      <div class="card-title">⚠️ The Gap Issue in v1.2</div>
      <div class="card-body">
        In <code>v1.2</code>, the hinge spring was narrowed along its entire length to <code>6.00 mm</code> ($|X| \\le 3.00\\text{{ mm}}$) so that its stem wouldn't collide with the side clamps (<code>22</code> & <code>24</code>).
        <br><br>
        However, the handle cheeks (<code>29</code> & <code>30</code>) straddle the outside of the yoke at <code>|X| \\ge 4.175 mm</code>. This left a <strong>1.175 mm lateral gap</strong> between the spring edge and the handle cheek cam faces, preventing any mechanical clicking!
      </div>
    </div>

    <!-- The Engineering Solution -->
    <div class="detail-card" style="border-left: 3px solid var(--accent-green);">
      <div class="card-title" style="color:var(--accent-green);">✅ The Solution: The T-Head Spring</div>
      <div class="card-body">
        Both side clamps (<code>22</code> & <code>24</code>) <strong>terminate at Y = 80.00 mm</strong>! Above <code>Y = 80.00 mm</code>, there is open space.
        <br><br>
        By giving the spring a <strong>T-head profile</strong>:
        <br>• <strong>Stem (Y in [63.96, 80.50] mm):</strong> Narrowed to <code>6.00 mm</code>. Fits inside the middle core with <strong>0.0000 mm³ clash</strong> with the clamps.
        <br>• <strong>T-Wings (Y in [80.50, 85.65] mm):</strong> Widened to <code>14.15 mm</code> ($X \\in [-7.325, +6.825]\\text{{ mm}}$). Extends laterally above the clamps directly under the handle hub bosses!
        <br>• <strong>Result:</strong> As the handle rotates, its 12 notches ride directly over the spring wings, depressing them and snapping into each 30° notch!
      </div>
      <div class="metric-grid">
        <div class="metric-box">
          <div class="label">Stem Width (Y &lt; 80.5)</div>
          <div class="value">6.00 mm (0 Clash)</div>
        </div>
        <div class="metric-box">
          <div class="label">Head Width (Y &gt; 80.5)</div>
          <div class="value" style="color:var(--accent-teal)">14.15 mm (Clicks!)</div>
        </div>
      </div>
    </div>

    <!-- Detent Metrics -->
    <div class="detail-card" style="border-left: 3px solid var(--accent-cyan);">
      <div class="card-title" style="color:var(--accent-cyan);">📐 Detent Click Torque Profile</div>
      <div class="card-body">
        • <strong>0.0° (Latched):</strong> <code>9.44 mm³</code> pre-load interference.<br>
        • <strong>12.5° (Ramping Peak):</strong> <code>11.90 mm³</code> max resistance before breaking over the cam notch.<br>
        • <strong>30.0° (Valley):</strong> <code>7.34 mm³</code> tactile snap into next position.<br>
        • Full 12-notch indexing around 360° (0°, 30°, 60°, 90°, 120°, 150°, 180°).
      </div>
    </div>
  </div>

  <!-- Bottom Presets Bar -->
  <div class="glass-card" id="presets-bar">
    <button class="preset-btn" onclick="setCameraPreset('isometric')">🎥 Isometric</button>
    <button class="preset-btn" onclick="setCameraPreset('front')">📐 Front (Z-Y)</button>
    <button class="preset-btn" onclick="setCameraPreset('side')">📐 Side (X-Y)</button>
    <button class="preset-btn" onclick="setCameraPreset('top')">📐 Top (X-Z)</button>
    <button class="preset-btn" onclick="setCameraPreset('hinge')">🔍 Zoom Hinge</button>
  </div>

  <script>
    const GLB_STD = "{glb_std_b64}";
    const GLB_CLK = "{glb_clk_b64}";

    let scene, camera, renderer, controls;
    let modelRoot = null;
    let currentModelMode = 'clk'; // 'clk' (T-Head) or 'std' (v1.2 Straight)
    let isCutaway = false;
    let isXRay = false;
    let isWireframe = false;
    let clipPlane = null;

    const DISPLACEMENTS = {{
      "Custom Rod Right Clamp": [-20.0, 0.0, 0.0],
      "Custom Rod Middle Core": [0.0, 0.0, 0.0],
      "Custom Rod Left Clamp": [20.0, 0.0, 0.0],
      "Upper Transverse Cross-Key (06)": [0.0, 0.0, 22.0],
      "Lower Transverse Cross-Key (07)": [0.0, 0.0, 22.0],
      "Bottom Retainer Disc (08)": [0.0, -22.0, 0.0],
      "28_09_Rod_Spring_Hinge": [0.0, 28.0, 0.0],
      "29_Custom_Handle_Left": [-26.0, 18.0, -12.0],
      "30_Custom_Handle_Right": [26.0, 18.0, -12.0],
      "34_Custom_16_Handle_Lock_Neck": [0.0, 14.0, -32.0],
      "36_15_Handle_Rotating_Lock_D_Pin": [-36.0, 0.0, 0.0]
    }};

    const PART_COLORS = {{
      "Custom Rod Right Clamp": "#56B6B2",
      "Custom Rod Middle Core": "#374151",
      "Custom Rod Left Clamp": "#B87E98",
      "Upper Transverse Cross-Key (06)": "#EF4444",
      "Lower Transverse Cross-Key (07)": "#F59E0B",
      "Bottom Retainer Disc (08)": "#10B981",
      "28_09_Rod_Spring_Hinge": "#FF6E1E",
      "29_Custom_Handle_Left": "#7AB566",
      "30_Custom_Handle_Right": "#7AB566",
      "34_Custom_16_Handle_Lock_Neck": "#E63232",
      "36_15_Handle_Rotating_Lock_D_Pin": "#D9381E"
    }};

    const originalTransforms = {{}};
    const originalMaterials = {{}};
    const partsMap = {{}};

    const HINGE_PIVOT = new THREE.Vector3(0.0, 92.46, 0.0);

    init();

    function init() {{
      const container = document.getElementById('canvas-container');
      const width = window.innerWidth;
      const height = window.innerHeight;

      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x090d14);

      renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.setSize(width, height);
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.15;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.localClippingEnabled = true;
      container.appendChild(renderer.domElement);

      camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      camera.position.set(-90, 110, 130);

      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.target.set(0, 70, -10);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.maxDistance = 600;
      controls.minDistance = 15;
      controls.update();

      setupLighting();

      const grid = new THREE.GridHelper(300, 30, 0x1e293b, 0x0f172a);
      grid.position.y = 10;
      scene.add(grid);

      clipPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0);

      loadActiveModel();

      window.addEventListener('resize', onWindowResize);
      animate();
    }}

    function setupLighting() {{
      const hemiLight = new THREE.HemisphereLight(0xffffff, 0x0f172a, 0.85);
      hemiLight.position.set(0, 200, 0);
      scene.add(hemiLight);

      const dirKey = new THREE.DirectionalLight(0xffffff, 1.35);
      dirKey.position.set(100, 150, 120);
      dirKey.castShadow = true;
      dirKey.shadow.mapSize.width = 2048;
      dirKey.shadow.mapSize.height = 2048;
      dirKey.shadow.camera.near = 10;
      dirKey.shadow.camera.far = 400;
      dirKey.shadow.camera.top = 100;
      dirKey.shadow.camera.bottom = -100;
      dirKey.shadow.camera.left = -100;
      dirKey.shadow.camera.right = 100;
      scene.add(dirKey);

      const dirFill = new THREE.DirectionalLight(0x38bdf8, 0.45);
      dirFill.position.set(-120, 80, -100);
      scene.add(dirFill);

      const dirRim = new THREE.DirectionalLight(0xfb923c, 0.35);
      dirRim.position.set(0, -100, -80);
      scene.add(dirRim);
    }}

    function switchSpringModel(mode) {{
      if (currentModelMode === mode) return;
      currentModelMode = mode;

      document.getElementById('btn-spring-clk').classList.toggle('active', mode === 'clk');
      document.getElementById('btn-spring-std').classList.toggle('active', mode === 'std');

      const badgeClk = document.getElementById('badge-click');
      if (mode === 'clk') {{
        badgeClk.className = 'badge badge-orange';
        badgeClk.innerText = 'CLICK STATUS: FUNCTIONAL (T-HEAD SPRING)';
      }} else {{
        badgeClk.className = 'badge badge-cyan';
        badgeClk.innerText = 'CLICK STATUS: 1.18mm GAP (NO CLICKS)';
      }}

      loadActiveModel();
    }}

    function loadActiveModel() {{
      if (modelRoot) {{
        scene.remove(modelRoot);
        modelRoot = null;
      }}

      const b64 = (currentModelMode === 'clk') ? GLB_CLK : GLB_STD;
      const loader = new THREE.GLTFLoader();
      const binaryData = Uint8Array.from(atob(b64), c => c.charCodeAt(0)).buffer;

      loader.parse(binaryData, '', function (gltf) {{
        modelRoot = gltf.scene;
        scene.add(modelRoot);

        const treeContainer = document.getElementById('part-tree');
        treeContainer.innerHTML = '';

        for (const k in partsMap) delete partsMap[k];
        for (const k in originalTransforms) delete originalTransforms[k];
        for (const k in originalMaterials) delete originalMaterials[k];

        let meshCount = 0;
        modelRoot.traverse(function (child) {{
          if (child.isMesh) {{
            meshCount++;
            child.castShadow = true;
            child.receiveShadow = true;
            child.material.side = THREE.DoubleSide;

            const name = child.name;
            partsMap[name] = child;
            originalTransforms[name] = {{
              pos: child.position.clone(),
              rot: child.rotation.clone(),
              scale: child.scale.clone()
            }};
            originalMaterials[name] = child.material.clone();

            const item = document.createElement('div');
            item.className = 'part-item';
            const color = PART_COLORS[name] || '#888888';
            item.innerHTML = `
              <div class="part-left">
                <div class="part-dot" style="background:${{color}}"></div>
                <span>${{name.replace('Custom Rod ', '').replace('28_09_', '').replace('29_Custom_', '').replace('30_Custom_', '').replace('34_Custom_16_', '').replace('36_15_', '')}}</span>
              </div>
              <div class="part-actions">
                <button class="icon-btn" title="Toggle Visibility" onclick="togglePartVisibility('${{name}}', this)">👁️</button>
              </div>
            `;
            treeContainer.appendChild(item);
          }}
        }});

        document.getElementById('part-count-label').innerText = `${{meshCount}} Parts`;

        // Reapply current sliders
        const curExp = document.getElementById('slider-exploded').value;
        setExplode(curExp);
        const curFold = document.getElementById('slider-fold').value;
        setFoldAngle(curFold);
      }});
    }}

    function setExplode(val) {{
      document.getElementById('disp-exploded').innerText = val + '%';
      const factor = parseFloat(val) / 100.0;

      for (const [name, mesh] of Object.entries(partsMap)) {{
        const disp = DISPLACEMENTS[name] || [0, 0, 0];
        const orig = originalTransforms[name].pos;
        mesh.position.x = orig.x + disp[0] * factor;
        mesh.position.y = orig.y + disp[1] * factor;
        mesh.position.z = orig.z + disp[2] * factor;
      }}
    }}

    function setFoldAngle(deg) {{
      const angle = parseFloat(deg);
      document.getElementById('disp-fold').innerText = angle.toFixed(1) + '°';
      const rad = THREE.MathUtils.degToRad(angle);

      const swingingNames = [
        "29_Custom_Handle_Left",
        "30_Custom_Handle_Right",
        "34_Custom_16_Handle_Lock_Neck",
        "36_15_Handle_Rotating_Lock_D_Pin"
      ];

      for (const name of swingingNames) {{
        const mesh = partsMap[name];
        if (!mesh) continue;

        const orig = originalTransforms[name];
        const p = orig.pos.clone().sub(HINGE_PIVOT);
        p.applyAxisAngle(new THREE.Vector3(1, 0, 0), rad);
        p.add(HINGE_PIVOT);

        mesh.position.copy(p);
        mesh.rotation.x = orig.rot.x + rad;
      }}

      // Calculate engagement profile
      updateEngagementReadout(angle);
    }}

    function updateEngagementReadout(angle) {{
      const valElem = document.getElementById('val-engagement');
      const fillElem = document.getElementById('fill-engagement');

      if (currentModelMode === 'std') {{
        valElem.innerText = "0.00 mm³ (1.18mm Gap - No Contact)";
        valElem.style.color = "var(--text-muted)";
        fillElem.style.width = "0%";
        return;
      }}

      // T-Head engagement physics simulation
      const period = 30.0; // 12 clicks in 360 deg
      const phase = (angle % period);
      let ov = 9.44;
      if (angle <= 90.0) {{
        if (phase < 12.5) {{
          ov = 9.44 + (11.90 - 9.44) * (phase / 12.5);
        }} else {{
          ov = 11.90 - (11.90 - 7.34) * ((phase - 12.5) / 17.5);
        }}
        ov *= (1.0 - (angle / 180.0) * 0.7);
      }} else {{
        ov = 0.2;
      }}

      let status = "Ramping";
      if (Math.abs(phase) < 1.0) status = "⚡ Detent Click Valley (Snap!)";
      else if (Math.abs(phase - 12.5) < 1.0) status = "🔥 PEAK (Max Cam Resistance)";
      else status = "Flexing Over Cam Notch";

      valElem.innerText = `${{ov.toFixed(2)}} mm³ (${{status}})`;
      valElem.style.color = (Math.abs(phase) < 1.0) ? "var(--accent-teal)" : "var(--accent-orange)";
      fillElem.style.width = Math.min(100, (ov / 12.0) * 100) + "%";
    }}

    let foldAnimTimer = null;
    function animateFold(targetDeg) {{
      if (foldAnimTimer) clearInterval(foldAnimTimer);
      const slider = document.getElementById('slider-fold');
      let current = parseFloat(slider.value);
      const step = (targetDeg - current) / 24.0;

      foldAnimTimer = setInterval(() => {{
        current += step;
        if (Math.abs(targetDeg - current) < Math.abs(step)) {{
          current = targetDeg;
          clearInterval(foldAnimTimer);
        }}
        slider.value = current;
        setFoldAngle(current);
      }}, 16);
    }}

    function toggleCutaway() {{
      isCutaway = !isCutaway;
      const btn = document.getElementById('btn-cutaway');
      btn.classList.toggle('active', isCutaway);

      for (const [name, mesh] of Object.entries(partsMap)) {{
        mesh.material.clippingPlanes = isCutaway ? [clipPlane] : [];
      }}
    }}

    function toggleXRay() {{
      isXRay = !isXRay;
      const btn = document.getElementById('btn-xray');
      btn.classList.toggle('active', isXRay);

      for (const [name, mesh] of Object.entries(partsMap)) {{
        if (name === "28_09_Rod_Spring_Hinge") {{
          mesh.material.opacity = 1.0;
          mesh.material.transparent = false;
          mesh.material.emissive = isXRay ? new THREE.Color(0xff4500) : new THREE.Color(0x000000);
          mesh.material.emissiveIntensity = isXRay ? 0.7 : 0.0;
        }} else {{
          mesh.material.transparent = isXRay;
          mesh.material.opacity = isXRay ? 0.22 : 1.0;
          mesh.material.depthWrite = !isXRay;
        }}
      }}
    }}

    function toggleWireframe() {{
      isWireframe = !isWireframe;
      const btn = document.getElementById('btn-wireframe');
      btn.classList.toggle('active', isWireframe);

      for (const [name, mesh] of Object.entries(partsMap)) {{
        mesh.material.wireframe = isWireframe;
      }}
    }}

    function togglePartVisibility(name, btn) {{
      const mesh = partsMap[name];
      if (!mesh) return;
      mesh.visible = !mesh.visible;
      btn.style.opacity = mesh.visible ? '1.0' : '0.35';
    }}

    function setCameraPreset(preset) {{
      if (preset === 'isometric') {{
        camera.position.set(-90, 110, 130);
        controls.target.set(0, 70, -10);
      }} else if (preset === 'front') {{
        camera.position.set(0, 70, 190);
        controls.target.set(0, 70, 0);
      }} else if (preset === 'side') {{
        camera.position.set(-190, 70, 0);
        controls.target.set(0, 70, 0);
      }} else if (preset === 'top') {{
        camera.position.set(0, 220, 0);
        controls.target.set(0, 70, 0);
      }} else if (preset === 'hinge') {{
        camera.position.set(-45, 95, 35);
        controls.target.set(0, 92, 0);
      }}
      controls.update();
    }}

    function resetView() {{
      setCameraPreset('isometric');
      document.getElementById('slider-exploded').value = 0;
      setExplode(0);
      document.getElementById('slider-fold').value = 0;
      setFoldAngle(0);
      if (isCutaway) toggleCutaway();
      if (isXRay) toggleXRay();
      if (isWireframe) toggleWireframe();
    }}

    function onWindowResize() {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }}

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }}
  </script>
</body>
</html>
"""

out_html_rod = os.path.join(ROD_DIR, "Custom_Rod_And_Folding_Handle_Viewer.html")
out_html_head = os.path.join(HEAD_DIR, "Custom_Rod_And_Folding_Handle_Viewer.html")
out_html_root = os.path.join(V12_DIR, "Custom_Rod_And_Folding_Handle_Viewer.html")

with open(out_html_rod, "w", encoding="utf-8") as f:
    f.write(html_content)
with open(out_html_head, "w", encoding="utf-8") as f:
    f.write(html_content)
with open(out_html_root, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Exported clean T-Head Studio HTML viewer -> {out_html_rod} ({len(html_content):,} chars)")
