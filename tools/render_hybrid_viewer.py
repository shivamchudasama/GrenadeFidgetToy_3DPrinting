"""Generate interactive 3D HTML assembly viewer for the Modified Hybrid Grenade."""
import os
import json
import sys
import base64

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

import build_custom_hybrid_modified as BHM

mod_dir = os.path.join(
    ROOT_DIR, "Derivatives", "custom", "Complete_STL_Set", "Custom_Hybrid_Grenade_Modified"
)
custom_dir = os.path.join(ROOT_DIR, "Derivatives", "custom")

items = BHM.build_modified_hybrid_items()
displacements = BHM.compute_hybrid_exploded_displacements(items)

glb_path = os.path.join(custom_dir, "Custom_Hybrid_Grenade_Modified_assembled.glb")
with open(glb_path, "rb") as f:
    glb_b64 = base64.b64encode(f.read()).decode("ascii")

parts_meta = []
for (name, m, color), disp in zip(items, displacements):
    vol = m.volume
    bb = m.bounds
    ext = bb[1] - bb[0]

    # Categorize group
    if "Bottom" in name or "Mid Shell" in name or "Internal Barrel" in name or "Upper Shell" in name or "Middle Spring" in name:
        group = "Base Mechanism"
    elif "Rod" in name or "Spinner Lever 06" in name or "Spinner Lever 07" in name or "Spinner Lever 08" in name:
        group = "Full-Depth Rod"
    else:
        group = "Modified Head & Lever"

    parts_meta.append({
        "name": name,
        "group": group,
        "color": list(color),
        "volume_mm3": round(float(vol), 1),
        "extents_mm": [round(float(x), 2) for x in ext],
        "disp": [round(float(d), 2) for d in disp],
    })

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Custom Hybrid Grenade (Modified) - Interactive 3D Viewer</title>
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
      border-radius: 14px;
      padding: 14px 22px;
      box-shadow: 0 12px 36px rgba(0,0,0,0.6);
      max-width: 450px;
    }}
    .header h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge {{
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      padding: 3px 8px;
      background: rgba(46, 160, 67, 0.25);
      border: 1px solid #2ea043;
      color: #3fb950;
      border-radius: 6px;
    }}
    .header p {{
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 6px;
      line-height: 1.4;
    }}
    .specs-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid rgba(255,255,255,0.1);
      font-size: 0.76rem;
    }}
    .spec-item span {{
      color: var(--text-muted);
      display: block;
    }}
    .spec-item strong {{
      color: var(--accent);
    }}

    /* Floating Control Bar */
    .toolbar {{
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      display: flex;
      align-items: center;
      gap: 10px;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 16px;
      padding: 10px 20px;
      box-shadow: 0 14px 44px rgba(0,0,0,0.7);
    }}
    .tool-btn {{
      background: var(--card-bg);
      border: 1px solid var(--panel-border);
      color: var(--text-main);
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}
    .tool-btn:hover {{
      background: rgba(88, 166, 255, 0.18);
      border-color: var(--accent);
      transform: translateY(-1px);
    }}
    .tool-btn.active {{
      background: var(--accent);
      color: #0d1117;
      border-color: var(--accent);
      font-weight: 600;
      box-shadow: 0 0 14px var(--accent-glow);
    }}

    .slider-group {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 0 12px;
      border-left: 1px solid var(--panel-border);
      border-right: 1px solid var(--panel-border);
    }}
    .slider-group label {{
      font-size: 0.78rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    input[type=range] {{
      appearance: none;
      background: rgba(255,255,255,0.18);
      height: 6px;
      border-radius: 3px;
      outline: none;
      width: 150px;
      cursor: pointer;
    }}
    input[type=range]::-webkit-slider-thumb {{
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 10px var(--accent-glow);
      cursor: pointer;
    }}

    /* Right Sidebar (Component Tree) */
    .sidebar {{
      position: absolute;
      top: 20px;
      right: 24px;
      width: 340px;
      max-height: calc(100vh - 48px);
      z-index: 10;
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--panel-border);
      border-radius: 14px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 14px 44px rgba(0,0,0,0.7);
      overflow: hidden;
    }}
    .sidebar-title {{
      font-size: 0.88rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .search-input {{
      width: 100%;
      background: var(--card-bg);
      border: 1px solid var(--panel-border);
      border-radius: 8px;
      padding: 6px 12px;
      color: var(--text-main);
      font-size: 0.8rem;
      outline: none;
    }}
    .search-input:focus {{
      border-color: var(--accent);
    }}
    .part-list {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      overflow-y: auto;
      padding-right: 4px;
      max-height: calc(100vh - 200px);
    }}
    .part-list::-webkit-scrollbar {{
      width: 4px;
    }}
    .part-list::-webkit-scrollbar-thumb {{
      background: rgba(255,255,255,0.25);
      border-radius: 2px;
    }}

    .group-header {{
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-top: 8px;
      margin-bottom: 2px;
      padding-left: 2px;
    }}

    .part-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--card-bg);
      border: 1px solid var(--panel-border);
      padding: 7px 10px;
      border-radius: 8px;
      font-size: 0.78rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .part-item:hover {{
      background: rgba(255,255,255,0.08);
      border-color: rgba(255,255,255,0.3);
    }}
    .part-info {{
      display: flex;
      align-items: center;
      gap: 8px;
      overflow: hidden;
    }}
    .part-color {{
      width: 12px;
      height: 12px;
      border-radius: 3px;
      flex-shrink: 0;
    }}
    .part-name {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 500;
    }}
    .part-vol {{
      font-size: 0.7rem;
      color: var(--text-muted);
      flex-shrink: 0;
    }}

    /* Loading Overlay */
    #loading-overlay {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #0a0c10;
      z-index: 100;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      transition: opacity 0.5s ease;
    }}
    .spinner {{
      width: 46px;
      height: 46px;
      border: 3px solid rgba(88, 166, 255, 0.2);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>

  <div id="loading-overlay">
    <div class="spinner"></div>
    <p style="color: var(--text-muted); font-size: 0.9rem; font-weight: 500;">Loading Custom Hybrid Grenade (Modified)...</p>
  </div>

  <div class="header">
    <h1>
      Hybrid Grenade Fidget Toy
      <span class="badge">36 Parts &bull; Modified</span>
    </h1>
    <p>Rebuilt with modified custom turned circular handles &bull; relocated neck lock at (12.00, 56.80) &bull; preloaded 16.80mm spring pocket.</p>
    <div class="specs-grid">
      <div class="spec-item"><span>Envelope Dimensions</span><strong>41.6 &times; 121.2 &times; 67.4 mm</strong></div>
      <div class="spec-item"><span>Tactile Mechanisms</span><strong>33-Waist + 32-Upper + 20-Gear</strong></div>
    </div>
  </div>

  <div id="canvas-container"></div>

  <div class="toolbar">
    <button class="tool-btn" id="btn-reset" title="Reset Camera View">🔄 Reset</button>
    <button class="tool-btn" id="btn-view-iso">📐 Isometric</button>
    <button class="tool-btn" id="btn-view-elevation">🏢 Elevation</button>
    <button class="tool-btn" id="btn-view-xray">✨ X-Ray / Glass</button>
    
    <div class="slider-group">
      <label for="explode-slider">Explode</label>
      <input type="range" id="explode-slider" min="0" max="1" step="0.01" value="0">
    </div>

    <button class="tool-btn" id="btn-anim-explode">🎬 Animate</button>
    <button class="tool-btn" id="btn-wireframe">🕸️ Wireframe</button>
  </div>

  <div class="sidebar">
    <div class="sidebar-title">
      <span>Components (36)</span>
      <button id="btn-toggle-all" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:0.75rem;">Show All</button>
    </div>
    <input type="text" class="search-input" id="search-input" placeholder="Filter parts...">
    <div class="part-list" id="part-list-container"></div>
  </div>

  <script>
    const PARTS_DATA = {json.dumps(parts_meta)};
    const GLB_BASE64 = "{glb_b64}";

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0c10);

    const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 1200);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Studio Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 0.85));

    const dir1 = new THREE.DirectionalLight(0xffffff, 1.3);
    dir1.position.set(100, 150, 120);
    scene.add(dir1);

    const dir2 = new THREE.DirectionalLight(0x79b8ff, 0.75);
    dir2.position.set(-100, -60, -100);
    scene.add(dir2);

    const dir3 = new THREE.DirectionalLight(0xffe4b5, 0.6);
    dir3.position.set(0, 120, -100);
    scene.add(dir3);

    // Floor Grid
    const grid = new THREE.GridHelper(300, 30, 0x30363d, 0x161b22);
    grid.position.set(0, -60, 0);
    scene.add(grid);

    const rootGroup = new THREE.Group();
    scene.add(rootGroup);

    const meshMap = {{}};
    const basePositions = {{}};
    let isXRay = false;
    let isWireframe = false;
    let animExplode = false;
    let animDir = 1;

    function resetCamera() {{
      camera.position.set(130, 80, 160);
      controls.target.set(0, 0, 0);
      controls.update();
    }}

    // Convert Base64 data to ArrayBuffer for GLTFLoader.parse
    function base64ToArrayBuffer(base64) {{
      const binaryString = window.atob(base64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {{
        bytes[i] = binaryString.charCodeAt(i);
      }}
      return bytes.buffer;
    }}

    const loader = new THREE.GLTFLoader();
    const arrayBuffer = base64ToArrayBuffer(GLB_BASE64);

    loader.parse(arrayBuffer, '', function(gltf) {{
      document.getElementById('loading-overlay').style.opacity = '0';
      setTimeout(() => document.getElementById('loading-overlay').style.display = 'none', 500);

      const box = new THREE.Box3().setFromObject(gltf.scene);
      const center = box.getCenter(new THREE.Vector3());

      gltf.scene.position.set(-center.x, -center.y, -center.z);
      rootGroup.add(gltf.scene);

      gltf.scene.traverse(function(child) {{
        if (child.isMesh || child.type === 'Mesh') {{
          child.geometry.computeVertexNormals();
          const nodeName = child.name || (child.parent ? child.parent.name : '');
          
          let meta = PARTS_DATA.find(p => p.name === nodeName || nodeName.includes(p.name) || p.name.includes(nodeName));
          if (!meta) {{
            const idx = Object.keys(meshMap).length;
            meta = PARTS_DATA[idx] || {{ name: nodeName, color: [180, 180, 180], disp: [0,0,0], volume_mm3: 0 }};
          }}
          
          const col = meta.color;
          const mat = new THREE.MeshStandardMaterial({{
            color: new THREE.Color(col[0]/255, col[1]/255, col[2]/255),
            metalness: 0.18,
            roughness: 0.35,
            side: THREE.DoubleSide
          }});
          child.material = mat;
          child.name = meta.name;
          meshMap[meta.name] = child;
          basePositions[meta.name] = child.position.clone();
        }}
      }});

      buildComponentTree();
      resetCamera();
    }}, function(error) {{
      console.error('Error parsing GLB buffer:', error);
    }});

    // Build Component UI List
    function buildComponentTree(filterText = '') {{
      const list = document.getElementById('part-list-container');
      list.innerHTML = '';

      let currentGroup = '';

      PARTS_DATA.forEach((meta) => {{
        if (filterText && !meta.name.toLowerCase().includes(filterText.toLowerCase())) {{
          return;
        }}

        if (meta.group !== currentGroup) {{
          currentGroup = meta.group;
          const grpEl = document.createElement('div');
          grpEl.className = 'group-header';
          grpEl.textContent = currentGroup;
          list.appendChild(grpEl);
        }}

        const item = document.createElement('div');
        item.className = 'part-item';
        item.innerHTML = `
          <div class="part-info">
            <div class="part-color" style="background: rgb(${{meta.color.join(',')}});"></div>
            <span class="part-name" title="${{meta.name}}">${{meta.name}}</span>
          </div>
          <span class="part-vol">${{meta.volume_mm3.toLocaleString()}} mm³</span>
        `;

        item.addEventListener('click', () => {{
          const mesh = meshMap[meta.name];
          if (mesh) {{
            mesh.visible = !mesh.visible;
            item.style.opacity = mesh.visible ? '1' : '0.35';
          }}
        }});

        list.appendChild(item);
      }});
    }}

    document.getElementById('search-input').addEventListener('input', (e) => {{
      buildComponentTree(e.target.value);
    }});

    // Explode Slider Logic
    const explodeSlider = document.getElementById('explode-slider');
    explodeSlider.addEventListener('input', function(e) {{
      const factor = parseFloat(e.target.value);
      applyExplode(factor);
    }});

    function applyExplode(factor) {{
      PARTS_DATA.forEach((meta) => {{
        const mesh = meshMap[meta.name];
        const base = basePositions[meta.name];
        if (mesh && base && meta.disp) {{
          mesh.position.set(
            base.x + meta.disp[0] * factor,
            base.y + meta.disp[1] * factor,
            base.z + meta.disp[2] * factor
          );
        }}
      }});
    }}

    // Toolbar Buttons
    document.getElementById('btn-reset').addEventListener('click', () => {{
      explodeSlider.value = 0;
      applyExplode(0);
      resetCamera();
    }});

    document.getElementById('btn-view-iso').addEventListener('click', () => {{
      camera.position.set(130, 80, 160);
      controls.target.set(0, 0, 0);
      controls.update();
    }});

    document.getElementById('btn-view-elevation').addEventListener('click', () => {{
      camera.position.set(0, 20, 220);
      controls.target.set(0, 20, 0);
      controls.update();
    }});

    document.getElementById('btn-view-xray').addEventListener('click', function() {{
      isXRay = !isXRay;
      this.classList.toggle('active', isXRay);
      Object.values(meshMap).forEach(mesh => {{
        if (mesh.material) {{
          mesh.material.transparent = isXRay;
          mesh.material.opacity = isXRay ? 0.38 : 1.0;
          mesh.material.roughness = isXRay ? 0.1 : 0.35;
        }}
      }});
    }});

    document.getElementById('btn-wireframe').addEventListener('click', function() {{
      isWireframe = !isWireframe;
      this.classList.toggle('active', isWireframe);
      Object.values(meshMap).forEach(mesh => {{
        if (mesh.material) {{
          mesh.material.wireframe = isWireframe;
        }}
      }});
    }});

    document.getElementById('btn-anim-explode').addEventListener('click', function() {{
      animExplode = !animExplode;
      this.classList.toggle('active', animExplode);
    }});

    document.getElementById('btn-toggle-all').addEventListener('click', () => {{
      Object.values(meshMap).forEach(m => m.visible = true);
      document.querySelectorAll('.part-item').forEach(el => el.style.opacity = '1');
    }});

    // Render Loop
    function animate() {{
      requestAnimationFrame(animate);

      if (animExplode) {{
        let val = parseFloat(explodeSlider.value);
        val += 0.008 * animDir;
        if (val >= 1.0) {{ val = 1.0; animDir = -1; }}
        if (val <= 0.0) {{ val = 0.0; animDir = 1; }}
        explodeSlider.value = val;
        applyExplode(val);
      }}

      controls.update();
      renderer.render(scene, camera);
    }}
    animate();

    window.addEventListener('resize', onWindowResize, false);
    function onWindowResize() {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }}
  </script>
</body>
</html>
"""

p1 = os.path.join(custom_dir, "hybrid_modified_assembly_viewer.html")
p2 = os.path.join(mod_dir, "hybrid_modified_assembly_viewer.html")

with open(p1, "w", encoding="utf-8") as f:
    f.write(html_content)
with open(p2, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated standalone: {p1} ({os.path.getsize(p1):,} bytes)")
print(f"Generated standalone: {p2} ({os.path.getsize(p2):,} bytes)")
