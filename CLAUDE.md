# CLAUDE.md

## Routine

After a **significant change** — one that makes something in this file wrong or incomplete (files added/renamed/reorganized, a new convention adopted, git/LFS setup changed) — say which section is affected and ask:

> Would you like to modify `CLAUDE.md` accordingly?

Do not ask on turns that change nothing here (questions, inspection, small edits that fit existing conventions). Keep this file lean — only what's needed to understand the repo.

## Scope — stay inside the repo root

**This repo, `D:\GIT_Repo\GrenadeFidgetToy_3DPrinting\`, is the whole working area. Never create, modify, move, rename or delete anything outside it without asking first.** Everything needed is in here: the three product folders, `tools/`, and `Derivatives/`.

- The upstream source `D:\3D Printing\Fidget Fuse\` holds the `.zip` downloads, the `+`-named unpacked folders these were copied from, `.webp` assembly images, `.3mf` slicer projects, and the `Originals\` folder this repo was copied out of. **Reading it is fine. Writing, moving or deleting is not** — ask, and say exactly which file and why.
- This extends to anywhere else on the machine: no writes to sibling project folders, no edits to global config, no new directories next to the repo.
- If a task seems to need a file outside the repo, stop and ask rather than reaching for it. A plausible reason is not permission.
- Temporary scratch files are the one exception — put them in the session scratchpad, never next to the parts.

`fidget.save()` enforces the outer half of this in code: it refuses any path resolving outside the repo root, and refuses the three pristine product folders. It derives that root as the parent of `tools/`, so it followed the move into git automatically — but its own docstrings still say `Originals/`. That guard is a backstop, not the rule — the rule applies to every tool, including plain shell commands.

## Companion documents

- **`DESIGN.md`** — how the toys work mechanically: the four recurring interfaces (tapered lock tab, click detent, thread, upper-shell rotation), the body stack with heights, wall thicknesses, fits and clearances, and a "before you commit a change" checklist. Read it before modifying any part's geometry. Every number is tagged measured / derived / guessed.
- **`TACTICAL_ASSEMBLY_HANDOFF.md`** — assembly-solving status: what is placed, what is not, what has been tried and ruled out.

## Repository nature

A **3D printing asset directory** holding pristine downloaded parts for three fidget-toy products. 110 STL files and one zip, 52 MB. The only authored content is `tools/` and `Derivatives/`; nothing in the three product folders is ours. No dependency manifest and no test runner — **do not fabricate build/lint/test commands**. There is a small toolkit for modifying the parts; see **Modifying parts**.

All 110 files are **binary STL** and every one carries the same `MW 1.0 <n> US` header, so the whole set came off one exporter. Sizes check out as `84 + 50 × triangles` with no mismatches (verified 2026-08-21).

**These are meshes, not CAD, and cannot be made parametric.** STL stores triangles only — no sketches, no extrudes, no feature tree, no analytic surfaces. Converting to STEP does **not** recover any of that: it wraps each triangle as a planar B-rep face, so `04_Gear_Bottom_Click` becomes a "solid" with 161,232 flat faces. Measured on 2026-08-21 at ~3.9 KB per triangle, an exact tessellated STEP of all 110 parts is **~3.7 GB**, and OCC booleans at that face count are impractical. Do not offer STL→STEP as a route to parametric editing. If a part genuinely needs to be parametric, it has to be **remodelled by hand** from measurements.

## Layout

Everything lives at the repo root: three pristine product folders, plus the toolkit and its output.

- `tools/` — `fidget.py` (the toolkit), `assembly.py` (pose-record scene builder, including `kit_column()` for parts with no pose), `build_tactical_body.py` / `build_tactical_variants.py` (regenerate Tactical exports — the latter also emits the unsolved-kit file), `build_index.py` (regenerates `parts_index.json`), `example_modify.py` (copyable template).
- `Derivatives/` — output, one subfolder per product. Created by `fidget.save()`. Holds 63 files as of 2026-08-22: assembled and exploded models for all three products, the derived-pose JSON for Tactical, and its `tactical/Body/` exports. See **Assemblies**. Modified parts belong here too. **Its `.stl`/`.glb`/`.3mf` output is gitignored and is not on the remote** — see **Git**.

The three product folders are **pristine upstream and read-only** — never write into them. They are flat, with no subdirectories:

- `Fidget Fuse Grenade 5-in-1 Snap-Fit Fidget Toy/` — 24 numbered parts (`01_`–`24_`, underscore-separated names) plus 6 `v2` revisions, plus `Fidget-Fuse Grenade All Parts.zip`. That zip holds **exactly the 24 non-v2 STLs** — it is the original download, and the `v2` files arrived separately. 552k triangles; the largest single part in the whole directory is `04_Gear_Bottom_Click.stl` at 8.1 MB / 161k triangles.
- `Fidget Fuse Tactical 7-in-1 Snap-Fit Fidget Toy/` — 59 files, by far the messiest naming; see **Naming**. 297k triangles.
- `Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy/` — 20 numbered parts (`01 - `–`20 - `) plus `11 - Middle Spring v2`. 81k triangles.

## Assemblies

Built 2026-08-22 into `Derivatives/`. Each product has `*_assembled` and `*_exploded` in three formats: `.3mf` and `.glb` keep the parts separate, named by source filename and individually coloured, so a scene reads as a parts list; `.stl` is the merged single mesh for tools that read nothing else.

**Grenade and Spinner Fuse were already exported in assembly coordinates upstream.** Loading their parts as-is *is* the assembly — no fitting needed. Verified by pairwise boolean interference: 3 overlapping pairs out of 276 for Grenade (max 7.5 mm³) and 2 of 171 for Spinner (max 5.1 mm³), all of them springs modelled uncompressed or a designed press-fit. Do not "re-assemble" these.

**Tactical had to be solved**, since its numbered series is at plate coordinates. Only the `v1.1` group ships positioned. The barrel was pinned from the three `v1.1` barrel pins (3 clean poses out of ~32,000); the shells were then seated by maximising surface contact at near-zero penetration. Every derived transform, with a per-part confidence note, is in `Derivatives/tactical/Tactical_variants_poses.json`.

### Tactical is one common body plus three swappable tops

Confirmed by the parent's `.3mf` print plates (`PLA+-+Grenade+Lever` holds exactly the 12 grenade-top parts) and by exact file arithmetic — 21+12+8+2+12+4 = 59, no overlap, nothing left over:

| group | files | contents |
|---|---|---|
| common body | 21 | `01`–`08`, **original** `09`–`14`, `20`, `27`–`30`, `32`, `33` |
| Grenade 6-in-1 top | 12 | `15`–`19`, `21`–`26`, `31` |
| Spinner 7-in-1 top | 8 | `Spinner Lever 01–08` |
| Bottle 5-in-1 top | 2 | `Bottle Cap Lever`, `Bottle Cap Lock` |
| `v1.1` revisions | 12 | 6 common barrel internals + the Spinner top + `Ring Large` |
| cosmetic | 4 | 2 mid shells, 2 lever editions |

Each variant ships a **complete** kit — all three have their own Rod Middle, Rod Left, Spring and Rod Lock (the three `Rod Lock 01` files are congruent at 706.7 mm³ but *not* byte-identical). They are alternatives; never put two kits in one assembly. Note `15`–`19` and `21`–`26` are **grenade-specific, not common**, despite falling inside the `01`–`30` numbering.

**`09`–`14` exist in two generations, and the row above counts the originals.** `09 - Internal Barrel (1)` / `10 - (2)` / `11 - (3)` and `12`/`13`/`14 - Internal Barrel Spring (3)/(2)/(1)` are the original parts; `09 - Internal Barrel Pin v1.1` … `14 - Internal Barrel Spring v1.1` are the revision, counted in the `v1.1` row. They are genuinely different parts — 135.4 vs 119.6 mm³ and 244.5 vs 211.7 mm³. **The pose record uses the `v1.1` six**, so every exported body is generation-mixed and the six originals are placed nowhere. The tops are split the same way: `Spinner Lever 01–08` and the whole grenade top are original-generation (9.0 mm rods), `1`–`5` + `Ring Large` are `v1.1` (7.0 mm). This is unresolved — see `TACTICAL_ASSEMBLY_HANDOFF.md` §5.7, and it blocks the `21 - Rod Middle` azimuth (§5.3).

`Mid Shell Solid Color` and `Hex Mid Shell Solid Color` replace **`32` *and* `33` together** with one piece — 12,640 mm³ ≈ 6,062 + 6,400, seating at the same `dy = 20.00`. Dropped in place of `33` alone they interfere by 5,643 mm³. The two-piece mid shell is the two-colour option.

The three complete body variants are in `Derivatives/tactical/Body/` (two-piece, solid, and hex mid shell). Their final lower stack is `04 → inverted 05 → inverted 06`; `01` enters from below and threads into `08`, carrying `02` and `03` on the same axis. The outer `04`–`06` module is raised 1.50 mm for clearance. `Tactical_variants_poses.json` is authoritative: regenerate with `tools/build_tactical_body.py` and `tools/build_tactical_variants.py`, rather than manually moving parts. Current body envelopes are 41.60 × 80.07 × 41.60 mm (two-piece), 41.95 × 80.07 × 41.95 mm (solid), and 41.85 × 80.07 × 42.12 mm (hex); final pairwise overlaps are at most 13.0 mm³.

### Not solved: the Grenade-6-in-1 top

10 of its 12 parts (`24`, `25`, `22`, `26`, `15`–`19`, `31`) have **no determined pose**; `21 - Rod Middle` and `23 - Rod Lock 01` are placed. Top parts mate with each other, not with the body, so body-contact carries no signal — measured: the *known-correct* Spinner head scores 0.07–0.11 surface contact against the body, and 6 mm off-true still scores 0.065–0.097. Forcing a fit put Rod Left and Rod Right at the same radius 36° apart, wrong for a handed pair. They ship laid out as a labelled kit column in `Tactical_Grenade_6in1_exploded_with_unsolved_kit.*`, regenerated by `build_tactical_variants.py` from the record's `unsolved_grenade_top` list. Finishing them needs a sub-assembly solver — parts against each other, where the fits are actually tight — and then placing that unit on the body.

`23 - Rod Lock 01` was solved that way rather than by contact scoring, and the technique generalises: **the 15.6 mm rod lock is a slotted retaining washer whose slot is tapered at −0.55 mm/mm, and it wedges onto a matching tapered tab (5.102 → 3.816 mm, −0.536 mm/mm) carried by `Bottle Cap Lever`, `3 - Rod Middle v1.1` and `21 - Rod Middle`.** Matching the two tapers fixes the height analytically — no search — and the surrounding parts then pin the slide to a window under 1 mm. The slot-mouth direction stays a free 180° choice. `22`/`26 - Rod Lock` are *not* discs (solid 2 mm plates, no slot), so this does not apply to them. The two lever editions are identical in envelope and volume to `31 - Lever` (2413.8 vs 2413.9 mm³), so they inherit whatever pose `31` eventually gets.

## Provenance

The three product folders are a **byte-identical copy** of three folders in `D:\3D Printing\Fidget Fuse\`, renamed only by turning `+` into spaces (hash-verified across all 110 files, 2026-08-21). This repo was in turn copied out of `D:\3D Printing\Fidget Fuse\Originals\`, which still exists there:

`Fidget-Fuse+Grenade+…`, `Fidget-Fuse+Tactical+…`, `Spinner-Fuse+Grenade+…`

That upstream folder also holds material that is **not** mirrored here: the source `.zip` downloads, three `.webp` assembly-instruction images, and four `.3mf` slicer projects (`Master+PLA+V3+Easier+Assembly+0.2+mm+Layer`, `PLA+-+Grenade+Lever+-+0.2+mm`, `PLA+v1.1+-+Master+Print+-+Ring+Diameter+20+mm+-+0.2+mm`, `Spinner-Fuse+Grenade+…`). Read them if a question needs them; do not copy them in, and do not modify them — see **Scope**.

Modified parts go in `Derivatives/`, never into a product folder.

## Modifying parts

**Use `tools/fidget.py`. Do not hand-roll mesh loading, and do not convert to STEP.**

```python
import sys; sys.path.insert(0, "tools")
import fidget

part = fidget.load("10_Body_OuterShell v2")          # -> trimesh.Trimesh
part = fidget.cut(part, fidget.cylinder(d=4, h=30, at=(12, 0, 0)))
fidget.save(part, "OuterShell_vented.stl", subdir="grenade")
```

Two lanes, and **the mesh lane is the default**:

- **Mesh lane** — `load` / `cut` / `union` / `intersect`, backed by trimesh + manifold3d. Fast and robust at any size in this set: the 161k-triangle `04_Gear_Bottom_Click` cuts in **0.26 s**.
- **CAD lane** — `fidget.solid()` returns a cadquery `Workplane` over the same OCP kernel. Only for analytic operations (fillets, offsets). Booleans there get impractical well before the heavy gears.
- **OpenSCAD** — reads STL, **not STEP** (verified: `ERROR: Unsupported file format`). Use `fidget.openscad(part)` to emit the correct `import(...)` line, and run with `--backend=Manifold`.

Rules that bite if ignored:

- **Coordinates differ by product — check before assuming.** Grenade, Spinner Fuse and the Tactical `v1.1` group are in **assembly coordinates** (Y up, axis at X=Z=0). The Tactical numbered `.stl.stl` series is at **plate coordinates** — `24 - Rod Left` is out at x≈403, and the `Spinner Lever 01–08` and `Bottle Cap` files likewise (x≈380–760). Either way build CSG tools relative to `part.bounds`, never to `(0,0,0)`. `load(..., center=True)` moves a part to the origin if you'd rather work there; the default preserves position, so a plate part exports back onto the same plate and an assembly part back into the assembly.
- **Check `body_count` after every cut**, not just `is_watertight`. A cut that severs the part leaves a watertight *two-body* mesh that slices as two objects.
- **A bare number is ambiguous** — `load("11")` raises and lists all six candidates. Pass a longer query or `product=("grenade"|"tactical"|"spinner")`.
- **Change a part, change its twins.** 21 of the 110 files are copies of another part, rotated or reflected. Call `fidget.twins(part)` before editing — it returns `(file, "rotation"|"reflection", deviation_mm)`. A reflected twin needs the mirrored edit, not the same one.
- **Don't trust `"reflection"` on its own — check whether the part is achiral first.** The label is whichever of the 48 frames the search happened to land on, so a symmetric part can be reported either way, and the index is self-inconsistent where that happens: all three `Rod Lock 01` files are pairwise congruent, yet `23`↔`Bottle Cap Lock` is labelled *reflection* while both of its other edges say *rotation*. All seven Tactical rod locks are in fact **achiral** (mirror maps back onto the original under a proper rotation, 0.0000 mm), so a mirrored edit there would be wrong. Test it: align the mirrored mesh to the original allowing only proper rotations; ~0 deviation means achiral.

Verify with `python tools/fidget.py check` (loads all 110, asserts watertight) and re-run `build_index.py` after anything changes in the product folders.

## Naming

Upstream names are kept exactly as downloaded — nothing has been cleaned up, and cleaning up is a decision to raise, not to make silently.

- **`.stl.stl`** — 45 of the 59 Tactical files carry a doubled extension from upstream. Don't strip it in passing; three quarters of that folder would stop matching.
- **Two overlapping number series in Tactical.** A zero-padded set (`01 - Bottom Lock Shell.stl.stl` … `33 - `) and an unpadded `v1.1` set (`1 - Rod Right v1.1.stl` … `5 - Gear v1.1.stl`). They are *different parts* and both series contain 09/10/11 and 12/13/14 — a bare number is ambiguous, so always match on the full filename. The series duplicate each other because each Tactical variant ships a complete kit; see **Assemblies**.
- **`v1.1` / `v2` are revisions kept beside their originals**, not replacements. Six `v2` files in Grenade, one in Spinner Fuse, ten `v1.1` in Tactical. In Grenade, `02_Spinner_FreeSpin` and `08_Spring_Middle_Click` are the *same byte size* as their `v2` but are not the same file — never dedupe on size here.
- **Some duplicates are intentional print-multiples.** Tactical `09/10/11 - Internal Barrel*v1.1` are three copies of one mesh, and `12/13/14 - Internal Barrel Spring v1.1` likewise — the only *byte-identical* files here. Their original-generation counterparts `09/10/11 - Internal Barrel (1)/(2)/(3)` and `12/13/14 - Internal Barrel Spring (3)/(2)/(1)` are print-multiples too, but sit at different plate positions, so they are congruent without being byte-identical.
- **Same name, same mesh, different bytes.** Spinner Fuse `18/19/20 - Handle Stapler Lock.stl` are one part copied three times — congruent at 0.0000 mm, but rotated on the plate, so the files differ byte-for-byte. Byte hashing does not find copies here; see **Mesh health**.
- `Lever Fidget Fuse Edition.step.stl` and `Lever Stripes Edition.step.stl` are STL, not STEP — the `.step` is part of the upstream name.

## Mesh health

Checked 2026-08-21 with `tools/build_index.py`; results cached in `tools/parts_index.json`.

- **110/110 watertight** — but only after one repair, which `fidget.load()` applies automatically. `24 - Rod Left.stl.stl` ships with a coincident opposite-normal face pair (a zero-volume flap at z=0) giving one 4-way edge. Dropping **both** faces fixes it; dropping one leaves a 3-way edge, still broken.
- **Three multi-body files**, which is upstream intent, not damage: `Lever Fidget Fuse Edition` (11 bodies), `Lever Stripes Edition` (4), `Ring Large` (2).
- **89 distinct shapes in 110 files** — 14 congruence classes covering 21 redundant copies. **Byte hashing finds only 4 of those 21**, because copies are rotated and reflected around the build plate, so the same shape lands as different bytes. Congruence is tested by aligning principal axes over all 48 signed axis frames and measuring worst surface deviation; tolerance is 0.01 mm, and copies differing only in tessellation land around 0.003 mm. Per-part detail is in `congruent_with` in `parts_index.json`, or `fidget.twins(part)`.
- Classes worth knowing: `05_Slider_Mechanism_Left`/`_Right` are a genuine handed pair (reflection). `13/14/15_Spring_Side` are **one part in three copies**, but **`16_Spring_Side_4` is a different part** — 45.97 mm³ against 41.59, deviating 0.409 mm. Do not treat the four side springs as a set. `23 - Rod Lock 01` ≡ `Bottle Cap Lock` ≡ `Spinner Lever 08 - Rod Lock`, and the whole `Spinner Lever 01–08` group duplicates numbered Tactical parts — those are alternative variant kits, not redundancy; see **Assemblies**.

## Git

Tracked on `main`, remote `origin` = `github.com/shivamchudasama/GrenadeFidgetToy_3DPrinting`.
Git LFS was wired up **before** the first commit, so no binary ever landed in
history as a plain blob.

`.gitattributes` routes `*.stl`, `*.3mf`, `*.glb`, `*.zip` and `*.pdf` to LFS.
`*.png` and `*.webp` are deliberately **not** routed — small doc images are
cheaper as ordinary blobs than as LFS storage/bandwidth, which is the scarce
resource (free tier: 1 GB storage, 1 GB/month).

### What is tracked, and what is not

**Tracked (~55 MB LFS):** the three pristine product folders — all 110 STL plus
the Grenade zip — the three `.md` docs, `tools/`, and
`Derivatives/tactical/Tactical_variants_poses.json`.

**Not tracked:** every `.stl`/`.glb`/`.3mf` under `Derivatives/` (~223 MB), and
`tools/__pycache__/`. That output is regenerable, and committing it would have
put the repo at ~28% of the free LFS storage tier with a full clone costing
276 MB against the 1 GB monthly bandwidth. Regenerate it with:

```
python tools/build_tactical_body.py
python tools/build_tactical_variants.py
```

**The one deliberate exception is `Tactical_variants_poses.json`, which is
un-ignored by a negation rule and must stay that way.** It is an *input* to
those scripts, not an output — `assembly.py` reads it — and it holds the solved
Tactical poses, which cannot be regenerated from anything in the repo. Losing it
would lose the assembly-solving work. Do not fold it into the `Derivatives/`
ignore.

If a future change adds a new binary type, add it to `.gitattributes` **before**
committing the first such file.
