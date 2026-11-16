"""Replay archive sources and compare every available scalar transfer to a Q oracle."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from sequence_atlas import catalogue
from sequence_library import library_entries
from sequence_archive import records
from sequence_research_notes import research_connections

ROOT=Path(__file__).resolve().parents[1]


def product(a,b,L):
    return [sum(a[j]*b[n-j] for j in range(n+1)) for n in range(L)]


def reciprocal(a):
    """Geometric expansion, independent of the JavaScript quotient recurrence."""
    L=len(a);u=[Q(0)]+[-x/a[0] for x in a[1:]]
    power=[Q(1)]+[Q(0)]*(L-1);total=power.copy()
    for _ in range(1,L):
        power=product(power,u,L);total=[x+y for x,y in zip(total,power)]
    return [x/a[0] for x in total]


def checks(node):
    entries=library_entries(catalogue());lookup={e['id']:e for e in entries};seen=Counter()
    assert len(entries)==len(lookup)==2292
    for entry in entries:
        assert type(entry['offset']) is int and entry['terms'] and entry['formulas']
        assert all(str(int(value))==value for value in entry['terms']),entry['id']
        assert all(f['source'].startswith('https://') for f in entry['formulas']),entry['id']
        seen['record_definitions']+=1;seen['stored_integers']+=len(entry['terms'])
    path=ROOT/'research/sequence-archive/generate_candidates.py'
    spec=importlib.util.spec_from_file_location('replayed_candidates',path);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    archive=module.create_catalog();controls=module.independent_tests(archive)
    for original,entry in zip(archive.items,records(catalogue())):
        assert (original.code,original.offset,list(map(str,original.terms)))==(entry['id'],entry['offset'],entry['terms'])
        seen['archive_source_records']+=1;seen['archive_source_terms']+=len(entry['terms'])
    assert seen['archive_source_records']==len(archive.items)==90
    source=next(e for e in entries if e['collection']=='atlas' and e['kind']=='euler')
    run=subprocess.run([node,str(ROOT/'tools/audit_sequence_transfer.mjs')],input=json.dumps(dict(entries=entries,source=source)),capture_output=True,text=True,encoding='utf-8',timeout=180,check=True)
    results=json.loads(run.stdout);assert len(results)==len(entries);excluded=[]
    for result in results:
        if 'excluded' in result:
            excluded.append(dict(id=result['id'],reason=result['excluded']));seen['excluded_'+result['excluded']]+=1;continue
        target=lookup[result['id']];L=result['count'];v=result['sourceAnchor']['position'];w=result['targetAnchor']['position']
        assert v==next(i for i,x in enumerate(source['terms']) if int(x))
        assert w==next(i for i,x in enumerate(target['terms']) if int(x))
        assert result['positionShift']==w-v and result['indexShift']==target['offset']+w-source['offset']-v
        a=list(map(Q,source['terms'][v:v+L]));b=list(map(Q,target['terms'][w:w+L]))
        h=product(b,reciprocal(a),L);k=product(a,reciprocal(b),L)
        assert result['verified'] and len(result['rows'])==L
        for j,row in enumerate(result['rows']):
            assert Q(row['kernel'])==h[j] and Q(row['inverse'])==k[j],(target['id'],j)
            assert Q(row['forward'])==b[j] and Q(row['recovered'])==a[j] and Q(row['residual'])==0
            assert Q(row['identity'])==int(j==0)
            assert row['sourceIndex']==source['offset']+v+j and row['targetIndex']==target['offset']+w+j
            seen['transfer_coefficients']+=1
        assert result['integerKernel']==all(x.denominator==1 for x in h)
        assert result['integerInverse']==all(x.denominator==1 for x in k)
        seen['transfer_pairs']+=1
    edges=research_connections()['edges'];assert len({edge['key'] for edge in edges})==len(edges)
    for edge in edges:
        assert edge['source'] in lookup and edge['target'] in lookup and edge['source_url'].startswith('https://')
        seen['typed_relations']+=1;seen['relation_overlap_values']+=edge['checked_overlaps']
    fib=next(e for e in entries if e['collection']=='atlas' and e['kind']=='fibonacci')
    named=next(result for result in results if result.get('targetId')==fib['id'])
    assert named['targetAnchor']['index']==1
    assert [row['kernel'] for row in named['rows'][:6]]==['1','2','-1','53','-1200','46233']
    return dict(status='passed',checks=dict(seen),archive_generator_controls=controls,excluded=excluded,results_sha256=hashlib.sha256(run.stdout.encode()).hexdigest(),scope='All local record definitions; original archive source replay; every available scalar target against signed-even Euler values, up to 12 anchored coefficients; typed source relations and available overlaps.',non_claims=['Finite transfers do not predict unrecorded values','No universal recurrence equivalence, historical novelty claim or independent manuscript review'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--node',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=checks(args.node);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))
