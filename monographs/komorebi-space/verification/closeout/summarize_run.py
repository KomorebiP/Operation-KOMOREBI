#!/usr/bin/env python3
"""Read and bind a completed unchanged-source Space replay, without rerunning Lean."""
from pathlib import Path
import collections
import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run01'
PUB=ROOT.parent/'formal_work/Komorebi_Space_Publication_v1.15.0'

def load(p):return json.loads(p.read_text())
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    r=load(RUN/'receipt.json');old=load(PUB/'verification/current/INTEGRATED_REPLAY.json')
    assert r['status']=='PASS'
    assert all(r[k] for k in ['source_unchanged','runtime_unchanged','objects_unchanged'])
    assert r['input_sha256']==old['input_sha256'] and len(r['input_sha256'])==229
    for n,h in r['input_sha256'].items():
        assert sha(PUB/n)==sha(RUN/'snapshot'/n)==h,n
    for c in r['commands']:
        assert not c['timeout'] and sha(RUN/c['log'])==c['log_sha256'],c['label']
    assert len(r['commands'])==262
    assert [c['label'] for c in r['commands']]==r['exact_command_labels']
    assert all(c['exit_code']==0 for c in r['commands'] if not c['label'].startswith('control_'))
    assert len(r['controls'])==56 and all(c['passed'] for c in r['controls'])
    for n,h in r['fresh_object_sha256'].items():assert sha(RUN/'build'/n)==h,n
    assert len(r['fresh_object_sha256'])==166
    assert sha(RUN/'declarations.json')==r['declarations_sha256']
    assert sha(RUN/'runtime_snapshot.json')==r['runtime_snapshot_sha256']
    inv=load(RUN/'declarations.json');prior=load(PUB/'verification/current/DECLARATIONS.json')
    def normalize(d):return {x['name']:{k:(sorted(v) if k=='axioms' else v) for k,v in x.items()} for x in d['declarations']}
    assert normalize(inv)==normalize(prior)
    runtime=load(RUN/'runtime_snapshot.json')
    counts=collections.Counter(c['expected'] for c in r['controls'])
    start=datetime.datetime.fromisoformat(r['started_utc']);end=datetime.datetime.fromisoformat(r['finished_utc'])
    out={'schema':'komorebi.space.fresh-release-replay-summary.v1','status':'PASS',
        'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'receipt':'run01/receipt.json','receipt_sha256':sha(RUN/'receipt.json'),
        'source_input_count':len(r['input_sha256']),'source_inputs_identical_to_accepted_predecessor':True,
        'production_modules':r['production_modules'],'entrypoints':len(r['entrypoints']),
        'compiled_targets':r['compile_targets'],'fresh_project_objects':len(r['fresh_object_sha256']),
        'explicit_theorem_lemma_declarations':r['explicit_theorem_lemma_count'],
        'exported_declarations':r['exported_declarations'],
        'compiled_theorem_constants_including_generated':sum(x['kind']=='theorem' for x in inv['declarations']),
        'declaration_records_semantically_identical_to_predecessor':True,
        'command_count':len(r['commands']),'total_seconds':(end-start).total_seconds(),
        'summed_command_seconds':sum(c['seconds'] for c in r['commands']),
        'controls':dict(counts),'all_control_outcomes_expected':True,
        'timed_out_commands':sum(c['timeout'] for c in r['commands']),
        'source_unchanged':r['source_unchanged'],'runtime_unchanged':r['runtime_unchanged'],
        'objects_unchanged':r['objects_unchanged'],'axiom_union':r['axiom_union'],
        'lean_version':r['lean_version'],'dependencies':r['dependencies'],
        'declarations_sha256':r['declarations_sha256'],'runtime_snapshot_sha256':r['runtime_snapshot_sha256'],
        'runtime_file_hash_records':len(runtime['file_sha256']),
        'runtime_symlink_records':len(runtime['symlink_targets']),
        'compile_policy':r['compile_policy'],'timeouts_seconds':r['timeouts_seconds'],
        'setup_record_sha256':sha(ROOT/'RUN01_SETUP.json'),
        'preserved_failed_attempts_in_this_closeout':[],
        'scope':'Actual fresh integrated compilation, recursive axiom audit and mixed diagnostic controls on unchanged accepted sources. No separate leanchecker object replay, independent kernel, upstream source rebuild, or new whole-manuscript semantic audit.'}
    (ROOT/'FRESH_REPLAY_SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
