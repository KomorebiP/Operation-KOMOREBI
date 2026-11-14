"""Exact finite checks for the expanded reading and its corrected edge cases."""
import argparse
from itertools import product
import json
from pathlib import Path
import sys
import sympy as S

# In the public bundle this script lives beside the retained stage-fourteen code.
HERE=Path(__file__).resolve().parent
if (HERE/'sector_recovery.py').exists():sys.path.insert(0,str(HERE))
else:sys.path.insert(0,str(HERE/'public-source/chemistry_stage14'))
from molecular_model import family as integral_family,eri_tensor
from normal_model import commutator,choi
from sector_recovery import setup,unpack
from recover_sector_cache import recover
from recover_cache import rational,sqrt_bounds


def dictionary(model,h,g):
    A=S.Matrix(3,3,lambda r,s:sum(g.get((p,p,r,s),0) for p in range(3)))
    R=S.Matrix(3,3,lambda p,s:sum(g.get((p,q,q,s),0) for q in range(3)))
    t=S.trace(h)+(S.trace(A)-S.trace(R))/2;K=-h-A+R/2;K-=S.trace(K)*S.eye(3)/3
    T=model['T'];D=S.diag(*[sum(x*x for x in Q) for Q in T])
    Gamma=S.Matrix(5,5,lambda a,b:sum(T[a][p,q]*g.get((p,q,r,s),0)*T[b][r,s] for p,q,r,s in product(range(3),repeat=4)))
    C=D.inv()*Gamma*D.inv()/2
    return t,K,C


def as_operator(model,t,K,C):
    ad=model['ad'];phi=t*S.eye(9)+commutator(K)
    phi+=sum((C[a,b]*ad[a]*ad[b] for a,b in product(range(5),repeat=2)),S.zeros(9))
    return model['change']*phi*model['change'].T


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if (args.output/'checks.json').exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True,exist_ok=True);checks=[]
    def check(name,condition,cases=1):
        if not condition:raise AssertionError(name)
        checks.append({'assertion':name,'cases':cases})
    model=setup();original=integral_family();U=model['change'];W=S.Matrix.hstack(*[S.Matrix(list(T)) for T in model['T']]);D=W.T*W
    for index,(label,H) in enumerate(zip(original['labels'],original['operators'])):
        h=S.zeros(3);g={}
        if label['kind']=='h':p,q=label['indices'];h[p,q]=h[q,p]=1
        else:g=eri_tensor(*map(tuple,label['indices']))
        t,K,C=dictionary(model,h,g)
        check(f'Complete integral-to-normal dictionary generator{index}',as_operator(model,t,K,C)==H)
    v=S.Matrix(list(S.eye(3)))
    for index,H in enumerate(model['basis']):
        phi=U.T*H*U;C=-D.inv()*W.T*choi(phi)*W*D.inv()/2;t=(v.T*phi*v)[0]/3
        quad=sum((C[a,b]*model['ad'][a]*model['ad'][b] for a,b in product(range(5),repeat=2)),S.zeros(9))
        psi=phi-t*S.eye(9)-quad
        K=S.Matrix(3,3,lambda i,k:sum(psi[3*i+j,3*k+j] for j in range(3)))/3
        expected=unpack(model,S.eye(21)[:,index])
        check(f'Choi/scalar/partial-trace extraction basis{index}',(t,K,C)==expected and as_operator(model,t,K,C)==H)
    data={'action_matrix':S.zeros(9,3).tolist(),'b_hat':[1]+[0]*8,'raw_error_radius':'1','source_radius':'0','energy':'0','eta':'1'}
    zero=recover(data)
    check('Counterexample to conflating a failed all-compatible margin with unknown existence',zero['full_linear_consistent'] and zero['positive_integral_feasibility'] is True and not zero['all_compatible_positive_integral'])
    data['raw_error_radius']='0';singleton=recover(data)
    check('Zero-noise zero-C singleton is feasible and all-compatible positive',singleton['positive_integral_feasibility'] is True and singleton['all_compatible_positive_integral'] and singleton['operator_radius_squared_upper']=='0')
    theta=S.zeros(21,1)
    for i,label in enumerate(model['labels']):
        if label.get('kind')=='quadratic' and label['indices'][0]==label['indices'][1]:theta[i]=-1
    negative=as_operator(model,*unpack(model,theta));data['action_matrix']=[[str(x) for x in row] for row in (negative*model['V']).tolist()]
    bad=recover(data)
    check('Negative-semidefinite non-PSD C singleton is infeasible, not just indefinite cases',bad['full_linear_consistent'] and bad['positive_integral_feasibility'] is False)
    for field,value in [('raw_error_radius','-1'),('source_radius','-1'),('eta','0'),('eta','-1')]:
        case={'action_matrix':S.zeros(9,3).tolist(),'b_hat':[1]+[0]*8,'raw_error_radius':'0','source_radius':'0','energy':'0','eta':'1'};case[field]=value
        try:recover(case)
        except ValueError:passed=True
        else:passed=False
        check(f'Reject invalid {field}={value}',passed)
    for value in [True,float('inf'),float('-inf'),float('nan')]:
        try:rational(value)
        except ValueError:passed=True
        else:passed=False
        check('Reject nonfinite or Boolean exact-number input',passed)
    roots=[S.Integer(0),S.Integer(1),S.Integer(2),S.Rational(1,3),S.Rational(1,2)**200,S.Integer(10)**30]
    check('Outward square-root bounds including zero, exact squares and below-grid values',all((lambda bounds:bounds[0]**2<=x<=bounds[1]**2)(sqrt_bounds(x)) for x in roots),len(roots))
    # Every scalar 2x2 block below is embedded in a retained9/discarded1 direct
    # sum; the eight other retained directions are uncoupled and have zero source.
    samples=0
    for E,eta,tau,a,d in product([S.Integer(-1),S.Integer(0),S.Rational(3,5)],[S.Rational(1,8),S.Integer(1),S.Integer(2)],[S.Integer(0),S.Rational(1,5),S.Rational(4,3)],[S.Integer(0),S.Rational(1,3)],[S.Integer(-2),S.Rational(3,7)]):
        H=S.Matrix([[a,tau],[tau,d]]);Hd=S.diag(a,d);T=H-Hd;z=E+S.I*eta
        R=(z*S.eye(2)-H).inv();Rd=(z*S.eye(2)-Hd).inv()
        assert (R-Rd-Rd*T*Rd-Rd*T*R*T*Rd).applyfunc(S.simplify)==S.zeros(2)
        delta=S.simplify(R[0,0]-1/(z-a));error2=S.simplify(S.re(delta)**2+S.im(delta)**2)
        assert error2<=tau**4/eta**6
        if tau==0:assert delta==0
        samples+=1
    check('Conditional truncation bound and exact second resolvent identity on the full rational grid',True,samples)
    theta=S.zeros(21,1);theta[1]=S.Rational(1,8)
    for i,label in enumerate(model['labels']):
        if label.get('kind')=='quadratic' and label['indices'][0]==label['indices'][1]:theta[i]=S.Rational(1,64)
    Hred=as_operator(model,*unpack(model,theta));mu=S.Rational(1,128);tau=S.Rational(1,32);kappa=S.Rational(1,100);delta=S.Rational(1,8192);eta=S.Integer(1)
    full=S.zeros(10);full[:9,:9]=Hred+mu*S.eye(9);full[9,9]=S.Rational(1,3);full[0,9]=full[9,0]=tau
    b=S.eye(10)[:,0]+delta*S.eye(10)[:,9];u=S.eye(9)[:,0]
    observed={'action_matrix':[[str(x) for x in row] for row in (Hred*model['V']).tolist()],'b_hat':[1]+[0]*8,'raw_error_radius':'1/4096','source_radius':'0','energy':'0','eta':'1'}
    cert=recover(observed);r=S.Rational(cert['operator_radius_rational_upper']);center=S.Rational(cert['response_center']['real'])+S.I*S.Rational(cert['response_center']['imaginary'])
    exact=S.simplify((b.T*((kappa+S.I*eta)*S.eye(10)-full).inv(method='DM')*b)[0]);difference=S.simplify(exact-center)
    bound=(r+mu+kappa)/eta**2+tau**2/eta**3+delta*(2+delta)/eta
    error2=S.simplify(S.re(difference)**2+S.im(difference)**2)
    check('Joint numerical, block mismatch, coupling, source leakage and energy-reference enclosure on exact10-state example',error2<=bound**2)
    summary={'status':'passed','check_count':len(checks),'aggregated_cases':sum(x['cases'] for x in checks),'checks':checks,
        'conditional_truncation_grid_cases':samples,'combined_example':{'dimension':10,'mu':str(mu),'tau':str(tau),'kappa':str(kappa),'delta':str(delta),'eta':str(eta),'radius_rational_upper':str(bound),'response_error_squared_exact':str(error2)},
        'scope':'Exact finite implementation checks supporting the explicitly written finite-dimensional proofs; same-author review',
        'non_claims':['No measured full-H10 coupling or physical source/reference caps','No world novelty claim','Finite grid is not a proof for all Hamiltonians','No independent reviewer or proof-assistant execution']}
    (args.output/'checks.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({key:summary[key] for key in ['status','check_count','aggregated_cases','conditional_truncation_grid_cases']},indent=2))


if __name__=='__main__':main()
