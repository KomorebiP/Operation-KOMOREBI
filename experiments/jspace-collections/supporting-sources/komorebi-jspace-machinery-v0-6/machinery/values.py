"""Values with explicit meanings and stable serialization. Komorebi P."""
from dataclasses import dataclass
import hashlib
import json
import numbers
import numpy as np

KINDS = {'scalar', 'index', 'color', 'flag', 'point', 'box', 'grid', 'mask'}


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


@dataclass(frozen=True, eq=False)
class Value:
    kind: str
    data: object

    def __post_init__(self):
        k, x = self.kind, self.data
        if k not in KINDS:
            raise Fault('type', f'Unknown value kind: {k}')
        if k == 'scalar':
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
        data = self.data.tolist() if isinstance(self.data, np.ndarray) else self.data
        if isinstance(data, tuple): data = list(data)
        return {'kind': self.kind, 'data': data}

    @classmethod
    def unpack(cls, obj):
        if not isinstance(obj, dict) or set(obj) != {'kind', 'data'}:
            raise Fault('schema', 'Expected a typed value with kind and data.')
        return cls(obj['kind'], obj['data'])

    def identity(self): return digest(self.pack())


def change(before, after):
    """Exact observed differences, distinct from inferred dependencies."""
    if before is None: return {'status': 'new', 'after': after.pack()}
    if after is None: return {'status': 'not_executed', 'before': before.pack()}
    if before.identity() == after.identity(): return {'status': 'unchanged'}
    result = {'status': 'changed', 'before': before.pack(), 'after': after.pack()}
    if before.kind != after.kind: return result
    if before.kind in ('scalar', 'index'): result['delta'] = after.data - before.data
    if before.kind in ('grid', 'mask'):
        if before.data.shape != after.data.shape:
            result['shape_changed'] = True
        else:
            coordinates = np.argwhere(before.data != after.data)
            result.update(changed_cells=len(coordinates), coordinates=coordinates[:256].tolist(),
                          coordinates_truncated=len(coordinates) > 256)
    return result
