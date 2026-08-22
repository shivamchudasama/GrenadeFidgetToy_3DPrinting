"""Build the Tactical common body in each mid-shell variant.

The bottom assembly order is intentional and follows the supplied instructions.
"""
from __future__ import annotations

import assembly as A


SUBDIR = "tactical/Body"

# Construction order, including the directionally inserted nested parts.
ORDER = [
    "04 - Bottom Shell 01",
    "05 - Bottom Shell 02",
    "06 - Bottom Shell 03",
    "01 - Bottom Lock Shell",
    "02 - Bottom Spring",
    "03 - Bottom Shell Spacer",
    "32 - Mid Shell P02",
    "33 - Mid Shell P01",
    "Mid Shell Solid Color",
    "Hex Mid Shell Solid Color",
    "20 - Mid Shell Spring",
    "08 - Internal Barrel",
    "09 - Internal Barrel Pin v1.1",
    "10 - Internal Barrel v1.1",
    "11 - Internal Barrel v1.1",
    "12 - Internal Barrel Spring v1.1",
    "13 - Internal Barrel Spring v1.1",
    "14 - Internal Barrel Spring v1.1",
    "07 - Internal Barrel Cap",
    "28 - Upper Shell Gear",
    "29 - Upper Shell Lock Ring",
    "30 - Upper Shell Rotating Spring",
    "27 - Upper Shell Top",
]

VARIANTS = {
    "Tactical_Body_MidShell_2pc": dict(exclude=(), include=()),
    "Tactical_Body_MidShell_Solid": dict(
        exclude=("32 - Mid Shell P02", "33 - Mid Shell P01"),
        include=("Mid Shell Solid Color",),
    ),
    "Tactical_Body_MidShell_Hex": dict(
        exclude=("32 - Mid Shell P02", "33 - Mid Shell P01"),
        include=("Hex Mid Shell Solid Color",),
    ),
}


def main():
    for stem, selection in VARIANTS.items():
        items = A.items_from_poses(
            "tactical", groups=["common"], order=ORDER, **selection
        )
        A.build(items, stem, SUBDIR)


if __name__ == "__main__":
    main()
