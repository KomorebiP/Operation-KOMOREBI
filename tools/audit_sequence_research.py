"""Independent exact checks for the bounded research tables and columns."""
from fractions import Fraction as Q
from math import comb, factorial
from collections import Counter


def verify_additions(entries, parameter, theta):
    from sequence_library import source_degree
    extra=[item for item in entries if item.get('research_addition')]
    assert len(extra)==139
    counts=Counter(); inverse={}
    for N in range(2,13):
        d=[Q(1,factorial(N*n)) for n in range(24)]
        q=[Q(1)]
        for n in range(1,24):q.append(-sum(d[k]*q[n-k] for k in range(1,n+1)))
        power=[Q(1)]+[Q(0)]*23
        for r in range(1,4):
            power=[sum(power[k]*q[n-k] for k in range(n+1)) for n in range(24)]
            inverse[N,r]=[value*factorial(N*n) for n,value in enumerate(power)]
    for item in extra:
        N=item['N'];kind=item['kind'];table=item.get('triangle')
        if not table:
            assert kind=='block-Appell coefficient column' and len(item['terms'])==24
            for n,value in enumerate(item['terms']):
                expected=comb(N*n+item['k'],item['k'])*inverse[N,item['power']][n]
                assert expected.denominator==1 and int(value)==expected,(item['id'],n)
                assert source_degree(item,n)==N*n+item['k']
                counts['appell_supported_column_terms']+=1;counts['source_index_maps']+=1
            continue
        assert len(table['row_lengths'])==13
        at=0
        for n,length in enumerate(table['row_lengths']):
            assert length==(2*n+1 if kind=='theta coefficient triangle' else n+1)
            assert table['row_offsets'][n]==at
            for k in range(length):
                if kind=='secancy coefficient triangle':expected=parameter[N][n][k];degree=N*n
                elif kind=='theta coefficient triangle':expected=theta[n][k];degree=2*n
                elif kind=='block-Appell coefficient triangle':
                    expected=comb(n,k)*inverse[N,item['power']][(n-k)//N] if (n-k)%N==0 else 0;degree=n
                else:
                    expected=comb(N*n,N*k)*(inverse[N,1][n-k] if kind=='inverse block-binomial triangle' else 1);degree=N*n
                assert int(item['terms'][at+k])==expected,(item['id'],n,k)
                assert source_degree(item,at+k)==degree,(item['id'],n,k)
                counts['triangle_coefficients']+=1;counts['source_index_maps']+=1
            at+=length
        assert at==len(item['terms'])
    # Both products are checked; the oracle uses direct binomials and reciprocal-series coefficients.
    for N in range(2,13):
        for n in range(13):
            for k in range(n+1):
                left=sum(comb(N*n,N*j)*comb(N*j,N*k)*inverse[N,1][j-k] for j in range(k,n+1))
                right=sum(comb(N*n,N*j)*inverse[N,1][n-j]*comb(N*j,N*k) for j in range(k,n+1))
                assert left==right==int(n==k),(N,n,k)
                counts['inverse_kernel_cells']+=1
    return dict(counts)
