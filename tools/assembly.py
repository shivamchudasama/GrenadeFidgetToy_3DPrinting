"""Build assembled / exploded scenes from a pose record.

Poses are stored as 4x4 matrices in Derivatives/<product>/*_poses.json, so an
assembly is reproducible without re-running the fitting search that found it.
Scene output keeps parts separate and individually coloured (.3mf/.glb) plus a
merged single mesh (.stl) for tools that read nothing else.

    import assembly as A
    items = A.items_from_poses("tactical", groups=["common"])
    A.build(items, "Tactical_Body", "tactical")
"""
from __future__ import annotations

import json
import os
import re

import numpy as np
import trimesh

import fidget

POSES = {
    "tactical": os.path.join(fidget.DERIVATIVES, "tactical",
                             "Tactical_variants_poses.json"),
}

# a categorical palette that stays legible when 30 parts share one image
PALETTE = [(214, 93, 84), (93, 150, 209), (122, 181, 102), (228, 169, 73),
           (150, 120, 196), (86, 182, 178), (219, 124, 171), (160, 168, 74),
           (110, 132, 203), (206, 140, 90), (98, 176, 140), (196, 104, 133),
           (126, 158, 190), (178, 152, 88), (139, 175, 198), (203, 116, 102),
           (114, 169, 180), (171, 138, 180), (148, 176, 120), (184, 126, 152),
           (95, 143, 166), (212, 158, 120), (131, 151, 132), (176, 110, 120),
           (120, 166, 158), (199, 177, 105), (108, 124, 158), (190, 146, 174),
           (140, 180, 166), (166, 132, 110)]


def color_for(i):
    return PALETTE[i % len(PALETTE)]


# ------------------------------------------------------------------ poses ---
def poses(product="tactical"):
    with open(POSES[product]) as f:
        return json.load(f)


def posed(entry, product="tactical"):
    """One pose record -> a transformed mesh in toy coordinates."""
    m = fidget.load(entry["source_stl"], product=product)
    m.apply_transform(np.asarray(entry["matrix"], float))
    return m


def items_from_poses(product="tactical", groups=None, include=(), exclude=(),
                     order=None):
    """[(name, mesh)] for the pose entries selected by group and/or name."""
    rows = poses(product)["parts"]
    by_name = {r["part"]: r for r in rows}
    picked = [r for r in rows if groups is not None and r["group"] in groups]
    for n in include:
        if n not in by_name:
            raise KeyError("no pose for %r" % n)
        if by_name[n] not in picked:
            picked.append(by_name[n])
    picked = [r for r in picked if r["part"] not in exclude]
    if order:
        rank = {n: i for i, n in enumerate(order)}
        picked.sort(key=lambda r: rank.get(r["part"], len(rank)))
    return [(r["part"], posed(r, product)) for r in picked]


# ----------------------------------------------------------------- checks ---
def interference(items, min_mm3=1.0):
    """Overlapping pairs, largest first. items: [(name, mesh)] or [(n, m, c)]."""
    ms = [(it[0], it[1]) for it in items]
    bad = []
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            a, b = ms[i][1], ms[j][1]
            if (a.bounds[0] > b.bounds[1]).any() or (b.bounds[0] > a.bounds[1]).any():
                continue
            try:
                v = trimesh.boolean.intersection([a, b], engine=fidget.ENGINE).volume
            except Exception:
                continue
            if v > min_mm3:
                bad.append((v, ms[i][0], ms[j][0]))
    bad.sort(reverse=True)
    return bad


# ---------------------------------------------------------------- explode ---
def explode(items, axis=1, margin=7.0, gap=3.5, axial_gain=0.40, slender=1.5,
            sat_spread=1.0):
    """items: [(name, mesh, color)] -> (n,3) displacements.

    These toys are all one concentric stack plus off-axis satellites, so a
    single linear pull-apart makes a 6x-too-tall ribbon: a 50 mm slider forces
    the whole column open. Split them instead --

      core       footprint straddles the axis and is squat enough to be a
                 stacking element (height < `slender` x its own diameter)
                 -> spread along the axis with bbox gaps
      satellite  everything else, including any long thin rod that threads
                 through the stack -> pushed radially clear of the core, so a
                 100 mm rod never stretches the column to match
    """
    other = [i for i in range(3) if i != axis]
    box = np.array([it[1].bounds for it in items])
    ctr = box.mean(1)
    n = len(items)

    straddles = np.array([(box[k, 0, other] < 0).all() and (box[k, 1, other] > 0).all()
                          for k in range(n)])
    height = box[:, 1, axis] - box[:, 0, axis]
    width = (box[:, 1][:, other] - box[:, 0][:, other]).max(axis=1)
    rc = np.linalg.norm(ctr[:, other], axis=1)
    # a long handle straddles the axis without being *on* it -- require both
    core = straddles & (height < slender * width) & (rc < 0.35 * width)

    foot_r = np.maximum(np.abs(box[:, 0][:, other]), np.abs(box[:, 1][:, other]))
    foot_r = np.linalg.norm(foot_r, axis=1)
    R_core = foot_r[core].max() if core.any() else 0.0

    disp = np.zeros((n, 3))
    sats = np.where(~core)[0]
    # satellites with no usable radial direction get fanned out evenly
    rv = ctr.copy()
    rv[:, axis] = 0.0
    r = np.linalg.norm(rv, axis=1)
    spare = iter(np.linspace(0, 2 * np.pi, max(1, int((r[sats] < 1.0).sum())),
                             endpoint=False))
    for k in sats:
        if r[k] < 1.0:
            a = next(spare)
            d = np.zeros(3)
            d[other[0]] = np.cos(a)
            d[other[1]] = np.sin(a)
        else:
            d = rv[k] / r[k]
        own = np.linalg.norm([max(abs(box[k, 0, o]), abs(box[k, 1, o])) for o in other])
        target = R_core + margin + own * sat_spread
        disp[k] = d * max(0.0, target - r[k])

    c0 = (box[:, 1, axis].max() + box[:, 0, axis].min()) / 2
    disp[:, axis] += (ctr[:, axis] - c0) * axial_gain

    # lanes: anything whose displaced cross-section still overlaps gets spread
    lo = box[:, 0][:, other] + disp[:, other]
    hi = box[:, 1][:, other] + disp[:, other]
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(n):
        for j in range(i + 1, n):
            if (lo[i] < hi[j]).all() and (lo[j] < hi[i]).all():
                parent[find(i)] = find(j)
    lanes = {}
    for i in range(n):
        lanes.setdefault(find(i), []).append(i)

    for members in lanes.values():
        members.sort(key=lambda i: ctr[i, axis] + disp[i, axis])
        before = np.mean([ctr[i, axis] + disp[i, axis] for i in members])
        cursor = -np.inf
        for i in members:
            a_lo = box[i, 0, axis] + disp[i, axis]
            if a_lo < cursor + gap:
                disp[i, axis] += cursor + gap - a_lo
            cursor = box[i, 1, axis] + disp[i, axis]
        after = np.mean([ctr[i, axis] + disp[i, axis] for i in members])
        for i in members:
            disp[i, axis] -= after - before
    return disp



def kit_column(names, product="tactical", x=95.0, z=0.0, y0=0.0, gap=6.0):
    """Unsolved parts laid out as a labelled reference column beside the scene.

    A part with no pose still has to be *shown* somewhere. Laying each one flat
    (its thinnest axis up) and stacking them clear of the assembly keeps the
    file readable as a parts list without implying a placement that was never
    solved. Order is the caller's -- the pose record's `unsolved_*` list is the
    canonical one, so the column stays stable across rebuilds.
    """
    flat = np.array([[1, 0, 0, 0],
                     [0, 0, 1, 0],
                     [0, -1, 0, 0],
                     [0, 0, 0, 1]], float)      # source +Z -> +Y
    items, cursor = [], y0
    for n in names:
        m = fidget.load(n, product=product)
        m.apply_transform(flat)
        c = m.bounds.mean(axis=0)
        m.apply_translation([x - c[0], cursor - m.bounds[0][1], z - c[2]])
        items.append((n, m))
        cursor = m.bounds[1][1] + gap
    return items

# ----------------------------------------------------------------- output ---
def coloured(items, start=0):
    """[(name, mesh)] -> [(name, mesh, color)]."""
    return [(n, m, color_for(start + k)) for k, (n, m) in enumerate(items)]


def scene(items, disp=None):
    s = trimesh.Scene()
    for k, it in enumerate(items):
        name, m = it[0], it[1]
        col = it[2] if len(it) > 2 else color_for(k)
        g = m.copy()
        if disp is not None:
            g.apply_translation(disp[k])
        g.visual.face_colors = np.tile(
            np.array(list(col) + [255], np.uint8), (len(g.faces), 1))
        s.add_geometry(g, node_name=name, geom_name=name)
    return s


def slug(s):
    return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')


def write(items, disp, stem, subdir, tags=("assembled", "exploded"),
          formats=("3mf", "glb", "stl")):
    out = []
    for tag in tags:
        d = None if tag == "assembled" else disp
        sc = scene(items, d)
        for ext in ("3mf", "glb"):
            if ext in formats:
                out.append(fidget.save(sc, "%s_%s.%s" % (stem, tag, ext), subdir=subdir))
        if "stl" in formats:
            merged = trimesh.util.concatenate([g for g in sc.geometry.values()])
            out.append(fidget.save(merged, "%s_%s.stl" % (stem, tag), subdir=subdir))
    return out


def build(items, stem, subdir, check=True, **kw):
    """Colour, explode, report interference, and write all six files."""
    if len(items[0]) == 2:
        items = coloured(items)
    bad = interference(items) if check else []
    bb = np.array([it[1].bounds for it in items])
    print("%-44s %2d parts  %s mm  interference %d pairs (max %.1f mm3)" % (
        stem, len(items), np.round(bb[:, 1].max(0) - bb[:, 0].min(0), 1),
        len(bad), bad[0][0] if bad else 0.0), flush=True)
    for v, a, b in bad[:4]:
        print("      %8.1f mm3  %s / %s" % (v, a, b))
    d = explode(items, **kw)
    return write(items, d, stem, subdir), bad
