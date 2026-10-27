#!/usr/bin/env python3
"""Extend the exact support exclusion to three low-congruence primes.
This program adapts primary arithmetic, explicitly not an independent checker.
"""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path
from trace_product_certificate import GEN as OLDGEN,norm,ev,need,ADD,MUL,dot
SUPPORT=(197,883,1373,1667,43,113,127)
GEN=dict(OLDGEN,**{})
GEN.update({113:(-1,-1,0,-1,1,1),127:(-2,-2,-2,1,1,1)})

def run(base):
    roots={};logs={};primitive={};norms={};records={}
    for q in SUPPORT:
        need(norm(GEN[q])==q,'Cyclotomic generator norm')
        norms[str(q)]=q
        roots[q]=next(r for r in range(2,q) if pow(r,7,q)==1 and ev(GEN[q],r,q)==0)
        g=next(g for g in range(2,q) if len({pow(g,i,q) for i in range(q-1)})==q-1)
        primitive[q]=g;logs[q]={pow(g,i,q):i%7 for i in range(q-1)}
    rows={}
    for ell in (29,71,491):
        row=[];records[str(ell)]={}
        for q in SUPPORT:
            vals=[ev(GEN[ell],pow(roots[q],b,q),q) for b in range(1,7)]
            ls=[logs[q][v] for v in vals]
            records[str(ell)][str(q)]={'residues':vals,'logs':ls}
            row.append(-sum(b*v for b,v in enumerate(ls,1))%7)
        rows[ell]=row
    ratios={};newk={}
    for q in (43,113,127):
        # Direct Kummer row at the inert place; prime-order root is in F_q.
        def l(x):return next(i for i in range(7) if pow(roots[q],i,q)==pow(x,(q-1)//7,q))
        row=[0,2*l(3)%7,l(5)];newk[q]=row
        ratios[q]=-row[2]*pow(row[1],-1,7)%7
    need(ratios=={43:5,113:4,127:2},'Wrong common-ratio conditions')
    results=[]
    for q in (43,113,127):
        j=SUPPORT.index(q);basis=[0]*len(SUPPORT);basis[j]=1
        basis[1]=-rows[71][j]*pow(rows[71][1],-1,7)%7
        current=[([u,ratios[q],1],[MUL[c][x] for x in basis]) for u in range(49) for c in range(1,49)]
        stages=[];after29=[]
        for ell in (29,491):
            kept=[]
            for a,s in current:
                beta=dot(rows[ell],s)
                products=[MUL[dot(k,a)][beta] for k in base['kummer_rows'][str(ell)]]
                good=all(v in base['good_trace_sets'][str(ell)] for v in products)
                bad=beta==0 and not any(products)
                if good or bad:kept.append((a,s))
            stages.append({'q':ell,'input_candidates':len(current),'survivors':len(kept)})
            current=kept
            if ell==29:after29=[{'alpha':a,'beta':s} for a,s in kept]
        need(not current,'New low-congruence support survives')
        results.append({'ramified_low_prime':q,'natural_ratio':ratios[q],
           'basis':basis,'initial_candidates':2352,'stages':stages,'after29':after29,'survivors':0,
           'note':'Only the unramified tests29 and491 are used; no Frobenius value at a ramified support prime is imposed.'})
    return {'schema':'beal.block62.low_extension.v1','status':'PASS_THREE_LOW_CONGRUENCE_EXTENSIONS',
      'support':list(SUPPORT),'new_generators':{str(q):list(GEN[q]) for q in (43,113,127)},
      'roots':{str(q):roots[q] for q in SUPPORT},'primitive_generators':{str(q):primitive[q] for q in SUPPORT},
      'norms':norms,'frobenius_rows':{str(q):v for q,v in rows.items()},'residue_evaluations':records,
      'new_kummer_rows':{str(q):v for q,v in newk.items()},'results':results,
      'total_added_candidates':7056,'total_with_base_candidates':127008,
      'scope':'All beta ramification in {43,113,127,197,883,1373,1667}; not arbitrary conductor.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=run(json.loads(a.base.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'])
if __name__=='__main__':main()
