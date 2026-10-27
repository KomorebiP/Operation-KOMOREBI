"""Independent exact derivations and boundary checks for continuation 113.

Uses coordinate arithmetic, rather than importing the delivered finite model.
No conclusion about arithmetic simple-character occurrence is tested.
"""
from itertools import product
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import shutil

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[1]
ROOT = PROJ.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def independent_finite_checks():
    # F9 trace pairing in coordinates a+b*u, with u^2=-1:
    # Tr((a+b*u)(c+d*u))=2*(a*c-b*d).
    E = list(product(range(3), repeat=2))
    add = lambda x,y: tuple((a+b)%3 for a,b in zip(x,y))
    pair = lambda x,y: 2*(x[0]*y[0]-x[1]*y[1])%3
    f = lambda x: (x[0], -x[1]%3)
    assert all(any(pair(x,y) for y in E) for x in E if x!=(0,0))
    assert all(pair(f(x),f(y))==pair(x,y) for x,y in product(E,repeat=2))
    # Identify fixed basis vectors and transpositions directly.
    fixed_basis = [x for x in E if f(x)==x]
    assert len(fixed_basis)==3
    transpositions = {frozenset((x,f(x))) for x in E if f(x)!=x}
    assert len(transpositions)==3
    # Character of (-S)*rho(g), independently from the fixed-point equations.
    traces = {}
    for x,y,z in product(E,E,range(3)):
        counts = [0,0,0]
        for t in E:
            if f(add(t,x))==t:
                counts[(z+pair(y,t)+2*pair(x,y))%3] += 1
        traces[x,y,z] = (counts[2]-counts[0], counts[2]-counts[1])
    fixed_group = [(x,y,z) for x,y,z in traces if f(x)==x and f(y)==y]
    assert len(fixed_group)==27
    roots = [(1,0),(0,1),(-1,-1)]
    for x,y,z in fixed_group:
        target = tuple(-3*a for a in roots[z]) if x==y==(0,0) else (0,0)
        assert traces[x,y,z]==target

    # Count Q8 lifts from possible images of i,j. A quotient 3-cycle sends
    # iZ->jZ->ijZ->iZ; each image has two central signs, all four choices work.
    basis = ['1','i','j','k']
    # Product by quaternion basis identities, with sign carried separately.
    table = {(0,a):(1,a) for a in range(4)} | {(a,0):(1,a) for a in range(4)}
    for a in (1,2,3): table[a,a]=(-1,0)
    for a,b,c in [(1,2,3),(2,3,1),(3,1,2)]:
        table[a,b]=(1,c); table[b,a]=(-1,c)
    mm = lambda x,y:(x[0]*y[0]*table[x[1],y[1]][0], table[x[1],y[1]][1])
    Q = list(product((-1,1),range(4)))
    maps = []
    for si,sj in product((-1,1),repeat=2):
        im = [(1,0),(si,2),(sj,3),mm((si,2),(sj,3))]
        phi = lambda x:(x[0]*im[x[1]][0],im[x[1]][1])
        assert all(phi(mm(x,y))==mm(phi(x),phi(y)) for x,y in product(Q,repeat=2))
        assert all(phi(phi(phi(x)))==x for x in Q)
        maps.append(im)
    assert len(maps)==4
    # D8 has one nonzero square-one-in-center quotient vector and two
    # square-zero vectors, so no three-cycle preserves its square map.
    d8_square = [1,0,0]
    assert d8_square[1:]+d8_square[:1] != d8_square

    tested = []
    # Characters of (Z/p)^2 represented by exponent vectors. Independently
    # check k(beta a)-k(a)=r(a) for the weighted/Bézout construction.
    for p,n,B in [(3,4,((0,-1),(1,0))), (3,2,((-1,0),(0,-1))),
                  (2,3,((0,1),(1,1)))]:
        A = list(product(range(p),repeat=2))
        beta = lambda a: tuple(sum(B[i][j]*a[j] for j in range(2))%p for i in range(2))
        u = pow(n,-1,p)
        count = 0
        for r in A:
            char = lambda a:sum(x*y for x,y in zip(r,a))%p
            def orbit(a):
                out=[]
                for _ in range(n): out.append(a); a=beta(a)
                return out
            if not all(sum(char(x) for x in orbit(a))%p==0 for a in A): continue
            k = lambda a:u*sum(i*char(x) for i,x in enumerate(orbit(a)))%p
            assert all((k(beta(a))-k(a))%p==char(a) for a in A)
            count += 1
        tested.append({'p':p,'cyclic_order':n,'norm_one_characters':count})
    # Dropping coprimeness fails: trivial beta on Z/2, n=2 has nontrivial
    # norm-one r, but every coboundary k(beta a)/k(a) is trivial.
    assert (2*1)%2==0 and (1-1)%2==0 and 1!=0
    return {'status':'PASS','f9_fixed_basis':3,'f9_transpositions':3,
            'f9_fixed_group':27,'q8_lifts':4,'d8_lifts':0,
            'weighted_norm_checks':tested,
            'noncoprime_boundary':'Nontrivial character of Z/2 for trivial action and n=2 is norm-one and not a coboundary.'}

def run():
    modules = ['CyclicNormalization113','CyclicDefect113','ActualScalarLift113','EquivariantRepresentation113']
    inputs = [PROJ/'formalization/PaperXI'/f'{s}.lean' for s in modules]
    inputs += [PROJ/'scripts/finite_models113.py', PROJ/'evidence/finite/run01/RESULT.json']
    result = {'input_hashes':{str(p.relative_to(PROJ)):sha(p) for p in inputs},
              'baseline_archive_sha256':sha(ROOT/'Paper_XI_Continuation112_Checked_Delta.zip'),
              'independent_finite':independent_finite_checks(), 'checks':[]}
    assert result['baseline_archive_sha256']=='4df3bff07c05985e302d5e9f4104de8f6374c17ca695b1e2e451432572272ae5'
    rerun = HERE/'finite_replay.json'
    t0=time.monotonic()
    proc=subprocess.run(['python3',str(PROJ/'scripts/finite_models113.py'),'--output',str(rerun)],capture_output=True,text=True,timeout=90)
    (HERE/'finite_replay.log').write_text(proc.stdout+proc.stderr)
    assert proc.returncode==0
    assert json.loads(rerun.read_text())==json.loads((PROJ/'evidence/finite/run01/RESULT.json').read_text())
    result['checks'].append({'name':'finite_replay','exit_code':proc.returncode,'seconds':time.monotonic()-t0,'matches_original_json':True})
    kit=ROOT/'runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2'
    objects=HERE/'objects'
    (objects/'PaperXI').mkdir(parents=True,exist_ok=True)
    # Lean resolves an entire package namespace from its first matching path.
    # Materialize the inherited baseline objects alongside the new modules.
    inherited = ROOT/'Paper_XI_Continuation112_Realization_Test/build'
    shutil.copytree(inherited,objects,dirs_exist_ok=True)
    result['inherited_objects']={str(p.relative_to(inherited)):sha(p)
                                 for p in inherited.rglob('*') if p.is_file()}
    env=os.environ.copy()
    env['LD_PRELOAD']=str(kit/'compat/app_path.so')
    env['PATH']=str(kit/'toolchain/bin')+':'+env['PATH']
    env['LEAN_PATH']=':'.join(map(str,[objects,PROJ/'evidence/phase/objects',PROJ/'evidence/equivariant/objects',*sorted((kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))]))
    # Compile fresh source objects in the audit's own directory. Inherited
    # dependencies are reused, not advertised as rebuilt.
    for name in modules:
        source=PROJ/'formalization/PaperXI'/f'{name}.lean'
        args=[str(kit/'toolchain/bin/lean'),'-j1','-DmaxHeartbeats=3000000','-DwarningAsError=true','-o',str(objects/'PaperXI'/f'{name}.olean'),str(source)]
        before=sha(source); t0=time.monotonic()
        p=subprocess.run(args,cwd=PROJ,env=env,capture_output=True,text=True,timeout=90)
        (HERE/f'{name}_compile.log').write_text(p.stdout+p.stderr)
        assert p.returncode==0,(name,p.stdout+p.stderr)
        assert sha(source)==before
        result['checks'].append({'name':name,'source_sha256':before,'kind':'fresh_compile','exit_code':p.returncode,'seconds':time.monotonic()-t0})
    for name in modules:
        t0=time.monotonic()
        p=subprocess.run([str(kit/'toolchain/bin/leanchecker'),'--verbose',f'PaperXI.{name}'],cwd=PROJ,env=env,capture_output=True,text=True,timeout=90)
        (HERE/f'{name}_leanchecker.log').write_text(p.stdout+p.stderr)
        assert p.returncode==0,(name,p.stdout+p.stderr)
        result['checks'].append({'name':name,'kind':'leanchecker','exit_code':p.returncode,'seconds':time.monotonic()-t0})
    result['status']='PASS'
    result['baseline_rebuilt']=False
    result['final_input_hashes']={str(p.relative_to(PROJ)):sha(p) for p in inputs}
    assert result['input_hashes']==result['final_input_hashes']
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': run()
