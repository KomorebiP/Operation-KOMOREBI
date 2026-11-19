"""Audit every generated scalar record-to-family link against its stored prefix.

Design/provenance command:
  python tools/audit_sequence_links.py --node node --write-contract CONTRACT.json

Finite replay command (OUTPUT must be inside the chosen fresh run directory):
  python tools/audit_sequence_links.py --node node --output OUTPUT/result.json

Use the documented bounded runner for before/after input hashes and a v2 manifest.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from urllib.parse import parse_qs, urlparse

from sequence_atlas import catalogue
from sequence_generalized import family_definitions, links_for, membership, source_manifest
from sequence_library import library_entries,verified_oeis_coverage

ROOT=Path(__file__).resolve().parents[1]
ASSERTION=(
    'For every scalar-record family-explorer link generated from the 2,327-record catalogue, '
    'the current exact JavaScript engine accepts its emitted parameters and reproduces every '
    'stored integer, original rational value where recorded, local offset and source degree '
    'in the complete requested prefix, truncated only to the available stored window. '
    'Every compared prefix contains at least eight terms; no sampling of links is used.'
)
NON_CLAIMS=[
    'No claim about coefficients beyond the compared stored prefixes.',
    'No infinite-sequence identity or historical novelty follows from finite agreement.',
    'Definition-only links and analytic families are counted but not numerically evaluated.',
    'Browser layout, events, clipboard and download behavior require separate browser tests.',
    'The Python catalogue is the preserved comparison oracle; this audit does not independently prove every catalogue formula.',
]


class LinkParser(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            values=dict(attrs)
            if values.get('href'):self.links.append(values['href'])


def source_degrees(entry,count):
    """Read the preserved record's coordinate convention, not the URL parameters."""
    indices=range(entry['offset'],entry['offset']+count);kind=entry['kind']
    if entry['collection']=='recovered':
        if kind in ('Euler/block','block powers'):
            match=re.search(r'N=(\d+)',entry['title'])
            if not match:raise ValueError('Archive block spacing missing: '+entry['id'])
            N=int(match.group(1));return [N*n for n in indices]
        if kind=='recurrence':return list(indices)
        raise ValueError('No archived explorer coordinate contract for '+entry['id'])
    if 'source_shift' in entry:return [entry['N']*n+entry['source_shift'] for n in indices]
    if kind=='classical multisection':return [entry['N']*n+entry['j'] for n in indices]
    if kind=='logarithmic companion':return [entry['N']*(n+1)-1 for n in indices]
    if kind in ('euler','Euler-transfer theta','theta polynomial column'):return [2*n for n in indices]
    if kind in ('reciprocal','reciprocal power','secancy parameter column') or kind.startswith('congruential '):return [entry['N']*n for n in indices]
    # Appell point evaluations, ordinary recurrences and curated classical seeds
    # keep their ordinary index, without compressed-degree factorial scaling.
    if kind.startswith('Appell ') or entry.get('linear_addition') or entry['collection']=='atlas':return list(indices)
    raise ValueError('Unspecified source coordinate contract for '+entry['id'])


def build_cases():
    entries=library_entries(catalogue());families={f['id']:f for f in family_definitions()}
    snapshot=json.loads((ROOT/'manifests/sequence-library-oeis.json').read_text(encoding='utf-8'))
    verified_oeis_coverage(entries,snapshot)
    catalogue_hash=snapshot['catalogue_terms_sha256']
    cases=[];definition_only=[];record_ids=set();all_links=0
    for entry in entries:
        parser=LinkParser();parser.feed(links_for(entry))
        if not parser.links or not membership(entry):raise ValueError('Unassigned record '+entry['id'])
        for href in parser.links:
            # HTMLParser has already decoded &amp; once. A second unescape
            # would corrupt the literal query name &parameters via &para.
            all_links+=1;url=urlparse(href);query=parse_qs(url.query)
            if 'parameters' not in query:
                if url.fragment!='definition':raise ValueError('Unexpected non-explorer link '+href)
                definition_only.append(dict(id=entry['id'],href=href));continue
            if url.fragment!='family-explorer':raise ValueError('Wrong explorer anchor '+href)
            family_id=query['family'][0];family=families[family_id]
            if not family['engine']:raise ValueError('Unsupported family engine '+family_id)
            if entry.get('triangle') or entry['index_symbol']=='j':raise ValueError('A triangle was treated as a scalar link')
            parameters=json.loads(query['parameters'][0]);requested=parameters.get('count')
            if type(requested) is not int or requested!=24:raise ValueError('The declared 24-term requested prefix changed; revise the audit contract')
            count=min(requested,len(entry['terms']))
            if count<8:raise ValueError('Fewer than eight preserved terms '+entry['id'])
            rational=entry.get('rational_terms')
            case=dict(case_id=entry['id']+'::'+family_id,record_id=entry['id'],family_id=family_id,
                engine=family['engine'],href=href,parameters=parameters,requested_terms=requested,
                compared_terms=count,offset=entry['offset'],expected_terms=entry['terms'][:count],
                expected_degrees=source_degrees(entry,count),
                expected_rational_terms=[str(Fraction(v)) for v in rational[:count]] if rational is not None else None)
            cases.append(case);record_ids.add(entry['id'])
    if len({case['case_id'] for case in cases})!=len(cases):raise ValueError('Duplicate link cases')
    if len(entries)!=2327 or len(cases)!=2169:raise ValueError('The declared finite population changed; revise the audit contract')
    return dict(schema=1,assertion_tested=ASSERTION,record_count=len(entries),membership_links=all_links,
        explorer_links=len(cases),unique_explorer_records=len(record_ids),definition_only_links=definition_only,
        preserved_catalogue_terms_sha256=catalogue_hash,cases=cases)


def input_paths(contract_path):
    """Declared dependency closure of local imports plus bound source/data files."""
    pending=[Path(__file__).resolve()];seen=set()
    while pending:
        path=pending.pop()
        if path in seen:continue
        seen.add(path)
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else
                [alias.name for alias in node.names] if isinstance(node,ast.Import) else [])
            for name in names:
                candidate=ROOT/'tools'/(name.split('.')[0]+'.py')
                if candidate.is_file() and candidate not in seen:pending.append(candidate)
    paths={path.relative_to(ROOT).as_posix() for path in seen}
    paths.update(['tools/audit_sequence_links.mjs','website/assets/sequence-family-core.mjs',
        'website/assets/sequence-atlas-core.mjs','manifests/sequence-generalized-sources.json',
        'manifests/sequence-library-oeis.json','research/sequence-archive/candidate_registry.json'])
    paths.update(source['path'] for source in source_manifest()['sources'])
    paths.add(contract_path.resolve().relative_to(ROOT).as_posix())
    return sorted(paths)


def write_contract(path,node):
    node_version=subprocess.run([node,'--version'],check=True,capture_output=True,text=True).stdout.strip()
    contract=dict(claim_id='SEQUENCE_EXPLORER_LINKS_2026_11_16',mathematics=dict(
        assertion_tested=ASSERTION,coefficient_domain='Exact integers and reduced rational numbers; no floating tolerance',
        conventions='Decimal strings cross JSON; original local offsets and source-degree maps are compared. Appell columns use polynomial row N*n+k and ordinary [x^k] coefficients. Factorial normalizations belong to the stated source degree. Rational denominators are positive.',
        inputs=['The 2,327 OEIS-compared records, including 35 closed-form records, and every generated family-explorer link.',
            'Independent Python catalogue coefficients and source coordinates versus the actual JavaScript family engine.'],
        bounds=dict(catalogue_records=2327,oeis_pinned_records=2327,generated_explorer_links=2169,minimum_compared_terms=8,
            requested_terms_per_link=24,prefix_rule='min(emitted parameters.count, available stored terms)',
            sampling='none; every emitted link is visited'),non_claims=NON_CLAIMS),
        execution_artifacts=input_paths(path),software=[dict(name='audit Python',version=platform.python_version()),
            dict(name='Node.js',version=node_version)],randomness=dict(used=False,generator='',seed=None))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(contract=str(path),execution_artifacts=len(contract['execution_artifacts']),executed=False)))


def replay(node,output):
    payload=build_cases();raw=json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n'
    output.parent.mkdir(parents=True,exist_ok=True)
    process=subprocess.run([node,str(ROOT/'tools/audit_sequence_links.mjs')],input=raw,text=True,
        encoding='utf-8',capture_output=True,check=True,timeout=210)
    actual=json.loads(process.stdout)
    if actual['cases']!=len(payload['cases']):raise ValueError('Engine returned a different population')
    failures=[];by_engine=Counter();by_length=Counter();total_values=0;rationals=0;details=[]
    for expected,observed in zip(payload['cases'],actual['results'],strict=True):
        if observed['case_id']!=expected['case_id']:raise ValueError('Engine result ordering changed')
        count=expected['compared_terms'];by_engine[expected['engine']]+=1;by_length[count]+=1
        errors=[]
        if observed['status']!='generated':errors.append(dict(field='engine',error=observed.get('error','rejected')))
        else:
            if len(observed['terms'])!=expected['requested_terms']:errors.append(dict(field='returned_term_count'))
            for field,got,want in [
                ('offset',observed['offset'],expected['offset']),
                ('terms',observed['terms'][:count],expected['expected_terms']),
                ('source_degrees',observed['degrees'][:count],expected['expected_degrees']),
            ]:
                if got!=want:errors.append(dict(field=field,expected=want,observed=got))
            if expected['expected_rational_terms'] is not None:
                rationals+=count
                got=(observed.get('rational_terms') or [])[:count]
                if got!=expected['expected_rational_terms']:errors.append(dict(field='rational_terms',expected=expected['expected_rational_terms'],observed=got))
            total_values+=count
        reference=dict(offset=expected['offset'],terms=expected['expected_terms'],
            source_degrees=expected['expected_degrees'],rational_terms=expected['expected_rational_terms'])
        observation=(dict(offset=observed['offset'],terms=observed['terms'][:count],
            source_degrees=observed['degrees'][:count],
            rational_terms=(observed.get('rational_terms') or [])[:count] if reference['rational_terms'] is not None else None)
            if observed['status']=='generated' else dict(error=observed.get('error','rejected')))
        digest=lambda value:sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        details.append(dict(case_id=expected['case_id'],status='failed' if errors else 'passed',compared_terms=count,
            first_index=expected['offset'],last_index=expected['offset']+count-1,
            source_first_degree=reference['source_degrees'][0],source_last_degree=reference['source_degrees'][-1],
            expected_sha256=digest(reference),observed_sha256=digest(observation)))
        if errors:failures.append(dict(case_id=expected['case_id'],errors=errors))
    report=dict(schema=1,status='failed' if failures else 'passed',assertion_tested=ASSERTION,
        record_count=payload['record_count'],membership_links=payload['membership_links'],
        explorer_links=payload['explorer_links'],unique_explorer_records=payload['unique_explorer_records'],
        definition_only_links=len(payload['definition_only_links']),links_by_engine=dict(sorted(by_engine.items())),
        compared_prefix_lengths={str(k):v for k,v in sorted(by_length.items())},exact_integers_compared=total_values,
        original_rationals_compared=rationals,source_degrees_compared=total_values,
        local_offsets_compared=sum(item['status']=='generated' for item in actual['results']),
        preserved_catalogue_terms_sha256=payload['preserved_catalogue_terms_sha256'],
        failures=failures,cases=details,
        input_payload_sha256=sha256(raw.encode('utf-8')).hexdigest(),
        engine_results_sha256=sha256(process.stdout.encode('utf-8')).hexdigest(),non_claims=NON_CLAIMS)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('status','record_count','explorer_links','definition_only_links',
        'exact_integers_compared','original_rationals_compared','source_degrees_compared','compared_prefix_lengths')}
        |dict(failures=len(failures),report=str(output))))
    return 1 if failures else 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--node',required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write-contract',type=Path);group.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.write_contract:write_contract(args.write_contract,args.node)
    else:raise SystemExit(replay(args.node,args.output))
