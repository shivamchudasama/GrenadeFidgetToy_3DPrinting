"""Where the printable package lives, and a guard so nothing writes elsewhere.

Six scripts need these paths, so a version bump should be one line rather than
six.  Change PACKAGE_NAME and everything downstream follows.

Released versions are **frozen**.  Once a package folder has been published it
is a record of what somebody printed, so the build scripts must never write
back into it: bump PACKAGE_NAME, copy the previous folder forward, and build
into the new one.  ``guard()`` enforces that in code, the way fidget.save()
enforces the repo-root rule -- a mistyped path fails loudly instead of quietly
rewriting a shipped design.
"""
from __future__ import annotations

import os

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TOOLS_DIR)

# The package currently being built.  Bump this, copy the previous folder
# forward, then build.
PACKAGE_NAME = "Hybrid_Grenade_v1.3"

# Frozen: shipped packages that scripts must not write into.  Every folder
# matching Hybrid_Grenade_v* other than PACKAGE_NAME is treated as frozen
# whether or not it is listed here; this is the explicit record.
FROZEN_PACKAGES = ("Hybrid_Grenade_v1.1", "Hybrid_Grenade_v1.2")

PACKAGE_DIR = os.path.join(ROOT_DIR, PACKAGE_NAME)
ASSEMBLED_SUBDIR = "All_Parts_Assembled_Coordinates"
ASSEMBLED_DIR = os.path.join(PACKAGE_DIR, ASSEMBLED_SUBDIR)


def guard(path):
    """Return ``path`` if it is safe to write, otherwise raise.

    A write is safe when it lands inside PACKAGE_DIR.  Anything under another
    Hybrid_Grenade_v* folder is refused outright, since that is a shipped
    package; anything outside the repo is refused as well.
    """
    target = os.path.abspath(path)
    root = os.path.abspath(ROOT_DIR)
    try:
        inside = os.path.commonpath([target, root]) == root
    except ValueError:          # different drives on Windows
        inside = False
    if not inside:
        raise ValueError("refusing to write outside the repo: %s" % target)

    rel = os.path.relpath(target, root)
    top = rel.split(os.sep)[0]
    if top.startswith("Hybrid_Grenade_v") and top != PACKAGE_NAME:
        raise ValueError(
            "refusing to write into %s -- it is a shipped package. Bump "
            "PACKAGE_NAME in tools/package_paths.py, copy the folder forward, "
            "and build into the new one instead." % top)
    return path
