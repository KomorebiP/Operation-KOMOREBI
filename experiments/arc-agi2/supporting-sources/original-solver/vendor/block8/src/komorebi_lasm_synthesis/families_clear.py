"""Generated finite macro families from the validated Block 8 exploration."""
from __future__ import annotations
import itertools
from collections import Counter, defaultdict
from typing import Any, Mapping
import numpy as np
from komorebi_lasm_compiler.common import arr, freeze, infer_background, components, bbox, equal
def comp_masks(a, bg, conn=8, separate=True):
    out = []
    colors = sorted(set(map(int, a.ravel())) - {bg}) if separate else [None]
    for color in colors:
        mask = a == color if color is not None else a != bg
        for c in components(mask, conn):
            m = np.zeros(a.shape, bool)
            for y, x in c:
                m[y, x] = 1
            out.append((color, c, m))
    return out

def singleton_markers(a):
    bg = infer_background(a)
    out = []
    for color, c, m in comp_masks(a, bg, 8, True):
        if len(c) == 1:
            out.append((c[0][0], c[0][1], int(color)))
    return out

def exec_voronoi_frame(g, p):
    a = arr(g)
    bg = infer_background(a)
    marks = singleton_markers(a)
    if len(marks) < 2 or len(marks) != np.count_nonzero(a != bg):
        raise ValueError
    axis = p['axis']
    tie = p['tie']
    full_boundary = p['full_boundary']
    out = np.full_like(a, bg)
    coords = []
    for y, x, c in marks:
        coords.append((y if axis == 'row' else x, c, y, x))
    if len(set((q[0] for q in coords))) != len(coords):
        raise ValueError
    coords.sort()
    n = a.shape[0] if axis == 'row' else a.shape[1]
    for i in range(n):
        ds = [abs(i - q[0]) for q in coords]
        m = min(ds)
        idxs = [j for j, d in enumerate(ds) if d == m]
        j = idxs[0] if tie == 'low' else idxs[-1]
        c = coords[j][1]
        marker_here = any((q[0] == i for q in coords))
        boundary = i in (0, n - 1) and full_boundary
        if axis == 'row':
            if marker_here or boundary:
                out[i, :] = c
            else:
                out[i, 0] = out[i, -1] = c
        elif marker_here or boundary:
            out[:, i] = c
        else:
            out[0, i] = out[-1, i] = c
    return out

def compile_voronoi(task):
    out = []
    for axis in ('row', 'col'):
        for tie in ('low', 'high'):
            for fb in (True, False):
                p = {'axis': axis, 'tie': tie, 'full_boundary': fb}
                try:
                    if all((equal(exec_voronoi_frame(e['input'], p), e['output']) for e in task['train'])):
                        out.append(('axis_voronoi_frame', p))
                except Exception:
                    pass
    return out

def find_pluses(a):
    bg = infer_background(a)
    h, w = a.shape
    used = set()
    vals = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            center = int(a[y, x])
            arms = [int(a[y - 1, x]), int(a[y + 1, x]), int(a[y, x - 1]), int(a[y, x + 1])]
            if center == bg or len(set(arms)) != 1 or arms[0] == bg or (arms[0] == center):
                continue
            cells = {(y, x), (y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)}
            if any(((yy, xx) in used for yy, xx in cells)):
                continue
            vals.append((y, x, center, arms[0], cells))
            used |= cells
    if used != set(map(tuple, np.argwhere(a != bg))):
        raise ValueError
    return vals

def exec_plus_stamp(g, p):
    a = arr(g)
    bg = infer_background(a)
    pluses = find_pluses(a)
    out = a.copy()
    R = p['radius']
    diag = p['diag']
    cross = p['cross']
    for y, x, cc, ac, cells in pluses:
        if cross:
            for d in range(1, R + 1):
                for dy, dx in ((-d, 0), (d, 0), (0, -d), (0, d)):
                    ny, nx = (y + dy, x + dx)
                    if 0 <= ny < a.shape[0] and 0 <= nx < a.shape[1]:
                        if out[ny, nx] not in (bg, ac):
                            raise ValueError
                        out[ny, nx] = ac
        if diag:
            for d in range(1, R + 1):
                for dy, dx in ((-d, -d), (-d, d), (d, -d), (d, d)):
                    ny, nx = (y + dy, x + dx)
                    if 0 <= ny < a.shape[0] and 0 <= nx < a.shape[1]:
                        if out[ny, nx] not in (bg, cc):
                            raise ValueError
                        out[ny, nx] = cc
    return out

def compile_plus(task):
    out = []
    for R in range(2, 6):
        for cross in (True, False):
            for diag in (True, False):
                if not (cross or diag):
                    continue
                p = {'radius': R, 'cross': cross, 'diag': diag}
                try:
                    if all((equal(exec_plus_stamp(e['input'], p), e['output']) for e in task['train'])):
                        out.append(('plus_stamp_closure', p))
                except Exception:
                    pass
    return out

def exec_manhattan(g, p):
    a = arr(g)
    bg = infer_background(a)
    marks = singleton_markers(a)
    if len(marks) < 2 or len(marks) != np.count_nonzero(a != bg):
        raise ValueError
    byc = {c: (y, x) for y, x, c in marks}
    if len(byc) != len(marks):
        raise ValueError
    pivot = p['pivot_color']
    fill = p['fill_color']
    routes = {int(k): v for k, v in p['routes']}
    if pivot not in byc or set(routes) != set(byc) - {pivot}:
        raise ValueError
    out = a.copy()
    py, px = byc[pivot]
    for c, order in routes.items():
        ty, tx = byc[c]
        path = []
        if order == 'hv':
            sx = 1 if tx >= px else -1
            for x in range(px + sx, tx + sx, sx):
                path.append((py, x))
            sy = 1 if ty >= py else -1
            for y in range(py + sy, ty + sy, sy):
                path.append((y, tx))
        else:
            sy = 1 if ty >= py else -1
            for y in range(py + sy, ty + sy, sy):
                path.append((y, px))
            sx = 1 if tx >= px else -1
            for x in range(px + sx, tx + sx, sx):
                path.append((ty, x))
        for y, x in path:
            if (y, x) == (ty, tx):
                continue
            if int(out[y, x]) not in (bg, fill):
                raise ValueError
            out[y, x] = fill
    return out

def compile_manhattan(task):
    first = arr(task['train'][0]['input'])
    marks = singleton_markers(first)
    colors = sorted((c for y, x, c in marks))
    if not 2 <= len(colors) <= 5:
        return []
    out = []
    target_colors = set(map(int, arr(task['train'][0]['output']).ravel()))
    input_colors = set(map(int, first.ravel()))
    fills = sorted(target_colors - input_colors)
    if not fills:
        fills = sorted(target_colors - {infer_background(first)})
    for pivot in colors:
        others = [c for c in colors if c != pivot]
        for orders in itertools.product(('hv', 'vh'), repeat=len(others)):
            for fill in fills:
                p = {'pivot_color': pivot, 'fill_color': fill, 'routes': tuple(zip(others, orders))}
                try:
                    if all((equal(exec_manhattan(e['input'], p), e['output']) for e in task['train'])):
                        out.append(('role_manhattan_connector', p))
                except Exception:
                    pass
    return out

def solid_rect_components(a):
    bg = infer_background(a)
    cs = comp_masks(a, bg, 4, True)
    out = []
    for color, c, m in cs:
        box = bbox(m)
        y0, y1, x0, x1 = box
        if int(m.sum()) != (y1 - y0) * (x1 - x0):
            raise ValueError
        out.append((int(color), (y0, y1, x0, x1)))
    if not out:
        raise ValueError
    return out

def exec_lattice(g, p):
    a = arr(g)
    bg = infer_background(a)
    rs = solid_rect_components(a)
    colors = {c for c, b in rs}
    if len(colors) != 1:
        raise ValueError
    dims = {(b[1] - b[0], b[3] - b[2]) for c, b in rs}
    if len(dims) != 1:
        raise ValueError
    ys = sorted(set(((b[0], b[1]) for c, b in rs)))
    xs = sorted(set(((b[2], b[3]) for c, b in rs)))
    if len(rs) != len(ys) * len(xs) or len(ys) < 2 or len(xs) < 2:
        raise ValueError
    if {(y0, y1, x0, x1) for y0, y1 in ys for x0, x1 in xs} != {b for c, b in rs}:
        raise ValueError
    bridge = p['bridge']
    terminal = p['terminal']
    out = a.copy()
    ymin = ys[0][0]
    ymax = ys[-1][1]
    xmin = xs[0][0]
    xmax = xs[-1][1]
    rowg = [(ys[i][1], ys[i + 1][0]) for i in range(len(ys) - 1) if ys[i][1] < ys[i + 1][0]]
    colg = [(xs[i][1], xs[i + 1][0]) for i in range(len(xs) - 1) if xs[i][1] < xs[i + 1][0]]
    if not rowg or not colg:
        raise ValueError
    for y0, y1 in rowg:
        out[y0:y1, xmin:xmax] = bridge
        out[y0:y1, :xmin] = terminal
        out[y0:y1, xmax:] = terminal
    for x0, x1 in colg:
        out[ymin:ymax, x0:x1] = bridge
        out[:ymin, x0:x1] = terminal
        out[ymax:, x0:x1] = terminal
    return out

def compile_lattice(task):
    first = arr(task['train'][0]['input'])
    outc = set(map(int, arr(task['train'][0]['output']).ravel())) - set(map(int, first.ravel()))
    if len(outc) < 1:
        return []
    vals = sorted(outc)
    out = []
    for bridge in vals:
        for terminal in vals:
            if bridge == terminal:
                continue
            p = {'bridge': bridge, 'terminal': terminal}
            try:
                if all((equal(exec_lattice(e['input'], p), e['output']) for e in task['train'])):
                    out.append(('rectangular_lattice_corridors', p))
            except Exception:
                pass
    return out
