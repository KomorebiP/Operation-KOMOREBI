#!/usr/bin/env python3
"""Independent exact GF(5) regression against executed Lean.
Oracle normalization uses homogeneous augmented matrices; execution walks the AST.
"""
from __future__ import annotations
import hashlib, itertools, json, random, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RD = ROOT/'results/v0.28.0/affine_tests'
RD.mkdir(parents=True,exist_ok=True)
rng = random.Random(20260913)

def sig(p):
    tag = p[0]
    if tag == 'map':
        _,n,m,a,b=p
        return n,m,[list(a[i])+[b[i]] for i in range(m)]+[[0]*n+[1]]
    if tag == 'id':
        n=p[1]
        return n,n,[[int(i==j) for j in range(n+1)] for i in range(n+1)]
    if tag == 'seq':
        n,m,a=sig(p[1]); l,k,b=sig(p[2]); assert m==l
        return n,k,[[sum(b[i][t]*a[t][j] for t in range(m+1))%5 for j in range(n+1)] for i in range(k+1)]
    n,m,a=sig(p[1]); n2,m2,b=sig(p[2]); assert (n,m)==(n2,m2)
    return n,m,[[(a[i][j]+b[i][j])%5 for j in range(n+1)] for i in range(m)]+[[0]*n+[1]]

def run(p,x):
    if p[0]=='map':
        return [(sum(ai*v for ai,v in zip(row,x))+b)%5 for row,b in zip(p[3],p[4])]
    if p[0]=='id': return list(x)
    if p[0]=='seq': return run(p[2],run(p[1],x))
    return [(a+b)%5 for a,b in zip(run(p[1],x),run(p[2],x))]

def costs(p):
    n,m,_=sig(p)
    if p[0]=='map':return m*(2*n+1),0
    if p[0]=='id':return 0,0
    a,c=costs(p[1]);b,d=costs(p[2])
    if p[0]=='sum':return a+b+m,c+d+m*(n+1)
    mid=sig(p[1])[1]
    return a+b,c+d+2*m*n*mid+m*(2*mid+1)

def gen(n,m,depth):
    if not depth or rng.random()<0.4:
        if n==m and rng.random()<0.15:return ['id',n]
        return ['map',n,m,[[rng.randrange(5) for _ in range(n)] for _ in range(m)],[rng.randrange(5) for _ in range(m)]]
    if rng.random()<0.6:
        k=rng.randrange(4)
        return ['seq',gen(n,k,depth-1),gen(k,m,depth-1)]
    return ['sum',gen(n,m,depth-1),gen(n,m,depth-1)]

def atom_sig(p):
    n,m,a=sig(p);return ['map',n,m,[r[:-1] for r in a[:-1]],[r[-1] for r in a[:-1]]]

queries=[]; expected=[]
# All 625 pairs of affine scalar GF(5) maps.
scalars=[['map',1,1,[[a]],[b]] for a in range(5) for b in range(5)]
for p,q in itertools.product(scalars,repeat=2):
    eq=all(run(p,[x])==run(q,[x]) for x in range(5))
    queries.append(['affine-compare-f5-v1',p,q]);expected.append(('compare',eq))
# Exhaustive input vectors for each seeded dimension-typed random program.
vector_checks=0; normal_cases=0
for idx in range(180):
    n=idx%4;m=(idx//4)%4;p=gen(n,m,3);calls=idx%9
    xs=[list(x) for x in itertools.product(range(5),repeat=n)]
    out=[run(p,x) for x in xs];vector_checks+=len(xs);normal_cases+=1
    norm=atom_sig(p);evalcost,compilecost=costs(p)
    queries.append(['affine-normalize-f5-v1',p,calls,xs])
    expected.append(('normalize',dict(n=n,m=m,matrix=norm[3],offset=norm[4],outputs=out,
        evalcost=evalcost,compilecost=compilecost,calls=calls)))
    queries.append(['affine-compare-f5-v1',p,norm]);expected.append(('compare',True))
    if m:
        altered=json.loads(json.dumps(norm));altered[4][0]=(altered[4][0]+1)%5
        queries.append(['affine-compare-f5-v1',p,altered]);expected.append(('compare',False))
# Wider dimensions are sampled, not exponentially enumerated.
for n,m in [(8,8),(8,0),(0,8),(5,3),(4,6)]:
    p=['map',n,m,[[rng.randrange(5) for _ in range(n)] for _ in range(m)],[rng.randrange(5) for _ in range(m)]]
    xs=[[rng.randrange(5) for _ in range(n)] for _ in range(20)]
    ec,cc=costs(p);normal_cases+=1;vector_checks+=len(xs)
    queries.append(['affine-normalize-f5-v1',p,4,xs]);expected.append(('normalize',dict(n=n,m=m,matrix=p[3],offset=p[4],outputs=[run(p,x) for x in xs],evalcost=ec,compilecost=cc,calls=4)))
invalid=[
 ['affine-normalize-f5-v1',['seq',['id',2],['id',3]],1,[]],
 ['affine-normalize-f5-v1',['sum',['id',2],['id',3]],1,[]],
 ['affine-normalize-f5-v1',['map',1,1,[[1,2]],[0]],1,[]],
 ['affine-normalize-f5-v1',['map',1,1,[],[0]],1,[]],
 ['affine-normalize-f5-v1',['map',1,1,[[1]],[]],1,[]],
 ['affine-normalize-f5-v1',['map',1,1,[[5]],[0]],1,[]],
 ['affine-normalize-f5-v1',['map',1,1,[[-1]],[0]],1,[]],
 ['affine-normalize-f5-v1',['map',1,1,[[True]],[0]],1,[]],
 ['affine-normalize-f5-v1',['map',1,1,[[1.5]],[0]],1,[]],
 ['affine-normalize-f5-v1',['id',9],1,[]],
 ['affine-normalize-f5-v1',['id',1],1,[[0,0]]],
 ['affine-normalize-f5-v1',['square',['id',1]],1,[]],
 ['affine-normalize-f5-v1',['id',1],1000001,[]],
 ['affine-compare-f5-v1',['id',1],['id',2]],
 ['affine-normalize-f5-v1',['id',0],1,[], 'extra'],
]
for q in invalid:queries.append(q);expected.append(('error',None))
files=[ROOT/f'AVOC/{x}.lean' for x in ['AffineSignature','TypedAffineProgram','AffineFusion','AffineExamples','AffineCodec']]+[ROOT/'tools/AffineMain.lean',ROOT/'tools/run_affine.py',Path(__file__)]
hashbefore={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
start=time.monotonic(); invocations=[]; replies=[]
for b in range(0,len(queries),128):
    f=RD/f'requests_{b//128:02}.json';f.write_text(json.dumps(queries[b:b+128],separators=(',',':'))+'\n')
    cmd=[sys.executable,str(ROOT/'tools/run_affine.py'),str(f),'--batch','--timeout','60']
    t=time.monotonic();p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=65)
    (RD/f'replies_{b//128:02}.jsonl').write_text(p.stdout)
    (RD/f'stderr_{b//128:02}.txt').write_text(p.stderr)
    invocations.append(dict(command=cmd,returncode=p.returncode,seconds=time.monotonic()-t))
    assert p.returncode==0,p.stderr
    rs=[json.loads(line) for line in p.stdout.splitlines()]
    assert len(rs)==len(queries[b:b+128]);replies+=rs
for i,(r,(kind,e)) in enumerate(zip(replies,expected)):
    if kind=='error':assert r['status']=='error',(i,r)
    elif kind=='compare':assert r.get('equivalent')==e,(i,r,e)
    else:
        n,m,calls=e['n'],e['m'],e['calls'];fuse=m*(2*n+1)
        assert r['normal']==dict(input_dim=n,output_dim=m,matrix=e['matrix'],offset=e['offset']),(i,r,e)
        assert r['outputs']==r['normal_outputs']==e['outputs'],(i,r,e)
        assert (r['per_call_original'],r['normalization_charge'],r['per_call_fused'])==(e['evalcost'],e['compilecost'],fuse),(i,r,e)
        assert r['basis_probe_count']==n+1 and r['coefficient_count']==m*(n+1)
        assert r['fused_lifecycle_charge']==e['compilecost']+calls*fuse
        assert r['baseline_deployment_charge']==calls*e['evalcost']
        assert r['fuse_breaks_even_including_normalization']==(e['compilecost']+calls*fuse<=calls*e['evalcost'])
hashafter={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert hashbefore==hashafter
summary=dict(status='PASS',seed=20260913,arithmetic='exact GF(5)',requests=len(queries),
 normalization_cases=normal_cases,scalar_pair_comparisons=625,comparison_cases=sum(k=='compare' for k,e in expected),
 vector_input_comparisons=vector_checks,invalid_requests=len(invalid),seconds=time.monotonic()-start,
 source_hashes=hashbefore,source_unchanged=True,invocations=invocations,
 boundaries=['Seeded program sample, not all ASTs','Exhaustive input vectors only for each sampled program with input dimension <= 3','Higher dimensions use 20 input samples; generic Lean proofs cover all dimensions and inputs','Python IO adapter is tested, not universally refined'])
(RD/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['invocations','source_hashes']},indent=2))
