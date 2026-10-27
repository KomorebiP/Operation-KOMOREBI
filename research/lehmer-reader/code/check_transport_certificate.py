#!/usr/bin/env python3
"""Independent exact check of the p31 hierarchical transfer certificate.

The historical generator uses rational row reduction. This checker establishes
matching lower rank bounds over two prime fields and structural upper bounds
from aggregation. It checks every displayed equality over Q. Only the one
generated shell/degree certificate is tested. No uniform-rank claim follows.
"""
from fractions import Fraction
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]

def scalar(value):
    if type(value) is int:
        return Fraction(value)
    assert isinstance(value,list) and len(value)==2
    assert all(type(x) is int for x in value) and value[1] != 0
    return Fraction(*value)

def matrix(value):
    assert value and len({len(row) for row in value}) == 1
    return [[scalar(x) for x in row] for row in value]

def mv(a,x):
    assert all(len(row)==len(x) for row in a)
    return [sum(v*w for v,w in zip(row,x)) for row in a]

def mm(a,b):
    assert all(len(row)==len(b) for row in a)
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]

def modular_rank(matrix_,p):
    # A nonzero minor mod p gives an exact rational lower bound on rank.
    a = [[(v.numerator%p)*pow(v.denominator,-1,p)%p for v in row] for row in matrix_]
    rank = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(rank,len(a)) if a[i][j]),None)
        if pivot is None:
            continue
        a[rank],a[pivot] = a[pivot],a[rank]
        inverse = pow(a[rank][j],-1,p)
        a[rank] = [v*inverse%p for v in a[rank]]
        for i in range(rank+1,len(a)):
            factor = a[i][j]
            a[i] = [(v-factor*w)%p for v,w in zip(a[i],a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--certificate',type=Path,
        default=Path('evidence/computation/replays/transport/p31_transport_certificate.json'))
    args = parser.parse_args()
    path = args.certificate if args.certificate.is_absolute() else ROOT/args.certificate
    cert = json.loads(path.read_text())
    assert cert['n']==31
    a,mc,mf,n,b = [matrix(cert[k]) for k in ['aggregation','coarse_matrix',
                             'fine_matrix','coefficient_kernel_basis','detail_matrix']]
    sc,sf = [[scalar(v) for v in cert[k]] for k in ['coarse_mass','fine_mass']]
    ac,ad = [[scalar(v) for v in cert[k]] for k in ['coarse_coefficients','detail_coefficients']]
    after_coarse,after_detail = [[scalar(v) for v in cert[k]] for k in ['after_coarse','after_detail']]
    assert len(mc)==6 and len(mf)==16
    assert all(sum(a[i][j] for i in range(len(a)))==1 for j in range(len(a[0])))
    assert all(any(row) for row in a)
    assert mm(a,mf)==mc and mv(a,sf)==sc
    assert mm(mf,n)==b
    assert all(v==0 for row in mm(a,b) for v in row)
    assert all(sum(row[j] for row in mc)==0 for j in range(len(mc[0])))
    assert all(sum(row[j] for row in mf)==0 for j in range(len(mf[0])))
    assert [v+w for v,w in zip(sf,mv(mf,ac))]==after_coarse
    assert [v+w for v,w in zip(after_coarse,mv(mf,ad))]==after_detail
    assert all(v==0 for v in mv(mc,ad))
    rank_rows = []
    for p in [65537,1000003]:
        ranks = [modular_rank(x,p) for x in [mc,mf,b]]
        assert ranks==[5,15,10]
        rank_rows.append({'prime_field':p,'coarse_rank_lower_bound':ranks[0],
                         'fine_rank_lower_bound':ranks[1],'detail_rank_lower_bound':ranks[2]})
    assert sum(after_detail)==-52843168 and sum(x!=0 for x in after_detail)==1
    result = {'status':'PASS','shell':31,'coefficient_domain':'Q and F_p, exact integers/Fraction',
              'degree_bound':22,'coarse_sectors':6,'fine_sectors':16,
              'rank_lower_bounds':rank_rows,'structural_upper_bounds':{'coarse':5,'fine':15,'detail':10},
              'exact_ranks':{'coarse':5,'fine':15,'detail':10},
              'surviving_total':-52843168,
              'non_claims':['Only this finite certificate and its stated degree range are verified',
                            'No uniform rank theorem or all-prime nonvanishing proof']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__ == '__main__':
    main()
