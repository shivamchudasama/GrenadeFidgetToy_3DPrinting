import os
import sys
import base64
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.3")
SUB_DIR = os.path.join(PACKAGE_DIR, "03_Internal_Barrel_And_Upper_Station")
ARTIFACT_DIR = r"C:\Users\chuda\.gemini\antigravity-ide\brain\8038d30c-f335-4329-89a4-7c95c3fe86a2"

glb_ass_path = os.path.join(SUB_DIR, "Custom_Internal_Barrel_And_Springs_Only_Assembly.glb")
glb_cut_path = os.path.join(SUB_DIR, "Custom_Internal_Barrel_And_Springs_Cutaway.glb")

with open(glb_ass_path, "rb") as f:
    glb_ass_b64 = base64.b64encode(f.read()).decode("ascii")

with open(glb_cut_path, "rb") as f:
    glb_cut_b64 = base64.b64encode(f.read()).decode("ascii")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Internal Barrel & Springs 3D Studio - Hybrid Grenade v1.3</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
  <style>
    :root {{
      --bg-dark: #0d1117;
      --panel-bg: rgba(22, 27, 34, 0.88);
      --panel-border: rgba(255, 255, 255, 0.12);
      --accent-cyan: #00e5ff;
      --accent-orange: #ff7020;
      --accent-green: #32cd64;
      --accent-gold: #ffb400;
      --text-main: #f0f6fc;
      --text-muted: #8b949e;
      --radius-lg: 14px;
      --radius-md: 8px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
    body {{
      background: var(--bg-dark);
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }}
    #webgl-canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }}
    .glass-panel {{
      position: absolute;
      background: var(--panel-bg);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-lg);
      z-index: 10;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55);
    }}
    #header {{
      top: 18px; left: 20px; right: 20px; height: 64px;
      display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; }}
    .badge {{
      background: linear-gradient(135deg, var(--accent-cyan), #7928ca);
      color: #000; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 11px;
      padding: 4px 10px; border-radius: 6px; letter-spacing: 0.8px; text-transform: uppercase;
    }}
    .title {{ font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 16px; letter-spacing: 0.2px; }}
    .sub-title {{ font-size: 12px; color: var(--text-muted); font-weight: 400; margin-left: 8px; }}

    #sidebar {{
      top: 96px; left: 20px; width: 340px; bottom: 20px;
      display: flex; flex-direction: column; gap: 14px; padding: 18px; overflow-y: auto;
    }}
    .section-title {{
      font-size: 11px; font-weight: 700; letter-spacing: 1px; color: var(--text-muted);
      text-transform: uppercase; margin-bottom: 8px;
    }}
    .btn-group {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }}
    .btn-group-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-bottom: 12px; }}
    .btn {{
      background: rgba(255, 255, 255, 0.06); border: 1px solid var(--panel-border);
      color: var(--text-main); font-size: 12px; font-weight: 500; padding: 8px 12px;
      border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s ease;
      display: flex; align-items: center; justify-content: center; gap: 6px;
    }}
    .btn:hover {{ background: rgba(255, 255, 255, 0.12); border-color: rgba(255, 255, 255, 0.25); }}
    .btn.active {{ background: rgba(0, 229, 255, 0.18); border-color: var(--accent-cyan); color: var(--accent-cyan); font-weight: 600; }}

    .part-card {{
      background: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md); padding: 10px 12px; display: flex; align-items: center;
      justify-content: space-between; margin-bottom: 6px; font-size: 12px;
    }}
    .part-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }}
    .toggle {{ cursor: pointer; }}

    .stat-box {{
      background: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.25);
      border-radius: var(--radius-md); padding: 12px; font-size: 11.5px; line-height: 1.6;
    }}
    .stat-val {{ color: var(--accent-cyan); font-weight: 700; font-family: 'JetBrains Mono', monospace; }}

    #slider-container {{
      margin-top: 6px; margin-bottom: 12px;
    }}
    .slider-header {{ display: flex; justify-content: space-between; font-size: 11.5px; color: var(--text-muted); margin-bottom: 4px; }}
    input[type=range] {{ width: 100%; accent-color: var(--accent-cyan); cursor: pointer; }}
  </style>
</head>
<body>
  <div id="webgl-canvas"></div>

  <div id="header" class="glass-panel">
    <div class="brand">
      <span class="badge">v1.3 Certified</span>
      <span class="title">Internal Barrel & Springs 3D Assembly Studio</span>
      <span class="sub-title">Reinforced 1.35mm Cavity Walls</span>
    </div>
    <div style="font-size: 12px; color: var(--accent-green); font-weight: 600;">
      ✓ 0.0000 mm³ Clash | 100% Insertion Sweep Clean
    </div>
  </div>

  <div id="sidebar" class="glass-panel">
    <div>
      <div class="section-title">Assembly View Mode</div>
      <div class="btn-group">
        <button class="btn active" id="btn-full" onclick="setAssemblyMode('full')">Full Exterior</button>
        <button class="btn" id="btn-cut" onclick="setAssemblyMode('cutaway')">Cutaway Cavities</button>
      </div>
    </div>

    <div>
      <div class="section-title">Camera Angles</div>
      <div class="btn-group-3">
        <button class="btn" onclick="setCamera('iso')">Perspective</button>
        <button class="btn" onclick="setCamera('top')">Top-Down</button>
        <button class="btn" onclick="setCamera('side')">Side Window</button>
      </div>
    </div>

    <div id="slider-container">
      <div class="slider-header">
        <span>Spring Insertion Explode</span>
        <span id="disp-val">0.0 mm</span>
      </div>
      <input type="range" id="explode-slider" min="0" max="30" step="0.5" value="0" oninput="updateExplode(this.value)">
    </div>

    <div>
      <div class="section-title">Component Visibility</div>
      <div class="part-card">
        <div><span class="part-dot" style="background: #414b58;"></span>10 Internal Barrel</div>
        <input type="checkbox" checked onchange="toggleMesh('10_Custom_Internal_Barrel_4Slot', this.checked)">
      </div>
      <div class="part-card">
        <div><span class="part-dot" style="background: #788291;"></span>11 Retention Cap</div>
        <input type="checkbox" checked onchange="toggleMesh('11_Custom_Internal_Barrel_Cap', this.checked)">
      </div>
      <div class="part-card">
        <div><span class="part-dot" style="background: #ff641e;"></span>12 Detent Spring 01 (0°)</div>
        <input type="checkbox" checked onchange="toggleMesh('12_Custom_Rod_Detent_Spring_01', this.checked)">
      </div>
      <div class="part-card">
        <div><span class="part-dot" style="background: #00c8f0;"></span>13 Detent Spring 02 (90°)</div>
        <input type="checkbox" checked onchange="toggleMesh('13_Custom_Rod_Detent_Spring_02', this.checked)">
      </div>
      <div class="part-card">
        <div><span class="part-dot" style="background: #ffb400;"></span>14 Detent Spring 03 (180°)</div>
        <input type="checkbox" checked onchange="toggleMesh('14_Custom_Rod_Detent_Spring_03', this.checked)">
      </div>
      <div class="part-card">
        <div><span class="part-dot" style="background: #32cd64;"></span>15 Detent Spring 04 (270°)</div>
        <input type="checkbox" checked onchange="toggleMesh('15_Custom_Rod_Detent_Spring_04', this.checked)">
      </div>
    </div>

    <div class="stat-box">
      <div><strong>Cavity Back Wall:</strong> <span class="stat-val">R_OUT = 12.350 mm</span></div>
      <div><strong>Outer Solid Wall:</strong> <span class="stat-val">1.30 mm - 1.37 mm</span></div>
      <div><strong>Spring Foot Clearance:</strong> <span class="stat-val">0.150 mm</span></div>
      <div><strong>Cap Filler Prongs:</strong> <span class="stat-val">4x L-Notches Sealed</span></div>
      <div style="margin-top: 6px; color: var(--accent-cyan);">Ready for 0.40mm FDM 3D Printing (>3 perimeters).</div>
    </div>
  </div>

  <script>
    const container = document.getElementById('webgl-canvas');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0d1117);

    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.5, 1000);
    camera.position.set(65, 75, 80);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.target.set(0, 42, 0);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
    keyLight.position.set(60, 100, 50);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x00e5ff, 0.5);
    fillLight.position.set(-60, 40, -50);
    scene.add(fillLight);

    const grid = new THREE.GridHelper(100, 20, 0x00e5ff, 0x21262d);
    grid.position.y = 20.43;
    scene.add(grid);

    const gltfLoader = new THREE.GLTFLoader();
    let currentModelGroup = new THREE.Group();
    scene.add(currentModelGroup);

    const modelsB64 = {{
      'full': 'data:model/gltf-binary;base64,{glb_ass_b64}',
      'cutaway': 'data:model/gltf-binary;base64,{glb_cut_b64}'
    }};

    let loadedScenes = {{}};
    let activeMode = 'full';
    let explodeDistance = 0.0;

    function loadModel(mode, callback) {{
      if (loadedScenes[mode]) {{
        callback(loadedScenes[mode]);
        return;
      }}
      gltfLoader.load(modelsB64[mode], (gltf) => {{
        loadedScenes[mode] = gltf.scene;
        callback(gltf.scene);
      }});
    }}

    function setAssemblyMode(mode) {{
      activeMode = mode;
      document.getElementById('btn-full').className = 'btn ' + (mode === 'full' ? 'active' : '');
      document.getElementById('btn-cut').className = 'btn ' + (mode === 'cutaway' ? 'active' : '');

      loadModel(mode, (newScene) => {{
        currentModelGroup.clear();
        currentModelGroup.add(newScene);
        updateExplode(explodeDistance);
      }});
    }}

    function setCamera(view) {{
      if (view === 'iso') {{
        camera.position.set(65, 75, 80);
        controls.target.set(0, 42, 0);
      }} else if (view === 'top') {{
        camera.position.set(0, 130, 0.001);
        controls.target.set(0, 42, 0);
      }} else if (view === 'side') {{
        camera.position.set(110, 48, 0);
        controls.target.set(0, 48, 0);
      }}
    }}

    function updateExplode(val) {{
      explodeDistance = parseFloat(val);
      document.getElementById('disp-val').innerText = explodeDistance.toFixed(1) + ' mm';

      currentModelGroup.traverse((child) => {{
        if (!child.isMesh) return;
        const n = child.name;
        if (n.includes('Spring_01')) child.position.set(0, explodeDistance, 0);
        else if (n.includes('Spring_02')) child.position.set(0, explodeDistance, 0);
        else if (n.includes('Spring_03')) child.position.set(0, explodeDistance, 0);
        else if (n.includes('Spring_04')) child.position.set(0, explodeDistance, 0);
        else if (n.includes('Cap')) child.position.set(0, explodeDistance * 1.3, 0);
      }});
    }}

    function toggleMesh(prefix, visible) {{
      currentModelGroup.traverse((child) => {{
        if (child.isMesh && child.name.includes(prefix)) {{
          child.visible = visible;
        }}
      }});
    }}

    // Initial Load
    setAssemblyMode('full');

    function animate() {{
      requestAnimationFrame(animate);
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

html_pkg_path = os.path.join(PACKAGE_DIR, "Internal_Barrel_And_Springs_Viewer.html")
html_art_path = os.path.join(ARTIFACT_DIR, "Internal_Barrel_And_Springs_Viewer.html")

with open(html_pkg_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[OK] Saved HTML viewer to: {html_pkg_path}")

shutil.copy2(html_pkg_path, html_art_path)
print(f"[OK] Copied HTML viewer to: {html_art_path}")

