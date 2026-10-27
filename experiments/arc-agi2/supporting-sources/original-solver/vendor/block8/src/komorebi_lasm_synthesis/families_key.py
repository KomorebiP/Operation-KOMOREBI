"""D4 key-to-block color transfer."""
from __future__ import annotations
from collections import Counter
from typing import Any, Mapping
import numpy as np
from komorebi_lasm_compiler.common import arr, freeze, infer_background, bbox, equal
def transforms(a):
    return [('id', a), ('r90', np.rot90(a, 1)), ('r180', np.rot90(a, 2)), ('r270', np.rot90(a, 3)), ('fliplr', np.fliplr(a)), ('flipud', np.flipud(a)), ('transpose', a.T), ('anti_transpose', np.rot90(a, 2).T)]

def parse_scene(g):
    a = arr(g)
    bg = infer_background(a)
    cnt = Counter((int(v) for v in a.ravel() if int(v) != bg))
    if len(cnt) < 2:
        raise ValueError
    scaffold = max(cnt, key=lambda c: (cnt[c], -c))
    sm = a == scaffold
    box = bbox(sm)
    if box is None:
        raise ValueError
    y0, y1, x0, x1 = box
    hh, ww = (y1 - y0, x1 - x0)
    keymask = (a != bg) & (a != scaffold)
    kb = bbox(keymask)
    if kb is None:
        raise ValueError
    ky0, ky1, kx0, kx1 = kb
    key = a[ky0:ky1, kx0:kx1].copy()
    if not (ky1 <= y0 or y1 <= ky0 or kx1 <= x0 or (x1 <= kx0)):
        raise ValueError
    nkey = int(np.count_nonzero(key != bg))
    choices = []
    for s in range(2, min(hh, ww) + 1):
        if hh % s or ww % s:
            continue
        gh, gw = (hh // s, ww // s)
        occ = np.zeros((gh, gw), bool)
        valid = True
        for r in range(gh):
            for c in range(gw):
                block = a[y0 + r * s:y0 + (r + 1) * s, x0 + c * s:x0 + (c + 1) * s]
                if np.all(block == scaffold):
                    occ[r, c] = 1
                elif np.all(block == bg):
                    pass
                else:
                    valid = False
                    break
            if not valid:
                break
        if valid and int(occ.sum()) == nkey:
            choices.append((s, occ))
    if not choices:
        raise ValueError
    s, occ = max(choices, key=lambda z: z[0])
    return (a, bg, scaffold, (y0, y1, x0, x1), s, key, occ)

def execute(g, p):
    a, bg, scaffold, (y0, y1, x0, x1), s, key, occ = parse_scene(g)
    d = dict(transforms(key))
    name = p['transform']
    if name not in d:
        raise ValueError
    t = d[name]
    if t.shape != occ.shape or not np.array_equal(t != bg, occ):
        raise ValueError
    out = a.copy()
    for r in range(occ.shape[0]):
        for c in range(occ.shape[1]):
            if occ[r, c]:
                out[y0 + r * s:y0 + (r + 1) * s, x0 + c * s:x0 + (c + 1) * s] = int(t[r, c])
    return out

def compile(t):
    out = []
    for name in ['id', 'r90', 'r180', 'r270', 'fliplr', 'flipud', 'transpose', 'anti_transpose']:
        p = {'transform': name}
        try:
            if all((equal(execute(e['input'], p), e['output']) for e in t['train'])):
                out.append(('d4_key_block_transfer', p))
        except:
            pass
    return out
