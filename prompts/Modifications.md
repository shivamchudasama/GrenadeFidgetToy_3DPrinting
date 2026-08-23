# TASK: 3D CAD Modeling, Assembly Solving & Script Development for Compact Hybrid Grenade Fidget Toy

## 1. Objective & Role
You are an expert Computational CAD & Mechanical 3D Printing Engineer specializing in Python-based mesh manipulation (`trimesh`, `manifold3d`, `fidget.py`, OpenSCAD/CadQuery).

Your objective is to model, assemble, solve fits for, and export a custom **Compact Hybrid Grenade Fidget Toy** that merges the tactile actions of the **Tactical 7-in-1 Native Base** and the **Spinner Fuse High-Tactile Mechanism**, adhering to two critical design principles:
1. **Full-Depth Rod Penetration & Retention**: Use the `Spinner Lever 01/02/03` architecture as the reference for a three-part printable rod (`Custom_Rod_Right.stl`, `Custom_Rod_Middle.stl`, and `Custom_Rod_Left.stl`). Preserve its two aligned transverse tunnels and join all three members with the actual `Spinner Lever 06 - Rod Lock` and `Spinner Lever 07 - Rod Lock` cross-keys. Keep `Spinner Lever 08 - Rod Lock` only as the separate bottom axial retainer. Cut both side members at $y=62\text{ mm}$ and keep the folding Handle/Lever yoke on the Middle.
2. **True Functional Integration (Preserving Body Height)**: Do **NOT** stack the full Spinner Fuse assembly on top of the Tactical body. Instead, integrate the Spinner Fuse-inspired rotary clicker mechanism directly into the existing Tactical body envelope ($y \approx -0.35 \dots 80.1\text{ mm}$) by interfacing `08 - Internal Barrel.stl` with `28 - Upper Shell Gear.stl` (or `27 - Upper Shell Top.stl`). If spatial congestion occurs, cleanly remove the legacy internal 3-spring barrel clicker mechanism to make room for the high-tactile leaf detent system.

---

## 2. Source Assets & Reference Files

### A. Reference Visuals & Data
- `CUSTOM_DESIGN.md` & `DESIGN.md` (Mechanical specs, coordinate frames, and measured dimensions)
- `Derivatives/custom/Custom_Toy_Native_2pc_assembled.glb` & `Custom_Toy_Ring_2pc_assembled.glb`
- `Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click/`

### B. Core Repositories / Part Directories
- **Custom Base & Native STLs**: `Derivatives/custom/Complete_STL_Set/Native_Waist_33_Click/`
  - `08 - Internal Barrel.stl` (Body spine, outer $r=16.22\text{ mm}$, $y=20.43\dots 63.24\text{ mm}$)
  - `28 - Upper Shell Gear.stl` (Rotating knurled gear/ring, $y=59.00\dots 62.98\text{ mm}$, 48 outer lobes, 3-lobe bore)
  - `27 - Upper Shell Top.stl` (Upper retention housing, $y=55.00\dots 74.83\text{ mm}$)
  - `29 - Upper Shell Lock Ring.stl` ($y=55.00\dots 58.88\text{ mm}$)
  - `30 - Upper Shell Rotating Spring.stl` ($y=63.75\dots 79.72\text{ mm}$)
  - `01 - Bottom Lock Shell.stl`, `02 - Bottom Spring.stl`, `03 - Bottom Shell Spacer.stl`
  - `04 - Bottom Shell 01.stl`, `05 - Bottom Shell 02.stl`, `06 - Bottom Shell 03.stl`
  - `20 - Mid Shell Spring.stl` / `Custom_Mid_Shell_Spring_33.stl`
  - `32 - Mid Shell P02.stl` & `33 - Mid Shell P01.stl`
  - `Spinner Lever 08 - Rod Lock.stl` (Slotted $-0.55\text{ mm/mm}$ tapered retaining disc)
  - `Spinner Lever 06 - Rod Lock.stl` & `Spinner Lever 07 - Rod Lock.stl` (Native transverse keys for the two aligned rod tunnels)
- **Composite Rod & Head Assets**: `Derivatives/custom/Parts/`
  - `Custom_Rod_Right.stl` (Separately printable lower right plate, cut at $y=62$)
  - `Custom_Rod_Middle.stl` (Full-depth middle with tapered lock tab and folding-head hinge yoke)
  - `Custom_Rod_Left.stl` (Separately printable lower left plate, cut at $y=62$)
  - `Custom_Rod_Lock_Upper_06.stl` (Rigidly posed copy of the native upper transverse key)
  - `Custom_Rod_Lock_Lower_07.stl` (Rigidly posed copy of the native lower transverse key)
  - `Custom_Handle_Left.stl` & `Custom_Handle_Right.stl` (Folding lever halves with gear rim journal)
  - `Custom_Ring_Spinner.stl` (Slimmed spinning ring)
- **Spinner Fuse Mechanism Reference**: `Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy/`
  - `04 - Middle Spinner Shell.stl` (32-tooth internal ratchet, $r=16.43\dots 17.53\text{ mm}$)
  - `11 - Middle Spring.stl` & `11 - Middle Spring v2.stl` (High-tactile leaf detent springs, reach $17.40\text{ mm}$)
  - `09 - Rod Spring.stl` (Hinge detent leaf spring)
  - `15 - Handle Rotating Lock.stl` (Hinge rotation lock pin)
- **Tooling & Libraries**: `tools/fidget.py`, `tools/assembly.py`, `tools/custom.py`

---

## 3. Sub-Assembly Hierarchy & Mechanical Specifications

### PART 1: Tactical Native Base Assembly (Bottom to Mid)

1. **Sub-Assembly A (Bottom Lock Core)**:
   - Place `02 - Bottom Spring.stl` inside `01 - Bottom Lock Shell.stl`.
   - Place `03 - Bottom Shell Spacer.stl` on top to seal and space the spring.
   - Result: **`Part A`**.

2. **Sub-Assembly B (Bottom Outer Shell Stack)**:
   - Insert **`Part A`** inside `04 - Bottom Shell 01.stl`.
   - Stack `05 - Bottom Shell 02.stl` on top (inverted).
   - Flip `06 - Bottom Shell 03.stl` by **180°** and seat it on top of `05`.
   - Result: **`Part B`**.

3. **Sub-Assembly C (Tactile Waist Clicker)**:
   - Concentrically align `32 - Mid Shell P02.stl` (33-lobe ratchet) and `33 - Mid Shell P01.stl`.
   - Seat `20 - Mid Shell Spring.stl` (or `Custom_Mid_Shell_Spring_33.stl` with 3 arms at $30^\circ/150^\circ/270^\circ$, reach $17.40\text{ mm}$) through the 3 windows of `08 - Internal Barrel.stl` ($y=20.43\dots 34.7\text{ mm}$).
   - Result: **`Part C`** (Provides 33 distinct rotary waist clicks per revolution + $15.84\text{ mm}$ square bore guide for the rod).

---

### PART 2: Three-Part Full-Depth Rod Integration

1. **Rod Architecture**:
   - **Do NOT use** the 3-piece multi-rod assembly (`05 - Rod Middle Right`, `06 - Rod Middle Left`, `07 - Rod Middle Linear Track`) which fails to reach full depth and lacks lower lock tabs.
   - Use the **three separately printable rod bodies**:
     - **Lower Section ($y \le 62.00\text{ mm}$)**: Retain the lower portions of `1 - Rod Right v1.1` and `2 - Rod Left v1.1` as independent Right and Left members around `3 - Rod Middle v1.1`. Keep the donor vertices and native $3.17733\text{ mm}$ click period unchanged. Trim both outer members at $y=62.00\text{ mm}$ so their Tactical circular head and supports are excluded.
     - **Transverse Rod Locks**: Preserve the two native tunnels inherited from `Spinner Lever 01/02/03`. Pose the unmodified `Spinner Lever 06 - Rod Lock` in the upper tunnel and `Spinner Lever 07 - Rod Lock` in the lower tunnel. Each key must pass through the Middle and both seams, retain $3.388\text{ mm}$ capture in each outer member, and keep its native $0.100\text{ mm}$ axial / $0.075\text{ mm}$ vertical clearance. Do not add new seam pockets or use `22/26` locks.
     - **Bottom Anchor Tab**: Carries the $-0.536\text{ mm/mm}$ tapered wedge tab ($5.102 \to 3.816\text{ mm}$) that slides into and friction-locks with `Spinner Lever 08 - Rod Lock.stl` (slotted $-0.55\text{ mm/mm}$ washer).
     - **Upper Section ($y > 62.00\text{ mm}$)**: Keep the established solid graft at `YOKE_JOIN = 62.000`, forming the hinge yoke ($\pm 3.58\text{ mm}$ thickness, $\varnothing 4.38\text{ mm}$ hinge bore) and retention pocket for `09 - Rod Spring.stl`. This yoke mounts the Custom Handle/Lever head and must not be replaced by the Tactical spinner head.
2. **Installation**:
   - Close the three rod members on their zero-gap side seams, align both transverse tunnels, then insert `Custom_Rod_Lock_Upper_06` and `Custom_Rod_Lock_Lower_07` across the entire stack.
   - Insert the locked three-part stack axially through `08 - Internal Barrel` and `20 - Mid Shell Spring`.
   - Slide `Spinner Lever 08 - Rod Lock.stl` onto the bottom taper as the separate axial retainer; the `06/07` cross-keys are what join the three rod members.

---

### PART 3: Compact Upper Rotary Clicker Integration (Non-Stacked, Height-Preserving)

1. **Height Constraint**:
   - The total body height must remain within the original Tactical envelope ($y \approx -0.35\dots 80.07\text{ mm}$, overall assembled toy $\le 121\text{ mm}$).
   - **No external module stacking**: The rotary clicker must be packaged entirely within the $y=55.00\dots 79.72\text{ mm}$ upper station.

2. **Rotary Mechanism Kinematics**:
   - **Actuator / Rotor**: `28 - Upper Shell Gear.stl` (and/or `27 - Upper Shell Top.stl`) acts as the rotating outer ring/gear driven by the user.
   - **Stator**: `08 - Internal Barrel.stl` upper cylinder ($y=45.0\dots 63.24\text{ mm}$, $r=16.22\text{ mm}$).
   - **Click Action**: Spring detent arms/leaves inspired by Spinner Fuse (reach $17.40\text{ mm}$, $5^\circ$ contact noses) engage internal ratchet notches in `28 - Upper Shell Gear` or between `08 - Internal Barrel` and `27 - Upper Shell Top`.

3. **Implementation Approaches**:
   - **Approach 1 (Coexistence / Enhanced Barrel)**:
     - Retain `08 - Internal Barrel.stl` core structure.
     - Integrate Spinner Fuse detent leaf springs (`11 - Middle Spring` profile or flexible detent arms) to interface between `08 - Internal Barrel` and `28 - Upper Shell Gear`.
     - Secure using `29 - Upper Shell Lock Ring.stl` and `27 - Upper Shell Top.stl`.
   - **Approach 2 (Direct Replacement / Clean Chamber - RECOMMENDED)**:
     - If retaining the legacy 3-spring channels (`12/13/14` springs and `09/10/11` pins) causes wall thickness issues ($<1.2\text{ mm}$) or geometric overlap:
     - **Remove / hollow out the legacy upper clicking channels** from `08 - Internal Barrel.stl`.
     - Directly incorporate high-tactile leaf detents / spring arms (inspired by Spinner Fuse `11/12 Middle Spring` or `30 - Upper Shell Rotating Spring`) positioned to snap into the internal lobes/teeth of `28 - Upper Shell Gear.stl` (or internal ratchet teeth cut into `27 - Upper Shell Top.stl`).
     - This gives a crisp, loud, heavy tactile click upon rotating `28 - Upper Shell Gear` without altering the outer height or silhouette.

---

### PART 4: Folding Handle & Rim-Roller Sub-Assembly (Required Head Integration)

1. **Folding Lever Hinge**:
   - Mount `Custom_Handle_Left.stl` and `Custom_Handle_Right.stl` to the rod's upper yoke using `15 - Handle Rotating Lock.stl` keyed D-pin and `09 - Rod Spring.stl`.
   - Provides 3 defined tactile fold detents ($0^\circ \to 30^\circ \to 60^\circ \to 90^\circ$).
2. **Rim Gear & Spinner Ring**:
   - Seat `Spinner Lever 05 - Gear.stl` onto the journal tube of the handle cheeks.
   - Insert `Spinner Lever 04 - Spring.stl` into the handle lever pod to provide 20 clicks/turn outer wheel rolling detents.
   - Insert `Custom_Ring_Spinner.stl` into the center bore on a $0.193\text{ mm}$ clearance journal for $360^\circ$ continuous free spinning.

---

## 4. Technical Constraints & Engineering Rules

1. **Mesh & Geometry Integrity**:
   - Use `tools/fidget.py` and `manifold3d` / `trimesh` CSG boolean pipelines (`fidget.load()`, `fidget.cut()`, `fidget.union()`).
   - Every modified part must be a **100% watertight single-body mesh** (`is_watertight == True`, `body_count == 1`).
   - Run axial ray-intersection checks on all through-bores and pin channels to guarantee zero-thickness skin defects do not occlude apertures.

2. **Tolerances & Fit Clearances**:
   - Running rotary & sliding journals: **$0.25\text{ mm}$ to $0.30\text{ mm}$**.
   - Snap fits: **$0.15\text{ mm}$ to $0.25\text{ mm}$**.
   - Minimum 3D-printable wall thickness in PLA: **$\ge 1.20\text{ mm}$** (target $\ge 1.50\text{ mm}$).

3. **Sweep & Detent Verification**:
   - **Rotary Detent Sweep**: Simulate full $360^\circ$ rotation of `28 - Upper Shell Gear` against the detent spring. Overlap volume must cycle between peak engagement ($\ge 4.0\text{ mm}^3$) and full release ($0.00\text{ mm}^3$) at each detent notch.
   - **Linear Detent Sweep**: Sweep the locked Right/Middle/Left rod stack through $9.0\text{ mm}$ against the detent springs. All three members must release together at the donor's native $3.17733\text{ mm}$ period.

---

## 5. Deliverables & Execution Steps

1. **Python Script Update / Implementation (`tools/build_custom_hybrid.py` or `tools/custom.py`)**:
   - Implement modular builder functions:
     - `build_base()`: Tactical body stack including bottom lock, waist detent, and `08 - Internal Barrel`.
     - `build_compact_upper_clicker()`: Integrated `08 - Internal Barrel` + `28 - Upper Shell Gear` rotary click mechanism (without vertical stacking).
     - `build_rod()`: Builds the separate Right/Middle/Left rod bodies, their native `Spinner Lever 06/07` transverse keys, and the `Spinner Lever 08 - Rod Lock` bottom axial retainer.
     - `build_hybrid_toy()`: Assembles the required folding Handle/Lever head, then runs the unified assembly validator, sweep tester, and interference analyzer.
2. **Exported Models in `Derivatives/custom/`**:
   - `Custom_Hybrid_Grenade_assembled.glb` & `.3mf` (Separated, named, color-coded components).
   - `Custom_Hybrid_Grenade_exploded.glb` & `.3mf` (Exploded assembly diagram).
   - `Custom_Hybrid_Grenade.stl` (Merged complete print model).
    - Individual printable STLs for modified components (`Custom_Rod_Right.stl`, `Custom_Rod_Middle.stl`, `Custom_Rod_Left.stl`, `Custom_Rod_Lock_Upper_06.stl`, `Custom_Rod_Lock_Lower_07.stl`, the bottom Rod Lock, modified `08 - Internal Barrel.stl`, and modified `28 - Upper Shell Gear.stl`) saved to `Derivatives/custom/Parts/`.
3. **Execution Report**:
   - Print terminal report displaying:
     - Total bounding envelope dimensions ($X \times Y \times Z \le 42 \times 122 \times 73\text{ mm}$).
     - Total part count and bill of materials.
     - Pairwise interference matrix (confirming max overlap $\le 13.0\text{ mm}^3$ for uncompressed flexures, $0.00\text{ mm}^3$ for rigid bodies).
     - Sweep detent validation curves for linear stroke, waist rotation, upper gear rotation, and handle fold.
