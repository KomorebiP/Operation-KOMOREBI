#!/usr/bin/env python3
"""Separate finite solver: enumerate admissible values on an invertible row basis.
Uses theta^2=theta+1 coefficient coordinates and the independent residue columns.
Imports no primary arithmetic. Counts finite necessary systems, not representations.
"""
from __future__ import annotations
import argparse,itertools,json,hashlib
from pathlib import Path

def check(x,msg):
    if not x:raise AssertionError(msg)
def rank(matrix):
    if not matrix:return 0
    a=[row[:] for row in matrix];i=0
    for j in range(len(a[0])):
        k=next((k for k in range(i,len(a)) if a[k][j]%7),None)
        if k is None:continue
        a[i],a[k]=a[k],a[i];iv=pow(a[i][j]%7,-1,7);a[i]=[x*iv%7 for x in a[i]]
        for k in range(i+1,len(a)):
            t=a[k][j]%7
            a[k]=[(x-t*y)%7 for x,y in zip(a[k],a[i])]
        i+=1
        if i==len(a):break
    return i

def inverse(matrix):
    n=len(matrix);a=[row[:]+[int(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    for j in range(n):
        k=next(k for k in range(j,n) if a[k][j]%7);a[k],a[j]=a[j],a[k]
        iv=pow(a[j][j]%7,-1,7);a[j]=[x*iv%7 for x in a[j]]
        for k in range(n):
            if k==j:continue
            t=a[k][j]%7;a[k]=[(x-t*y)%7 for x,y in zip(a[k],a[j])]
    check([r[:n] for r in a]==[[int(i==j) for j in range(n)] for i in range(n)],'Singular selected row basis')
    return [r[n:] for r in a]
def theta(code):
    a,b=code%7,code//7
    return (a-b)%7+7*(2*b%7)
def allowed(d,ell,v,r):
    if ell in (71,29):return (0,)
    pairs=[{theta(z) for z in pair} for pair in d['paired_trace_sets'][str(ell)]]
    # u=v*w=-v+2v*theta.
    out=[]
    for b in range(7):
        t=b*(2 if ell==43 else 1)%7
        products=[t*(-v*x+r*y+z)%7+7*(2*t*v*x%7) for x,y,z in d['kummer_rows'][str(ell)]]
        if not any(products) or any(set(products)<=pair for pair in pairs):out.append(b)
    return tuple(out)

def solve(universe,cols,d):
    output=[];cover=[]
    for r in range(1,7):
        qs=[q for q in universe if cols[q]['ratio'] in (r,'all')];n=len(qs)
        tests=[ell for ell in d['test_order'] if ell not in qs]
        rows={ell:[cols[q]['rows'][str(ell)] for q in qs] for ell in tests}
        for v in range(1,7):
            opts={ell:allowed(d,ell,v,r) for ell in tests}
            if any(not a for a in opts.values()):continue
            chosen=[];bs=[];labels=[]
            for ell in sorted(tests,key=lambda ell:(len(opts[ell]),ell)):
                if rank(chosen+[rows[ell]])>len(chosen):
                    chosen.append(rows[ell]);bs.append(opts[ell]);labels.append(ell)
                if len(chosen)==n:break
            for i in range(n):
                e=[int(j==i) for j in range(n)]
                if rank(chosen+[e])>len(chosen):chosen.append(e);bs.append(tuple(range(7)));labels.append('inertia'+str(i))
                if len(chosen)==n:break
            check(len(chosen)==n,'No full enumeration basis')
            inv=inverse(chosen);total=1
            for s in bs:total*=len(s)
            # Convert every remaining row into coordinates on the selected value basis.
            transformed={ell:[sum(rows[ell][k]*inv[k][j] for k in range(n))%7 for j in range(n)] for ell in tests}
            accepted=0
            for rhs in itertools.product(*bs):
                if not any(rhs):continue
                values={};okay=True
                for ell in tests:
                    value=sum(a*b for a,b in zip(transformed[ell],rhs))%7
                    if value not in opts[ell]:okay=False;break
                    values[str(ell)]=value
                if not okay:continue
                x=[sum(a*b for a,b in zip(row,rhs))%7 for row in inv]
                check(any(x),'Unexpected zero inertia')
                output.append({'alpha':[7*v,r,1],'columns':qs,'inertia':x,'values':values});accepted+=1
            cover.append({'ratio':r,'v':v,'columns':qs,'basis_labels':labels,'rhs_assignments_checked':total,'accepted':accepted})
        print('independent ratio',r,'cumulative',len(output),flush=True)
    canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
    output.sort(key=canon);check(len({canon(x) for x in output})==len(output),'Independent duplicate')
    return output,cover

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--columns',type=Path,required=True);p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=json.loads(a.fixture.read_text());cc=json.loads(a.columns.read_text());cert=json.loads(a.certificate.read_text())
    check(cc['status']=='PASS_SEPARATE_COLUMN_AUDIT','Unchecked independent columns')
    cols={row['q']:row for row in cc['rows']};summaries={}
    for key,universe in [('baseline25',d['inherited_universe']),('expanded28',sorted(cols))]:
        found,cover=solve(universe,cols,d)
        check(found==cert[key]['survivors'],'Changed complete survivor list')
        check(len(found)==cert[key]['count'],'Changed survivor count')
        summaries[key]={'count':len(found),'basis_covers':cover,'survivor_sha256':hashlib.sha256(('\n'.join(json.dumps(s,sort_keys=True,separators=(',',':')) for s in found)+'\n').encode()).hexdigest()}
    out={'schema':'beal.block68.independent-sieve.v1','status':'PASS_SEPARATE_FINITE_SIEVE','primary_imports':False,'coefficient_basis':'theta^2=theta+1, w=2theta-1','method':'Complete allowed value tuples on an invertible row basis','cases':summaries}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'])
if __name__=='__main__':main()
