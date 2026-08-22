# CUSTOM_DESIGN.md — the custom build

`DESIGN.md` describes the **upstream** mechanisms; this file describes **ours**.
Same evidence tags: **[M]** measured, **[D]** derived, **[?]** informed guess.

Rebuild with `python tools/build_custom.py`. Last verified 2026-08-22.

---

## 1. What was asked for

1. **Keep the Tactical base** — and put the rotary click **into** it, modifying
   the base and the rod as needed. Not a second toy stacked on top.
2. **The click of `04 - Middle Spinner Shell`**, with the middle springs.
3. **`Spinner Lever 05 - Gear` on the outer rim of the handle**, rolled from
   outside, with `17 - Ring Spinner` still spinning inside it.

> An earlier pass got 1 and 3 wrong: it lifted the whole Spinner Fuse upper
> module 73 mm and sat it on the body (a 165.6 mm tall toy), and it sank the
> gear into a slot between the handle halves behind lugs that stood 4.9 mm
> proud of the teeth. Both are replaced by what follows. The stacked output is
> deleted; do not go looking for `Custom_Toy_*`.

---

## 2. The base already has this mechanism

**[M]** This is the finding the whole build now rests on, and nothing in
`DESIGN.md` or `CLAUDE.md` records it:

| part | feature |
|---|---|
| `08 - Internal Barrel` | outer is a **clean cylinder, r 16.21 .. 16.22**, with **three windows at 30° / 150° / 270°**, each 22° wide, open y 20.43 .. ~34.7 |
| `32 - Mid Shell P02` | bore is a **33-lobe ratchet, r 16.43 .. 17.53** — 1.10 mm deep |
| `20 - Mid Shell Spring` | **three arms at 30 / 150 / 270** poking out through those windows to **r 17.20** |

**[M]** Sweeping the mid shell against the spring gives a clean
**6.43 → 0.00 → 6.43 mm³ cycle every 10.909°**, i.e. 360/33.

**[D]** So the Tactical waist is *already* the Spinner Fuse's machine — one lobe
different and 0.13 mm shallower. `20 - Mid Shell Spring` is dual-purpose: its
15.84 mm square bore is the linear click on the rod (`DESIGN.md` §2.2), and its
three arms are a rotary detent nobody had noticed.

**[M]** And `04 - Middle Spinner Shell`'s bore is **r 16.49** against the
barrel's **r 16.22** — a **0.27 mm journal**, versus the Spinner Fuse's own 0.25.
It drops straight onto the Tactical spine with no adapter, and its OD of r 21.00
sits flush against the mid shell's 20.82.

### 2.1 The base is 3-fold, and that governs everything

**[M]** Three windows, a 3-lobed barrel bore, three spring arms, 33 mid-shell
lobes, and `DESIGN.md` §2.4's three barrel pins at 120°.

**[D]** A detent only clicks if **every nose seats at once**, which needs the
nose spacings to be whole notch counts. That single rule explains both products:

| | notches | noses | works because |
|---|---|---|---|
| Tactical mid shell | 33 | 3 at 120° | 33/3 = 11 |
| Spinner Fuse `04` | 32 | 2 at 180° | 32/2 = 16 |

**[M]** Put `04`'s 32 notches against the base's three 120° arms and the sweep
goes **flat — 4.87 .. 5.22 mm³ at every angle**. That is constant drag, not a
click: 32/3 is not an integer, so the three noses sit permanently at thirds of a
notch.

**[D]** Two dead ends, both measured, so nobody repeats them:

- **A 2-fold spring does not fit this base.** Rotating a leaf 180° to make an
  opposed pair drives it **93.5 mm³ into the barrel** — the barrel bore is
  3-lobed and the spring's rings are shaped to match it.
- **Cutting a fourth barrel window at 210°** works geometrically (160.3 mm³
  removed, openings then at 20-40 / 140-160 / **200-220** / 260-280) but only
  serves that same 2-fold spring, so it is not used.

**[D]** The way out is that three noses *can* seat on 32 notches if they are
spaced **11 + 10 + 11** notches instead of evenly. That puts them at
**30.00° / 153.75° / 266.25°** — and all three land inside windows the barrel
already has *and* on arms the spring already has. So `04` and `08 - Internal
Barrel` are both used **exactly as they ship**.

---

## 3. The clicking waist

Two variants, same station, same 41.6 × 80.1 × 41.6 mm envelope as the stock
body. Nothing is stacked and the toy does not get taller.

| variant | band | noses | clicks/turn | detent |
|---|---|---|---|---|
| **Ring** | `04 - Middle Spinner Shell`, unmodified | 30.00 / 153.75 / 266.25 | **32** | **3.11 .. 12.52 mm³** |
| **Native** | the base's own mid shell | 30 / 150 / 270 | **33** | **1.33 .. 10.18 mm³** |
| *stock, for comparison* | mid shell | 30 / 150 / 270 | 33 | 0.00 .. 6.43 mm³ |

**Ring** swaps `04` in as a visible twist band at the waist and trims the mid
shell to sit above it. **Native** leaves the body looking exactly as it ships and
just deepens the detent it already has.

### 3.1 The only part that changes is the spring

**[D]** `20 - Mid Shell Spring` gets two minimal edits:

1. **Narrower noses.** The upstream arm tip is ~11° wide — a whole notch pitch —
   so it can never drop *into* a notch. Left as-is the swept overlap bottoms out
   at **9.2 mm³** instead of releasing. Every tip is pulled back inside the crest
   circle (r 16.30) and a **5° nose** put back on each arm.
2. **Deeper reach**, 17.20 → **17.40** — the reach measured on `11 - Middle
   Spring` and `12 - Optional Middle Spring`. Against a 16.50 crest that takes
   engagement from 0.70 mm to **0.90 mm**.

**[M]** Heights are tightly boxed and both bounds were measured:

- the spring can rise at most **0.25 mm** before it fouls the barrel
  (0.00 mm³ at dy 0.25, 6.56 at 0.50, 78.54 at 1.00);
- `04` must rise at least **3.50 mm** to clear `06 - Bottom Shell 03`
  (391 mm³ at dy 2.50, 93.6 at 3.25, 0.15 at 3.50).

**[D]** At spring dy **0.25** and ring dy **3.50** the spring sits at
y 30.00 .. 34.00 and `04`'s ratchet band at y 30.00 .. 40.50 — exact coverage.

**[D]** **The rod does not need changing.** Its 3.000 mm serrations already run
from y ≈ 29.5 upward, and the spring's square bore is untouched, so the linear
click still works at the new height.

---

## 4. The gear on the outer rim

**[M]** `Spinner Lever 05 - Gear`: **20 teeth, tip ⌀36.00, root ⌀33.62, bore
⌀25.514** (with a ~110° relief to ⌀28.21), **8.60 thick**. Axis taken from tooth
concentricity — order-1 amplitude 0.000 at the bbox centre.

**[M]** The detent is `Spinner Lever 04 - Spring`'s job upstream: it seats in
`3 - Rod Middle v1.1` over y 63.48 .. 79.19 and meets the gear at **r 17.58**,
riding the tooth tips with 0.42 mm engagement — 20 clicks a turn.

### 4.1 What the head needed

**[D]** The gear will not go on as-is: bore ⌀25.514 against a housing bore of
⌀24.96 leaves a 0.28 mm wall. Turning `17 - Ring Spinner`'s mid-plane bulge down
to the **⌀22.10** it already carries at z = ±3 lets the housing bore go to ⌀22.60
and the journal to ⌀25.05 — a **1.30 mm wall**. Retention is untouched: the ±9.2
lips grip at r 9.71 against the ring's ⌀21.24 ends. **[M]** As built the ring
runs on 0.193 mm clearance.

**[M]** Four captive locks sat inside the gear's tooth annulus and had to move
out to r 20.500: `18`/`19`/`20 - Handle Stapler Lock` (from r 14.650 at 45/105/
345°) and `16 - Handle Lock` (from r 15.362 at 222.85°).

### 4.2 Making it a rim wheel

**[D]** The lugs carrying those pins originally ran through the gear's own band
at r 22.9 — **4.9 mm proud of a tooth tip at 18.00** — which shrouded the wheel
and is exactly what made it unrollable. They now exist **only outside
|z| ≤ 4.60**, and the pins bridge the gap bare, seated in a blind pocket in each
half like a hinge pin.

**[M]** Result: the gear's teeth stand proud of the handle over **264° of 360°
(73%)**. The remaining 96° is three 4°-wide bare pins and the handle arm itself
at 188.5–270°, which has to be there.

**[M]** The detent still measures **0.00 .. 2.58 mm³ over an exact 18° pitch,
9 of 19 degrees free — 20 clicks/turn.**

---

## 5. What was verified

- Upstream intact: `python tools/fidget.py check` → **110/110 watertight**.
- Every changed part is **watertight and single-body**; `build_parts()` refuses
  to write anything that is not.
- **The waist adds no interference.** Worst pair in either variant is
  **12.97 mm³**, `08 - Internal Barrel` / `07 - Internal Barrel Cap` —
  pre-existing and already flagged in `DESIGN.md` §5. The spring-against-band
  figure (10.33 Ring / 10.18 Native) *is* the detent, a spring modelled
  uncompressed.
- Both click mechanisms confirmed by rotation sweep, not by inspection.

---

## 6. Open

- **[?]** **The handle is not yet joined to the base.** The waist and the head
  are both finished and verified, but as separate assemblies. Upstream the
  handle hinges on the Spinner Fuse rod stack (`15 - Handle Rotating Lock`),
  which no longer exists here; the Tactical mounts its tops on a rod through the
  barrel instead. This is the next piece of work and it is not started.
- **[?]** Whether **1.30 mm** is enough wall under the gear journal in PLA at a
  0.4 mm nozzle — `DESIGN.md` §6 already calls 1.70 thin. First thing to check
  on a test print.
- **[?]** The four relocated locks now sit in blind pockets opening toward the
  gear slot rather than being pinched full-length; retention is weaker than
  upstream, and the head's far side is no longer pinned.
- **[?]** Ring variant leaves the mid shell as a short top ring above `04`;
  its support has not been checked under load.
- **[?]** Whether the deepened detent is too stiff to turn by hand. 12.52 mm³
  peak is nearly double the stock 6.43, and that is a printed flexure.

---

## 7. Files

```
python tools/build_custom.py waist    # Custom_Waist_Ring_2pc, Custom_Waist_Native_2pc
python tools/build_custom.py head     # Custom_Head
python tools/build_custom.py parts    # printable STLs of every changed part
```

Geometry in `tools/custom.py`, driver in `tools/build_custom.py`, output in
`Derivatives/custom/`. Nothing here writes into a product folder.
