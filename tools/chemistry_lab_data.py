"""Build bounded, exact browser fixtures from the sealed Stage 14 export.

Standard-library rational implementation, separate from the SymPy decoder.
Run: python -B tools/chemistry_lab_data.py [--check]
"""
from fractions import Fraction as Q
from itertools import combinations
import argparse
import hashlib
import json
from pathlib import Path

from computational_chemistry import load

ROOT = Path(__file__).resolve().parents[1]
DATA = 'website/assets/chemistry/lab-v1.json'


def transpose(a): return list(map(list, zip(*a)))
def eye(n): return [[Q(i == j) for j in range(n)] for i in range(n)]
def mm(a, b): return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def plus(a, b, scale=1): return [[x+scale*y for x,y in zip(r,s)] for r,s in zip(a,b)]
def flatten(a): return [x for row in a for x in row]
def strings(a):
    return [strings(x) if isinstance(x,list) else str(x) for x in a]


def rref(a, columns=None):
    a = [list(map(Q,row)) for row in a]; pivots=[]; target=0
    for j in range(columns if columns is not None else len(a[0])):
        pivot=next((i for i in range(target,len(a)) if a[i][j]),None)
        if pivot is None: continue
        a[target],a[pivot]=a[pivot],a[target]
        d=a[target][j]; a[target]=[x/d for x in a[target]]
        for i in range(len(a)):
            if i != target and a[i][j]:
                d=a[i][j]; a[i]=[x-d*y for x,y in zip(a[i],a[target])]
        pivots.append(j); target+=1
        if target == len(a): break
    return a,pivots


def inverse(a):
    n=len(a); rows,pivots=rref([r+s for r,s in zip(a,eye(n))],n)
    assert len(pivots)==n
    return [r[n:] for r in rows]


def combine(basis, theta):
    return [[sum(theta[k]*basis[k][i][j] for k in range(21)) for j in range(9)] for i in range(9)]


def normal_model():
    t=[[[Q(0) for _ in range(3)] for _ in range(3)] for _ in range(5)]
    for i,v in enumerate([1,-1,0]): t[0][i][i]=Q(v)
    for i,v in enumerate([1,1,-2]): t[1][i][i]=Q(v)
    for a,(i,j) in enumerate([(0,1),(0,2),(1,2)],2): t[a][i][j]=t[a][j][i]=Q(1)
    ad=[[[a[i//3][j//3]*(i%3==j%3)-(i//3==j//3)*a[j%3][i%3] for j in range(9)] for i in range(9)] for a in t]
    normal=[eye(9)]+ad
    labels=['scalar']+['K'+str(i+1) for i in range(5)]
    for a in range(5):
        for b in range(a,5):
            normal.append(mm(ad[a],ad[b]) if a==b else plus(mm(ad[a],ad[b]),mm(ad[b],ad[a])))
            labels.append('C'+str(a+1)+str(b+1))
    # Determinants: alpha pairs (01,02,12), each followed by beta 0,1,2.
    change=[[Q(0) for _ in range(9)] for _ in range(9)]
    pairs=list(combinations(range(3),2))
    for i in range(3):
        row=pairs.index(tuple(q for q in range(3) if q!=i))
        for j in range(3): change[3*row+j][3*i+j]=Q((-1)**i)
    return [mm(mm(change,h),transpose(change)) for h in normal],labels


def response(h, b, energy, eta):
    # Solve the real 18x18 system for (zI-H)^-1 b with exact fractions.
    a=plus([[energy*x for x in row] for row in eye(9)],h,-1)
    rows=[a[i]+[-eta*x for x in eye(9)[i]]+[b[i]] for i in range(9)]
    rows += [[eta*x for x in eye(9)[i]]+a[i]+[Q(0)] for i in range(9)]
    solved,pivots=rref(rows,18); assert len(pivots)==18
    real=[r[-1] for r in solved[:9]]; imag=[r[-1] for r in solved[9:]]
    assert [sum(a[i][j]*real[j] for j in range(9))-eta*imag[i] for i in range(9)]==b
    assert all(sum(a[i][j]*imag[j] for j in range(9))+eta*real[i]==0 for i in range(9))
    return dict(real=str(sum(x*y for x,y in zip(b,real))),imaginary=str(sum(x*y for x,y in zip(b,imag))),solution_real=strings(real),solution_imaginary=strings(imag))


def build():
    record,files=load(ROOT); basis,labels=normal_model()
    probes=[[Q(v) for v in row] for row in json.loads(files['chemistry_stage14/probes.json'])['queries']]
    m=transpose([flatten(mm(h,probes)) for h in basis]); mt=transpose(m)
    left=mm(inverse(mm(mt,m)),mt); assert mm(left,m)==eye(21)
    stages=[]
    for count in [1,2,3]:
        reduced,pivots=rref([m[3*i+j] for i in range(9) for j in range(count)])
        free=next((j for j in range(21) if j not in pivots),None)
        witness=[Q(0)]*21
        if free is not None:
            witness[free]=Q(1)
            for i,j in enumerate(pivots): witness[j]=-reduced[i][free]
        delta=combine(basis,witness)
        assert all(x==0 for row in mm(delta,[r[:count] for r in probes]) for x in row)
        assert any(flatten(delta)) if count<3 else not any(flatten(delta))
        stages.append(dict(count=count,rank=len(pivots),nullity=21-len(pivots),witness_theta=strings(witness),witness_operator=strings(delta)))
    samples=[]
    for key,title,path in [('exact','Exact rational example','chemistry_stage14/example_cache.json'),('h10','H10-derived reduced model','chemistry_stage14/molecular-audit-001/molecular_cache.json')]:
        data=json.loads(files[path]); data['action_matrix']=[[str(Q(x)) for x in row] for row in data['action_matrix']]
        cert_path='chemistry_stage14/'+('exact-audit-001/example_certificate.json' if key=='exact' else 'molecular-audit-001/molecular_certificate.json')
        samples.append(dict(id=key,title=title,cache=data,saved_certificate=json.loads(files[cert_path]),source_path=path,source_sha256=hashlib.sha256(files[path]).hexdigest(),certificate_path=cert_path))
    toy=samples[0]['cache']
    def synthetic(key,title,theta,epsilon):
        h=combine(basis,theta)
        return dict(id=key,title=title,cache=dict(action_matrix=strings(mm(h,probes)),b_hat=toy['b_hat'],raw_error_radius=epsilon,source_radius='0',energy='0',eta='1/100'),source_path=None)
    samples.append(synthetic('zero','Zero operator: a boundary case',[Q(0)]*21,'1/4096'))
    negative=[Q(0)]*21; negative[6]=Q(-1,64)
    samples.append(synthetic('unresolved','Negative interaction estimate',[*negative],'1/4096'))
    inconsistent=synthetic('inconsistent','Actions outside the model',[Q(x) for x in samples[0]['saved_certificate']['theta']],'1/4096')
    # A nonzero vector in the orthogonal complement of the action image.
    projection=mm(m,left)
    column=next(j for j in range(27) if projection[j][j]!=1)
    residual=[Q(i==column)-projection[i][column] for i in range(27)]
    assert all(sum(left[k][i]*residual[i] for i in range(27))==0 for k in range(21))
    y=flatten([[Q(x) for x in row] for row in inconsistent['cache']['action_matrix']])
    y=[v+w/64 for v,w in zip(y,residual)]
    inconsistent['cache']['action_matrix']=strings([y[3*i:3*i+3] for i in range(9)])
    samples.append(inconsistent)
    etas=['1/1000','1/100','1/10','1/2','1']
    for sample in samples:
        cache=sample['cache']; y=[Q(x) for row in cache['action_matrix'] for x in row]
        theta=[sum(x*v for x,v in zip(row,y)) for row in left]; h=combine(basis,theta)
        sample['theta']=strings(theta); sample['estimated_H']=strings(h)
        d2=sum((x-y)**2 for x,y in zip(y,flatten(mm(h,probes))))
        sample['residual_squared']=str(d2)
        sample['responses']={eta:response(h,list(map(Q,cache['b_hat'])),Q(cache['energy']),Q(eta)) for eta in etas}
        if sample.get('saved_certificate'):
            cert=sample['saved_certificate']; assert strings(h)==cert['estimated_H']
            assert str(d2)==cert['least_squares_residual_squared']
            assert sample['responses'][cache['eta']]['real']==cert['response_center']['real']
            assert sample['responses'][cache['eta']]['imaginary']==cert['response_center']['imaginary']
    return dict(version=1,archive_sha256=record['sha256'],basis=strings(basis),labels=labels,probes=strings(probes),left_inverse=strings(left),stages=stages,etas=etas,samples=samples,
                scope='Exact finite fixtures for the declared 21-dimensional real integral-symmetry family; no full-molecule accuracy or Coulomb realizability claim.')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    raw=(json.dumps(build(),separators=(',',':'))+'\n').encode(); target=ROOT/DATA
    if args.check:
        if target.read_bytes()!=raw: raise ValueError('Stale chemistry lab fixtures')
    else:
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw)
    print(json.dumps(dict(status='passed',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),examples=5,response_cases=25)))


if __name__=='__main__': main()
