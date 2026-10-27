#!/usr/bin/env python3
"""Collect current proof/runtime evidence; never count historical logs or timeouts as success."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from summarize_v022 import without_comments

ROOT = Path(__file__).resolve().parents[1]
RD = ROOT / 'results/v0.27.0'
ALLOWED = {'propext','Classical.choice','Quot.sound'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def current_imports(src: Path) -> dict[str, str]:
    names = re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$', src.read_text(), re.M)
    return {n: sha(ROOT/'.lake/build/lib/lean'/Path(n.replace('.','/')).with_suffix('.olean')) for n in names}


def checked_record(src: Path, record_path: Path, output: Path | None = None,
                   positive: bool = True) -> dict:
    record = read(record_path)
    require(not record['timed_out'], f'timeout: {record_path.name}')
    require((record['returncode'] == 0) == positive, f'wrong status: {record_path.name}')
    require(record.get('source_unchanged') and record.get('imports_unchanged'), f'input drift: {src}')
    require(record['source_sha256'] == sha(src) == record['source_before_sha256'], f'stale source: {src}')
    log = ROOT/record['log']
    require(record['log_sha256'] == sha(log), f'changed log: {log}')
    require(record['import_outputs'] == current_imports(src), f'stale imports: {src}')
    if output is not None:
        require(record['output_sha256'] == sha(output), f'stale output: {output}')
    if not positive:
        text = log.read_text()
        require('error:' in text, f'no substantive error: {src}')
        require(not re.search(r'object file .*does not exist|unknown module|failed to locate application|unknown package', text), f'setup rejection: {src}')
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    args = parser.parse_args()
    order = read(RD/'build_order.json')
    builds = []
    for rel in order:
        src = ROOT/rel
        record = checked_record(src, RD/f'clean_{src.stem}.json',
                                ROOT/'.lake/build/lib/lean'/Path(rel).with_suffix('.olean'))
        builds.append({'source':rel,'source_sha256':sha(src),'record':f'results/v0.27.0/clean_{src.stem}.json',
                       'returncode':record['returncode'],'output_sha256':record['output_sha256']})
    checked_record(ROOT/'AVOC/FullAudit.lean', RD/'full_axiom_audit.json')
    audit_text = (RD/'full_axiom_audit.log').read_text()
    reported = re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)", audit_text, re.M)
    inventory = read(RD/'declaration_inventory.json')
    require(len(reported) == len(inventory) and set(reported) == {x['qualified_name'] for x in inventory}, 'audit name set mismatch')
    axioms = set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]', audit_text, re.S):
        axioms.update(x.strip() for x in block.split(',') if x.strip())
    require(axioms <= ALLOWED, 'unexpected foundational axiom: '+str(axioms-ALLOWED))
    negatives=[]
    for src in sorted((ROOT/'tests/negative').glob('*.lean')):
        rec=checked_record(src,RD/f'negative_{src.stem}.json',positive=False)
        negatives.append({'source':str(src.relative_to(ROOT)),'returncode':rec['returncode'],
                          'log':rec['log'],'source_sha256':sha(src),'log_sha256':rec['log_sha256']})
    modules=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ('FullAudit.lean','Audit.lean')]
    census=[]; forbidden=[]
    for src in modules + list((ROOT/'tools').glob('*.lean')):
        text=without_comments(src.read_text())
        if src in modules:
            census.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',text,re.M))
        for pattern in [r'\bsorry\b',r'\bnative_decide\b',r'(?m)^\s*(?:unsafe\s+|axiom\s+)',
                        r'(?m)^\s*admit\s*$',r':=\s*admit\b']:
            if re.search(pattern,text):forbidden.append((str(src.relative_to(ROOT)),pattern))
    require(not forbidden,'forbidden positive shortcut: '+str(forbidden))
    require(len(census)==len(inventory),'independent theorem census mismatch')
    inherited={}
    with zipfile.ZipFile(args.baseline) as z:
        require(z.testzip() is None,'baseline ZIP integrity failed')
        for member in z.namelist():
            if re.fullmatch(r'[^/]+/AVOC/[^/]+\.lean',member) and Path(member).name not in ('Audit.lean','FullAudit.lean'):
                rel='/'.join(member.split('/')[1:]);raw=z.read(member)
                require((ROOT/rel).read_bytes()==raw,'inherited source changed: '+rel)
                inherited[rel]=hashlib.sha256(raw).hexdigest()
        require('AVOC_Formal_v0.26.0/AVOC/RecursiveSynthesis.lean' in z.namelist(),'wrong v0.26 branch')
    pins=read(RD/'dependency_pins.json')
    require(len(pins)==9 and all(x['passed'] and x['expected']==x['actual'] for x in pins),'dependency revision check failed')
    for rel,digest in read(ROOT/'library_source_pins.json').items():
        require(sha(ROOT/rel)==digest,'changed reviewed runtime source '+rel)
    test_source=ROOT/'checks/test_global_library.py'
    wire=read(RD/'library_tests/wire_summary.json')
    store=read(RD/'library_tests/store_summary.json')
    for label,s in [('wire',wire),('store',store)]:
        require(s['passed'],'failed '+label+' regression')
        require(s['source_sha256']==sha(test_source),'changed test source since '+label+' run')
    require(wire['returncode']==0 and not wire['timed_out'],'wire execution failed')
    require(wire['request_sha256_before']==wire['request_sha256_after']==sha(RD/'library_tests/wire_requests.json'),'wire request changed')
    require(wire['stdout_sha256']==sha(RD/'library_tests/wire_stdout.jsonl'),'wire output changed')
    require(all(c['passed'] for c in wire['cases_detail']) and all(c['passed'] for c in store['case_details']),'test detail mismatch')
    outputs=[json.loads(x) for x in (RD/'library_tests/wire_stdout.jsonl').read_text().splitlines() if x.strip()]
    require(len(outputs)==wire['cases'],'wire case count')
    require(outputs[0]['status']=='globally_certified','concrete certificate not executed successfully')
    cert_path=ROOT/'examples/library/global.json'
    cert=read(cert_path);rows=cert[4]
    require(len(rows)==256 and sum(row[1] for row in rows)==1640 and max(row[1] for row in rows)==10,'concrete bank stats drift')
    require(cert_path.read_bytes()==(ROOT/'examples/library/lean_depth3.json').read_bytes(),'independent/cold producer witnesses differ')
    cold=read(RD/'cold_lean_record.json')
    require(cold['returncode']==0 and not cold['timed_out'],'cold producer did not finish')
    require(cold['source_sha256']==sha(ROOT/'AVOC/SemanticSynthesisRuntime.lean'),'cold producer source drift')
    require(cold['output_sha256']==sha(RD/'cold_lean_stdout.json'),'cold output drift')
    recheck=read(RD/'validated_lean_depth3.json')
    require(recheck['status']=='globally_certified' and recheck['validation_charged']==210245,'fresh exported bank not accepted')
    probe=read(RD/'kernel_table_probe.json')
    require(probe['timed_out'] and probe['returncode']!=0,'optional probe status unexpectedly changed')
    require(sha(RD/'experiments/KernelTableProbe.lean.txt')==probe['source_sha256'],'failed probe source mismatch')
    require(probe['log_sha256']==sha(RD/'kernel_table_probe.log'),'failed probe log mismatch')
    counts=read(RD/'source_counts.json')
    require(counts['total_theorems']==len(inventory) and counts['non_audit_modules']==len(modules),'source count mismatch')
    require(len(inherited)==counts['non_audit_modules']-len(counts['new_modules']),'inherited module count mismatch')
    summary={
      'passed':True,'collected_at_utc':datetime.now(timezone.utc).isoformat(),
      'version':'0.27.0','baseline_branch':'semantic-feedback v0.26; alternate rewrite branch unmerged',
      'baseline_sha256':sha(args.baseline),'source_counts':counts,
      'local_compilation_targets':len(builds),'theorem_axiom_reports':len(reported),
      'axioms':sorted(axioms),'negative_rejections':len(negatives),
      'inherited_non_audit_modules_unchanged':len(inherited),'source_shortcut_scan_hits':forbidden,
      'wire_cases':wire['cases'],'funded_global_queries_checked':wire['successful_query_comparisons'],
      'individual_truth_comparisons':wire['individual_truth_comparisons'],'store_cases':store['cases'],
      'certificate':{'sha256':sha(cert_path),'bytes':cert_path.stat().st_size,'entries':len(rows),
          'sum_costs':sum(row[1] for row in rows),'max_cost':max(row[1] for row in rows),
          'histogram':dict(sorted(Counter(row[1] for row in rows).items())),
          'constructor_inequalities':196869,'validation_tariff':210245,
          'actual_lean_import':'PASS','independent_size_layer_oracle':'PASS',
          'fresh_lean_generator_matches_python_producer':True},
      'optional_monolithic_kernel_table_proof':{'status':'TIMED_OUT_NOT_PROVED','seconds':probe['seconds'],
          'record':'results/v0.27.0/kernel_table_probe.json'},
      'scope':'Current local proof sources and full axiom census compiled against pinned external caches; executed proved certificate checker and bounded Python/IO regressions. No full mathlib rebuild, static concrete-table kernel certificate, old live/crash suite rerun, physical speedup, or empirical LLM result.'}
    (RD/'final_build_records.json').write_text(json.dumps(builds,indent=2)+'\n')
    (RD/'negative_final.json').write_text(json.dumps(negatives,indent=2)+'\n')
    (RD/'inherited_source_hashes.json').write_text(json.dumps(inherited,indent=2)+'\n')
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
