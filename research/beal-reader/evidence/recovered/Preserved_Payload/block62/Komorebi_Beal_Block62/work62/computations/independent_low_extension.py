#!/usr/bin/env python3
"""Independent added-support check, using only the independent arithmetic module.
Does not import any primary arithmetic. The prior independent program verifies
all point counts; this program rederives added symbols and support exclusions.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from independent_check import (GEN as OLDGEN,check,inverse_basis,cyclo_norm,value,
  phi_power,FM,FA,NEG,fdot,to_w)
GEN=dict(OLDGEN)
GEN.update({113:(-1,-1,0,-1,1,1),127:(-2,-2,-2,1,1,1)})
S=(197,883,1373,1667,43,113,127)
def run(data,base):
    roots={};rows={};inverses={q:inverse_basis(GEN[q]) for q in S};evaluations=0
    for q in S:
        check(cyclo_norm(inverses[q])==q,'Independent added norm')
        rt=next(t for t in range(2,q) if pow(t,7,q)==1 and value(inverses[q],t,q)==0)
        roots[q]=pow(rt,-1,q);check(data['roots'][str(q)]==roots[q],'Root comparison')
    for ell in (29,71,491):
        row=[]
        for q in S:
            g=2 if q in (197,883,1373,1667) else 3
            check(len({pow(g,i,q) for i in range(q-1)})==q-1,'Primitive residue generator')
            check(data['primitive_generators'][str(q)]==g,'Generator record')
            eta=pow(g,(q-1)//7,q);logs=[];vals=[]
            for b in range(1,7):
                v=value(inverse_basis(GEN[ell]),pow(roots[q],-b,q),q)
                symbol=pow(v,(q-1)//7,q)
                logs.append(next(j for j in range(7) if pow(eta,j,q)==symbol));vals.append(v);evaluations+=1
            check(data['residue_evaluations'][str(ell)][str(q)]=={'residues':vals,'logs':logs},'Added residue data')
            row.append(-sum(b*x for b,x in enumerate(logs,1))%7)
        rows[ell]=row;check(data['frobenius_rows'][str(ell)]==row,'Added twisted row')
    ratios={}
    for q in (43,113,127):
        rr=[]
        for x in ((0,1),(3,0),(-1,2)):
            sym=phi_power(x,(q*q-1)//7,q);check(sym[1]==0,'Nonrational Kummer root')
            rr.append(next(i for i in range(7) if pow(roots[q],i,q)==sym[0]))
        check(data['new_kummer_rows'][str(q)]==rr,'Added natural symbol')
        ratios[q]=-rr[2]*pow(rr[1],-1,7)%7
    stats=[]
    for q in (43,113,127):
        j=S.index(q);basis=[0]*7;basis[j]=1;basis[1]=-rows[71][j]*pow(rows[71][1],-1,7)%7
        current=[([u,ratios[q],1],[FM[c][x] for x in basis]) for c in range(1,49) for u in range(49)]
        stages=[];after29=[]
        for ell in (29,491):
            good={x for x in range(49) if to_w(x) in base['good_trace_sets'][str(ell)]};kept=[]
            for a,s in current:
                beta=fdot(rows[ell],s);values=[FM[fdot(k,a)][beta] for k in base['kummer_rows'][str(ell)]]
                if all(x in good for x in values) or (not beta and not any(values)):kept.append((a,s))
            stages.append({'q':ell,'input_candidates':len(current),'survivors':len(kept)})
            current=kept
            if ell==29:after29=sorted((tuple(to_w(x) for x in a),tuple(to_w(x) for x in s)) for a,s in kept)
        record=next(x for x in data['results'] if x['ramified_low_prime']==q)
        check(record['basis']==basis and record['natural_ratio']==ratios[q],'Added parameterization')
        check(record['stages']==stages and record['survivors']==0 and not current,'Added support contradiction')
        check(after29==sorted((tuple(x['alpha']),tuple(x['beta'])) for x in record['after29']),'Added checkpoint mismatch')
        stats.append({'q':q,'stages':stages})
    check(data['total_added_candidates']==7056 and data['total_with_base_candidates']==127008,'Added totals')
    return {'schema':'beal.block62.independent_low.v1','status':'PASS_INDEPENDENT_LOW_SUPPORT_EXTENSION',
      'direct_symbols':evaluations,'new_natural_symbols':9,'added_candidates':7056,'stages':stats,
      'note':'Uses the separately verified Frobenius tables; no extra point counts or primary arithmetic imports.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--extension',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=run(json.loads(a.extension.read_text()),json.loads(a.base.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(d['status'])
if __name__=='__main__':main()
