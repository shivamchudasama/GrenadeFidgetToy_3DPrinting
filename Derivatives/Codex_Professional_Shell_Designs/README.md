# Professional Tactical shell designs

Five new coordinated shell families for the **Fidget Fuse Tactical 7-in-1**.
This generation was rebuilt from a clean exterior base and does not reuse the
procedural groove designs from `Codex_Shell_Designs`.

## Families

1. **AeroFlow** — 16 long, softly swept ribs shaped as continuous ergonomic grips.
2. **Vector Chevron** — 16 sculpted directional chevrons with rounded shoulders.
3. **Orbit** — a completely redesigned staggered field of rounded traction pods.
4. **Ergo Scoops / Thread-Cut Rails** — twelve continuous vertical grip rails
   cut by a four-start right-hand screw-thread pattern, with crowned rail faces
   and continuously rounded cutter-edge fillets.
5. **Contour Twist** — deep twisted torque flutes with narrow crests, recessed
   valleys, and a two-colour mid-shell reveal.

Each family contains:

- `Bottom_Shell`, replacing `04 - Bottom Shell 01.stl.stl`;
- `Mid_Shell`, a one-piece replacement for the `32` + `33` assembly;
- `Upper_Shell_Top`, replacing `27 - Upper Shell Top.stl.stl`.

AeroFlow, Vector Chevron, Orbit, and Thread-Cut Rails use furnished cosmetic
skins sampled at 720 positions around the shell and at no more than 0.14 mm
axially. Their raised features blend through C2-continuous fillets for clean
highlights and smooth exported surfaces. Contour Twist retains its established
finished tessellation and geometry.

Contour Twist is the two-colour exception: its mid-shell is split into
`Mid_Shell_Outer` and `Mid_Shell_Inner`, derived from the original `33 - Mid
Shell P01` and `32 - Mid Shell P02` pair. Six rounded diagonal windows in the
outer contour valleys reveal the contrasting inner shell. The provided 3MF and
close-up preview use the corrected P01/P02 clocking and original axial fit.

All mating geometry comes from the originals. Only explicitly designated outer
cosmetic bands are changed; the upper functional neck, bores, snap features,
ledges, and top/bottom interfaces remain untouched. Parts are centred on X/Y,
retain the original print orientation, and sit at `Z=0`.

AeroFlow and Vector Chevron use a dense 16-feature circumference (about 7.9 mm
pitch on the 40 mm shell body) so a fingertip readily catches a raised grip when
spinning any shell in the assembled fidget toy.

The other families use distinct grip mechanisms: Orbit's staggered pods break
up every smooth circumferential lane, Ergo Scoops now uses twelve chamfered
vertical rails interrupted by four interleaved helical cuts, and Contour Twist
uses a larger crest-to-valley depth with steeper torque faces. The thread cuts
pass completely through the raised rails and continue only slightly into the
base skin, producing repeated tactile drive blocks without weakening the shell.

## Contour Twist two-colour assembly

1. Print `05_Contour_Twist_Mid_Shell_Outer.stl` in the main shell colour.
2. Print `05_Contour_Twist_Mid_Shell_Inner.stl` in the reveal colour.
3. Keep the inner part upright as exported. Flip the outer part top-to-bottom,
   nest it over the inner part, rotate to the keyed notch position, and seat the
   original P01/P02 snap fit. The reference assembly corrects the independently
   recorded source poses by rotating the inner part `+6°`; the three equivalent
   seated positions repeat every `120°`.

`05_Contour_Twist_Mid_Shell_2Color_Assembly.3mf` is an assembled reference with
named main/reveal materials, not a print-plate layout. The matching GLB embeds
the display colours for general 3D viewers, while
`two_colour_mid_shell_preview.png` gives a quick rendered reference.

`05_Contour_Twist_Full_Shell_Assembly.glb` contains the Bottom Shell, Mid Shell
Inner, Mid Shell Outer, and Upper Shell Top as four named components with four
distinct embedded colours for design review.

Regenerate from the repository root:

```powershell
python tools\build_professional_shell_designs.py
```

`manifest.json` records per-file topology and protected-surface validation.
