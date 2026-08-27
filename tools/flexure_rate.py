"""Measure the spring rate of a printed planar flexure.

Both of this toy's detent springs are *planar serpentines*: a 2D profile
extruded a few millimetres, bending in its own plane.  A cantilever formula
gets their rate badly wrong, because the load path folds back on itself several
times -- a section normal to the leaf's length cuts three separate strands.
This solves the profile directly instead: the shape is rasterised onto a
regular grid of plane-stress Q4 elements and one linear system is solved, so
"make it stiffer" becomes a number instead of a hope.

    python tools/flexure_rate.py

Absolute values carry the usual uncertainty in a printed part's modulus (layer
adhesion, infill, print orientation).  Ratios between two profiles solved the
same way are far more trustworthy, and ratios are what sizing decisions need.
"""
from __future__ import annotations

import os
import sys
from typing import NamedTuple

import numpy as np
import shapely
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import spsolve

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from package_paths import ASSEMBLED_DIR as PACKAGE_ASSEMBLED_DIR, ROOT_DIR
ASSEMBLED = PACKAGE_ASSEMBLED_DIR

E_PETG = 1700.0     # MPa, printed, in the layer plane
NU = 0.38

# Printed PETG cracks somewhere above ~4% strain; stay well under it, because
# a detent spring sees its peak deflection on every single click.
STRAIN_BUDGET = 0.025


class Result(NamedTuple):
    k: float                # N/mm at the nose, in the load direction
    cells: int
    elements: int
    strain_per_mm: float    # peak principal strain per mm of nose travel

    def strain_at(self, deflection):
        return self.strain_per_mm * deflection

    def force_at(self, deflection):
        return self.k * deflection


def _ke(E, nu):
    """Plane-stress stiffness of a unit-thickness square Q4 element.

    Scale-invariant in 2D, so element size never enters and only thickness
    multiplies it.  Node order runs anticlockwise from the lower-left corner.
    """
    k = np.array([0.5 - nu / 6, 0.125 + nu / 8, -0.25 - nu / 12,
                  -0.125 + 3 * nu / 8, -0.25 + nu / 12, -0.125 - nu / 8,
                  nu / 6, 0.125 - 3 * nu / 8])
    i = np.array([[0, 1, 2, 3, 4, 5, 6, 7],
                  [1, 0, 7, 6, 5, 4, 3, 2],
                  [2, 7, 0, 5, 6, 3, 4, 1],
                  [3, 6, 5, 0, 7, 2, 1, 4],
                  [4, 5, 6, 7, 0, 1, 2, 3],
                  [5, 4, 3, 2, 1, 0, 7, 6],
                  [6, 3, 4, 1, 2, 7, 0, 5],
                  [7, 2, 1, 4, 3, 6, 5, 0]])
    return E / (1 - nu ** 2) * k[i]


def section_profile(mesh, origin, normal, axes):
    """The 2D profile of a prismatic part, expressed in two toy axes.

    ``axes`` is the pair of toy axis indices the profile lives in -- (1, 2) for
    a part extruded along toy x.  The returned polygon's coordinates *are* toy
    coordinates, so masks can be written in toy terms rather than in whatever
    frame ``to_2D`` happened to pick.
    """
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        raise ValueError("empty section")
    p2, to_3d = sec.to_2D()
    polys = list(p2.polygons_full)
    if not polys:
        raise ValueError("section encloses no area")
    poly = max(polys, key=lambda p: p.area)
    M = np.asarray(to_3d)

    def lift(coords):
        c = np.asarray(coords, dtype=float)
        h = np.column_stack([c, np.zeros(len(c)), np.ones(len(c))])
        return (h @ M.T)[:, list(axes)]

    return shapely.Polygon(lift(poly.exterior.coords),
                           [lift(r.coords) for r in poly.interiors])


def rate(poly, thickness, fixed, loaded, direction, h=0.10, E=E_PETG, nu=NU):
    """Tip rate in N/mm of a planar flexure profile.

    ``fixed`` and ``loaded`` take an (n, 2) array of node coordinates and
    return a boolean mask.  ``direction`` is the 2D direction of the load.

    This wants a part with a real anchor.  The rod follower has one -- its back
    bears on the barrel -- so its rate is trustworthy.  A part that reacts its
    own load through its own body, like the waist ring floating on its three
    arms, does not, and is not modelled here.
    """
    x0, y0, x1, y1 = poly.bounds
    nx, ny = int(np.ceil((x1 - x0) / h)), int(np.ceil((y1 - y0) / h))
    cx = x0 + (np.arange(nx) + 0.5) * h
    cy = y0 + (np.arange(ny) + 0.5) * h
    gx, gy = np.meshgrid(cx, cy, indexing="ij")
    solid = shapely.contains_xy(poly, gx.ravel(), gy.ravel()).reshape(nx, ny)
    if solid.sum() < 20:
        raise ValueError("profile too thin for a %.3f mm grid" % h)

    nnx, nny = nx + 1, ny + 1
    n_nodes = nnx * nny
    ex, ey = np.nonzero(solid)
    nid = lambda i, j: i * nny + j
    conn = np.stack([nid(ex, ey), nid(ex + 1, ey),
                     nid(ex + 1, ey + 1), nid(ex, ey + 1)], axis=1)

    NX, NY = np.meshgrid(np.arange(nnx), np.arange(nny), indexing="ij")
    NODES = np.column_stack([x0 + NX.ravel() * h, y0 + NY.ravel() * h])

    used = np.zeros(n_nodes, dtype=bool)
    used[conn.ravel()] = True
    fmask = fixed(NODES) & used
    lmask = loaded(NODES) & used
    if not fmask.any():
        raise ValueError("no anchor nodes")
    if not lmask.any():
        raise ValueError("no loaded nodes")

    # Rasterising can shed islands; keep only what is connected to the anchor,
    # or the system is singular.
    rows = np.repeat(np.arange(len(conn)), 4)
    inc = coo_matrix((np.ones(conn.size), (rows, conn.ravel())),
                     shape=(len(conn), n_nodes)).tocsr()
    _, lab = connected_components((inc.T @ inc) > 0, directed=False)
    keep = lab == np.bincount(lab[fmask]).argmax()
    conn = conn[keep[conn[:, 0]]]
    used[:] = False
    used[conn.ravel()] = True
    fmask &= used
    lmask &= used
    if not lmask.any():
        raise ValueError("the nose is not connected to the anchor")

    KE = _ke(E, nu) * thickness
    edof = np.empty((len(conn), 8), dtype=int)
    edof[:, 0::2] = conn * 2
    edof[:, 1::2] = conn * 2 + 1
    K = coo_matrix((np.tile(KE.ravel(), len(conn)),
                    (np.repeat(edof, 8, axis=1).ravel(),
                     np.tile(edof, (1, 8)).ravel())),
                   shape=(2 * n_nodes, 2 * n_nodes)).tocsr()

    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    li = np.flatnonzero(lmask)
    f = np.zeros(2 * n_nodes)
    f[2 * li] = d[0] / len(li)          # one newton, spread over the nose
    f[2 * li + 1] = d[1] / len(li)

    free = np.zeros(2 * n_nodes, dtype=bool)
    ui = np.flatnonzero(used)
    free[2 * ui] = True
    free[2 * ui + 1] = True
    fi = np.flatnonzero(fmask)
    free[2 * fi] = False
    free[2 * fi + 1] = False

    u = np.zeros(2 * n_nodes)
    u[free] = spsolve(K[free][:, free].tocsc(), f[free])
    delta = float(np.array([u[2 * li].mean(), u[2 * li + 1].mean()]) @ d)

    # Peak strain per millimetre of tip travel.  A printed flexure fails by
    # cracking long before anything else goes wrong, so the rate is only half
    # the answer -- how hard the material is working is the other half.
    ux = u[2 * conn]
    uy = u[2 * conn + 1]
    dNdx = np.array([-1.0, 1.0, 1.0, -1.0]) / (2.0 * h)
    dNdy = np.array([-1.0, -1.0, 1.0, 1.0]) / (2.0 * h)
    ex_ = ux @ dNdx
    ey_ = uy @ dNdy
    gxy = ux @ dNdy + uy @ dNdx
    principal = 0.5 * (ex_ + ey_) + np.sqrt((0.5 * (ex_ - ey_)) ** 2 + (0.5 * gxy) ** 2)
    strain_per_mm = float(np.abs(principal).max() / abs(delta))
    return Result(k=1.0 / delta, cells=int(solid.sum()), elements=int(len(conn)),
                  strain_per_mm=strain_per_mm)


STOCK_FOLLOWER = os.path.join(
    ROOT_DIR, "Fidget Fuse Tactical 7-in-1 Snap-Fit Fidget Toy",
    "12 - Internal Barrel Spring v1.1.stl")


def strand_thickness(poly, h=0.05):
    """Local material thickness across a profile, as percentiles in mm.

    Rasterises the interior and takes twice the distance to the nearest edge at
    every solid cell.  The low percentiles are the slender strands that carry
    the bending -- and that a slicer has to be able to render in whole
    extrusions -- which is the number that decides printability.  The maximum
    is just the bulkiest lump and says nothing useful.
    """
    from scipy import ndimage

    x0, y0, x1, y1 = poly.bounds
    nx, ny = int(np.ceil((x1 - x0) / h)), int(np.ceil((y1 - y0) / h))
    gx, gy = np.meshgrid(x0 + (np.arange(nx) + 0.5) * h,
                         y0 + (np.arange(ny) + 0.5) * h, indexing="ij")
    solid = shapely.contains_xy(poly, gx.ravel(), gy.ravel()).reshape(nx, ny)
    dist = ndimage.distance_transform_edt(np.pad(solid, 1)) [1:-1, 1:-1] * h
    t = 2.0 * dist[solid]
    return {p: float(np.percentile(t, p)) for p in (1, 5, 25, 50)}


def _load(name):
    path = name if os.path.isabs(name) else os.path.join(ASSEMBLED, name)
    m = trimesh.load(path, process=True)
    m.merge_vertices()
    trimesh.repair.fill_holes(m)
    return m


def follower_profile(mesh=None):
    """The rod follower's profile, in the toy (y, z) plane."""
    m = mesh if mesh is not None else _load(STOCK_FOLLOWER)
    return section_profile(m, [0.625, 0, 0], [1, 0, 0], axes=(1, 2))


def follower_rate(poly, thickness=3.75, h=0.08):
    """Radial rate of a follower: nose on the rack, back reacted on the barrel."""
    zs = np.array(poly.exterior.coords)[:, 1]
    return rate(poly, thickness,
                fixed=lambda V: V[:, 1] > zs.max() - 0.35,
                loaded=lambda V: V[:, 1] < zs.min() + 0.35,
                direction=(0.0, 1.0), h=h)


def report():
    print("=" * 78)
    print("PLANAR FLEXURE RATE   E = %.0f MPa (PETG), nu = %.2f" % (E_PETG, NU))
    print("=" * 78)

    poly = follower_profile()
    zs = np.array(poly.exterior.coords)[:, 1]
    res = follower_rate(poly)
    k, cells, elems = res.k, res.cells, res.elements
    print()
    print("  12 - Internal Barrel Spring v1.1 -- the stock rod follower")
    print("    profile area %.2f mm2, extruded %.2f mm" % (poly.area, 3.75))
    print("    toy z %.3f (nose, on the rack) .. %.3f (back, on the barrel)"
          % (zs.min(), zs.max()))
    print("    %d solid cells, %d connected elements" % (cells, elems))
    print("    RADIAL RATE  k = %.3f N/mm" % k)
    print("    at its 0.868 mm crest deflection: %.2f N each, %.2f N over three"
          % (k * 0.868, 3 * k * 0.868))
    print("    peak strain there: %.2f%%  (budget %.1f%%)"
          % (100 * res.strain_at(0.868), 100 * STRAIN_BUDGET))
    print()
    print("  Use score_detent.py for the force the thumb actually feels: this")
    print("  rate only becomes a force once the rack geometry says how far the")
    print("  nose is pushed and how steep the flank under it is.")


if __name__ == "__main__":
    report()
