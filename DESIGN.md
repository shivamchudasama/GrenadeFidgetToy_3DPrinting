# DESIGN.md — how these toys are put together

A description of the **mechanical design**, written for the case where you want to
change a part and need to know what else that breaks. `CLAUDE.md` covers repo
conventions; this file covers the geometry itself, what is still unsolved (§8)
and what to do about it next (§9).

**Everything here is measured from the STLs, not from a spec sheet.** There is no
upstream CAD and no documentation — every number below came from sectioning or
boolean-testing the meshes, and each claim is tagged:

- **[M]** measured directly, repeatable with the snippets shown
- **[D]** derived — a fit or an inference from several measurements
- **[?]** informed guess, stated because it is useful, not because it is proven

Reproduce anything here with `tools/fidget.py` + `tools/assembly.py`. Last
verified 2026-08-22.

---

## 1. Frame and units

**[M]** Millimetres. **Y is up**, the toy's axis of revolution is `X = Z = 0`, and
the assembled Tactical body sits at `y = -0.35 .. 79.72`.

**[M]** Source STLs are in one of two coordinate systems, and this trips people up:

| coordinates | which files | what it means |
|---|---|---|
| **assembly** | Grenade (all), Spinner Fuse (all), Tactical `v1.1` group | loading the file *is* the placement, no fitting needed |
| **plate** | Tactical numbered `.stl.stl` series, `Spinner Lever 01–08`, `Bottle Cap *` | laid out flat for printing at x ≈ 380–760, z-min = 0 |

Anything in plate coordinates needs a pose before it means anything. Those poses
live in `Derivatives/tactical/Tactical_variants_poses.json`.

**[M]** All 110 files are binary STL from one exporter (`MW 1.0 <n> US` header,
size exactly `84 + 50 × triangles`). They are **meshes, not CAD** — no feature
tree, no analytic surfaces, and converting to STEP does not recover any. A part
that must become parametric has to be remodelled from measurements.

---

## 2. The recurring interfaces

These four interfaces appear over and over. **They are the things to preserve
when you modify a part** — change one end of an interface and you must change
every part that mates on it.

### 2.1 The tapered lock tab — a self-locking wedge

The single most reused joint in the Tactical. A rod (or the bottle lever) ends in
a **tapered tab**; a **slotted disc** slides on sideways and the taper wedges it
tight. No snap, no thread — friction from the wedge.

**[M]** Tab, measured on three different parts, identical on all three:

| | at the free end | +2.4 mm inboard | slope |
|---|---|---|---|
| tab thickness | 5.102 mm | 3.816 mm | **−0.536 mm/mm** |

**[M]** Tab width varies by part — `Bottle Cap Lever` 13.403 mm,
`3 - Rod Middle v1.1` 7.000 mm, `21 - Rod Middle` 9.000 mm — and immediately
inboard of the tab the section jumps to ~13.40 mm.

**[M]** The disc (`23 - Rod Lock 01` ≡ `Bottle Cap Lock` ≡
`Spinner Lever 08 - Rod Lock`, 706.7 mm³): **15.6 mm diameter × 4.8 mm thick**.
Solid over its lower ~2.2 mm; the upper ~2.6 mm carries a U-slot cut in from one
edge, **14.1 mm deep**, tapering **5.38 → 4.06 mm at −0.55 mm/mm**.

**[D]** The two tapers match to within 3%, which is what makes the joint work.
Height is therefore *determined* — match the tapers and the disc's axial position
falls out with no search. Along the slot the disc is free to slide until the
surrounding parts stop it, typically a window under 1 mm wide.

**[D]** The slot-mouth direction is a **free 180° choice**. Both orientations
score identically. It only records which side the disc was slid on from.

**[M]** All seven Tactical rod locks are **achiral** — the mirrored mesh maps
back onto the original under a proper rotation, deviation 0.0000 mm. So a pose
transferred from one lock to another is always a **proper rotation, never a
mirror**, whatever `parts_index.json` labels the pair (§7, item 2). An earlier attempt
to place `23 - Rod Lock 01` by reflecting `Bottle Cap Lock` was wrong twice over:
the relation is not a reflection, *and* the source pose was not seated — it sat
0.436 mm clear of the lever, touching nothing in the assembly, while its own note
in the record claimed `contact 0.350`. **Check that a source pose is actually
seated before transferring it**, or the error propagates into every part derived
from it. Matching the tapers, above, avoids the transfer entirely.

> **If you change this:** the same disc is used by all three variant kits, so
> retapering one tab orphans the other two. Keep −0.536 mm/mm, or change the tab
> on `Bottle Cap Lever`, `3 - Rod Middle v1.1` and `21 - Rod Middle` together and
> re-cut the slot to match.

### 2.2 The click detent — serrated rod through a sprung bore & rotary waist ratchet

This is the primary fidget action: push or pull the middle rod and it clicks, and twist the waist and it ratchets.

These are two **separate** mechanisms, not one dual-purpose part. Corrected
2026-08-27 against the shipped meshes; the earlier reading of this section was
wrong in every number, and the error is recorded below because it survived a
long time by being self-consistent.

**[M] The rack.** The rod middles carry sawtooth serrations on both long edges:
pitch **3.17733 mm** (crest spacing, measured 3.177–3.178 and matching
`custom.py:ROD_TOOTH_PITCH`), crest **|z| 6.8901**, V-root **|z| 5.7652** — so
**crest-to-crest 13.780 mm** and **tooth depth 1.125 mm per side**. The flanks
are straight at **40.63°** and the crest is crowned over ±0.41 mm. Both side
clamps carry the same rack, so the rod presents three rack faces, at azimuth
**90° / 210° / 330°**.

> **The 16.02 mm figure is the rod's overall bounding box** at the yoke
> shoulder, not the tooth crest, and 3.000 mm was an autocorrelation result
> rounded onto its own sampling grid.

**[M] The axial detent** is `12`/`13`/`14 - Internal Barrel Spring` alone —
three planar serpentine followers in slots in `08 - Internal Barrel`, one per
rack face. Nothing else touches the rod: the barrel pins `09`/`10`/`11` clear
it by **1.47–3.33 mm** and `20 - Mid Shell Spring` by **1.158 mm**.

**[M] The rotary waist detent** is `20 - Mid Shell Spring`: a flat ring, 4.0 mm
thick, at y = 29.75 .. 33.75, with a **15.84 × 15.84 mm square bore** and three
radial arms through the barrel windows at **30° / 150° / 270°** to
**r 17.20–17.40 mm**, engaging the 33-lobe ratchet of `32 - Mid Shell P02`
(bore r 16.43 .. 17.53) — **33 clicks per turn**, 10.909° pitch.

> **[D] Its square bore is not a linear detent.** 13.780 mm of crest through a
> 15.84 mm bore is **1.03 mm of clearance per side**, and the measured
> clearance to the rod is 1.158 mm. The old claim of 0.09 mm interference came
> from pairing the bore against the rod's bbox instead of its crest.

> **If you change this:** the rack and the followers are one dimension pair;
> the waist spring is independent of both and cannot change the axial feel.
> Measure any change with `tools/score_detent.py`, which reports **force**, not
> just swept volume — swept volume hides a dead band. For the rotary waist,
> 3 arms at 120° only click on whole-multiple lobe counts (33/3 = 11 notches).

### 2.3 The threaded bottom lock

**[M]** `Bottle Cap Lever`'s shaft is threaded over y = 29 .. 59: pitch
**3.200 mm**, radius oscillating **5.78 .. 7.34 mm** (major ⌀14.68, minor ⌀11.56).
**[M]** `01 - Bottom Lock Shell` threads into `08 - Internal Barrel`; the recorded
engagement is at θ = 294°.

### 2.4 The upper shell rotation

**[M]** `28 - Upper Shell Gear` is **not** a gear in the meshing sense — its outer
profile is 48 lobes only **0.54 mm** deep (r 19.98 .. 20.52), i.e. a knurled grip.
Its **bore is 3-lobed** (r 18.60 .. 18.79), which keys it to the body.
**[M]** `29 - Upper Shell Lock Ring` (⌀39.99 × 3.88) and
`30 - Upper Shell Rotating Spring` (y 63.75 .. 79.72) complete the rotating group.

**[M]** The body has **3-fold symmetry**, but the two families are **not
co-located**: barrel pins `09`/`10`/`11` sit at **30° / 150° / 270°** (the
window azimuths) and the followers `12`/`13`/`14` at **90° / 210° / 330°**,
58.5° away from the nearest pin. The gear bore is 3-lobed.

**[D]** A 2-fold-symmetric rod in a 3-fold body gives a **60° azimuth period** —
confirmed by sweep. This is why azimuth answers are only ever defined
mod 60°.

---

## 3. Tactical 7-in-1 — architecture

**[M]** One **common body** (21 parts) plus **three swappable tops**, each a
complete alternative kit. Never combine two tops.

### 3.1 Body stack, bottom to top

Placed `y` ranges from the pose record **[M]**:

| y range | part | role |
|---|---|---|
| −0.35 .. 28.72 | `01 - Bottom Lock Shell` | threads into `08` from below, carries `02`/`03` |
| −0.05 .. 12.24 | `04 - Bottom Shell 01` | outer bottom cap |
| 9.25 .. 19.05 | `05 - Bottom Shell 02` | **inverted** |
| 11.25 .. 19.25 | `06 - Bottom Shell 03` | **inverted** |
| 10.90 .. 13.90 | `02 - Bottom Spring` | flexure, 3.0 mm thick |
| 14.15 .. 28.60 | `03 - Bottom Shell Spacer` | |
| 20.00 .. 53.80 | `32 - Mid Shell P02` | wall **1.75 mm**, inner 33-lobe ratchet |
| 20.00 .. 54.80 | `33 - Mid Shell P01` | wall **1.70 mm**, outer ribbed grip |
| 29.75 .. 33.75 | `20 - Mid Shell Spring` | dual-purpose linear & rotary click detent (§2.2) |
| 20.43 .. 63.24 | `08 - Internal Barrel` | the spine with 3 waist windows and 3 vertical pin channels |
| 45.62 .. 63.13 | `12`/`13`/`14 - Internal Barrel Spring` | 3 off, 120° apart |
| 56.64 .. 61.23 | `09`/`10`/`11 - Internal Barrel Pin` | 3 off, 120° apart |
| 62.00 .. 63.60 | `07 - Internal Barrel Cap` | top barrel seal |
| 55.00 .. 58.88 | `29 - Upper Shell Lock Ring` | |
| 55.00 .. 62.98 | `28 - Upper Shell Gear` | knurled grip, 3-lobe bore |
| 55.00 .. 74.83 | `27 - Upper Shell Top` | wall **3.00 mm** |
| 63.75 .. 79.72 | `30 - Upper Shell Rotating Spring` | |

**[M]** Assembly order for the lower stack is directional and matters:
`04 → inverted 05 → inverted 06`, then `01` inserted **from below**, then `02` and
`03` from above. The rigid `04`–`06` module is raised **1.50 mm** for clearance.

**[M]** Body envelope 41.60 × 80.07 × 41.60 mm (two-piece mid shell);
41.95 (solid), 41.85 × 80.07 × 42.12 (hex).

### 3.2 Mid shell — two-piece, solid, and standardized options

**[M]** `Mid Shell Solid Color` and `Hex Mid Shell Solid Color` each replace
**`32` *and* `33` together** with one piece — 12,640 mm³ ≈ 6,062 + 6,400, same axial seat
`dy = 20.00`, wall 3.20 / 3.30 mm against the two-piece 1.70–1.75 mm. Substituting
one for `33` alone drives a 5,643 mm³ interference.

In the hybrid package, **8 interchangeable mid shell options** are dimensionally standardized to an exact **34.80 mm total height** and **40.00 mm interface diameter** (see `CUSTOM_DESIGN.md` §3).

### 3.3 The tops

| top | parts | contents |
|---|---|---|
| Grenade 6-in-1 | 12 | `15`–`19`, `21`–`26`, `31` (spoon mechanism + rods + locks) |
| Spinner 7-in-1 | 8 | `Spinner Lever 01–08` |
| Bottle 5-in-1 | 2 | `Bottle Cap Lever`, `Bottle Cap Lock` |

**[M]** Spinner geometry as placed: two 10 mm wing plates (`1`/`2 - Rod Right`/
`Left v1.1`) sandwich a 7 mm middle rod (`3`), 27 mm across; all three start at
`y = 18.08`, threading the full body. `1` and `2` are the same part rotated
**exactly 180.00°** about Y at centroid radius **6.628 mm**. `5 - Gear v1.1` is a
20-tooth wheel spinning about **X** (r 16.79 .. 18.02, 6.6 mm thick).

**[M]** `21 - Rod Middle` sits at azimuth **30°** — re-derived 2026-08-22 by
rotating its pose about the toy axis. Overlap against every non-`v1.1` body part
falls to **0.000 mm³** there.

---

## 4. The two generations & Unified Hybrid Architecture

**[M]** The Tactical folder contains **two complete generations**, not one design
plus spares:

| | original | `v1.1` |
|---|---|---|
| rod middle thickness | **9.0 mm** | **7.0 mm** |
| wing rod thickness | 9.0 mm | 10.0 mm |
| barrel internals `09`–`11` | `(1)`/`(2)`/`(3)`, 135.4 mm³ | `v1.1`, 119.6 mm³ |
| barrel springs `12`–`14` | `(3)`/`(2)`/`(1)`, 244.5 mm³ | `v1.1`, 211.7 mm³ |
| spinner top | `Spinner Lever 01–08` | `1`–`5` + `Ring Large` |
| grenade top | all of it | — none — |
| bottle top | both parts | — none — |

**[M]** Both generations keep the **same rack and lock taper** — crest
**13.780 mm**, pitch **3.177 mm**, depth **1.11–1.12 mm per side**, taper
−0.536 mm/mm. The interfaces were held constant across the revision; only
thicknesses moved. (See §2.2: the 16.02 / 3.000 pair quoted here previously was
the bounding box and a rounded autocorrelation, not the crest and pitch.)

**[D] Unified Hybrid Architecture**: In the hybrid package, the generation split was resolved by adopting the **`v1.1` barrel pins and springs** inside the Tactical `08 - Internal Barrel` combined with the full-depth 3-part solid-yoke rod (`Custom_Rod_Middle`, `Custom_Rod_Right`, `Custom_Rod_Left`), locked via transverse cross-keys `06` and `07`.

---

## 5. Fits, clearances and springs

**[M]** In the assembled model, designed interference per part pair runs
**2.6 – 13.0 mm³**. Those are press fits and springs modelled uncompressed, not
errors.

**[M]** Upstream `v1.1` parts, which ship in true assembly coordinates, show
**0.4 – 0.55 mm axial gaps** between stacked parts. Treat ~0.5 mm as the
house clearance for a sliding fit.

**[M]** Every spring is a **printed flexure**, single-body, no metal:

| part | bbox (mm) | vol (mm³) |
|---|---|---|
| `02 - Bottom Spring` | 16.70 × 31.82 × 3.00 | 374.6 |
| `20 - Mid Shell Spring` | 29.97 × 29.57 × 4.00 | 665.1 |
| `30 - Upper Shell Rotating Spring` | 31.07 × 30.63 × 15.97 | 3668.7 |
| `4 - Spring` (v1.1) | 6.70 × 18.00 × 11.70 | 708.1 |
| `Spinner Lever 04 - Spring` | 11.70 × 17.99 × 8.70 | 923.6 |
| `18 - Lever Spring` | 11.70 × 20.52 × 8.70 | 1029.0 |
| `12`–`14 - Internal Barrel Spring` | 8.60 × 17.71 × 4.00 (orig) | 244.5 |
| `12`–`14 - Internal Barrel Spring v1.1` | 3.75 × 17.51 × 8.43 | 211.7 |

---

## 6. Wall thicknesses

**[M]** Median of 48 radial rays at mid-height:

| part | wall |
|---|---|
| `32 - Mid Shell P02` | 1.75 mm |
| `33 - Mid Shell P01` | 1.70 mm |
| `Mid Shell Solid Color` | 3.20 mm |
| `Hex Mid Shell Solid Color` | 3.30 mm |
| `27 - Upper Shell Top` | 3.00 mm |
| `04 - Bottom Shell 01` | 4.30 mm |

---

## 7. Checklist — before you commit a change

1. **Find the twins.** `fidget.twins(part)` — 21 of 110 files are copies of
   another part. A change to one usually has to be made to all.
2. **Do not trust a `"reflection"` label on its own.** All seven Tactical rod locks are **achiral**. Mirroring an achiral part is silently wrong. Test: align the mirrored mesh allowing only proper rotations; ~0 deviation means achiral.
3. **Identify which interface you are touching** (§2) and change both halves.
4. **Check `body_count`, not just `is_watertight`.** A cut that severs a part
   leaves a watertight *two-body* mesh that slices as two objects.
5. **Re-check interference** — `A.interference(items)` should stay in the
   2.6–13.0 mm³ band with every pair explainable as a press fit or an
   uncompressed spring.
6. **Rebuild and diff**: `python tools/export_3d_print_package.py` and `python tools/build_shell_variants_glbs.py`.
7. **Never write into the three product folders.** `fidget.save()` enforces it;
   plain shell commands do not.

---

## 8. Solved & Unsolved Mechanisms

### Solved Mechanisms:
- **Tactical Waist Rotary Ratchet**: Confirmed as a native 33-click detent driven by `20 - Mid Shell Spring` / `09_Custom_Mid_Shell_Spring_33` engaging `32 - Mid Shell P02`'s 33-lobe ratchet through 3 windows in `08 - Internal Barrel`.
- **Transverse Rod Locks (`06` & `07`)**: Identified and positioned as transverse cross-keys locking the 3-part rod assembly through aligned tunnels at $y = 48.654 .. 58.186\text{ mm}$ and $y = 23.654 .. 33.186\text{ mm}$.
- **Tapered Bottom Axial Retainer**: Solved analytically by matching the $-0.536\text{ mm/mm}$ taper on `Spinner Lever 08 - Rod Lock`.
- **Unified Hybrid Assembly**: Solved and packaged as `Hybrid_Grenade_v1.1` (36 parts) and `v1.2` (35 parts), with the solid-yoke 3-piece rod, 8 standardized mid shell variants, and the 4-position folding spinner head.
- **Axial Rod Detent** (`v1.2`, 2026-08-27): rebuilt as a **long-arm C spring on the Spinner Fuse's `11 - Middle Spring` pattern** — two opposed arms at azimuth 90°/270°, housed in new axial pockets cut into `08 - Internal Barrel` (449.8 mm³, 2.3%, outer surface untouched). Rate **1.005 N/mm at 0.831%/mm** against `11`'s 1.207 / 0.714 and v1.1's 2.951 / 1.278. Preloaded 0.40 mm, so the **12% dead band is gone**. The rod also gained a defined stroke — **14.07 mm, about 4.4 clicks** — where it previously had no upward stop and could be pulled out. Built by `tools/build_rod_detent.py`, scored by `tools/score_detent.py`.

### Upstream Open Items (for stock un-modified kits):
- **Upstream Grenade 6-in-1 Spoon Mechanism**: The standalone spoon mechanism (`15 - Lever Base`, `16`/`17`/`19 - Lever Lock Front/Back/Mid`, `18 - Lever Spring`, `31 - Lever`) mates against itself and remains unsolved for the legacy un-unified Grenade-top plate.

---

## 9. Reproducing any measurement here

```python
import sys; sys.path.insert(0, "tools")
import fidget, assembly as A
import numpy as np

rows = {r["part"]: r for r in A.poses("tactical")["parts"]}

rod    = A.posed(rows["21 - Rod Middle"])
spring = A.posed(rows["20 - Mid Shell Spring"])

# cross-section extent at a height
s = rod.slice_plane([0, 31.0, 0], [0, -1, 0]).slice_plane([0, 30.95, 0], [0, 1, 0])
print(np.round(s.bounds[1] - s.bounds[0], 3))

# a horizontal profile, for bores and tooth counts
sec = spring.section(plane_origin=[0, 31.75, 0], plane_normal=[0, 1, 0])
poly, _ = sec.to_2D()
q = max(poly.polygons_full, key=lambda g: g.area)
bore = np.array(q.interiors[0].coords)
print(len(q.interiors), np.round(np.ptp(bore, axis=0), 2))
```
