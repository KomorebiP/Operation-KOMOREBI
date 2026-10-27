#!/usr/bin/env python3
"""Generate typeset counts from successfully executed current reports."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    obj=json.loads((ROOT/path).read_text())
    if obj.get('status')!='PASS':raise ValueError(f'Non-PASS report: {path}')
    return obj
c=load('audit/concordance_result.json')
o=load('audit/exact_examples.json')
r=load('audit/revision_exact.json')
m=load('evidence/moving_v032/audit/publication_fresh_finite/RESULT.json')
f=load('audit/formal/release.json')
e=load('audit/expansion_exact.json')
h=load('audit/deepening_exact.json')
values={'EditionClaims':c['claims'],'EditionReferences':c['references_resolved'],
        'EditionWrittenOnly':c['written_only'],'EditionOriginalChecks':o['assertions'],
        'EditionRecoveredChecks':m['assertions'],'EditionRevisionChecks':r['assertions'],
        'EditionExpansionChecks':e['assertions'],'EditionDeepeningChecks':h['assertions'],
        'EditionTotalChecks':o['assertions']+m['assertions']+r['assertions']+e['assertions']+h['assertions'],
        'EditionFormalModules':f['production_modules'], 'EditionAuditedDeclarations':f['declarations_audited'],
        'EditionNewTheorems':f['new_explicit_named_theorems'], 'EditionFormalTheorems':f['explicit_named_theorems'],
        'EditionNewConstructions':f['new_indexed_constructions'], 'EditionReplays':len(f['replays']),
        'EditionNegativeControls':f['negative_controls']+f['policy_controls']}
(ROOT/'source/edition_stats.tex').write_text('% Generated from current executed reports. Do not hand edit.\n'+
 '\n'.join('\\newcommand{\\'+k+'}{'+format(v,',')+'}' for k,v in values.items())+'\n')
(ROOT/'data/edition_stats.json').write_text(json.dumps(values,indent=2)+'\n')
print(json.dumps(values,indent=2))
