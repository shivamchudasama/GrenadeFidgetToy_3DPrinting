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

### 2.2 The click detent — serrated rod through a sprung bore

This is the fidget action: push or pull the middle rod and it clicks.

**[M]** The rod middles carry **sawtooth serrations on both long edges**, pitch
**3.000 mm** (autocorrelation, all three rod middles across both generations),
tooth depth **2.22 mm per side**, crest-to-crest **16.02 mm**. On
`21 - Rod Middle` the serrated span runs roughly y = 20.5 .. 42.4 of its 68.4 mm
length.

**[M]** `20 - Mid Shell Spring` is a flat ring, 4.0 mm thick, sitting at
y = 29.75 .. 33.75, with a **15.84 × 15.84 mm square bore**.

**[D]** 16.02 mm of crest through a 15.84 mm bore is a **0.09 mm per-side
interference** — the spring ring deflects as each tooth passes, one click per
3.000 mm of travel. **[M]** In the assembled (rest) pose the rod presents only
~13.8 mm at the spring's height, so it sits in clearance at rest and only clicks
over part of the stroke.

> **If you change this:** rod crest width and the spring bore are one dimension
> pair. Changing the 3.000 mm pitch changes the click feel; changing 16.02 or
> 15.84 changes the click force, and going to clearance kills the click entirely.

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

**[M]** The body has **3-fold symmetry**: barrel pins `09`/`10`/`11` at
**0° / 120° / 240°**, barrel springs `12`/`13`/`14` likewise, and the gear bore is
3-lobed.

**[D]** A 2-fold-symmetric rod in a 3-fold body gives a **60° azimuth period** —
confirmed by sweep (below). This is why azimuth answers are only ever defined
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
| 20.00 .. 53.80 | `32 - Mid Shell P02` | wall **1.75 mm** |
| 20.00 .. 54.80 | `33 - Mid Shell P01` | wall **1.70 mm** |
| 29.75 .. 33.75 | `20 - Mid Shell Spring` | the click detent (§2.2) |
| 20.43 .. 63.24 | `08 - Internal Barrel` | the spine |
| 45.62 .. 63.13 | `12`/`13`/`14 - Internal Barrel Spring` | 3 off, 120° apart |
| 56.64 .. 61.23 | `09`/`10`/`11 - Internal Barrel Pin` | 3 off, 120° apart |
| 62.00 .. 63.60 | `07 - Internal Barrel Cap` | |
| 55.00 .. 58.88 | `29 - Upper Shell Lock Ring` | |
| 55.00 .. 62.98 | `28 - Upper Shell Gear` | knurled grip, 3-lobe bore |
| 55.00 .. 74.83 | `27 - Upper Shell Top` | wall **3.00 mm** |
| 63.75 .. 79.72 | `30 - Upper Shell Rotating Spring` | |

**[M]** Assembly order for the lower stack is directional and matters:
`04 → inverted 05 → inverted 06`, then `01` inserted **from below**, then `02` and
`03` from above. The rigid `04`–`06` module is raised **1.50 mm** for clearance.

**[M]** Body envelope 41.60 × 80.07 × 41.60 mm (two-piece mid shell);
41.95 (solid), 41.85 × 80.07 × 42.12 (hex).

### 3.2 Mid shell — two-piece or one-piece

**[M]** `Mid Shell Solid Color` and `Hex Mid Shell Solid Color` each replace
**`32` *and* `33` together** — 12,640 mm³ ≈ 6,062 + 6,400, same axial seat
`dy = 20.00`, wall 3.20 / 3.30 mm against the two-piece 1.70–1.75 mm. Substituting
one for `33` alone drives a 5,643 mm³ interference. The two-piece version exists
so you can print the band in a second colour.

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
falls to **0.000 mm³** there, against 8.259 mm³ at the previously recorded 42°.
The sweep is 60°-periodic and spans 0.23 .. 33.14 mm³; the minimum is a
**flat-bottomed well 27.5° .. 33.0°**, i.e. a designed clearance, centred on 30°.

> **Sweep a recorded pose, never a reconstructed one.** Rebuilding the rod from
> its source STL at an assumed base height and sweeping *that* gives a flat curve
> — 60.8–64.9 mm³ at every angle — and the false conclusion "no azimuth signal".
> The flatness is an artefact: reconstruction puts the 3.000 mm serrations at a
> different vertical phase than the record, fouling `20 - Mid Shell Spring` by a
> constant ~29.8 mm³ that swamps the real 99.3% spread. In its recorded pose the
> rod clears that spring at 0.000 mm³. Every part here is covered in 3 mm-pitch
> teeth, so this trap applies to all of them:
>
> ```python
> R = trimesh.transformations.rotation_matrix(np.radians(delta), [0, 1, 0])
> m = src.copy(); m.apply_transform(R @ M_recorded)     # not a rebuild
> ```

---

## 4. The two generations — read this before changing any rod

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

**[M]** Both generations keep the **same** 16.02 mm serration crest, 3.000 mm
pitch and −0.536 mm/mm lock taper — the interfaces were held constant across the
revision; only thicknesses moved.

**[M]** The pose record currently uses the **`v1.1`** barrel internals, so every
exported body is **generation-mixed**, and the six original internals are placed
nowhere. This is unresolved, and it is the first item of §9 because everything
else inherits the answer.

> **If you change a rod's thickness you are making a generation change.** Check it
> against *both* barrel-internal sets, not just whichever the record happens to
> load.

---

## 5. Fits, clearances and springs

**[M]** In the assembled model, designed interference per part pair runs
**2.6 – 13.0 mm³**. Those are press fits and springs modelled uncompressed, not
errors. The current worst is 13.0 mm³ between `08 - Internal Barrel` and
`07 - Internal Barrel Cap` — **[?]** unexplained, predates this work, worth a look.

**[M]** Upstream `v1.1` parts, which ship in true assembly coordinates, show
**0.4 – 0.55 mm axial gaps** between stacked parts (`3 - Rod Middle v1.1` top at
80.18 against `5 - Gear v1.1` base at 80.73; body top 79.72). Treat ~0.5 mm as the
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

**[?]** Their stiffness is set by the flexure section, which is close to the
bbox's smallest dimension. Thinning any of these by a layer or two is the obvious
lever for a lighter action — and the obvious way to snap one.

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

**[?]** The 1.70–1.75 mm mid shells are about four perimeters at 0.4 mm nozzle —
thin them and the band will go translucent and lose hoop stiffness where the
click spring loads it.

---

## 7. Checklist — before you commit a change

1. **Find the twins.** `fidget.twins(part)` — 21 of 110 files are copies of
   another part. A change to one usually has to be made to all.
2. **Do not trust a `"reflection"` label on its own.** It is whichever of 48
   frames the search landed on. All seven Tactical rod locks are **achiral**, and
   `parts_index.json` is self-inconsistent about them. Mirroring an achiral part
   is silently wrong. Test: align the mirrored mesh allowing only proper
   rotations; ~0 deviation means achiral.
3. **Identify which interface you are touching** (§2) and change both halves.
4. **Check `body_count`, not just `is_watertight`.** A cut that severs a part
   leaves a watertight *two-body* mesh that slices as two objects.
5. **Re-check interference** — `A.interference(items)` should stay in the
   2.6–13.0 mm³ band with every pair explainable as a press fit or an
   uncompressed spring.
6. **Rebuild and diff**: `python tools/build_tactical_body.py`,
   `python tools/build_tactical_variants.py`, then
   `python tools/fidget.py check` (expect 110/110) and
   `python tools/build_index.py`.
7. **Never write into the three product folders.** `fidget.save()` enforces it;
   plain shell commands do not.

---

## 8. What is *not* understood

Being explicit so nobody re-derives a dead end:

- **The grenade spoon mechanism** (`15 - Lever Base`, `16`/`17`/`19 - Lever Lock
  Front`/`Back`/`Mid`, `18 - Lever Spring`, `31 - Lever`). Unsolved. These mate
  with *each other*, not the body, so body-contact scoring has no discriminating
  power — measured: a known-correct head scores 0.07–0.11 and 6 mm off-true still
  scores 0.065–0.097.
- **`22 - Rod Lock 04` and `26 - Rod Lock 03`.** Solid 9.33 × 13.78 × 2.0 mm
  plates, no slot, no hole, so §2.1 does not apply. **[?]** Their 13.78 mm is
  suspiciously close to the 13.40 mm rod section — that is the lead.
- **`24`/`25 - Rod Left`/`Right` placement.** 4.00 mm plates, near-mirror but
  *not* an exact congruence (2416.5 vs 2403.6 mm³, 0.5% apart). **[D]** They must
  be related by a rotation about the toy axis, as `1`/`2 - Rod v1.1` are.
- **Which generation is "current"**, and whether the body should ship with
  generation-matched internals per variant (§4).
- **The 13.0 mm³ `08`/`07` overlap** (§5).
- **Grenade 5-in-1 and Spinner Fuse 5-in-1 internals.** Both ship in assembly
  coordinates and were verified as correct-as-downloaded (3 overlapping pairs of
  276, max 7.5 mm³; and 2 of 171, max 5.1 mm³), so no fitting was ever needed —
  and consequently nobody has taken their mechanisms apart. `04_Gear_Bottom_Click`
  (161k triangles, the largest part here) is presumably their click mechanism.

---

## 9. Open work, in order

The order matters — item 1 gates the rest. The pose record
(`Derivatives/tactical/Tactical_variants_poses.json`) currently places **34 of the
59** Tactical files; the 25 unplaced are 10 grenade-top parts, 2 lever editions,
`Spinner Lever 01`–`07`, and the 6 original barrel internals.

1. **Settle the generation question** (§4). All three exported bodies mix
   generations and the six original barrel internals are placed nowhere. Decide
   whether to ship one body per generation, or one body with generation-matched
   internals per variant. The grenade and original-spinner tops are
   original-generation (9.0 mm rods) and are currently being fitted to a body
   carrying `v1.1` internals, so every fit below depends on this.
2. **Solve `22 - Rod Lock 04` and `26 - Rod Lock 03`** (§8). Solid 2 mm plates
   with no slot — §2.1 does not apply and there is nothing to transfer. Start
   from the 13.78 mm vs 13.40 mm coincidence against the rod section.
3. **Solve the grenade spoon sub-assembly** (`15 - Lever Base`, `16`/`17`/`19`,
   `18 - Lever Spring`, `31 - Lever`) against *itself*, then seat the finished
   unit on the body as one rigid group. This is the hard one, and the reason the
   grenade top is unsolved: the parts mate with each other, so body-contact
   scoring has no discriminating power (§8). `23 - Rod Lock 01` was solved this
   way — against its mating part, not against the body — and the approach
   generalises.
4. **Place `24`/`25 - Rod Left`/`Right`**, constrained to be related by a rotation
   about the toy axis, as `1`/`2 - Rod v1.1` are at radius 6.628 mm (§3.3). The
   earlier attempt failed by putting them at the same radius only 36° apart,
   which is wrong for a handed pair.
5. **Place `Spinner Lever 06`/`07 - Rod Lock`** — the same two thin plates as
   item 2, so solve them together. There is no `v1.1` rod lock, so these stay
   live parts of the spinner top: a complete spinner top is 6 + 3 locks = 9
   parts, of which `Spinner Lever 08` is already placed.
6. **Emit the attachments** as standalone sub-assemblies in
   `Derivatives/tactical/Attachments/`, then as body × top combinations. Once
   those exist the combined `Tactical_Spinner_7in1_*MidShell*` files become
   redundant with `Body/ × Attachments/` — **ask before deleting anything.**

Rebuild after any of these with `tools/build_tactical_body.py` and
`tools/build_tactical_variants.py`; both read the pose record, which is the source
of truth. Do not re-run a search to reproduce an assembly that already exists.

---

## 10. Reproducing any measurement here

```python
import sys; sys.path.insert(0, "tools")
import fidget, assembly as A
import numpy as np

rows = {r["part"]: r for r in A.poses("tactical")["parts"]}

# A.posed() gives toy coordinates. fidget.load() gives the file as-is, which for
# these two parts is PLATE coordinates -- sectioning that at a toy height finds
# nothing at all. This is the single most common mistake here (see section 1).
rod    = A.posed(rows["21 - Rod Middle"])
spring = A.posed(rows["20 - Mid Shell Spring"])

# cross-section extent at a height -- how every dimension above was taken
s = rod.slice_plane([0, 31.0, 0], [0, -1, 0]).slice_plane([0, 30.95, 0], [0, 1, 0])
print(np.round(s.bounds[1] - s.bounds[0], 3))      # -> [13.434  0.05  12.782]

# a horizontal profile, for bores and tooth counts
sec = spring.section(plane_origin=[0, 31.75, 0], plane_normal=[0, 1, 0])
poly, _ = sec.to_2D()
q = max(poly.polygons_full, key=lambda g: g.area)
bore = np.array(q.interiors[0].coords)             # numpy 2.x: np.ptp(), not .ptp()
print(len(q.interiors), np.round(np.ptp(bore, axis=0), 2))   # -> 1 [15.84 15.84]
```

Pitches were taken by autocorrelating a width-versus-height profile sampled at
0.05–0.1 mm; tapers by a linear fit over the tab length; wall thicknesses as the
median solid run along 48 radial rays; interference by manifold boolean.
