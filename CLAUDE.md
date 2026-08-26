# CLAUDE.md

## Routine

After a **significant change** — one that makes something in this file wrong or incomplete (files added/renamed/reorganized, a new convention adopted, git/LFS setup changed) — say which section is affected and ask:

> Would you like to modify `CLAUDE.md` accordingly?

Do not ask on turns that change nothing here (questions, inspection, small edits that fit existing conventions). Keep this file lean — only what's needed to understand the repo.

## Scope — stay inside the repo root

**This repo, `D:\GIT_Repo\GrenadeFidgetToy_3DPrinting\`, is the whole working area. Never create, modify, move, rename or delete anything outside it without asking first.** Everything needed is in here: the three product folders, `Hybrid_Grenade_v1.1/`, `tools/`, and `Derivatives/`.

- The upstream source `D:\3D Printing\Fidget Fuse\` holds the `.zip` downloads, the `+`-named unpacked folders these were copied from, `.webp` assembly images, `.3mf` slicer projects, and the `Originals\` folder this repo was copied out of. **Reading it is fine. Writing, moving or deleting is not** — ask, and say exactly which file and why.
- This extends to anywhere else on the machine: no writes to sibling project folders, no edits to global config, no new directories next to the repo.
- If a task seems to need a file outside the repo, stop and ask rather than reaching for it. A plausible reason is not permission.
- Temporary scratch files are the one exception — put them in the session scratchpad, never next to the parts.

`fidget.save()` enforces the outer half of this in code: it refuses any path resolving outside the repo root, and refuses the three pristine product folders. It derives that root as the parent of `tools/`, so it followed the move into git automatically — but its own docstrings still say `Originals/`. That guard is a backstop, not the rule — the rule applies to every tool, including plain shell commands.

## Companion documents

- **`DESIGN.md`** — how the upstream toys work mechanically: the four recurring interfaces (tapered lock tab, click detent, thread, upper-shell rotation), the body stack with heights, wall thicknesses, fits and clearances, and a "before you commit a change" checklist. Read it before modifying any part's geometry. Every number is tagged measured / derived / guessed. It also records the solved/unsolved assembly status (§8) and open work in dependency order (§9).
- **`CUSTOM_DESIGN.md`** — our production custom build: the Tactical base with its native 33-click rotary waist detent, 8 standardized interchangeable mid shell variants, the solid-yoke 3-piece rod mechanism, and the folding handle carrying a 20-click rim gear and 360° spinner ring. Same evidence tags. Its §4.6 is worth reading before trusting any geometry check: a cut tool whose face lands coplanar with a part's own face leaves a **zero-thickness skin** that passes watertightness, body-count and interference and still closes a hole in the slicer.

## Repository nature

A **3D printing asset directory** holding pristine downloaded parts for three fidget-toy products, our custom hybrid production package, and associated tools. The pristine upstream folders are read-only; authored content lives in `Hybrid_Grenade_v1.1/`, `tools/`, and `Derivatives/`. No dependency manifest and no test runner — **do not fabricate build/lint/test commands**. There is a comprehensive toolkit for analyzing, modifying, and exporting parts; see **Modifying parts**.

All 110 upstream files are **binary STL** and every one carries the same `MW 1.0 <n> US` header, so the whole set came off one exporter. Sizes check out as `84 + 50 × triangles` with no mismatches (verified 2026-08-21).

**These are meshes, not CAD, and cannot be made parametric.** STL stores triangles only — no sketches, no extrudes, no feature tree, no analytic surfaces. Converting to STEP does **not** recover any of that: it wraps each triangle as a planar B-rep face, so `04_Gear_Bottom_Click` becomes a "solid" with 161,232 flat faces. Measured on 2026-08-21 at ~3.9 KB per triangle, an exact tessellated STEP of all 110 parts is **~3.7 GB**, and OCC booleans at that face count are impractical. Do not offer STL→STEP as a route to parametric editing. If a part genuinely needs to be parametric, it has to be **remodelled by hand** from measurements.

## Layout

Everything lives at the repo root: three pristine product folders, our hybrid production package, the toolkit, and derivative exports:

- `Hybrid_Grenade_v1.1/` — Complete, production-ready 3D printing package for the Native Tactical/Spinner Hybrid Grenade with 8 interchangeable mid shell options. Contains 36 numbered STLs across 5 subassemblies (`01_Base_And_Bottom_Shell/`, `02_Waist_Mechanism/` + `Mid_Shell_Options/`, `03_Internal_Barrel_And_Upper_Station/`, `04_Rod_Assembly_And_Locks/`, `05_Folding_Head_And_Spinner/`), flat-bed oriented STLs (`All_Parts_Flat_Bed_Oriented/`), assembled-coordinate STLs (`All_Parts_Assembled_Coordinates/`), slicer project plates (`Plates_3MF/`), multi-view GLBs (assembled, cutaway, exploded, shell variants), the realtime web studio (`Interactive_Shell_Variants_Viewer.html`), and `README_3D_PRINTING.md`.
- `tools/` — Python toolchain:
  - `fidget.py` — core mesh toolkit (fast Manifold-backed CSG, watertight checks, twin detection).
  - `assembly.py` — scene builder, exploded views, interference checking, and 3MF/GLB exporter.
  - `custom.py` — geometric definitions and CSG transforms for the custom hybrid toy.
  - `build_custom.py` — driver for custom build phases (`waist`, `head`, `toy`, `parts`).
  - `export_3d_print_package.py` — builds and organizes the full 36-part `Hybrid_Grenade_v1.1/` package.
  - `build_shell_variants_glbs.py` — exports all 8 mid shell assembled/cutaway/exploded GLBs.
  - `build_custom_hybrid_modified.py` / `render_hybrid_viewer.py` — assembly pipeline and standalone HTML 3D viewer generator.
  - `build_tactical_body.py` / `build_tactical_variants.py` — Tactical body and variant exports.
  - `build_professional_shell_designs.py` — cosmetic Tactical shell series.
  - `build_index.py` — regenerates `parts_index.json`.
- `Derivatives/` — output, created by `fidget.save()`. Subfolders per product (`grenade/`, `spinner/`, `tactical/`) and `Codex_Professional_Shell_Designs/` (the cosmetic shell families with `README.md`, `manifest.json` and per-design `preview.png`). See **Assemblies**.

The three product folders are **pristine upstream and read-only** — never write into them. They are flat, with no subdirectories:

- `Fidget Fuse Grenade 5-in-1 Snap-Fit Fidget Toy/` — 24 numbered parts (`01_`–`24_`, underscore-separated names) plus 6 `v2` revisions, plus `Fidget-Fuse Grenade All Parts.zip`. 552k triangles.
- `Fidget Fuse Tactical 7-in-1 Snap-Fit Fidget Toy/` — 59 files, 297k triangles.
- `Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy/` — 20 numbered parts (`01 - `–`20 - `) plus `11 - Middle Spring v2`. 81k triangles.

## Assemblies

Built into `Derivatives/` and `Hybrid_Grenade_v1.1/`. Each assembly provides separate, individually coloured parts in `.3mf` and `.glb`, and merged `.stl`.

**Grenade and Spinner Fuse were already exported in assembly coordinates upstream.** Loading their parts as-is *is* the assembly — no fitting needed. Verified by pairwise boolean interference: 3 overlapping pairs out of 276 for Grenade (max 7.5 mm³) and 2 of 171 for Spinner (max 5.1 mm³), all of them springs modelled uncompressed or a designed press-fit. Do not "re-assemble" these.

**Tactical had to be solved**, since its numbered series is at plate coordinates. Only the `v1.1` group ships positioned. The barrel was pinned from the three `v1.1` barrel pins; the shells were then seated by maximising surface contact at near-zero penetration. Every derived transform, with a per-part confidence note, is in `Derivatives/tactical/Tactical_variants_poses.json`.

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

`Mid Shell Solid Color` and `Hex Mid Shell Solid Color` replace **`32` *and* `33` together** with one piece — 12,640 mm³ ≈ 6,062 + 6,400, seating at the same `dy = 20.00`. Dropped in place of `33` alone they interfere by 5,643 mm³. The two-piece mid shell is the two-colour option.

The three complete body variants are in `Derivatives/tactical/Body/` (two-piece, solid, and hex mid shell). Their final lower stack is `04 → inverted 05 → inverted 06`; `01` enters from below and threads into `08`, carrying `02` and `03` on the same axis. Current body envelopes are 41.60 × 80.07 × 41.60 mm (two-piece), 41.95 × 80.07 × 41.95 mm (solid), and 41.85 × 80.07 × 42.12 mm (hex).

### The custom hybrid build (`Hybrid_Grenade_v1.1`)

The production-ready design is documented in `CUSTOM_DESIGN.md` and packaged in `Hybrid_Grenade_v1.1/` (BOM and assembly guide in `README_3D_PRINTING.md`).

Key mechanical features:
- **33-Click Waist Detent**: The Tactical base features a native 33-click rotary detent: `08 - Internal Barrel` carries 3 windows at 30°/150°/270°; `20 - Mid Shell Spring` / `09_Custom_Mid_Shell_Spring_33` extends 3 arms through them to r 17.40; `32 - Mid Shell P02` carries a 33-lobe inner ratchet (10.909° pitch).
- **8 Interchangeable Mid Shell Options**: 100% verified identical **34.80 mm total height** and **40.00 mm mating interface diameters** across Baseline (2-piece), 01 AeroFlow, 02 Vector Chevron, 03 Orbit, 04 Ergo Scoops, 05 Contour Twist (2-piece dual color), 06 Hex Tactical, and 07 Classic Solid Tactical.
- **Tactical Internal Spine & Upper Station**: Uses `08 - Internal Barrel` with 3 pins (`09/10/11`) and 3 leaf springs (`12/13/14`), capped by `07 - Cap`, and the rotating top assembly (`27`, `28`, `29`, `30`).
- **Solid-Yoke 3-Piece Rod**: Full-depth rod assembly with seamless integral yoke on `Custom_Rod_Middle` with side clamps `Custom_Rod_Right` and `Custom_Rod_Left`, locked by transverse `06` and `07` cross-keys and retained axially by `Spinner Lever 08 - Rod Lock` (no upper wedge lock).
- **Folding Head & Spinner**: 4-position detent fold (0°, 30°, 60°, 90° on `15 - Handle Rotating Lock` and `09 - Rod Spring`), 360° free-spinning center ring (`Custom_Ring_Spinner` at ⌀22.10 mm), 20-click outer rim gear (`Spinner Lever 05 - Gear` against `04 - Spring` in a 274° pod), and refined turned 45°-chamfered cheeks with flush exterior surfaces.

Rebuild / export:
```bash
python tools/export_3d_print_package.py
python tools/build_shell_variants_glbs.py
```

## Provenance

The three product folders are a **byte-identical copy** of three folders in `D:\3D Printing\Fidget Fuse\`, renamed only by turning `+` into spaces (hash-verified across all 110 files, 2026-08-21). This repo was in turn copied out of `D:\3D Printing\Fidget Fuse\Originals\`, which still exists there:

`Fidget-Fuse+Grenade+…`, `Fidget-Fuse+Tactical+…`, `Spinner-Fuse+Grenade+…`

That upstream folder also holds material that is **not** mirrored here: the source `.zip` downloads, three `.webp` assembly-instruction images, and four `.3mf` slicer projects. Read them if a question needs them; do not copy them in, and do not modify them — see **Scope**.

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

- **Coordinates differ by product — check before assuming.** Grenade, Spinner Fuse and the Tactical `v1.1` group are in **assembly coordinates** (Y up, axis at X=Z=0). The Tactical numbered `.stl.stl` series is at **plate coordinates** — `24 - Rod Left` is out at x≈403, and the `Spinner Lever 01–08` and `Bottle Cap` files likewise (x≈380–760). Either way build CSG tools relative to `part.bounds`, never to `(0,0,0)`. `load(..., center=True)` moves a part to the origin if you'd rather work there; the default preserves position.
- **Check `body_count` after every cut**, not just `is_watertight`. A cut that severs the part leaves a watertight *two-body* mesh that slices as two objects.
- **A bare number is ambiguous** — `load("11")` raises and lists all six candidates. Pass a longer query or `product=("grenade"|"tactical"|"spinner")`.
- **Change a part, change its twins.** 21 of the 110 files are copies of another part, rotated or reflected. Call `fidget.twins(part)` before editing — it returns `(file, "rotation"|"reflection", deviation_mm)`. A reflected twin needs the mirrored edit, not the same one.
- **Don't trust `"reflection"` on its own — check whether the part is achiral first.** All seven Tactical rod locks are in fact **achiral** (mirror maps back onto the original under a proper rotation, 0.0000 mm). Test it: align the mirrored mesh to the original allowing only proper rotations; ~0 deviation means achiral.

Verify with `python tools/fidget.py check` (loads all 110, asserts watertight) and re-run `build_index.py` after anything changes in the product folders.

## Naming

Upstream names are kept exactly as downloaded — nothing has been cleaned up, and cleaning up is a decision to raise, not to make silently.

- **`.stl.stl`** — 45 of the 59 Tactical files carry a doubled extension from upstream. Don't strip it in passing; three quarters of that folder would stop matching.
- **Two overlapping number series in Tactical.** A zero-padded set (`01 - Bottom Lock Shell.stl.stl` … `33 - `) and an unpadded `v1.1` set (`1 - Rod Right v1.1.stl` … `5 - Gear v1.1.stl`). Match on the full filename.
- **`v1.1` / `v2` are revisions kept beside their originals**, not replacements. Six `v2` files in Grenade, one in Spinner Fuse, ten `v1.1` in Tactical.
- **Some duplicates are intentional print-multiples.** Tactical `09/10/11 - Internal Barrel*v1.1` are three copies of one mesh, and `12/13/14 - Internal Barrel Spring v1.1` likewise.
- `Lever Fidget Fuse Edition.step.stl` and `Lever Stripes Edition.step.stl` are STL, not STEP — the `.step` is part of the upstream name.

## Mesh health

Checked 2026-08-21 with `tools/build_index.py`; results cached in `tools/parts_index.json`.

- **110/110 watertight** — after one repair, which `fidget.load()` applies automatically. `24 - Rod Left.stl.stl` ships with a coincident opposite-normal face pair at z=0. Dropping **both** faces fixes it.
- **Three multi-body files**, which is upstream intent, not damage: `Lever Fidget Fuse Edition` (11 bodies), `Lever Stripes Edition` (4), `Ring Large` (2).
- **89 distinct shapes in 110 files** — 14 congruence classes covering 21 redundant copies.

## Git

Tracked on `main`, remote `origin` = `github.com/shivamchudasama/GrenadeFidgetToy_3DPrinting`.
Git LFS was wired up **before** the first commit, so no binary ever landed in history as a plain blob.

`.gitattributes` routes `*.stl`, `*.3mf`, `*.glb`, `*.zip` and `*.pdf` to LFS.
`*.png` and `*.webp` are deliberately **not** routed — small doc images are cheaper as ordinary blobs than as LFS storage/bandwidth.

### What is tracked, and what is not

**Tracked (~55 MB LFS + production package):**
- The three pristine product folders (110 STLs + Grenade zip).
- `Hybrid_Grenade_v1.1/` — complete 36-part package, 8 mid shell variants, 3MF project plates, GLB models, `Interactive_Shell_Variants_Viewer.html`, and `README_3D_PRINTING.md`.
- Documentation (`CLAUDE.md`, `CUSTOM_DESIGN.md`, `DESIGN.md`).
- `tools/` toolchain.
- `Derivatives/tactical/Tactical_variants_poses.json` (essential solved pose record).
- Small text and image sidecars under `Derivatives/Codex_Professional_Shell_Designs/` (`README.md`, `manifest.json`, `preview.png`).

**Not tracked:**
- Regenerable `.stl`/`.glb`/`.3mf` under `Derivatives/` (kept out of LFS to conserve bandwidth).
- `tools/__pycache__/`.

Regenerate derivative exports with:
```bash
python tools/build_tactical_body.py
python tools/build_tactical_variants.py
python tools/build_custom.py
python tools/build_professional_shell_designs.py
```

**The one deliberate exception is `Tactical_variants_poses.json`, which is un-ignored by a negation rule and must stay that way.** It is an *input* to those scripts, holding the solved Tactical poses.

If a future change adds a new binary type, add it to `.gitattributes` **before** committing the first such file.

