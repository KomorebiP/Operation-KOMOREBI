"""Exact minimax energy-grid planning over declared conservative cell weights."""
from fractions import Fraction as F
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'stage16'))
from interval_certificate import endpoint,cell

SCALE=10**18
def ceiling(x):
    x=F(x);return F(-(-x.numerator*SCALE//x.denominator),SCALE)

def sharp_radius(r0,r1,C):
    r0,r1,C=map(F,(r0,r1,C))
    if min(r0,r1,C)<0:raise ValueError('Nonnegative radii and coefficient required')
    if not C or abs(r1-r0)>=C:return max(r0,r1)
    return (r0+r1)/2+C/4+(r1-r0)**2/(4*C)

def edge(a,b):
    if a['eta']!=b['eta']:raise ValueError('Broadenings differ')
    def ep(p):return endpoint(p['energy'],p['eta'],p['center'],p['radius'])
    s=cell(ep(a),ep(b));C=ceiling(s['interpolation_coefficient'])
    return C,ceiling(sharp_radius(a['radius'],b['radius'],C))

def weights(points):
    if not 2<=len(points)<=166:raise ValueError('Unsupported saved-node count')
    if any(F(a['energy'])>=F(b['energy']) for a,b in zip(points,points[1:])):raise ValueError('Energy nodes must increase strictly')
    n=len(points);out=[[None]*n for _ in points]
    for i in range(n):
        for j in range(i+1,n):out[i][j]=edge(points[i],points[j])[1]
    return out

def frontier(W):
    """Pareto rows: strictly improving bottleneck, exact number of used nodes."""
    n=len(W)
    if n<2 or any(len(row)!=n for row in W):raise ValueError('Square ordered weight matrix required')
    if any(W[i][j] is None or W[i][j]<0 for i in range(n) for j in range(i+1,n)):raise ValueError('Complete nonnegative forward weights required')
    values=[[None]*n for _ in range(n+1)];parent=[[None]*n for _ in range(n+1)];values[1][0]=F(0)
    rows=[];best=None
    for count in range(2,n+1):
        for j in range(count-1,n):
            candidates=[(max(values[count-1][i],W[i][j]),i) for i in range(count-2,j) if values[count-1][i] is not None]
            if candidates:values[count][j],parent[count][j]=min(candidates)
        radius=values[count][-1]
        if radius is not None and (best is None or radius<best):
            ids=[n-1];j=n-1
            for level in range(count,1,-1):j=parent[level][j];ids.append(j)
            ids.reverse();assert ids[0]==0 and len(ids)==count
            rows.append(dict(nodes=count,radius=str(radius),indices=ids));best=radius
    return rows

def choose(rows,tolerance):
    tolerance=F(tolerance)
    if tolerance<=0:raise ValueError('Positive absolute response tolerance required')
    return next((r for r in rows if F(r['radius'])<=tolerance),None)

def greedy(W,tolerance):
    ids=[0];last=len(W)-1
    while ids[-1]!=last:
        feasible=[j for j in range(ids[-1]+1,last+1) if W[ids[-1]][j]<=tolerance]
        if not feasible:return None
        ids.append(max(feasible))
    return ids

def shortest(W,tolerance):
    """Independent threshold-feasibility calculation (node count, not minimax)."""
    n=len(W);distance=[None]*n;distance[0]=1
    for j in range(1,n):
        options=[distance[i]+1 for i in range(j) if distance[i] is not None and W[i][j]<=tolerance]
        if options:distance[j]=min(options)
    return distance[-1]

def select(groups,eta,tolerance,objective='actions'):
    if objective not in ['actions','energies']:raise ValueError('Unknown planning objective')
    plans=[dict(order=g['order'],saved_nodes=g['saved_nodes'],**r) for g in groups if g['eta']==eta and (r:=choose(g['frontier'],tolerance))]
    return min(plans,key=(lambda p:(p['order'],p['nodes'])) if objective=='actions' else (lambda p:(p['nodes'],p['order']))) if plans else None
