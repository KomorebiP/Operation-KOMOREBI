"""Delta-routed same-shape relational synthesis lanes for Block 6.

The implementations were recovered from the Block 5 research probes and are
kept task-ID-free.  Every parameter is inferred from training demonstrations.
"""

from __future__ import annotations

import json,itertools,math,time

from collections import Counter,defaultdict,deque

from dataclasses import dataclass

from pathlib import Path

from typing import Any,Callable

import numpy as np

def A(x):return np.asarray(x,dtype=np.int16)

def F(x):return tuple(tuple(int(v) for v in row) for row in A(x).tolist())

def bg(a):return Counter(map(int,a.ravel())).most_common(1)[0][0]

def bbox(m):
 y,x=np.nonzero(m)
 return None if len(y)==0 else (int(y.min()),int(y.max()+1),int(x.min()),int(x.max()+1))

def components_mask(m,conn=4):
 h,w=m.shape;seen=np.zeros_like(m,bool);out=[]
 dirs=[(-1,0),(1,0),(0,-1),(0,1)]
 if conn==8:dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]
 for y in range(h):
  for x in range(w):
   if not m[y,x] or seen[y,x]:continue
   q=[(y,x)];seen[y,x]=1;c=[]
   while q:
    yy,xx=q.pop();c.append((yy,xx))
    for dy,dx in dirs:
     ny,nx=yy+dy,xx+dx
     if 0<=ny<h and 0<=nx<w and m[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;q.append((ny,nx))
   out.append(c)
 return out

def exact_all(fn,task):
 try:return all(np.array_equal(fn(ex['input']),A(ex['output'])) for ex in task['train'])
 except Exception:return False

@dataclass
class Compiled:
 family:str
 params:dict[str,Any]
 fn:Callable[[Any],np.ndarray]
 def key(self):return self.family+':'+json.dumps(self.params,sort_keys=True,separators=(',',':'))

def intervals_from_blank(a,b,axis):
 blank=[i for i in range(a.shape[axis]) if np.all((a[i,:] if axis==0 else a[:,i])==b)]
 runs=[];start=None
 for i in range(a.shape[axis]):
  if i in blank:
   if start is not None:runs.append((start,i));start=None
  elif start is None:start=i
 if start is not None:runs.append((start,a.shape[axis]))
 return runs

def exec_tile_complement(grid,params):
 a=A(grid);b=bg(a);rs=intervals_from_blank(a,b,0);cs=intervals_from_blank(a,b,1)
 if len(rs)*len(cs)<2:raise ValueError
 out=np.full_like(a,b);color=int(params['target_color']);policy=params['policy']
 for y0,y1 in rs:
  for x0,x1 in cs:
   sub=a[y0:y1,x0:x1];m=sub!=b
   if policy=='nonempty_only' and not m.any():continue
   out[y0:y1,x0:x1]=np.where(~m,color,b)
 return out

def compile_tile_complement(task):
 colors=set(range(10))
 # target color candidates from training nonbackground colors
 candidates=set()
 for ex in task['train']:
  y=A(ex['output']);bb=bg(y);c=set(map(int,y.ravel()))-{bb}
  candidates |= c
 out=[]
 for c in candidates:
  for policy in ('all_tiles','nonempty_only'):
   p={'target_color':int(c),'policy':policy};fn=lambda g,p=p:exec_tile_complement(g,p)
   if exact_all(fn,task):out.append(Compiled('tile_complement',p,fn))
 return out

def axis_candidates(a,b):
 out=[]
 for x in range(a.shape[1]):
  col=a[:,x]
  if np.all(col!=b):out.append(('vertical',x))
 for y in range(a.shape[0]):
  row=a[y,:]
  if np.all(row!=b):out.append(('horizontal',y))
 return out

def choose_axis(a,b,role):
 cs=axis_candidates(a,b)
 if not cs:raise ValueError
 if role=='unique':
  if len(cs)!=1:raise ValueError
  return cs[0]
 # score axis by side imbalance of nonbackground support excluding axis
 scored=[]
 for ori,k in cs:
  if ori=='vertical':neg=np.count_nonzero(a[:,:k]!=b);pos=np.count_nonzero(a[:,k+1:]!=b)
  else:neg=np.count_nonzero(a[:k,:]!=b);pos=np.count_nonzero(a[k+1:,:]!=b)
  scored.append((abs(int(neg)-int(pos)),ori,k,neg,pos))
 scored.sort(reverse=True)
 if len(scored)>1 and scored[0][0]==scored[1][0]:raise ValueError
 _,ori,k,neg,pos=scored[0]
 return ori,k

def exec_axis_reflect(grid,params):
 a=A(grid);b=bg(a);ori,k=choose_axis(a,b,params['axis_role'])
 if ori!=params['orientation']:raise ValueError
 out=a.copy();mode=params['source_side']
 if mode=='denser':
  neg=np.count_nonzero((a[:,:k] if ori=='vertical' else a[:k,:])!=b)
  pos=np.count_nonzero((a[:,k+1:] if ori=='vertical' else a[k+1:,:])!=b)
  side='negative' if neg>pos else 'positive'
  if neg==pos:raise ValueError
 else:side=mode
 if ori=='vertical':
  xs=range(0,k) if side=='negative' else range(k+1,a.shape[1])
  for x in xs:
   tx=2*k-x
   if 0<=tx<a.shape[1]:
    for y in range(a.shape[0]):
     if params['copy_background'] or a[y,x]!=b:out[y,tx]=a[y,x]
 else:
  ys=range(0,k) if side=='negative' else range(k+1,a.shape[0])
  for y in ys:
   ty=2*k-y
   if 0<=ty<a.shape[0]:
    for x in range(a.shape[1]):
     if params['copy_background'] or a[y,x]!=b:out[ty,x]=a[y,x]
 return out

def compile_axis_reflect(task):
 out=[]
 for ori in ('vertical','horizontal'):
  for ar in ('unique','max_imbalance'):
   for side in ('denser','negative','positive'):
    for cb in (False,True):
     p={'orientation':ori,'axis_role':ar,'source_side':side,'copy_background':cb}
     fn=lambda g,p=p:exec_axis_reflect(g,p)
     if exact_all(fn,task):out.append(Compiled('axis_reflect_copy',p,fn))
 return out

DIRECTIONS={'se':(1,1),'sw':(1,-1),'south':(1,0),'east':(0,1)}

def exec_phase_recolor(grid,p):
 a=A(grid);b=bg(a);out=a.copy();dy,dx=DIRECTIONS[p['direction']]
 # each color separately, find starts lacking predecessor
 for color in sorted(set(map(int,a.ravel()))-{b}):
  cells={(int(y),int(x)) for y,x in zip(*np.nonzero(a==color))}
  starts=sorted((y,x) for y,x in cells if (y-dy,x-dx) not in cells)
  visited=set()
  for y,x in starts:
   i=0
   while (y,x) in cells and (y,x) not in visited:
    visited.add((y,x))
    if i%p['period'] in p['residues']:out[y,x]=p['target_color']
    y,x=y+dy,x+dx;i+=1
  # fail closed on cycles/branches/unvisited
  if visited!=cells:raise ValueError
 return out

def compile_phase_recolor(task):
 tc=set()
 for ex in task['train']:
  x=A(ex['input']);y=A(ex['output']);
  tc |= set(map(int,y[x!=y]))
 out=[]
 for direction in DIRECTIONS:
  for period in range(2,6):
   for bits in range(1,2**period-1):
    residues=tuple(i for i in range(period) if bits>>i&1)
    for color in tc:
     p={'direction':direction,'period':period,'residues':residues,'target_color':int(color)}
     fn=lambda g,p=p:exec_phase_recolor(g,p)
     if exact_all(fn,task):out.append(Compiled('phase_chain_recolor',p,fn))
 return out

def path_order(comp):
 s=set(comp);adj={c:[d for d in ((c[0]-1,c[1]),(c[0]+1,c[1]),(c[0],c[1]-1),(c[0],c[1]+1)) if d in s] for c in s}
 if any(len(v)>2 for v in adj.values()):raise ValueError
 ends=sorted(k for k,v in adj.items() if len(v)<=1)
 if len(s)==1:return list(s)
 if len(ends)!=2:raise ValueError
 order=[];prev=None;cur=ends[0]
 while True:
  order.append(cur);nxt=[v for v in adj[cur] if v!=prev]
  if not nxt:break
  prev,cur=cur,nxt[0]
 if len(order)!=len(s):raise ValueError
 return order

def exec_reverse_paths(grid,p):
 a=A(grid);b=bg(a);out=a.copy();comps=components_mask(a!=b,4)
 for c in comps:
  if len(c)<p['minimum_length']:
   if p['short_policy']=='reject':raise ValueError
   continue
  order=path_order(c);vals=[int(a[y,x]) for y,x in order][::-1]
  for (y,x),v in zip(order,vals):out[y,x]=v
 return out

def compile_reverse_paths(task):
 out=[]
 for ml in (1,2,3):
  for sp in ('keep','reject'):
   p={'minimum_length':ml,'short_policy':sp};fn=lambda g,p=p:exec_reverse_paths(g,p)
   if exact_all(fn,task):out.append(Compiled('reverse_path_colors',p,fn))
 return out

def exec_quadrant_transport(grid,p):
 a=A(grid);b=bg(a);cs=components_mask(a!=b,4);objs=[]
 for c in cs:
  box=bbox(np.isin(np.indices(a.shape).transpose(1,2,0).reshape(-1,2),c).all(axis=2)) if False else None
  ys=[y for y,x in c];xs=[x for y,x in c];y0,y1,x0,x1=min(ys),max(ys)+1,min(xs),max(xs)+1
  vals=[int(a[y,x]) for y,x in c];objs.append((c,(y0,y1,x0,x1),Counter(vals).most_common(1)[0][0]))
 centers=[o for o in objs if len(o[0])==4 and o[1][1]-o[1][0]==2 and o[1][3]-o[1][2]==2 and all(a[y,x]==o[2] for y,x in o[0])]
 if len(centers)!=1:raise ValueError
 c,box,cc=centers[0];y0,y1,x0,x1=box;cy=(y0+y1-1)/2;cx=(x0+x1-1)/2
 singles=[o for o in objs if len(o[0])==1 and o is not centers[0]]
 q={}
 for cells,bb,col in singles:
  y,x=cells[0];name=('n' if y<cy else 's')+('w' if x<cx else 'e')
  if name in q:raise ValueError
  q[name]=col
 if set(q)!= {'nw','ne','sw','se'}:raise ValueError
 out=np.full_like(a,b)
 out[y0,x0]=q['nw'];out[y0,x0+1]=q['ne'];out[y0+1,x0]=q['sw'];out[y0+1,x0+1]=q['se']
 return out

def compile_quadrant(task):
 p={};fn=lambda g:exec_quadrant_transport(g,p)
 return [Compiled('quadrant_marker_transport',p,fn)] if exact_all(fn,task) else []

def line_info(a,b):
 cs=components_mask(a!=b,4)
 if len(cs)!=1:raise ValueError
 c=cs[0];ys=sorted(set(y for y,x in c));xs=sorted(set(x for y,x in c));color=int(a[c[0]])
 if len(xs)==1 and len(c)==len(ys) and ys==list(range(min(ys),max(ys)+1)):return 'vertical',xs[0],min(ys),max(ys),color
 if len(ys)==1 and len(c)==len(xs) and xs==list(range(min(xs),max(xs)+1)):return 'horizontal',ys[0],min(xs),max(xs),color
 raise ValueError

def exec_line_cone(grid,p):
 a=A(grid);b=bg(a);ori,axis,start,end,c=line_info(a,b);out=np.full_like(a,b);alt=p['alternate_color']
 if ori!=p['orientation']:raise ValueError
 # expand from one line end; radius equals remaining line length
 if ori=='vertical':
  direction=p['expand_toward']
  rows=range(start,end+1)
  endpoint=end if direction=='start' else start
  for y in rows:
   radius=(end-y) if direction=='start' else (y-start)
   # wait: expand toward start means widest at start => radius=end-y
   for x in range(max(0,axis-radius),min(a.shape[1],axis+radius+1)):
    out[y,x]=c if abs(x-axis)%2==0 else alt
 else:
  direction=p['expand_toward']
  cols=range(start,end+1)
  for x in cols:
   radius=(end-x) if direction=='start' else (x-start)
   for y in range(max(0,axis-radius),min(a.shape[0],axis+radius+1)):
    out[y,x]=c if abs(y-axis)%2==0 else alt
 return out

def compile_line_cone(task):
 colors=set()
 for ex in task['train']:
  x=A(ex['input']);y=A(ex['output']);colors |= (set(map(int,y.ravel()))-set(map(int,x.ravel())))
 out=[]
 for ori in ('vertical','horizontal'):
  for toward in ('start','end'):
   for c in colors:
    p={'orientation':ori,'expand_toward':toward,'alternate_color':int(c)};fn=lambda g,p=p:exec_line_cone(g,p)
    if exact_all(fn,task):out.append(Compiled('alternating_line_cone',p,fn))
 return out

def solid_rects(a,b):
 out=[]
 for color in sorted(set(map(int,a.ravel()))-{b}):
  for comp in components_mask(a==color,4):
   ys=[y for y,x in comp];xs=[x for y,x in comp];box=(min(ys),max(ys)+1,min(xs),max(xs)+1)
   y0,y1,x0,x1=box
   if len(comp)==(y1-y0)*(x1-x0):out.append((box,color))
 return out

def exec_perforate(grid,p):
 a=A(grid);b=bg(a);out=a.copy();rects=solid_rects(a,b)
 if not rects:raise ValueError
 for (y0,y1,x0,x1),color in rects:
  h,w=y1-y0,x1-x0
  if p['orientation']=='horizontal' and h==p['thickness']:
   row=y0+h//2
   for x in range(x0,x1):
    if (x-x0)%p['period'] in p['erase_residues']:out[row,x]=b
  elif p['orientation']=='vertical' and w==p['thickness']:
   col=x0+w//2
   for y in range(y0,y1):
    if (y-y0)%p['period'] in p['erase_residues']:out[y,col]=b
  elif p['reject_nonmatching']:raise ValueError
 return out

def compile_perforate(task):
 out=[]
 for ori in ('horizontal','vertical'):
  for thick in (3,5):
   for period in (2,3):
    for bits in range(1,2**period):
     residues=tuple(i for i in range(period) if bits>>i&1)
     for reject in (False,True):
      p={'orientation':ori,'thickness':thick,'period':period,'erase_residues':residues,'reject_nonmatching':reject}
      fn=lambda g,p=p:exec_perforate(g,p)
      if exact_all(fn,task):out.append(Compiled('rectangle_midline_perforation',p,fn))
 return out

def all_solid_rectangles(mask,min_h,min_w):
 h,w=mask.shape;rects=[]
 # enumerate top/bottom and maintain columns all true; grids <=30
 for y0 in range(h):
  cols=np.ones(w,bool)
  for y1 in range(y0+1,h+1):
   cols &= mask[y1-1]
   if y1-y0<min_h:continue
   x=0
   while x<w:
    if not cols[x]:x+=1;continue
    s=x
    while x<w and cols[x]:x+=1
    e=x
    if e-s>=min_w:rects.append((y0,y1,s,e))
 return rects

def maximal_rectangles(rects):
 out=[]
 for r in rects:
  if not any(r!=q and q[0]<=r[0] and q[1]>=r[1] and q[2]<=r[2] and q[3]>=r[3] for q in rects):out.append(r)
 return out

def exec_retain_rectangles(grid,p):
 a=A(grid);b=bg(a);out=np.full_like(a,b);found=0
 for color in sorted(set(map(int,a.ravel()))-{b}):
  rs=maximal_rectangles(all_solid_rectangles(a==color,p['min_h'],p['min_w']))
  if p['selection']=='max_area' and rs:
   area=max((y1-y0)*(x1-x0) for y0,y1,x0,x1 in rs);rs=[r for r in rs if (r[1]-r[0])*(r[3]-r[2])==area]
  for y0,y1,x0,x1 in rs:out[y0:y1,x0:x1]=color;found+=1
 if not found:raise ValueError
 return out

def compile_retain_rectangles(task):
 out=[]
 for mh,mw in ((2,2),(2,3),(3,2),(3,3)):
  for sel in ('all_maximal','max_area'):
   p={'min_h':mh,'min_w':mw,'selection':sel};fn=lambda g,p=p:exec_retain_rectangles(g,p)
   if exact_all(fn,task):out.append(Compiled('retain_maximal_rectangles',p,fn))
 return out

FAMILIES=[compile_tile_complement,compile_axis_reflect,compile_phase_recolor,compile_reverse_paths,compile_quadrant,compile_line_cone,compile_perforate,compile_retain_rectangles]

def compile_task(task):
 out=[]
 for c in FAMILIES:
  try:out+=c(task)
  except Exception:pass
 # dedup keys
 return {x.key():x for x in out}

def exec_minimum_span_fill(grid,p):
 a=A(grid); b=bg(a); out=a.copy(); axis=p['axis']
 records=[]
 n=a.shape[0] if axis=='row' else a.shape[1]
 for i in range(n):
  line=a[i,:] if axis=='row' else a[:,i]
  inds=[j for j,v in enumerate(line) if int(v)!=b]
  if len(inds)!=2:continue
  colors=[int(line[j]) for j in inds]
  if p['require_same_color'] and colors[0]!=colors[1]:continue
  records.append((i,inds[1]-inds[0],inds,colors[0]))
 if not records:raise ValueError
 minimum=min(r[1] for r in records)
 for i,span,inds,color in records:
  if span!=minimum:continue
  lo,hi=inds
  if axis=='row':out[i,lo:hi+1]=color
  else:out[lo:hi+1,i]=color
 return out

def compile_minimum_span_fill(task):
 out=[]
 for axis in ('row','col'):
  for same in (True,False):
   p={'axis':axis,'require_same_color':same};fn=lambda g,p=p:exec_minimum_span_fill(g,p)
   if exact_all(fn,task):out.append(Compiled('minimum_span_fill',p,fn))
 return out

def exec_axis_rank_recolor(grid,p):
 a=A(grid); b=bg(a); mask=a!=b
 rows=sorted(set(int(y) for y in np.nonzero(mask)[0]));cols=sorted(set(int(x) for x in np.nonzero(mask)[1]))
 if p['axis_rule']=='more_unique':
  if len(rows)==len(cols):raise ValueError
  axis='row' if len(rows)>len(cols) else 'col'
 else:axis=p['axis_rule']
 coords=rows if axis=='row' else cols
 out=a.copy();seq=tuple(p['sequence']);period=len(seq)
 for rank,coord in enumerate(coords):
  color=seq[(p['phase']+p['step']*rank)%period]
  if axis=='row':out[coord,mask[coord,:]]=color
  else:out[mask[:,coord],coord]=color
 return out

def compile_axis_rank_recolor(task):
 # require support preservation and one common output sequence over rank modulo p
 ins=[A(e['input']) for e in task['train']];outs=[A(e['output']) for e in task['train']]
 out=[]
 for axis_rule in ('more_unique','row','col'):
  for period in range(2,7):
   for step in range(1,period):
    for phase in range(period):
     slots=[None]*period;valid=True
     for a,y in zip(ins,outs):
      b=bg(a);mask=a!=b
      if a.shape!=y.shape or not np.array_equal(mask,y!=b):valid=False;break
      rows=sorted(set(int(v) for v in np.nonzero(mask)[0]));cols=sorted(set(int(v) for v in np.nonzero(mask)[1]))
      if axis_rule=='more_unique':
       if len(rows)==len(cols):valid=False;break
       axis='row' if len(rows)>len(cols) else 'col'
      else:axis=axis_rule
      coords=rows if axis=='row' else cols
      for rank,coord in enumerate(coords):
       vals=set(int(v) for v in (y[coord,mask[coord,:]] if axis=='row' else y[mask[:,coord],coord]))
       if len(vals)!=1:valid=False;break
       value=next(iter(vals));slot=(phase+step*rank)%period
       if slots[slot] is not None and slots[slot]!=value:valid=False;break
       slots[slot]=value
      if not valid:break
     if not valid or any(v is None for v in slots):continue
     p={'axis_rule':axis_rule,'sequence':tuple(int(v) for v in slots),'period':period,'step':step,'phase':phase}
     fn=lambda g,p=p:exec_axis_rank_recolor(g,p)
     if exact_all(fn,task):out.append(Compiled('axis_rank_recolor',p,fn))
 return out

FAMILIES.extend([compile_minimum_span_fill,compile_axis_rank_recolor])

def _all_same_shape(task):
 return all(A(e['input']).shape==A(e['output']).shape for e in task['train'])

def _support_relation(task,relation):
 for e in task['train']:
  a=A(e['input']);y=A(e['output']);bi=bg(a);mi=a!=bi;mo=y!=bi
  if a.shape!=y.shape:return False
  if relation=='same' and not np.array_equal(mi,mo):return False
  if relation=='subset' and np.any(mo & ~mi):return False
  if relation=='superset' and np.any(mi & ~mo):return False
 return True

def _line_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'superset'):return False
 try:
  for e in task['train']:line_info(A(e['input']),bg(A(e['input'])))
  return True
 except Exception:return False

def _quadrant_route(task):
 if not _all_same_shape(task):return False
 for e in task['train']:
  a=A(e['input']);b=bg(a);cs=components_mask(a!=b,4);sizes=sorted(map(len,cs))
  if sizes.count(1)!=4 or sizes.count(4)!=1 or len(sizes)!=5:return False
 return True

def _tile_route(task):
 if not _all_same_shape(task):return False
 for e in task['train']:
  a=A(e['input']);b=bg(a);rs=intervals_from_blank(a,b,0);cs=intervals_from_blank(a,b,1)
  if len(rs)<1 or len(cs)<1 or len(rs)*len(cs)<2:return False
 return True

def _phase_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'same'):return False
 # Require sparse monochrome directional chains in the first input.
 a=A(task['train'][0]['input']);b=bg(a)
 return np.count_nonzero(a!=b)<=max(64,a.size//2)

def _path_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'same'):return False
 try:
  for e in task['train']:
   a=A(e['input']);b=bg(a)
   for comp in components_mask(a!=b,4):path_order(comp)
  return True
 except Exception:return False

def _perforate_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'subset'):return False
 return all(bool(solid_rects(A(e['input']),bg(A(e['input'])))) for e in task['train'])

def _rect_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'subset'):return False
 return all(np.count_nonzero(A(e['input'])!=bg(A(e['input'])))>np.count_nonzero(A(e['output'])!=bg(A(e['output']))) for e in task['train'])

def _span_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'superset'):return False
 return True

def _axis_rank_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'same'):return False
 for e in task['train']:
  a=A(e['input']);b=bg(a)
  if any(len(c)!=1 for c in components_mask(a!=b,8)):return False
 return True

def _axis_reflect_route(task):
 if not _all_same_shape(task) or not _support_relation(task,'superset'):return False
 return any(axis_candidates(A(e['input']),bg(A(e['input']))) for e in task['train'])

ROUTED=[
 (_tile_route,compile_tile_complement),
 (_axis_reflect_route,compile_axis_reflect),
 (_phase_route,compile_phase_recolor),
 (_path_route,compile_reverse_paths),
 (_quadrant_route,compile_quadrant),
 (_line_route,compile_line_cone),
 (_perforate_route,compile_perforate),
 (_rect_route,compile_retain_rectangles),
 (_span_route,compile_minimum_span_fill),
 (_axis_rank_route,compile_axis_rank_recolor),
]

def compile_task_routed(task):
 out=[];routes=[]
 for pred,compiler in ROUTED:
  try:ok=pred(task)
  except Exception:ok=False
  if not ok:continue
  routes.append(compiler.__name__)
  try:out+=compiler(task)
  except Exception:pass
 return {x.key():x for x in out},routes

TARGETED_FAMILY_EXECUTORS = {
    "tile_complement": exec_tile_complement,
    "axis_reflect_copy": exec_axis_reflect,
    "phase_chain_recolor": exec_phase_recolor,
    "reverse_path_colors": exec_reverse_paths,
    "quadrant_marker_transport": exec_quadrant_transport,
    "alternating_line_cone": exec_line_cone,
    "rectangle_midline_perforation": exec_perforate,
    "retain_maximal_rectangles": exec_retain_rectangles,
    "minimum_span_fill": exec_minimum_span_fill,
    "axis_rank_recolor": exec_axis_rank_recolor,
}


def execute_targeted_family(family: str, grid: Any, parameters: dict[str, Any]) -> np.ndarray:
    try:
        executor = TARGETED_FAMILY_EXECUTORS[family]
    except KeyError as error:
        raise KeyError(f"unknown targeted family {family!r}") from error
    return A(executor(grid, parameters))
