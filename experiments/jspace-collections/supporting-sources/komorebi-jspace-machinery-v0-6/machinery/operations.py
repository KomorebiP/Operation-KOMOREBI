"""Supplied scalar/grid machinery and frozen v0.5 kernel adapters. Komorebi P."""
from pathlib import Path
import hashlib
import json
import numpy as np
from .values import Value, Fault
from .runtime import Registry
from .legacy_kernels import Kernels

ROOT = Path(__file__).resolve().parent.parent


def division(a, b):
    if b.data == 0: raise Fault('zero_division','The denominator is zero.')
    return Value('scalar', a.data / b.data)


def bbox(mask):
    cells = np.argwhere(mask.data)
    if not len(cells): raise Fault('empty_selection','The mask selects no cells.')
    low, high = cells.min(axis=0), cells.max(axis=0)+1
    return Value('box', [*low.tolist(), *high.tolist()])


def crop(scene, region):
    r0,c0,r1,c1 = region.data
    if r1 > scene.data.shape[0] or c1 > scene.data.shape[1]: raise Fault('bounds','Crop exceeds the scene.')
    return Value('grid', scene.data[r0:r1,c0:c1])


def paint(scene, mask, color):
    if scene.data.shape != mask.data.shape: raise Fault('shape','Paint mask and scene sizes differ.')
    result = scene.data.copy(); result[mask.data] = color.data
    return Value('grid', result)


def paste(scene, patch, at, transparent):
    row,col = at.data; h,w = patch.data.shape
    if row < 0 or col < 0 or row+h > scene.data.shape[0] or col+w > scene.data.shape[1]:
        raise Fault('bounds','The entire patch must fit inside the destination scene.')
    result = scene.data.copy(); view = result[row:row+h,col:col+w]
    selected = patch.data != 0 if transparent.data else np.ones(patch.data.shape,bool)
    view[selected] = patch.data[selected]
    return Value('grid', result)


def masked_copy(destination, source, mask):
    if not destination.data.shape == source.data.shape == mask.data.shape:
        raise Fault('shape','Masked copy requires aligned grids and mask.')
    result = destination.data.copy(); result[mask.data] = source.data[mask.data]
    return Value('grid', result)


def changed(a,b):
    if a.data.shape != b.data.shape: raise Fault('shape','Difference masks require equal grid sizes.')
    return Value('mask',a.data != b.data)


def base_registry():
    registry = Registry()
    # Bind native semantics to this release's source, not merely a friendly name.
    source = b''.join((ROOT/'machinery'/name).read_bytes() for name in ['operations.py','values.py','runtime.py'])
    version = hashlib.sha256(source).hexdigest()
    def add(name, parameters, output, fn):
        registry.native(name,parameters,output,fn,version+':'+name)
    for name,fn in [('number.add',lambda a,b:a+b),('number.subtract',lambda a,b:a-b),('number.multiply',lambda a,b:a*b)]:
        add(name,{'a':'scalar','b':'scalar'},'scalar',lambda a,b,f=fn:Value('scalar',f(a.data,b.data)))
    add('number.divide',{'a':'scalar','b':'scalar'},'scalar',division)
    add('number.greater',{'a':'scalar','b':'scalar'},'flag',lambda a,b:Value('flag',a.data>b.data))
    add('flag.not',{'value':'flag'},'flag',lambda value:Value('flag',not value.data))
    add('grid.color_mask',{'scene':'grid','color':'color'},'mask',lambda scene,color:Value('mask',scene.data==color.data))
    add('mask.bounds',{'mask':'mask'},'box',bbox)
    add('mask.count',{'mask':'mask'},'index',lambda mask:Value('index',int(mask.data.sum())))
    add('mask.nonempty',{'mask':'mask'},'flag',lambda mask:Value('flag',bool(mask.data.any())))
    add('mask.origin',{'mask':'mask'},'point',lambda mask:Value('point',bbox(mask).data[:2]))
    add('grid.crop',{'scene':'grid','region':'box'},'grid',crop)
    add('grid.rotate',{'patch':'grid','turns':'index'},'grid',lambda patch,turns:Value('grid',np.rot90(patch.data,turns.data%4)))
    add('grid.paint',{'scene':'grid','mask':'mask','color':'color'},'grid',paint)
    add('grid.paste',{'scene':'grid','patch':'grid','at':'point','transparent':'flag'},'grid',paste)
    add('grid.masked_copy',{'destination':'grid','source':'grid','mask':'mask'},'grid',masked_copy)
    add('grid.changed',{'a':'grid','b':'grid'},'mask',changed)
    model = Kernels.load(ROOT/'models/learned_square_0.npz')
    catalog = json.loads((ROOT/'models/catalog_square_0.json').read_text())
    if model.identity() != catalog['receipt']['kernel_identity']:
        raise Fault('identity','The primitive catalog does not match the model.')
    kernel_source = hashlib.sha256((ROOT/'machinery/legacy_kernels.py').read_bytes()).hexdigest()
    for channel in catalog['accepted']:
        def kernel(a,b,channel=channel): return Value('scalar',float(model.call(channel,a.data,b.data)))
        registry.native('learned.'+channel,{'a':'scalar','b':'scalar'},'scalar',kernel,
                        model.identity()+':'+kernel_source+':'+channel,origin='learned_frozen_v0.5')
    return registry
