#!/usr/bin/env python3
"""Reconstruct the input fixture from frozen visible source leaves and exact new generators.
No old arithmetic module is imported. New norm-q generators are certificates,
not a claimed exhaustive search; both arithmetic programs verify them.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
GENS={197:[0,1,2,0,2,0],337:[-1,1,-1,3,-1,1],673:[-1,3,-1,1,-1,1],547:[-2,-2,0,0,-2,1],743:[-3,1,-1,-3,1,-3],883:[0,3,0,2,0,4],1933:[-1,2,3,0,1,0]}
def build():
    folder=ROOT/'work80/inputs'
    old=json.loads((folder/'pinned_0_primary79.json').read_text())['restricted_p_tangent']
    fx=json.loads((folder/'pinned_9_fixture70.json').read_text())
    patterns={}
    for line in (folder/'pinned_9_SURVIVORS.md').read_text().splitlines():
        fields=line.split('|')
        if len(fields)==6 and fields[1] in ('A','B','C','D'):
            name=fields[1]
            S=list(map(int,fields[3].split(',')))
            s=list(map(int,fields[4].split(',')))
            if len(S)!=9 or len(s)!=9 or S!=old['patterns'][name]['support']:
                raise ValueError('frozen pattern transcription mismatch')
            patterns[name]={'support':S,'inertia':s}
    if set(patterns)!=set('ABCD'):raise ValueError('missing frozen pattern')
    qs=sorted({q for p in patterns.values() for q in p['support']})
    normals={}
    degree2_proof=(folder/'pinned_11_DEGREE_TWO_RECIPROCITY.md').read_text()
    for fragment in ('q307:  g=5+phi', 'q797:  g=4+phi', 'q1483: g=3+phi'):
        if fragment not in degree2_proof: raise ValueError('degree-two normalization is not pinned')
    # Degree-two normalization is explicitly recorded in the Block68 proof,
    # preserved in the nested checkpoint. The following exact elements also
    # undergo full order and symbol checks in both production implementations.
    for q in qs:
        if q%7==1:
            oldcol=next(x for x in fx['inherited_columns'] if x['q']==q)
            rec={'beta_generator':[oldcol['primitive'],0],'degree':1}
        else:
            rec={'beta_generator':[{307:5,797:4,1483:3}[q],1],'degree':2}
        rec['ordinary_generator_offset']=next(x['generator_offset'] for x in old['residue_data'] if x['q']==q)
        normals[str(q)]=rec
    return {'version':'8.0.0','patterns':patterns,'normalizations':normals,
      'conductor_generators':{str(k):v for k,v in GENS.items()},
      'old_fixed_and_minus_constraints':old,
      'earlier_test_generators':{str(x):fx['generators'][str(x)] for x in (29,71)},
      'earlier_twisted_rows':{str(q):{str(t):next(e for e in fx['inherited_columns'] if e['q']==q)['rows'][str(t)] for t in (29,71)} for q in qs if q%7==1},
      'nonclaims':['No numerical global primitive p0','No actual affine target supplied','No actual deformation or pattern exclusion']}
if __name__=='__main__':
    out=ROOT/'work80/inputs/finite_inputs.json'
    out.write_text(json.dumps(build(),indent=2,sort_keys=True)+'\n')
    print('REBUILT_INPUT_FIXTURE')
