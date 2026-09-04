"""Build and export the 6-part assembled Internal Barrel & Springs Sub-Assembly.

This script manages the 6 components requested:
  1. 10_Custom_Internal_Barrel_4Slot (4-slot internal barrel chassis)
  2. 11_Custom_Internal_Barrel_Cap (Top retention disc cap)
  3. 12_Custom_Rod_Detent_Spring_01 (Axial rod detent spring 01 - az 0°, single-headed)
  4. 13_Custom_Rod_Detent_Spring_02 (Axial rod detent spring 02 - az 90°, single-headed)
  5. 14_Custom_Rod_Detent_Spring_03 (Axial rod detent spring 03 - az 180°, single-headed)
  6. 15_Custom_Rod_Detent_Spring_04 (Axial rod detent spring 04 - az 270°, single-headed)

Outputs:
  - Hybrid_Grenade_v1.2/03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_Assembly.glb
  - Hybrid_Grenade_v1.2/03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_Assembly_Exploded.glb
  - Hybrid_Grenade_v1.2/03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_Assembly.3mf
  - Hybrid_Grenade_v1.2/03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_Assembly_Viewer.html
  - Hybrid_Grenade_v1.2/03_Internal_Barrel_And_Upper_Station/Custom_Internal_Barrel_And_Springs_Assembly.glb
  - Hybrid_Grenade_v1.2/Custom_Internal_Barrel_Assembly.glb
  - Hybrid_Grenade_v1.2/Custom_Internal_Barrel_And_Springs_Assembly.glb
  - Hybrid_Grenade_v1.2/Dual_Assembly_Inspection_Viewer.html
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import trimesh

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
ASY_DIR = os.path.join(V12_DIR, "All_Parts_Assembled_Coordinates")
SUBASSY_DIR = os.path.join(V12_DIR, "03_Internal_Barrel_And_Upper_Station")
ROD_DIR = os.path.join(V12_DIR, "04_Rod_Assembly_And_Locks")

BARREL_SPRINGS_PARTS = [
    {
        "id": 10,
        "filename": "10_Custom_Internal_Barrel_4Slot.stl",
        "name": "10 Custom Internal Barrel 4Slot",
        "title": "4-Slot Internal Barrel Chassis (10)",
        "desc": "Cylindrical internal barrel chassis with 4 vertical detent spring slots at 90° intervals.",
        "color_rgb": (55, 65, 75),       # Gunmetal Dark Slate
        "color_hex": "#37414B",
        "metallic": 0.35,
        "roughness": 0.45,
        "disp": np.array([0.0, 0.0, 0.0]),
    },
    {
        "id": 11,
        "filename": "11_Custom_Internal_Barrel_Cap.stl",
        "name": "11 Custom Internal Barrel Cap",
        "title": "Internal Barrel Retention Cap (11)",
        "desc": "Top retention washer cap retaining the detent springs axially in the barrel slots.",
        "color_rgb": (160, 170, 180),    # Steel / Nickel
        "color_hex": "#A0AAB4",
        "metallic": 0.55,
        "roughness": 0.35,
        "disp": np.array([0.0, 20.0, 0.0]),
    },
    {
        "id": 12,
        "filename": "12_Custom_Rod_Detent_Spring_01.stl",
        "name": "12 Custom Rod Detent Spring 01",
        "title": "Rod Detent Spring 01 (az 0°, Single-Headed)",
        "desc": "Axial detent flexure spring at 0° (X- axis) engaging the rod with a single detent nose at Y=57.41 mm.",
        "color_rgb": (249, 115, 22),     # Safety Orange
        "color_hex": "#F97316",
        "metallic": 0.20,
        "roughness": 0.40,
        "disp": np.array([-22.0, 0.0, 0.0]),
    },
    {
        "id": 13,
        "filename": "13_Custom_Rod_Detent_Spring_02.stl",
        "name": "13 Custom Rod Detent Spring 02",
        "title": "Rod Detent Spring 02 (az 90°, Single-Headed)",
        "desc": "Axial detent flexure spring at 90° (Z+ axis) engaging the rod with a single detent nose at Y=57.41 mm.",
        "color_rgb": (249, 115, 22),     # Safety Orange
        "color_hex": "#F97316",
        "metallic": 0.20,
        "roughness": 0.40,
        "disp": np.array([0.0, 0.0, 22.0]),
    },
    {
        "id": 14,
        "filename": "14_Custom_Rod_Detent_Spring_03.stl",
        "name": "14 Custom Rod Detent Spring 03",
        "title": "Rod Detent Spring 03 (az 180°, Single-Headed)",
        "desc": "Axial detent flexure spring at 180° (X+ axis) engaging the rod with a single detent nose at Y=57.41 mm.",
        "color_rgb": (249, 115, 22),     # Safety Orange
        "color_hex": "#F97316",
        "metallic": 0.20,
        "roughness": 0.40,
        "disp": np.array([22.0, 0.0, 0.0]),
    },
    {
        "id": 15,
        "filename": "15_Custom_Rod_Detent_Spring_04.stl",
        "name": "15 Custom Rod Detent Spring 04",
        "title": "Rod Detent Spring 04 (az 270°, Single-Headed)",
        "desc": "Axial detent flexure spring at 270° (Z- axis) engaging the rod with a single detent nose at Y=57.41 mm.",
        "color_rgb": (249, 115, 22),     # Safety Orange
        "color_hex": "#F97316",
        "metallic": 0.20,
        "roughness": 0.40,
        "disp": np.array([0.0, 0.0, -22.0]),
    },
]


def load_barrel_springs_parts():
    loaded = []
    for info in BARREL_SPRINGS_PARTS:
        path = os.path.join(ASY_DIR, info["filename"])
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing assembled source file: {path}")
        mesh = trimesh.load(path, force="mesh", process=True)
        loaded.append({
            **info,
            "mesh": mesh,
        })
    return loaded


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

    data_3mf = scene.export(file_type="3mf")
    with open(output_path, "wb") as f:
        f.write(data_3mf)

    # Enrich 3MF metadata
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
    """Export PBR GLB models for assembled and exploded sub-assembly."""
    # 1. Assembled GLB
    scene_asy = trimesh.Scene()
    for p in parts:
        m = p["mesh"].copy()
        r, g, b = p["color_rgb"]
        color_norm = [r / 255.0, g / 255.0, b / 255.0, 1.0]
        mat = trimesh.visual.material.PBRMaterial(
            baseColorFactor=color_norm,
            metallicFactor=float(p["metallic"]),
            roughnessFactor=float(p["roughness"]),
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
            metallicFactor=float(p["metallic"]),
            roughnessFactor=float(p["roughness"]),
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
            "title": p["title"],
            "filename": p["filename"],
            "desc": p["desc"],
            "color_rgb": p["color_rgb"],
            "color_hex": p["color_hex"],
            "volume_mm3": round(float(m.volume), 1),
            "extents_mm": [round(float(x), 2) for x in ext],
            "bounds_y": [round(float(bb[0][1]), 2), round(float(bb[1][1]), 2)],
            "disp": [round(float(d), 2) for d in p["disp"]],
        })

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Internal Barrel & Springs Assembly (6 Parts)</title>
  <style>
    :root {{
      --bg-dark: #090d16;
      --bg-card: rgba(15, 23, 42, 0.92);
      --border-color: rgba(255, 255, 255, 0.12);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.35);
      --danger: #f43f5e;
      --warning: #fbbf24;
      --success: #34d399;
      --magenta: #ec4899;
      --orange: #f97316;
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
      width: 440px;
      height: 100%;
      background: var(--bg-card);
      backdrop-filter: blur(18px);
      border-left: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      padding: 24px;
      gap: 16px;
      overflow-y: auto;
      z-index: 10;
      box-shadow: -8px 0 24px rgba(0,0,0,0.5);
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
      font-size: 0.84rem;
      color: var(--text-muted);
      line-height: 1.4;
    }}
    .control-card {{
      background: rgba(15, 23, 42, 0.65);
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
    .notice-card {{
      background: rgba(244, 63, 94, 0.1);
      border: 1px solid rgba(244, 63, 94, 0.35);
      border-radius: 10px;
      padding: 12px 14px;
      font-size: 0.8rem;
      color: #fecdd3;
      line-height: 1.45;
    }}
    .notice-title {{
      font-weight: 700;
      color: #fb7185;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .parts-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 360px;
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
      font-size: 0.74rem;
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
    .toggle-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.82rem;
    }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
  <div id="canvas-container">
    <div class="info-overlay">
      <div style="font-weight: 700; color: var(--accent); margin-bottom: 4px;">6-Part Internal Barrel & Springs Sub-Assembly</div>
      <div style="color: var(--text-muted); font-size: 0.78rem;">Left click + drag to rotate • Right click to pan • Scroll to zoom</div>
    </div>
    <div id="toolbar">
      <button id="btn-reset">Reset View</button>
      <button id="btn-transparent-barrel">Translucent Barrel</button>
      <button id="btn-wireframe">Wireframe</button>
      <button id="btn-autorotate">Auto Rotate</button>
    </div>
  </div>

  <div id="sidebar">
    <div>
      <h1>Internal Barrel & Springs <span class="badge">6 Parts</span></h1>
      <p class="subtitle" style="margin-top: 6px;">Chassis (10), Top Retention Cap (11), and 4 Rod Detent Springs (12, 13, 14, 15) in assembled coordinates.</p>
    </div>

    <div class="notice-card" style="border-left: 3px solid #22c55e;">
      <div class="notice-title" style="color: #22c55e;">✓ Equal Single-Headed Springs Configuration</div>
      All four rod detent springs (12, 13, 14, 15) are standardized to identical single-headed flexures (detent nose at Y=57.41 mm). Eliminates upper head extension and ensures full clearance with the solid rod assembly and cap.
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

    <div class="control-card">
      <div class="toggle-row">
        <span>Barrel Opacity</span>
        <span id="opacity-val" style="color: var(--accent);">100%</span>
      </div>
      <input type="range" id="slider-opacity" min="10" max="100" value="100">
    </div>

    <div style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">
      Assembly Components
    </div>

    <div class="parts-list" id="parts-list"></div>
  </div>

  <script>
    const PARTS_DATA = {json.dumps(parts_json)};
    const GLB_B64 = "{glb_b64}";

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x090d16);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(55, 60, 85);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 48, 0);

    // Studio Lighting
    const ambLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambLight);

    const dir1 = new THREE.DirectionalLight(0xffffff, 1.4);
    dir1.position.set(60, 100, 70);
    scene.add(dir1);

    const dir2 = new THREE.DirectionalLight(0x38bdf8, 0.6);
    dir2.position.set(-60, -20, -50);
    scene.add(dir2);

    const dir3 = new THREE.DirectionalLight(0xffeedd, 0.7);
    dir3.position.set(0, 80, -80);
    scene.add(dir3);

    // Grid Floor
    const grid = new THREE.GridHelper(120, 24, 0x334155, 0x1e293b);
    grid.position.y = 18;
    scene.add(grid);

    let assemblyGroup = new THREE.Group();
    scene.add(assemblyGroup);

    let meshesByName = {{}};
    let origPositions = {{}};
    let isBarrelTranslucent = false;

    // Load base64 GLB
    const loader = new THREE.GLTFLoader();
    const binaryStr = atob(GLB_B64);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) {{
      bytes[i] = binaryStr.charCodeAt(i);
    }}

    loader.parse(bytes.buffer, '', (gltf) => {{
      assemblyGroup.add(gltf.scene);
      gltf.scene.traverse((child) => {{
        if (child.isMesh) {{
          meshesByName[child.name] = child;
          origPositions[child.name] = child.position.clone();
          child.castShadow = true;
          child.receiveShadow = true;
        }}
      }});
      populateSidebar();
    }});

    function populateSidebar() {{
      const listEl = document.getElementById('parts-list');
      listEl.innerHTML = '';
      PARTS_DATA.forEach((p) => {{
        const item = document.createElement('div');
        item.className = 'part-item';
        item.dataset.name = p.name;
        item.innerHTML = `
          <div class="part-header">
            <div class="part-title-wrap">
              <div class="color-dot" style="background: ${{p.color_hex}};"></div>
              <div class="part-title">${{p.title}}</div>
            </div>
            <span class="badge" style="font-size: 0.7rem;">#${{p.id}}</span>
          </div>
          <div class="part-meta">
            <span>Vol: ${{p.volume_mm3.toLocaleString()}} mm³</span>
            <span>Y: [${{p.bounds_y[0]}}, ${{p.bounds_y[1]}}] mm</span>
          </div>
          <div class="part-desc">${{p.desc}}</div>
        `;
        item.addEventListener('click', () => {{
          document.querySelectorAll('.part-item').forEach(el => el.classList.remove('active'));
          item.classList.add('active');
          focusPart(p.name);
        }});
        listEl.appendChild(item);
      }});
    }}

    function focusPart(name) {{
      const mesh = meshesByName[name];
      if (!mesh) return;
      const box = new THREE.Box3().setFromObject(mesh);
      const center = new THREE.Vector3();
      box.getCenter(center);
      controls.target.copy(center);
    }}

    // Explode logic
    const sliderExpl = document.getElementById('slider-exploded');
    const explVal = document.getElementById('expl-val');
    sliderExpl.addEventListener('input', (e) => {{
      const t = parseFloat(e.target.value) / 100.0;
      explVal.textContent = Math.round(t * 100) + '%';
      applyExplosion(t);
    }});

    document.getElementById('btn-exp-0').addEventListener('click', () => setExplode(0));
    document.getElementById('btn-exp-50').addEventListener('click', () => setExplode(50));
    document.getElementById('btn-exp-100').addEventListener('click', () => setExplode(100));

    function setExplode(val) {{
      sliderExpl.value = val;
      explVal.textContent = val + '%';
      applyExplosion(val / 100.0);
    }}

    function applyExplosion(factor) {{
      PARTS_DATA.forEach((p) => {{
        const mesh = meshesByName[p.name];
        if (mesh && origPositions[p.name]) {{
          const disp = p.disp;
          mesh.position.set(
            origPositions[p.name].x + disp[0] * factor,
            origPositions[p.name].y + disp[1] * factor,
            origPositions[p.name].z + disp[2] * factor
          );
        }}
      }});
    }}

    // Translucent Barrel
    const sliderOpacity = document.getElementById('slider-opacity');
    const opacityVal = document.getElementById('opacity-val');
    sliderOpacity.addEventListener('input', (e) => {{
      const val = parseFloat(e.target.value);
      opacityVal.textContent = Math.round(val) + '%';
      setBarrelOpacity(val / 100.0);
    }});

    function setBarrelOpacity(alpha) {{
      const barrelMesh = meshesByName['10 Custom Internal Barrel 4Slot'];
      if (barrelMesh && barrelMesh.material) {{
        barrelMesh.material.transparent = alpha < 0.99;
        barrelMesh.material.opacity = alpha;
        barrelMesh.material.needsUpdate = true;
      }}
    }}

    document.getElementById('btn-transparent-barrel').addEventListener('click', () => {{
      isBarrelTranslucent = !isBarrelTranslucent;
      const targetAlpha = isBarrelTranslucent ? 0.35 : 1.0;
      sliderOpacity.value = Math.round(targetAlpha * 100);
      opacityVal.textContent = sliderOpacity.value + '%';
      setBarrelOpacity(targetAlpha);
    }});

    // Toolbar buttons
    document.getElementById('btn-reset').addEventListener('click', () => {{
      camera.position.set(55, 60, 85);
      controls.target.set(0, 48, 0);
      setExplode(0);
    }});

    let wireframe = false;
    document.getElementById('btn-wireframe').addEventListener('click', () => {{
      wireframe = !wireframe;
      Object.values(meshesByName).forEach((m) => {{
        if (m.material) m.material.wireframe = wireframe;
      }});
    }});

    let autoRotate = false;
    document.getElementById('btn-autorotate').addEventListener('click', () => {{
      autoRotate = !autoRotate;
      controls.autoRotate = autoRotate;
      controls.autoRotateSpeed = 2.5;
    }});

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


def generate_dual_assembly_viewer(rod_glb_path, barrel_glb_path, output_html_path):
    """Build a side-by-side and overlaid interactive dual-assembly viewer."""
    with open(rod_glb_path, "rb") as f:
        rod_b64 = base64.b64encode(f.read()).decode("ascii")
    with open(barrel_glb_path, "rb") as f:
        barrel_b64 = base64.b64encode(f.read()).decode("ascii")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dual Assembly Inspection: Rod vs Barrel & Springs</title>
  <style>
    :root {{
      --bg-dark: #090d16;
      --bg-card: rgba(15, 23, 42, 0.94);
      --border-color: rgba(255, 255, 255, 0.12);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.35);
      --danger: #f43f5e;
      --warning: #fbbf24;
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
      width: 460px;
      height: 100%;
      background: var(--bg-card);
      backdrop-filter: blur(20px);
      border-left: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      padding: 24px;
      gap: 16px;
      overflow-y: auto;
      z-index: 10;
      box-shadow: -8px 0 28px rgba(0,0,0,0.5);
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
      font-size: 0.84rem;
      color: var(--text-muted);
      line-height: 1.4;
    }}
    .control-card {{
      background: rgba(15, 23, 42, 0.7);
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
      grid-template-columns: repeat(2, 1fr);
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
    .danger-box {{
      background: rgba(244, 63, 94, 0.12);
      border: 1px solid rgba(244, 63, 94, 0.35);
      border-radius: 10px;
      padding: 14px;
      font-size: 0.82rem;
      color: #fecdd3;
      line-height: 1.5;
    }}
    .danger-box h3 {{
      color: #fb7185;
      font-size: 0.9rem;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .toggle-pill {{
      display: flex;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 3px;
      gap: 4px;
    }}
    .toggle-pill button {{
      flex: 1;
      background: transparent;
      border: none;
      padding: 6px;
      font-size: 0.78rem;
    }}
    .toggle-pill button.active {{
      background: var(--accent);
      color: #090d16;
      font-weight: 700;
    }}
    #toolbar {{
      position: absolute;
      bottom: 24px;
      left: 24px;
      display: flex;
      gap: 10px;
      z-index: 5;
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(12px);
      padding: 8px 12px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
    }}
    .info-overlay {{
      position: absolute;
      top: 24px;
      left: 24px;
      background: rgba(15, 23, 42, 0.8);
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
      <div style="font-weight: 700; color: var(--accent); margin-bottom: 4px;">Dual Assembly Visualizer</div>
      <div style="color: var(--text-muted); font-size: 0.78rem;">Custom Rod Assembly (04) & Internal Barrel Sub-Assembly (03)</div>
    </div>
    <div id="toolbar">
      <button id="btn-reset">Reset View</button>
      <button id="btn-toggle-clip">Toggle XZ Clipping Plane</button>
      <button id="btn-autorotate">Auto Rotate</button>
    </div>
  </div>

  <div id="sidebar">
    <div>
      <h1>Assembly Comparison <span class="badge">Dual Systems</span></h1>
      <p class="subtitle" style="margin-top: 6px;">Compare <code>Custom_Rod_Assembly.glb</code> with <code>Custom_Internal_Barrel_Assembly.glb</code> in real-time 3D.</p>
    </div>

    <div class="danger-box" style="border-color: rgba(34, 197, 94, 0.4); background: rgba(34, 197, 94, 0.08);">
      <h3 style="color: #22c55e;">✓ Resolved with Equal Single-Headed Springs:</h3>
      <ul style="padding-left: 18px; display: flex; flex-direction: column; gap: 6px;">
        <li><strong>Standardized Single Heads:</strong> All 4 springs (12, 13, 14, 15) terminate cleanly at Y=62.92 mm with single detent noses at Y=57.41 mm.</li>
        <li><strong>Zero Collar Interference:</strong> Full clearance maintained against Custom Rod Middle solid collar at Y &gt; 61 mm.</li>
        <li><strong>Unrestricted Insertion:</strong> Rod inserts smoothly top-down into barrel without obstruction.</li>
      </ul>
    </div>

    <div class="control-card">
      <div class="slider-label">View Layout</div>
      <div class="toggle-pill">
        <button id="btn-mode-overlaid" class="active">Overlaid (Mated)</button>
        <button id="btn-mode-sidebyside">Side-by-Side</button>
      </div>
    </div>

    <div class="control-card">
      <div class="slider-row">
        <div class="slider-label">
          <span>Rod Stroke Travel (Y Offset)</span>
          <span id="stroke-val" style="color: var(--accent);">0.0 mm</span>
        </div>
        <input type="range" id="slider-stroke" min="-15" max="15" step="0.5" value="0">
      </div>
      <div class="btn-group">
        <button id="btn-stroke-reset">Center (Neutral)</button>
        <button id="btn-stroke-top">Top (+10mm)</button>
      </div>
    </div>

    <div class="control-card">
      <div class="slider-row">
        <div class="slider-label">
          <span>Internal Barrel Chassis Opacity</span>
          <span id="trans-val" style="color: var(--accent);">35%</span>
        </div>
        <input type="range" id="slider-trans" min="0" max="100" value="35">
      </div>
      <div class="btn-group">
        <button id="btn-barrel-hide">Hide Barrel</button>
        <button id="btn-barrel-show">Solid Barrel</button>
      </div>
    </div>

    <div class="control-card">
      <div class="slider-label">Assembly Visibility</div>
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <label style="font-size: 0.82rem; display: flex; align-items: center; gap: 8px; cursor: pointer;">
          <input type="checkbox" id="chk-rod" checked> Show Custom Rod Assembly
        </label>
        <label style="font-size: 0.82rem; display: flex; align-items: center; gap: 8px; cursor: pointer;">
          <input type="checkbox" id="chk-barrel" checked> Show Internal Barrel & Springs
        </label>
      </div>
    </div>
  </div>

  <script>
    const ROD_B64 = "{rod_b64}";
    const BARREL_B64 = "{barrel_b64}";

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x090d16);

    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(65, 75, 95);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    renderer.localClippingEnabled = true;
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 52, 0);

    const ambLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambLight);

    const dir1 = new THREE.DirectionalLight(0xffffff, 1.4);
    dir1.position.set(60, 100, 70);
    scene.add(dir1);

    const dir2 = new THREE.DirectionalLight(0x38bdf8, 0.6);
    dir2.position.set(-60, -20, -50);
    scene.add(dir2);

    const grid = new THREE.GridHelper(140, 28, 0x334155, 0x1e293b);
    grid.position.y = 15;
    scene.add(grid);

    const rodGroup = new THREE.Group();
    const barrelGroup = new THREE.Group();
    scene.add(rodGroup);
    scene.add(barrelGroup);

    let barrelChassisMesh = null;
    let clipPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 0);
    let isClipping = false;

    const loader = new THREE.GLTFLoader();

    function loadGLB(b64, targetGroup, isBarrel) {{
      const binStr = atob(b64);
      const u8 = new Uint8Array(binStr.length);
      for (let i = 0; i < binStr.length; i++) u8[i] = binStr.charCodeAt(i);
      loader.parse(u8.buffer, '', (gltf) => {{
        targetGroup.add(gltf.scene);
        if (isBarrel) {{
          gltf.scene.traverse((c) => {{
            if (c.isMesh && c.name.includes('10')) {{
              barrelChassisMesh = c;
              if (c.material) {{
                c.material = c.material.clone();
                c.material.transparent = true;
                c.material.opacity = 0.35;
              }}
            }}
          }});
        }}
      }});
    }}

    loadGLB(ROD_B64, rodGroup, false);
    loadGLB(BARREL_B64, barrelGroup, true);

    // Layout Modes
    let currentMode = 'overlaid';
    document.getElementById('btn-mode-overlaid').addEventListener('click', () => setMode('overlaid'));
    document.getElementById('btn-mode-sidebyside').addEventListener('click', () => setMode('sidebyside'));

    function setMode(mode) {{
      currentMode = mode;
      document.getElementById('btn-mode-overlaid').classList.toggle('active', mode === 'overlaid');
      document.getElementById('btn-mode-sidebyside').classList.toggle('active', mode === 'sidebyside');
      if (mode === 'overlaid') {{
        rodGroup.position.x = 0;
        barrelGroup.position.x = 0;
        controls.target.set(0, 52, 0);
      }} else {{
        rodGroup.position.x = 28;
        barrelGroup.position.x = -28;
        controls.target.set(0, 52, 0);
      }}
    }}

    // Stroke Slider
    const sliderStroke = document.getElementById('slider-stroke');
    const strokeVal = document.getElementById('stroke-val');
    sliderStroke.addEventListener('input', (e) => {{
      const dy = parseFloat(e.target.value);
      strokeVal.textContent = (dy >= 0 ? '+' : '') + dy.toFixed(1) + ' mm';
      rodGroup.position.y = dy;
    }});

    document.getElementById('btn-stroke-reset').addEventListener('click', () => {{
      sliderStroke.value = 0;
      strokeVal.textContent = '0.0 mm';
      rodGroup.position.y = 0;
    }});

    document.getElementById('btn-stroke-top').addEventListener('click', () => {{
      sliderStroke.value = 10;
      strokeVal.textContent = '+10.0 mm';
      rodGroup.position.y = 10;
    }});

    // Barrel Opacity
    const sliderTrans = document.getElementById('slider-trans');
    const transVal = document.getElementById('trans-val');
    sliderTrans.addEventListener('input', (e) => {{
      const val = parseFloat(e.target.value);
      transVal.textContent = Math.round(val) + '%';
      if (barrelChassisMesh && barrelChassisMesh.material) {{
        barrelChassisMesh.material.transparent = val < 99;
        barrelChassisMesh.material.opacity = val / 100.0;
      }}
    }});

    document.getElementById('btn-barrel-hide').addEventListener('click', () => {{
      sliderTrans.value = 0;
      transVal.textContent = '0%';
      if (barrelChassisMesh && barrelChassisMesh.material) {{
        barrelChassisMesh.material.transparent = true;
        barrelChassisMesh.material.opacity = 0;
      }}
    }});

    document.getElementById('btn-barrel-show').addEventListener('click', () => {{
      sliderTrans.value = 100;
      transVal.textContent = '100%';
      if (barrelChassisMesh && barrelChassisMesh.material) {{
        barrelChassisMesh.material.transparent = false;
        barrelChassisMesh.material.opacity = 1.0;
      }}
    }});

    // Visibility Checkboxes
    document.getElementById('chk-rod').addEventListener('change', (e) => {{
      rodGroup.visible = e.target.checked;
    }});
    document.getElementById('chk-barrel').addEventListener('change', (e) => {{
      barrelGroup.visible = e.target.checked;
    }});

    // Reset View
    document.getElementById('btn-reset').addEventListener('click', () => {{
      camera.position.set(65, 75, 95);
      controls.target.set(0, 52, 0);
      sliderStroke.value = 0;
      strokeVal.textContent = '0.0 mm';
      rodGroup.position.y = 0;
    }});

    // Clipping plane
    document.getElementById('btn-toggle-clip').addEventListener('click', () => {{
      isClipping = !isClipping;
      renderer.clippingPlanes = isClipping ? [clipPlane] : [];
    }});

    let autoRotate = false;
    document.getElementById('btn-autorotate').addEventListener('click', () => {{
      autoRotate = !autoRotate;
      controls.autoRotate = autoRotate;
      controls.autoRotateSpeed = 2.5;
    }});

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
    print("=" * 80)
    print("BUILDING INTERNAL BARREL & SPRINGS SUB-ASSEMBLY (6 PARTS)")
    print("=" * 80)

    print("\n[1/5] Loading 6 components from assembled coordinate space...")
    parts = load_barrel_springs_parts()
    for p in parts:
        m = p["mesh"]
        bb = m.bounds
        print(f"  - [{p['id']:02d}] {p['title']}")
        print(f"       File: {p['filename']} | Vol: {m.volume:9.1f} mm3")
        print(f"       Bounds Y: [{bb[0][1]:.2f}, {bb[1][1]:.2f}] mm | X: [{bb[0][0]:.2f}, {bb[1][0]:.2f}] | Z: [{bb[0][2]:.2f}, {bb[1][2]:.2f}]")

    os.makedirs(SUBASSY_DIR, exist_ok=True)
    out_glb_assy = os.path.join(SUBASSY_DIR, "Custom_Internal_Barrel_Assembly.glb")
    out_glb_exp = os.path.join(SUBASSY_DIR, "Custom_Internal_Barrel_Assembly_Exploded.glb")
    out_3mf = os.path.join(SUBASSY_DIR, "Custom_Internal_Barrel_Assembly.3mf")
    out_html = os.path.join(SUBASSY_DIR, "Custom_Internal_Barrel_Assembly_Viewer.html")

    # Also build the descriptive named GLB in 03 subfolder
    out_glb_desc = os.path.join(SUBASSY_DIR, "Custom_Internal_Barrel_And_Springs_Assembly.glb")

    print("\n[2/5] Exporting Assembled and Exploded GLBs...")
    glb_bytes = export_glb_models(parts, out_glb_assy, out_glb_exp)
    shutil.copy2(out_glb_assy, out_glb_desc)
    # Also place at V12 root
    shutil.copy2(out_glb_assy, os.path.join(V12_DIR, "Custom_Internal_Barrel_Assembly.glb"))
    shutil.copy2(out_glb_desc, os.path.join(V12_DIR, "Custom_Internal_Barrel_And_Springs_Assembly.glb"))
    print(f"  -> Assembled GLB: {out_glb_assy} ({len(glb_bytes):,} bytes)")
    print(f"  -> Exploded GLB:  {out_glb_exp}")

    print("\n[3/5] Exporting Multi-Body 3MF Project...")
    export_3mf_project(parts, out_3mf)
    print(f"  -> 3MF Project:   {out_3mf}")

    print("\n[4/5] Generating Standalone 3D Assembly HTML Viewer...")
    generate_interactive_viewer(parts, glb_bytes, out_html)
    print(f"  -> HTML Viewer:   {out_html}")

    print("\n[5/5] Generating Dual-Assembly Inspection HTML Viewer...")
    rod_glb = os.path.join(ROD_DIR, "Custom_Rod_Assembly.glb")
    dual_html = os.path.join(V12_DIR, "Dual_Assembly_Inspection_Viewer.html")
    if os.path.exists(rod_glb):
        generate_dual_assembly_viewer(rod_glb, out_glb_assy, dual_html)
        print(f"  -> Dual Viewer:   {dual_html}")
    else:
        print(f"  [WARN] Custom_Rod_Assembly.glb not found at {rod_glb}")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL BARREL & SPRINGS SUB-ASSEMBLY ARTIFACTS CREATED")
    print("=" * 80)


if __name__ == "__main__":
    main()
