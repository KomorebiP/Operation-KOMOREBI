"""Additional semantic macro families."""
from __future__ import annotations
import itertools
from collections import Counter, defaultdict
from typing import Any, Mapping
import numpy as np
from komorebi_lasm_compiler.common import arr, freeze, infer_background, components, bbox, equal
def d4(a):
    return [('id', a), ('r90', np.rot90(a, 1)), ('r180', np.rot90(a, 2)), ('r270', np.rot90(a, 3)), ('flip', np.fliplr(a)), ('flip90', np.rot90(np.fliplr(a), 1)), ('flip180', np.rot90(np.fliplr(a), 2)), ('flip270', np.rot90(np.fliplr(a), 3))]

def exec_blank_frame(g, p):
    a = arr(g)
    bg = infer_background(a)
    if np.any(a != bg):
        raise ValueError
    out = a.copy()
    c = int(p['color'])
    out[0, :] = c
    out[-1, :] = c
    out[:, 0] = c
    out[:, -1] = c
    return out

def compile_blank_frame(t):
    colors = []
    for e in t['train']:
        a = arr(e['input'])
        y = arr(e['output'])
        bg = infer_background(a)
        if np.any(a != bg) or a.shape != y.shape:
            return []
        added = set(map(int, y.ravel())) - {bg}
        if len(added) != 1:
            return []
        c = next(iter(added))
        colors.append(c)
    if len(set(colors)) != 1:
        return []
    p = {'color': colors[0]}
    return [('blank_to_constant_frame', p)] if all((equal(exec_blank_frame(e['input'], p), e['output']) for e in t['train'])) else []

def exec_singleton_frame(g, p):
    a = arr(g)
    bg = infer_background(a)
    ys, xs = np.nonzero(a != bg)
    if len(ys) != 1:
        raise ValueError
    c = int(a[ys[0], xs[0]])
    out = np.full_like(a, bg)
    out[0, :] = c
    out[-1, :] = c
    out[:, 0] = c
    out[:, -1] = c
    return out

def compile_singleton_frame(t):
    try:
        if all((equal(exec_singleton_frame(e['input'], {}), e['output']) for e in t['train'])):
            return [('singleton_to_frame', {})]
    except Exception:
        pass
    return []

def line_info(a, bg):
    nonbg = a != bg
    h, w = a.shape
    rows = [r for r in range(h) if np.all(nonbg[r, :])]
    cols = [c for c in range(w) if np.all(nonbg[:, c])]
    outs = []
    for r in rows:
        for c in cols:
            if np.count_nonzero(nonbg) != h + w - 1:
                continue
            hc = [int(a[r, x]) for x in range(w) if x != c]
            vc = [int(a[y, c]) for y in range(h) if y != r]
            if len(set(hc)) != 1 or len(set(vc)) != 1 or hc[0] == vc[0]:
                continue
            outs.append((r, c, hc[0], vc[0]))
    return outs

def exec_cross_halo(g, p):
    a = arr(g)
    bg = infer_background(a)
    li = line_info(a, bg)
    if len(li) != 1:
        raise ValueError
    r, c, hc, vc = li[0]
    color = int(p['color'])
    out = a.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == dx == 0:
                continue
            y, x = (r + dy, c + dx)
            if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]:
                out[y, x] = color
    return out

def compile_cross_halo(t):
    cols = []
    for e in t['train']:
        a = arr(e['input'])
        y = arr(e['output'])
        bg = infer_background(a)
        if a.shape != y.shape or len(line_info(a, bg)) != 1:
            return []
        added = set(map(int, y.ravel())) - set(map(int, a.ravel()))
        if len(added) != 1:
            return []
        cols.append(next(iter(added)))
    if len(set(cols)) != 1:
        return []
    p = {'color': cols[0]}
    return [('cross_intersection_halo', p)] if all((equal(exec_cross_halo(e['input'], p), e['output']) for e in t['train'])) else []

def color_components8(a, bg):
    out = []
    for color in sorted(set(map(int, a.ravel())) - {bg}):
        for comp in components(a == color, 8):
            out.append((color, comp))
    return out

def execute_shear(g, p):
    a = arr(g)
    bg = infer_background(a)
    out = np.full_like(a, bg)
    axis = p['axis']
    anchor = p['anchor']
    direction = p.get('direction', 'toward_anchor')
    for color, comp in color_components8(a, bg):
        if axis == 'rows':
            groups = defaultdict(list)
            for y, x in comp:
                groups[y].append(x)
            keys = sorted(groups)
            ak = keys[0] if anchor == 'low' else keys[-1]
            alo, ahi = (min(groups[ak]), max(groups[ak]))
            acenter = (alo + ahi) / 2
            for k in keys:
                xs = sorted(groups[k])
                lo, hi = (min(xs), max(xs))
                if k == ak:
                    nlo, nhi = (lo, hi)
                else:
                    slo = 1 if alo > lo else -1 if alo < lo else 0
                    shi = 1 if ahi > hi else -1 if ahi < hi else 0
                    if direction == 'away':
                        slo, shi = (-slo, -shi)
                    nlo, nhi = (lo + slo, hi + shi)
                for x in xs:
                    nx = int(round(nlo if hi == lo else nlo + (x - lo) * (nhi - nlo) / (hi - lo)))
                    if not 0 <= nx < a.shape[1]:
                        raise ValueError
                    if out[k, nx] != bg:
                        raise ValueError
                    out[k, nx] = color
        else:
            groups = defaultdict(list)
            for y, x in comp:
                groups[x].append(y)
            keys = sorted(groups)
            ak = keys[0] if anchor == 'low' else keys[-1]
            alo, ahi = (min(groups[ak]), max(groups[ak]))
            for k in keys:
                ys = sorted(groups[k])
                lo, hi = (min(ys), max(ys))
                if k == ak:
                    nlo, nhi = (lo, hi)
                else:
                    slo = 1 if alo > lo else -1 if alo < lo else 0
                    shi = 1 if ahi > hi else -1 if ahi < hi else 0
                    if direction == 'away':
                        slo, shi = (-slo, -shi)
                    nlo, nhi = (lo + slo, hi + shi)
                for y in ys:
                    ny = int(round(nlo if hi == lo else nlo + (y - lo) * (nhi - nlo) / (hi - lo)))
                    if not 0 <= ny < a.shape[0]:
                        raise ValueError
                    if out[ny, k] != bg:
                        raise ValueError
                    out[ny, k] = color
    return out

def compile_shear(t):
    out = []
    for axis in ('rows', 'cols'):
        for anchor in ('low', 'high'):
            for direction in ('toward_anchor', 'away'):
                p = {'axis': axis, 'anchor': anchor, 'direction': direction}
                try:
                    if all((arr(e['input']).shape == arr(e['output']).shape and equal(execute_shear(e['input'], p), e['output']) for e in t['train'])):
                        out.append(('rowwise_shear_relaxation', p))
                except Exception:
                    pass
    return out
