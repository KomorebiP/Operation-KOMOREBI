#!/usr/bin/env python3
"""Finite mutation controls for expression extraction; not a compiler proof."""
import argparse
import hashlib
import json
from bind_python_source import ROOT
from emit_python_expressions import generate

def main():
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():p.error('--output must be new')
    c=(ROOT/'research/coupled_lab.py').read_bytes().decode('utf-8');f=(ROOT/'research/family_lab.py').read_bytes().decode('utf-8')
    target=(ROOT/'lean/CoupledSourceExpressions.lean').read_bytes().decode('utf-8')
    assert generate(c,f)==target
    cases=[
        ('binomial','c','comb(2*n, 2*i+1)','comb(2*n+1, 2*i+1)'),
        ('array index','c','*u[i]*v[n-1-i]','*u[i]*v[n-i]'),
        ('seed denominator','c','bound = x/(1-x*x)','bound = x/(1+x*x)'),
        ('update sign','c','bound = x*(1+bound*bound)','bound = x*(1-bound*bound)'),
        ('tail exponent','c','tail = majorant*(x/s)**(2*last+3)','tail = majorant*(x/s)**(2*last+1)'),
        ('normalization','f','Q(a, factorial(2*n+1))','Q(a, factorial(2*n))'),
        ('dictionary component','c','"U":(partial[0],partial[0]+tail)','"U":(partial[1],partial[1]+tail)'),
        ('dictionary type','c','"last_index":last','"last_index":x'),
        ('default steps','c','max_steps=20,','max_steps=19,'),
        ('control structure','c','for x in reversed(ladder):','for x in ladder:')]
    records=[]
    for name,where,before,after in cases:
        text=c if where=='c' else f;assert before in text
        changed=text.replace(before,after,1)
        try:
            result=generate(changed if where=='c' else c,changed if where=='f' else f)
            assert result!=target,name
            mechanism='different expression artifact'
        except (ValueError,AttributeError,IndexError,TypeError) as e:
            mechanism='closed-fragment rejection: '+str(e)
        records.append({'name':name,'rejected':True,'mechanism':mechanism})
    assert generate('# comment\n'+c,f)==target
    report={'status':'passed','negative_controls':len(records),'positive_controls':2,'controls':records,
            'artifact_sha256':hashlib.sha256(target.encode('utf-8')).hexdigest(),
            'non_claim':'Finite emitter controls do not prove parser/emitter correctness.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'passed','negative_controls':len(records),'positive_controls':2}))

if __name__=='__main__':main()
