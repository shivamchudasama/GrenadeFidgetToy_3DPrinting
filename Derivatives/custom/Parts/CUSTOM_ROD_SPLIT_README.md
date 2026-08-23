# Custom rod upper-yoke split

The upper folding yoke is no longer fused into one support-prone mesh.
`Custom_Rod_Middle.stl` now carries only the center linear-track slab above the
unchanged lower rod. The donor-derived outer slabs and adapted wedge are:

- `Custom_Rod_Upper_Right.stl`
- `Custom_Rod_Upper_Left.stl`
- `Custom_Rod_Upper_Lock.stl`

The existing lower parts remain in use:

- `Custom_Rod_Right.stl`
- `Custom_Rod_Middle.stl`
- `Custom_Rod_Left.stl`
- `Custom_Rod_Lock_Upper_06.stl`
- `Custom_Rod_Lock_Lower_07.stl`
- `Custom_Rod_Bottom_Lock.stl`

## Printing

- Lay each Upper Right/Left member on its broad 1.705 mm face. The lock tunnel
  then runs vertically through the print and needs no support.
- Lay the Upper Lock on its 8.0 x 2.0 mm face; its printed height is 1.3 mm.
- Keep the proven lower-rod orientation for Right/Left. For Middle, angle the
  long axis about 45 degrees from the build plate if the slicer's bridge preview
  flags the center-track graft; the former outer-slab ceiling has been removed.
- Use a brim for the long Middle part if it is printed on an angled edge.

The upper key has 0.150 mm nominal CSG clearance per bounding face and a measured
nearest surface gap of 0.0977 mm. Print the key first if the printer's dimensional
accuracy is unknown.

## Assembly

1. Fit `09 - Rod Spring` into the center linear track.
2. Place Upper Right and Upper Left against the track, aligning the lower wedge
   tunnel and the upper hinge bore.
3. Push `Custom_Rod_Upper_Lock` transversely through the lower tunnel. It spans
   all three members and captures 0.420 mm beyond each outer face.
4. Fit the handle halves and insert `15 - Handle Rotating Lock` through the
   hinge bore. This hinge pin is the upper transverse retainer, as on the donor.
5. Assemble the unchanged lower Right/Middle/Left stack with locks 06 and 07,
   then install the unchanged bottom lock.

See `../Custom_Rod_Split_Preview.png` for assembled and exploded views.
