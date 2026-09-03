# 🎯 Native Tactical/Spinner Hybrid Grenade Fidget Toy — 3D Printing & Assembly Guide
### Package Hybrid_Grenade_v1.2

This directory contains the complete, production-ready 3D printing package for the **Native Tactical/Spinner Hybrid Grenade Fidget Toy**.

## What changed in v1.2

One change, to the **up/down click of the central rod** — and one thing it costs, recorded plainly below. Everything else — the 33-click waist, the 20-click rim gear, the 4-position fold, the spinner ring, all 8 mid shell options — is untouched and measures identically to v1.1.

### The rod detent is now four arms of `11 - Middle Spring`

The reference is the Spinner Fuse Grenade's `11 - Middle Spring`. Measured, what makes it good is **not** force — it peaks at 2.00 N, well under v1.1's 5.53 N — but how gently it works its material: **1.207 N/mm on 0.714% strain per millimetre of travel**, against the v1.1 leaf's 2.951 N/mm on 1.278%. Over the tens of thousands of clicks a fidget sees, that is the difference between a flexure that lasts and one that cracks.

That part is a closed C, 34.81 × 32.63 × 3.00 mm, and it cannot go in whole — the rod is inserted full depth through the barrel and there is nowhere for a closed C to sit. So it is **cut in half at the middle** and one arm is transplanted: the reference's own outline, trimmed of the bridge and of the shell tab, mapped into the slot at **0.53 radial / 0.74 axial** scale. It keeps the shape that matters — the long slanted leg, the fold out to an outer rail, the U-turn, and the hook back inward to the nose — and only the two ends are ours: a rigid foot where `11` had its bridge, carrying the **extended notch**, and a nose cut for this rod's rack.

| | v1.1 | v1.2 | `11 - Middle Spring` |
|---|---|---|---|
| architecture | 3 short leaves at 90/210/330 | **4 transplanted arms at 0/90/180/270** | 2 arms on one C |
| rate per arm | 2.951 N/mm | **0.631 N/mm** | 1.207 N/mm |
| strain per mm | 1.278 % | **0.831 %** | 0.714 % |
| **strain per click** | 1.11 % | **1.12 %** | 0.59 % |
| peak force | 5.53 N | **2.26 N** | 2.00 N |
| held at every click | 0.00 N | **0.45 N** | 0.00 N |
| dead band | 12% of pitch | **0%** | 3% |

In v1.1 the nose sat 0.10 mm *clear* of the rack at every click, so the force fell to exactly zero across the middle 12% of each tooth — nothing held the rod between clicks, and since 0.10 mm is inside normal print variation a given print could have had no click at all. That is gone. The fix is not obvious and is worth stating: the rack's groove is only **2.58 mm wide at crest level**, and a tongue whose flanks match the rack's is 2.618 mm wide there *whatever* tip radius it uses — so it can never be pushed deeper than a perfect fit, and a perfect fit carries no preload. This nose is deliberately **wider** than the groove and wedges down onto the crest shoulders instead, which is what gives it 0.45 N to hold with.

The rod's rack is a **turned ring**, the same at every azimuth, so all four arms bite equally. Print the springs in **PETG**, not PLA.

### What it cost: the barrel's other slots, the pins and the cap's keys

The barrel now carries **exactly four slots and nothing else**. Three sets of features had to go to get there:

- **The three pin channels at 30° / 150° / 270° are filled**, and parts `09/10/11 - Internal Barrel Pin` leave the kit. Four slots 90° apart cannot fit around three channels 120° apart — the nearest miss is 15°, and clearing one needs r ≥ 17.4 mm against the barrel's 16.22.
- **The three stock follower slots at 90° / 210° / 330° are filled too.** At azimuth 90 a new slot lands on an old one, and leaving it gave a hybrid of the two profiles — deeper and wider above r 12.30 than the new section, shallower below.
- **The cap loses all three keys**, because they keyed into those same slots. `11_Custom_Internal_Barrel_Cap` is the plain lobed disc that remains; it still presses onto the barrel's top face and its underside at y 63.205 is what holds all four springs down. Its rotational lock is gone — measured, the rim alone does not replace it.

> **The upper station is no longer retained axially.** Those pins were the only thing holding `27 - Upper Shell Top` down on the barrel — lift it and it now comes straight off, meeting zero interference. Rotation is unaffected: the barrel keys the shell with its own lobes. A replacement retention is still to be designed; do not print this package expecting a finished toy.

The slots keep the stock two-step section — a neck with a one-sided widening that the notch rides in — 0.30 mm wider than stock so the spring can be the reference's own 3.00 mm thickness, and they stop at r 12.30 instead of 14.55. They have to: above y 54 the barrel is a **narrow** cylinder, 13.95 in the troughs and 14.70 at 0° and 180°, with three lobes to 17.10 at 90° / 210° / 330° that were the only reason the stock slots could be as deep as they were. Filling and cutting together take the barrel from 19365 mm³ to 19022 mm³, a net 1.8%, and the thinnest wall left outboard of any slot is **1.50 mm** — thicker than the 0.49 mm the stock barrel already carries elsewhere. Nothing is cut through to the outside, so the journal the mid shell rides on is untouched.

**v1.1 and v1.2 barrels are not interchangeable**, and neither are the caps.

### Key Architectural Highlights
1. **Tactical Internal Spine**: The native `08 - Internal Barrel`, its three pin channels filled and four spring slots cut at 0° / 90° / 180° / 270°, carrying the 4 preloaded springs (`12/13/14/15`) that ride the rod's rack and are the whole of the axial click.
2. **Original Tactical Upper Station**: Retains `28 - Upper Shell Gear`, `27 - Upper Shell Top`, `29 - Lock Ring`, and `30 - Rotating Spring`.
3. **Solid-Yoke 3-Piece Rod**: Full-depth rod assembly with seamless integral yoke (`Custom_Rod_Middle`, `Custom_Rod_Right`, and `Custom_Rod_Left`) locked via transverse `06` and `07` cross-keys and retained axially by `Spinner Lever 08 - Rod Lock`. (No upper wedge lock and no unnecessary keyway holes).
4. **Folding Head & Spinner**: High-tactile folding lever mechanism with 4 detent positions (0°, 30°, 60°, 90°), free-spinning center ring (360°), and outer rim clicker gear (20 clicks/turn).

---

## 📦 Directory Structure

```text
3D_Print_Custom_Hybrid_Grenade/
├── 3D_Print_Custom_Hybrid_Grenade_Assembled.glb # Complete full 3D assembly (PBR materials & metadata)
├── 3D_Print_Custom_Hybrid_Grenade_Exploded.glb  # Fully parted exploded view showing all 36 internal parts
├── 3D_Print_Custom_Hybrid_Grenade_Cutaway.glb   # Coronal/sagittal cutaway revealing internal rack & springs
├── 01_Base_And_Bottom_Shell/               # 6 STLs: Bottom lock cylinder, spacer, flexure spring & 3 outer shell tiers
├── 02_Waist_Mechanism/                     # 3 STLs: 33-lobe ratchet ring, outer shell body & 3-arm detent spring
├── 03_Internal_Barrel_And_Upper_Station/   # 12 STLs: barrel (4 slots), cap, 4 rod detent springs, gear, top & lock ring
├── 04_Rod_Assembly_And_Locks/              # 6 STLs: Full-depth 3-part rod (solid yoke), 2 cross-keys & bottom axial retainer
├── 05_Folding_Head_And_Spinner/            # 9 STLs: Folding lever cheeks, center spinner ring, rim gear & clicker, hinge lock pins
├── All_Parts_Flat_Bed_Oriented/            # Every STL pre-oriented flat on Z=0 for instant drag-and-drop slicing
├── All_Parts_Assembled_Coordinates/        # Every STL in exact solved global assembly space
├── Plates_3MF/                             # Multi-part 3MF build plates arranged for Bambu Studio / OrcaSlicer / PrusaSlicer
└── README_3D_PRINTING.md                   # Complete BOM, slicer recommendations & step-by-step assembly manual
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
| **07** | Waist Mech | `07_32_Mid_Shell_P02_Ratchet.stl` | PLA (Olive Drab Green) | 1 | No |
| **08** | Waist Mech | `08_33_Mid_Shell_P01_Outer.stl` | PLA (Olive Drab Green) | 1 | No |
| **09** | Waist Mech | `09_Custom_Mid_Shell_Spring_33.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **10** | Upper Station | `10_Custom_Internal_Barrel_4Slot.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **11** | Upper Station | `11_Custom_Internal_Barrel_Cap.stl` | PLA (Gunmetal / Black) | 1 | No |
| **12** | Upper Station | `12_Custom_Rod_Detent_Spring_01.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **13** | Upper Station | `13_Custom_Rod_Detent_Spring_02.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **14** | Upper Station | `14_Custom_Rod_Detent_Spring_03.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **15** | Upper Station | `15_Custom_Rod_Detent_Spring_04.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **16** | Upper Station | `16_Custom_Internal_Barrel_Pin_01.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **17** | Upper Station | `17_Custom_Internal_Barrel_Pin_02.stl` | PLA / PETG (Gunmetal / Black) | 1 | No |
| **18** | Upper Station | `18_27_Upper_Shell_Top.stl` | PLA (Olive Drab Green) | 1 | No |
| **19** | Upper Station | `19_28_Upper_Shell_Gear.stl` | PLA (Silver / Gunmetal) | 1 | No |
| **20** | Upper Station | `20_29_Upper_Shell_Lock_Ring.stl` | PLA (Olive Drab Green) | 1 | No |
| **21** | Upper Station | `21_30_Upper_Shell_Rotating_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **22** | Rod Assembly | `22_Custom_Rod_Right.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **23** | Rod Assembly | `23_Custom_Rod_Middle.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | Minimal (under yoke) |
| **24** | Rod Assembly | `24_Custom_Rod_Left.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **25** | Rod Assembly | `25_Custom_Rod_Lock_Upper_06.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **26** | Rod Assembly | `26_Custom_Rod_Lock_Lower_07.stl` | PETG / PLA+ (Safety Orange / Red) | 1 | No |
| **27** | Rod Assembly | `27_Spinner_Lever_08_Rod_Lock.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **28** | Head & Spinner | `28_09_Rod_Spring_Hinge.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
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
- **Supports**: Disabled on every part but one (only minimal support under the central rod's hinge yoke overhang).

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
2. Seal the top of the barrel with `11_Custom_Internal_Barrel_Cap.stl`. It is a plain disc with no keys, so it drops on either way round; its underside traps all four springs.
3. Slide `19_28_Upper_Shell_Gear.stl` over the upper barrel station.
4. Install `21_30_Upper_Shell_Rotating_Spring.stl` and `20_29_Upper_Shell_Lock_Ring.stl`.
5. Seat `18_27_Upper_Shell_Top.stl` over the upper station to close the main body. Insert the two retention pins (`16_Custom_Internal_Barrel_Pin_01.stl` and `17_Custom_Internal_Barrel_Pin_02.stl`) through the shell's side windows into the barrel channels at 30° and 150° to lock `18_27_Upper_Shell_Top.stl` axially. Slide `19_28_Upper_Shell_Gear.stl` and `20_29_Upper_Shell_Lock_Ring.stl` over the shell neck to trap and enclose the pins.

### Stage 4: Unified Full-Height Rod Assembly & Enclosed Hinge Spring
1. Insert narrowed `28_09_Rod_Spring_Hinge.stl` into the central spring channel of `23_Custom_Rod_Middle.stl`.
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
