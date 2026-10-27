"""Exact finite examples for Series09. These checks do not solve inverse Galois."""
from pathlib import Path
import argparse
import itertools
import json
import sympy as sp


def compose(p, q):
    """p after q; permutations map index i to p[i]."""
    return tuple(p[q[i]] for i in range(len(p)))


def subgroup(generators, n):
    elements = {tuple(range(n))}
    while True:
        enlarged = elements | {compose(a, b) for a in elements for b in generators}
        if enlarged == elements:
            return sorted(elements)
        elements = enlarged


def product_set(h, k):
    return {compose(a, b) for a in h for b in k}


def matrix_json(a):
    return [[str(a[i, j]) for j in range(a.cols)] for i in range(a.rows)]


def permutation_matrix(g, basis):
    index = {h: i for i, h in enumerate(basis)}
    a = sp.zeros(len(basis))
    for j, h in enumerate(basis):
        a[index[compose(g, h)], j] = 1
    return a


def average(h, basis):
    return sum((permutation_matrix(g, basis) for g in h), sp.zeros(len(basis))) / len(h)


def factor_record(f, x, p):
    _, factors = sp.factor_list(f, x, modulus=p)
    out = []
    for factor, multiplicity in factors:
        poly = sp.Poly(factor, x, modulus=p).monic()
        out.append({'coefficients_descending': [int(c) % p for c in poly.all_coeffs()],
                    'degree': poly.degree(), 'multiplicity': multiplicity})
    out.sort(key=lambda item: (item['degree'], item['coefficients_descending']))
    return out


def run():
    x = sp.Symbol('x')
    polynomials = {
        'C2': x**2 - 2,
        'V4_primitive_element': x**4 - 10*x**2 + 1,
        'C3': x**3 + x**2 - 2*x - 1,
        'S3': x**3 - 2,
        'S4': x**4 - x - 1,
    }
    records = {}
    for name, f in polynomials.items():
        records[name] = {'polynomial': str(f), 'coefficients_descending':
                        [int(c) for c in sp.Poly(f, x).all_coeffs()],
                        'discriminant': str(sp.discriminant(f, x)),
                        'factorization_over_Q': str(sp.factor(f)),
                        'irreducible_over_Q_sympy': bool(sp.Poly(f, x).is_irreducible)}
    assert [records[k]['discriminant'] for k in ['C2','C3','S3','S4']] == ['8','49','-108','-283']
    assert sp.expand((sp.sqrt(2)+sp.sqrt(3))**4 - 10*(sp.sqrt(2)+sp.sqrt(3))**2+1) == 0
    records['C3']['rational_root_candidates'] = {'-1': 1, '1': -1}
    for a, value in records['C3']['rational_root_candidates'].items():
        assert int(polynomials['C3'].subs(x,int(a))) == value
    records['S4']['modular_factors'] = {str(p): factor_record(polynomials['S4'],x,p) for p in [2,7]}
    assert [r['degree'] for r in records['S4']['modular_factors']['2']] == [4]
    assert [r['degree'] for r in records['S4']['modular_factors']['7']] == [1,3]
    cubic = x**3+3*x**2+2*x+5
    records['S4']['mod7_cubic_root_residues'] = [int(cubic.subs(x,a))%7 for a in range(7)]
    assert records['S4']['mod7_cubic_root_residues'] == [5,4,1,2,6,5,5]
    assert sp.Poly((x-3)*cubic-polynomials['S4'],x,modulus=7).is_zero

    basis = list(itertools.permutations(range(3)))
    e = tuple(range(3));h=subgroup([(1,0,2)],3);k=subgroup([(0,2,1)],3)
    groups = {'1':[e], 'H12':h, 'H23':k, 'H13':subgroup([(2,1,0)],3),
              'A3':subgroup([(1,2,0)],3), 'S3':basis}
    matrices = {name:average(elements,basis) for name,elements in groups.items()}
    subgroup_checks=[]
    for name,elements in groups.items():
        a=matrices[name]
        assert a*a==a and a.T==a and a.rank()==6//len(elements)
        subgroup_checks.append({'name':name,'order':len(elements),'rank':a.rank(),'idempotent':True,'self_adjoint':True})
    pair_checks=[]
    for hn,he in groups.items():
        for kn,ke in groups.items():
            hk=product_set(he,ke);kh=product_set(ke,he)
            commute=matrices[hn]*matrices[kn]==matrices[kn]*matrices[hn]
            assert commute==(hk==kh)
            if commute:assert matrices[hn]*matrices[kn]==average(sorted(hk),basis)
            pair_checks.append({'H':hn,'K':kn,'permutable':hk==kh,'commuting_averages':commute})
    commutator=matrices['H12']*matrices['H23']-matrices['H23']*matrices['H12']
    assert commutator!=sp.zeros(6)
    norm_squared=sp.trace(commutator.T*commutator)
    s3={'basis_permutations_zero_based':[list(p) for p in basis],
        'basis_cycle_labels':['()','(23)','(12)','(123)','(132)','(13)'],
        'composition':'p after q; lambda(g)e_x=e_(gx)',
        'subgroups':subgroup_checks,'all_ordered_subgroup_pairs':pair_checks,
        'H12_average':matrix_json(matrices['H12']), 'H23_average':matrix_json(matrices['H23']),
        'commutator':matrix_json(commutator), 'commutator_frobenius_norm_squared':str(norm_squared)}

    c4=subgroup([(1,2,3,0)],4);transposition=subgroup([(1,0,2,3)],4)
    hk=product_set(c4,transposition);kh=product_set(transposition,c4)
    assert hk!=kh
    pavg=sp.zeros(4)
    for g in c4:
        for j in range(4):pavg[g[j],j]+=sp.Rational(1,4)
    sum_zero_basis=sp.Matrix([[1,0,0],[0,1,0],[0,0,1],[-1,-1,-1]])
    assert pavg==sp.ones(4)/4 and pavg*sum_zero_basis==sp.zeros(4,3)
    s4_boundary={'H_cycle':'(1234)','K_cycle':'(12)','H_order':4,'K_order':2,
                 'HK':sorted(map(list,hk)),'KH':sorted(map(list,kh)),
                 'HK_not_KH_witness':list(sorted(hk-kh)[0]),
                 'permutation_space_average':matrix_json(pavg),
                 'sum_zero_basis_columns':matrix_json(sum_zero_basis),
                 'restricted_average':matrix_json(sp.zeros(3)),
                 'meaning':'Faithful standard S4 group representation need not be faithful as a Q[S4] representation.'}

    c4_hom_images=[a for a in range(4) if (2*a)%4==0]
    compatible_lifts=[a for a in c4_hom_images if a%2==1]
    assert c4_hom_images==[0,2] and compatible_lifts==[]
    embedding={'Gamma':'C2 (finite toy, not absolute Galois group)', 'E':'C4','G':'C2',
               'homomorphism_generator_images':c4_hom_images,'compatible_lifts':compatible_lifts,
               'split_lifts_into_C2xC2':[[[0,0],[a,1]] for a in [0,1]],
               'split_lift_image_orders':[2,2],'split_group_order':4}
    specialization=[{'t':n,'polynomial':str(x**3-n),'discriminant':str(sp.discriminant(x**3-n,x)),
                     'factors_over_Q':str(sp.factor(x**3-n))} for n in [0,1,2]]
    return {'schema_version':1, 'coefficient_domain':'Q and exact finite fields F2,F7',
            'polynomials':records,'S3_regular_representation':s3,
            'faithful_group_representation_boundary':s4_boundary,'finite_embedding_toys':embedding,
            'specialization_group_change_toy':specialization,
            'scope':{'polynomials':5,'S3_subgroups':6,'S3_ordered_subgroup_pairs':36,
                     'S4_boundary':1,'finite_embedding_problems':2,'specializations':3},
            'non_claims':['No universal inverse Galois realization theorem',
                          'No polynomial group is certified solely by numerical roots',
                          'The family X^3-t is not a regular S3 extension over Q(t)',
                          'Finite group lifting toys are not absolute-Galois obstructions']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='computations/exact_examples.json')
    args=parser.parse_args();result=run();p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'passed','output':str(p),'scope':result['scope']}))
