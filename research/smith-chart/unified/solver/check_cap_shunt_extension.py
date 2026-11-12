"""Physical controls and union coverage for both terminal shunt classes."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import cap_shunt_rl_refutation as cap
import shunt_rc_refutation as ind
from reactive_skeletons import generate,no_parallel_same_kind
from exact_phasor import C,response

def main():
    cert=cap.certificate();check=cap.verify(cert)
    assert cert==json.loads((Path(__file__).resolve().parent/'cap_shunt_rl_refutation.json').read_bytes())
    controls=[]
    for mode in ('square','class','shape','margin'):
        bad=deepcopy(cert)
        if mode=='square':bad['proof']['squares'][-1]['weight']='0'
        elif mode=='class':bad['physical_family']='All RLC networks'
        elif mode=='shape':bad['shape_lemma']='UnprovedRule'
        else:bad['margin']='1/1000'
        try:cap.verify(bad)
        except ValueError:controls.append(mode)
        else:raise AssertionError('Corrupted certificate accepted')
    bridge=[('R',1,2,F(2)),('R',2,0,F(3)),('R',1,3,F(5)),
            ('L',3,0,F(7,5)),('L',2,3,F(4,3))]
    graphs=[bridge,[('L',1,2,F(3)),('R',2,0,F(2))],
      [('R',1,0,F(7)),('L',1,0,F(2))],[('R',1,0,F(2))]]
    physical=0
    for graph in graphs:
        for scale in (F(1,10),F(1),F(10)):
            for capacitance in (None,F(1,3),F(7)):
                edges=[(k,u,v,x*scale) for k,u,v,x in graph]
                if capacitance:edges.append(('C',1,0,capacitance))
                values=[]
                for s in cap.SAMPLES:
                    g=response(edges,C(s))['gamma'];assert not g.im
                    values.append((1-g.re)/(1+g.re))
                assert sum(w*y for w,y in zip(cap.WEIGHTS,values))>=0
                physical+=1
    levels=generate(4);rows=[]
    for q in (2,3,4):
        population=[g for g in levels[q] if len({e[0] for e in g})==2 and no_parallel_same_kind(g)]
        left=[g for g in population if ind.covered(g)];right=[g for g in population if cap.covered(g)]
        union=[g for g in population if ind.covered(g) or cap.covered(g)]
        rows.append({'budget':q,'mixed_population':len(population),'inductor_class':len(left),
          'capacitor_class':len(right),'overlap':len(set(left)&set(right)),
          'excluded_union':len(union),'remaining':len(population)-len(union)})
    assert [r['excluded_union'] for r in rows]==[7,26,86]
    assert sum(r['remaining'] for r in rows)==2011
    print(json.dumps({'status':'PASS','refutation':check,'independent_physical_shapes':physical,
      'adversarial_controls':controls,'coverage':rows,'total_mixed_representatives_excluded':119,
      'additional_beyond_inductor_class':59,'remaining_mixed_representatives':2011,
      'scope':'Both quantified physical classes, with overlapping canonical placements counted once; other mixed networks remain unresolved.'},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    main()
