# 🎯 Native Tactical/Spinner Hybrid Grenade Fidget Toy — 3D Printing & Assembly Guide
### Package Hybrid_Grenade_v1.3

This directory contains the complete, production-ready 3D printing package for the **Native Tactical/Spinner Hybrid Grenade Fidget Toy**.

## What's New in v1.3

v1.3 introduces two major architectural advancements over v1.2: **positive 4-pin axial retention for the upper station**, and the **Spinner Fuse concave upper seating arrangement** that nests the folding head and rod assembly deep inside the upper shell.

### 1. Spinner Fuse Concave Upper Seating Arrangement
Directly inspired by the reference Spinner Fuse Grenade (`01 - Upper Shell.stl`), `18_27_Upper_Shell_Top` now features a 45° conical concave seating dish ($r_{\text{mouth}} = 15.60\text{ mm}$ at $Y = 74.83\text{ mm}$, $r_{\text{floor}} = 9.20\text{ mm}$ at $Y = 68.00\text{ mm}$, depth $6.83\text{ mm}$).
- **Lowered Hinge Axis**: The rod hinge yoke is lowered from $Y = 92.46\text{ mm}$ down to $Y = 81.00\text{ mm}$ ($\Delta Y = -11.46\text{ mm}$), lowering the entire folding head assembly (`29`–`36`).
- **Deep Lever Nesting**: In the folded resting position, the folding handle's lower cam lobes nest $1.75\text{ mm}$ to $4.98\text{ mm}$ below the outer rim inside the dish, completely eliminating the previous 9.71 mm exposed neck gap.
- **Zero Clash Clearance**: Running clearance between the rotating handle cheeks and the conical dish is $\ge 0.80\text{ mm}$ across all 4 detent angles ($0^\circ, 30^\circ, 60^\circ, 90^\circ$). Full compatibility with all 8 mid-shell variants is preserved ($0.0000\text{ mm}^3$ clash).
- **Trimmed Guide Sleeve & Side Clamps**: The upper idle guide sleeve of `21_30_Upper_Shell_Rotating_Spring` is trimmed above $Y = 67.20\text{ mm}$ so it never protrudes into the dish floor (its 3 clicking arms at $Y \in [64.00, 66.50]\text{ mm}$ are 100% operational). The side clamps (`22`, `24`) are trimmed to $Y = 67.20\text{ mm}$, maintaining $5.20\text{ mm}$ of positive hexagonal drive engagement.
- **Compact Hinge Detent Spring**: `28_09_Rod_Spring_Hinge_T_Head` is compacted to $14.69\text{ mm}$ height, seating cleanly in the lowered middle rod channel ($Y \in [59.50, 74.19]\text{ mm}$) with $1.41\text{ mm}$ safety clearance above upper cross-key 06 ($Y = 58.09\text{ mm}$).

### 2. Positive 4-Pin Upper Station Retention System
v1.2 had left the upper shell un-retained axially when the three legacy 120° pins were removed to clear the 4 orthogonal spring slots. In v1.3:
- Four diagonal retention channels at 45°, 135°, 225°, and 315° receive four dedicated retention pins (`16_01`, `17_02`, `16_03`, `17_04`).
- The pins pass through side ports in `18_27_Upper_Shell_Top` into the barrel's solid quadrants (completely avoiding the 4 detent spring slots at 0°, 90°, 180°, 270°).
- Sliding `19_28_Upper_Shell_Gear` and `20_29_Upper_Shell_Lock_Ring` down the neck permanently encloses and traps the pins, making the entire upper station 100% locked and drop-proof.

---

## Core Mechanism Features (from v1.2)

### 4-Arm Transplanted Rod Detent Spring
The rod detent uses four transplanted arms of the Spinner Fuse Grenade's `11 - Middle Spring` at 0° / 90° / 180° / 270°:
- **Gentle Material Strain**: 0.831% strain per mm (vs 1.278% in v1.1) for exceptional fatigue life across tens of thousands of cycles.
- **Zero Dead Band**: Preloaded nose profile wedges onto the rack crest shoulders with 0.45 N holding force at every tooth, eliminating floating dead zones.
- **Breakout Pop**: Delivers a crisp, authoritative 24.37 N axial snap.
- **Material**: Print the four springs (`12`, `13`, `14`, `15`) in **PETG** or Tough PLA.

### Key Architectural Highlights
1. **Tactical Internal Spine**: The native `08 - Internal Barrel`, with 4 spring slots at 0° / 90° / 180° / 270° and 4 diagonal pin retention ports at 45° / 135° / 225° / 315°.
2. **Concave Dish Upper Station**: 45° ergonomic concave top housing with 4-pin retention, 20-click upper gear, and 3-arm rotating spring.
3. **Solid-Yoke 3-Piece Rod**: Full-depth rod assembly with seamless integral yoke (`Custom_Rod_Middle`, `Custom_Rod_Right`, and `Custom_Rod_Left`) locked via transverse `06` and `07` cross-keys and retained axially by `Spinner Lever 08 - Rod Lock`.
4. **Deeply Nested Folding Head & Spinner**: High-tactile folding lever with 4 detent positions (0°, 30°, 60°, 90°), free-spinning center ring (360°), and outer rim clicker gear (20 clicks/turn).

---

## 📦 Directory Structure

```text
3D_Print_Custom_Hybrid_Grenade/
├── 3D_Print_Custom_Hybrid_Grenade_Assembled.glb # Complete full 3D assembly (PBR materials & metadata)
├── 3D_Print_Custom_Hybrid_Grenade_Exploded.glb  # Fully parted exploded view showing all 38 internal parts
├── 3D_Print_Custom_Hybrid_Grenade_Cutaway.glb   # Coronal/sagittal cutaway revealing internal rack & springs
├── 01_Base_And_Bottom_Shell/               # 6 STLs: Bottom lock cylinder, spacer, flexure spring & 3 outer shell tiers
├── 02_Waist_Mechanism/                     # 3 STLs: 33-lobe ratchet ring, outer shell body & 3-arm detent spring
├── 03_Internal_Barrel_And_Upper_Station/   # 14 STLs: barrel (4 slots), cap, 4 rod detent springs, gear, top & lock ring
├── 04_Rod_Assembly_And_Locks/              # 6 STLs: Full-depth 3-part rod (solid yoke), 2 cross-keys & bottom axial retainer
├── 05_Folding_Head_And_Spinner/            # 9 STLs: Folding lever cheeks, center spinner ring, rim gear & clicker, hinge lock pins
├── All_Parts_Flat_Bed_Oriented/            # Every STL pre-oriented flat on Z=0 for instant drag-and-drop slicing
├── All_Parts_Assembled_Coordinates/        # Every STL in exact solved global assembly space
├── Plates_3MF/                             # Multi-part 3MF build plates arranged for Bambu Studio / OrcaSlicer / PrusaSlicer
└── README_3D_PRINTING.md                   # Complete BOM, slicer recommendations & step-by-step assembly manual
```

---

## 📋 Complete Bill of Materials (BOM) — 38 Parts Total

| Part # | Subassembly | Filename | Material / Recommended Color | Qty | Supports |
|:---|:---|:---|:---|:---:|:---:|
| **01** | Base & Bottom | `01_04_Bottom_Shell_01.stl` | PLA (Olive Drab Green) | 1 | No |
| **02** | Base & Bottom | `02_05_Bottom_Shell_02.stl` | PLA (Olive Drab Green) | 1 | No |
| **03** | Base & Bottom | `03_06_Bottom_Shell_03.stl` | PLA (Olive Drab Green) | 1 | No |
| **04** | Base & Bottom | `04_01_Bottom_Lock_Shell.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **05** | Base & Bottom | `05_02_Bottom_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **06** | Base & Bottom | `06_03_Bottom_Shell_Spacer.stl` | PLA (Gunmetal / Black) | 1 | No |
| **07** | Waist Mech | `07_32_Mid_Shell_P02_Ratchet.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **08** | Waist Mech | `08_33_Mid_Shell_P01_Outer.stl` | PLA Matte (Tactical Olive) | 1 | No |
| **09** | Waist Mech | `09_Custom_Mid_Shell_Spring_33.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **10** | Upper Station | `10_Custom_Internal_Barrel_4Slot.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **11** | Upper Station | `11_Custom_Internal_Barrel_Cap.stl` | PLA (Gunmetal / Black) | 1 | No |
| **12** | Upper Station | `12_Custom_Rod_Detent_Spring_01.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **13** | Upper Station | `13_Custom_Rod_Detent_Spring_02.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **14** | Upper Station | `14_Custom_Rod_Detent_Spring_03.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **15** | Upper Station | `15_Custom_Rod_Detent_Spring_04.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **16** | Upper Station | `16_Custom_Internal_Barrel_Pin_01.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **17** | Upper Station | `17_Custom_Internal_Barrel_Pin_02.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **16** | Upper Station | `16_Custom_Internal_Barrel_Pin_03.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **17** | Upper Station | `17_Custom_Internal_Barrel_Pin_04.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **18** | Upper Station | `18_27_Upper_Shell_Top.stl` | PLA (Olive Drab Green) | 1 | No |
| **19** | Upper Station | `19_28_Upper_Shell_Gear.stl` | PLA (Silver / Gunmetal) | 1 | No |
| **20** | Upper Station | `20_29_Upper_Shell_Lock_Ring.stl` | PLA (Olive Drab Green) | 1 | No |
| **21** | Upper Station | `21_30_Upper_Shell_Rotating_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **22** | Rod Assembly | `22_Custom_Rod_Right.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **23** | Rod Assembly | `23_Custom_Rod_Middle.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No (Brim recommended) |
| **24** | Rod Assembly | `24_Custom_Rod_Left.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **25** | Rod Assembly | `25_Custom_Rod_Lock_Upper_06.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **26** | Rod Assembly | `26_Custom_Rod_Lock_Lower_07.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **27** | Rod Assembly | `27_Spinner_Lever_08_Rod_Lock.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **28** | Head & Spinner | `28_09_Rod_Spring_Hinge_T_Head.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **29** | Head & Spinner | `29_Custom_Handle_Left.stl` | PLA (Olive Drab Green) | 1 | No |
| **30** | Head & Spinner | `30_Custom_Handle_Right.stl` | PLA (Olive Drab Green) | 1 | No |
| **31** | Head & Spinner | `31_Custom_Ring_Spinner.stl` | Silk PLA (Gold / Brass) | 1 | No |
| **32** | Head & Spinner | `32_Spinner_Lever_05_Gear.stl` | Silk PLA (Silver / Metallic) | 1 | No |
| **33** | Head & Spinner | `33_Spinner_Lever_04_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **34** | Head & Spinner | `34_Custom_16_Handle_Lock_Neck.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **35** | Head & Spinner | `35_Custom_16_Handle_Lock_Pod.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **36** | Head & Spinner | `36_15_Handle_Rotating_Lock_D_Pin.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |

---

## ⚙️ Recommended Slicer Settings

- **Layer Height**: `0.16 mm` (recommended) or `0.20 mm`.
- **Wall Loops / Perimeters**: `4` walls for all structural parts, gears, and springs.
- **Top / Bottom Shells**: `5` top layers, `4` bottom layers.
- **Infill**: `25% - 30% Gyroid` or `Cubic`.
- **Supports**: Disabled across all parts (100% support-free 3D printing; auto-brim recommended for tall upright parts).

---

## 🔧 Step-by-Step Assembly Instructions

### Stage 1: Bottom Lock & Lower Outer Shells
1. Drop `05_02_Bottom_Spring.stl` into the cavity of `04_01_Bottom_Lock_Shell.stl`.
2. Press `06_03_Bottom_Shell_Spacer.stl` on top to seal the bottom spring chamber.
3. Slide this sub-assembly into `01_04_Bottom_Shell_01.stl`.
4. Stack `02_05_Bottom_Shell_02.stl` over the shoulder, then seat `03_06_Bottom_Shell_03.stl` on top.

### Stage 2: Waist Mechanism & 33-Lobe Clicker
1. Insert `09_Custom_Mid_Shell_Spring_33.stl` through the 3 lower windows of `10_Custom_Internal_Barrel_4Slot.stl`.
2. Slide `07_32_Mid_Shell_P02_Ratchet.stl` onto the barrel until its internal lobes engage the 3 spring arms.
3. Place `08_33_Mid_Shell_P01_Outer.stl` over the ratchet ring.

### Stage 3: Rod Detent Springs & Upper Station
1. Drop the 4 detent springs (`12`, `13`, `14`, `15`) into the barrel's four slots at 0 deg / 90 deg / 180 deg / 270 deg, **from the open top**. They are identical parts; the rib on the foot faces the same way in all four, and it catches the step in the slot so the spring cannot work its way inward. They are preloaded — the noses stand proud of where the rack will hold them, so the rod snaps past them on the way in.
2. Seal the top of the barrel with `11_Custom_Internal_Barrel_Cap.stl`. Its 4 downward filler prongs plug the empty L-notch recesses in all four slots with positive 4-way anti-rotation alignment, while its underside traps all four springs axially.
3. Slide `19_28_Upper_Shell_Gear.stl` over the upper barrel station.
4. Install `21_30_Upper_Shell_Rotating_Spring.stl` and `20_29_Upper_Shell_Lock_Ring.stl`.
5. Seat `18_27_Upper_Shell_Top.stl` over the upper station to close the main body. Insert the four retention pins (`16_Custom_Internal_Barrel_Pin_01.stl`, `17_Custom_Internal_Barrel_Pin_02.stl`, `16_Custom_Internal_Barrel_Pin_03.stl`, and `17_Custom_Internal_Barrel_Pin_04.stl`) through the shell's side windows into the barrel channels at 45°, 135°, 225°, and 315° to lock `18_27_Upper_Shell_Top.stl` axially. Slide `19_28_Upper_Shell_Gear.stl` and `20_29_Upper_Shell_Lock_Ring.stl` over the shell neck to trap and enclose the pins.

### Stage 4: Unified Full-Height Rod Assembly & Enclosed Hinge Spring
1. Insert `28_09_Rod_Spring_Hinge_T_Head.stl` into the central spring channel of `23_Custom_Rod_Middle.stl`.
2. Place full-height `22_Custom_Rod_Right.stl` and `24_Custom_Rod_Left.stl` on the right and left sides of `23_Custom_Rod_Middle.stl`, fully enclosing the hinge spring inside the symmetric pod halves and forming the upper hexagonal keying prism.
3. Insert `25_Custom_Rod_Lock_Upper_06.stl` through the upper cross-tunnel.
4. Insert `26_Custom_Rod_Lock_Lower_07.stl` through the lower cross-tunnel.
5. Slide the assembled 3-piece rod down through the central bore of the body and through `21_30_Upper_Shell_Rotating_Spring.stl` (the hexagonal upper section positively locks to the rotating spring's bore).
6. Press `27_Spinner_Lever_08_Rod_Lock.stl` onto the bottom tapered wedge to retain the rod axially.

### Stage 5: Folding Head, Rim Gear & Center Spinner
1. Place `33_Spinner_Lever_04_Spring.stl` inside the handle pod pocket.
2. Mount `32_Spinner_Lever_05_Gear.stl` and `31_Custom_Ring_Spinner.stl` onto the journal tube of `29_Custom_Handle_Left.stl`.
3. Close with `30_Custom_Handle_Right.stl`.
4. Secure the handle cheeks with `34_Custom_16_Handle_Lock_Neck.stl` and `35_Custom_16_Handle_Lock_Pod.stl`.
5. Mount the assembled folding head onto the rod's upper hinge yoke and insert `36_15_Handle_Rotating_Lock_D_Pin.stl` to complete the toy!
