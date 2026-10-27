"""Supplied object constructors and spatial operations. Komorebi P."""
from collections import deque
import numpy as np
from .values import Value, Fault, MAX_ITEMS, digest


def components(scene,background,connectivity):
    """Deterministic same-color connected components, in row-major order."""
    if connectivity.data not in (4,8):raise Fault('connectivity','Connectivity must be 4 or 8.')
    grid=scene.data;h,w=grid.shape;visited=np.zeros(grid.shape,bool);objects=[]
    neighbors=[(-1,0),(0,-1),(0,1),(1,0)]
    if connectivity.data==8:neighbors += [(-1,-1),(-1,1),(1,-1),(1,1)]
    for row in range(h):
        for col in range(w):
            if visited[row,col] or grid[row,col]==background.data:continue
            color=int(grid[row,col]);visited[row,col]=True;pending=deque([(row,col)]);pixels=[]
            while pending:
                r,c=pending.popleft();pixels.append([r,c,color])
                for dr,dc in neighbors:
                    nr,nc=r+dr,c+dc
                    if 0<=nr<h and 0<=nc<w and not visited[nr,nc] and grid[nr,nc]==color:
                        visited[nr,nc]=True;pending.append((nr,nc))
            if len(objects)>=MAX_ITEMS:raise Fault('budget',f'More than {MAX_ITEMS} objects were found.')
            pixels.sort();source=scene.identity()
            obj={'source':source,'origin_id':digest({'source':source,'pixels':pixels}),
                 'shape':[h,w],'pixels':pixels}
            objects.append(Value('object',obj))
    return Value('list[object]',objects)


def coordinates(item):
    pixels=np.asarray(item.data.pixels,dtype=int)
    return pixels[:,0],pixels[:,1],pixels[:,2]


def translate(item,offset):
    obj=item.data.pack();dr,dc=offset.data
    obj['pixels']=[[r+dr,c+dc,color] for r,c,color in item.data.pixels]
    return Value('object',obj)


def recolor(item,color):
    obj=item.data.pack();obj['pixels']=[[r,c,color.data] for r,c,_ in item.data.pixels]
    return Value('object',obj)


def color_of(item):
    colors={p[2] for p in item.data.pixels}
    if len(colors)!=1:raise Fault('ambiguous_color','Object has more than one color.')
    return Value('color',next(iter(colors)))


def bounds(item):
    r,c,_=coordinates(item)
    return Value('box',[int(r.min()),int(c.min()),int(r.max())+1,int(c.max())+1])


def mask(item):
    result=np.zeros(item.data.shape,bool);r,c,_=coordinates(item);result[r,c]=True
    return Value('mask',result)


def paint(state,item,background,overwrite):
    if state.data.shape!=item.data.shape:raise Fault('shape','Object and destination coordinate frames differ.')
    r,c,colors=coordinates(item)
    if not overwrite.data and np.any(state.data[r,c]!=background.data):
        raise Fault('collision','Painting would overwrite an occupied destination cell.')
    result=state.data.copy();result[r,c]=colors
    return Value('grid',result)


def erase(state,item,background):
    if state.data.shape!=item.data.shape:raise Fault('shape','Object and source coordinate frames differ.')
    r,c,colors=coordinates(item)
    if np.any(state.data[r,c]!=colors):raise Fault('stale_object','Object pixels no longer match the source scene.')
    result=state.data.copy();result[r,c]=background.data
    return Value('grid',result)


def register(add):
    add('grid.components',{'scene':'grid','background':'color','connectivity':'index'},'list[object]',components)
    add('object.translate',{'item':'object','offset':'point'},'object',translate)
    add('object.recolor',{'item':'object','color':'color'},'object',recolor)
    add('object.color',{'item':'object'},'color',color_of)
    add('object.area',{'item':'object'},'index',lambda item:Value('index',len(item.data.pixels)))
    add('object.bounds',{'item':'object'},'box',bounds)
    add('object.mask',{'item':'object'},'mask',mask)
    add('object.paint',{'state':'grid','item':'object','background':'color','overwrite':'flag'},'grid',paint)
    add('object.erase',{'state':'grid','item':'object','background':'color'},'grid',erase)
    add('objects.count',{'items':'list[object]'},'index',lambda items:Value('index',len(items.data)))
    add('index.at_least',{'a':'index','b':'index'},'flag',lambda a,b:Value('flag',a.data>=b.data))
    add('index.add',{'a':'index','b':'index'},'index',lambda a,b:Value('index',a.data+b.data))
