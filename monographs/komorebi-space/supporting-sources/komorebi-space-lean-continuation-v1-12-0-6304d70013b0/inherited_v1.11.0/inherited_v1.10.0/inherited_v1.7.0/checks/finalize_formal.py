#!/usr/bin/env python3
"""Bind completed replay records to current source and theorem inventories."""
from pathlib import Path
import argparse,hashlib,json,re,datetime,sys
from build_concordance import strip_comments
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--labels',nargs='+',required=True);a=ap.parse_args()
    reps=[]
    for label in a.labels:
        p=R/'audit/formal'/label/'receipt.json';d=json.loads(p.read_text())
        if d['status']!='PASS':raise RuntimeError(f'Replay not PASS: {label}')
        for name,h in d['source_sha256'].items():
            if sha(R/'formal'/name)!=h:raise RuntimeError('Current source mismatch: '+name)
        for name,h in d['test_source_sha256'].items():
            if sha(R/'formal'/name)!=h:raise RuntimeError('Current test mismatch: '+name)
        if sha(R/'formal/scripts/ExportAudit.lean')!=d['audit_program_sha256']:
            raise RuntimeError('Audit program changed: '+label)
        for name,h in d['auxiliary_sha256'].items():
            if sha(R/'formal'/name)!=h:raise RuntimeError('Auxiliary source changed: '+name)
        ax=R/'audit/formal'/label/'axioms.json'
        if sha(ax)!=d['axiom_json_sha256']:raise RuntimeError('Axiom report hash mismatch')
        reps.append(d)
    first=reps[0]
    if any(d['source_sha256']!=first['source_sha256'] for d in reps):raise RuntimeError('Replay source versions differ')
    data=json.loads((R/'audit/formal'/a.labels[-1]/'axioms.json').read_text())
    lexical=[]
    for name,h in first['source_sha256'].items():
        p=R/'formal'/name;clean=strip_comments(p.read_text())
        for m in re.finditer(r'\b(theorem|lemma|def|abbrev|structure)\s+([^\s(:{\[]+)',clean):
            lexical.append({'file':'formal/'+name,'kind':m.group(1),'name':m.group(2),'line':clean[:m.start()].count('\n')+1,'sha256':h})
    newmods=['FinitePrefixBoundary','DyadicSupport','ProtectedHilbertRepair','ProtectedLinearCertificates','FiniteRealizationExistence']
    all_theorems=sum(r['kind'] in ['theorem','lemma'] for r in lexical)
    newrows=[r for r in lexical if Path(r['file']).stem in newmods]
    byid={'KS54':'FinitePrefixBoundary','KS55':'DyadicSupport','KS56':'ProtectedHilbertRepair','KS57':'ProtectedLinearCertificates','KS58':'FiniteRealizationExistence'}
    result={'status':'PASS','edition':'1.2.0','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'replays':a.labels,'production_modules':first['production_modules'],'compile_targets_per_replay':first['compile_targets'],
            'declarations_audited':len(data['declarations']),'explicit_named_theorems':all_theorems,
            'new_explicit_named_theorems':sum(r['kind'] in ['theorem','lemma'] for r in newrows),
            'new_indexed_constructions':sum(r['kind'] not in ['theorem','lemma'] for r in newrows),
            'new_modules':newmods,'completed_items':byid,
            'axiom_union':first['axiom_union'],'axiom_report':f'audit/formal/{a.labels[-1]}/axioms.json',
            'positive_files':sum(c['label'].startswith('positive_') for c in reps[-1]['commands']),
            'negative_controls':sum(c['label'].startswith('negative_') for c in reps[-1]['commands']),
            'policy_controls':sum(c['label'].startswith('policy_') for c in reps[-1]['commands']),
            'source_sha256':first['source_sha256'],'trust_boundary':first['trust_boundary']}
    (R/'audit/formal/release.json').write_text(json.dumps(result,indent=2)+'\n')
    (R/'data/canonical_declarations.json').write_text(json.dumps(lexical,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))
if __name__=='__main__':main()
