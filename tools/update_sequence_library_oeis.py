"""Compare all local records with one retained official OEIS bulk snapshot."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from sequence_atlas import catalogue
from sequence_archive import records
from sequence_formula_catalogue import expanded_catalogue


def canonical(value):
    negative=value.startswith('-');digits=value.lstrip('+-').lstrip('0') or '0'
    if not digits.isdecimal():
        raise ValueError('Non-integer in OEIS export')
    return ('-' if negative and digits!='0' else '')+digits


def compare(stripped,names,entries,minimum=8,limit=50):
    index=defaultdict(list)
    for entry in entries:
        if len(entry['terms'])>=minimum:
            index[tuple(entry['terms'][:minimum])].append(entry)
    matches={entry['id']:[] for entry in entries};totals={entry['id']:0 for entry in entries};headers=[];count=0
    def rank(hit):return (-hit['matched_terms'],hit['id'],hit['position'])
    with gzip.open(stripped,'rt',encoding='utf-8') as stream:
        for line in stream:
            if line.startswith('#'):
                headers.append(line.rstrip());continue
            if not line.strip():continue
            identifier,raw=line.split(None,1)
            if len(identifier)!=7 or identifier[0]!='A' or not identifier[1:].isdigit():raise ValueError('Malformed OEIS ID')
            values=[canonical(v) for v in raw.strip().strip(',').split(',')];count+=1
            for position in range(len(values)-minimum+1):
                for entry in index.get(tuple(values[position:position+minimum]),()):
                    length=minimum
                    while length<min(len(entry['terms']),len(values)-position) and entry['terms'][length]==values[position+length]:length+=1
                    key=entry['id'];totals[key]+=1
                    matches[key].append(dict(id=identifier,position=position,matched_terms=length))
                    if len(matches[key])>limit*2:matches[key]=sorted(matches[key],key=rank)[:limit]
    for key in matches:matches[key]=sorted(matches[key],key=rank)[:limit]
    wanted={m['id'] for group in matches.values() for m in group};titles={}
    with gzip.open(names,'rt',encoding='utf-8') as stream:
        for line in stream:
            if line.startswith('#') or not line.strip():continue
            identifier,name=line.rstrip().split(None,1)
            if identifier in wanted:titles[identifier]=name
    for group in matches.values():
        for hit in group:hit['name']=titles.get(hit['id'],'Name absent from the names snapshot')
    return dict(schema=1,compared_at=datetime.now(timezone.utc).isoformat(),sequence_count=count,headers=headers,
        method=f'First {minimum} exact local terms at every exported position; extend each hit through all available local terms. Retain the best {limit} hits per local record and report the uncapped count. Excerpt positions are not mathematical offsets.',
        minimum_terms=minimum,retained_limit=limit,matches=matches,total_matches=totals,
        catalogue_terms_sha256=hashlib.sha256(json.dumps([(e['id'],e['terms']) for e in entries],separators=(',',':')).encode()).hexdigest(),
        stripped_sha256=hashlib.sha256(Path(stripped).read_bytes()).hexdigest(),names_sha256=hashlib.sha256(Path(names).read_bytes()).hexdigest(),
        attribution='The Online Encyclopedia of Integer Sequences, OEIS Foundation Inc.',license='CC-BY-SA-4.0',source_urls=['https://oeis.org/stripped.gz','https://oeis.org/names.gz'],
        non_claims=['Finite matches do not prove infinite sequence identity','No novelty or pairwise distinctness claim','The bulk exports do not contain mathematical offsets, full formulas, comments or history'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    base=catalogue();entries=base+records(base)+expanded_catalogue()
    report=compare(args.source/'stripped.gz',args.source/'names.gz',entries)
    snapshot=json.loads((args.source/'snapshot.json').read_text(encoding='utf-8'));report['snapshot']=snapshot
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(sequences_scanned=report['sequence_count'],local_records=len(entries),records_with_matches=sum(bool(x) for x in report['matches'].values()),retained_hits=sum(map(len,report['matches'].values())),observed_hits=sum(report['total_matches'].values()))))
