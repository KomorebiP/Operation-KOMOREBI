#!/usr/bin/env python3
"""Exact finite regression against an independent image-span/rational-free oracle.
This checks executions, not universal correctness of the Python proposer.
"""
from __future__ import annotations
import copy, hashlib, itertools, json, os, random, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import factor_affine as gen
OUT=ROOT/'results/v0.29.0/factor_tests';OUT.mkdir(parents=True,exist_ok=True)

def hmatmul(a,b):
    return [[sum(x*y for x,y in zip(row,col))%5 for col in zip(*b)] for row in a]

def homogeneous(p):
    n,m,_,_=gen.shape(p)
    if p[0]=='map':return [row+[bias] for row,bias in zip(p[3],p[4])]+[[0]*n+[1]]
    if p[0]=='id':return [[int(i==j) for j in range(n+1)] for i in range(n+1)]
    a=homogeneous(p[1]);b=homogeneous(p[2])
    if p[0]=='seq':return hmatmul(b,a)
    return [[(a[i][j]+b[i][j])%5 for j in range(n+1)] for i in range(m)]+[[0]*n+[1]]

def rank_by_image(a,n,m):
    span={(0,)*m};rank=0
    for j in range(n):
        col=tuple(a[i][j] for i in range(m))
        if col not in span:
            rank+=1;span={tuple((v[i]+t*col[i])%5 for i in range(m)) for v in span for t in range(5)}
    return rank

def execute(p,x):
    tag=p[0]
    if tag=='id':return x[:]
    if tag=='map':return [(sum(v*w for v,w in zip(row,x))+b)%5 for row,b in zip(p[3],p[4])]
    if tag=='seq':return execute(p[2],execute(p[1],x))
    return [(a+b)%5 for a,b in zip(execute(p[1],x),execute(p[2],x))]

def cost(p):
    n,m,_,_=gen.shape(p)
    if p[0]=='map':return m*(2*n+1)
    if p[0]=='id':return 0
    return cost(p[1])+cost(p[2])+(m if p[0]=='sum' else 0)

def check_charge(n,m,k):return (2*m*n*k+m*(2*k+1))+2*k*m*n+2*k*n*k+m*(n+1)+k*k

def certificate_valid(req):
    p=req[1];n,m,_,_=gen.shape(p);k,d,t,c,b,u,v=req[2]
    H=homogeneous(p);A=[row[:n] for row in H[:m]];off=[row[n] for row in H[:m]]
    return (all(sum(c[i][l]*d[l][j] for l in range(k))%5==A[i][j] for i in range(m) for j in range(n))
      and all((sum(c[i][l]*t[l] for l in range(k))+b[i])%5==off[i] for i in range(m))
      and all(sum(u[i][s]*A[s][t]*v[t][j] for s in range(m) for t in range(n))%5==int(i==j)
              for i in range(k) for j in range(k)))

def main():
    start=time.monotonic();rng=random.Random(20260913);requests=[];expect=[]
    def add_program(p,calls=100,oracle_rank=None):
        n,m,_,norm=gen.shape(p)
        xs=[list(x) for x in itertools.product(range(5),repeat=n)] if n<=2 else [[0]*n]+[[int(i==j) for i in range(n)] for j in range(n)]
        cfg=dict(program=p,calls=calls,credit=100000000,inputs=xs)
        req,meter=gen.prepare(cfg);assert req is not None
        mat=homogeneous(p);a=[row[:n] for row in mat[:m]]
        rank=rank_by_image(a,n,m) if oracle_rank is None else oracle_rank
        assert req[2][0]==rank
        requests.append(req);expect.append(dict(status='certified_minimum_width',rank=rank,p=p,n=n,m=m,normal=mat,calls=calls,norm=norm))
    # Every 2x2 matrix, deterministic varied offsets; not all affine maps of all shapes.
    for t,v in enumerate(itertools.product(range(5),repeat=4)):
        add_program(['map',2,2,[list(v[:2]),list(v[2:])],[t%5,(t//5)%5]],calls=(0,1,10,100)[t%4])
    # Rectangular and zero-dimensional maps, plus constructed ranks.
    for n in range(5):
        for m in range(5):
            for k in range(min(n,m)+1):
                c=[[int(i==j) if i<k else rng.randrange(5) for j in range(k)] for i in range(m)]
                d=[[int(i==j) if j<k else rng.randrange(5) for j in range(n)] for i in range(k)]
                a=[[sum(c[i][t]*d[t][j] for t in range(k))%5 for j in range(n)] for i in range(m)]
                add_program(['map',n,m,a,[rng.randrange(5) for _ in range(m)]],oracle_rank=k)
    # Wider known-rank witnesses; independent semantic checks remain exact.
    for n,m,k in [(8,8,1),(8,8,8),(8,3,3),(2,8,2),(0,8,0),(8,0,0)]:
        a=[[int(i==j and i<k) for j in range(n)] for i in range(m)]
        add_program(['map',n,m,a,[i%5 for i in range(m)]],oracle_rank=k)
    for i in range(60):
        n,k,m=[rng.randrange(1,5) for _ in range(3)]
        def atom(a,b):return ['map',a,b,[[rng.randrange(5) for _ in range(a)] for _ in range(b)],[rng.randrange(5) for _ in range(b)]]
        p=['seq',atom(n,k),atom(k,m)]
        if i%3==0:p=['sum',p,atom(n,m)]
        add_program(p,calls=i)
    for n in range(9):add_program(['id',n],oracle_rank=n)
    for name in ['rank_one','rank_one_short','constant','fusion','bottleneck','identity']:
        cfg=json.loads((ROOT/f'examples/factorization/{name}.json').read_text());add_program(cfg['program'],cfg['calls'])
    valid_count=len(requests)
    # Nonzero affine first biases: the second bias must compensate exactly.
    for index in range(0,625,25):
        req=copy.deepcopy(requests[index]);c=req[2];k=c[0]
        t=[(j+1)%5 for j in range(k)];c[2]=t
        c[4]=[(c[4][i]-sum(c[3][i][j]*t[j] for j in range(k)))%5 for i in range(req[1][2])]
        requests.append(req);expect.append(copy.deepcopy(expect[index]))
    offset_variants=len(requests)-valid_count
    # Forged upper/lower witnesses and wrong offset.
    for index in range(1,625,17):
        req=copy.deepcopy(requests[index]);c=req[2];k=c[0]
        if k==0:continue
        for field,row,col in [(1,0,0),(5,0,0),(6,0,0)]:
            bad=copy.deepcopy(req);bad[2][field][row][col]=(bad[2][field][row][col]+1)%5
            requests.append(bad);expect.append(copy.deepcopy(expect[index]) if certificate_valid(bad) else {'status':'rejected_certificate'})
        bad=copy.deepcopy(req);bad[2][4][0]=(bad[2][4][0]+1)%5
        requests.append(bad);expect.append(copy.deepcopy(expect[index]) if certificate_valid(bad) else {'status':'rejected_certificate'})
    # Credit below the checker reservation is not a 'bad certificate' result.
    for index in range(0,625,41):
        req=copy.deepcopy(requests[index]);n,m,_,norm=gen.shape(req[1]);fee=check_charge(n,m,req[2][0])
        req[5]=norm+req[4]+fee-1
        requests.append(req);expect.append({'status':'unfunded_certificate'})
    bads=[]
    seed=copy.deepcopy(requests[1])
    bad=copy.deepcopy(seed);bad[0]='unknown';bads.append(bad)
    bad=copy.deepcopy(seed);bad[2][0]=9;bads.append(bad)
    bad=copy.deepcopy(seed);bad[2][5]=[];bads.append(bad)
    bad=copy.deepcopy(seed);bad[2][2]=[0,0,0];bads.append(bad)
    bad=copy.deepcopy(seed);bad[2][1][0][0]=5;bads.append(bad)
    bad=copy.deepcopy(seed);bad[3]=True;bads.append(bad)
    bad=copy.deepcopy(seed);bad[3]=-1;bads.append(bad)
    bad=copy.deepcopy(seed);bad[3]=1.25;bads.append(bad)
    bad=copy.deepcopy(seed);bad[6]=[[0]];bads.append(bad)
    bad=copy.deepcopy(seed);bad[1]=['seq',['id',2],['id',3]];bads.append(bad)
    for b in bads:requests.append(b);expect.append({'status':'error'})
    lean,env=gen.environment();outputs=[];runs=[]
    for start_i in range(0,len(requests),128):
        path=OUT/f'requests_{start_i:04d}.json';path.write_text(json.dumps(requests[start_i:start_i+128]))
        cmd=[str(lean),'--run',str(ROOT/'tools/AffineFactorMain.lean'),'--batch',str(path)]
        t=time.monotonic();p=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=90)
        (OUT/f'output_{start_i:04d}.jsonl').write_text(p.stdout)
        (OUT/f'stderr_{start_i:04d}.txt').write_text(p.stderr)
        assert p.returncode==0,p.stderr
        rows=[json.loads(line) for line in p.stdout.splitlines()];assert len(rows)==len(requests[start_i:start_i+128])
        outputs.extend(rows);runs.append(dict(command=cmd,returncode=p.returncode,seconds=time.monotonic()-t,input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(p.stdout.encode()).hexdigest()))
    vectors=0;counts={}
    for i,(req,e,out) in enumerate(zip(requests,expect,outputs)):
        assert out['status']==e['status'],(i,e,out)
        counts[out['status']]=counts.get(out['status'],0)+1
        if e['status']!='certified_minimum_width':continue
        n=e['n'];m=e['m'];k=e['rank'];mat=e['normal'];p=e['p']
        assert out['rank']==k
        assert out['normal']['matrix']==[row[:n] for row in mat[:m]]
        assert out['normal']['offset']==[row[n] for row in mat[:m]]
        cmin=min(cost(p),m*(2*n+1),k*(2*n+1)+m*(2*k+1))
        assert out['per_call_selected']==cmin
        assert cost(out['selected'])==cmin
        fee=check_charge(n,m,k);spent=e['norm']+req[4]+fee
        assert out['spent']==spent and out['spent']+out['remaining']==req[5]
        assert out['campaign_total']==spent+req[3]*cmin
        assert out['net_gain']==req[3]*(cost(p)-cmin)-spent
        assert out['breaks_even']==(out['net_gain']>=0)
        for x,y in zip(req[6],out['outputs']):
            assert y==execute(p,x)==execute(out['selected'],x);vectors+=1
    # Explicit generator-credit and wrapper validation cases.
    for budget in range(0,30):
        req,meta=gen.prepare(dict(program=['map',2,2,[[1,2],[3,4]],[0,0]],credit=budget,calls=5))
        assert meta['spent']<=budget
    wrapper_rejections=0
    for badcfg in [dict(program=['id',True]),dict(program=['id',2],calls=1.5),dict(program=['id',2],credit=-1),dict(program=['id',2],unknown=3)]:
        try:gen.prepare(badcfg)
        except ValueError:wrapper_rejections+=1
        else:raise AssertionError('bad config accepted')
    summary=dict(passed=True,seed=20260913,requests=len(requests),statuses=counts,
        all_2x2_matrices=625,valid_base_programs=valid_count,nonzero_offset_variants=offset_variants,
        vector_comparisons=vectors,generation_budget_cases=30,wrapper_validation_rejections=wrapper_rejections,
        seconds=time.monotonic()-start,runs=runs,oracle='homogeneous matrices; exact column-image span cardinality; independent AST execution',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256((ROOT/'tools/factor_affine.py').read_bytes()).hexdigest())
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
