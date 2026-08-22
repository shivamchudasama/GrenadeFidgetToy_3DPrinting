"""
STL-native workflow for the Fidget Fuse parts.

These parts are meshes, not CAD. There is no feature tree to edit, so a part is
modified by CSG against solid primitives, not by changing a dimension. Two lanes:

    mesh lane  (default)  trimesh + manifold3d  -- fast, robust, handles the
                                                   161k-triangle gears fine
    CAD lane   (opt-in)   OCP / cadquery        -- exact B-rep, needed only for
                                                   fillets and analytic ops, and
                                                   very slow above ~20k faces

Everything lives inside Originals/. The three product folders are pristine
upstream and read-only; output goes to Derivatives/. save() refuses both a
product folder and any path escaping Originals/.

    import fidget
    m = fidget.load("10_Body_OuterShell v2")      # -> trimesh.Trimesh
    m = fidget.cut(m, fidget.cylinder(d=4, h=30, at=(12, 0, 0)))
    fidget.save(m, "OuterShell_vented.stl")       # -> Derivatives/

CLI:
    python tools/fidget.py list [product]
    python tools/fidget.py info <query>
    python tools/fidget.py check
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

import numpy as np
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Originals/
DERIVATIVES = os.path.join(ROOT, "Derivatives")
INDEX_PATH = os.path.join(ROOT, "tools", "parts_index.json")

ENGINE = "manifold"  # manifold3d: the only engine installed, and the good one

PRODUCTS = {
    "grenade": "Fidget Fuse Grenade 5-in-1 Snap-Fit Fidget Toy",
    "tactical": "Fidget Fuse Tactical 7-in-1 Snap-Fit Fidget Toy",
    "spinner": "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy",
}

# The pristine upstream downloads. tools/ and Derivatives/ live alongside them
# inside Originals/, so "read-only" is these three folders specifically -- not
# the whole of ROOT, which is now also where output goes.
PRISTINE = [os.path.abspath(os.path.join(ROOT, f)) for f in PRODUCTS.values()]

# --------------------------------------------------------------------------
# index / lookup
# --------------------------------------------------------------------------

_index = None


def index():
    """Rows from tools/parts_index.json. Rebuild with tools/build_index.py."""
    global _index
    if _index is None:
        with open(INDEX_PATH) as f:
            _index = json.load(f)
    return _index


def path_of(row):
    return os.path.join(ROOT, row["folder"], row["file"])


def find(query, product=None):
    """Rows matching query, best match class first.

    Tactical carries two overlapping number series, so a bare number is
    genuinely ambiguous -- every candidate comes back and the caller decides.
    """
    rows = index()
    if product:
        rows = [r for r in rows if r["product"] == product]
    q = str(query).strip().lower()

    exact = [r for r in rows if r["file"].lower() == q or r["stem"].lower() == q]
    if exact:
        return exact
    starts = [r for r in rows if r["stem"].lower().startswith(q)]
    if starts:
        return starts
    return [r for r in rows if q in r["stem"].lower()]


def resolve(query, product=None):
    """Exactly one row, or raise with the candidates spelled out."""
    if isinstance(query, dict):
        return query
    hits = find(query, product)
    if not hits:
        raise KeyError("no part matches %r%s"
                       % (query, " in " + product if product else ""))
    if len(hits) > 1:
        listing = "\n".join("    %-9s %s" % (r["product"], r["file"]) for r in hits)
        raise KeyError(
            "%r is ambiguous, %d matches:\n%s\n"
            "    pass a longer query, or product=('grenade'|'tactical'|'spinner')"
            % (query, len(hits), listing)
        )
    return hits[0]


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def _repair(m):
    """Drop coincident opposite-normal face pairs (zero-volume flaps).

    '24 - Rod Left.stl.stl' ships with exactly one such pair, which is the only
    thing standing between it and a watertight mesh.
    """
    srt = np.sort(m.faces, axis=1)
    uq, cnt = np.unique(srt, axis=0, return_counts=True)
    if not (cnt > 1).any():
        return m
    drop = np.zeros(len(m.faces), bool)
    for d in uq[cnt > 1]:
        drop[np.where((srt == d).all(axis=1))[0]] = True
    return trimesh.Trimesh(m.vertices, m.faces[~drop], process=True)


def load(query, product=None, repair=True, center=False):
    """A part as a trimesh.Trimesh.

    Coordinates are left at their original plate position by default, so an
    export drops back where it came from. center=True moves it to the origin.
    """
    row = resolve(query, product)
    m = trimesh.load(path_of(row), process=True)
    if repair:
        m = _repair(m)
    if center:
        m.apply_translation(-m.bounds.mean(axis=0))
    m.metadata["fidget_source"] = row["file"]
    m.metadata["fidget_product"] = row["product"]
    return m


def twins(query, product=None):
    """Parts congruent with this one, as (file, how, deviation_mm).

    Several parts are the same shape copied around the plate by rotation or
    reflection, so a change to one usually has to be made to the others too.
    """
    return [tuple(t) for t in resolve(query, product)["congruent_with"]]


def solid(query, product=None):
    """A part as a cadquery Workplane (B-rep, one planar face per triangle).

    Only worth it for analytic operations. Booleans get impractical well before
    the heavy gears -- prefer the mesh lane.
    """
    import cadquery as cq
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeShapeOnMesh
    from OCP.Message import Message_ProgressRange
    from OCP.RWStl import RWStl

    m = load(query, product)
    fh = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
    tmp = fh.name
    fh.close()
    try:
        m.export(tmp)
        tri = RWStl.ReadFile_s(tmp, Message_ProgressRange())
    finally:
        os.unlink(tmp)
    mk = BRepBuilderAPI_MakeShapeOnMesh(tri)
    mk.Build(Message_ProgressRange())
    return cq.Workplane(obj=cq.Shape.cast(mk.Shape()))


# --------------------------------------------------------------------------
# CSG
# --------------------------------------------------------------------------

def _check(m, who):
    if not m.is_watertight:
        raise ValueError("%s is not watertight; CSG would give garbage" % who)
    return m


def cut(mesh, *tools):
    """mesh minus tools."""
    return trimesh.boolean.difference([_check(mesh, "mesh")] + list(tools),
                                      engine=ENGINE)


def union(*meshes):
    return trimesh.boolean.union(list(meshes), engine=ENGINE)


def intersect(*meshes):
    return trimesh.boolean.intersection(list(meshes), engine=ENGINE)


def cylinder(d, h, at=(0, 0, 0), axis="z", sections=96):
    """Solid cylinder, centred on `at`, for use as a CSG tool."""
    c = trimesh.creation.cylinder(radius=d / 2.0, height=h, sections=sections)
    if axis == "x":
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    elif axis == "y":
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    c.apply_translation(at)
    return c


def box(size, at=(0, 0, 0)):
    b = trimesh.creation.box(extents=size)
    b.apply_translation(at)
    return b


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------

def save(obj, name, subdir=""):
    """Write into Derivatives/.

    Refuses to write into the three pristine product folders, and refuses to
    escape Originals/ entirely -- a '../' in `name` or `subdir` would otherwise
    land output somewhere nobody asked for.
    """
    dest = os.path.abspath(os.path.join(DERIVATIVES, subdir, name))
    root = os.path.abspath(ROOT)
    if os.path.commonpath([dest, root]) != root:
        raise PermissionError(
            "refusing to write outside Originals/: %s" % dest)
    for pristine in PRISTINE:
        if os.path.commonpath([dest, pristine]) == pristine:
            raise PermissionError(
                "%s is pristine upstream and read-only" % os.path.basename(pristine))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if hasattr(obj, "export"):          # trimesh
        obj.export(dest)
    else:                               # cadquery
        import cadquery as cq
        cq.exporters.export(obj, dest)
    print("wrote %s  (%.2f MB)" % (os.path.relpath(dest, ROOT),
                                   os.path.getsize(dest) / 1e6))
    return dest


def openscad(query, product=None):
    """The import() line for a part -- OpenSCAD reads STL, not STEP."""
    row = resolve(query, product)
    return 'import("%s");' % path_of(row).replace(os.sep, "/")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _fmt(r):
    bb = "x".join("%g" % v for v in r["bbox_mm"])
    vol = "{:,.1f}".format(r["volume_mm3"]) if r["volume_mm3"] else "-"
    return "%-9s %9s tri %12s mm3  %22s  %s" % (
        r["product"], "{:,}".format(r["triangles"]), vol, bb, r["file"])


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "list"
    if cmd == "list":
        rows = index()
        if len(argv) > 2:
            rows = [r for r in rows if r["product"] == argv[2]]
        for r in rows:
            print(_fmt(r))
        print("\n%d parts" % len(rows))
    elif cmd == "info":
        for r in find(" ".join(argv[2:])):
            print(_fmt(r))
            print("   origin %s  watertight=%s bodies=%s"
                  % (r["origin_mm"], r["watertight"], r["bodies"]))
            for f, how, dev in r["congruent_with"]:
                print("   twin: %-46s %-10s %.4f mm" % (f, how, dev))
    elif cmd == "check":
        bad = []
        for r in index():
            if not load(r).is_watertight:
                bad.append(r["file"])
        print("%d/%d watertight after repair" % (len(index()) - len(bad), len(index())))
        for b in bad:
            print("   FAILS:", b)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
