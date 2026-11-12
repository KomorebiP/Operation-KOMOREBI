"""Independent physical shape checks and coverage of the shunt-L extension."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
from shunt_rc_refutation import certificate,verify,covered
from reactive_skeletons import generate,no_parallel_same_kind
from parallel_refutation import WEIGHTS,SAMPLES
from exact_phasor import C,response

def main():
    cert=certificate();consumer=verify(cert)
    retained=json.loads((Path(__file__).resolve().parent/'shunt_rc_refutation.json').read_bytes())
    assert cert==retained
    for mode in ('square','family','shape_rule'):
        bad=deepcopy(cert)
        if mode=='square':bad['proof']['squares'][-1]['weight']='0'
        elif mode=='family':bad['physical_family']='All mixed RLC networks'
        else:bad['shape_lemma']='UnprovedRule'
        try:verify(bad)
        except ValueError:pass
        else:raise AssertionError('Mutated proof or class accepted')
    bridge=[('R',1,2,F(2)),('R',2,0,F(3)),('R',1,3,F(5)),
            ('C',3,0,F(7,5)),('C',2,3,F(4,3))]
    graphs=[bridge,[('C',1,2,F(3)),('R',2,0,F(2))],
        [('R',1,0,F(7)),('C',1,0,F(2))],[('R',1,0,F(2))]]
    physical=0
    for graph in graphs:
        for scale in (F(1,10),F(1),F(10)):
            for L in (None,F(1,3),F(7)):
                edges=[(k,u,v,x*scale) for k,u,v,x in graph]
                if L:edges.append(('L',1,0,L))
                values=[]
                for s in SAMPLES[:4]:
                    g=response(edges,C(s))['gamma'];assert not g.im
                    values.append((1-g.re)/(1+g.re))
                assert sum(w*y for w,y in zip(WEIGHTS,values))<=0
                physical+=1
    outside=[('C',1,0,F(1)),('R',1,2,F(1)),('L',2,0,F(1))]
    outside_values=[]
    for s in SAMPLES[:4]:
        g=response(outside,C(s))['gamma'].re
        outside_values.append((1-g)/(1+g))
    outside_stencil=sum(w*y for w,y in zip(WEIGHTS,outside_values))
    assert outside_stencil>0  # The necessary shape must not be extended to this class.
    levels=generate(4);rows=[]
    for q in (2,3,4):
        population=[g for g in levels[q] if len({e[0] for e in g})==2 and no_parallel_same_kind(g)]
        hits=[g for g in population if covered(g)]
        rows.append({'budget':q,'mixed_population':len(population),'covered':len(hits),
            'remaining':len(population)-len(hits)})
    assert [r['covered'] for r in rows]==[4,13,43]
    assert sum(r['remaining'] for r in rows)==2070
    print(json.dumps({'status':'PASS','refutation':consumer,'independent_physical_shapes':physical,
      'adversarial_controls':3,'coverage':rows,'total_mixed_representatives_excluded':60,
      'additional_beyond_original_parallel_case':59,'remaining_mixed_representatives':2070,
      'complementary_class_positive_stencil':str(outside_stencil),
      'scope':'Coverage counts are exact consequences of the earlier canonical graph enumeration; the class proof allows arbitrarily many RC branches.'},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
