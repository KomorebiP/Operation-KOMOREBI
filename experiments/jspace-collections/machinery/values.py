"""Values with explicit meanings and stable serialization. Komorebi P."""
from dataclasses import dataclass
import hashlib
import json
import numbers
import numpy as np

BASE_KINDS = {'scalar', 'index', 'color', 'flag', 'point', 'box', 'grid', 'mask', 'object'}
KINDS = BASE_KINDS | {'list['+kind+']' for kind in BASE_KINDS}
MAX_ITEMS = 64


class Fault(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def integer(x):
    return isinstance(x, numbers.Integral) and not isinstance(x, (bool, np.bool_))


def element_kind(kind):
    return kind[5:-1] if isinstance(kind,str) and kind in KINDS and kind.startswith('list[') else None


@dataclass(frozen=True)
class GridObject:
    source: str
    origin_id: str
    shape: tuple
    pixels: tuple

    @classmethod
    def from_dict(cls,obj):
        if not isinstance(obj,dict) or set(obj)!={'source','origin_id','shape','pixels'}:
            raise Fault('schema','Objects require source, origin_id, shape and pixels.')
        for field in ['source','origin_id']:
            if not isinstance(obj[field],str) or len(obj[field])!=64 or any(c not in '0123456789abcdef' for c in obj[field]):
                raise Fault('identity','Object provenance requires hexadecimal SHA-256 identifiers.')
        shape=obj['shape']
        if not isinstance(shape,(list,tuple)) or len(shape)!=2 or not all(integer(v) and 0<v<=128 for v in shape):
            raise Fault('shape','Invalid object coordinate frame.')
        pixels=obj['pixels']
        if not isinstance(pixels,(list,tuple)) or not 0<len(pixels)<=shape[0]*shape[1]:
            raise Fault('shape','An object needs at least one pixel.')
        rows=[]; seen=set()
        for pixel in pixels:
            if not isinstance(pixel,(list,tuple)) or len(pixel)!=3 or not all(integer(v) for v in pixel):
                raise Fault('type','Object pixels contain integer row, column and color.')
            r,c,color=map(int,pixel)
            if not (0<=r<shape[0] and 0<=c<shape[1] and 0<=color<=9):
                raise Fault('bounds','An object pixel lies outside its frame or color range.')
            if (r,c) in seen: raise Fault('shape','An object cannot contain duplicate coordinates.')
            seen.add((r,c));rows.append((r,c,color))
        return cls(obj['source'],obj['origin_id'],tuple(map(int,shape)),tuple(sorted(rows)))

    def pack(self):
        return {'source':self.source,'origin_id':self.origin_id,'shape':list(self.shape),'pixels':[list(p) for p in self.pixels]}


@dataclass(frozen=True, eq=False)
class Value:
    kind: str
    data: object

    def __post_init__(self):
        k, x = self.kind, self.data
        if not isinstance(k,str) or k not in KINDS:
            raise Fault('type', f'Unknown value kind: {k}')
        if element_kind(k):
            if not isinstance(x,(list,tuple)) or len(x)>MAX_ITEMS:
                raise Fault('budget',f'Collections permit at most {MAX_ITEMS} items.')
            items=tuple(v if isinstance(v,Value) else Value.unpack(v) for v in x)
            if any(v.kind!=element_kind(k) for v in items): raise Fault('type','Collection element types must match.')
            x=items
        elif k == 'object':
            x=GridObject.from_dict(x.pack() if isinstance(x,GridObject) else x)
        elif k == 'scalar':
            if isinstance(x, (bool, np.bool_)) or not isinstance(x, numbers.Real) or not np.isfinite(x):
                raise Fault('type', 'A scalar must be a finite real number.')
            x = float(x)
        elif k in ('index', 'color'):
            if not integer(x) or (k == 'color' and not 0 <= x <= 9):
                raise Fault('type', f'Invalid {k}.')
            x = int(x)
        elif k == 'flag':
            if not isinstance(x, (bool, np.bool_)):
                raise Fault('type', 'A flag must be Boolean.')
            x = bool(x)
        elif k in ('point', 'box'):
            size = 2 if k == 'point' else 4
            if not isinstance(x, (list, tuple)) or len(x) != size or not all(integer(v) for v in x):
                raise Fault('type', f'{k} requires {size} integer coordinates.')
            x = tuple(int(v) for v in x)
            if k == 'box' and not (0 <= x[0] < x[2] and 0 <= x[1] < x[3]):
                raise Fault('bounds', 'Box endpoints are exclusive and must enclose a positive region.')
        else:
            try:
                a = np.asarray(x)
            except (ValueError, TypeError) as exc:
                raise Fault('shape', 'Expected a rectangular two-dimensional value.') from exc
            if a.ndim != 2 or not all(0 < n <= 128 for n in a.shape):
                raise Fault('shape', 'Grids and masks require 1..128 rows and columns.')
            if k == 'grid':
                if a.dtype.kind not in 'iu' or np.any(a < 0) or np.any(a > 9):
                    raise Fault('type', 'Grid entries must be integer colors from 0 through 9.')
                x = a.astype(np.int64, copy=True)
            else:
                if a.dtype.kind != 'b':
                    raise Fault('type', 'Mask entries must be Boolean.')
                x = a.copy()
            x.setflags(write=False)
        object.__setattr__(self, 'data', x)

    def pack(self):
        if element_kind(self.kind): return {'kind':self.kind,'data':[v.pack() for v in self.data]}
        if self.kind=='object': return {'kind':self.kind,'data':self.data.pack()}
        data = self.data.tolist() if isinstance(self.data, np.ndarray) else self.data
        if isinstance(data, tuple): data = list(data)
        return {'kind': self.kind, 'data': data}

    @classmethod
    def unpack(cls, obj):
        if not isinstance(obj, dict) or set(obj) != {'kind', 'data'}:
            raise Fault('schema', 'Expected a typed value with kind and data.')
        return cls(obj['kind'], obj['data'])

    def identity(self): return digest(self.pack())


def equivalent(a,b,atol=1e-9):
    if a.kind!=b.kind:return False
    if a.kind=='scalar':return abs(a.data-b.data)<=atol
    if element_kind(a.kind):
        return len(a.data)==len(b.data) and all(equivalent(x,y,atol) for x,y in zip(a.data,b.data))
    return a.identity()==b.identity()


def change(before, after):
    """Exact observed differences, distinct from inferred dependencies."""
    if before is None: return {'status': 'new', 'after': after.pack()}
    if after is None: return {'status': 'not_executed', 'before': before.pack()}
    if before.identity() == after.identity(): return {'status': 'unchanged'}
    result = {'status': 'changed', 'before': before.pack(), 'after': after.pack()}
    if before.kind != after.kind: return result
    if before.kind in ('scalar', 'index'): result['delta'] = after.data - before.data
    if element_kind(before.kind):
        result['length_before']=len(before.data); result['length_after']=len(after.data)
        result['changed_indices']=[i for i in range(max(len(before.data),len(after.data)))
                                   if i>=len(before.data) or i>=len(after.data) or before.data[i].identity()!=after.data[i].identity()]
    if before.kind in ('grid', 'mask'):
        if before.data.shape != after.data.shape:
            result['shape_changed'] = True
        else:
            coordinates = np.argwhere(before.data != after.data)
            result.update(changed_cells=len(coordinates), coordinates=coordinates[:256].tolist(),
                          coordinates_truncated=len(coordinates) > 256)
    return result
