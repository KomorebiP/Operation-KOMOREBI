#!/usr/bin/env python3
"""Exact bounded audit of August weighted dyadic equation (13.1).

Both coefficient vectors (n(b),n(b+h))=(1,0),(0,1) are tested for
every odd b below h and every unit u modulo2^s, s3..9. This covers87376
integer coefficient equalities. Historical s3..14 count89478480 is only a
resource-count formula here, not a replay at that bound.
"""
import argparse,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    rows=[]
    for s in range(3,10):
        m=2**s;h=m//2;count=0
        for b in range(1,h,2):
            for u in range(1,m,2):
                r=u*b%m;rp=u*(b+h)%m
                low=u*b%h
                epsilon=-1 if r<h else 1
                for nb,nh in ((1,0),(0,1)):
                    lhs=nb*(r-h)+nh*(rp-h)
                    rhs=(nb+nh)*(low-h//2)+(h//2)*(nb-nh)*epsilon
                    assert lhs==rhs,(s,b,u,nb,nh,lhs,rhs)
                    count+=1
        assert count==m*m//4
        rows.append({'s':s,'modulus':m,'coefficient_equalities':count})
    total=sum(r['coefficient_equalities'] for r in rows)
    assert total==87376
    data={'status':'PASS: exact bounded weighted dyadic coefficient identities','s_min':3,'s_max':9,'actual_coefficient_checks':total,'rows':rows,'historic_s3_through14_expected_count':sum((2**s)**2//4 for s in range(3,15)),'historic_bound_replayed':False,'nonclaims':['No proof by sampling of the all-degree identity','No replay at degree16384']}
    a.out.write_text(json.dumps(data,indent=2)+'\n');print(data['status'],total)

if __name__=='__main__':main()
