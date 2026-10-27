#!/usr/bin/env python3
"""Independent exact representation/linear audit of the frozen Block80 data.

SymPy's GF(7) matrices and integer determinants check stored rank certificates.
Fresh scalar polynomial Hensel lifts check every conductor self-unit. A separate
script is loaded solely to query the archived target evaluator, whose answers
are compared with exact augmented ranks. All targets here are synthetic.
"""
from __future__ import annotations
import argparse, importlib.util, itertools, json
from pathlib import Path
import sympy as sp
from sympy.polys.matrices import DomainMatrix

BASE = Path('evidence/computation/inputs/block80/work80')

def require(value, message):
    if not value:
        raise ValueError(message)

def domain_matrix(M):
    return DomainMatrix.from_Matrix(sp.Matrix(M)).convert_to(sp.GF(7))

def rank(M):
    return len(domain_matrix(M).rref()[1])

def mat_product(A, B):
    return (sp.Matrix(A)*sp.Matrix(B)).applyfunc(lambda x: int(x)%7).tolist()

def determinant_certificate(M):
    cols = list(domain_matrix(M).rref()[1])
    selected = [[row[j] for j in cols] for row in M]
    rows = list(domain_matrix(sp.Matrix(selected).T.tolist()).rref()[1])
    minor = [[M[i][j] for j in cols] for i in rows]
    det = int(sp.Matrix(minor).det(method='domain-ge'))
    require(det%7 != 0, 'selected integer rank minor vanishes mod7')
    return {'rank': len(cols), 'row_indices': rows, 'column_indices': cols, 'integer_determinant': str(det), 'determinant_mod7': det%7}

def pair_product(x, y, modulus, phi=False):
    a,b=x;c,d=y
    if phi:
        return ((a*c+b*d)%modulus, (a*d+b*c+b*d)%modulus)
    return ((a*c+5*b*d)%modulus, (a*d+b*c)%modulus)

def repeated_power(x, exponent, modulus, phi=False):
    result=(1,0)
    for _ in range(exponent):
        result=pair_product(result,x,modulus,phi)
    return result

def encoded_image(A, vector):
    real=[v%7 for v in vector];imag=[v//7 for v in vector]
    return [sum(x*y for x,y in zip(row,real))%7+7*(sum(x*y for x,y in zip(row,imag))%7) for row in A]

def encoded_add(u,v):
    return [(a%7+b%7)%7+7*((a//7+b//7)%7) for a,b in zip(u,v)]

def augmented_image_test(A, target):
    augmented=[row+[y%7,y//7] for row,y in zip(A,target)]
    return rank(augmented)==rank(A)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    ns=parser.parse_args();ns.output.mkdir(parents=True,exist_ok=True)
    cert=json.loads((BASE/'verification/primary80.json').read_text())
    require(cert==json.loads((BASE/'verification/independent80.json').read_text()), 'primary/secondary result mismatch')
    inputs=json.loads((BASE/'inputs/finite_inputs.json').read_text())
    extra=json.loads((BASE/'verification/independent80_extra.json').read_text())
    require(pow(5,3,7)==6, 'w²−5 reducible overF7')
    field_products=0
    for a,b,c,d in itertools.product(range(7),repeat=4):
        wproduct=pair_product((a,b),(c,d),7)
        phi_product=pair_product(((a-b)%7,2*b%7),((c-d)%7,2*d%7),7,True)
        require(phi_product==((wproduct[0]-wproduct[1])%7,2*wproduct[1]%7),'field basis conversion is not multiplicative')
        field_products+=1
    p49=repeated_power((25,25),48,49)
    t49=repeated_power((3,0),48,49)
    plog=[((p49[0]-1)//7)%7,p49[1]//7%7]
    tlog=[((t49[0]-1)//7)%7,t49[1]//7%7]
    require(plog==[0,5]==cert['local_phi_log_w'] and tlog==[6,0]==cert['local_three_log_w'],'7-adic unit witnesses changed')
    require(all(record['fixed_logs'][0]==0 for record in cert['residue_data'].values()),'phi not locally zero at support')
    self_units=[]
    for old in extra['self_uniformizer_units']:
        q=old['prime'];cs=inputs['conductor_generators'][str(q)];g=inputs['normalizations'][str(q)]['beta_generator'][0]
        root=pow(g,(q-1)//7,q);modulus=q*q
        phi_value=sum(pow(root,i,modulus) for i in range(7))%modulus
        derivative=sum(i*pow(root,i-1,q) for i in range(1,7))%q
        lift=root+q*(-(phi_value//q)*pow(derivative,-1,q)%q)
        require(sum(pow(lift,i,modulus) for i in range(7))%modulus==0,'Hensel cyclotomic lift failed')
        pi=sum(c*pow(lift,i,modulus) for i,c in enumerate(cs))%modulus
        require(pi%q==0 and pi!=0,'pi_q is not valuation1 at chosen conductor place')
        unit=pi//q
        powers=[pow(root,i,q) for i in range(7)]
        log=lambda value:powers.index(pow(value,(q-1)//7,q))
        ul=log(unit)
        other=[log(sum(c*pow(pow(root,b,q),i,q) for i,c in enumerate(cs))%q) for b in range(2,7)]
        require((ul+sum(other))%7==0,'self-unit norm relation fails')
        row=(-ul-sum(b*l for b,l in zip(range(2,7),other)))%7
        index=cert['prime_order'].index(q)
        require(row==cert['beta_uniformizer_rows_over_Q'][str(q)][index],'conductor self-row sign/normalization changed')
        require(lift==old['cyclotomic_root_mod_q2'] and unit==old['local_unit'] and ul==old['local_unit_log'],'independent scalar Hensel result differs')
        self_units.append({'q':q,'lift':lift,'unit':unit,'unit_log':ul,'self_row':row})
    spec=importlib.util.spec_from_file_location('archived_evaluator',BASE/'computations/evaluate_target.py')
    evaluator=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluator)
    patterns={};basis_targets=0;image_targets=0;origin_tests=0;malformed=0
    for label,data in cert['patterns'].items():
        L=data['localization_relations'];J=data['localization_image_basis'];E=data['constraint_matrix'];A=data['global_to_constraint_matrix'];N=data['dual_obstruction_basis'];K=data['kernel_basis']
        require(mat_product(L,J)==[[0]*10 for _ in range(14)],'LJ!=0')
        require(mat_product(E,J)==A,'A!=EJ')
        require(mat_product(N,A)==[[0]*10 for _ in N],'NA!=0')
        require(mat_product(A,sp.Matrix(K).T.tolist())==[[0]*len(K) for _ in A],'AK!=0')
        ranks={name:determinant_certificate(M) for name,M in [('L',L),('J',J),('A',A),('N',N),('K',K)]}
        require([ranks[x]['rank'] for x in ['L','J','A','N','K']]==[14,10,data['rank'],15-data['rank'],10-data['rank']],'rank/nullity mismatch')
        base={'kind':'synthetic','provenance':'fresh independent basis audit only','basis':evaluator.BASIS,'pattern':label}
        for j in range(15):
            for scalar in range(49):
                target=[scalar if i==j else 0 for i in range(15)]
                result=evaluator.evaluate({**base,'target':target},cert)
                require(result['linear_target_in_image']==augmented_image_test(A,target),'evaluator disagrees with GF7 augmented rank')
                require(not result['arithmetic_target_authenticated'] and not result['actual_pattern_eliminated'],'synthetic target promoted')
                basis_targets+=1
        bad=data['synthetic_nonimage_target'];obstruction=encoded_image(N,bad)
        for j in range(10):
            for scalar in range(49):
                z=[scalar if i==j else 0 for i in range(10)];target=encoded_image(A,z)
                result=evaluator.evaluate({**base,'target':target},cert)
                require(result['linear_target_in_image'] and encoded_image(A,result['particular_character_correction'])==target,'synthetic correction reconstruction failed')
                image_targets+=1
                require(encoded_image(N,encoded_add(bad,target))==obstruction,'origin-invariant cokernel class changed')
                origin_tests+=1
        for replacement in (True,False,-1,49,7.0,'7',None,{},[]):
            try:evaluator.evaluate({**base,'target':[0]*14+[replacement]},cert)
            except ValueError:malformed+=1
            else:raise ValueError('malformed target accepted')
        patterns[label]={'ranks_and_exact_integer_minors':ranks,'support':data['support'],'homogeneous_dimension':len(K),'obstruction_dimension':len(N),'remaining_character_support':data['remaining_character_support']}
    x,y,a,b,lam=sp.symbols('x y a b lam',nonzero=True)
    differential=lam*a/x+lam*b/y-lam*(a+x*b)/(x*y)+a*(1/y-1)*lam/x
    trace=(x-1)*lam*a/x+a*(1/x-1)*lam
    c,d,f,t=sp.symbols('c d f t')
    gauge=c*(f+t*d)-(b+t*c)*d-(c*f-b*d)
    require(sp.cancel(differential)==0 and sp.cancel(trace)==0 and sp.expand(gauge)==0,'symbolic primitive/gauge identity fails')
    out={'status':'PASS_INDEPENDENT_EXACT_AUDIT','software':{'python':__import__('platform').python_version(),'sympy':sp.__version__},
         'field_basis_product_comparisons':field_products,'phi48_mod49_w':list(p49),'three48_mod49_w':list(t49),'phi_log_w':plog,'three_log_w':tlog,
         'self_conductor_units':self_units,'patterns':patterns,'all_field_scalar_basis_target_tests':basis_targets,
         'all_field_scalar_basis_image_tests':image_targets,'all_field_scalar_origin_tests':origin_tests,'malformed_encoded_entries_rejected':malformed,
         'symbolic_identities_checked':['fixed primitive differential','fixed trace','Frobenius lift invariance'],
         'actual_arithmetic_target_authenticated':False,'patterns_eliminated':0,
         'nonclaims':['Basis targets cover the full coefficient field but do not enumerate all49^15 targets.',
                     'The independent arithmetic audit does not prove the inherited actual geometry or instantiate a global primitive.']}
    (ns.output/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'])
    return 0

if __name__=='__main__':
    raise SystemExit(main())
