#!/usr/bin/env python3
"""Collect current proof/execution records, not substitute for running their checks.

Collector timing excludes the previously recorded builds and runtime tests.
"""
from __future__ import annotations
import datetime
import hashlib
import json
import platform
import re
import sys
import time
import zipfile
from pathlib import Path
from summarize_v029 import check_record, strip_comments_strings

ROOT = Path(__file__).resolve().parents[1]
RD = ROOT / 'results/v0.30.0'

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))

def canonical(x) -> bytes:
    return (json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False)+'\n').encode()

def main() -> None:
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    tick = time.monotonic()
    baseline = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent/'AVOC_Formal_v0.29.0.zip'
    order = load(RD/'build_order.json')
    assert len(order) == len(set(order)) == 166
    for f in order:
        check_record(load(RD/f'clean_{Path(f).stem}.json'), f,
                     ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean'))

    inventory = load(RD/'declaration_inventory.json')
    expected = {x['qualified_name'] for x in inventory}
    assert len(expected) == len(inventory) == 1612
    check_record(load(RD/'full_axiom_audit.json'), 'AVOC/FullAudit.lean')
    text = (RD/'full_axiom_audit.log').read_text()
    names = re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)", text, re.M)
    assert len(names) == len(expected) and set(names) == expected
    deps = set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]', text, re.S):
        deps.update(x.strip() for x in block.split(',') if x.strip())
    assert deps <= {'propext','Classical.choice','Quot.sound'}, deps
    audit = load(RD/'axiom_audit_summary.json')
    assert audit['passed'] and audit['audited'] == len(inventory)
    assert sorted(deps) == audit['axioms']

    negatives = sorted((ROOT/'tests/negative').glob('*.lean'))
    assert len(negatives) == 84
    for f in negatives:
        rec = load(RD/f'negative_{f.stem}.json')
        log = (ROOT/rec['log']).read_text()
        assert rec['returncode'] != 0 and not rec['timed_out'], str(f)
        assert rec['source_unchanged'] and rec['imports_unchanged'], str(f)
        assert rec['source_before_sha256'] == rec['source_sha256'] == sha(f), str(f)
        assert rec['log_sha256'] == sha(ROOT/rec['log']), str(f)
        assert 'error' in log, str(f)
        assert not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),str(f)
        imports = {}
        for d in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$', f.read_text(), re.M):
            imports[d] = sha(ROOT/'.lake/build/lib/lean'/Path(d.replace('.','/')).with_suffix('.olean'))
        assert imports == rec['import_outputs'], str(f)

    same = 0
    with zipfile.ZipFile(baseline) as z:
        assert z.testzip() is None
        pref = 'AVOC_Formal_v0.29.0/'
        for name in z.namelist():
            rel = name.removeprefix(pref)
            if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ('Audit.lean','FullAudit.lean'):
                assert z.read(name) == (ROOT/rel).read_bytes(), rel
                same += 1
    assert same == 144
    modules = [p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ('Audit.lean','FullAudit.lean')]
    bad=[]; census=[]
    for p in modules:
        source=strip_comments_strings(p.read_text())
        hits=re.findall(r'\b(?:sorry|native_decide|axiom|unsafe)\b|\bby\s+admit\b|^\s*admit\s*$', source, re.M)
        if hits: bad.append([p.name,hits])
        census.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',source,re.M))
    assert not bad, bad
    assert len(census) == len(inventory)
    assert len(modules) == 148

    testdir=RD/'cache_tests'
    tests=load(testdir/'differential_summary.json')
    assert tests['passed'] and tests['requests'] == 1361
    requests=load(testdir/'requests.json'); responses=load(testdir/'responses.json')
    assert len(requests) == len(responses) == tests['requests']
    assert len(tests['invocations']) == (len(requests)+119)//120
    for i, rec in enumerate(tests['invocations']):
        assert rec['returncode'] == 0 and not rec['stderr']
        req_bytes = canonical(requests[120*i:120*(i+1)])
        out_bytes = b''.join(canonical(x) for x in responses[120*i:120*(i+1)])
        assert hashlib.sha256(req_bytes).hexdigest() == rec['request_sha256'], i
        assert hashlib.sha256(out_bytes).hexdigest() == rec['stdout_sha256'], i
    provpaths=[testdir/'differential_provenance.json']
    live=[]
    for group,count in [('basic',6),('economics',6),('integrity',5)]:
        data=load(testdir/f'live_{group}.json')
        assert data['passed'] and data['cases'] == len(data['records']) == count
        assert all(x['passed'] for x in data['records'])
        live.append(data)
        provpaths.append(testdir/f'live_{group}_provenance.json')
    for path in provpaths:
        prov=load(path)
        assert prov['unchanged']
        for name,digest in prov['source_pins'].items(): assert sha(ROOT/name) == digest, (path,name)
    cold=load(testdir/'demo_cold.json'); warm=load(testdir/'demo_warm.json')
    assert cold['generator_executed'] and not warm['generator_executed']
    assert cold['spent']==240 and warm['spent']==149
    assert load(testdir/'demo_warm_ten_calls.json')['net_gain']==1
    assert load(testdir/'demo_optimistic_loss.json')['net_gain']==-75

    pins=load(RD/'dependency_pins.json')
    assert len(pins)==9 and all(x['passed'] for x in pins)
    counts=load(RD/'source_counts.json')
    new=load(RD/'new_declarations.json')
    assert len(new)==64 and counts['total_theorems']==1612
    summary={
        'passed':True, 'release':'0.30.0', 'current_compilations':len(order),
        'theorems':len(inventory), 'new_theorems':len(new), 'axioms':sorted(deps),
        'negative_rejections':len(negatives), 'inherited_unchanged':same,
        'non_audit_modules':len(modules), 'non_audit_source_lines':counts['source_lines'],
        'positive_source_scan_hits':bad, 'dependency_pins':len(pins),
        'differential_requests':tests['requests'],
        'exhaustive_2x2_linear_maps':tests['exhaustive_2x2_linear_maps'],
        'individual_vector_comparisons':tests['individual_vector_comparisons'],
        'live_groups':len(live), 'live_cases':sum(x['cases'] for x in live),
        'baseline_sha256':sha(baseline),
        'interruption_scope':'Initial unsplit live test hit host timeout and was excluded. All 3 final groups and differential suite reran against pinned final source. Publication fixture is a Python exception, not SIGKILL or power failure.',
        'scope':'Fresh local proofs and full axiom/negative checks against pinned caches; new affine cache tests only. Old live/crash/synthesis tests remain historical.'}
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    outs=[RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',
          testdir/'differential_summary.json',*[testdir/f'live_{g}.json' for g in ['basic','economics','integrity']]]
    manifest={
      'schema_version':1, 'claim_id':'AVOC-v030-affine-reuse-and-preflight',
      'repository':{'commit':'archive:'+sha(baseline),'dirty':True},
      'command':'python tools/summarize_v030.py '+str(baseline),
      'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d',
          'mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],
          'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Current-source proofs, all theorem axiom reports, substantive negative errors, exact GF(5) reuse and opportunity gates, protected immutable-store cases. Collector duration excludes earlier proof/test runs.',
          'coefficient_domain':'Generic field algebra; runtime exact GF(5)',
          'conventions':'column vectors; second after first; explicit first/second offsets; full saved certificate validation; nominal dense costs; preflight is a necessary opportunity test, not guaranteed profitability',
          'inputs':['frozen v0.29 archive','4 new Lean modules and executed entrypoint','Python RREF proposer unchanged','independent homogeneous-matrix and image-span oracle','fresh temporary cache stores'],
          'bounds':{'local_targets':166,'theorems':1612,'negative_files':84,'wire_requests':1361,'max_runtime_dimension':8,'exhaustive_2x2_linear_maps':625,'live_cases':17,'seed':20260913},
          'non_claims':['No arbitrary sparse/multistage affine cost optimum','No calibrated physical cost or full metareasoning optimum','No formal filesystem/Python refinement or power-failure guarantee','No fresh mathlib source rebuild','No empirical LLM/autonomous improvement claim']},
      'randomness':{'used':True,'generator':'random.Random in the earlier pinned finite regression','seed':20260913},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-tick,'exit_status':0},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outs],
      'checks':['current source/import/output/log hashes for all local targets','exact named axiom census','all per-file substantive negative records','unchanged inherited proof sources','reconstructed raw differential invocation hashes','final source pins for each split live group','expected positive and negative economics demos'],
      'result':'PASS within the declared proof and bounded implementation scopes',
      'residual_risks':['trusted compiler/kernel and external caches','Python parsing,metering,filesystem and protected host','nominal tariffs omit physical overhead','v1-only adapted manifest validator; metadata alone is not proof']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
