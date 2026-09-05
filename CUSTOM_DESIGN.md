# CUSTOM_DESIGN.md — the custom hybrid build

`DESIGN.md` describes the **upstream** mechanisms; this file describes **ours**.
Same evidence tags: **[M]** measured, **[D]** derived, **[?]** informed guess.

Production package located in: [`Hybrid_Grenade_v1.3/`](file:///d:/GIT_Repo/GrenadeFidgetToy_3DPrinting/Hybrid_Grenade_v1.3/) (BOM & Assembly Guide: [`README_3D_PRINTING.md`](file:///d:/GIT_Repo/GrenadeFidgetToy_3DPrinting/Hybrid_Grenade_v1.3/README_3D_PRINTING.md)).
**Versioning.** `Hybrid_Grenade_v1.1/` and `Hybrid_Grenade_v1.2/` are frozen: they are the record of what has already been printed, and the build scripts refuse to write into them (`tools/package_paths.py`, `guard()`). Work happens in the folder named by `PACKAGE_NAME`; to start a new one, bump that constant, copy the previous folder forward, and rebuild. v1.3 adds:
1. **Positive 4-Pin Upper Shell Retention**: four diagonal retention pins at 45° / 135° / 225° / 315° locking `18_27_Upper_Shell_Top` to the barrel, enclosed by gear and lock ring.
2. **Spinner Fuse Concave Upper Seating**: 45° conical concave dish ($6.83\text{ mm}$ deep) on `18_27_Upper_Shell_Top`, lowering the hinge axis from $Y = 92.46\text{ mm}$ down to $Y = 81.00\text{ mm}$ ($\Delta Y = -11.46\text{ mm}$) so the folding lever cheeks nest deeply inside the shell ($1.75\text{ mm}$ to $4.98\text{ mm}$ below the outer rim), eliminating the exposed neck gap.

Rebuild toolchain:
```bash
python tools/build_concave_upper_station.py   # builds concave station and lowers head assembly
python tools/export_3d_print_package.py       # exports plates, STLs, and package GLBs
python tools/build_shell_variants_glbs.py     # exports all 8 mid-shell variant GLBs
python tools/export_subassembly_glbs.py       # exports the 5 subassembly GLBs
python tools/score_detent.py                 # detent mechanics verification
```

---

## 1. Design Overview & Requirements

The custom toy unifies the best mechanical and tactile features of the **Fidget Fuse Tactical 7-in-1** and the **Spinner Fuse Grenade 5-in-1** into a single, cohesive, production-ready fidget toy:

1. **Tactical Base & Native 33-Click Waist Detent**: Preserves the Tactical common base body, utilizing its native 3-window internal barrel and 3-arm leaf spring to drive a crisp 33-click rotary detent without increasing overall height.
2. **8 Interchangeable Mid Shell Variants**: 100% verified mechanical standardization across 8 mid shell designs (Baseline 2-piece, 01 AeroFlow, 02 Vector Chevron, 03 Orbit, 04 Ergo Scoops, 05 Contour Twist, 06 Hex Tactical, and 07 Classic Solid Tactical) sharing an exact **34.80 mm total height** and **40.00 mm mating interface diameter**.
3. **Tactical Internal Spine & 4-Pin Upper Retention**: The native `08 - Internal Barrel` with four spring slots at 0° / 90° / 180° / 270° and four diagonal pin ports at 45° / 135° / 225° / 315°, locked axially by 4 pins (`16_01..04`) trapped under `19_28_Upper_Shell_Gear` and `20_29_Upper_Shell_Lock_Ring`.
4. **Spinner Fuse Concave Upper Seating Arrangement**: 45° conical concave dish on `18_27_Upper_Shell_Top` with the folding head assembly lowered by $\Delta Y = -11.46\text{ mm}$ ($Y_{\text{hinge}} = 81.00\text{ mm}$), eliminating the exposed neck gap and nesting the handle cheeks below the outer rim.
5. **Solid-Yoke 3-Piece Rod Architecture**: Full-depth rod assembly with a seamless integral yoke on `Custom_Rod_Middle` flanked by `Custom_Rod_Right` and `Custom_Rod_Left`, locked via dual transverse cross-keys (`Custom_Rod_Lock_Upper_06` and `Custom_Rod_Lock_Lower_07`) and retained axially by `Spinner Lever 08 - Rod Lock` (no upper wedge lock or split yoke).
6. **Folding Head & Spinner**: Folding handle with 4 detent positions (0°, 30°, 60°, 90° on `15 - Handle Rotating Lock` and `09 - Rod Spring`), 360° free-spinning center ring (`Custom_Ring_Spinner` at ⌀22.10 mm), 20-click outer rim gear (`Spinner Lever 05 - Gear` against `04 - Spring` in a 274° pod), and refined turned 45°-chamfered cheeks with flush exterior surfaces.

---

## 2. Tactical Base Mechanism & The 33-Click Detent

**[M]** The Tactical base mechanism already houses a native 3-fold rotary detent:

| part | feature |
|---|---|
| `08 - Internal Barrel` | outer is a **clean cylinder, r 16.21 .. 16.22**, with **three windows at 30° / 150° / 270°**, each 22° wide, open y 20.43 .. ~34.7 |
| `32 - Mid Shell P02` | bore is a **33-lobe ratchet, r 16.43 .. 17.53** — 1.10 mm deep |
| `20 - Mid Shell Spring` / `09_Custom_Mid_Shell_Spring_33` | **three arms at 30° / 150° / 270°** poking out through those windows to **r 17.40** |

**[M]** Sweeping the mid shell against the spring gives a clean **1.33 → 10.18 mm³ cycle every 10.909°**, i.e. 360/33 (33 clicks per full turn).

**[M]** `20 - Mid Shell Spring` is **rotary only**. Its 15.84 mm square bore clears the rod by **1.158 mm** and contributes nothing axially — see `DESIGN.md` §2.2, where this claim is corrected in full. The waist and the axial click are fully decoupled: neither can be tuned through the other.

### 2.1 The 3-Fold Symmetry Rule

**[M]** Three windows, a 3-lobed barrel bore, three spring arms, 33 mid-shell lobes, and three barrel pins at 120°.

**[D]** A detent only clicks if **every nose seats simultaneously**, which requires the nose spacings to be integer multiples of the notch pitch:

| Mechanism | Notches | Noses | Works Because |
|---|---|---|---|
| Tactical mid shell | 33 | 3 at 120° | 33 / 3 = 11 notches between arms (Integer) |
| Spinner Fuse `04` | 32 | 2 at 180° | 32 / 2 = 16 notches between arms (Integer) |

**[M]** If `04`'s 32 notches are placed against three 120° arms, the swept overlap is **flat (4.87 .. 5.22 mm³)** resulting in constant drag rather than discrete clicks.
For the 32-click Ring variant, three arms spaced at **11 + 10 + 11 notches** (**30.00° / 153.75° / 266.25°**) seat cleanly inside the barrel's existing windows.
For the Native 33-click system, symmetrical **30.00° / 150.00° / 270.00°** arms seat into all 33 lobes simultaneously.

---

## 3. The 8 Interchangeable Mid Shell Options

To provide full customization, 8 mid shell variants were created and dimensionally standardized. Every variant was measured to ensure complete mechanical compatibility with the waist mechanism and adjacent body shells:

| Shell Variant | Architecture & Window Style | Total Height ($Z$) | Base / Ledge Dia | Max Grip Outer Dia | Part Files |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Baseline (Standard)** | 2-Piece (16 Vertical Slot Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 41.60 mm | `08_33_Mid_Shell_P01_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **01. AeroFlow** | 2-Piece (16 Swept Ribbon Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 41.68 mm | `08_Mid_Shell_Option_01_AeroFlow_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **02. Vector Chevron** | 2-Piece (16 Chevron V-Angle Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 41.52 mm | `08_Mid_Shell_Option_02_Vector_Chevron_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **03. Orbit Pods** | 2-Piece (12 Weaving Ribbon Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 41.55 mm | `08_Mid_Shell_Option_03_Orbit_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **04. Ergo Scoops** | 2-Piece (12 Channel Capsule Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 41.84 mm | `08_Mid_Shell_Option_04_Ergo_Scoops_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **05. Contour Twist** | 2-Piece (6 Twisted Flute Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 43.00 mm (tri-lobed) | `08_Mid_Shell_Option_05_Contour_Twist_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **06. Hex Tactical** | 2-Piece (39 Honeycomb Hex Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 42.12 mm | `08_Mid_Shell_Option_06_Hex_Tactical_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |
| **07. Classic Solid Tactical** | 2-Piece (16 Tilted Ribbon Windows) | **34.80 mm** (Outer)<br>**33.80 mm** (Inner) | **40.00 mm** | 41.95 mm | `08_Mid_Shell_Option_07_Classic_Solid_Tactical_Outer.stl`<br>`07_32_Mid_Shell_P02_Ratchet.stl` |

*Note: All 8 variants standardize on the 2-Piece Split Architecture with Aesthetic Through-Windows: print the universal internal ratchet core (`07_32_Mid_Shell_P02_Ratchet.stl`) in Safety Orange PETG for crisp, wear-resistant detent clicks against `09_Custom_Mid_Shell_Spring_33.stl`, and the cosmetic outer shell (`08`) in Tactical Olive PLA Matte. The outer shells feature custom-patterned through-windows that expose the contrasting inner core in a striking two-colour fidget toy design. Both pieces slide together with positive 3-pocket anti-rotation keyways and support-free flat-bed printability.*

---

## 4. Folding Head, Rim Gear & Cheek Refinement

### 4.1 Rim Gear & Detent Pod
- **`Spinner Lever 05 - Gear`**: 20 teeth, tip ⌀36.00 mm, root ⌀33.62 mm, bore ⌀25.514 mm, thickness 8.60 mm.
- **`Spinner Lever 04 - Spring`**: Unmodified serpentine spring housed inside a dedicated pod on the lever oriented at **274°** from the gear axis.
- **Exposed Rim**: Gear teeth stand proud over **>69% of the circumference** (249° / 360°), providing optimal thumb rolling accessibility.
- **Detent Feel**: **0.00 .. 4.20 mm³ over an 18° tooth pitch, 6 of 19 degrees free — 20 clicks/turn**.

### 4.2 Center Spinning Ring
- **`Custom_Ring_Spinner`**: Turned down from `17 - Ring Spinner`'s center bulge to **⌀22.10 mm**, riding on a **⌀22.60 mm** housing bore (1.30 mm journal wall) with **0.193 mm clearance**.
- Retains full **360° free spinning** action.

### 4.3 Handle Cheek & Surface Refinements
- **Pristine 45° Chamfered Cheeks**: Replaced stepped contour lines with pristine turned circular cheek solids ($r \le 16.30\text{ mm}$) featuring $1.50\text{ mm} \times 45^\circ$ outer chamfers.
- **Flush Outer Surface**: Filled the $1.50\text{ mm}$ deep sunken gap at $r = 13.50\text{ mm}$ completely flush to $z = \pm 9.50\text{ mm}$, eliminating circular surface arc lines.
- **Enclosed Pod**: Extended the spring housing pod inboard to merge continuously and organically with the head journal tube.
- **Pin Retention & Open Bores**:
  - Neck Lock at $(12.00, 56.80)$, spun $-17.5^\circ$.
  - Pod Lock at $(31.44, 31.07)$, spun $44.0^\circ$.
  - Sealed the unused legacy hole at $(17.53, 58.59)$.
  - Preserved native hinge detent scallops at $(0.0, 58.12)$.
  - Every full-width bore is ray-checked to ensure complete pass-through clearance with zero coplanar boolean skins.

---

## 5. Solid-Yoke 3-Piece Rod Architecture

### 5.1 Mechanical Evolution
The production design incorporates the **Unified Full-Height Hex-Keyed Rod & Enclosed Hinge Spring Pod Architecture** optimized for the v1.3 concave upper seating:

1. **Integral Solid Yoke (`23_Custom_Rod_Middle`)**: The upper hinge yoke is seamlessly integrated into the central middle rod ($y = 18.08 \dots 88.16\text{ mm}$), lowered by $\Delta Y = -11.46\text{ mm}$ ($Y_{\text{pin}} = 81.00\text{ mm}$). It provides exceptional structural strength for the folding head and hinge pin (`36_15_Handle_Rotating_Lock_D_Pin`). It contains an enclosed central cavity for the compacted hinge spring ($Y \in [59.50, 74.19]\text{ mm}$) with **zero upper through-holes**.
2. **Monolithic Side Clamps (`22_Custom_Rod_Right` & `24_Custom_Rod_Left`)**:
   - Each side member spans ($y = 18.08 \dots 67.20\text{ mm}$) in a single solid, continuous part, trimmed at the top to clear the $45^\circ$ conical dish of `18_27_Upper_Shell_Top`.
   - The lower section ($y \in [18.08, 62.00]\text{ mm}$) carries the axial detent rack channels and transverse key capture pockets.
   - The upper section ($y \in [62.00, 67.20]\text{ mm}$) forms the hexagonal keying prism that matches the bore of `21_30_Upper_Shell_Rotating_Spring.stl` with $0.20\text{ mm}$ radial clearance, maintaining $5.20\text{ mm}$ of positive rotational drive engagement.
3. **Dual Transverse Cross-Keys (`06` & `07`)**:
   - `Custom_Rod_Lock_Upper_06`: Located at $y = 48.654 .. 58.186\text{ mm}$.
   - `Custom_Rod_Lock_Lower_07`: Located at $y = 23.654 .. 33.186\text{ mm}$.
   - Each key passes through the middle rod and captures $3.388\text{ mm}$ inside each side member with $0.100\text{ mm}$ axial and $0.075\text{ mm}$ radial clearance ($0.000\text{ mm}^3$ interference).
   - Distance between key 06 top ($Y = 58.09\text{ mm}$) and spring floor ($Y = 59.50\text{ mm}$) provides a robust $1.41\text{ mm}$ solid bulkhead.
4. **Compacted Hinge Spring (`28_09_Rod_Spring_Hinge_T_Head`)**: Compacted to $14.69\text{ mm}$ height, seating cleanly within $Y \in [59.50, 74.19]\text{ mm}$ to maintain full 4-position detent click action.
5. **Bottom Axial Retainer (`27_Spinner_Lever_08_Rod_Lock`)**: Wedges onto the $-0.536\text{ mm/mm}$ bottom tapered tab to axially secure the entire 3-part rod assembly.

### 5.2 Axial Click Detent (Dual-Headed Option B System)

**[M]** The click is produced by **four springs alone** — `12/13/14/15_Custom_Rod_Detent_Spring` in slots in `08 - Internal Barrel` at azimuth **0° / 90° / 180° / 270°**:
- **01 & 03 (az 0° & 180°)**: Single-headed springs ($Y \in [36.00, 62.92]\text{ mm}$) with lower detent nose at $Y = 57.40\text{ mm}$.
- **02 & 04 (az 90° & 270°)**: Dual-headed springs ($Y \in [36.00, 72.45]\text{ mm}$) carrying both the lower detent nose at $Y = 57.40\text{ mm}$ and an extended upper detent head at $Y = 66.94\text{ mm}$ (exactly $3 \times \text{pitch} = 9.532\text{ mm}$ above the lower nose), passing through $3.60\text{ mm}$ channels in `11_Custom_Internal_Barrel_Cap`.
- **Synchronous Engagement**: All 6 detent noses engage the rod rack simultaneously in exact phase, providing a **$23.91\text{ N}$ total axial breakout pop** with a crisp **$7.62\times$ snap-action force ratio**.

**[M]** The rack: pitch **3.17733 mm**, crest **r 6.8901**, V-root **r 5.7652**, straight **40.63°** flanks — and it is a **turned ring, not a pair of flat faces**. Measured at every azimuth from 0° to 350° over y 34 .. 60, the rod's outer radius is 6.88–6.89 at the crest and 5.77–5.81 at the root. A nose therefore works at any azimuth, which is what makes a four-fold layout possible at all.

**[M]** The two transverse cross-keys are part of that ring. The three rod pieces part along z = 0, and between **y 48.75 and 58.09** that parting line is an open gap; `25_Custom_Rod_Lock_Upper_06` fills it and carries the same rack (crest 6.888, root 5.780). A spring at azimuth 0° or 180° rides that key.

**[D] Exact V2 Geometry & Dual Flexure Arms**: Directly sourced from Spinner Fuse `11 - Middle Spring v2`, preserving the cantilever flexure stalk, 180° hairpin U-turn arch, teardrop head, and rack-matched detent nose facets. The downward shelf has been removed to provide $0.600\text{ mm}$ slot clearance and $100\%$ linear compliance across full tooth stroke.

| the spring | value |
|---|---|
| foot | y 36.00 → 42.60, r 7.40 → 12.20 — rigid anchor bearing on slot outer wall and seated on floor; **4.00 mm** wide outboard of r 11.55, **3.00 mm** inboard (notch step) |
| single arm (01/03) | y 36.00 → 62.92 mm, r 7.40 → 10.90 mm, volume **229.71 mm³**, watertight single body |
| dual arm (02/04) | y 36.00 → 72.45 mm, r 7.40 → 10.90 mm, upper nose at y 66.94 mm, volume **303.42 mm³**, watertight single body |
| nose geometry | 0.75 mm tip radius on rack-matched 49.37° flanks, apex **r 5.54 mm** at seated depth |
| barrel cap (11) | 4 downward $1.20\text{ mm}$ filler prongs matching the 4 L-shaped slots, sealing upper notch recesses and providing positive 4-way anti-rotation alignment |

### 5.3 Rod Stroke

**[M]** The rod has **no upward stop**: swept to +24 mm it meets nothing, so the click count is undefined and the rod can be pulled out of the toy. Downward it bottoms after **0.30 mm** (retainer rim on the barrel's lower face). v1.2 briefly carried two inward lands at azimuth 90°/270° that gave a 14.07 mm stroke; they were dropped with the C-follower design they belonged to, and the stroke is again unlimited.

**[D]** Growing the retainer instead does not work, and the reason is worth keeping: above it the spacer bore is **8.30 mm** from y 16 to 27, and the first thing narrower is the waist spring's **7.915 mm** bore, so a collar would have to live inside a **0.385 mm** window. That is inside FDM variation — a given print would either bind in the spacer or slip past the spring.

---

## 6. The Complete Assembled Toy & Interactive Web Studio

### 6.1 Assembled Envelopes & Dimensions

- **Total Part Count**: 38 parts (6 in 01 Base & Bottom, 3 in 02 Waist Mech, 14 in 03 Upper Station, 6 in 04 Rod Assembly, 9 in 05 Folding Head & Spinner).
- **Assembled Envelope**: **41.63 × 114.80 × 72.47 mm** ($X \times Y \times Z$ with handle folded down at 0°).
- **Height**: ~114.8 mm total (handle folded; previously 126.3 mm before lowering the hinge pin by 11.46 mm and deeply nesting into the concave dish).

| Action | Mechanism | Measured Performance |
|---|---|---|
| **Fold Handle (0° → 90°)** | `36 D-Pin` + `28 T-Head Spring` | **7.34 .. 11.90 mm³ detent**, 4 positions (**0°, 30°, 60°, 90°**), 3 clicks |
| **Spin Center Ring** | `Custom_Ring_Spinner` | **360° free spin** (0.193 mm clearance journal) |
| **Roll Rim Gear** | `05 Gear` + `04 Spring` in pod | **0.00 .. 4.23 mm³ detent**, **20 clicks/turn** |
| **Waist Twist** | Mid Shell + `09 Spring 33` | **0.07 .. 9.62 mm³ detent**, **33 clicks/turn** ($134.9\times$ ratio) |
| **Linear Rod Push/Pull** | 3-Piece Rod + 4 preloaded followers | **24.37 N peak / 4.85 N held**, **3.177 mm pitch**, 0% dead band |

---

## 7. Complete Bill of Materials (BOM) — 38 parts

Numbers 16 and 17 are the four diagonal retention pins (azimuths 45°, 135°, 225°, 315°) that axially lock `18_27_Upper_Shell_Top.stl` to `10_Custom_Internal_Barrel_4Slot.stl`. They completely avoid the 4 orthogonal spring slots at 0°, 90°, 180°, and 270°, providing positive, drop-proof axial retention, trapped and enclosed under `19_28_Upper_Shell_Gear` and `20_29_Upper_Shell_Lock_Ring`.

| Part # | Subassembly | Filename | Recommended Material / Color | Qty | Supports |
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
| **20** | Upper Station | `20_29_Upper_Shell_Lock_Ring.stl` | PLA (Olive Drab Accent) | 1 | No |
| **21** | Upper Station | `21_30_Upper_Shell_Rotating_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **22** | Rod Assembly | `22_Custom_Rod_Right.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **23** | Rod Assembly | `23_Custom_Rod_Middle.stl` | PLA+ / PETG (Charcoal Black) | 1 | Minimal (under yoke) |
| **24** | Rod Assembly | `24_Custom_Rod_Left.stl` | PLA+ / PETG (Gunmetal / Black) | 1 | No |
| **25** | Rod Assembly | `25_Custom_Rod_Lock_Upper_06.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **26** | Rod Assembly | `26_Custom_Rod_Lock_Lower_07.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **27** | Rod Assembly | `27_Spinner_Lever_08_Rod_Lock.stl` | PLA+ / PETG (Gunmetal Disc) | 1 | No |
| **28** | Head & Spinner | `28_09_Rod_Spring_Hinge_T_Head.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **29** | Head & Spinner | `29_Custom_Handle_Left.stl` | PLA (Olive Drab Green) | 1 | No |
| **30** | Head & Spinner | `30_Custom_Handle_Right.stl` | PLA (Olive Drab Green) | 1 | No |
| **31** | Head & Spinner | `31_Custom_Ring_Spinner.stl` | Silk PLA (Gold / Brass) | 1 | No |
| **32** | Head & Spinner | `32_Spinner_Lever_05_Gear.stl` | Silk PLA (Silver Chrome) | 1 | No |
| **33** | Head & Spinner | `33_Spinner_Lever_04_Spring.stl` | PETG / Tough PLA (Safety Orange) | 1 | No |
| **34** | Head & Spinner | `34_Custom_16_Handle_Lock_Neck.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **35** | Head & Spinner | `35_Custom_16_Handle_Lock_Pod.stl` | PETG / PLA+ (Crimson Red) | 1 | No |
| **36** | Head & Spinner | `36_15_Handle_Rotating_Lock_D_Pin.stl` | PETG / PLA+ (Crimson Red) | 1 | No |

---

## 8. Verification & 3D Print Guidelines

- **Watertightness**: 100% of the 36 parts are single-body, manifold, and watertight (`python tools/fidget.py check` passes 110/110).
- **Detent regression check**: `python tools/score_detent.py` reports peak, trough and **force** for all five motions. Run it after any change to the rod, the springs or the barrel — nothing else re-measures the axial detent, and swept volume on its own will not reveal a dead band.
- **Rebuild order matters**: `export_3d_print_package.py` clears and rewrites `Plates_3MF/`, and `build_shell_variants_glbs.py` writes one plate plus the three `Mid_Shell_Options/` folders into it. Run them in that order and only that order:
  ```bash
  python tools/build_rod_detent.py            # only if the detent changed
  python tools/export_3d_print_package.py
  python tools/build_shell_variants_glbs.py
  ```
- **Note on `tools/custom.py`**: it still builds the earlier **split-yoke** rod with an upper wedge lock, not the shipped solid-yoke one. The package is regenerated from `All_Parts_Assembled_Coordinates/` by `export_3d_print_package.py`; `custom.py` is upstream of an older lineage.
- **Ray-Checked Bores**: All pin bores verified open with zero residual boolean skins.
- **Recommended Slicer Settings**:
  - **Layer Height**: `0.16 mm` (recommended) or `0.20 mm`.
  - **Wall Loops / Perimeters**: `4` walls for structural parts, gears, and flexures.
  - **Top / Bottom Shells**: `5` top layers, `4` bottom layers.
  - **Infill**: `25% - 30% Gyroid` or `Cubic`.
  - **Supports**: Disabled on every part but one (only minimal support under the central rod hinge yoke).
