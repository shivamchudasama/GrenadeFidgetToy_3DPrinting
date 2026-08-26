# Custom Hybrid Grenade (Modified) — Complete STL Set

This directory is the self-contained, single-source repository for all 3D printing STL files and assembly models for the **Compact Tactical/Spinner Hybrid Grenade (Modified)**.

Every STL part in this folder is 100% watertight, single-body, manifold, and verified to match the 3D assembly models bit-for-bit.

---

## Complete Bill of Materials (35 Printable Parts)

Print **1 copy** of every STL file below (total: 35 printed pieces):

### 1. Base Mechanism & Lower Shells (6 Parts)
| File Name | Description |
| :--- | :--- |
| `01 - Bottom Lock Shell.stl` | Bottom retaining screw lock shell |
| `02 - Bottom Spring.stl` | Helical leaf return spring for lower stack |
| `03 - Bottom Shell Spacer.stl` | Central cylindrical alignment spacer |
| `04 - Bottom Shell 01.stl` | Outer lower shell tier 01 |
| `05 - Bottom Shell 02.stl` | Outer lower shell tier 02 |
| `06 - Bottom Shell 03.stl` | Outer lower shell tier 03 |

### 2. Waist Mechanism & Detent (3 Parts)
| File Name | Description |
| :--- | :--- |
| `32 - Mid Shell P02.stl` | Upper half of the 33-tooth internal ratchet mid shell |
| `33 - Mid Shell P01.stl` | Lower half of the 33-tooth internal ratchet mid shell |
| `Custom_Mid_Shell_Spring_33.stl` | 3-arm radial leaf spring tuned for 33-click waist |

### 3. Compact Upper Station Rotary Clicker (8 Parts)
| File Name | Description |
| :--- | :--- |
| `07 - Internal Barrel Cap.stl` | Upper barrel retention cap |
| `Hybrid_08_Internal_Barrel.stl` | Internal barrel turned to r=16.22 mm journal with 4 orthogonal open-top guide slots (90° apart) |
| `Hybrid_11_Middle_Spring.stl` | Primary Spinner Fuse cross-spring (along X-axis) engaging ratchet at 0° and 180° |
| `Hybrid_12_Optional_Middle_Spring.stl` | Perpendicular Spinner Fuse cross-spring (along Z-axis) engaging ratchet at 90° and 270° |
| `Hybrid_27_Upper_Shell_Top_Chamber.stl` | Upper shell top housing with relieved 32-tooth internal ratchet chamber & lobe windows |
| `Hybrid_28_Upper_Shell_Gear_32_Click.stl` | Upper rotor with integrated 32-tooth internal ratchet annulus |
| `29 - Upper Shell Lock Ring.stl` | Rotor axial retention ring |
| `30 - Upper Shell Rotating Spring.stl` | Upper station torsion leaf spring |

### 4. 3-Part Full-Depth Split Rod & Transverse Locks (9 Parts)
| File Name | Description |
| :--- | :--- |
| `Custom_Rod_Right.stl` | Right longitudinal rod side plate (with cross-lock tunnels) |
| `Custom_Rod_Middle.stl` | Center linear-track rod member (split support-free version) |
| `Custom_Rod_Left.stl` | Left longitudinal rod side plate (with cross-lock tunnels) |
| `Custom_Rod_Upper_Right.stl` | Right upper yoke cap |
| `Custom_Rod_Upper_Left.stl` | Left upper yoke cap |
| `Custom_Rod_Lock_Upper_06.stl` | Upper transverse cross-locking key (passes through all 3 rod members) |
| `Custom_Rod_Lock_Lower_07.stl` | Lower transverse cross-locking key (passes through all 3 rod members) |
| `Custom_Rod_Upper_Lock.stl` | Upper yoke retention wedge |
| `Spinner Lever 08 - Rod Lock.stl` | Bottom axial retainer for the rod assembly |

### 5. Modified Folding Head & Lever Mechanism (9 Parts)
| File Name | Description |
| :--- | :--- |
| `09 - Rod Spring.stl` | Yoke hinge leaf spring |
| `Custom_Handle_Left.stl` | Left folding lever half (pristine turned circular cheeks, optimized spring pocket) |
| `Custom_Handle_Right.stl` | Right folding lever half (pristine turned circular cheeks, optimized spring pocket) |
| `Custom_Ring_Spinner.stl` | Center spinner ring (free 360° rotation) |
| `Spinner Lever 05 - Gear.stl` | Exposed thumb clicker gear (20-click detent) |
| `Spinner Lever 04 - Spring.stl` | Leaf spring arm for thumb gear detent |
| `Custom_16_Handle_Lock.stl` | Functioning neck alignment lock pin (neck station) |
| `Custom_16_Handle_Lock_pod.stl` | Functioning pod tail alignment lock pin (pod station) |
| `15 - Handle Rotating Lock.stl` | D-bore hinge axle locking pin |

---

## Assembly & Reference Models Included in this Folder

- `Custom_Hybrid_Grenade_Modified_assembled.glb` — Full 35-part assembled 3D scene (PBR colors).
- `Custom_Hybrid_Grenade_Modified_exploded.glb` — Full 35-part exploded 3D scene.
- `Custom_Hybrid_Grenade_Modified_assembled.3mf` — Multi-material color palette 3MF assembly.
- `Custom_Hybrid_Grenade_Modified_exploded.3mf` — Exploded multi-material 3MF assembly.
- `hybrid_modified_assembly_viewer.html` — Interactive WebGL 3D assembly & exploded viewer (open in any web browser).

---

## Key Mechanism Features

1. **33-Click Waist Rotary Detent**: Built directly into the tactical base via `32 - Mid Shell P02` / `33 - Mid Shell P01` and `Custom_Mid_Shell_Spring_33`.
2. **32-Click Upper Station Rotary Detent**: 4-slot cross-barrel architecture housing two orthogonal Spinner Fuse cross-springs (`Hybrid_11_Middle_Spring` & `Hybrid_12_Optional_Middle_Spring`) engaging the internal 32-tooth ratchet inside `Hybrid_28_Upper_Shell_Gear_32_Click` at 0°, 90°, 180°, and 270°.
3. **Smooth Slide-In Assembly**: Open-top through channels on `Hybrid_08_Internal_Barrel` allow effortless vertical slide-in assembly with 0 collision.
4. **Support-Free 3-Part Split Rod**: Full-depth rod split into 3 vertical members locked solidly with transverse keys (`Custom_Rod_Lock_Upper_06`, `07`, `Upper_Lock`).
5. **90° Folding Lever Head**: Smooth folding lever head with exposed 20-click thumb gear and free-spinning center ring.
