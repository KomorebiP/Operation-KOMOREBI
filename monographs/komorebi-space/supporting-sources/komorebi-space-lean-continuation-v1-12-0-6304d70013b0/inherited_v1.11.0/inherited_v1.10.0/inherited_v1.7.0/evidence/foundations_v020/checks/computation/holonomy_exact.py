#!/usr/bin/env python3
"""Independent exact-rational audit of holonomy, anchored repair and a sharp example.

The finite assertions do not replace the universally quantified Lean theorems.
All matrices use Fraction, directed transport t[i,j] maps view j to view i,
and composition A*B means A after B. No random numbers or floating tolerances.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, itertools as it, json, platform, time
from collections import deque
from fractions import Fraction as Q
from pathlib import Path

ASSERTIONS = 0

def check(ok: bool, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    if not ok:
        raise AssertionError(message)

def mat(rows): return tuple(tuple(Q(v) for v in row) for row in rows)
def eye(n): return mat([[int(i == j) for j in range(n)] for i in range(n)])
def transpose(a): return tuple(zip(*a))
def mm(a,b):
    return mat([[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a])
def mv(a,x): return tuple(sum((y*z for y,z in zip(row,x)),Q(0)) for row in a)
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def norm(x): return max(map(abs,x),default=Q(0))
def vnorm(x): return max(map(norm,x),default=Q(0))
def rref(a, ncols=None):
    n = ncols if ncols is not None else len(a[0])
    a=[list(map(Q,row)) for row in a]; row=0; pivots=[]
    for col in range(n):
        pivot=next((i for i in range(row,len(a)) if a[i][col]),None)
        if pivot is None: continue
        a[row],a[pivot]=a[pivot],a[row]
        d=a[row][col];a[row]=[v/d for v in a[row]]
        for i in range(len(a)):
            if i != row and a[i][col]:
                d=a[i][col];a[i]=[x-d*y for x,y in zip(a[i],a[row])]
        pivots.append(col); row+=1
        if row==len(a): break
    return a,pivots

def kernel(a,ncols):
    r,pivots=rref(a,ncols); free=[j for j in range(ncols) if j not in pivots]; out=[]
    for j in free:
        z=[Q(0)]*ncols;z[j]=Q(1)
        for i,k in enumerate(pivots):z[k]=-r[i][j]
        out.append(tuple(z))
    return out

I=eye(2)
GROUP=[]
for perm in it.permutations(range(2)):
    for signs in it.product((-1,1),repeat=2):
        GROUP.append(mat([[signs[i] if j==perm[i] else 0 for j in range(2)] for i in range(2)]))

def routes(n,edges,reverse=False):
    adj=[[] for _ in range(n)]
    for i,j in edges: adj[i].append(j);adj[j].append(i)
    paths={0:[0]};q=deque([0])
    while q:
        i=q.popleft()
        for j in sorted(adj[i],reverse=reverse):
            if j not in paths: paths[j]=paths[i]+[j];q.append(j)
    if len(paths)!=n:raise ValueError('Fixture graph not connected')
    return [paths[i] for i in range(n)]

def path_matrix(path,t):
    a=I
    for i,j in zip(path,path[1:]):a=mm(a,t[i,j])
    return a

def residual(x,t,directed):return [sub(mv(t[i,j],x[j]),x[i]) for i,j in directed]
def reconstruct(frames,z):return [mv(e,z) for e in frames]

def audit_graph(n,edges,mode,counts,dimensions):
    directed=sorted(edges+[(j,i) for i,j in edges]); t={}
    vertex_frames=[GROUP[(2*i+mode)%len(GROUP)] for i in range(n)]
    for k,(i,j) in enumerate(edges):
        if mode==0:a=mm(vertex_frames[i],transpose(vertex_frames[j]))
        elif mode==1:a=I
        elif mode==2:a=mat([[1,0],[0,-1]]) if k==len(edges)-1 else I
        else:a=GROUP[(i+3*j+5*mode+k)%len(GROUP)]
        t[i,j]=a;t[j,i]=transpose(a)
    paths=routes(n,edges); Ts=[path_matrix(p,t) for p in paths];frames=[transpose(a) for a in Ts]
    radius=max(len(p)-1 for p in paths)
    loops={a:mm(mm(Ts[a[0]],t[a]),frames[a[1]]) for a in directed}
    L=mat([[K[i][j]-I[i][j] for j in range(2)] for K in loops.values() for i in range(2)])
    D=[]
    for i,j in directed:
        for k in range(2):
            row=[Q(0)]*(2*n)
            row[2*i+k]=-1
            for l in range(2):row[2*j+l]+=t[i,j][k][l]
            D.append(tuple(row))
    D=mat(D); fixed=kernel(L,2); parallel=kernel(D,2*n)
    check(len(fixed)==len(parallel),'Kernel dimension mismatch')
    dimensions[len(fixed)]=dimensions.get(len(fixed),0)+1
    for z in fixed:
        x=reconstruct(frames,z)
        check(all(v==0 for v in mv(D,tuple(it.chain.from_iterable(x)))),'Fixed anchor not exact')
        check(x[0]==z,'Anchor changed')
        check(vnorm(x)==norm(z),'Parameter map not isometric')
    for y in parallel:
        x=[tuple(y[2*i:2*i+2]) for i in range(n)]
        check(x==reconstruct(frames,x[0]),'Global nullspace not reconstructed')
    for (i,j),K in loops.items():
        loop=paths[i]+[j]+list(reversed(paths[j]))[1:]
        check(path_matrix(loop,t)==K,'Root holonomy not actual loop transport')
        check(mm(K,transpose(K))==I,'Loop not an isometry')
    alt=routes(n,edges,True);AltT=[path_matrix(p,t) for p in alt];AltE=[transpose(a) for a in AltT]
    AltL=mat([[mm(mm(AltT[i],t[i,j]),AltE[j])[k][l]-I[k][l]
                for l in range(2)] for i,j in directed for k in range(2)])
    check(len(kernel(tuple(L)+tuple(AltL),2))==len(fixed),'Route-dependent fixed space')
    for z in fixed:check(reconstruct(frames,z)==reconstruct(AltE,z),'Feasible reconstruction route-dependent')
    for seed in range(8):
        x=[(Q(((i+1)*(seed+2))%11-5,2),Q((i*i+seed*3)%13-6,3)) for i in range(n)]
        dx=residual(x,t,directed); eps=vnorm(dx); y=reconstruct(frames,x[0])
        check(vnorm([sub(a,b) for a,b in zip(x,y)])<=radius*eps,'Routed estimate failed')
        root=vnorm([sub(mv(K,x[0]),x[0]) for K in loops.values()])
        check(root==vnorm(residual(y,t,directed)),'Residual normalization changed norm')
        check(root<=(2*radius+1)*eps,'Anchor loop estimate failed')
        for z in fixed or [(Q(0),Q(0))]:
            y=reconstruct(frames,z)
            check(vnorm([sub(a,b) for a,b in zip(x,y)])<=radius*eps+norm(sub(x[0],z)),
                  'Changed-anchor estimate failed')
            xx=list(x);xx[0]=z
            check(vnorm([sub(a,b) for a,b in zip(xx,y)])<=radius*vnorm(residual(xx,t,directed)),
                  'Feasible-anchor repair bound failed')
        counts['graph_candidates']+=1
    counts['connection_systems']+=1


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    start=time.monotonic();timestamp=dt.datetime.now(dt.timezone.utc).isoformat()
    counts={'connection_systems':0,'graph_candidates':0,'reflection_candidates':0};dimensions={}
    for n in range(3,8):
        cases=[[(i,i+1) for i in range(n-1)],[(0,i) for i in range(1,n)],
               [(i,i+1) for i in range(n-1)]+[(0,n-1)],list(it.combinations(range(n),2))]
        for edges in cases:
            for mode in range(6):audit_graph(n,edges,mode,counts,dimensions)
    edges=[(0,1),(0,2),(1,2)];t={(i,j):I for i,j in edges};t[0,2]=mat([[1,0],[0,-1]])
    t.update({(j,i):transpose(v) for (i,j),v in list(t.items())});directed=sorted(t)
    def repair(x):return [(x[0][0],Q(0))]*3
    for a in [(7,7,7),(7,8,6),(-2,1,3)]:
        for b in it.product(range(-2,3),repeat=3):
            x=[(Q(a[i]),Q(b[i],2)) for i in range(3)];y=repair(x)
            eps=vnorm(residual(x,t,directed));err=vnorm([sub(u,v) for u,v in zip(x,y)])
            check(err<=Q(3,2)*eps,'Sharp reflection bound violated')
            check(vnorm(residual(y,t,directed))==0,'Repair not exact')
            check(y[0][0]==x[0][0],'Protected coordinate changed')
            check(repair(y)==y,'Repair not idempotent')
            counts['reflection_candidates']+=1
    sharp=[(Q(7),Q(3,2)),(Q(7),Q(1,2)),(Q(7),Q(-1,2))]
    eps=vnorm(residual(sharp,t,directed));err=vnorm([sub(u,v) for u,v in zip(sharp,repair(sharp))])
    check(eps==1 and err==Q(3,2),'Sharp witness incorrect')
    reflection=mat([[1,0],[0,-1]])
    counterclaims=[
        ('every_anchor_survives_holonomy',mv(reflection,(Q(7),Q(1)))==(Q(7),Q(1))),
        ('nontrivial_holonomy_forces_zero_exact_core',vnorm(residual([(Q(7),Q(0))]*3,t,directed))!=0),
        ('reflection_repair_has_gain_one',err<=eps),
        ('order_of_noncommuting_path_factors_irrelevant',mm(GROUP[0],GROUP[5])==mm(GROUP[5],GROUP[0])),
    ]
    # Pick an explicit noncommuting pair, without depending on the enumeration order.
    pair=next((a,b) for a in GROUP for b in GROUP if mm(a,b)!=mm(b,a))
    counterclaims[-1]=(counterclaims[-1][0],mm(*pair)==mm(pair[1],pair[0]))
    for name,bad in counterclaims:check(not bad,'False-claim control accepted: '+name)
    out={'status':'PASS','started_at_utc':timestamp,'runtime_seconds':time.monotonic()-start,
         'python':platform.python_version(),'counts':counts,'fixed_space_dimensions':dimensions,
         'assertions':ASSERTIONS,'negative_controls':[{'claim':n,'rejected':not b} for n,b in counterclaims],
         'arithmetic':'fractions.Fraction; signed 2x2 permutation matrices; exact Gaussian elimination',
         'conventions':'t[i,j] maps j to i; A*B applies B then A; vertex/edge sup norms',
         'bounds':{'vertices':[3,4,5,6,7],'graph_shapes':['path','star','cycle','complete'],
                   'connection_fixtures_per_graph':6,'candidates_per_connection':8,
                   'reflection_horizontal_fixtures':3,'reflection_vertical_values':['-1','-1/2','0','1/2','1']},
         'randomness':{'used':False},'sharp_witness':{'residual_norm':'1','repair_error':'3/2'},
         'non_claims':['Finite fixtures do not enumerate all graphs, connections or vectors.',
                       'Universal claims come from Lean, not this computation.',
                       'No nonisometric, nonlinear or unknown-connection repair is tested.'],
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
