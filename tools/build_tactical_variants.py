"""Build the Tactical body-plus-top combinations from the pose record."""
from __future__ import annotations

import numpy as np

import assembly as A
from build_tactical_body import ORDER


VARIANTS = (
    ("Tactical_Bottle_5in1", ["common", "bottle-5in1 top"], (), ()),
    ("Tactical_Spinner_7in1", ["common", "spinner-7in1 top"], (), ()),
    ("Tactical_Grenade_6in1", ["common", "grenade-6in1 top"], (), ()),
    (
        "Tactical_Spinner_7in1_MidShellSolid",
        ["common", "spinner-7in1 top"],
        ("32 - Mid Shell P02", "33 - Mid Shell P01"),
        ("Mid Shell Solid Color",),
    ),
    (
        "Tactical_Spinner_7in1_HexMidShell",
        ["common", "spinner-7in1 top"],
        ("32 - Mid Shell P02", "33 - Mid Shell P01"),
        ("Hex Mid Shell Solid Color",),
    ),
)


def build_grenade_with_kit():
    """Grenade 6-in-1, exploded, with the unsolved top parts as a kit column.

    Kept in the build so it is regenerated with everything else -- it was
    previously a one-off and silently went stale against the pose record when
    the lower stack was corrected.
    """
    rec = A.poses("tactical")
    items = A.items_from_poses(
        "tactical", groups=["common", "grenade-6in1 top"], order=ORDER)
    items = A.coloured(items)
    disp = A.explode(items)

    kit = A.coloured(A.kit_column(rec["unsolved_grenade_top"]), start=len(items))
    allitems = items + kit
    alldisp = np.vstack([disp, np.zeros((len(kit), 3))])

    print("%-44s %2d placed + %d unsolved kit"
          % ("Tactical_Grenade_6in1_..._unsolved_kit", len(items), len(kit)))
    # the stem already reads "exploded", so write it directly rather than
    # through A.write(), which would append a second "_exploded" tag
    sc = A.scene(allitems, alldisp)
    stem = "Tactical_Grenade_6in1_exploded_with_unsolved_kit"
    return [A.fidget.save(sc, "%s.%s" % (stem, ext), subdir="tactical")
            for ext in ("3mf", "glb")]


def main():
    for stem, groups, exclude, include in VARIANTS:
        items = A.items_from_poses(
            "tactical", groups=groups, exclude=exclude, include=include, order=ORDER
        )
        A.build(items, stem, "tactical")
    build_grenade_with_kit()


if __name__ == "__main__":
    main()
