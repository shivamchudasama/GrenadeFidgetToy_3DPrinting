# 🎯 Native Tactical/Spinner Hybrid Grenade Fidget Toy — 3D Printing & Assembly Guide

This directory contains the complete, production-ready 3D printing package for the **Native Tactical/Spinner Hybrid Grenade Fidget Toy** featuring **8 interchangeable mid shell design variants**.

### Key Architectural Highlights
1. **Original Tactical Internal Spine**: Retains the native `08 - Internal Barrel` with its 3 internal pin channels (`09/10/11 Pins`) and 3 leaf springs (`12/13/14 Springs`) providing crisp linear clicks against the rod.
2. **Original Tactical Upper Station**: Retains `28 - Upper Shell Gear`, `27 - Upper Shell Top`, `29 - Lock Ring`, and `30 - Rotating Spring`.
3. **Solid-Yoke 3-Piece Rod**: Full-depth rod assembly with seamless integral yoke (`Custom_Rod_Middle`, `Custom_Rod_Right`, and `Custom_Rod_Left`) locked via transverse `06` and `07` cross-keys and retained axially by `Spinner Lever 08 - Rod Lock`. (No upper wedge lock and no unnecessary keyway holes).
4. **Folding Head & Spinner**: High-tactile folding lever mechanism with 4 detent positions (0°, 30°, 60°, 90°), free-spinning center ring (360°), and outer rim clicker gear (20 clicks/turn).
5. **8 Interchangeable Mid Shell Designs**: 100% verified identical **34.80 mm total height** and **40.00 mm mating interface diameters** for seamless plug-and-play swapping.

---

## 🌐 Interactive 3D Web Studio

Open [`Interactive_Shell_Variants_Viewer.html`](./Interactive_Shell_Variants_Viewer.html) directly in any modern browser to:
- Realtime switch between all **8 Mid Shell Variants** in 3D.
- Toggle between **🚀 Assembled**, **🔍 CAD Cutaway**, and **💥 Exploded** views.
- Inspect 36 individual parts, view verified dimensions, toggle wireframes, and explore camera presets (Isometric, Front, Side, Top, Waist Close-up).

---

## 📐 Mid Shell Interchangeability & Dimensional Verification

Every mid shell design was measured to ensure complete mechanical compatibility with the waist mechanism and adjacent body shells:

| Shell Variant | Architecture | Total Height ($Z$) | Base / Ledge Dia | Max Grip Outer Dia | Part Files |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Baseline (Standard)** | 2-Piece (Outer + Inner) | **34.80 mm** | **40.00 mm** | 41.60 mm | `08_33_Mid_Shell_P01_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **01. AeroFlow** | 1-Piece Monolithic Solid | **34.80 mm** | **40.00 mm** | 41.68 mm | `08_Mid_Shell_Option_01_AeroFlow.stl` |
| **02. Vector Chevron** | 1-Piece Monolithic Solid | **34.80 mm** | **40.00 mm** | 41.52 mm | `08_Mid_Shell_Option_02_Vector_Chevron.stl` |
| **03. Orbit Pods** | 1-Piece Monolithic Solid | **34.80 mm** | **40.00 mm** | 41.55 mm | `08_Mid_Shell_Option_03_Orbit.stl` |
| **04. Ergo Scoops** | 1-Piece Monolithic Solid | **34.80 mm** | **40.00 mm** | 41.84 mm | `08_Mid_Shell_Option_04_Ergo_Scoops.stl` |
| **05. Contour Twist** | 2-Piece Dual-Color | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 43.00 mm (tri-lobed) | `08_Mid_Shell_Option_05_Contour_Twist_Outer.stl`<br>`07_Mid_Shell_Option_05_Contour_Twist_Inner.stl` |
| **06. Hex Tactical** | 1-Piece Monolithic Solid | **34.80 mm** | **40.00 mm** | 42.12 mm | `08_Mid_Shell_Option_06_Hex_Tactical.stl` |
| **07. Classic Solid Tactical** | 1-Piece Monolithic Solid | **34.80 mm** | **40.00 mm** | 41.95 mm | `08_Mid_Shell_Option_07_Classic_Solid_Tactical.stl` |

*Note: All variants mate with the exact same 33-click waist detent leaf spring (`09_Custom_Mid_Shell_Spring_33.stl`).*

---

## 📦 Directory Structure & 3D Models

```text
Hybrid_Grenade_v1.1/
├── Interactive_Shell_Variants_Viewer.html           # Realtime 3D Web Studio (All 8 Variants in 3D)
│
├── 3D_Print_Custom_Hybrid_Grenade_Assembled.glb     # Baseline full assembly
├── 3D_Print_Custom_Hybrid_Grenade_Cutaway.glb       # Baseline cutaway
├── 3D_Print_Custom_Hybrid_Grenade_Exploded.glb      # Baseline exploded
│
├── 3D_Print_Custom_Hybrid_Grenade_01_AeroFlow_Assembled.glb
├── 3D_Print_Custom_Hybrid_Grenade_02_Vector_Chevron_Assembled.glb
├── 3D_Print_Custom_Hybrid_Grenade_03_Orbit_Assembled.glb
├── 3D_Print_Custom_Hybrid_Grenade_04_Ergo_Scoops_Assembled.glb
├── 3D_Print_Custom_Hybrid_Grenade_05_Contour_Twist_Assembled.glb
├── 3D_Print_Custom_Hybrid_Grenade_06_Hex_Tactical_Assembled.glb
├── 3D_Print_Custom_Hybrid_Grenade_07_Classic_Solid_Tactical_Assembled.glb
│
├── 01_Base_And_Bottom_Shell/               # 6 STLs: Bottom lock cylinder, spacer, spring & 3 outer shells
├── 02_Waist_Mechanism/                     # 3 STLs: Baseline 33-lobe ratchet, outer shell & leaf spring
│   └── Mid_Shell_Options/                  # STLs for all 7 alternate mid shell options (01-07) & GLB 2-color assembly
├── 03_Internal_Barrel_And_Upper_Station/   # 12 STLs: Original Tactical barrel, cap, pins, springs, gear & lock ring
├── 04_Rod_Assembly_And_Locks/              # 6 STLs: Full-depth 3-part rod (solid yoke), cross-keys & retainer
├── 05_Folding_Head_And_Spinner/            # 9 STLs: Folding lever cheeks, center ring, rim gear, clicker & pins
├── All_Parts_Flat_Bed_Oriented/            # Individual STLs oriented flat on Z=0 (including Mid_Shell_Options)
├── All_Parts_Assembled_Coordinates/        # Individual STLs in global solved assembly space (including Mid_Shell_Options)
├── Plates_3MF/                             # Multi-part 3MF project plates for OrcaSlicer / Bambu Studio
└── README_3D_PRINTING.md                   # Complete BOM & Assembly Manual
```

---

## 📋 Complete Bill of Materials (BOM) — 36 Parts Total

| Part # | Subassembly | Filename | Material / Recommended Color | Qty | Supports |
|:---|:---|:---|:---|:---:|:---:|
| **01** | Base & Bottom | `01_04_Bottom_Shell_01.stl` | PLA (Olive Drab Green) | 1 | No |
| **02** | Base & Bottom | `02_05_Bottom_Shell_02.stl` | PLA (Olive Drab Green) | 1 | No |
| **03** | Base & Bottom | `03_06_Bottom_Shell_03.stl` | PLA (Olive Drab Green) | 1 | No |
| **04** | Base & Bottom | `04_01_Bottom_Lock_Shell.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **05** | Base & Bottom | `05_02_Bottom_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **06** | Base & Bottom | `06_03_Bottom_Shell_Spacer.stl` | PLA (Gunmetal / Black) | 1 | No |
| **07** | Waist Mech | `07_32_Mid_Shell_P02_Ratchet.stl` *(or Option 05 Inner)* | PLA (Olive Drab Accent) | 1 | No |
| **08** | Waist Mech | `08_33_Mid_Shell_P01_Outer.stl` *(or Options 01–07)* | PLA (Olive Drab Green) | 1 | No |
| **09** | Waist Mech | `09_Custom_Mid_Shell_Spring_33.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **10** | Upper Station | `10_08_Internal_Barrel.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **11** | Upper Station | `11_07_Internal_Barrel_Cap.stl` | PLA (Gunmetal / Black) | 1 | No |
| **12** | Upper Station | `12_09_Internal_Barrel_Pin_01.stl` | PLA+ / Tough PLA (Crimson Red / Black) | 1 | No |
| **13** | Upper Station | `13_10_Internal_Barrel_Pin_02.stl` | PLA+ / Tough PLA (Crimson Red / Black) | 1 | No |
| **14** | Upper Station | `14_11_Internal_Barrel_Pin_03.stl` | PLA+ / Tough PLA (Crimson Red / Black) | 1 | No |
| **15** | Upper Station | `15_12_Internal_Barrel_Spring_01.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **16** | Upper Station | `16_13_Internal_Barrel_Spring_02.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **17** | Upper Station | `17_14_Internal_Barrel_Spring_03.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **18** | Upper Station | `18_27_Upper_Shell_Top.stl` | PLA (Olive Drab Green) | 1 | No |
| **19** | Upper Station | `19_28_Upper_Shell_Gear.stl` | PLA (Silver / Gunmetal) | 1 | No |
| **20** | Upper Station | `20_29_Upper_Shell_Lock_Ring.stl` | PLA (Olive Drab Accent) | 1 | No |
| **21** | Upper Station | `21_30_Upper_Shell_Rotating_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **22** | Rod Assembly | `22_Custom_Rod_Right.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **23** | Rod Assembly | `23_Custom_Rod_Middle.stl` | PLA+ / PETG (Charcoal Black) | 1 | Minimal (under yoke) |
| **24** | Rod Assembly | `24_Custom_Rod_Left.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **25** | Rod Assembly | `25_Custom_Rod_Lock_Upper_06.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **26** | Rod Assembly | `26_Custom_Rod_Lock_Lower_07.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **27** | Rod Assembly | `27_Spinner_Lever_08_Rod_Lock.stl` | PLA+ / PETG (Gunmetal Disc) | 1 | No |
| **28** | Head & Spinner | `28_09_Rod_Spring_Hinge.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **29** | Head & Spinner | `29_Custom_Handle_Left.stl` | PLA (Olive Drab Green) | 1 | No |
| **30** | Head & Spinner | `30_Custom_Handle_Right.stl` | PLA (Olive Drab Green) | 1 | No |
| **31** | Head & Spinner | `31_Custom_Ring_Spinner.stl` | Silk PLA (Gold / Brass) | 1 | No |
| **32** | Head & Spinner | `32_Spinner_Lever_05_Gear.stl` | Silk PLA (Silver Chrome) | 1 | No |
| **33** | Head & Spinner | `33_Spinner_Lever_04_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **34** | Head & Spinner | `34_Custom_16_Handle_Lock_Neck.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **35** | Head & Spinner | `35_Custom_16_Handle_Lock_Pod.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **36** | Head & Spinner | `36_15_Handle_Rotating_Lock_D_Pin.stl` | PETG / PLA+ (Crimson Red) | 1 | No |

---

## ⚙️ Recommended Slicer Settings

- **Layer Height**: `0.16 mm` (recommended) or `0.20 mm`.
- **Wall Loops / Perimeters**: `4` walls for all structural parts, gears, and flexure leaf springs.
- **Top / Bottom Shells**: `5` top layers, `4` bottom layers.
- **Infill**: `25% - 30% Gyroid` or `Cubic`.
- **Supports**: Disabled on 35/36 parts (only minimal support needed under the central rod hinge yoke).

---

## 🔧 Step-by-Step Assembly Instructions

### Stage 1: Bottom Lock & Lower Outer Shells
1. Drop `05_02_Bottom_Spring.stl` into the cavity of `04_01_Bottom_Lock_Shell.stl`.
2. Press `06_03_Bottom_Shell_Spacer.stl` on top to seal the bottom spring chamber.
3. Slide this sub-assembly into `01_04_Bottom_Shell_01.stl`.
4. Stack `02_05_Bottom_Shell_02.stl` over the shoulder, then seat `03_06_Bottom_Shell_03.stl` on top.

### Stage 2: Waist Mechanism & Mid Shell Installation
1. Insert `09_Custom_Mid_Shell_Spring_33.stl` through the 3 lower windows of `10_08_Internal_Barrel.stl`.
2. **Choose your mid shell option**:
   - **Option A (Baseline)**: Slide `07_32_Mid_Shell_P02_Ratchet.stl` onto the barrel to engage the 3 spring arms, then press `08_33_Mid_Shell_P01_Outer.stl` over it.
   - **Option B (Options 01–04, 06, 07 Monolithic Shells)**: Directly slide your chosen 1-piece monolithic mid shell (e.g. `08_Mid_Shell_Option_06_Hex_Tactical.stl` or `Option_01_AeroFlow.stl`) onto the barrel over the spring.
   - **Option C (Option 05 Contour Twist)**: Slide `07_Mid_Shell_Option_05_Contour_Twist_Inner.stl` onto the barrel, then slide `08_Mid_Shell_Option_05_Contour_Twist_Outer.stl` over it.

### Stage 3: Original Internal Barrel Clicking Pins & Upper Station
1. Insert the 3 pins (`12_09`, `13_10`, `14_11`) into the vertical pin slots of `10_08_Internal_Barrel.stl`.
2. Seat the 3 leaf springs (`15_12`, `16_13`, `17_14`) behind the pins.
3. Seal the top of the barrel with `11_07_Internal_Barrel_Cap.stl`.
4. Slide `19_28_Upper_Shell_Gear.stl` over the upper barrel station.
5. Install `21_30_Upper_Shell_Rotating_Spring.stl` and `20_29_Upper_Shell_Lock_Ring.stl`.
6. Seat `18_27_Upper_Shell_Top.stl` over the upper station to close the main body.

### Stage 4: Three-Part Full-Depth Rod Assembly
1. Place `22_Custom_Rod_Right.stl` and `24_Custom_Rod_Left.stl` on either side of `23_Custom_Rod_Middle.stl`.
2. Insert `25_Custom_Rod_Lock_Upper_06.stl` through the upper cross-tunnel.
3. Insert `26_Custom_Rod_Lock_Lower_07.stl` through the lower cross-tunnel.
4. Slide the locked 3-part rod down through the central square bore of the body.
5. Press `27_Spinner_Lever_08_Rod_Lock.stl` onto the bottom tapered wedge to retain the rod axially.

### Stage 5: Folding Head, Rim Gear & Center Spinner
1. Insert `28_09_Rod_Spring_Hinge.stl` into the yoke pocket between the upper rod cheeks.
2. Place `33_Spinner_Lever_04_Spring.stl` inside the handle pod pocket.
3. Mount `32_Spinner_Lever_05_Gear.stl` and `31_Custom_Ring_Spinner.stl` onto the journal tube of `29_Custom_Handle_Left.stl`.
4. Close with `30_Custom_Handle_Right.stl`.
5. Secure the handle cheeks with `34_Custom_16_Handle_Lock_Neck.stl` and `35_Custom_16_Handle_Lock_Pod.stl`.
6. Mount the assembled folding head onto the rod's upper hinge yoke and insert `36_15_Handle_Rotating_Lock_D_Pin.stl` to complete the toy!
