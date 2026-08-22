# Tactical assembly — handoff

Status as of **2026-08-22**. Read `CLAUDE.md` first for the repo rules; this file
only covers the Tactical assembly work and what is left to do.

**Goal:** assemble the Fidget Fuse Tactical 7-in-1 as a *body* (three cosmetic
mid-shell options) plus three swappable *attachments* (bottle, spinner, grenade).

- Phase 1 — body in three mid-shell variants: **done**, files written and rebuilt
  from the final pose record.
- Phase 2 — attachments: known poses are exported, but the spinner locks and most
  of the grenade top remain unsolved; remaining work is below.

---

## 0. Durable implementation — do not depend on temp files

The reusable assembly implementation is now in the repository:

| file | purpose |
|---|---|
| `tools/assembly.py` | reads the pose record, constructs scenes, checks interference, and writes assembled/exploded 3MF, GLB, and STL files |
| `tools/build_tactical_body.py` | builds all three common-body variants in `Derivatives/tactical/Body/` |
| `tools/build_tactical_variants.py` | builds all current body-plus-top combinations in `Derivatives/tactical/` |

The earlier fitting experiments were scratch work only. The saved JSON record and
the three files above are sufficient to reproduce the current exports.

---

## 1. Environment

Verified working, no install needed:

```
python 3.14   trimesh 4.12.2   numpy 2.4.3   scipy 1.18.0   manifold3d (present)
```

`trimesh.triangles` emits a benign `RuntimeWarning: invalid value encountered in
divide` on some parts — it is the zero-volume-flap repair, not an error.

Load parts only through the toolkit:

```python
import sys; sys.path.insert(0, "tools")
import fidget, assembly as A
```

---

## 2. Coordinate frame and the pose record

**Frame:** Y up, toy axis at X = Z = 0, millimetres.

The authoritative record is
**`Derivatives/tactical/Tactical_variants_poses.json`** — 34 entries, each with a
4×4 `matrix`, a `group`, and a `note` carrying the confidence evidence
(`contact`, `penetration`, `runner-up` scores). Groups:

| group | n | note |
|---|---|---|
| `common` | 21 | the body — but see §5.7, it is generation-mixed |
| `spinner-7in1 top` | 7 | 6 in upstream assembly coords + `Spinner Lever 08 - Rod Lock` |
| `bottle-5in1 top` | 2 | solved; `Bottle Cap Lock` corrected 2026-08-22 (§5.2) |
| `grenade-6in1 top` | 2 | `21 - Rod Middle` and `23 - Rod Lock 01` |
| `cosmetic` | 2 | `Mid Shell Solid Color`, `Hex Mid Shell Solid Color` |

It covers 34 of the 59 Tactical files; 25 remain unplaced (10 grenade top,
2 lever editions, 7 `Spinner Lever 01`–`07`, 6 original barrel internals).

**This record is the source of truth.** All current body and body-plus-top exports
were regenerated from it after the final lower-stack correction. Rebuild from the
JSON; do not re-run a search merely to reproduce an existing assembly.

---

## 3. Scene builder and repeatable Tactical builds

The scene-building code was moved out of the temp scratchpad into the repo. It is
pose-record driven:

```python
items = A.items_from_poses("tactical", groups=["common"],
                           exclude=("32 - Mid Shell P02", "33 - Mid Shell P01"),
                           include=("Hex Mid Shell Solid Color",),
                           order=ORDER)          # -> [(name, trimesh.Trimesh)]
files, bad = A.build(items, "Tactical_Body_MidShell_Hex", "tactical/Body")
```

| function | purpose |
|---|---|
| `poses(product)` / `posed(entry)` | read the JSON; apply one matrix to its source STL |
| `items_from_poses(...)` | select by `groups` / `include` / `exclude`, sort by `order` |
| `interference(items, min_mm3=1.0)` | pairwise manifold boolean, bbox-rejected first; returns `(volume, a, b)` largest first |
| `explode(items)` | core/satellite split — concentric parts spread along Y, off-axis parts pushed out radially, so one long rod does not stretch the whole column |
| `scene` / `write` / `build` | colour, explode, report, and emit all six files |

`build()` writes `<stem>_assembled.{3mf,glb,stl}` and `<stem>_exploded.{3mf,glb,stl}`.
`.3mf`/`.glb` keep parts separate, named by source filename and individually
coloured; `.stl` is the merged single mesh.

---

## 4. Phase 1 — done

Written to **`Derivatives/tactical/Body/`** (18 files):

| variant | parts | envelope (mm) | mid shell |
|---|---|---|---|
| `Tactical_Body_MidShell_2pc` | 21 | 41.60 x 80.07 x 41.60 | `32 - Mid Shell P02` + `33 - Mid Shell P01` |
| `Tactical_Body_MidShell_Solid` | 20 | 41.95 x 80.07 x 41.95 | `Mid Shell Solid Color` |
| `Tactical_Body_MidShell_Hex` | 20 | 41.85 x 80.07 x 42.12 | `Hex Mid Shell Solid Color` |

Two-piece common-body bounds: `[-20.78, -0.35, -20.80] .. [20.82, 79.72, 20.80]`.

Interference (pairs over 1 mm³) — all press-fit / uncompressed-spring level:

```
2pc    10 pairs   13.0 (08 Barrel / 07 Barrel Cap)  11.5 (32/33)  6.4 (32/20)  4.6 (30/27)
Solid   8 pairs   13.0 (08/07)  4.6 (30/27)  3.1 (05/02)  2.6 (01/03)
Hex     8 pairs   13.0 (08/07)  4.6 (30/27)  3.1 (05/02)  2.6 (01/03)
```

The `08 - Internal Barrel` / `07 - Internal Barrel Cap` 13.0 mm³ overlap is present
in every variant and predates this session — it comes from the barrel-pin solve,
not from the mid-shell choice. Worth a second look but not a blocker.

Run `python tools/build_tactical_body.py` to regenerate the three bodies, then
`python tools/build_tactical_variants.py` to regenerate the five current
body-plus-top combinations. Both builders read the same JSON record and use the
same `ORDER` list.

### Final lower-stack correction — do not undo

The exact user-guided construction order is: **`04 → 05 → flipped 06`**. `04` is
unflipped and snap-seated to the inverted `05`; `06` is upside down relative to
its source part. Insert `01 - Bottom Lock Shell` into that shell stack **from
below**, then insert `02 - Bottom Spring` and `03 - Bottom Shell Spacer` from
above. In the saved final pose, `01` is thread-seated into `08 - Internal Barrel`
at theta 294 degrees and carries `02`/`03` on that axis; it is no longer hanging
below the barrel. The rigid `04`/`05`/`06` outer module was raised **1.50 mm** for
clearance.

Exploded column order (`ORDER` in `tools/build_tactical_body.py`) is bottom → top
and follows that construction sequence: `04, 05, 06, 01, 02, 03, [mid shell], 20,
08, 09-11 pins, 12-14 springs, 07, 28, 29, 30, 27`.

Visual check: all three render as the same body with only the shell changing — hex
faceted / striped solid / two-piece. The one-piece shells correctly span both the
mid section and the upper band, i.e. they replace `32` **and** `33` together.

---

## 5. Phase 2 — remaining attachment work

### 5.1 The spinner attachment is incomplete as currently built

The `v1.1` revision group covers only `1`–`5` + `Ring Large`. There is **no `v1.1`
rod lock**, so `Spinner Lever 06/07/08 - Rod Lock` are still live parts of the
spinner top. Complete spinner top = 6 + 3 locks = **9 parts**.

`Spinner Lever 08 - Rod Lock` is now **placed** (see §5.2), so
`Tactical_Spinner_7in1_assembled` is 28 parts and the two thin locks
`Spinner Lever 06/07` remain.

### 5.2 The rod locks mate on a tapered tab — solved for the 15.6 mm disc

**The earlier plan in this section was wrong and has been replaced.** It proposed
transferring the solved `Bottle Cap Lock` pose onto `23 - Rod Lock 01` through a
reflection. Two things were wrong with it:

- **The source pose was not seated.** As recorded, `Bottle Cap Lock` sat at
  y 92.60..97.40, 2.00 mm off-axis, **0.436 mm clear of the lever and touching no
  part in the assembly** (0.000 of its surface within 0.3 mm of anything, no body
  part within 5 mm). Its note claimed "contact 0.350". Transferring it would have
  propagated a floating pose into three more parts.
- **The relation is not a reflection.** All seven rod locks are **achiral** (the
  mirror maps onto the original under a proper rotation, deviation 0.0000 mm), so
  `parts_index.json`'s "reflection" label is an artifact of its 48-frame search
  reporting whichever frame it hit first. The index is self-inconsistent here:
  `23`≡`SL08` and `BCL`≡`SL08` are both labelled *rotation*, which cannot coexist
  with `23`≡`BCL` being a reflection unless the part is achiral. Every transfer
  between these locks is a proper rotation — never mirror a placement.

**The real mechanism.** The 15.6 mm disc (`23 - Rod Lock 01` ≡ `Bottle Cap Lock`
≡ `Spinner Lever 08 - Rod Lock`) is a **slotted retaining washer**: solid over its
lower half, with a U-slot cut in from one edge through the upper half. The slot is
**tapered**, and it matches a **tapered tab** on the mating part:

| | free end | +2.4 mm in | slope |
|---|---|---|---|
| lock slot | 5.38 mm | 4.06 mm | −0.55 mm/mm |
| `Bottle Cap Lever` foot | 5.102 mm | 3.816 mm | −0.536 mm/mm |
| `3 - Rod Middle v1.1` foot | 5.102 mm | 3.816 mm | −0.536 mm/mm |
| `21 - Rod Middle` tab | 5.102 mm | 3.816 mm | −0.536 mm/mm |

It is a self-locking wedge: slide it on sideways and the taper holds it. The tab
is 13.403 mm wide on the lever, 7.000 mm on the v1.1 rod, 9.000 mm on `21`, in a
14.1 mm-deep slot.

**Three poses follow from this and are now in the record:**

| part | on | contact | rod pen. | body clash |
|---|---|---|---|---|
| `Bottle Cap Lock` (**corrected**) | `Bottle Cap Lever` | 0.129 | 0.000 | 0.000 |
| `Spinner Lever 08 - Rod Lock` (**new**) | `3 - Rod Middle v1.1` | 0.060 | 0.000 | 0.000 |
| `23 - Rod Lock 01` (**new**) | `21 - Rod Middle` | 0.079 | 0.000 | 0.000 |

Height is fixed analytically by the taper match, not searched. Along the slot the
disc is free to slide; the surrounding parts pin it to a window under 1 mm wide,
and it is seated at the deep end of that window. For the spinner lock the window
is `+0.40..+1.00` mm once the v1.1 wing rods are included — outside it the lock
fouls `2 - Rod Left v1.1` or `03 - Bottom Shell Spacer`.

**Two caveats, both recorded in the notes:**

- The **slot-mouth direction is a free 180° choice** in all three cases — the two
  options score identically (spread 0.0000), since the tab is symmetric. It only
  says which side the lock was slid on from.
- `23 - Rod Lock 01` **inherits the azimuth of `21 - Rod Middle`**, which is itself
  uncertain (§5.3). Its pose is rigid *relative to* `21`, so it stays correct if
  `21` is later re-azimuthed — re-derive it from `21` rather than keeping the
  absolute matrix.

**`22 - Rod Lock 04` and `26 - Rod Lock 03` are still unsolved.** They are not
discs: both are solid 9.33 × 13.78 × 2.0 mm plates with no slot and no through
hole, so the tapered-tab mechanism does not apply to them and there is nothing to
transfer. Their 13.78 mm dimension is suspiciously close to the 13.40 mm rod
cross-section, which is the lead worth following.

### 5.3 `21 - Rod Middle`'s azimuth — SOLVED at 30°

**Was 42°; re-derived to 30° on 2026-08-22.** The rod now clears every non-`v1.1`
body part at exactly **0.000 mm³**, against **8.259 mm³** at 42° (all of it against
`30 - Upper Shell Rotating Spring`). Only 0.227 mm³ remains, against
`13 - Internal Barrel Spring v1.1` — a generation-mismatched part, see §5.7.

The method matters, because an earlier attempt in this session got the opposite
answer:

- **Wrong way (don't repeat it):** rebuild the rod from its source STL at an
  assumed base height and sweep the azimuth. That gave a *flat* curve, 60.8–64.9
  mm³ at every angle, and the conclusion "no azimuth signal". The flatness was an
  artefact — reconstructing the rod put its 3.000 mm serrations at a different
  vertical phase than the record, so it fouled `20 - Mid Shell Spring` by a
  constant ~29.8 mm³ that swamped everything. In its *recorded* pose the rod
  clears that spring at 0.000 mm³.
- **Right way:** rotate the **recorded pose** about the toy axis, so nothing but
  the azimuth changes:

  ```python
  R = trimesh.transformations.rotation_matrix(np.radians(delta), [0, 1, 0])
  m = src.copy(); m.apply_transform(R @ M_recorded)
  ```

  That sweep spans **0.23 .. 33.14 mm³ — a 99.3% spread**, with minima every
  **60°** (the body is 3-fold symmetric, the rod 2-fold). The minimum is a
  **flat-bottomed well from 27.5° to 33.0°**, i.e. a designed clearance rather
  than a touch point, centred on **30°**. 42° sat on the shoulder of that well.

`23 - Rod Lock 01` was rotated with it, being rigid to the rod, and still seats at
0.000 mm³ against both the rod and the body.

The height was never in doubt and is unchanged: base `y = 18.28`, cross-checked
against `18.08` for the v1.1 rod.

**General lesson for the remaining parts:** sweep a *recorded* pose, never a
reconstructed one. Reconstruction silently changes the phase of the serrations,
and these parts are covered in 3 mm-pitch teeth.

### 5.4 Structural analogy — the spinner top, as placed

```
1 - Rod Right v1.1    x -13.50 .. -3.50    y  18.08 .. 115.04
2 - Rod Left  v1.1    x   3.50 .. 13.50    y  18.08 .. 115.04
3 - Rod Middle v1.1   x  -3.50 ..  3.50    y  18.08 ..  80.18
4 - Spring            x  -3.35 ..  3.35    y  63.48 ..  81.48
5 - Gear v1.1         x  -3.30 ..  3.30    y  80.73 .. 116.39
Ring Large            x -12.50 .. 12.50    y  86.09 .. 112.02
```

Two 10 mm wing plates sandwich a 7 mm middle rod — 27 mm total across. All three
rods start at the same `y = 18.08`, i.e. they thread the full body (body top is
`y = 79.72`). `1` and `2` are the same part rotated exactly **180.00°** about Y at
centroid radius **6.628 mm** — so the grenade's `24`/`25` pair should likewise be
related by a rotation about the toy axis, at a radius to be determined.

### 5.5 What the grenade parts actually are

Rendered flat-on and iso (`gren_parts_top.png`, `gren_parts_iso.png`). Dimensions
are raw plate-coordinate bboxes.

| part | bbox (mm) | vol (mm³) | what it is |
|---|---|---|---|
| `21 - Rod Middle` | 68.43 × 16.02 × 9.00 | 5003.8 | plunger rod, integral coil spring mid-span, forked foot, notched head — **SOLVED (azimuth suspect)** |
| `24 - Rod Left` | 74.92 × 35.39 × 4.00 | 2416.5 | 4 mm plate: spring plunger + flat footplate with two holes and a wedge |
| `25 - Rod Right` | 74.92 × 35.39 × 4.00 | 2403.6 | mirror-handed twin of `24` — near-mirror but **not** an exact congruence (13 mm³ apart, 0.5%) |
| `22 - Rod Lock 04` | 9.33 × 13.78 × 2.05 | 248.9 | thin scalloped key/washer |
| `26 - Rod Lock 03` | 9.33 × 13.78 × 2.00 | 239.2 | ditto, slightly thinner |
| `23 - Rod Lock 01` | 15.60 × 15.60 × 4.80 | 706.7 | 15.6 mm slotted disc — caps the rod stack |
| `15 - Lever Base` | 43.90 × 30.42 × 8.56 | 4048.2 | L-shaped bracket, round pivot hole, scalloped edge |
| `16 - Lever Lock Front` | 4.38 × 24.03 × 3.07 | 191.2 | thin wedge bar |
| `17 - Lever Lock Back` | 17.00 × 5.20 × 4.35 | 237.1 | headed pin |
| `19 - Lever Lock Mid` | 8.30 × 6.00 × 3.00 | 90.7 | small pin |
| `18 - Lever Spring` | 11.70 × 20.52 × 8.70 | 1029.0 | serpentine flat spring with ball end |
| `31 - Lever` | 60.21 × 14.00 × 3.00 | 2413.8 | the grenade spoon |

`15`–`19` + `31` form a grenade spoon mechanism that mates **to itself**, which is
exactly why body-contact scoring failed on it (see `unsolved_reason` in the pose
record: the known-correct spinner head scores 0.07–0.11 against the body and 6 mm
off-true still scores 0.065–0.097 — no discriminating power).

`Lever Fidget Fuse Edition.step.stl` and `Lever Stripes Edition.step.stl` are
cosmetic replacements for `31 - Lever`, identical in envelope and volume
(2413.8 vs 2413.9 mm³). They inherit whatever pose `31` gets.

### 5.6 Upstream assembly instructions

`D:\3D Printing\Fidget Fuse\Part 1.webp`, `Part 2.webp`, `Part 3.webp` — 1080×1080
each, official assembly-instruction images — were reviewed during the lower-body
correction. They are useful for the staged body assembly, but did not resolve the
grenade spoon mechanism or the rod azimuth. Recheck them when beginning that
sub-assembly work. Reading the parent folder is allowed; writing to it is not.

### 5.7 The body mixes two part generations, and six files are unplaced

`parts_index.json` and the pose record disagree with the folder. There are **two
complete generations** of the barrel internals, and the record uses only one:

| original (unplaced) | v1.1 (in the record) | vol |
|---|---|---|
| `09 - Internal Barrel (1)` | `09 - Internal Barrel Pin v1.1` | 135.4 vs 119.6 |
| `10 - Internal Barrel (2)` | `10 - Internal Barrel v1.1` | 135.4 vs 119.6 |
| `11 - Internal Barrel (3)` | `11 - Internal Barrel v1.1` | 135.4 vs 119.6 |
| `12/13/14 - Internal Barrel Spring (3)/(2)/(1)` | `12/13/14 - ... Spring v1.1` | 244.5 vs 211.7 |

These are different parts, not duplicates. `CLAUDE.md`'s "common body = 21 parts,
`01`–`14`, ..." counts the **original** six; the pose record's `common` group
contains the **v1.1** six. So all three exported bodies are mixed-generation
builds, and **`09`–`14` `(1)/(2)/(3)` appear nowhere in the record** — they are 6
of the 27 unplaced files.

This matters beyond bookkeeping: the grenade and original-spinner tops are
original-generation (9.0 mm rods), and they are currently being fitted to a body
carrying v1.1 internals. Deciding whether to ship one body per generation, or one
body with a generation-matched barrel per variant, is the next structural
decision — and §5.3's azimuth question depends on it.

---

## 6. Remaining work

Reordered after the 2026-08-22 session; items 1, 2 and 5 of the previous list are
done or superseded.

1. **Settle the generation question** (§5.7). Six original barrel internals are
   unplaced and the exported bodies mix generations. This gates the azimuth work,
   so do it first.
2. ~~**Re-derive `21 - Rod Middle`'s azimuth**~~ — **done**, 30° (§5.3).
   `23 - Rod Lock 01` moved with it.
3. **Solve `22 - Rod Lock 04` and `26 - Rod Lock 03`** (§5.2). Solid 2 mm plates,
   no slot — the tapered-tab mechanism does not apply. Start from the 13.78 mm vs
   13.40 mm coincidence against the rod cross-section.
4. **Solve the grenade spoon sub-assembly** (`15`, `16`, `17`, `18`, `19`, `31`)
   against *itself*, then seat the finished unit on the body as one rigid group.
   Still the hard part, and still the reason the top is unsolved.
5. **Place `24`/`25 - Rod Left/Right`**, constrained to be related by a rotation
   about the toy axis (§5.4). The earlier attempt failed by putting them at the
   same radius only 36° apart, which is wrong for a handed pair.
6. **Place `Spinner Lever 06/07 - Rod Lock`** — the same two thin plates as
   item 3, so solve them together.
7. **Emit the attachments** as standalone sub-assemblies
   (`Derivatives/tactical/Attachments/`) and as body × top combinations.

### Acceptance checks

- `python tools/fidget.py check` → 110/110 watertight.
- `A.interference(items)` on any new assembly: no pair much over ~13 mm³, and any
  that appears should be explainable as an uncompressed spring or a designed
  press fit.
- Rebuild from the JSON and diff bounds/volume against the written STL, as in §2.
- Re-run `tools/build_index.py` after anything changes under `Originals/`.

---

## 7. Gotchas that will bite

- **Never write into the three product folders or anywhere outside `Originals/`.**
  `fidget.save()` enforces this, but plain shell commands do not.
- **`.stl.stl`** — 45 of 59 Tactical files carry a doubled extension upstream.
  Do not strip it.
- **A bare number is ambiguous.** Tactical has two overlapping series; both contain
  09/10/11 and 12/13/14. `fidget.load("11")` raises and lists candidates. Match on
  the full filename or pass `product=`.
- **Each variant ships a complete kit** — three Rod Middles, three Rod Locks, etc.
  They are alternatives. Never put two kits in one assembly.
- **`15`–`19` and `21`–`26` are grenade-specific**, not common, despite falling
  inside the `01`–`30` numbering.
- **Check `body_count` after every cut**, not just `is_watertight`.
- **Change a part, change its twins** — `fidget.twins(part)` returns
  `(file, "rotation"|"reflection", deviation_mm)`. A reflected twin needs the
  mirrored edit.
- `Mid Shell Solid Color` / `Hex Mid Shell Solid Color` replace `32` **and** `33`
  together. Dropped in place of `33` alone they interfere by 5643 mm³.
- These are meshes, not CAD. Do not convert to STEP to "make it parametric".

---

## 8. Current contents of `Derivatives/tactical/`

Flat in `tactical/` (33 files), all regenerated from the pose record on
2026-08-22:

```
Tactical_Bottle_5in1_{assembled,exploded}.{3mf,glb,stl}      23 parts
Tactical_Spinner_7in1_{assembled,exploded}.{3mf,glb,stl}     28 parts  (missing SL 06/07)
Tactical_Spinner_7in1_HexMidShell_{assembled,exploded}.*     27 parts
Tactical_Spinner_7in1_MidShellSolid_{assembled,exploded}.*   27 parts
Tactical_Grenade_6in1_{assembled,exploded}.{3mf,glb,stl}     23 parts (partial top)
Tactical_Grenade_6in1_exploded_with_unsolved_kit.{3mf,glb}   + 10 unsolved as a kit column
Tactical_variants_poses.json                                 34 pose entries
```

Body variants in `tactical/Body/` (18 files) — unchanged by this session:

```
Body/Tactical_Body_MidShell_{2pc,Solid,Hex}_{assembled,exploded}.{3mf,glb,stl}
```

**The unsolved-kit file is now part of the build.** It used to be a one-off and
had gone stale against the record — it still carried the pre-correction azimuths
for `02 - Bottom Spring` (12.03 mm out) and `03 - Bottom Shell Spacer` (8.81 mm).
`build_tactical_variants.build_grenade_with_kit()` regenerates it, and
`assembly.kit_column()` reproduces the original column layout exactly (verified
to 0.0000 mm): parts laid flat, source +Z up, centred at x = 95, z = 0, stacked
from y = 0 with a uniform 6 mm gap, in the record's `unsolved_grenade_top` order.

Once the attachments land, the older combined `Tactical_Spinner_7in1_*MidShell*`
files may become redundant with `Body/ × Attachments/` and are candidates for
removal — **ask the user before deleting anything.**

## 9. Documentation status

`CLAUDE.md` and this handoff were updated on 2026-08-22 after the final lower-stack
correction, and this handoff again later the same day after the rod-lock work
(§5.1, §5.2, §5.3, §5.7, §6, §8). Preserve the pose record and builders as the
durable source for the next agent.

**`CLAUDE.md` has not yet been updated for §5.7** — its "common body … 21 files,
`01`–`14`" line and its `Assemblies` part counts are now out of step with the
record. Raise that with the user.
