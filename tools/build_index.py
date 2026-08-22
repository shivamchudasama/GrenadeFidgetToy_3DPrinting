"""Scan Originals/ and write tools/parts_index.json.

Records identity, size and mesh health for every STL, plus which parts are
congruent with which -- several parts are exact copies or mirrors of another,
so changing one means changing its twin. Occasional script; re-run after any
change to Originals/.

    python tools/build_index.py
"""
import hashlib
import json
import os
from collections import defaultdict

import numpy as np
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Originals/
ORIG = ROOT
PRODUCTS = {
    "grenade": "Fidget Fuse Grenade 5-in-1 Snap-Fit Fidget Toy",
    "tactical": "Fidget Fuse Tactical 7-in-1 Snap-Fit Fidget Toy",
    "spinner": "Spinner Fuse Grenade 5-in-1 Snap-Fit Fidget Toy",
}
# Congruence tolerance. Well under print resolution, well above the float32
# noise in the STL coordinates -- copies that differ only in tessellation land
# around 0.003 mm.
CONGRUENT_TOL = 0.01


def _frames():
    """The 48 signed axis permutations, for principal-axis alignment."""
    import itertools
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            P = np.zeros((3, 3))
            for i, j in enumerate(perm):
                P[i, j] = signs[i]
            yield P


def congruence(a, b):
    """(max surface deviation, handedness) of b onto a, best over all frames.

    Parts are copied around the build plate by arbitrary rotation as well as
    mirroring, so testing mirrors alone misses most of them.
    """
    A = a.copy(); A.apply_translation(-A.center_mass)
    B = b.copy(); B.apply_translation(-B.center_mass)
    Ra = np.linalg.eigh(A.moment_inertia)[1]
    Rb = np.linalg.eigh(B.moment_inertia)[1]
    best, hand = 1e9, 0
    for P in _frames():
        R = Ra @ P @ Rb.T
        det = np.linalg.det(R)
        if abs(abs(det) - 1) > 1e-6:
            continue
        d = trimesh.proximity.closest_point(A, (R @ B.vertices.T).T)[1].max()
        if d < best:
            best, hand = d, det
    return best, ("rotation" if hand > 0 else "reflection")


def stem(fn):
    s = fn
    for _ in range(3):
        if s.lower().endswith(".stl"):
            s = s[:-4]
    return s


def repair(m):
    """Drop coincident opposite-normal face pairs; mirrors fidget._repair."""
    srt = np.sort(m.faces, axis=1)
    uq, cnt = np.unique(srt, axis=0, return_counts=True)
    if not (cnt > 1).any():
        return m, 0
    drop = np.zeros(len(m.faces), bool)
    for d in uq[cnt > 1]:
        drop[np.where((srt == d).all(axis=1))[0]] = True
    return trimesh.Trimesh(m.vertices, m.faces[~drop], process=True), int(drop.sum())


def main():
    rows, meshes = [], {}
    for key, folder in PRODUCTS.items():
        d = os.path.join(ORIG, folder)
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith(".stl"):
                continue
            p = os.path.join(d, fn)
            raw = trimesh.load(p, process=False)
            m, dropped = repair(trimesh.load(p, process=True))
            ext = m.bounds[1] - m.bounds[0]
            rows.append({
                "product": key,
                "folder": folder,
                "file": fn,
                "stem": stem(fn),
                "md5": hashlib.md5(open(p, "rb").read()).hexdigest(),
                "bytes": os.path.getsize(p),
                "triangles": int(len(raw.faces)),
                "repaired_faces": dropped,
                "watertight": bool(m.is_watertight),
                "winding_consistent": bool(m.is_winding_consistent),
                "bodies": int(m.body_count),
                "volume_mm3": round(float(m.volume), 3) if m.is_watertight else None,
                "bbox_mm": [round(float(v), 3) for v in ext],
                "origin_mm": [round(float(v), 3) for v in m.bounds[0]],
                "congruent_with": [],
            })
            c = m.copy()
            c.apply_translation(-c.bounds.mean(axis=0))
            meshes[fn] = c

    # Congruence. Bucket on rotation-invariant quantities (volume, area, the
    # principal moments), then confirm each candidate pair by aligning
    # principal axes and measuring the worst surface deviation.
    buck = defaultdict(list)
    for r in rows:
        if not r["watertight"]:
            continue
        m = meshes[r["file"]]
        inertia = np.sort(np.linalg.eigvalsh(m.moment_inertia))
        inertia = inertia / max(abs(inertia).max(), 1e-9)
        buck[(round(r["volume_mm3"], 1), round(float(m.area), 1),
              tuple(np.round(inertia, 4)))].append(r)

    by_file = {r["file"]: r for r in rows}
    for group in buck.values():
        if len(group) < 2:
            continue
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                dev, how = congruence(meshes[a["file"]], meshes[b["file"]])
                if dev < CONGRUENT_TOL:
                    by_file[a["file"]]["congruent_with"].append(
                        [b["file"], how, round(float(dev), 5)])
                    by_file[b["file"]]["congruent_with"].append(
                        [a["file"], how, round(float(dev), 5)])

    with open(os.path.join(ROOT, "tools", "parts_index.json"), "w") as f:
        json.dump(rows, f, indent=1)

    bad = [r for r in rows if not r["watertight"]]
    fixed = [r for r in rows if r["repaired_faces"]]
    print("indexed %d parts" % len(rows))
    print("watertight after repair: %d/%d" % (len(rows) - len(bad), len(rows)))
    for r in fixed:
        print("   repaired %s (dropped %d face(s))" % (r["file"], r["repaired_faces"]))
    for r in bad:
        print("   STILL BAD %s" % r["file"])

    # congruence classes = connected components over the links
    parent = {r["file"]: r["file"] for r in rows}

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in rows:
        for other, _how, _dev in r["congruent_with"]:
            ra, rb = root(r["file"]), root(other)
            if ra != rb:
                parent[ra] = rb
    classes = defaultdict(list)
    for r in rows:
        classes[root(r["file"])].append(r["file"])
    shared = {k: v for k, v in classes.items() if len(v) > 1}
    print("\n%d files -> %d distinct shapes (%d congruence classes)"
          % (len(rows), len(classes), len(shared)))
    for members in sorted(shared.values(), key=lambda m: -len(m)):
        head = by_file[members[0]]
        print("   [%d] vol=%9.1f mm3" % (len(members), head["volume_mm3"]))
        for f in members:
            how = next((h for o, h, _ in by_file[f]["congruent_with"]), "-")
            print("        %-9s %-46s %s" % (by_file[f]["product"], f, how))

    for r in rows:
        if r["bodies"] > 1:
            print("   multi-body: %-9s %s  bodies=%d"
                  % (r["product"], r["file"], r["bodies"]))


if __name__ == "__main__":
    main()
