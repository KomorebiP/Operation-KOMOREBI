#!/usr/bin/env python3
"""Exact finite corroboration only; universal conclusions are proved in Lean."""
from itertools import product
from pathlib import Path
import json,hashlib,platform

def mm(a,b,m):return tuple(tuple(sum(a[i][j]*b[j][k] for j in range(2))%m for k in range(2)) for i in range(2))
def sub(a,b,m):return tuple(tuple((a[i][j]-b[i][j])%m for j in range(2)) for i in range(2))
def main():
    # H1(C2^2,F2) -> H1(C2,F2)^3 for the two axes and the diagonal.
    image={(x,y,(x+y)%2) for x,y in product(range(2),repeat=2)}
    mismatch=(0,0,1)
    assert len(image)==4 and mismatch not in image
    assert all(any(v[i]==mismatch[i] and v[j]==mismatch[j] for v in image)
               for i in range(3) for j in range(3))
    # Enumerate all maps C2^2 -> (Z/4)^x and test multiplication, no float arithmetic.
    G=list(product(range(2),repeat=2));units=(1,3);characters=[]
    for values in product(units,repeat=4):
        f=dict(zip(G,values))
        if f[(0,0)]!=1:continue
        if all(f[((a[0]+b[0])%2,(a[1]+b[1])%2)]==f[a]*f[b]%4 for a in G for b in G):characters.append(f)
    assert len(characters)==4
    assert not any(f[(1,0)]==1 and f[(0,1)]==1 and f[(1,1)]==3 for f in characters)
    # Tame frame discrepancy in GL2(Z/9): the local mismatch is a coboundary.
    a=((8,0),(0,1));b=((8,6),(0,1));u=((1,3),(0,1));ui=((1,6),(0,1));eye=((1,0),(0,1))
    assert mm(a,a,9)==eye and mm(b,b,9)==eye and mm(u,ui,9)==eye
    assert mm(mm(u,a,9),ui,9)==b and mm(a,b,9)!=mm(b,a,9)
    ar=((2,0),(0,1));x=((0,1),(0,0))
    d0x=sub(mm(mm(ar,x,3),ar,3),x,3)
    local_a=((0,1),(0,0))
    assert d0x==local_a
    out={'status':'PASS','python':platform.python_version(),'domain':'exact modular integers',
         'checks':{'F2_localization_matrix':[[1,0],[0,1],[1,1]],'image_cardinality':4,
         'local_target_cardinality':8,'cokernel_dimension_over_F2':1,
         'mismatch':[0,0,1],'mismatch_in_global_image':False,'all_pairwise_prescriptions_extend':True,
         'maps_C2_squared_to_Z4_units_tested':16,'homomorphisms_found':4,
         'Z9_kernel_conjugacy':True,'Z9_literal_noncommutation':True,
         'Z9_normalized_mismatch_is_d0_of_E12':True},
         'scope':'two finite fixtures only; class vanishing/nonvanishing derived using the general Lean criterion',
         'nonclaims':['no universal localization surjectivity','no arithmetic Selmer vanishing','no Strong Artin result'],
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(__file__).with_name('FINITE_GAUGE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
