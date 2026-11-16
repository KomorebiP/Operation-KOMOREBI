"""Exact small-model checks for the matrix-free kernel and FP certificates."""
import argparse
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import numpy as np
import sympy as S
from full_model import ElectronicModel,masks,sqrt_upper
from float_certificate import certify_grid
from audit_reduction import residual_certificate


def scomplex(z):return S.Rational(F(float(z.real)).numerator,F(float(z.real)).denominator)+S.I*S.Rational(F(float(z.imag)).numerator,F(float(z.imag)).denominator)
def sr(x):return S.Rational(x.numerator,x.denominator)
def exact_error_squared(vector,column,denominator):
    total=F(0)
    for i,x in enumerate(vector):total+=(F(float(x))-F(column.get(i,0),denominator))**2
    return total


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True);rng=np.random.default_rng(150916);columns=0;responses=0;identities=0
    assert masks(4,2)==[3,5,6,9,10,12]
    for n,sector in [(2,(1,1)),(3,(2,1)),(4,(2,1)),(4,(2,2))]:
        size=n*(n+1)//2
        hraw=rng.integers(-4,5,size=(n,n))/16
        graw=rng.integers(-3,4,size=(size,size))/32
        model=ElectronicModel(hraw,graw,sector);model.prepare_float()
        all_masks=[a+(b<<n) for a in model.alpha for b in model.beta]
        exact_columns=[model.column(mask) for mask in all_masks]
        H=S.Matrix(model.dimension,model.dimension,lambda i,j:S.Rational(exact_columns[j].get(i,0),model.denominator))
        assert H==H.T
        float_images=[]
        for j,col in enumerate(exact_columns):
            v=np.eye(model.dimension)[:,j];y=model.apply_float(v)
            assert exact_error_squared(y,col,model.denominator)<=model.action_error_per_norm**2
            float_images.append(y);columns+=1
        # Independent spin-free E-product reconstruction, distinct from ladder columns.
        E=[]
        for p,q in product(range(n),repeat=2):
            integer=np.zeros((model.dimension,model.dimension))
            a,b=model.links[p*n+q]
            for src,dst,sign in zip(*a):
                for beta in range(len(model.beta)):integer[dst*len(model.beta)+beta,src*len(model.beta)+beta]+=sign
            for src,dst,sign in zip(*b):
                for alpha in range(len(model.alpha)):integer[alpha*len(model.beta)+dst,alpha*len(model.beta)+src]+=sign
            E.append(S.Matrix(integer.astype(int)))
        independent=S.zeros(model.dimension)
        for p,q in product(range(n),repeat=2):independent+=sr(model.h[p][q])*E[p*n+q]
        for p,q,r,s in product(range(n),repeat=4):
            independent+=sr(model.g[p,q,r,s])*(E[p*n+q]*E[r*n+s]-(E[p*n+s] if q==r else S.zeros(model.dimension)))/2
        assert independent==H;identities+=1
        # Both a Galerkin-like and a deliberately non-Galerkin observed basis.
        source=rng.integers(-2,3,size=model.dimension).astype(float)/4
        if not np.any(source):source[0]=1
        Q=np.eye(model.dimension)[:,:min(3,model.dimension)];Y=np.column_stack(float_images)[:,:Q.shape[1]]
        records=certify_grid(model,Q,Y,source,[F(-1,3),F(1,8)],[F(1,10),F(1,2)],dict(method='coordinate-audit',actions=Q.shape[1]))
        # Observed dense, nonorthogonal binary64 columns exercise the actual
        # Q*a / Y*a rounding terms; the proof requires neither Q.T*Q=I nor
        # an exact solution of the projected system.
        dense=rng.normal(size=(model.dimension,min(3,model.dimension)))
        dense[:,0]*=1.3;dense[:,1]+=.2*dense[:,0]
        images=np.column_stack([model.apply_float(dense[:,j]) for j in range(dense.shape[1])])
        records+=certify_grid(model,dense,images,source,[F(-1,3),F(1,8)],[F(1,10),F(1,2)],dict(method='dense-audit',actions=dense.shape[1]))
        b=S.Matrix([sr(F(float(x))) for x in source])
        for record in records:
            z=sr(F(record['ionic_energy']))+S.I*sr(F(record['eta']))
            exact=(b.T*(z*S.eye(model.dimension)-H).inv(method='DM')*b)[0]
            center=sr(F(record['response_center']['real']))+S.I*sr(F(record['response_center']['imaginary']))
            delta=S.expand_complex(exact-center)
            assert S.re(delta)**2+S.im(delta)**2<=sr(F(record['radius_rational_upper']))**2
            responses+=1
    # Generic complex approximate x needs the explicit Galerkin-defect term.
    x=-S.I*S.Rational(11,10);z=S.I;b=S.Integer(1);r=b-z*x
    error=b*b/z-b*x
    assert S.simplify(error-x*r-r*r/z)==0
    assert abs(error)>abs(r)**2
    # Exact residual-certificate formula also handles arbitrary source leakage.
    H=S.Matrix([[S.Rational(1,2),S.Rational(1,8)],[S.Rational(1,8),S.Rational(-1,4)]])
    source=S.Matrix([1,S.Rational(1,3)]);z=S.Rational(1,5)+S.I*S.Rational(1,10)
    xx=np.array([.3-.7j]);center=complex(xx[0])
    cert=residual_certificate([[F(1,2)]],[[F(1,64)]],[F(1,24)],F(1,9),[F(1)],xx,(F(1,5),F(1,10)),center)
    exact=(source.T*(z*S.eye(2)-H).inv()*source)[0];difference=S.expand_complex(exact-scomplex(center))
    assert S.re(difference)**2+S.im(difference)**2<=sr(F(cert['radius_rational_upper']))**2
    # Full H10 columns also have an exact reference; measured error includes
    # converting neither the target nor the approximation to a tolerance test.
    with np.load('research/computational-chemistry/stage15/inputs/h10_view.npz',allow_pickle=False) as data:
        full=ElectronicModel(data['h1'],data['eri'],(5,4))
    full.prepare_float();full_error_squares=[]
    try:full.apply_float(np.full(full.dimension,2.**21))
    except ValueError:pass
    else:raise AssertionError('Missing action range rejection')
    try:full.apply_float(np.full(full.dimension,2.**-1000))
    except ValueError:pass
    else:raise AssertionError('Missing underflow guard rejection')
    for mask in full.retained_masks():
        vector=np.zeros(full.dimension);vector[full.index(mask)]=1
        image=full.apply_float(vector);col=full.column(mask)
        error2=exact_error_squared(image,col,full.denominator)
        assert error2<=full.action_error_per_norm**2;full_error_squares.append(str(error2))
    result=dict(status='passed',seed=150916,exact_kernel_columns=columns,independent_spin_free_operator_identities=identities,
        exact_response_inclusions=responses,generic_defect_counterexample_checked=True,source_leakage_example_checked=True,
        full_h10_exact_column_checks=9,full_h10_action_error_squared=full_error_squares,
        scope='Finite exact implementation checks; general FP certificate remains conditional on its explicit primitive-operation model and range guards')
    (args.output/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
