"""Exact finite checks for interpolation and the prepared FP response cache."""
import argparse,json,gc as gc_module
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import sympy as S
from cached_response import ResponseCache
from full_model import ElectronicModel
from float_certificate import certify_grid
from interval_certificate import endpoint,cell,evaluate,sqrt_upper
from blocked_action import apply as apply_blocked

def sf(x):return S.Rational(x.numerator,x.denominator)
def frac(x):
    x=S.cancel(x)
    if not x.is_Rational:raise ValueError('Expected exact real rational')
    return F(int(x.p),int(x.q))
def center(x):
    re,im=S.expand_complex(x).as_real_imag();return dict(real=str(frac(re)),imaginary=str(frac(im)))
def expr(p):return sf(F(p['real']))+S.I*sf(F(p['imaginary']))
def inside(value,p,radius):
    delta=S.expand_complex(value-expr(p));re,im=delta.as_real_imag()
    return frac(re)**2+frac(im)**2<=F(radius)**2

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True);identities=inclusions=0
    models=[(S.Matrix([[0]]),S.Matrix([1])),(S.Matrix([[S.Rational(1,2),S.Rational(1,8)],[S.Rational(1,8),S.Rational(-1,4)]]),S.Matrix([1,S.Rational(1,3)])),(S.Matrix([[1,S.I/4,S.Rational(1,5)],[-S.I/4,-1,S.Rational(1,7)],[S.Rational(1,5),S.Rational(1,7),0]]),S.Matrix([1,S.I/3,S.Rational(1,2)])),(S.eye(2),S.zeros(2,1))]
    perturb=sf(F(1,2**20))+S.I*sf(F(1,2**21));cap=F(3,2**21)
    for H,b in models:
        assert H==H.conjugate().T;I=S.eye(H.rows)
        for eta in [F(1,100),F(1,10),F(1,2)]:
            for width in [F(1,100),F(1,10),F(2)]:
                a=F(-1,3);c=a+width;za=sf(a)+S.I*sf(eta);zc=sf(c)+S.I*sf(eta)
                Ra=(za*I-H).inv();Rc=(zc*I-H).inv();ga=(b.conjugate().T*Ra*b)[0];gc=(b.conjugate().T*Rc*b)[0]
                segment=cell(endpoint(a,eta,center(ga+perturb),cap),endpoint(c,eta,center(gc-perturb),cap))
                for j in range(9):
                    t=F(j,8);E=a+t*width;R=((sf(E)+S.I*sf(eta))*I-H).inv();g=(b.conjugate().T*R*b)[0]
                    error=g-((1-sf(t))*ga+sf(t)*gc);product=(b.conjugate().T*Ra*R*Rc*b)[0]
                    assert S.simplify(error+sf(t*(1-t)*width**2)*product)==0;identities+=1
                    estimate=evaluate(segment,t);assert inside(g,estimate['center'],estimate['radius']);inclusions+=1
                    assert F(estimate['radius'])<=segment['uniform_radius_upper']
    # Hermiticity is indispensable: this real Jordan example has positive
    # endpoint strength but violates the proposed Hermitian interpolation bound.
    H=S.Matrix([[0,100],[0,0]]);b=S.Matrix([1,1]);I=S.eye(2);a=F(0);c=F(1,100);eta=F(1)
    g=lambda E:(b.T*((sf(E)+S.I)*I-H).inv()*b)[0]
    segment=cell(endpoint(a,eta,center(g(a)),0),endpoint(c,eta,center(g(c)),0));estimate=evaluate(segment,F(1,2))
    assert not inside(g((a+c)/2),estimate['center'],estimate['radius'])
    rng=np.random.default_rng(160920);fp=0;columns=0
    for n,sector in [(2,(1,1)),(3,(2,1)),(4,(2,1)),(4,(2,2))]:
        size=n*(n+1)//2;model=ElectronicModel(rng.integers(-4,5,size=(n,n))/16,rng.integers(-3,4,size=(size,size))/32,sector);model.prepare_float()
        masks=[a+(b<<n) for a in model.alpha for b in model.beta];cols=[model.column(m) for m in masks]
        H=S.Matrix(model.dimension,model.dimension,lambda i,j:S.Rational(cols[j].get(i,0),model.denominator))
        for j,exact_column in enumerate(cols):
            unit=np.zeros(model.dimension);unit[j]=1;image=apply_blocked(model,unit,block=7)
            error=sum((F(float(v))-F(exact_column.get(i,0),model.denominator))**2 for i,v in enumerate(image))
            assert error<=model.action_error_per_norm**2;columns+=1
        b=rng.integers(-2,3,size=model.dimension).astype(float)/4;Q=rng.normal(size=(model.dimension,3));Q[:,1]+=.2*Q[:,0]
        Y=np.column_stack([apply_blocked(model,Q[:,j],block=7) for j in range(3)]);cache=ResponseCache(model,Q,Y,b)
        energies=[F(-1,3),F(1,8)];etas=[F(1,100),F(1,10)];meta=dict(method='prepared-cache-audit',actions=3)
        records=cache.evaluate(energies,etas,meta);old=certify_grid(model,Q,Y,b,energies,etas,meta)
        qpath=(args.output/'mapped-q.bin').resolve();ypath=(args.output/'mapped-y.bin').resolve()
        assert qpath.parent==args.output.resolve() and ypath.parent==args.output.resolve()
        mq=np.memmap(qpath,dtype=float,mode='w+',shape=Q.shape);my=np.memmap(ypath,dtype=float,mode='w+',shape=Y.shape);mq[:]=Q;my[:]=Y;mq.flush();my.flush();del mq,my
        mq=np.memmap(qpath,dtype=float,mode='r',shape=Q.shape);my=np.memmap(ypath,dtype=float,mode='r',shape=Y.shape)
        mapped=ResponseCache(model,mq,my,b,copy=False);assert np.shares_memory(mapped.Q,mq) and np.shares_memory(mapped.Y,my)
        mapped_records=mapped.evaluate(energies,etas,meta)
        # Repeated calls must reuse the same prepared matrices and own immutable
        # copies, even if the caller subsequently changes its original arrays.
        qcopy=cache.Q.copy();Q[:]=0;Y[:]=0;b[:]=0
        assert np.array_equal(cache.Q,qcopy) and not cache.Q.flags.writeable
        assert records==cache.evaluate(energies,etas,meta)
        source=S.Matrix([sf(F(float(x))) for x in cache.source]);I=S.eye(model.dimension)
        for row,prior,mapped_row in zip(records,old,mapped_records):
            z=sf(F(row['ionic_energy']))+S.I*sf(F(row['eta']));actual=(source.T*(z*I-H).inv(method='DM')*source)[0]
            assert inside(actual,row['response_center'],row['radius_rational_upper'])
            assert inside(actual,prior['response_center'],prior['radius_rational_upper'])
            assert inside(actual,mapped_row['response_center'],mapped_row['radius_rational_upper']);fp+=2
        del mapped,mq,my;gc_module.collect();qpath.unlink();ypath.unlink()
    invalid=0
    for arguments in [(0,0,dict(real='0',imaginary='0'),0),(0,1,dict(real='0',imaginary='0'),-1),(0,1,dict(real='0',imaginary='1'),0)]:
        try:endpoint(*arguments)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid endpoint accepted')
    with np.load('research/computational-chemistry/stage15/inputs/h10_view.npz',allow_pickle=False) as data:full=ElectronicModel(data['h1'],data['eri'],(5,4))
    full.prepare_float()
    for mask in full.retained_masks():
        v=np.zeros(full.dimension);v[full.index(mask)]=1;image=apply_blocked(full,v);col=full.column(mask)
        error=sum((F(float(x))-F(col.get(i,0),full.denominator))**2 for i,x in enumerate(image));assert error<=full.action_error_per_norm**2
    result=dict(status='passed',seed=160920,exact_matrix_interpolation_identities=identities,exact_interpolation_disk_inclusions=inclusions,prepared_cache_exact_response_inclusions=fp,blocked_exact_small_columns=columns,blocked_exact_full_columns=9,source_array_mutation_isolated=True,prepared_state_reused=True,file_backed_arrays_reused_without_copy=True,invalid_endpoints_rejected=invalid,nonnormal_counterexample_checked=True,scope='Finite implementation checks; general interval theorem is established by the separate analytic proof, endpoint FP assumptions remain conditional')
    (args.output/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
