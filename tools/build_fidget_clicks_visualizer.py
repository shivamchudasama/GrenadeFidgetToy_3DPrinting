"""Build Interactive Fidget Clicks Visualizer Studio for Hybrid Grenade v1.2.

Generates:
  Hybrid_Grenade_v1.2/Interactive_Fidget_Clicks_Visualizer.html

A standalone, high-performance Three.js WebGL application that interactively simulates,
scrubs, animates, visualizes, and synthesizes procedural audio for all fidget clicks
and mechanisms across the entire 34-part assembly with 100% exact CAD geometry alignment.
"""
from __future__ import annotations

import json
import os
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)
V12_DIR = os.path.join(ROOT_DIR, "Hybrid_Grenade_v1.2")
OUTPUT_HTML = os.path.join(V12_DIR, "Interactive_Fidget_Clicks_Visualizer.html")

# Part specification metadata for the 34-part BOM
PARTS_DATA = [
    # 01 - Base & Bottom Shell
    {"id": 1, "name": "01_04_Bottom_Shell_01", "file": "01_04_Bottom_Shell_01.stl", "subassembly": "01_Base_And_Bottom_Shell", "color": "#7ab566", "material": "PLA (Olive Drab)", "disp": [0.0, -52.0, 0.0]},
    {"id": 2, "name": "02_05_Bottom_Shell_02", "file": "02_05_Bottom_Shell_02.stl", "subassembly": "01_Base_And_Bottom_Shell", "color": "#7ab566", "material": "PLA (Olive Drab)", "disp": [0.0, -40.0, 0.0]},
    {"id": 3, "name": "03_06_Bottom_Shell_03", "file": "03_06_Bottom_Shell_03.stl", "subassembly": "01_Base_And_Bottom_Shell", "color": "#7ab566", "material": "PLA (Olive Drab)", "disp": [0.0, -28.0, 0.0]},
    {"id": 4, "name": "04_01_Bottom_Lock_Shell", "file": "04_01_Bottom_Lock_Shell.stl", "subassembly": "01_Base_And_Bottom_Shell", "color": "#414b55", "material": "PLA/PETG (Gunmetal)", "disp": [0.0, -44.0, 0.0]},
    {"id": 5, "name": "05_02_Bottom_Spring", "file": "05_02_Bottom_Spring.stl", "subassembly": "01_Base_And_Bottom_Shell", "color": "#ff6e1e", "material": "PETG (Safety Orange)", "disp": [0.0, -32.0, 0.0]},
    {"id": 6, "name": "06_03_Bottom_Shell_Spacer", "file": "06_03_Bottom_Shell_Spacer.stl", "subassembly": "01_Base_And_Bottom_Shell", "color": "#505a64", "material": "PLA (Gunmetal)", "disp": [0.0, -16.0, 0.0]},

    # 02 - Waist Mechanism
    {"id": 7, "name": "07_32_Mid_Shell_P02_Ratchet", "file": "07_32_Mid_Shell_P02_Ratchet.stl", "subassembly": "02_Waist_Mechanism", "color": "#8cbe73", "material": "PLA (Olive Accent)", "disp": [36.0, 0.0, 0.0]},
    {"id": 8, "name": "08_33_Mid_Shell_P01_Outer", "file": "08_33_Mid_Shell_P01_Outer.stl", "subassembly": "02_Waist_Mechanism", "color": "#7ab566", "material": "PLA (Olive Drab)", "disp": [-36.0, 0.0, 0.0]},
    {"id": 9, "name": "09_Custom_Mid_Shell_Spring_33", "file": "09_Custom_Mid_Shell_Spring_33.stl", "subassembly": "02_Waist_Mechanism", "color": "#ff7d28", "material": "PETG (Safety Orange)", "disp": [0.0, 0.0, 34.0]},

    # 03 - Internal Barrel & Upper Station
    {"id": 10, "name": "10_Custom_Internal_Barrel_4Slot", "file": "10_Custom_Internal_Barrel_4Slot.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#37414b", "material": "PLA+/PETG (Gunmetal)", "disp": [0.0, 0.0, 0.0]},
    {"id": 11, "name": "11_Custom_Internal_Barrel_Cap", "file": "11_Custom_Internal_Barrel_Cap.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#46505a", "material": "PLA (Gunmetal)", "disp": [0.0, 20.0, 0.0]},
    {"id": 12, "name": "12_Custom_Rod_Detent_Spring_01", "file": "12_Custom_Rod_Detent_Spring_01.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#ff822d", "material": "PETG (Safety Orange)", "disp": [-44.0, 0.0, 24.0]},
    {"id": 13, "name": "13_Custom_Rod_Detent_Spring_02", "file": "13_Custom_Rod_Detent_Spring_02.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#00e5ff", "material": "PETG (Electric Cyan Dual-Head)", "disp": [44.0, 0.0, 24.0]},
    {"id": 14, "name": "14_Custom_Rod_Detent_Spring_03", "file": "14_Custom_Rod_Detent_Spring_03.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#ff822d", "material": "PETG (Safety Orange)", "disp": [-44.0, 0.0, -24.0]},
    {"id": 15, "name": "15_Custom_Rod_Detent_Spring_04", "file": "15_Custom_Rod_Detent_Spring_04.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#00e5ff", "material": "PETG (Electric Cyan Dual-Head)", "disp": [44.0, 0.0, -24.0]},
    {"id": 18, "name": "18_27_Upper_Shell_Top", "file": "18_27_Upper_Shell_Top.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#7ab566", "material": "PLA (Olive Drab)", "disp": [0.0, 56.0, 0.0]},
    {"id": 19, "name": "19_28_Upper_Shell_Gear", "file": "19_28_Upper_Shell_Gear.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#c3cdd7", "material": "Silk PLA (Silver Metallic)", "disp": [0.0, 32.0, 0.0]},
    {"id": 20, "name": "20_29_Upper_Shell_Lock_Ring", "file": "20_29_Upper_Shell_Lock_Ring.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#8cbe73", "material": "PLA (Olive Accent)", "disp": [0.0, 24.0, 0.0]},
    {"id": 21, "name": "21_30_Upper_Shell_Rotating_Spring", "file": "21_30_Upper_Shell_Rotating_Spring.stl", "subassembly": "03_Internal_Barrel_And_Upper_Station", "color": "#ff6e1e", "material": "PETG (Safety Orange)", "disp": [0.0, 44.0, 0.0]},

    # 04 - Rod Assembly & Locks
    {"id": 22, "name": "22_Custom_Rod_Right", "file": "22_Custom_Rod_Right.stl", "subassembly": "04_Rod_Assembly_And_Locks", "color": "#4b555f", "material": "PLA+/PETG (Gunmetal)", "disp": [24.0, 68.0, 0.0]},
    {"id": 23, "name": "23_Custom_Rod_Middle", "file": "23_Custom_Rod_Middle.stl", "subassembly": "04_Rod_Assembly_And_Locks", "color": "#323a44", "material": "PLA+/PETG (Charcoal Black)", "disp": [0.0, 68.0, 0.0]},
    {"id": 24, "name": "24_Custom_Rod_Left", "file": "24_Custom_Rod_Left.stl", "subassembly": "04_Rod_Assembly_And_Locks", "color": "#4b555f", "material": "PLA+/PETG (Gunmetal)", "disp": [-24.0, 68.0, 0.0]},
    {"id": 25, "name": "25_Custom_Rod_Lock_Upper_06", "file": "25_Custom_Rod_Lock_Upper_06.stl", "subassembly": "04_Rod_Assembly_And_Locks", "color": "#e63232", "material": "PETG/PLA+ (Crimson Red Key)", "disp": [0.0, 68.0, 22.0]},
    {"id": 26, "name": "26_Custom_Rod_Lock_Lower_07", "file": "26_Custom_Rod_Lock_Lower_07.stl", "subassembly": "04_Rod_Assembly_And_Locks", "color": "#e63232", "material": "PETG/PLA+ (Crimson Red Key)", "disp": [0.0, 68.0, 22.0]},
    {"id": 27, "name": "27_Spinner_Lever_08_Rod_Lock", "file": "27_Spinner_Lever_08_Rod_Lock.stl", "subassembly": "04_Rod_Assembly_And_Locks", "color": "#3c4650", "material": "PLA+/PETG (Retainer Disc)", "disp": [0.0, 50.0, 0.0]},

    # 05 - Folding Head & Spinner
    {"id": 28, "name": "28_09_Rod_Spring_Hinge", "file": "28_09_Rod_Spring_Hinge.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#ff6e1e", "material": "PETG (Safety Orange)", "disp": [0.0, 102.0, 0.0]},
    {"id": 29, "name": "29_Custom_Handle_Left", "file": "29_Custom_Handle_Left.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#7ab566", "material": "PLA (Olive Drab)", "disp": [-32.0, 114.0, 0.0]},
    {"id": 30, "name": "30_Custom_Handle_Right", "file": "30_Custom_Handle_Right.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#7ab566", "material": "PLA (Olive Drab)", "disp": [32.0, 114.0, 0.0]},
    {"id": 31, "name": "31_Custom_Ring_Spinner", "file": "31_Custom_Ring_Spinner.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#ebb941", "material": "Silk PLA (Gold Gyro Ring)", "disp": [0.0, 114.0, -42.0]},
    {"id": 32, "name": "32_Spinner_Lever_05_Gear", "file": "32_Spinner_Lever_05_Gear.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#c8d2dc", "material": "Silk PLA (Silver Chrome Gear)", "disp": [0.0, 114.0, -26.0]},
    {"id": 33, "name": "33_Spinner_Lever_04_Spring", "file": "33_Spinner_Lever_04_Spring.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#ff7d28", "material": "PETG (Safety Orange)", "disp": [0.0, 114.0, -12.0]},
    {"id": 34, "name": "34_Custom_16_Handle_Lock_Neck", "file": "34_Custom_16_Handle_Lock_Neck.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#e63232", "material": "PETG/PLA+ (Crimson Pin)", "disp": [44.0, 114.0, -14.0]},
    {"id": 35, "name": "35_Custom_16_Handle_Lock_Pod", "file": "35_Custom_16_Handle_Lock_Pod.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#e63232", "material": "PETG/PLA+ (Crimson Pin)", "disp": [44.0, 114.0, -28.0]},
    {"id": 36, "name": "36_15_Handle_Rotating_Lock_D_Pin", "file": "36_15_Handle_Rotating_Lock_D_Pin.stl", "subassembly": "05_Folding_Head_And_Spinner", "color": "#e63232", "material": "PETG/PLA+ (Crimson D-Pin)", "disp": [-44.0, 114.0, 0.0]},
]

SHELL_VARIANTS = [
    {"id": "01_AeroFlow", "name": "01. AeroFlow (Active Production)", "desc": "16 swept aerodynamic ergonomic ribs", "file": "3D_Print_Custom_Hybrid_Grenade_01_AeroFlow_Assembled.glb", "arch": "1-Piece Monolithic Solid", "maxDia": "41.68 mm"},
    {"id": "Baseline", "name": "Baseline Tactile Ribs", "desc": "Original standard 2-piece ribbed waist shell", "file": "3D_Print_Custom_Hybrid_Grenade_Assembled.glb", "arch": "2-Piece (Outer + Ratchet Ring)", "maxDia": "41.60 mm"},
    {"id": "02_Vector_Chevron", "name": "02. Vector Chevron", "desc": "Sculpted continuous interlocking chevrons", "file": "3D_Print_Custom_Hybrid_Grenade_02_Vector_Chevron_Assembled.glb", "arch": "1-Piece Monolithic Solid", "maxDia": "41.52 mm"},
    {"id": "03_Orbit", "name": "03. Orbit Pods", "desc": "Staggered raised traction pods & bands", "file": "3D_Print_Custom_Hybrid_Grenade_03_Orbit_Assembled.glb", "arch": "1-Piece Monolithic Solid", "maxDia": "41.55 mm"},
    {"id": "04_Ergo_Scoops", "name": "04. Ergo Scoops", "desc": "Grip rails with multi-start thread flutes", "file": "3D_Print_Custom_Hybrid_Grenade_04_Ergo_Scoops_Assembled.glb", "arch": "1-Piece Monolithic Solid", "maxDia": "41.84 mm"},
    {"id": "05_Contour_Twist", "name": "05. Contour Twist", "desc": "Deep twisted torque flutes (Dual-Color)", "file": "3D_Print_Custom_Hybrid_Grenade_05_Contour_Twist_Assembled.glb", "arch": "2-Piece Dual-Color (Outer + Core)", "maxDia": "43.00 mm"},
    {"id": "06_Hex_Tactical", "name": "06. Hex Tactical Solid", "desc": "Machined hexagonal honeycomb knurled grip", "file": "3D_Print_Custom_Hybrid_Grenade_06_Hex_Tactical_Assembled.glb", "arch": "1-Piece Monolithic Solid", "maxDia": "42.12 mm"},
    {"id": "07_Classic_Solid_Tactical", "name": "07. Classic Solid Tactical", "desc": "Monolithic solid version of original ribs", "file": "3D_Print_Custom_Hybrid_Grenade_07_Classic_Solid_Tactical_Assembled.glb", "arch": "1-Piece Monolithic Solid", "maxDia": "41.95 mm"},
]

DETENT_SPECS = {
    "axial": {
        "title": "Axial Rod Detent (Linear Plunger)",
        "pitch_mm": 3.17733,
        "flank_deg": 40.63,
        "peak_force_N": 23.91,
        "held_force_N": 3.14,
        "ratio": "7.62x Snap-Action",
        "spring_count": "4 Springs (2 Single + 2 Dual-Headed)",
        "synchronous_heads": 6,
        "max_stroke_mm": 24.0,
        "stroke_clicks": 7.55,
    },
    "waist": {
        "title": "33-Click Rotary Waist Detent",
        "pitch_deg": 10.909,
        "clicks_per_rev": 33,
        "lobes": 33,
        "spring_arms": 3,
        "symmetry": "3-Fold (30° / 150° / 270°)",
        "swept_volume_mm3": "1.33 to 10.18 mm³",
    },
    "hinge": {
        "title": "4-Position Folding Handle Hinge",
        "positions_deg": [0, 30, 60, 90],
        "labels": ["0° Folded Down", "30° Low Cant", "60° High Cant", "90° Tactical Deployed"],
        "d_pin_notches": 12,
        "notch_pitch_deg": 30.0,
        "swept_volume_mm3": "9.44 to 12.29 mm³",
    },
    "rim_gear": {
        "title": "20-Tooth Knurled Rim Gear",
        "teeth": 20,
        "pitch_deg": 18.0,
        "exposed_arc": "249° (>69% perimeter)",
        "swept_volume_mm3": "0.00 to 4.20 mm³",
    },
    "ring_spinner": {
        "title": "High-Speed Center Gyro Spinner",
        "diameter_mm": 22.10,
        "housing_bore_mm": 22.60,
        "clearance_mm": 0.193,
        "motion": "360° Free Inertia Gyro Spin",
    },
}

def generate_html() -> str:
    parts_json = json.dumps(PARTS_DATA)
    variants_json = json.dumps(SHELL_VARIANTS)
    detent_json = json.dumps(DETENT_SPECS)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hybrid Grenade v1.2 — Interactive Fidget Clicks & Kinematics Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070a13;
      --panel-bg: rgba(13, 19, 32, 0.88);
      --panel-bg-subtle: rgba(18, 26, 44, 0.65);
      --panel-border: rgba(255, 255, 255, 0.12);
      --panel-border-bright: rgba(255, 255, 255, 0.22);
      --accent-cyan: #00e5ff;
      --accent-cyan-glow: rgba(0, 229, 255, 0.35);
      --accent-orange: #ff7b25;
      --accent-orange-glow: rgba(255, 123, 37, 0.35);
      --accent-green: #10b981;
      --accent-green-glow: rgba(16, 185, 129, 0.35);
      --accent-purple: #a855f7;
      --accent-purple-glow: rgba(168, 85, 247, 0.35);
      --accent-gold: #ffc107;
      --accent-gold-glow: rgba(255, 193, 7, 0.35);
      --accent-red: #ef4444;
      --text-bright: #ffffff;
      --text-main: #e2e8f0;
      --text-muted: #94a3b8;
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

    /* Glassmorphism Panel Base */
    .glass-panel {{
      position: absolute;
      background: var(--panel-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-lg);
      padding: 16px 20px;
      box-shadow: 0 16px 48px rgba(0, 0, 0, 0.65);
      z-index: 10;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: auto;
    }}

    /* Top Header Bar */
    #top-bar {{
      top: 16px;
      left: 20px;
      right: 20px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .brand-badge {{
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
      color: #000;
      font-family: 'Outfit', sans-serif;
      font-weight: 800;
      font-size: 11px;
      padding: 5px 10px;
      border-radius: 6px;
      letter-spacing: 1px;
      text-transform: uppercase;
      box-shadow: 0 0 16px var(--accent-cyan-glow);
    }}

    .brand-titles h1 {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-bright);
      letter-spacing: -0.2px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .pulse-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-cyan);
      box-shadow: 0 0 10px var(--accent-cyan);
      display: inline-block;
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.3; transform: scale(0.85); }}
    }}

    .brand-titles p {{
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 1px;
    }}

    .header-badges {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .h-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      padding: 4px 9px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 5px;
    }}

    .h-badge.cyan {{ color: var(--accent-cyan); border-color: rgba(0, 229, 255, 0.3); background: rgba(0, 229, 255, 0.08); }}
    .h-badge.orange {{ color: var(--accent-orange); border-color: rgba(255, 123, 37, 0.3); background: rgba(255, 123, 37, 0.08); }}
    .h-badge.green {{ color: var(--accent-green); border-color: rgba(16, 185, 129, 0.3); background: rgba(16, 185, 129, 0.08); }}
    .h-badge.gold {{ color: var(--accent-gold); border-color: rgba(255, 193, 7, 0.3); background: rgba(255, 193, 7, 0.08); }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .btn {{
      background: var(--panel-bg-subtle);
      border: 1px solid var(--panel-border);
      color: var(--text-bright);
      font-family: 'Outfit', sans-serif;
      font-weight: 600;
      font-size: 0.8rem;
      padding: 7px 14px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}

    .btn:hover {{
      background: rgba(255, 255, 255, 0.12);
      border-color: var(--panel-border-bright);
      transform: translateY(-1px);
    }}

    .btn:active {{
      transform: translateY(1px);
    }}

    .btn-primary {{
      background: linear-gradient(135deg, rgba(0, 229, 255, 0.25), rgba(168, 85, 247, 0.25));
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
      box-shadow: 0 0 14px var(--accent-cyan-glow);
    }}

    .btn-primary:hover {{
      background: linear-gradient(135deg, rgba(0, 229, 255, 0.4), rgba(168, 85, 247, 0.4));
      color: #fff;
    }}

    .btn-active {{
      background: var(--accent-cyan);
      color: #000;
      border-color: var(--accent-cyan);
      box-shadow: 0 0 14px var(--accent-cyan-glow);
    }}

    /* Main Left Panel: Fidget Interactive Studio */
    #fidget-panel {{
      top: 92px;
      left: 20px;
      bottom: 20px;
      width: 380px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      padding: 16px;
    }}

    .panel-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--panel-border);
    }}

    .panel-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-bright);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .fidget-scroll-area {{
      flex: 1;
      overflow-y: auto;
      padding-right: 6px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    /* Fidget Mechanism Card */
    .fidget-card {{
      background: var(--panel-bg-subtle);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-md);
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    .fidget-card:hover {{
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .fidget-card.active-mech {{
      border-color: var(--accent-cyan);
      box-shadow: 0 0 18px rgba(0, 229, 255, 0.15);
    }}

    .fidget-card-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .mech-badge-title {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .mech-icon {{
      font-size: 1.1rem;
    }}

    .mech-name {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-bright);
    }}

    .mech-stats {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.68rem;
      color: var(--accent-cyan);
      background: rgba(0, 229, 255, 0.1);
      padding: 2px 7px;
      border-radius: 4px;
    }}

    .mech-slider-wrap {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .slider-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 0.7rem;
      color: var(--text-muted);
    }}

    .slider-labels span.cur-val {{
      color: var(--text-bright);
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
    }}

    input[type="range"] {{
      -webkit-appearance: none;
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: rgba(255, 255, 255, 0.12);
      outline: none;
      cursor: pointer;
    }}

    input[type="range"]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--accent-cyan);
      box-shadow: 0 0 10px var(--accent-cyan-glow);
      cursor: pointer;
      transition: transform 0.1s ease;
    }}

    input[type="range"]::-webkit-slider-thumb:hover {{
      transform: scale(1.2);
    }}

    .mech-btn-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
    }}

    .mech-btn-grid.four-col {{
      grid-template-columns: repeat(4, 1fr);
    }}

    .btn-sm {{
      padding: 5px 8px;
      font-size: 0.72rem;
      justify-content: center;
    }}

    /* RPM Gauge Bar */
    .rpm-gauge {{
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
      position: relative;
    }}

    .rpm-bar {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent-green), var(--accent-gold), var(--accent-red));
      transition: width 0.1s ease;
    }}

    /* Main Right Panel: Multi-Tab Analytics, Cutaway, BOM & Variants */
    #right-panel {{
      top: 92px;
      right: 20px;
      bottom: 20px;
      width: 400px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      padding: 16px;
    }}

    /* Tab Selector */
    .tab-bar {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 4px;
      background: rgba(0, 0, 0, 0.35);
      padding: 4px;
      border-radius: var(--radius-md);
      margin-bottom: 12px;
    }}

    .tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-family: 'Outfit', sans-serif;
      font-size: 0.72rem;
      font-weight: 600;
      padding: 6px 4px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .tab-btn:hover {{
      color: var(--text-bright);
      background: rgba(255, 255, 255, 0.05);
    }}

    .tab-btn.active {{
      color: var(--text-bright);
      background: var(--panel-bg);
      border: 1px solid var(--panel-border-bright);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }}

    .tab-content {{
      flex: 1;
      overflow-y: auto;
      padding-right: 4px;
      display: none;
    }}

    .tab-content.active {{
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    /* Analytics Tab Content */
    .metric-box {{
      background: var(--panel-bg-subtle);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-md);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .metric-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-bright);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .chart-container {{
      width: 100%;
      height: 90px;
      background: rgba(0, 0, 0, 0.45);
      border-radius: var(--radius-sm);
      border: 1px solid rgba(255, 255, 255, 0.06);
      position: relative;
      overflow: hidden;
    }}

    .chart-svg {{
      width: 100%;
      height: 100%;
    }}

    .chart-cursor {{
      stroke: var(--accent-cyan);
      stroke-width: 2;
      stroke-dasharray: 2, 2;
    }}

    .chart-path {{
      fill: none;
      stroke-width: 2.5;
    }}

    .chart-fill {{
      opacity: 0.18;
    }}

    /* View & Inspection Controls */
    .view-modes-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }}

    .camera-presets-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
    }}

    /* Shell Variants Grid */
    .variant-card {{
      background: var(--panel-bg-subtle);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius-md);
      padding: 10px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .variant-card:hover {{
      border-color: rgba(255, 255, 255, 0.3);
      transform: translateY(-1px);
    }}

    .variant-card.active {{
      border-color: var(--accent-cyan);
      background: rgba(0, 229, 255, 0.08);
      box-shadow: 0 0 14px rgba(0, 229, 255, 0.2);
    }}

    .variant-info h4 {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--text-bright);
    }}

    .variant-info p {{
      font-size: 0.68rem;
      color: var(--text-muted);
    }}

    /* BOM Hierarchy List */
    .bom-group-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--accent-cyan);
      margin-top: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .bom-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 8px;
      border-radius: var(--radius-sm);
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 0.72rem;
    }}

    .bom-item:hover {{
      background: rgba(255, 255, 255, 0.06);
    }}

    .bom-item-name {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .color-swatch {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      border: 1px solid rgba(255, 255, 255, 0.4);
    }}

    .bom-actions {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .icon-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 0.8rem;
      padding: 2px;
      transition: color 0.15s ease;
    }}

    .icon-btn:hover {{
      color: var(--text-bright);
    }}

    /* Loading Overlay */
    #loader {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 14px;
      z-index: 100;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }}

    .spinner {{
      width: 48px;
      height: 48px;
      border: 3px solid rgba(0, 229, 255, 0.15);
      border-top-color: var(--accent-cyan);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }}

    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}

    .loader-text {{
      font-family: 'Outfit', sans-serif;
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--accent-cyan);
      letter-spacing: 0.5px;
    }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.15); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 255, 255, 0.3); }}
  </style>
</head>
<body>
  <div id="webgl-canvas"></div>

  <!-- Top Navigation & Header Bar -->
  <div class="glass-panel" id="top-bar">
    <div class="brand-group">
      <div class="brand-badge">v1.2 Studio</div>
      <div class="brand-titles">
        <h1><span class="pulse-dot"></span> Custom Hybrid Grenade Fidget Toy</h1>
        <p>Interactive Kinematics, 5-Detent Mechanics & 3D Click Visualizer</p>
      </div>
    </div>

    <div class="header-badges">
      <div class="h-badge cyan">💥 23.91 N Plunger Detent</div>
      <div class="h-badge orange">🔄 33-Click Waist Detent</div>
      <div class="h-badge green">📐 4-Pos Hinge (0°-90°)</div>
      <div class="h-badge gold">💫 360° Gyro Spinner</div>
    </div>

    <div class="header-actions">
      <button class="btn" id="btn-sound-toggle" title="Toggle Synthesized Audio Clicks">🔊 Audio On</button>
      <button class="btn btn-primary" id="btn-showcase-all">🎬 Showcase All Clicks</button>
      <button class="btn" id="btn-reset-assembly" title="Reset All Motions to Zero">↺ Reset</button>
    </div>
  </div>

  <!-- Left Panel: Fidget Interactive Studio -->
  <div class="glass-panel" id="fidget-panel">
    <div class="panel-header">
      <div class="panel-title">🎮 Fidget Controls</div>
      <span style="font-size: 0.7rem; color: var(--accent-cyan);">6 Live Stations</span>
    </div>

    <div class="fidget-scroll-area">
      <!-- 1. Axial Plunger Detent -->
      <div class="fidget-card active-mech" id="card-plunger">
        <div class="fidget-card-top">
          <div class="mech-badge-title">
            <span class="mech-icon">💥</span>
            <span class="mech-name">Axial Rod Plunger</span>
          </div>
          <span class="mech-stats" id="plunger-click-badge">Click 0 / 7</span>
        </div>
        <div class="mech-slider-wrap">
          <div class="slider-labels">
            <span>Stroke Travel (Y)</span>
            <span class="cur-val" id="val-plunger">0.00 mm</span>
          </div>
          <input type="range" id="slider-plunger" min="0" max="24" step="0.05" value="0">
        </div>
        <div class="mech-btn-grid">
          <button class="btn btn-sm" id="btn-plunger-down">⬇️ -1 Click (3.18mm)</button>
          <button class="btn btn-sm" id="btn-plunger-up">⬆️ +1 Click (3.18mm)</button>
        </div>
        <div class="mech-btn-grid">
          <button class="btn btn-sm" id="btn-plunger-snap">⚡ Snap to Nearest</button>
          <button class="btn btn-sm" id="btn-plunger-loop">🔄 Auto Plunge Loop</button>
        </div>
      </div>

      <!-- 2. Rotary 33-Click Waist Detent -->
      <div class="fidget-card" id="card-waist">
        <div class="fidget-card-top">
          <div class="mech-badge-title">
            <span class="mech-icon">🔄</span>
            <span class="mech-name">33-Click Waist Detent</span>
          </div>
          <span class="mech-stats" id="waist-click-badge">Click 0 / 33</span>
        </div>
        <div class="mech-slider-wrap">
          <div class="slider-labels">
            <span>Mid-Shell Angle</span>
            <span class="cur-val" id="val-waist">0.0°</span>
          </div>
          <input type="range" id="slider-waist" min="0" max="360" step="0.1" value="0">
        </div>
        <div class="mech-btn-grid">
          <button class="btn btn-sm" id="btn-waist-prev">◀ -1 Click (10.9°)</button>
          <button class="btn btn-sm" id="btn-waist-next">▶ +1 Click (10.9°)</button>
        </div>
        <div class="mech-btn-grid">
          <button class="btn btn-sm" id="btn-waist-spin-fwd">⚡ Continuous CW</button>
          <button class="btn btn-sm" id="btn-waist-spin-rev">⚡ Continuous CCW</button>
        </div>
      </div>

      <!-- 3. Folding Handle Hinge Detent -->
      <div class="fidget-card" id="card-hinge">
        <div class="fidget-card-top">
          <div class="mech-badge-title">
            <span class="mech-icon">📐</span>
            <span class="mech-name">Folding Handle Hinge</span>
          </div>
          <span class="mech-stats" id="hinge-pos-badge">0° Folded</span>
        </div>
        <div class="mech-slider-wrap">
          <div class="slider-labels">
            <span>Hinge Fold Angle</span>
            <span class="cur-val" id="val-hinge">0.0°</span>
          </div>
          <input type="range" id="slider-hinge" min="0" max="90" step="0.5" value="0">
        </div>
        <div class="mech-btn-grid four-col">
          <button class="btn btn-sm" id="btn-hinge-0">0°</button>
          <button class="btn btn-sm" id="btn-hinge-30">30°</button>
          <button class="btn btn-sm" id="btn-hinge-60">60°</button>
          <button class="btn btn-sm" id="btn-hinge-90">90°</button>
        </div>
      </div>

      <!-- 4. Outer Rim Gear Roll Detent -->
      <div class="fidget-card" id="card-gear">
        <div class="fidget-card-top">
          <div class="mech-badge-title">
            <span class="mech-icon">⚙️</span>
            <span class="mech-name">20-Tooth Rim Gear</span>
          </div>
          <span class="mech-stats" id="gear-click-badge">Tooth 0 / 20</span>
        </div>
        <div class="mech-slider-wrap">
          <div class="slider-labels">
            <span>Thumb Roll Angle</span>
            <span class="cur-val" id="val-gear">0.0°</span>
          </div>
          <input type="range" id="slider-gear" min="0" max="360" step="0.5" value="0">
        </div>
        <div class="mech-btn-grid">
          <button class="btn btn-sm" id="btn-gear-prev">◀ -1 Tooth (18°)</button>
          <button class="btn btn-sm" id="btn-gear-next">▶ +1 Tooth (18°)</button>
        </div>
        <button class="btn btn-sm" id="btn-gear-roll">🎡 Continuous Roll</button>
      </div>

      <!-- 5. Center Gyro Ring Spinner -->
      <div class="fidget-card" id="card-spinner">
        <div class="fidget-card-top">
          <div class="mech-badge-title">
            <span class="mech-icon">💫</span>
            <span class="mech-name">Center Gyro Ring</span>
          </div>
          <span class="mech-stats" id="spinner-rpm-badge">0 RPM</span>
        </div>
        <div class="rpm-gauge">
          <div class="rpm-bar" id="rpm-bar-fill"></div>
        </div>
        <div class="mech-btn-grid">
          <button class="btn btn-sm btn-primary" id="btn-flick-spin">⚡ FLICK TO SPIN</button>
          <button class="btn btn-sm" id="btn-stop-spin">🛑 Stop Spin</button>
        </div>
      </div>

      <!-- 6. Upper Station Crown Twist -->
      <div class="fidget-card" id="card-upper">
        <div class="fidget-card-top">
          <div class="mech-badge-title">
            <span class="mech-icon">👑</span>
            <span class="mech-name">Upper Station Crown</span>
          </div>
          <span class="mech-stats">Rotary Top</span>
        </div>
        <div class="mech-slider-wrap">
          <div class="slider-labels">
            <span>Upper Crown Angle</span>
            <span class="cur-val" id="val-upper">0.0°</span>
          </div>
          <input type="range" id="slider-upper" min="0" max="360" step="1" value="0">
        </div>
      </div>
    </div>
  </div>

  <!-- Right Panel: Multi-Tab Analytics, View Modes, Variants & BOM -->
  <div class="glass-panel" id="right-panel">
    <!-- Tab Selector -->
    <div class="tab-bar">
      <button class="tab-btn active" data-tab="tab-analytics">📊 Telemetry</button>
      <button class="tab-btn" data-tab="tab-view">🔍 Inspection</button>
      <button class="tab-btn" data-tab="tab-variants">🛡️ Shells</button>
      <button class="tab-btn" data-tab="tab-bom">🧩 34 BOM</button>
    </div>

    <!-- Tab 1: Live Detent Telemetry & Waveforms -->
    <div class="tab-content active" id="tab-analytics">
      <!-- Axial Plunger Detent Waveform -->
      <div class="metric-box">
        <div class="metric-title">
          <span>Axial Detent Force Curve F(y)</span>
          <span style="color: var(--accent-cyan);" id="telemetry-force">0.0 N</span>
        </div>
        <div class="chart-container">
          <svg class="chart-svg" id="svg-axial-chart" viewBox="0 0 300 90">
            <line x1="0" y1="45" x2="300" y2="45" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
            <path class="chart-path" stroke="#00e5ff" d="M 0 75 Q 37.5 10 75 75 T 150 75 T 225 75 T 300 75"/>
            <line id="cursor-axial" class="chart-cursor" x1="0" y1="0" x2="0" y2="90"/>
          </svg>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.68rem; color: var(--text-muted);">
          <span>Peak: 23.91 N Breakout</span>
          <span>Pitch: 3.177 mm</span>
          <span>Snap Ratio: 7.62x</span>
        </div>
      </div>

      <!-- Waist Ratchet Detent Waveform -->
      <div class="metric-box">
        <div class="metric-title">
          <span>Waist Detent Swept Overlap V(θ)</span>
          <span style="color: var(--accent-orange);" id="telemetry-waist">1.33 mm³</span>
        </div>
        <div class="chart-container">
          <svg class="chart-svg" id="svg-waist-chart" viewBox="0 0 300 90">
            <line x1="0" y1="45" x2="300" y2="45" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
            <path class="chart-path" stroke="#ff7b25" d="M 0 70 Q 25 15 50 70 T 100 70 T 150 70 T 200 70 T 250 70 T 300 70"/>
            <line id="cursor-waist" class="chart-cursor" stroke="#ff7b25" x1="0" y1="0" x2="0" y2="90"/>
          </svg>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.68rem; color: var(--text-muted);">
          <span>Trough: 1.33 mm³</span>
          <span>Peak: 10.18 mm³</span>
          <span>Pitch: 10.909°</span>
        </div>
      </div>

      <!-- Hinge Detent Potential Wells -->
      <div class="metric-box">
        <div class="metric-title">
          <span>Hinge 4-Position Potential Wells</span>
          <span style="color: var(--accent-green);" id="telemetry-hinge">0° Folded</span>
        </div>
        <div class="chart-container">
          <svg class="chart-svg" id="svg-hinge-chart" viewBox="0 0 300 90">
            <path class="chart-path" stroke="#10b981" d="M 0 75 C 25 15, 75 15, 100 75 C 125 15, 175 15, 200 75 C 225 15, 275 15, 300 75"/>
            <circle cx="0" cy="75" r="4" fill="#10b981"/>
            <circle cx="100" cy="75" r="4" fill="#10b981"/>
            <circle cx="200" cy="75" r="4" fill="#10b981"/>
            <circle cx="300" cy="75" r="4" fill="#10b981"/>
            <line id="cursor-hinge" class="chart-cursor" stroke="#10b981" x1="0" y1="0" x2="0" y2="90"/>
          </svg>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.68rem; color: var(--text-muted);">
          <span>0° Folded</span>
          <span>30° Low Cant</span>
          <span>60° High Cant</span>
          <span>90° Upright</span>
        </div>
      </div>
    </div>

    <!-- Tab 2: CAD Inspection, Cutaway & Camera Directors -->
    <div class="tab-content" id="tab-view">
      <div class="metric-box">
        <div class="metric-title"><span>Viewing Modes</span></div>
        <div class="view-modes-grid">
          <button class="btn btn-sm btn-active" id="btn-mode-assembled">🚀 Assembled</button>
          <button class="btn btn-sm" id="btn-mode-cutaway">🔬 CAD Cutaway</button>
          <button class="btn btn-sm" id="btn-mode-xray">👻 X-Ray Ghost</button>
          <button class="btn btn-sm" id="btn-mode-exploded">💥 Exploded View</button>
        </div>
      </div>

      <!-- Cutaway Controls (Visible in Cutaway Mode) -->
      <div class="metric-box" id="box-cutaway-controls" style="display: none;">
        <div class="metric-title">
          <span>Cross-Section Clipping Plane</span>
          <button class="btn btn-sm" id="btn-flip-cut" style="padding: 2px 6px; font-size:0.68rem;">Invert Side</button>
        </div>
        <div class="mech-slider-wrap">
          <div class="slider-labels">
            <span>Cut Plane Offset (Z Axis)</span>
            <span class="cur-val" id="val-cut-offset">0.0 mm</span>
          </div>
          <input type="range" id="slider-cut-offset" min="-25" max="25" step="0.5" value="0">
        </div>
      </div>

      <!-- Exploded Slider (Visible in Exploded Mode) -->
      <div class="metric-box" id="box-exploded-controls" style="display: none;">
        <div class="metric-title">
          <span>Exploded Distance</span>
          <span class="cur-val" id="val-explode-pct">100%</span>
        </div>
        <input type="range" id="slider-explode" min="0" max="150" step="1" value="100">
      </div>

      <!-- Focused Camera Presets -->
      <div class="metric-box">
        <div class="metric-title"><span>Camera Director Presets</span></div>
        <div class="camera-presets-grid">
          <button class="btn btn-sm" id="cam-iso">🎥 Isometric</button>
          <button class="btn btn-sm" id="cam-plunger">🎯 Plunger</button>
          <button class="btn btn-sm" id="cam-waist">🎯 Waist 33</button>
          <button class="btn btn-sm" id="cam-hinge">🎯 Hinge Pod</button>
          <button class="btn btn-sm" id="cam-gear">🎯 20T Gear</button>
          <button class="btn btn-sm" id="cam-spinner">🎯 Gyro Ring</button>
        </div>
      </div>
    </div>

    <!-- Tab 3: 8 Interchangeable Mid Shell Variants -->
    <div class="tab-content" id="tab-variants">
      <div style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 4px;">
        100% mechanically verified 34.80mm height & 40.00mm mating land.
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px;" id="variant-list-container">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- Tab 4: 34-Part BOM Hierarchy & Isolation -->
    <div class="tab-content" id="tab-bom">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span style="font-size: 0.72rem; color: var(--text-muted);">All 34 parts watertight & single-body</span>
        <button class="btn btn-sm" id="btn-show-all-parts" style="padding: 2px 8px; font-size: 0.68rem;">Show All</button>
      </div>
      <div style="display: flex; flex-direction: column; gap: 6px;" id="bom-list-container">
        <!-- Rendered dynamically -->
      </div>
    </div>
  </div>

  <!-- Loader Spinner -->
  <div id="loader">
    <div class="spinner"></div>
    <div class="loader-text" id="loader-msg">Initializing 3D Assembly & Kinematic Rig...</div>
  </div>

  <!-- Three.js and Dependencies -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>

  <script>
    // Data Constants
    const PARTS_DATA = {parts_json};
    const VARIANTS_DATA = {variants_json};
    const DETENT_SPECS = {detent_json};

    // Kinematic & Simulation State
    const kinematics = {{
      plungerY: 0.0,       // 0.0 to 24.0 mm
      waistAngle: 0.0,     // 0.0 to 360.0 deg
      hingeAngle: 0.0,     // 0.0 to 90.0 deg
      gearAngle: 0.0,      // 0.0 to 360.0 deg
      spinnerAngle: 0.0,   // continuous
      spinnerRPM: 0.0,     // 0 to 4500 RPM
      upperAngle: 0.0,     // 0 to 360.0 deg
      cutPlaneZ: 0.0,      // clipping plane
      cutInverted: false,
      explodeFactor: 0.0,  // 0.0 to 1.5
      isPlungerLooping: false,
      isWaistSpinningFwd: false,
      isWaistSpinningRev: false,
      isGearRolling: false,
      isShowcaseActive: false,
      audioEnabled: true
    }};

    // Three.js State
    let scene, camera, renderer, controls;
    let mainModelRoot = null;
    let meshMap = {{}};
    let currentMode = 'Assembled'; // Assembled, Cutaway, XRay, Exploded
    let activeVariantIdx = 0;
    let clipPlane = null;

    // Kinematic Groups in Scenegraph
    let groupBase, groupWaist, groupUpperGear, groupRodPlunger, groupHingeFold, groupRimGear, groupRingSpinner;
    let springMeshes = {{}};

    // Web Audio Synthesizer
    let audioCtx = null;

    function initAudio() {{
      if (!audioCtx) {{
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) audioCtx = new AudioContext();
      }}
      if (audioCtx && audioCtx.state === 'suspended') {{
        audioCtx.resume();
      }}
    }}

    function playTactileSound(type, param = 1.0) {{
      if (!kinematics.audioEnabled) return;
      initAudio();
      if (!audioCtx) return;

      const now = audioCtx.currentTime;

      if (type === 'plunger') {{
        // Crisp dual-click snap
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(110, now + 0.04);
        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.045);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.05);

        // Click transient noise burst
        const bufferSize = audioCtx.sampleRate * 0.015;
        const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {{
          output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.3));
        }}
        const noise = audioCtx.createBufferSource();
        noise.buffer = noiseBuffer;
        const filter = audioCtx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.value = 2400;
        filter.Q.value = 3.0;
        const nGain = audioCtx.createGain();
        nGain.gain.setValueAtTime(0.4, now);
        noise.connect(filter);
        filter.connect(nGain);
        nGain.connect(audioCtx.destination);
        noise.start(now);
      }} else if (type === 'waist') {{
        // Sharp metallic/plastic tooth click (33-ratchet)
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(1450, now);
        osc.frequency.exponentialRampToValueAtTime(450, now + 0.018);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.02);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.025);
      }} else if (type === 'hinge') {{
        // Deep tactile latch thud
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(160, now);
        osc.frequency.exponentialRampToValueAtTime(60, now + 0.06);
        gain.gain.setValueAtTime(0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.065);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.07);
      }} else if (type === 'gear') {{
        // Fine tooth tick (20T gear)
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(2800, now);
        osc.frequency.exponentialRampToValueAtTime(900, now + 0.012);
        gain.gain.setValueAtTime(0.22, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.015);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.02);
      }} else if (type === 'flick') {{
        // Gyro ring spin flick impulse
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(2200, now + 0.08);
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.12);
      }}
    }}

    // Three.js Scene Setup
    function init() {{
      const container = document.getElementById('webgl-canvas');

      // Scene
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x070a13);
      scene.fog = new THREE.FogExp2(0x070a13, 0.002);

      // Camera
      camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.set(130, 85, 145);

      // Clipping Plane for CAD Cutaway
      clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);

      // Renderer
      renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false, powerPreference: 'high-performance' }});
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.2;
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.localClippingEnabled = true;
      container.appendChild(renderer.domElement);

      // Orbit Controls
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.maxDistance = 450;
      controls.minDistance = 25;
      controls.target.set(0, 52, 0);

      // Studio Lighting
      setupLighting();

      // Floor Grid
      const grid = new THREE.GridHelper(260, 26, 0x1a2638, 0x0e1724);
      grid.position.y = -5;
      scene.add(grid);

      // Build UI Components
      buildShellVariantsUI();
      buildBomListUI();
      setupEventListeners();

      // Load Active Default 3D Assembly Model (01 AeroFlow)
      loadAssemblyModel(VARIANTS_DATA[0].file);

      // Animation Loop
      animate();
    }}

    function setupLighting() {{
      // Ambient Light
      const hemiLight = new THREE.HemisphereLight(0xddeeff, 0x111822, 0.75);
      scene.add(hemiLight);

      // Main Key Light
      const keyLight = new THREE.DirectionalLight(0xffffff, 1.35);
      keyLight.position.set(90, 140, 110);
      keyLight.castShadow = true;
      keyLight.shadow.mapSize.width = 2048;
      keyLight.shadow.mapSize.height = 2048;
      keyLight.shadow.camera.near = 10;
      keyLight.shadow.camera.far = 350;
      keyLight.shadow.camera.left = -70;
      keyLight.shadow.camera.right = 70;
      keyLight.shadow.camera.top = 90;
      keyLight.shadow.camera.bottom = -40;
      keyLight.shadow.bias = -0.0005;
      scene.add(keyLight);

      // Cyan Cool Fill Light
      const fillLight = new THREE.DirectionalLight(0x00e5ff, 0.65);
      fillLight.position.set(-100, 60, -70);
      scene.add(fillLight);

      // Warm Accent Rim Light
      const rimLight = new THREE.DirectionalLight(0xff7b25, 0.45);
      rimLight.position.set(0, -50, -80);
      scene.add(rimLight);
    }}

    // Part Classification Helper
    function getPartGroup(name) {{
      if (name.includes('Mid_Shell') && !name.includes('Spring_33')) return 'waist';
      if (name.includes('19_28_Upper_Shell_Gear')) return 'upper_gear';
      if (name.includes('Custom_Rod_Right') || name.includes('Custom_Rod_Middle') || name.includes('Custom_Rod_Left') ||
          name.includes('Custom_Rod_Lock') || name.includes('Spinner_Lever_08_Rod_Lock') ||
          name.includes('09_Rod_Spring_Hinge') || name.includes('15_Handle_Rotating_Lock_D_Pin')) {{
        return 'rod';
      }}
      if (name.includes('Custom_Handle_Left') || name.includes('Custom_Handle_Right') ||
          name.includes('Spinner_Lever_04_Spring') || name.includes('Custom_16_Handle_Lock_Neck') ||
          name.includes('Custom_16_Handle_Lock_Pod')) {{
        return 'handle';
      }}
      if (name.includes('Spinner_Lever_05_Gear')) return 'rim_gear';
      if (name.includes('Custom_Ring_Spinner')) return 'ring_spinner';
      if (name.includes('Custom_Rod_Detent_Spring_01')) return 'spring_01';
      if (name.includes('Custom_Rod_Detent_Spring_02')) return 'spring_02';
      if (name.includes('Custom_Rod_Detent_Spring_03')) return 'spring_03';
      if (name.includes('Custom_Rod_Detent_Spring_04')) return 'spring_04';
      return 'base';
    }}

    // Load & Rig 3D Assembly Kinematics with Exact 1:1 World CAD Alignment
    function loadAssemblyModel(filename) {{
      const loaderEl = document.getElementById('loader');
      const loaderMsg = document.getElementById('loader-msg');
      loaderEl.style.display = 'flex';
      loaderEl.style.opacity = '1';
      loaderMsg.textContent = `Loading ${{filename}}...`;

      // Clear previous model if exists
      if (mainModelRoot) {{
        scene.remove(mainModelRoot);
        mainModelRoot = null;
      }}

      meshMap = {{}};
      springMeshes = {{}};

      const gltfLoader = new THREE.GLTFLoader();
      gltfLoader.load(
        filename,
        (gltf) => {{
          const root = gltf.scene;
          mainModelRoot = new THREE.Group();
          scene.add(mainModelRoot);

          // Collect all raw meshes
          const rawMeshes = {{}};
          root.traverse((child) => {{
            if (child.isMesh) {{
              child.castShadow = true;
              child.receiveShadow = true;
              rawMeshes[child.name] = child;
            }}
          }});

          // Rig Kinematic Groups:
          // 1. Base Static Group (origin at 0, 0, 0)
          groupBase = new THREE.Group();
          groupBase.name = 'Kinematic_Group_Base';
          mainModelRoot.add(groupBase);

          // 2. Waist Rotator Group (rotates around Y axis at 0,0,0)
          groupWaist = new THREE.Group();
          groupWaist.name = 'Kinematic_Group_Waist';
          mainModelRoot.add(groupWaist);

          // 3. Upper Gear Group (rotates around Y axis at 0,0,0)
          groupUpperGear = new THREE.Group();
          groupUpperGear.name = 'Kinematic_Group_UpperGear';
          mainModelRoot.add(groupUpperGear);

          // 4. Rod Plunger Group (translates along Y axis)
          groupRodPlunger = new THREE.Group();
          groupRodPlunger.name = 'Kinematic_Group_RodPlunger';
          mainModelRoot.add(groupRodPlunger);

          // 5. Handle Hinge Group (Pivot at [0, 92.87, 0] relative to Rod)
          groupHingeFold = new THREE.Group();
          groupHingeFold.name = 'Kinematic_Group_HingeFold';
          groupHingeFold.position.set(0, 92.87, 0);
          groupRodPlunger.add(groupHingeFold);

          // 6. Rim Gear Group (Pivot at [0, 10.17, -28.79] relative to Hinge, which is [0, 103.04, -28.79] in world)
          groupRimGear = new THREE.Group();
          groupRimGear.name = 'Kinematic_Group_RimGear';
          groupRimGear.position.set(0, 10.17, -28.79);
          groupHingeFold.add(groupRimGear);

          // 7. Ring Spinner Group (Same pivot journal)
          groupRingSpinner = new THREE.Group();
          groupRingSpinner.name = 'Kinematic_Group_RingSpinner';
          groupRingSpinner.position.set(0, 10.17, -28.79);
          groupHingeFold.add(groupRingSpinner);

          // Attach meshes into kinematic groups with exact compensated local offsets:
          Object.entries(rawMeshes).forEach(([meshName, mesh]) => {{
            const pGroup = getPartGroup(meshName);
            meshMap[meshName] = mesh;

            // Find BOM spec if available
            const spec = PARTS_DATA.find(p => meshName.includes(p.name) || p.name.includes(meshName));
            mesh.userData.partSpec = spec;
            mesh.userData.dispVec = spec ? new THREE.Vector3(...spec.disp) : new THREE.Vector3(0, 0, 0);

            if (pGroup === 'waist') {{
              mesh.position.set(0, 0, 0);
              groupWaist.add(mesh);
            }} else if (pGroup === 'upper_gear') {{
              mesh.position.set(0, 0, 0);
              groupUpperGear.add(mesh);
            }} else if (pGroup === 'rod') {{
              mesh.position.set(0, 0, 0);
              groupRodPlunger.add(mesh);
            }} else if (pGroup === 'handle') {{
              // Local offset inside groupHingeFold (pivot at 92.87)
              mesh.position.set(0, -92.87, 0);
              groupHingeFold.add(mesh);
            }} else if (pGroup === 'rim_gear') {{
              // Local offset inside groupRimGear (pivot at 103.04, -28.79)
              mesh.position.set(0, -103.04, 28.79);
              groupRimGear.add(mesh);
            }} else if (pGroup === 'ring_spinner') {{
              // Local offset inside groupRingSpinner (pivot at 103.04, -28.79)
              mesh.position.set(0, -103.04, 28.79);
              groupRingSpinner.add(mesh);
            }} else if (pGroup.startsWith('spring_')) {{
              mesh.position.set(0, 0, 0);
              groupBase.add(mesh);
              springMeshes[pGroup] = mesh;
            }} else {{
              mesh.position.set(0, 0, 0);
              groupBase.add(mesh);
            }}
          }});

          applyViewMode(currentMode);
          updateKinematicsVisuals();

          loaderEl.style.opacity = '0';
          setTimeout(() => {{ loaderEl.style.display = 'none'; }}, 300);
        }},
        (xhr) => {{
          if (xhr.lengthComputable) {{
            const pct = Math.round((xhr.loaded / xhr.total) * 100);
            loaderMsg.textContent = `Loading 3D Model: ${{pct}}%`;
          }}
        }},
        (err) => {{
          console.error("GLTF load error:", err);
          loaderMsg.textContent = "Error loading model!";
        }}
      );
    }}

    // Kinematic Transformation & Spring Deflection Solver
    function updateKinematicsVisuals() {{
      if (!groupRodPlunger) return;

      // 1. Axial Plunger Vertical Translation
      groupRodPlunger.position.y = kinematics.plungerY;

      // 2. Waist Rotation (about Y axis)
      if (groupWaist) {{
        groupWaist.rotation.y = THREE.MathUtils.degToRad(kinematics.waistAngle);
      }}

      // 3. Upper Gear Rotation (about Y axis)
      if (groupUpperGear) {{
        groupUpperGear.rotation.y = THREE.MathUtils.degToRad(kinematics.upperAngle);
      }}

      // 4. Hinge Folding (about X axis)
      if (groupHingeFold) {{
        groupHingeFold.rotation.x = THREE.MathUtils.degToRad(kinematics.hingeAngle);
      }}

      // 5. Rim Gear Roll (about local X axis)
      if (groupRimGear) {{
        groupRimGear.rotation.x = THREE.MathUtils.degToRad(kinematics.gearAngle);
      }}

      // 6. Ring Spinner Gyro (about local X axis)
      if (groupRingSpinner) {{
        groupRingSpinner.rotation.x = THREE.MathUtils.degToRad(kinematics.spinnerAngle);
      }}

      // 7. Dynamic Spring Deflections:
      // Axial springs flex outward when rack teeth pass
      const pitch = DETENT_SPECS.axial.pitch_mm;
      const rackPhase = (kinematics.plungerY % pitch) / pitch;
      const axialDeflect = Math.sin(rackPhase * Math.PI * 2) * 0.45;

      if (springMeshes['spring_01']) springMeshes['spring_01'].position.x = -axialDeflect;
      if (springMeshes['spring_02']) springMeshes['spring_02'].position.z = axialDeflect;
      if (springMeshes['spring_03']) springMeshes['spring_03'].position.x = axialDeflect;
      if (springMeshes['spring_04']) springMeshes['spring_04'].position.z = -axialDeflect;

      // 8. Exploded View Offsets
      if (currentMode === 'Exploded') {{
        const ef = kinematics.explodeFactor;
        Object.values(meshMap).forEach((m) => {{
          if (m.userData.dispVec) {{
            const dv = m.userData.dispVec;
            m.position.x = dv.x * ef * 0.01;
            m.position.y = dv.y * ef * 0.01;
            m.position.z = dv.z * ef * 0.01;
          }}
        }});
      }}

      // Update Telemetry Displays
      updateTelemetryUI();
    }}

    function updateTelemetryUI() {{
      // Axial Plunger Telemetry
      const pY = kinematics.plungerY;
      const pitch = DETENT_SPECS.axial.pitch_mm;
      const clickIdx = Math.floor(pY / pitch);
      document.getElementById('val-plunger').textContent = `${{pY.toFixed(2)}} mm`;
      document.getElementById('plunger-click-badge').textContent = `Click ${{clickIdx}} / 7`;

      const normPhase = (pY % pitch) / pitch;
      const curForce = (Math.sin(normPhase * Math.PI) * (DETENT_SPECS.axial.peak_force_N - DETENT_SPECS.axial.held_force_N) + DETENT_SPECS.axial.held_force_N).toFixed(1);
      document.getElementById('telemetry-force').textContent = `${{curForce}} N`;
      const curX = ((pY / 24.0) * 300).toFixed(1);
      const cursorAxial = document.getElementById('cursor-axial');
      if (cursorAxial) cursorAxial.setAttribute('x1', curX), cursorAxial.setAttribute('x2', curX);

      // Waist Telemetry
      const wA = kinematics.waistAngle;
      const wClick = Math.floor((wA % 360) / DETENT_SPECS.waist.pitch_deg);
      document.getElementById('val-waist').textContent = `${{wA.toFixed(1)}}°`;
      document.getElementById('waist-click-badge').textContent = `Click ${{wClick}} / 33`;
      const wVol = (Math.sin(((wA % 10.909) / 10.909) * Math.PI) * (10.18 - 1.33) + 1.33).toFixed(2);
      document.getElementById('telemetry-waist').textContent = `${{wVol}} mm³`;
      const curWX = (((wA % 360) / 360.0) * 300).toFixed(1);
      const cursorWaist = document.getElementById('cursor-waist');
      if (cursorWaist) cursorWaist.setAttribute('x1', curWX), cursorWaist.setAttribute('x2', curWX);

      // Hinge Telemetry
      const hA = kinematics.hingeAngle;
      document.getElementById('val-hinge').textContent = `${{hA.toFixed(1)}}°`;
      let hLabel = 'Free Travel';
      if (Math.abs(hA - 0) < 3) hLabel = '0° Folded Down';
      else if (Math.abs(hA - 30) < 3) hLabel = '30° Low Cant';
      else if (Math.abs(hA - 60) < 3) hLabel = '60° High Cant';
      else if (Math.abs(hA - 90) < 3) hLabel = '90° Tactical Upright';
      document.getElementById('hinge-pos-badge').textContent = hLabel;
      document.getElementById('telemetry-hinge').textContent = hLabel;
      const curHX = ((hA / 90.0) * 300).toFixed(1);
      const cursorHinge = document.getElementById('cursor-hinge');
      if (cursorHinge) cursorHinge.setAttribute('x1', curHX), cursorHinge.setAttribute('x2', curHX);

      // Gear Telemetry
      const gA = kinematics.gearAngle;
      const gTooth = Math.floor((gA % 360) / DETENT_SPECS.rim_gear.pitch_deg);
      document.getElementById('val-gear').textContent = `${{gA.toFixed(1)}}°`;
      document.getElementById('gear-click-badge').textContent = `Tooth ${{gTooth}} / 20`;

      // Spinner Telemetry
      document.getElementById('spinner-rpm-badge').textContent = `${{Math.round(kinematics.spinnerRPM)}} RPM`;
      const rpmPct = Math.min(kinematics.spinnerRPM / 3500.0 * 100, 100);
      document.getElementById('rpm-bar-fill').style.width = `${{rpmPct}}%`;

      // Upper Crown Telemetry
      document.getElementById('val-upper').textContent = `${{kinematics.upperAngle.toFixed(0)}}°`;
    }}

    // Viewing Modes Handler
    function applyViewMode(mode) {{
      currentMode = mode;

      document.querySelectorAll('.view-modes-grid .btn').forEach(b => b.classList.remove('btn-active'));
      const btnMap = {{
        'Assembled': 'btn-mode-assembled',
        'Cutaway': 'btn-mode-cutaway',
        'XRay': 'btn-mode-xray',
        'Exploded': 'btn-mode-exploded'
      }};
      const btn = document.getElementById(btnMap[mode]);
      if (btn) btn.classList.add('btn-active');

      document.getElementById('box-cutaway-controls').style.display = (mode === 'Cutaway') ? 'flex' : 'none';
      document.getElementById('box-exploded-controls').style.display = (mode === 'Exploded') ? 'flex' : 'none';

      // Material Transformations
      Object.values(meshMap).forEach((m) => {{
        if (!m.material) return;
        const mat = m.material;

        if (mode === 'Cutaway') {{
          mat.clippingPlanes = [clipPlane];
          mat.clipShadows = true;
          mat.transparent = false;
          mat.opacity = 1.0;
        }} else if (mode === 'XRay') {{
          mat.clippingPlanes = [];
          const isSpring = m.name && (m.name.includes('Spring') || m.name.includes('spring'));
          mat.transparent = true;
          mat.opacity = isSpring ? 0.95 : 0.28;
          mat.wireframe = false;
        }} else {{
          // Assembled or Exploded
          mat.clippingPlanes = [];
          mat.transparent = false;
          mat.opacity = 1.0;
        }}
        mat.needsUpdate = true;
      }});
    }}

    // UI Event Listeners & Interactive Handlers
    function setupEventListeners() {{
      window.addEventListener('resize', onWindowResize);

      // Sound Toggle
      const soundBtn = document.getElementById('btn-sound-toggle');
      soundBtn.addEventListener('click', () => {{
        kinematics.audioEnabled = !kinematics.audioEnabled;
        soundBtn.textContent = kinematics.audioEnabled ? '🔊 Audio On' : '🔇 Audio Muted';
        soundBtn.classList.toggle('btn-primary', kinematics.audioEnabled);
      }});

      // Reset Button
      document.getElementById('btn-reset-assembly').addEventListener('click', () => {{
        kinematics.plungerY = 0;
        kinematics.waistAngle = 0;
        kinematics.hingeAngle = 0;
        kinematics.gearAngle = 0;
        kinematics.spinnerRPM = 0;
        kinematics.upperAngle = 0;
        kinematics.isPlungerLooping = false;
        kinematics.isWaistSpinningFwd = false;
        kinematics.isWaistSpinningRev = false;
        kinematics.isGearRolling = false;
        kinematics.isShowcaseActive = false;
        syncAllSliders();
        updateKinematicsVisuals();
      }});

      // Plunger Slider & Step Buttons
      const sPlunger = document.getElementById('slider-plunger');
      let lastPlungerClick = 0;
      sPlunger.addEventListener('input', (e) => {{
        kinematics.plungerY = parseFloat(e.target.value);
        const curClick = Math.floor(kinematics.plungerY / DETENT_SPECS.axial.pitch_mm);
        if (curClick !== lastPlungerClick) {{
          playTactileSound('plunger');
          lastPlungerClick = curClick;
        }}
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-plunger-up').addEventListener('click', () => {{
        kinematics.plungerY = Math.min(kinematics.plungerY + DETENT_SPECS.axial.pitch_mm, 24.0);
        sPlunger.value = kinematics.plungerY;
        playTactileSound('plunger');
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-plunger-down').addEventListener('click', () => {{
        kinematics.plungerY = Math.max(kinematics.plungerY - DETENT_SPECS.axial.pitch_mm, 0.0);
        sPlunger.value = kinematics.plungerY;
        playTactileSound('plunger');
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-plunger-snap').addEventListener('click', () => {{
        const pitch = DETENT_SPECS.axial.pitch_mm;
        kinematics.plungerY = Math.round(kinematics.plungerY / pitch) * pitch;
        sPlunger.value = kinematics.plungerY;
        playTactileSound('plunger');
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-plunger-loop').addEventListener('click', () => {{
        kinematics.isPlungerLooping = !kinematics.isPlungerLooping;
        document.getElementById('btn-plunger-loop').classList.toggle('btn-primary', kinematics.isPlungerLooping);
      }});

      // Waist Slider & Controls
      const sWaist = document.getElementById('slider-waist');
      let lastWaistClick = 0;
      sWaist.addEventListener('input', (e) => {{
        kinematics.waistAngle = parseFloat(e.target.value);
        const curClick = Math.floor((kinematics.waistAngle % 360) / DETENT_SPECS.waist.pitch_deg);
        if (curClick !== lastWaistClick) {{
          playTactileSound('waist');
          lastWaistClick = curClick;
        }}
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-waist-next').addEventListener('click', () => {{
        kinematics.waistAngle = (kinematics.waistAngle + DETENT_SPECS.waist.pitch_deg) % 360;
        sWaist.value = kinematics.waistAngle;
        playTactileSound('waist');
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-waist-prev').addEventListener('click', () => {{
        kinematics.waistAngle = (kinematics.waistAngle - DETENT_SPECS.waist.pitch_deg + 360) % 360;
        sWaist.value = kinematics.waistAngle;
        playTactileSound('waist');
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-waist-spin-fwd').addEventListener('click', () => {{
        kinematics.isWaistSpinningFwd = !kinematics.isWaistSpinningFwd;
        kinematics.isWaistSpinningRev = false;
        document.getElementById('btn-waist-spin-fwd').classList.toggle('btn-primary', kinematics.isWaistSpinningFwd);
        document.getElementById('btn-waist-spin-rev').classList.remove('btn-primary');
      }});

      document.getElementById('btn-waist-spin-rev').addEventListener('click', () => {{
        kinematics.isWaistSpinningRev = !kinematics.isWaistSpinningRev;
        kinematics.isWaistSpinningFwd = false;
        document.getElementById('btn-waist-spin-rev').classList.toggle('btn-primary', kinematics.isWaistSpinningRev);
        document.getElementById('btn-waist-spin-fwd').classList.remove('btn-primary');
      }});

      // Hinge Slider & Presets
      const sHinge = document.getElementById('slider-hinge');
      sHinge.addEventListener('input', (e) => {{
        kinematics.hingeAngle = parseFloat(e.target.value);
        updateKinematicsVisuals();
      }});

      [0, 30, 60, 90].forEach(deg => {{
        const btn = document.getElementById(`btn-hinge-${{deg}}`);
        if (btn) {{
          btn.addEventListener('click', () => {{
            kinematics.hingeAngle = deg;
            sHinge.value = deg;
            playTactileSound('hinge');
            updateKinematicsVisuals();
          }});
        }}
      }});

      // Gear Slider & Controls
      const sGear = document.getElementById('slider-gear');
      let lastGearTooth = 0;
      sGear.addEventListener('input', (e) => {{
        kinematics.gearAngle = parseFloat(e.target.value);
        const curTooth = Math.floor((kinematics.gearAngle % 360) / DETENT_SPECS.rim_gear.pitch_deg);
        if (curTooth !== lastGearTooth) {{
          playTactileSound('gear');
          lastGearTooth = curTooth;
        }}
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-gear-next').addEventListener('click', () => {{
        kinematics.gearAngle = (kinematics.gearAngle + DETENT_SPECS.rim_gear.pitch_deg) % 360;
        sGear.value = kinematics.gearAngle;
        playTactileSound('gear');
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-gear-prev').addEventListener('click', () => {{
        kinematics.gearAngle = (kinematics.gearAngle - DETENT_SPECS.rim_gear.pitch_deg + 360) % 360;
        sGear.value = kinematics.gearAngle;
        playTactileSound('gear');
        updateKinematicsVisuals();
      }});

      document.getElementById('btn-gear-roll').addEventListener('click', () => {{
        kinematics.isGearRolling = !kinematics.isGearRolling;
        document.getElementById('btn-gear-roll').classList.toggle('btn-primary', kinematics.isGearRolling);
      }});

      // Spinner Flick
      document.getElementById('btn-flick-spin').addEventListener('click', () => {{
        kinematics.spinnerRPM = Math.min(kinematics.spinnerRPM + 2800, 4200);
        playTactileSound('flick');
      }});

      document.getElementById('btn-stop-spin').addEventListener('click', () => {{
        kinematics.spinnerRPM = 0;
      }});

      // Upper Crown Slider
      document.getElementById('slider-upper').addEventListener('input', (e) => {{
        kinematics.upperAngle = parseFloat(e.target.value);
        updateKinematicsVisuals();
      }});

      // Tab Switching
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
          btn.classList.add('active');
          const target = document.getElementById(btn.dataset.tab);
          if (target) target.classList.add('active');
        }});
      }});

      // View Modes
      document.getElementById('btn-mode-assembled').addEventListener('click', () => applyViewMode('Assembled'));
      document.getElementById('btn-mode-cutaway').addEventListener('click', () => applyViewMode('Cutaway'));
      document.getElementById('btn-mode-xray').addEventListener('click', () => applyViewMode('XRay'));
      document.getElementById('btn-mode-exploded').addEventListener('click', () => applyViewMode('Exploded'));

      // Cutaway Offset Slider
      document.getElementById('slider-cut-offset').addEventListener('input', (e) => {{
        const val = parseFloat(e.target.value);
        kinematics.cutPlaneZ = val;
        document.getElementById('val-cut-offset').textContent = `${{val.toFixed(1)}} mm`;
        const dir = kinematics.cutInverted ? 1 : -1;
        clipPlane.set(new THREE.Vector3(0, 0, dir), -val * dir);
      }});

      document.getElementById('btn-flip-cut').addEventListener('click', () => {{
        kinematics.cutInverted = !kinematics.cutInverted;
        const dir = kinematics.cutInverted ? 1 : -1;
        clipPlane.set(new THREE.Vector3(0, 0, dir), -kinematics.cutPlaneZ * dir);
      }});

      // Explode Slider
      document.getElementById('slider-explode').addEventListener('input', (e) => {{
        kinematics.explodeFactor = parseFloat(e.target.value);
        document.getElementById('val-explode-pct').textContent = `${{Math.round(kinematics.explodeFactor)}}%`;
        updateKinematicsVisuals();
      }});

      // Camera Presets
      setupCameraPresets();

      // Showcase All
      document.getElementById('btn-showcase-all').addEventListener('click', toggleShowcaseMode);
    }}

    function syncAllSliders() {{
      document.getElementById('slider-plunger').value = kinematics.plungerY;
      document.getElementById('slider-waist').value = kinematics.waistAngle;
      document.getElementById('slider-hinge').value = kinematics.hingeAngle;
      document.getElementById('slider-gear').value = kinematics.gearAngle;
      document.getElementById('slider-upper').value = kinematics.upperAngle;
    }}

    function setupCameraPresets() {{
      const presets = {{
        'cam-iso': {{ pos: [130, 85, 145], target: [0, 52, 0] }},
        'cam-plunger': {{ pos: [45, 55, 65], target: [0, 50, 0] }},
        'cam-waist': {{ pos: [65, 38, 55], target: [0, 37, 0] }},
        'cam-hinge': {{ pos: [40, 95, 45], target: [0, 92, 0] }},
        'cam-gear': {{ pos: [35, 105, -15], target: [0, 103, -28] }},
        'cam-spinner': {{ pos: [25, 108, -10], target: [0, 103, -28] }}
      }};

      Object.entries(presets).forEach(([btnId, cfg]) => {{
        const btn = document.getElementById(btnId);
        if (btn) {{
          btn.addEventListener('click', () => {{
            animateCamera(cfg.pos, cfg.target);
          }});
        }}
      }});
    }}

    function animateCamera(targetPos, targetLookAt) {{
      const startPos = camera.position.clone();
      const startTarget = controls.target.clone();
      const endPos = new THREE.Vector3(...targetPos);
      const endTarget = new THREE.Vector3(...targetLookAt);

      let startTime = performance.now();
      const duration = 650;

      function step(now) {{
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1.0);
        const ease = 0.5 - Math.cos(progress * Math.PI) / 2;

        camera.position.lerpVectors(startPos, endPos, ease);
        controls.target.lerpVectors(startTarget, endTarget, ease);
        controls.update();

        if (progress < 1.0) {{
          requestAnimationFrame(step);
        }}
      }}
      requestAnimationFrame(step);
    }}

    // Automated Fidget Showcase Choreography
    let showcasePhase = 0;
    let showcaseTimer = 0;
    function toggleShowcaseMode() {{
      kinematics.isShowcaseActive = !kinematics.isShowcaseActive;
      const btn = document.getElementById('btn-showcase-all');
      btn.classList.toggle('btn-active', kinematics.isShowcaseActive);
      btn.textContent = kinematics.isShowcaseActive ? '⏹ Stop Showcase' : '🎬 Showcase All Clicks';
      if (kinematics.isShowcaseActive) {{
        showcasePhase = 0;
        showcaseTimer = 0;
      }}
    }}

    // Build Shell Variants Selector UI
    function buildShellVariantsUI() {{
      const container = document.getElementById('variant-list-container');
      container.innerHTML = '';
      VARIANTS_DATA.forEach((v, idx) => {{
        const card = document.createElement('div');
        card.className = `variant-card ${{idx === activeVariantIdx ? 'active' : ''}}`;
        card.innerHTML = `
          <div class="variant-info">
            <h4>${{v.name}}</h4>
            <p>${{v.desc}}</p>
          </div>
          <span style="font-size:0.68rem; color:var(--accent-cyan); font-family: 'JetBrains Mono';">${{v.maxDia}}</span>
        `;
        card.addEventListener('click', () => {{
          document.querySelectorAll('.variant-card').forEach(c => c.classList.remove('active'));
          card.classList.add('active');
          activeVariantIdx = idx;
          loadAssemblyModel(v.file);
        }});
        container.appendChild(card);
      }});
    }}

    // Build 34-Part BOM Hierarchy UI
    function buildBomListUI() {{
      const container = document.getElementById('bom-list-container');
      container.innerHTML = '';

      let currentSub = '';
      PARTS_DATA.forEach(p => {{
        if (p.subassembly !== currentSub) {{
          currentSub = p.subassembly;
          const subTitle = document.createElement('div');
          subTitle.className = 'bom-group-title';
          subTitle.textContent = currentSub.replace(/_/g, ' ');
          container.appendChild(subTitle);
        }}

        const item = document.createElement('div');
        item.className = 'bom-item';
        item.innerHTML = `
          <div class="bom-item-name">
            <div class="color-swatch" style="background: ${{p.color}};"></div>
            <span>${{p.name}}</span>
          </div>
          <div class="bom-actions">
            <button class="icon-btn" title="Isolate Part" data-part="${{p.name}}">👁️</button>
          </div>
        `;

        item.querySelector('.icon-btn').addEventListener('click', () => {{
          isolatePart(p.name);
        }});

        container.appendChild(item);
      }});

      document.getElementById('btn-show-all-parts').addEventListener('click', () => {{
        Object.values(meshMap).forEach(m => m.visible = true);
      }});
    }}

    function isolatePart(partName) {{
      Object.entries(meshMap).forEach(([name, m]) => {{
        m.visible = name.includes(partName) || partName.includes(name);
      }});
    }}

    function onWindowResize() {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }}

    // Animation & Kinematics Tick Loop
    let lastTime = performance.now();
    let waistClickAcc = 0;
    let gearClickAcc = 0;

    function animate(time) {{
      requestAnimationFrame(animate);
      const delta = (time - lastTime) * 0.001;
      lastTime = time;

      // 1. Center Gyro Ring Inertia Drag Physics
      if (kinematics.spinnerRPM > 0.1) {{
        const rps = kinematics.spinnerRPM / 60.0;
        kinematics.spinnerAngle += rps * 360 * delta;
        kinematics.spinnerRPM *= Math.pow(0.97, delta * 60);
        if (kinematics.spinnerRPM < 1) kinematics.spinnerRPM = 0;
        updateKinematicsVisuals();
      }}

      // 2. Plunger Auto-Oscillation
      if (kinematics.isPlungerLooping) {{
        const pSpeed = 16.0; // mm/s
        kinematics.plungerY += pSpeed * delta;
        if (kinematics.plungerY > 24.0) kinematics.plungerY = 0.0;
        document.getElementById('slider-plunger').value = kinematics.plungerY;
        updateKinematicsVisuals();
      }}

      // 3. Waist Continuous Rotation
      if (kinematics.isWaistSpinningFwd || kinematics.isWaistSpinningRev) {{
        const dir = kinematics.isWaistSpinningFwd ? 1 : -1;
        const wSpeed = 45.0 * dir; // deg/s
        kinematics.waistAngle = (kinematics.waistAngle + wSpeed * delta + 360) % 360;
        document.getElementById('slider-waist').value = kinematics.waistAngle;

        waistClickAcc += Math.abs(wSpeed * delta);
        if (waistClickAcc >= DETENT_SPECS.waist.pitch_deg) {{
          playTactileSound('waist');
          waistClickAcc -= DETENT_SPECS.waist.pitch_deg;
        }}
        updateKinematicsVisuals();
      }}

      // 4. Rim Gear Continuous Roll
      if (kinematics.isGearRolling) {{
        const gSpeed = 72.0; // deg/s
        kinematics.gearAngle = (kinematics.gearAngle + gSpeed * delta) % 360;
        document.getElementById('slider-gear').value = kinematics.gearAngle;

        gearClickAcc += gSpeed * delta;
        if (gearClickAcc >= DETENT_SPECS.rim_gear.pitch_deg) {{
          playTactileSound('gear');
          gearClickAcc -= DETENT_SPECS.rim_gear.pitch_deg;
        }}
        updateKinematicsVisuals();
      }}

      // 5. Automated Showcase Choreography
      if (kinematics.isShowcaseActive) {{
        showcaseTimer += delta;
        if (showcasePhase === 0) {{
          // Unfold Hinge 0 -> 90
          kinematics.hingeAngle = Math.min(showcaseTimer * 45, 90);
          document.getElementById('slider-hinge').value = kinematics.hingeAngle;
          if (showcaseTimer >= 2.0) {{
            showcasePhase = 1;
            showcaseTimer = 0;
            playTactileSound('flick');
            kinematics.spinnerRPM = 3200;
          }}
        }} else if (showcasePhase === 1) {{
          // Roll Gear & Spin Gyro
          kinematics.gearAngle = (kinematics.gearAngle + 120 * delta) % 360;
          document.getElementById('slider-gear').value = kinematics.gearAngle;
          if (showcaseTimer >= 2.5) {{
            showcasePhase = 2;
            showcaseTimer = 0;
          }}
        }} else if (showcasePhase === 2) {{
          // Axial Plunger In/Out
          kinematics.plungerY = Math.sin(showcaseTimer * 3.0) * 12.0 + 12.0;
          document.getElementById('slider-plunger').value = kinematics.plungerY;
          if (showcaseTimer >= 3.0) {{
            showcasePhase = 3;
            showcaseTimer = 0;
            kinematics.plungerY = 0;
          }}
        }} else if (showcasePhase === 3) {{
          // Waist 360 Rotation
          kinematics.waistAngle = (kinematics.waistAngle + 180 * delta) % 360;
          document.getElementById('slider-waist').value = kinematics.waistAngle;
          if (showcaseTimer >= 2.0) {{
            showcasePhase = 4;
            showcaseTimer = 0;
          }}
        }} else if (showcasePhase === 4) {{
          // Fold Hinge 90 -> 0
          kinematics.hingeAngle = Math.max(90 - showcaseTimer * 45, 0);
          document.getElementById('slider-hinge').value = kinematics.hingeAngle;
          if (showcaseTimer >= 2.0) {{
            showcasePhase = 0;
            showcaseTimer = 0;
          }}
        }}
        updateKinematicsVisuals();
      }}

      controls.update();
      renderer.render(scene, camera);
    }}

    // Initialize on DOM Ready
    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
"""
    return html

def main():
    print(f"Generating Interactive Fidget Clicks Visualizer: {OUTPUT_HTML}")
    html_content = generate_html()
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated {OUTPUT_HTML} ({len(html_content)} bytes)")

if __name__ == "__main__":
    main()
