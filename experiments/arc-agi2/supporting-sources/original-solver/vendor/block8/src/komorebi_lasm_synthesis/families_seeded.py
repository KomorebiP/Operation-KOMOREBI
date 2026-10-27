"""Seeded component interior recoloring."""
from __future__ import annotations
from collections import Counter
from typing import Any, Mapping
import numpy as np
from komorebi_lasm_compiler.common import arr, freeze, infer_background, components, equal

def _binary_erosion3(mask: np.ndarray) -> np.ndarray:
    padded=np.pad(mask.astype(bool),1,constant_values=False)
    result=np.ones_like(mask,dtype=bool)
    for dy in range(3):
        for dx in range(3):
            result &= padded[dy:dy+mask.shape[0],dx:dx+mask.shape[1]]
    return result
def execute(g, p):
    a = arr(g)
    bg = infer_background(a)
    cnt = Counter((int(v) for v in a.ravel() if int(v) != bg))
    if not cnt:
        raise ValueError
    scaffold = max(cnt, key=lambda c: (cnt[c], -c))
    support = a != bg
    out = a.copy()
    valid = 0
    for comp in components(support, 4):
        cm = np.zeros(a.shape, bool)
        for y, x in comp:
            cm[y, x] = 1
        markers = sorted(set((int(a[y, x]) for y, x in comp if int(a[y, x]) != scaffold)))
        if not markers:
            continue
        if len(markers) != 1:
            raise ValueError
        c = markers[0]
        interior = _binary_erosion3(cm)
        if not np.any(interior):
            raise ValueError
        out[interior] = c
        valid += 1
    if not valid:
        raise ValueError
    return out

def compile(t):
    try:
        if all((equal(execute(e['input'], {}), e['output']) for e in t['train'])):
            return [('seeded_component_interior_recolor', {})]
    except:
        pass
    return []
