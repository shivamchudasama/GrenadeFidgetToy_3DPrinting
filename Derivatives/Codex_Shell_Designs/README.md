# Codex shell designs

Five coordinated cosmetic shell sets for the **Fidget Fuse Tactical 7-in-1**.
Each design folder contains three print-ready STLs:

- `Bottom_Shell` replaces `04 - Bottom Shell 01.stl.stl`.
- `Mid_Shell` is a one-piece replacement for the `32` + `33` two-piece assembly,
  based on `Mid Shell Solid Color.stl.stl`.
- `Upper_Shell_Top` replaces `27 - Upper Shell Top.stl.stl`.

## Designs

1. **Diamond Grip** — crossed diagonal grip grooves.
2. **Spiral Ribs** — eight sweeping helical grip channels.
3. **Dragon Scales** — layered scalloped scale lines.
4. **Dimple Field** — staggered tactile dimples.
5. **Armor Panels** — staggered plate seams with recessed bolt marks.

All parts retain the upstream print orientation, are centred on X/Y, and sit at
`Z=0`. Decoration is recessed by no more than 0.8 mm into outward-facing surfaces.
Inward-facing mating surfaces and protected top/bottom interface bands are not
moved. See `manifest.json` for per-file geometry validation and dimensions.

Regenerate everything from the repository root with:

```powershell
python tools\build_codex_shell_designs.py
```
