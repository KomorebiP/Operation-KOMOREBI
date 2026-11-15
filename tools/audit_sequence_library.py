"""Independent finite coefficient checks; optional full OEIS replay.

This checks the enumerated windows, not novelty, distinctness, or identities
inferred from a finite OEIS match.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import json
from math import comb, factorial
from pathlib import Path
from sequence_atlas import catalogue, reciprocal
from sequence_formula_catalogue import COUNT, expanded_catalogue, inverse_power, hyper_parameters, tangent, appell
from sequence_library import library_entries, source_degree
from update_sequence_library_oeis import compare


def product(a,b,count):
    return [sum(a[k]*b[n-k] for k in range(n+1)) for n in range(count)]


def checks():
    entries=expanded_catalogue();counts=Counter(x['kind'] for x in entries)
    assert dict(counts)=={'reciprocal power':99,'logarithmic companion':15,'congruential numerator':264,'congruential denominator':264,'Appell numerator':80,'Appell denominator':60,'classical multisection':1001}
    checked=Counter()
    for N in range(2,17):
        d=[Q((-1)**n,factorial(N*n)) for n in range(COUNT)]
        inverse=[Q(1)]
        for n in range(1,COUNT):inverse.append(-sum(d[k]*inverse[n-k] for k in range(1,n+1)))
        powered=[Q(1)]+[Q(0)]*(COUNT-1)
        for r in range(1,9):
            powered=product(powered,inverse,COUNT)
            assert [v*factorial(N*n) for n,v in enumerate(powered)]==list(reciprocal(N,r,COUNT)),(N,r)
            checked['reciprocal_terms']+=COUNT
        t=tangent(N)
        for n in range(COUNT):
            assert sum(d[k]*Q(t[n-k],factorial(N*(n-k+1)-1)) for k in range(n+1))==Q((-1)**n,factorial(N*(n+1)-1)),(N,n)
            checked['tangent_coefficients']+=1
        for j in range(N):
            params=[Q(p) for p in hyper_parameters(N,j)];coefficient=Q(1)
            for n in range(COUNT):
                if n:
                    denominator=n*N**N
                    for p in params:denominator*=p+n-1
                    coefficient/=denominator
                assert coefficient==Q(factorial(j),factorial(N*n+j)),(N,j,n)
                checked['hypergeometric_seed_coefficients']+=1
    for N in range(2,13):
        for j in range(1,N):
            base=[Q(1)]
            for n in range(1,COUNT):base.append(-sum(comb(N*n+j,N*k)*base[k] for k in range(n))/comb(N*n+j,N*n))
            powered=[Q(1)]+[Q(0)]*(COUNT-1)
            for r in range(1,5):
                powered=[sum(comb(N*n,N*k)*powered[k]*base[n-k] for k in range(n+1)) for n in range(COUNT)]
                assert list(inverse_power(N,j,r))==powered,(N,j,r)
                checked['congruential_rational_coefficients']+=COUNT
    for N in range(2,7):
        for j in range(N):
            for r in range(1,3):
                coeff=inverse_power(N,j,r)
                h=[coeff[n//N]/factorial(n) if n%N==0 else Q(0) for n in range(COUNT)]
                for x in (1,2):
                    expected=[v*factorial(n) for n,v in enumerate(product(h,[Q(x**n,factorial(n)) for n in range(COUNT)],COUNT))]
                    assert appell(N,j,r,x)==expected,(N,j,r,x)
                    checked['appell_rational_coefficients']+=COUNT
    limit=12*COUNT;bell=[1];fubini=[1];fib=[];lucas=[];pell=[];a,b=Q(1),Q(0);c,d=1,0
    for n in range(limit):
        fib.append(int(2*b));lucas.append(int(2*a));pell.append(d)
        a,b=(a+5*b)/2,(a+b)/2;c,d=c+2*d,c+d
        if n:
            bell.append(sum(comb(n-1,k)*bell[k] for k in range(n)))
            fubini.append(sum(comb(n,k)*fubini[n-k] for k in range(1,n+1)))
    def classical(kind,m):
        return {'fibonacci':lambda:fib[m],'lucas':lambda:lucas[m],'pell':lambda:pell[m],
            'factorial':lambda:factorial(m),'catalan':lambda:comb(2*m,m)//(m+1),'central-binomial':lambda:comb(2*m,m),
            'triangular':lambda:m*(m+1)//2,'square':lambda:m*m,'cube':lambda:m**3,
            'power-two':lambda:2**m,'power-three':lambda:3**m,'bell':lambda:bell[m],'fubini':lambda:fubini[m]}[kind]()
    for entry in entries:
        for n,value in enumerate(entry['terms']):
            expected_degree=n if entry['kind'].startswith('Appell ') else entry['N']*(n+1)-1 if entry['kind']=='logarithmic companion' else entry['N']*n+(entry['j'] if entry['kind']=='classical multisection' else 0)
            assert source_degree(entry,n)==expected_degree
            checked['source_index_maps']+=1
            if entry['kind']=='classical multisection':
                assert value==str(classical(entry['source_kind'],expected_degree)),(entry['id'],n)
                checked['classical_subsequence_terms']+=1
            if 'rational_terms' in entry:
                assert value==str(getattr(Q(entry['rational_terms'][n]),entry['component']))
                checked['reduced_integer_components']+=1
        if entry.get('source_kind') in ('catalan','central-binomial'):
            N,j=entry['N'],entry['j'];delta=2 if entry['source_kind']=='catalan' else 1;coefficient=Q(classical(entry['source_kind'],j))
            for n in range(COUNT):
                if n:
                    factor=Q(4**N)
                    for k in range(N):factor*=Q(2*j+1+2*k,2*N)+n-1;factor/=Q(j+delta+k,N)+n-1
                    coefficient*=factor
                assert coefficient==int(entry['terms'][n]),(entry['id'],n)
                checked['subsequence_hypergeometric_coefficients']+=1
    return dict(status='passed',records=len(entries),terms=sum(len(x['terms']) for x in entries),checks=dict(checked),assertion_tested='Every enumerated stored coefficient/component, source-index map, and stated hypergeometric coefficient representation agrees with exact independent constructions in the documented finite ranges.',non_claims=['No novelty or distinctness conclusion','Finite OEIS matches do not prove infinite identities'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--oeis',action='store_true');args=parser.parse_args()
    result=checks()
    if args.oeis:
        root=Path(__file__).resolve().parents[1];original=json.loads((root/'manifests/sequence-library-oeis.json').read_text(encoding='utf-8'))
        replay=compare(root/'research/oeis-snapshot/stripped.gz',root/'research/oeis-snapshot/names.gz',library_entries(catalogue()))
        for key in ['matches','total_matches','sequence_count','catalogue_terms_sha256','stripped_sha256','names_sha256']:assert original[key]==replay[key],key
        result['oeis_replay']=dict(sequences=replay['sequence_count'],local_records=len(replay['matches']),retained_hits=sum(map(len,replay['matches'].values())),observed_hits=sum(replay['total_matches'].values()))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))
