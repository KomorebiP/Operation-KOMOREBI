"""Pinned adapter to the existing Komorebi Math Haar packet implementation.

The vendored wheel is used unchanged. Its numeric implementation is NOT
relabelled exact arithmetic. Unnormalized impulse responses are checked against
an independent integer recurrence, then exported to the exact prime-field layer.
"""
from __future__ import annotations
import hashlib
import importlib
import itertools
from pathlib import Path
import sys
from typing import Sequence
from zipfile import ZipFile
from packet_information import Matrix

ROOT=Path(__file__).resolve().parents[1]
WHEEL=ROOT/'vendor'/'komorebi_math-1.0.0b4-4b21-py3-none-any.whl'
EXPECTED={
 'komorebi_math/signals/wavelets.py':'a61d4097dfb53f04ff3810d34194b01290e48cb8eaa6974a1b37a13e29d99063',
 'komorebi_math/signals/filterbanks.py':'41c241aeaf678fd22558cf0adbe44d3be317d66f7722deb9a0a1688491b5b1f1',
}
GITHUB_WAVELETS_BLOB='db646e04f6d3d67ecf22a4eee7376647e7ae598f'
EXPECTED_WHEEL_SHA256='a7b41efe91524ad1e6e641b0567b571a04247c0b17994c1d019e7d6ac2c4e52d'


def source_receipt() -> dict:
    wheel_digest=hashlib.sha256(WHEEL.read_bytes()).hexdigest()
    if wheel_digest != EXPECTED_WHEEL_SHA256:
        raise ValueError('pinned wheel hash mismatch')
    records={}
    with ZipFile(WHEEL) as z:
        for name,expected in EXPECTED.items():
            b=z.read(name)
            sha=hashlib.sha256(b).hexdigest()
            if sha!=expected:
                raise ValueError(f'pinned upstream source hash mismatch: {name}')
            records[name]={'sha256':sha,'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),
                           'bytes':len(b)}
    if records['komorebi_math/signals/wavelets.py']['git_blob_sha1'] != GITHUB_WAVELETS_BLOB:
        raise ValueError('wavelets source differs from the retrieved GitHub blob')
    return {'wheel':WHEEL.name,'wheel_sha256':wheel_digest,
            'files':records,'github_wavelets_blob':GITHUB_WAVELETS_BLOB,
            'github_repository':'KomorebiP/komorebi-math','scope':'Pinned wheel; wavelets blob matches the GitHub file read in this continuation. Not a full latest-repository audit.'}


def backend():
    source_receipt()
    if str(WHEEL) not in sys.path:
        sys.path.insert(0,str(WHEEL))
    module=importlib.import_module('komorebi_math.signals.wavelets')
    # Do not silently use a previously imported, different library instance.
    if str(WHEEL) not in str(module.__file__):
        raise RuntimeError('a non-pinned Komorebi Math module is already imported; use a fresh interpreter')
    return module


def complete_prunings(depth: int, path: str='') -> tuple[tuple[str,...],...]:
    if type(depth) is not int or depth<0 or depth>5:
        raise ValueError('pruning enumeration supports integer depth 0..5')
    if depth==0:
        return ((path,),)
    left=complete_prunings(depth-1,path+'0')
    right=complete_prunings(depth-1,path+'1')
    return ((path,),)+tuple(a+b for a in left for b in right)


def integer_nodes(signal: Sequence[int],depth: int) -> dict[str,tuple[int,...]]:
    """Independent unnormalized split recurrence, with Python integer arithmetic."""
    if type(depth) is not int or depth<0 or depth>12:
        raise ValueError('depth must be an integer in 0..12')
    x=tuple(signal)
    if not x or len(x)%(2**depth) or any(type(v) is not int for v in x):
        raise ValueError('finite integer signal is incompatible with packet depth')
    nodes={'':x}
    for level in range(depth):
        for path in tuple(p for p in nodes if len(p)==level):
            y=nodes[path]
            nodes[path+'0']=tuple(y[i]+y[i+1] for i in range(0,len(y),2))
            nodes[path+'1']=tuple(y[i]-y[i+1] for i in range(0,len(y),2))
    return nodes


def export_haar(length: int,depth: int,*,leaves: Sequence[str] | None=None,p: int=5) -> tuple[Matrix,dict]:
    """Export a complete pruning, not a hidden-full-tree 'erasure' simulation.

    Coefficients are ordered by sorted leaf path, then within-leaf position.
    Large dimensions are guarded because this is an exact audit adapter.
    """
    if type(length) is not int or length<1 or length>256:
        raise ValueError('length must be an integer in 1..256')
    module=backend()
    import numpy as np
    template=module.haar_packet_analyze(np.zeros(length),depth,normalized=False)
    selected=template.full_leaves if leaves is None else template.validate_pruning(tuple(leaves))
    columns=[]
    for j in range(length):
        v=tuple(int(i==j) for i in range(length))
        tree=module.haar_packet_analyze(np.array(v,dtype=float),depth,normalized=False)
        native=tuple(float(t) for path in selected for t in tree.coefficient(path))
        oracle=integer_nodes(v,depth)
        expected=tuple(t for path in selected for t in oracle[path])
        if len(native)!=length or any(a!=b for a,b in zip(native,expected)):
            raise ArithmeticError('library impulse response differs from exact integer recurrence')
        columns.append(expected)
    rows=tuple(tuple(columns[j][i] for j in range(length)) for i in range(length))
    analysis=Matrix(p,length,rows)
    inverse=analysis.inverse()  # Reject a bad prime, not an approximate inverse.
    if inverse @ analysis != Matrix.identity(p,length):
        raise ArithmeticError('exported modular inverse is invalid')
    slots=[]
    for path in selected:
        slots.extend((path,k) for k in range(length//(2**len(path))))
    return analysis,{'length':length,'depth':depth,'leaves':selected,'coordinates':slots,
                     'integer_analysis_rows':rows,'coefficient_field':f'GF({p})',
                     'library_numeric_mode':'normalized=False, binary floating execution',
                     'exact_mode':'independent integer impulse recurrence, then exact modular arithmetic',
                     'native_library_finite_field_support_claimed':False}


def native_integer_packets(signal: Sequence[int],depth: int,*,p: int=5,
                           leaves: Sequence[str] | None=None) -> tuple[int,...]:
    """Run the real library, certify integer outputs, then reduce modulo p.

    This is a bounded exact-data adapter, not a change to upstream arithmetic.
    The magnitude guard prevents silently treating a rounded float as an exact
    integer. The independent recurrence checks the coefficients before reduction.
    """
    x=tuple(signal)
    oracle=integer_nodes(x,depth)
    Matrix(p,0,())  # Validate the declared prime, even for a constant task.
    if len(x)>256 or max(abs(v) for v in x)*(2**depth)>2**52:
        raise ValueError('native integer packet magnitude/length guard exceeded')
    import numpy as np
    lib=backend()
    tree=lib.haar_packet_analyze(np.asarray(x,dtype=float),depth,normalized=False)
    selected=tree.full_leaves if leaves is None else tree.validate_pruning(tuple(leaves))
    values=tuple(float(v) for path in selected for v in tree.coefficient(path))
    exact=tuple(v for path in selected for v in oracle[path])
    if len(values)!=len(exact) or any(not a.is_integer() or a!=b for a,b in zip(values,exact)):
        raise ArithmeticError('native packet values are not certified exact integers')
    return tuple(v%p for v in exact)
