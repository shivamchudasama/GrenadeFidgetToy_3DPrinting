"""Build and export the complete 6-part assembled rod from 04_Rod_Assembly_And_Locks.

This script loads the 6 parts forming the complete Custom Rod Assembly:
  1. 22_Custom_Rod_Right (Right full-height clamp)
  2. 23_Custom_Rod_Middle (Center solid rod with rack & integral yoke)
  3. 24_Custom_Rod_Left (Left full-height clamp)
  4. 25_Custom_Rod_Lock_Upper_06 (Upper transverse cross-key 06)
  5. 26_Custom_Rod_Lock_Lower_07 (Lower transverse cross-key 07)
  6. 27_Spinner_Lever_08_Rod_Lock (Bottom axial slotted retainer disc 08)

Outputs:
  - Hybrid_Grenade_v1.2/04_Rod_Assembly_And_Locks/Custom_Rod_Assembly.stl
  - Hybrid_Grenade_v1.2/04_Rod_Assembly_And_Locks/Custom_Rod_Assembly.3mf
  - Hybrid_Grenade_v1.2/04_Rod_Assembly_And_Locks/Custom_Rod_Assembly.glb
  - Hybrid_Grenade_v1.2/04_Rod_Assembly_And_Locks/Custom_Rod_Assembly_Exploded.glb
  - Hybrid_Grenade_v1.2/04_Rod_Assembly_And_Locks/Custom_Rod_Assembly_Viewer.html
  - Hybrid_Grenade_v1.2/Custom_Rod_Assembly.stl
  - Hybrid_Grenade_v1.2/Custom_Rod_Assembly.3mf
  - Hybrid_Grenade_v1.2/Custom_Rod_Assembly.glb
"""
from __future__ import annotations

import base64
import io
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import trimesh
import manifold3d

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
ASY_DIR = os.path.join(V12_DIR, "All_Parts_Assembled_Coordinates")
ROD_DIR = os.path.join(V12_DIR, "04_Rod_Assembly_And_Locks")

ROD_PARTS = [
    {
        "id": 22,
        "filename": "22_Custom_Rod_Right.stl",
        "name": "Custom Rod Right Clamp",
        "desc": "Full-height right clamp with upper hex key cheek & spring pod wall",
        "color_rgb": (86, 182, 178),      # Cyan / Teal
        "color_hex": "#56B6B2",
        "disp": np.array([-18.0, 0.0, 0.0]),
    },
    {
        "id": 23,
        "filename": "23_Custom_Rod_Middle.stl",
        "name": "Custom Rod Middle Core",
        "desc": "Solid central rod with dual gear racks (+Z/-Z), integral hinge yoke, and transverse tunnels",
        "color_rgb": (55, 65, 81),       # Charcoal / Gunmetal
        "color_hex": "#374151",
        "disp": np.array([0.0, 0.0, 0.0]),
    },
    {
        "id": 24,
        "filename": "24_Custom_Rod_Left.stl",
        "name": "Custom Rod Left Clamp",
        "desc": "Full-height left clamp with upper hex key cheek & spring pod wall",
        "color_rgb": (184, 126, 152),     # Mauve / Rose
        "color_hex": "#B87E98",
        "disp": np.array([18.0, 0.0, 0.0]),
    },
    {
        "id": 25,
        "filename": "25_Custom_Rod_Lock_Upper_06.stl",
        "name": "Upper Transverse Cross-Key (06)",
        "desc": "Upper cross-key locking left, middle, and right rod members together",
        "color_rgb": (239, 68, 68),       # Crimson Red
        "color_hex": "#EF4444",
        "disp": np.array([0.0, 0.0, 20.0]),
    },
    {
        "id": 26,
        "filename": "26_Custom_Rod_Lock_Lower_07.stl",
        "name": "Lower Transverse Cross-Key (07)",
        "desc": "Lower cross-key locking left, middle, and right rod members together",
        "color_rgb": (245, 158, 11),      # Amber Orange
        "color_hex": "#F59E0B",
        "disp": np.array([0.0, 0.0, 20.0]),
    },
    {
        "id": 27,
        "filename": "27_Spinner_Lever_08_Rod_Lock.stl",
        "name": "Bottom Retainer Disc (08)",
        "desc": "Slotted axial retainer disc locking onto bottom taper",
        "color_rgb": (16, 185, 129),      # Emerald Green
        "color_hex": "#10B981",
        "disp": np.array([0.0, -18.0, 0.0]),
    },
]


def load_rod_parts():
    loaded = []
    for info in ROD_PARTS:
        path = os.path.join(ASY_DIR, info["filename"])
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing assembled source: {path}")
        mesh = trimesh.load(path, force="mesh", process=True)
        loaded.append({
            **info,
            "mesh": mesh,
        })
    return loaded


def create_solid_stl(parts):
    """Create a clean, watertight single-body STL by unioning all components."""
    manifolds = []
    for p in parts:
        m = p["mesh"]
        src = manifold3d.Mesh64(
            np.ascontiguousarray(m.vertices, dtype=np.float64),
            np.ascontiguousarray(m.faces, dtype=np.uint64),
            tolerance=1e-5,
        )
        src.merge()
        mani = manifold3d.Manifold(src)
        manifolds.append(mani)

    # Boolean union all parts together
    combined_manifold = manifolds[0]
    for mani in manifolds[1:]:
        combined_manifold = combined_manifold + mani

    rebuilt = combined_manifold.to_mesh64()
    fused_mesh = trimesh.Trimesh(
        vertices=np.asarray(rebuilt.vert_properties)[:, :3],
        faces=np.asarray(rebuilt.tri_verts),
        process=True,
    )
    return fused_mesh


def export_3mf_project(parts, output_path):
    """Export multi-body 3MF with per-part material colors, names, and objects."""
    scene = trimesh.Scene()
    for p in parts:
        m = p["mesh"].copy()
        r, g, b = p["color_rgb"]
        m.visual = trimesh.visual.ColorVisuals(
            mesh=m,
            vertex_colors=np.tile([r, g, b, 255], (len(m.vertices), 1))
        )
        scene.add_geometry(m, node_name=p["name"], geom_name=p["name"])

    # Export basic 3MF
    data_3mf = scene.export(file_type="3mf")
    with open(output_path, "wb") as f:
        f.write(data_3mf)

    # Inject rich 3MF metadata and basematerials
    with zipfile.ZipFile(output_path, "r") as source:
        members = [(info, source.read(info.filename)) for info in source.infolist()]

    model_idx = next((i for i, (info, _) in enumerate(members) if info.filename.endswith(".model")), None)
    if model_idx is not None:
        info, data = members[model_idx]
        root = ET.fromstring(data)
        ns = root.tag.partition("}")[0].lstrip("{")
        ET.register_namespace("", ns)

        def q(tag):
            return f"{{{ns}}}{tag}"

        resources = root.find(q("resources"))
        if resources is not None:
            mat_id = 100
            materials = ET.Element(q("basematerials"), {"id": str(mat_id)})
            resources.insert(0, materials)

            for idx, p in enumerate(parts):
                r, g, b = p["color_rgb"]
                ET.SubElement(
                    materials,
                    q("base"),
                    {
                        "name": p["name"],
                        "displaycolor": f"#{r:02X}{g:02X}{b:02X}FF",
                    }
                )

            objects = resources.findall(q("object"))
            for idx, obj in enumerate(objects):
                if idx < len(parts):
                    obj.set("name", parts[idx]["name"])
                    obj.set("pid", str(mat_id))
                    obj.set("pindex", str(idx))

            members[model_idx] = (info, ET.tostring(root, encoding="utf-8", xml_declaration=True))

        with zipfile.ZipFile(output_path, "w") as target:
            for member_info, member_data in members:
                target.writestr(member_info, member_data)


def export_glb_models(parts, assembled_glb_path, exploded_glb_path):
    """Export PBR GLB models for both fully assembled and exploded states."""
    # 1. Assembled GLB
    scene_asy = trimesh.Scene()
    for p in parts:
        m = p["mesh"].copy()
        r, g, b = p["color_rgb"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        mat = trimesh.visual.material.PBRMaterial(
            baseColorFactor=color_norm,
            metallicFactor=0.35,
            roughnessFactor=0.45,
            name=f"mat_{p['id']}",
        )
        m.visual = trimesh.visual.TextureVisuals(material=mat)
        scene_asy.add_geometry(m, node_name=p["name"], geom_name=p["name"])

    glb_asy_bytes = scene_asy.export(file_type="glb")
    with open(assembled_glb_path, "wb") as f:
        f.write(glb_asy_bytes)

    # 2. Exploded GLB
    scene_exp = trimesh.Scene()
    for p in parts:
        m = p["mesh"].copy()
        m.apply_translation(p["disp"])
        r, g, b = p["color_rgb"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        mat = trimesh.visual.material.PBRMaterial(
            baseColorFactor=color_norm,
            metallicFactor=0.35,
            roughnessFactor=0.45,
            name=f"mat_{p['id']}_exp",
        )
        m.visual = trimesh.visual.TextureVisuals(material=mat)
        scene_exp.add_geometry(m, node_name=f"{p['name']} (Exploded)", geom_name=f"{p['name']}_exp")

    glb_exp_bytes = scene_exp.export(file_type="glb")
    with open(exploded_glb_path, "wb") as f:
        f.write(glb_exp_bytes)

    return glb_asy_bytes


def generate_interactive_viewer(parts, glb_bytes, output_html_path):
    """Build standalone interactive 3D HTML viewer with WebGL and Three.js."""
    glb_b64 = base64.b64encode(glb_bytes).decode("ascii")

    parts_json = []
    for p in parts:
        m = p["mesh"]
        bb = m.bounds
        ext = bb[1] - bb[0]
        parts_json.append({
            "id": p["id"],
            "name": p["name"],
            "filename": p["filename"],
            "desc": p["desc"],
            "color_rgb": p["color_rgb"],
            "color_hex": p["color_hex"],
            "volume_mm3": round(float(m.volume), 1),
            "extents_mm": [round(float(x), 2) for x in ext],
            "disp": [round(float(d), 2) for d in p["disp"]],
        })

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Custom Rod Assembly - 6 Parts (Hybrid Grenade v1.2)</title>
  <style>
    :root {{
      --bg-dark: #0f172a;
      --bg-card: rgba(30, 41, 59, 0.88);
      --border-color: rgba(255, 255, 255, 0.12);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.35);
      --success: #34d399;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    body {{
      background: radial-gradient(circle at 50% 35%, #1e293b 0%, #090d16 100%);
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
      width: 400px;
      height: 100%;
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      border-left: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      padding: 24px;
      gap: 18px;
      overflow-y: auto;
      z-index: 10;
      box-shadow: -8px 0 24px rgba(0,0,0,0.4);
    }}
    h1 {{
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
    }}
    .subtitle {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.4;
    }}
    .control-card {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .slider-row {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .slider-label {{
      display: flex;
      justify-content: space-between;
      font-size: 0.82rem;
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
      background: var(--accent);
      cursor: pointer;
      box-shadow: 0 0 10px var(--accent-glow);
    }}
    .btn-group {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }}
    button {{
      background: rgba(51, 65, 85, 0.8);
      color: #fff;
      border: 1px solid var(--border-color);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    button:hover {{
      background: var(--accent);
      color: #090d16;
      font-weight: 600;
    }}
    .parts-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 380px;
      overflow-y: auto;
      padding-right: 4px;
    }}
    .part-item {{
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .part-item:hover, .part-item.active {{
      border-color: var(--accent);
      background: rgba(56, 189, 248, 0.08);
    }}
    .part-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .part-title-wrap {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .color-dot {{
      width: 14px;
      height: 14px;
      border-radius: 4px;
      border: 1px solid rgba(255,255,255,0.4);
      flex-shrink: 0;
    }}
    .part-title {{
      font-size: 0.85rem;
      font-weight: 600;
    }}
    .part-meta {{
      font-size: 0.75rem;
      color: var(--text-muted);
      display: flex;
      gap: 12px;
    }}
    .part-desc {{
      font-size: 0.76rem;
      color: #cbd5e1;
      line-height: 1.35;
    }}
    #toolbar {{
      position: absolute;
      bottom: 24px;
      left: 24px;
      display: flex;
      gap: 10px;
      z-index: 5;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(12px);
      padding: 8px 12px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
    }}
    .info-overlay {{
      position: absolute;
      top: 24px;
      left: 24px;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(12px);
      padding: 14px 18px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
      font-size: 0.85rem;
      pointer-events: none;
    }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
  <div id="canvas-container">
    <div class="info-overlay">
      <div style="font-weight: 700; color: var(--accent); margin-bottom: 4px;">6-Part Custom Rod Assembly</div>
      <div style="color: var(--text-muted); font-size: 0.78rem;">Left click + drag to rotate • Right click to pan • Scroll to zoom</div>
    </div>
    <div id="toolbar">
      <button id="btn-reset">Reset View</button>
      <button id="btn-wireframe">Toggle Wireframe</button>
      <button id="btn-autorotate">Auto Rotate</button>
    </div>
  </div>

  <div id="sidebar">
    <div>
      <h1>Solid Yoke Rod <span class="badge">6 Parts</span></h1>
      <p class="subtitle" style="margin-top: 6px;">Unified mechanical assembly from <code>04_Rod_Assembly_And_Locks</code> with full dual gear rack teeth, hexagonal key cheek, and interlocking transverse cross-keys.</p>
    </div>

    <div class="control-card">
      <div class="slider-row">
        <div class="slider-label">
          <span>Exploded View</span>
          <span id="expl-val" style="color: var(--accent);">0%</span>
        </div>
        <input type="range" id="slider-exploded" min="0" max="100" value="0">
      </div>
      <div class="btn-group">
        <button id="btn-exp-0">Assembled</button>
        <button id="btn-exp-50">50%</button>
        <button id="btn-exp-100">Exploded</button>
      </div>
    </div>

    <div style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">
      Assembly Components
    </div>

    <div class="parts-list" id="parts-list"></div>
  </div>

  <script>
    const PARTS_DATA = {json.dumps(parts_json)};
    const GLB_B64 = "{glb_b64}";

    // Three.js Setup
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(45, 75, 95);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 55, 0);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight1.position.set(60, 100, 60);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.6);
    dirLight2.position.set(-60, -30, -50);
    scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0xffffff, 0.5);
    pointLight.position.set(0, 80, 40);
    scene.add(pointLight);

    // Grid Floor
    const grid = new THREE.GridHelper(160, 32, 0x38bdf8, 0x1e293b);
    grid.position.y = 12;
    scene.add(grid);

    // Load Model
    const loader = new THREE.GLTFLoader();
    const meshMap = new Map();
    let isWireframe = false;
    let autoRotate = false;

    const binaryData = atob(GLB_B64);
    const bytes = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {{
      bytes[i] = binaryData.charCodeAt(i);
    }}

    loader.parse(bytes.buffer, '', (gltf) => {{
      const root = gltf.scene;
      scene.add(root);

      root.traverse((child) => {{
        if (child.isMesh) {{
          child.originalPos = child.position.clone();
          for (const p of PARTS_DATA) {{
            if (child.name.includes(p.name) || p.name.includes(child.name)) {{
              meshMap.set(p.id, child);
              child.partMeta = p;
              break;
            }}
          }}
        }}
      }});
    }});

    // Build sidebar list
    const partsListEl = document.getElementById('parts-list');
    PARTS_DATA.forEach((p) => {{
      const item = document.createElement('div');
      item.className = 'part-item';
      item.id = `part-item-${{p.id}}`;
      item.innerHTML = `
        <div class="part-header">
          <div class="part-title-wrap">
            <div class="color-dot" style="background: ${{p.color_hex}};"></div>
            <div class="part-title">${{p.name}}</div>
          </div>
          <span style="font-size: 0.72rem; color: var(--accent); font-family: monospace;">#${{p.id}}</span>
        </div>
        <div class="part-desc">${{p.desc}}</div>
        <div class="part-meta">
          <span>Vol: ${{p.volume_mm3}} mm³</span>
          <span>STL: ${{p.filename}}</span>
        </div>
      `;
      item.addEventListener('click', () => {{
        document.querySelectorAll('.part-item').forEach(el => el.classList.remove('active'));
        item.classList.add('active');
        const mesh = meshMap.get(p.id);
        if (mesh) {{
          controls.target.copy(mesh.position).add(new THREE.Vector3(0, 0, 0));
        }}
      }});
      partsListEl.appendChild(item);
    }});

    // Exploded Slider Logic
    const slider = document.getElementById('slider-exploded');
    const explVal = document.getElementById('expl-val');

    function updateExploded(factor) {{
      explVal.innerText = `${{Math.round(factor * 100)}}%`;
      PARTS_DATA.forEach((p) => {{
        const mesh = meshMap.get(p.id);
        if (mesh && mesh.originalPos) {{
          mesh.position.x = mesh.originalPos.x + p.disp[0] * factor;
          mesh.position.y = mesh.originalPos.y + p.disp[1] * factor;
          mesh.position.z = mesh.originalPos.z + p.disp[2] * factor;
        }}
      }});
    }}

    slider.addEventListener('input', (e) => {{
      updateExploded(e.target.value / 100);
    }});

    document.getElementById('btn-exp-0').onclick = () => {{ slider.value = 0; updateExploded(0); }};
    document.getElementById('btn-exp-50').onclick = () => {{ slider.value = 50; updateExploded(0.5); }};
    document.getElementById('btn-exp-100').onclick = () => {{ slider.value = 100; updateExploded(1.0); }};

    document.getElementById('btn-reset').onclick = () => {{
      camera.position.set(45, 75, 95);
      controls.target.set(0, 55, 0);
      slider.value = 0;
      updateExploded(0);
      document.querySelectorAll('.part-item').forEach(el => el.classList.remove('active'));
    }};

    document.getElementById('btn-wireframe').onclick = () => {{
      isWireframe = !isWireframe;
      meshMap.forEach((mesh) => {{
        if (mesh.material) {{
          mesh.material.wireframe = isWireframe;
        }}
      }});
    }};

    document.getElementById('btn-autorotate').onclick = () => {{
      autoRotate = !autoRotate;
      controls.autoRotate = autoRotate;
      controls.autoRotateSpeed = 2.5;
    }};

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
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    print("[1/5] Loading 6 rod assembly components from assembled space...")
    parts = load_rod_parts()
    for p in parts:
        m = p["mesh"]
        print(f"  - [{p['id']}] {p['name']}: {p['filename']} (vol={m.volume:.2f} mm3, bounds={m.bounds.tolist()})")

    # Destination directories
    os.makedirs(ROD_DIR, exist_ok=True)
    os.makedirs(V12_DIR, exist_ok=True)

    # 1. Solid / Fused Watertight STL
    print("\n[2/5] Creating solid watertight assembly STL...")
    fused_mesh = create_solid_stl(parts)
    print(f"  -> Solid STL: is_watertight={fused_mesh.is_watertight}, vol={fused_mesh.volume:.2f} mm3, vertices={len(fused_mesh.vertices)}, faces={len(fused_mesh.faces)}")
    
    out_stl_sub = os.path.join(ROD_DIR, "Custom_Rod_Assembly.stl")
    out_stl_pkg = os.path.join(V12_DIR, "Custom_Rod_Assembly.stl")
    fused_mesh.export(out_stl_sub)
    fused_mesh.export(out_stl_pkg)
    print(f"  -> Exported: {out_stl_sub}")
    print(f"  -> Exported: {out_stl_pkg}")

    # 2. Multi-Body 3MF with Color Metadata
    print("\n[3/5] Exporting Multi-Body 3MF project plate...")
    out_3mf_sub = os.path.join(ROD_DIR, "Custom_Rod_Assembly.3mf")
    out_3mf_pkg = os.path.join(V12_DIR, "Custom_Rod_Assembly.3mf")
    export_3mf_project(parts, out_3mf_sub)
    export_3mf_project(parts, out_3mf_pkg)
    print(f"  -> Exported: {out_3mf_sub}")
    print(f"  -> Exported: {out_3mf_pkg}")

    # 3. PBR GLB Models (Assembled & Exploded)
    print("\n[4/5] Exporting GLB 3D models (Assembled + Exploded)...")
    out_glb_asy_sub = os.path.join(ROD_DIR, "Custom_Rod_Assembly.glb")
    out_glb_exp_sub = os.path.join(ROD_DIR, "Custom_Rod_Assembly_Exploded.glb")
    out_glb_asy_pkg = os.path.join(V12_DIR, "Custom_Rod_Assembly.glb")

    glb_asy_bytes = export_glb_models(parts, out_glb_asy_sub, out_glb_exp_sub)
    with open(out_glb_asy_pkg, "wb") as f:
        f.write(glb_asy_bytes)
    print(f"  -> Exported: {out_glb_asy_sub}")
    print(f"  -> Exported: {out_glb_exp_sub}")
    print(f"  -> Exported: {out_glb_asy_pkg}")

    # 4. Interactive 3D HTML Viewer
    print("\n[5/5] Generating standalone interactive 3D WebGL viewer...")
    out_html = os.path.join(ROD_DIR, "Custom_Rod_Assembly_Viewer.html")
    generate_interactive_viewer(parts, glb_asy_bytes, out_html)
    print(f"  -> Exported: {out_html}")

    print("\n[SUCCESS] Complete 6-part Custom Rod Assembly successfully built and exported!")


if __name__ == "__main__":
    main()
