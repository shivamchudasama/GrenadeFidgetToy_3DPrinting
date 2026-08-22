# CUSTOM_DESIGN.md — the custom build

`DESIGN.md` describes the **upstream** mechanisms; this file describes **ours**.
Same evidence tags: **[M]** measured, **[D]** derived, **[?]** informed guess.

Rebuild with `python tools/build_custom.py`. Last verified 2026-08-23.
**The head is frozen** -- one design, no variants.

---

## 1. What was asked for

1. **Keep the Tactical base** — and put the rotary click **into** it, modifying
   the base and the rod as needed. Not a second toy stacked on top.
2. **The click of `04 - Middle Spinner Shell`**, with the middle springs.
3. **`Spinner Lever 05 - Gear` on the outer rim of the handle**, rolled from
   outside, with `17 - Ring Spinner` still spinning inside it.

Then, in a second pass, the handle itself had to carry all three of the actions
the two donor toys have between them:

4. **Fold 90° up and down with a click**, as the Spinner Fuse handle does.
5. **A 360° spinning ring**, as both donors have — this is item 3's ring.
6. **The gear on the handle's outer diameter, clicking against a spring** —
   item 3 again, stated as a spring rather than as a wheel.

So 5 and 6 were already built (§4); 4 is §5, and it is what finally joins the
handle to the base (§6).

> An earlier pass got 1 and 3 wrong: it lifted the whole Spinner Fuse upper
> module 73 mm and sat it on the body (a 165.6 mm tall toy), and it sank the
> gear into a slot between the handle halves behind lugs that stood 4.9 mm
> proud of the teeth. Both are replaced by what follows. That build's code is
> gone from `tools/custom.py` as well as its output; the `Custom_Toy_*` files
> that exist now are §6, not it.

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

**[D]** **The rod's serrations do not change.** Its 3.000 mm teeth already run
from y ≈ 29.5 upward, and the spring's square bore is untouched, so the linear
click still works at the new height. The rod's *top* does change, but only above
y 62 — see §5.3.

---

## 4. The gear on the outer rim

**[M]** `Spinner Lever 05 - Gear`: **20 teeth, tip ⌀36.00, root ⌀33.62, bore
⌀25.514** (with a ~110° relief to ⌀28.21), **8.60 thick**. Axis taken from tooth
concentricity — order-1 amplitude 0.000 at the bbox centre.

**[M]** The detent is `Spinner Lever 04 - Spring`'s job upstream: it seats in
`3 - Rod Middle v1.1` over y 63.48 .. 79.19 and meets the gear at **r 17.58**,
riding the tooth tips with 0.42 mm engagement — 20 clicks a turn. **[M]** Swept,
the upstream pair `4 - Spring` / `5 - Gear v1.1` gives **0.00 .. 9.55 mm³ over
one 18° pitch, 4 of 19 degrees free** — that curve is the benchmark §4.3 is
measured against.

Here the wheel has moved out to the rim and the upstream spring's seat has
become the hinge yoke (§5.3), so the spring has to go somewhere else — but it is
still `Spinner Lever 04 - Spring` itself, unmodified. §4.3 says where.

### 4.1 What the head needed

**[D]** The gear will not go on as-is: bore ⌀25.514 against a housing bore of
⌀24.96 leaves a 0.28 mm wall. Turning `17 - Ring Spinner`'s mid-plane bulge down
to the **⌀22.10** it already carries at z = ±3 lets the housing bore go to ⌀22.60
and the journal to ⌀25.05 — a **1.30 mm wall**. Retention is untouched: the ±9.2
lips grip at r 9.71 against the ring's ⌀21.24 ends. **[M]** As built the ring
runs on 0.193 mm clearance — **this is requirement 5, and it is unchanged from
the Spinner Fuse: `17 - Ring Spinner` still spins 360° in the handle's head.**

**[M]** Four captive locks sat inside the gear's tooth annulus and had to move
out to r 20.500: `18`/`19`/`20 - Handle Stapler Lock` (from r 14.650 at 45/105/
345°) and `16 - Handle Lock` (from r 15.362 at 222.85°).

### 4.2 Making it a rim wheel

**[D]** The lugs carrying those pins originally ran through the gear's own band
at r 22.9 — **4.9 mm proud of a tooth tip at 18.00** — which shrouded the wheel
and is exactly what made it unrollable. They now exist **only outside
|z| ≤ 4.60**, and the pins bridge the gap bare, seated in a blind pocket in each
half like a hinge pin.

**[M]** Result: the gear's teeth stand proud of the handle over **249° of 360°
(69%)** measured in the gear's own plane, and **247° (69%)** measured across the
cheek band either side of it. The rest is the handle arm at 188.5–270° and the
pod.

> **A correction.** This figure was previously recorded as 264° (73%). That was
> measured by rays cast at **z = 0** — exactly the plane the old two-piece pawl
> was split on, and its two halves stood 0.15 mm either side of it. Every ray
> went through the slit, so 48° of shrouded rim scored as open. The check now
> samples at z = ±2 and takes the worse, which is why both numbers below are
> lower than the one that stood before. Nothing about the geometry got worse.

### 4.3 The detent spring — `Spinner Lever 04 - Spring`, in a pod on the lever

**Nothing sprung is moulded into the handle.** The gear's detent is the upstream
part itself, unmodified, 923.6 mm³, pointing at the gear axis from **274°** down
a pod on the lever. It slides into a slot and the gear caps it — upstream
retention, unchanged.

**[M] Where it can go is forced.** In the gear's own plane the handle head is a
**1.2 mm journal tube and nothing else**. Ray-cast at z = 0 from the gear axis
there is no material past r 12.5 between 270° and 180°; from 195° to 255° there
is 3.0 mm of it at 195°, 5.4 at 210° and 9.6 at 255°, and that is the lot.
`Spinner Lever 04 - Spring` is a straight serpentine that pushes along its own
length and wants **17.99 mm** of that depth. It does not fit anywhere as the
handle ships, so the lever grows a pod.

**[M] The lean is not cosmetic.** Run down the arm's own centreline (258.4° from
the gear axis) the housing reaches inboard to head x 16.8. Head x *is* toy radius
at z = 0 and the body's silhouette is r 20.81, so that buried the spring
**70.89 mm³** into `27 - Upper Shell Top` and the handle another **38.10**. At
**274°** the whole housing stays outboard of the arm's inner face with ~2 mm to
spare, and the bulge lands on the face you hold rather than the face that lies
against the body.

**[M]** Detent as built: **0.00 .. 4.20 mm³ over one 18° pitch, 6 of 19 degrees
free — 20 clicks/turn**, against the upstream pair's 0.00 .. 9.55 and 4 of 19.

### 4.4 The pod, and the head it hangs off

**The pod is lofted, and exactly as wide as the lever.** A stadium section
lofted through **72 sections of 96 points**, spaced on `sin(u)` so they crowd at
the ends where the profile turns. **[D]** Stacking extruded slabs cannot do this
— every slab has vertical walls, so 24 of them read as 24 contour lines.

**[M] Its width is a printing constraint, not a styling one.**
`13 - Handle Left`'s arm measures **z −9.50 .. +9.50**, constant over y 24 .. 48.
A pod any narrower sits in a groove between the lever's two faces, and that
groove is an **undercut**: printed outer-face-down — the orientation the spring
slot and every pin pocket need, because it is the one that leaves them opening
upward — the pod's flank has to grow out over thin air. Flush at ±9.50 it does
not: the flanks leave the bed vertically and the only departure is a 0.80 mm
round-over onto the face, the same edge break the lever already carries.

**The pod splits on the handle's own parting plane.** Left whole it was a closed
cavity inside `13 - Handle Left`, reachable only through the mouth at r 18.30:
an internal overhang with no way to place the spring. Over the pod's footprint
`13` now gives up everything above z = 0 and `14 - Handle Right` takes it — the
pod's shell *and* the arm underneath it, or `14`'s share would float — so each
half prints open-faced and the spring drops in when they close.

**[D]** The pod is trimmed on the gear slot's own r 18.30 circle where it meets
the head, which also opens the pocket's mouth: a stadium runs half a width
*past* the line it is built on, back to r 10.3, and that sealed the spring in.

**The head is two turned cheeks, and nothing else.** **[M]** Measured off
`1`/`2 - Rod Right`/`Left v1.1` around `5 - Gear v1.1`: the two wing plates
close into a disc of r 16.48 at 4 mm off the gear's face, 15.63 at 8, 14.67 at
11 and 14.00 at 13, against a tooth tip of **17.83**. The cheeks are *inside*
the tooth circle at every height, so the gear stands proud all the way round.
This head is the same proportions against a tip of 18.00 — **r 16.30 at
|z| 4.60 falling on a smoothstep to 14.20 at 9.40** — revolved, not stepped.

> **A collar was tried here and was a mistake.** Sized to hold pins in the head
> it reached r 22.90 — 4.9 mm proud of a tooth tip at 18.00 — and put the wheel
> in a 9.2 mm groove where nothing could turn it. The cost was measured, written
> down, and the thing shipped anyway; it should not have been.

**[D] The head therefore carries no pins.** A lock pin is ⌀4.31 and has to cross
z = 0 to hold the halves together, and between r 12.5 and r 18.3 the halves
never meet — that band is the gear's. So a head pin stands at r 20.5 and
anything holding it reaches 22.9. **There is no arrangement of head pins that
leaves the gear rollable.**

**[D]** The Tactical does not have any either. `1`/`2 - Rod Right`/`Left v1.1`
are not pinned to each other at the head — they are clamped along their whole
length by the rod between them and the lock at its foot, and the head is a
cantilever off that. This handle is built the same way: the halves meet at the
neck and the arm, two locks close them there, and the head hangs off it.
`18`/`19`/`20 - Handle Stapler Lock` are **not used** — they are 13.8 mm long in
a handle 19.0 mm wide, so they only ever sit in a **blind** pocket, and there is
no way to get one into the pod once the halves are closed nor to press it home
before they are. All four vacated upstream pockets are still plugged.

### 4.5 The two locks that close it

Both are `16 - Handle Lock`, the same printed part twice, in **through** holes.

**[M] It is not a dowel.** Its section is a blade: **3.00 mm across its narrow
axis against 6.00 across the other**, with the narrow one lying at **50°** in
the part's own frame. Placed by translation alone it therefore arrives tilted
and eats 5.59 mm of whatever direction is short of room. Spinning it costs
nothing — it is a printed pin — and both copies are spun to put the narrow axis
where the room is tight.

**At the neck**, spun −17.5° so the narrow axis points at the gear. **[M]** The
pin must stand ≥ 20.95 from the wheel axis or it fouls the gear and ≥ 10.70 from
the fold hinge or it eats the hub the fold detent runs on; unturned, those two
circles close completely at y 58.59 — its upstream height — where x would have
to be at once ≤ 10.63 and ≥ 10.70. Turned, it presents only **0.78 mm** toward
the gear instead of 2.80 and the whole span **x 10.56 .. 12.83** is legal at
that height. It sits at **(12.20, 58.76) — 0.17 mm from where `13`/`14` carry
it**. Out at x 12.20 it also clears the hinge yoke by 5 mm, so its bore has a
wall round it instead of opening into the neck's cavity.

**Through the pod's tail**, spun **44°**. **[M]** That angle was swept, not
guessed: the pocket is boxed in by the slot's **flat** end face inboard and the
pod's **round** cap outboard, and over all 360° the shortest tail is the
orientation that lays the flat edge against the flat end and nests the round
edge into the cap. Its opposite, 224°, costs 0.8 mm more. So placed the pin
spans **r 37.43 .. 40.43** with **1.55 mm of wall at both ends**.

**[M] `ARM_POD_TAIL` is 16.4, and that is the floor.** The pod's far point is
now exactly the pin's outer edge plus its wall — 35.88 (slot) + 1.55 + 3.00
(pin) + 1.55 = **41.98**, which is y 27.14. Nothing is left to remove without
thinning the wall or shrinking the pin. For comparison the tail was 18.5 with
the pin unturned and 23.0 when it was sized around a stapler.

### 4.6 A hole that measured open and was not

**[M]** `_pin_pockets()` used to clip each pocket to this half's side of z = 0.
That gave the cut tool a face exactly **coplanar** with the handle's own mating
face, and the boolean left a **zero-thickness skin across the bore**.

It has no volume. Interference reads **0.000 mm³**, a containment probe down the
axis reads empty at every height, and the part is watertight and single-body —
every check in this file passed it. But it is a real face: a slicer closes the
hole on it and the pin cannot be pushed through. It took two rounds of "the hole
is not thorough" before a ray cast down the axis returned **two hits at
z = 0.0000 and nothing else**.

**[D]** The pocket is now cut from both halves unclipped. That is safe because
neither half has material on the other's side of the parting plane anywhere a
pin sits — measured, the half's volume is unchanged to 0.1 mm³.

**[D] And `build_parts()` now checks it.** Every full-width pin gets a ray down
its axis, and a finished bore returns **no hits at all**; anything else fails
the build. `18`/`19`/`20 - Handle Stapler Lock` are exempt — they are 13.8 mm in
a 19.0 mm handle and blind on purpose. Volume and watertightness cannot catch
this class of fault; only the ray can.

**[D]** One more trap in the same family: two different things whose export
names collide. Both gear-spring variants once carried a `16 - Handle Lock`, they
slugged to the same filename, and one silently overwrote the other -- so the
exported pin could be the other design's placement sitting 3 mm off the hole,
which reads exactly like a hole that was never bored. Only one head ships now,
but `build_parts()` still writes into a dict keyed by name: a collision there is
silent.

---

## 5. The 90° fold

**[M]** This is the one action that was missing, and **none of its mechanism is
invented** — the Spinner Fuse already had all four pieces, and `handle_half()`
never touched any of them, because every cut it makes is around `HEAD_C` at
(28.790, 69.040), **30.5 mm away from the hinge**. The scallops arrive intact.

| piece | what it is | **[M]** |
|---|---|---|
| `13`/`14 - Handle Left`/`Right` | a **D-bore** through each cheek at (0, 58.12) | r 2.21 with a flat at 0.99, over \|z\| 5 .. 9.5; counterbored to r 2.71 over z 7 .. 9.5 |
| the same two parts | the **hub**: 12 notches at 30° | crest r 6.97, root r 7.75 — 0.78 mm deep — over 180° .. 285° of arc |
| `15 - Handle Rotating Lock` | the **pin** | D3.90 shaft flatted 1.00 mm off axis, D4.98 head over z 6.5 .. 9.5, 19.00 long, 198.1 mm³ |
| `09 - Rod Spring` | the **detent leaf** | a serpentine, 7.23 × 21.69 × 14.15, 887.8 mm³; nose stands at r 6.47 below the axis |

**[D]** The pin is **keyed to the handle and turns with it**: the handle's bore
carries a matching flat, while the yoke's bore is round — **[M]** r 2.185 ..
2.205 at every height, 0.24 mm of clearance on the shaft.

### 5.1 The scalloped arc is exactly the swing

**[D]** The leaf is fixed at 270° of the hub's frame. A handle turned 0° → 90°
presents 270° → 180° of its own hub to it, and 180° .. 285° is precisely where
the notches are. Nothing else on the hub is scalloped. **12 notches at 30° pitch
means the fold is exactly three clicks**, and the arc was cut for a 90° fold and
nothing more.

**[M]** Swept against the yoke and leaf, the detent runs
**9.44 .. 12.29 mm³ on a 30.0° pitch** — the same curve the donor gives, because
it is the same parts.

**[M]** The floor of the swing is a **hard stop, not a detent**: measured
against the assembled body, 0.00 mm³ at 0°, **30.71 at −2°, 231.40 at −4°,
652.36 at −6°**. So 0° is stowed against the body, and the handle goes up from
there.

### 5.2 The one new part is the yoke

**[D]** `05` + `06` + `07 - Rod Middle *`, unioned, are a **single watertight
body of 4806.0 mm³** that already carries the pin bore and, below it, the slot
the leaf stands in — the slot runs through all three slabs at the same x, so the
union keeps it. Two trims and it is done:

- **Thickness → ±3.580 along the pin.** That is what the stack measures at the
  hinge anyway. Below the hinge it fattens to ±6.66 and lower still to ±9.82,
  and none of that fits either between the hub bosses (which start at 4.17) or
  down the body's bore.
- **Length**, cut so the graft lands in solid rod — see §5.3.

**[M]** As built: 2303.4 mm³, single watertight body, and ~1.9 mm of solid floor
under the leaf's foot (section 94 .. 100 mm² over head y 28.0 .. 29.9, falling to
41.6 mm² above, where only the two prongs beside the slot remain).

**[D]** The leaf is **14.14 mm along the pin against the yoke's 7.16**, so its
ends stand proud and bear on the two hub bosses. That is upstream's arrangement,
not a consequence of the trim — upstream it stands 0.41 mm proud of a 13.32 mm
stack, and the bearing surfaces are the same either way.

### 5.3 Grafting it onto the rod

**[M]** `3 - Rod Middle v1.1` is **one polygon from y 58.5 to 63.0** and **forks
into two rails above 63.5** — upstream that fork is the seat for `4 - Spring`,
which this build does not use. So `YOKE_JOIN = 62.000`, in solid material, and
everything above it is replaced by the yoke.

**[D]** The head module turns **90° about Y**. That sends the pin axis to the
toy's **+x**, which is the direction the rod is *thin* in — 7.00 mm against
16.02 — so the yoke slides between the hub bosses with no change of section and
the leaf, wide along the pin, spans the direction the rod is wide. Turned the
other way the leaf would have to fit through 7.00 mm and nothing works.

**[M]** The lift is **34.000**, boxed by two measurements 3 mm apart:

| bound | why |
|---|---|
| ≥ **31.0** | below it the leaf's foot fouls the body's bore. Above the barrel cap that bore is a clean cylinder — largest that fits is **r 8.35 over y 62 .. 64** and **r 8.19** from there to the top — and the foot's corner sits at **r 8.21** |
| > **32.04** | below it the yoke's floor rises above `YOKE_JOIN`, gets cut off with the graft, and the leaf drops straight out |

At 34.000 the floor is 1.96 mm and the hub clears the body top by **4.65 mm**.

**[M]** The finished rod is **5677.2 mm³, single watertight body**, x ±3.58,
y 18.08 .. 99.62, z ±8.01.

---

## 6. The whole toy

`Custom_Toy_Ring_2pc` and `Custom_Toy_Native_2pc` — the clicking waist of §3,
the rod of §5.3, and the head of §4 folded down at 0°.

**[M]** 34 parts (Ring) / 33 (Native), envelope **41.63 × 126.26 × 72.47 mm**,
y −0.35 .. 125.91.

Bounding boxes, as `x × y × z` in each toy's own frame — the handle reaches
along **−z** here and along **+x** on the Spinner Fuse, so the two long
horizontal figures are the same measurement:

| | bbox (mm) | tall | handle reach |
|---|---|---|---|
| this toy | 41.63 × **126.26** × 72.47 | 126.3 | 72.5 |
| stock Tactical spinner 7-in-1 | 41.60 × **116.74** × 41.60 | 116.7 | — |
| stock Spinner Fuse | 66.60 × **84.55** × 41.61 | 84.6 | 66.6 |

**[D]** So it stands 9.5 mm taller than the tallest stock variant, and reaches
sideways for the same reason the Spinner Fuse does — the handle lies alongside
the body rather than on top of it. The extra 5.9 mm of reach over the donor is
the gear on the rim and the pawl's anchor, which the donor's handle did not
carry.

**[M]** Three actions, three sweeps, all on the assembled toy:

| action | measured |
|---|---|
| fold the handle 0° → 90° | detent **9.44 .. 12.29 mm³** on a 30° pitch, **3 clicks**; and **0.00 mm³** against the body at every step |
| spin the ring | 0.193 mm clearance journal, free |
| roll the gear on the rim | detent **0.00 .. 4.20 mm³** on an 18° pitch, **20 clicks/turn** |
| *plus, from the base* | waist twist **32 or 33 clicks/turn** (§3), and the linear click **0.00 .. 2.10 mm³ over 9 mm of rod travel on the 3.000 mm serration pitch**, carrying the whole head |

**[D]** The linear click is the one that could have been lost — the head hangs
off the rod, so it travels with it. It is not: the rest pose is the **bottom** of
the stroke (the rod jams going down, 15.14 mm³ at −2 mm), the head moves *away*
from the body on the way up, and the click survives the graft unchanged.

---

## 7. What was verified

- Upstream intact: `python tools/fidget.py check` → **110/110 watertight**.
- Every changed part is **watertight and single-body**; `build_parts()` refuses
  to write anything that is not.
- **The waist adds no interference.** Worst pair in either waist variant is
  **12.97 mm³**, `08 - Internal Barrel` / `07 - Internal Barrel Cap` —
  pre-existing and already flagged in `DESIGN.md` §5. The spring-against-band
  figure (10.33 Ring / 10.18 Native) *is* the detent, a spring modelled
  uncompressed.
- **The toy adds none either.** 12–13 pairs, worst still that same 12.97 mm³.
  The new entries are the two halves of the fold detent — `09 - Rod Spring`
  against `Custom Handle Left` 5.14 and `Right` 4.30 — again a spring at rest.
- All four click mechanisms confirmed by **sweep, not by inspection**, and the
  gear's is measured against the upstream pair's own curve (§4).
- **Every full-width bore is ray-checked.** `build_parts()` fails the build if
  one is not open — see §4.6 for why volume and watertightness cannot.

### 7.1 Bill of materials

Printed from `Derivatives/custom/Parts/` — 10 files: `Custom_Rod`,
`Custom_Handle_Left`, `Custom_Handle_Right`, `Custom_Ring_Spinner`,
`Custom_Mid_Shell_Spring_32` (or `_33`), `Custom_Mid_Shell_P01`/`_P02`, and
**`Custom_16_Handle_Lock` plus `Custom_16_Handle_Lock_pod`** — the same printed
part twice, one closing the neck and one closing the pod, each already spun to
its own orientation (§4.5).

Printed **unmodified from the product folders**: `15 - Handle Rotating Lock` and
`09 - Rod Spring` (Spinner Fuse), `Spinner Lever 05 - Gear` and
`Spinner Lever 04 - Spring`, `Spinner Lever 05 - Gear` and
`Spinner Lever 08 - Rod Lock` (Tactical), `04 - Middle Spinner Shell` for the
Ring waist, and the rest of the Tactical common body.

---

## 8. Open

- **[?]** Whether **1.30 mm** is enough wall under the gear journal in PLA at a
  0.4 mm nozzle — `DESIGN.md` §6 already calls 1.70 thin. First thing to check
  on a test print.
- **[?]** The four relocated locks now sit in blind pockets opening toward the
  gear slot rather than being pinched full-length; retention is weaker than
  upstream, and the head's far side is no longer pinned.
- **[?]** Ring variant leaves the mid shell as a short top ring above `04`;
  its support has not been checked under load.
- **[?]** Whether the deepened waist detent is too stiff to turn by hand.
  12.52 mm³ peak is nearly double the stock 6.43, and that is a printed flexure.
- **[?]** **The yoke's floor is 1.96 mm.** It is the only thing holding the leaf
  down and it prints as a small bridge over the slot. If it proves weak, the
  lift is the lever — every extra millimetre of `MODULE_LIFT` is another
  millimetre of floor, at a millimetre of extra height.
- **[?]** **What stops the fold at 90°.** Upstream nothing does either — the
  sweep runs clean past 120° — so the handle is held open by the detent alone,
  which is 3 clicks up and no more positive than the 4th.
- **[?]** The leaf is guided in the swing plane over ±3.58 of its ±7.07 half
  width, where upstream it had ±6.66. Whether that is enough to keep it from
  cocking has not been tested.
- **[?]** **The head has no pins in it** (§4.4). Its far side is held
  by the journal tube and the two retaining flanges, with the halves closed at
  the neck by `16 - Handle Lock` and the hinge pin. That is the Tactical's own
  arrangement, but this head is a longer cantilever than the Tactical's, and
  nothing about the load has been calculated.
- **[M]** **Two cosmetic consequences of the donor body being shorter.** The
  Spinner Fuse handle was drawn for a 50 mm body and this one is 80 mm:
  - stowed, the lever covers **y 43 .. 83 of a −0.35 .. 79.7 body** — the top
    half only, where on the donor it runs nearly to the floor;
  - the yoke is bare between the body top and the hub, **y 79.7 .. 84.4**.

  Both work; neither looks like the donor. Lengthening the lever means drawing
  new geometry rather than trimming upstream, which is why it was not done.

### 8.1 Recorded, so it is not re-derived

**[M]** `12 - Optional Middle Spring` is the one Spinner Fuse file shipped in
plate coordinates. Its bbox matches `11 - Middle Spring`'s exactly, but dropping
it on that bbox as-shipped drives it 51.7 mm³ into `07` / `09` / `01`. Turning it
180° about its own normal first brings that to 0.01 mm³ and puts its engaging arm
at y ≈ 29.4 against `11`'s y ≈ 30 — the same seat and the same engagement height,
so the two really are alternates. A **proper rotation, not a mirror**: the
mirrored candidates score identically only because the plate is symmetric, and
mirroring a printed part is how `DESIGN.md` §7 item 2 says these searches go
wrong. Neither spring is used by this build — §3 uses the base's own
`20 - Mid Shell Spring` — but the measurement stands.

---

## 9. Files

```
python tools/build_custom.py waist    # Custom_Waist_Ring_2pc, Custom_Waist_Native_2pc
python tools/build_custom.py head     # Custom_Head -- gear, ring, spring and the fold
python tools/build_custom.py toy      # Custom_Toy_Ring_2pc, Custom_Toy_Native_2pc
python tools/build_custom.py parts    # printable STLs of every changed part
```

Geometry in `tools/custom.py`, driver in `tools/build_custom.py`, output in
`Derivatives/custom/`. Nothing here writes into a product folder.

The shipped `Custom_Toy_*` files are the handle stowed at 0°. Any other fold
angle is one argument away — `custom.toy_items(ring=True, deg=90.0)` gives the
same assembly with the handle up.
