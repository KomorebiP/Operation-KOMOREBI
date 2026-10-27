"""Primitive-period consensus projection."""
from __future__ import annotations
from collections import Counter
from typing import Any, Mapping
import numpy as np
from komorebi_lasm_compiler.common import freeze, equal
def bgof(a):
    return Counter(map(int, a.ravel())).most_common(1)[0][0]

def majority_stack(blocks):
    n, p, q = blocks.shape
    out = np.empty((p, q), dtype=np.int16)
    for r in range(p):
        for c in range(q):
            cc = Counter(map(int, blocks[:, r, c]))
            mx = max(cc.values())
            out[r, c] = min((k for k, v in cc.items() if v == mx))
    return out

def execute(g, max_period=12, min_repeats=2, require_primitive=True):
    a = np.asarray(g, dtype=np.int16)
    h, w = a.shape
    bg = bgof(a)
    best = []
    bestkey = None
    maxp = min(max_period, h // min_repeats)
    maxq = min(max_period, w // min_repeats)
    for p in range(2, maxp + 1):
        for q in range(2, maxq + 1):
            for nr in range(min_repeats, h // p + 1):
                hh = nr * p
                for nc in range(min_repeats, w // q + 1):
                    ww = nc * q
                    for ay, y0 in (('top', 0), ('bottom', h - hh)):
                        for ax, x0 in (('left', 0), ('right', w - ww)):
                            region = a[y0:y0 + hh, x0:x0 + ww]
                            blocks = region.reshape(nr, p, nc, q).transpose(0, 2, 1, 3).reshape(nr * nc, p, q)
                            templ = majority_stack(blocks)
                            if require_primitive:
                                nonprimitive = False
                                for pp in range(1, p):
                                    if p % pp == 0 and np.array_equal(templ, np.tile(templ[:pp, :], (p // pp, 1))):
                                        nonprimitive = True
                                        break
                                if nonprimitive:
                                    continue
                                for qq in range(1, q):
                                    if q % qq == 0 and np.array_equal(templ, np.tile(templ[:, :qq], (1, q // qq))):
                                        nonprimitive = True
                                        break
                                if nonprimitive:
                                    continue
                            rec = np.full_like(a, bg)
                            rec[y0:y0 + hh, x0:x0 + ww] = np.tile(templ, (nr, nc))
                            mismatch = int(np.count_nonzero(rec != a))
                            key = (mismatch, p * q, -hh * ww, p, q, -nr * nc, ay, ax)
                            if bestkey is None or key < bestkey:
                                bestkey = key
                                best = [(rec, {'p': p, 'q': q, 'nr': nr, 'nc': nc, 'anchor_y': ay, 'anchor_x': ax, 'mismatch': mismatch, 'template_area': p * q, 'modeled_area': hh * ww})]
                            elif key == bestkey:
                                best.append((rec, {'p': p, 'q': q, 'nr': nr, 'nc': nc, 'anchor_y': ay, 'anchor_x': ax, 'mismatch': mismatch, 'template_area': p * q, 'modeled_area': hh * ww}))
    if not best:
        raise ValueError('no periodic model')
    uniq = {freeze(r): meta for r, meta in best}
    if len(uniq) != 1:
        raise ValueError('ambiguous periodic optimum')
    out, meta = next(iter(uniq.items()))
    return (out, meta)

def compile_task(t):
    if not t.get('train') or not t.get('test'):
        return None
    metas = []
    for e in t['train']:
        if np.asarray(e['input']).shape != np.asarray(e['output']).shape:
            return None
        if np.array_equal(e['input'], e['output']):
            return None
        try:
            o, m = execute(e['input'])
        except Exception:
            return None
        if o != freeze(e['output']):
            return None
        metas.append(m)
    try:
        outs = tuple((execute(e['input'])[0] for e in t['test']))
    except Exception:
        return None
    return {'family': 'periodic_consensus_restore', 'metas': metas, 'outputs': outs}
