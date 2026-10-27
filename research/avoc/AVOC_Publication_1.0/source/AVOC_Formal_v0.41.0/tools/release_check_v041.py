#!/usr/bin/env python3
"""Fail-closed release gate: exact current sources, evidence membership and dependencies."""
import json, re, subprocess, sys
from pathlib import Path
from release_common_v041 import ROOT,RD,BASE_SHA256,BASELINE_RECORD_SHA256,RELEASE_TOOLS,sha,write_json,build_graph,build_record_errors,kit_path
from inventory_v041 import collect as inventory_collect
from source_scan_v041 import collect as scan_collect
from run_negative_v041 import valid as negative_valid
from verify_v041 import audit_summary

def recorder_oracle_errors(oracle):
    """Require the declared executable comparisons, not a generic passed flag."""
    problems=[]
    expected_sources={
        'checks/test_observation_recorder.py','tools/observation_recorder.py',
        'tools/run_recorder_lean.py','tools/calibrate_quote.py',
        'AVOC/ObservationRecorder.lean','AVOC/RecorderReveal.lean',
        'AVOC/RecorderCodec.lean','tools/RecorderMain.lean',
        'examples/observation_recorder/scenarios.json',
        'examples/observation_recorder/registry.json',
        'examples/observation_recorder/complete.json',
        'examples/observation_recorder/pending.json',
    }
    if set(oracle.get('source_sha256',{}))!=expected_sources:
        problems.append('recorder oracle input membership differs from declared experiment')
    expected={
        'finite_oracle':dict(status='passed',alphabet_size=16,operation_ids=[0,1],
            keys=[0,1],word_lengths=[0,4],word_count=69905,longer_scenarios=12),
        'interface':dict(status='passed',invalid_structures=20,invalid_raw_json=7,
            resource_rejections=3,boundary_acceptances=4,file_checks=4),
        'calibration_export':dict(status='passed',checks=16,terminal_events=4,
            checked_prefix={'n':2,'successes':1},old_intent_then_terminal_rejected=True,
            global_pending_blocks_export=True,authentication_established=False),
        'actual_lean':dict(status='passed',exhaustive_words=4369,word_lengths=[0,3],
            longer_scenarios=12,total_words=4381,invalid_structure_checks=22,
            valid_boundary_checks=4,per_call_timeout_seconds=180,
            comparison='exact parsed JSON equality'),
    }
    for section,fields in expected.items():
        actual=oracle.get(section)
        if not isinstance(actual,dict):
            problems.append('missing recorder oracle section: '+section);continue
        for key,value in fields.items():
            if actual.get(key)!=value:problems.append('recorder oracle incomplete/mismatched '+section+'.'+key)
    finite=oracle.get('finite_oracle',{})
    statuses=finite.get('status_counts',{}) if isinstance(finite,dict) else {}
    if not isinstance(statuses,dict) or set(statuses)!={'recorded','rejected'} or any(type(v) is not int or v<=0 for v in statuses.values()) or sum(statuses.values())!=69905:
        problems.append('recorder oracle does not account for all finite outcomes')
    actual_lean=oracle.get('actual_lean',{})
    batches=actual_lean.get('batches',[]) if isinstance(actual_lean,dict) else []
    if not isinstance(batches,list) or len(batches)!=18:
        problems.append('actual Lean batch count mismatch')
    else:
        position=0
        for batch in batches:
            if not isinstance(batch,dict):problems.append('malformed actual Lean batch');continue
            count=batch.get('count')
            if batch.get('start')!=position or type(count) is not int or not 0<count<=256:
                problems.append('actual Lean batches have missing/overlapping/invalid ranges')
            else:position+=count
            for key in ('request_sha256','response_sha256'):
                if not isinstance(batch.get(key),str) or re.fullmatch(r'[0-9a-f]{64}',batch[key]) is None:
                    problems.append('actual Lean batch lacks '+key)
            if not isinstance(batch.get('runtime_seconds'),(int,float)) or batch['runtime_seconds']<0:
                problems.append('actual Lean batch lacks elapsed time')
        if position!=4381:problems.append('actual Lean batch membership does not cover 4381 words')
    return problems

def main():
    errors=[]; evidence={}; targets=[]
    def load(relative):
        path=ROOT/relative
        if not path.is_file():errors.append('missing evidence: '+relative);return None
        evidence[relative]=sha(path)
        try:value=json.loads(path.read_text())
        except ValueError as error:errors.append('invalid evidence JSON: '+relative+': '+str(error));return None
        expected_type=list if relative in {'results/v0.41.0/build_order.json','results/v0.41.0/declaration_inventory.json'} else dict
        if not isinstance(value,expected_type) or not value:
            errors.append('empty or wrong-type evidence: '+relative);return None
        return value
    def check_hashes(label, mapping):
        if not isinstance(mapping,dict) or not mapping:errors.append(label+' has no source/output hashes');return
        for source,digest in mapping.items():
            path=ROOT/source
            if not path.is_file() or sha(path)!=digest:errors.append(label+' stale/missing file: '+source)
    def current_record(source,relative,output=True):
        record=load(relative)
        if record is None:return False
        problems=build_record_errors(source,record,output=output)
        if pins and record.get('lean_executable_sha256')!=pins.get('lean_executable_sha256'):problems.append('different Lean executable')
        if problems:errors.append(dict(target=source,problems=problems))
        return not problems
    baseline=load('results/v0.41.0/release_baseline.json')
    inherited_modules={}
    if baseline:
        if evidence.get('results/v0.41.0/release_baseline.json')!=BASELINE_RECORD_SHA256 or baseline.get('base_archive_sha256')!=BASE_SHA256:
            errors.append('baseline archive record differs from exact v0.40 source')
        inherited_modules=baseline.get('inherited_non_audit_sha256',{})
        if len(inherited_modules)!=191:errors.append('baseline module count is not 191')
        check_hashes('historical release evidence',baseline.get('historical_evidence_sha256'))
        check_hashes('inherited runtime sources',baseline.get('inherited_runtime_sha256'))
        check_hashes('inherited mathematical sources',inherited_modules)
    order,deps=build_graph(); recorded_order=load('results/v0.41.0/build_order.json')
    if recorded_order!=order:errors.append('build target/order membership differs from current sources')
    pins=load('results/v0.41.0/dependency_pins.json')
    manifest=json.loads((ROOT/'lake-manifest.json').read_text())['packages']
    if pins:
        expected={p['name']:p['rev'] for p in manifest};actual={p['name']:p['actual'] for p in pins.get('pins',[])}
        if len(expected)!=9 or len(pins.get('pins',[]))!=9 or expected!=actual or not pins.get('passed'):errors.append('not exactly nine matching dependency pins')
        if pins.get('manifest_sha256')!=sha(ROOT/'lake-manifest.json') or pins.get('toolchain_sha256')!=sha(ROOT/'lean-toolchain'):errors.append('dependency metadata changed')
        try:
            kit=kit_path()
            if sha(kit/'toolchain/bin/lean')!=pins.get('lean_executable_sha256'):errors.append('Lean executable changed')
            for name,revision in expected.items():
                directory=kit/'workspace/.lake/packages'/name
                current=subprocess.check_output(['git','-c',f'safe.directory={directory}','-C',str(directory),'rev-parse','HEAD'],text=True).strip()
                if current!=revision:errors.append('current dependency pin changed: '+name)
        except (OSError,RuntimeError,subprocess.CalledProcessError) as error:errors.append('cannot verify current runtime: '+str(error))
    for source in order:
        relative=f'results/v0.41.0/clean_{Path(source).stem}.json'
        passed=current_record(source,relative)
        targets.append(dict(source=source,passed=passed,record_sha256=evidence.get(relative)))
    inventory=load('results/v0.41.0/declaration_inventory.json')
    actual_inventory,old_inventory=inventory_collect()
    if inventory!=actual_inventory:errors.append('named declaration inventory differs from current sources')
    counts=load('results/v0.41.0/source_counts.json')
    if counts:
        if counts.get('total_named_theorems')!=len(actual_inventory):errors.append('source count mismatch')
        check_hashes('source inventory',counts.get('source_sha256'))
    audit=load('results/v0.41.0/axiom_audit_summary.json');audit_log=RD/'full_axiom_audit.log'
    if audit:
        if not audit_log.is_file():errors.append('missing full axiom audit log')
        else:
            recomputed=audit_summary(audit_log.read_text(),actual_inventory)
            if not recomputed['passed'] or any(audit.get(key)!=value for key,value in recomputed.items()):errors.append('full axiom audit content/membership mismatch')
            if audit.get('inventory_sha256')!=sha(RD/'declaration_inventory.json') or audit.get('audit_source_sha256')!=sha(ROOT/'AVOC/FullAudit.lean'):errors.append('axiom audit inventory/source changed')
            if audit.get('audit_record_sha256')!=sha(RD/'full_axiom_audit.json'):errors.append('axiom audit record changed')
        current_record('AVOC/FullAudit.lean','results/v0.41.0/full_axiom_audit.json',output=False)
    negatives=load('results/v0.41.0/negative_all/summary.json')
    negative_sources=sorted((ROOT/'tests/negative').rglob('*.lean'))
    expected_negative={p.relative_to(ROOT).as_posix() for p in negative_sources}
    if negatives:
        records=negatives.get('records',[])
        if {r.get('source') for r in records}!=expected_negative or len(records)!=len(expected_negative):errors.append('negative suite membership mismatch')
        if negatives.get('total')!=len(expected_negative) or negatives.get('substantive_rejections')!=len(expected_negative) or not negatives.get('complete'):errors.append('negative suite incomplete')
        for source in negative_sources:
            if not negative_valid(source):errors.append('negative failure stale or not substantive: '+source.relative_to(ROOT).as_posix())
            negative_record=load(f'results/v0.41.0/negative_all/{source.stem}.json')
            if negative_record and pins and negative_record.get('lean_executable_sha256')!=pins.get('lean_executable_sha256'):
                errors.append('negative proof used a different Lean executable: '+source.relative_to(ROOT).as_posix())
    scan=load('results/v0.41.0/source_scan.json');current_scan=scan_collect()
    if scan!=current_scan or current_scan['hits']:errors.append('source shortcut scan stale or contains forbidden tokens')
    identity=load('results/v0.41.0/inherited_source_identity.json')
    if identity:
        records=identity.get('records',[])
        if identity.get('base_archive_sha256')!=BASE_SHA256 or identity.get('total')!=191 or identity.get('byte_identical')!=191 or not identity.get('passed') or len(records)!=191 or len({r['source'] for r in records})!=191:errors.append('inherited non-audit module membership/count mismatch')
        if {r.get('source'):r.get('sha256') for r in records}!=inherited_modules:errors.append('inherited identity differs from exact archive membership/digests')
        for record in records:
            if not (ROOT/record['source']).is_file() or sha(ROOT/record['source'])!=record['sha256']:errors.append('inherited module changed: '+record['source'])
    archived_oracle=load('results/v0.40.0/oracle_results.json')
    if archived_oracle:
        if archived_oracle.get('status')!='passed':errors.append('archived observation oracle did not pass')
        check_hashes('archived observation oracle current inputs',archived_oracle.get('source_sha256'))
    oracle=load('results/v0.41.0/oracle_results.json')
    if oracle:
        if oracle.get('status')!='passed':errors.append('recorder oracle did not pass')
        errors.extend(recorder_oracle_errors(oracle))
        check_hashes('recorder oracle',oracle.get('source_sha256'))
        if oracle.get('output_sha256'):check_hashes('recorder oracle outputs',oracle['output_sha256'])
        runtime=oracle.get('actual_lean',{}).get('runtime_provenance',{})
        if not isinstance(runtime,dict) or not runtime:
            errors.append('recorder oracle lacks actual runtime provenance')
        else:
            closure=set()
            def visit_runtime(source):
                if source in closure:return
                closure.add(source)
                for dependency in deps.get(source,set()):visit_runtime(dependency)
            visit_runtime('tools/RecorderMain.lean')
            expected_objects={'.lake/build/lib/lean/'+str(Path(source).with_suffix('.olean')) for source in closure}
            if set(runtime.get('local_source_sha256',{}))!=closure or runtime.get('local_module_count')!=len(closure):
                errors.append('recorder oracle runtime source closure mismatch')
            if set(runtime.get('local_olean_sha256',{}))!=expected_objects:
                errors.append('recorder oracle compiled import closure mismatch')
            check_hashes('recorder oracle runtime sources',runtime.get('local_source_sha256'))
            check_hashes('recorder oracle runtime compiled imports',runtime.get('local_olean_sha256'))
            if not isinstance(runtime.get('lean_executable'),str) or not runtime['lean_executable']:
                errors.append('recorder oracle lacks Lean executable identity')
            if pins and runtime.get('lean_sha256')!=pins.get('lean_executable_sha256'):
                errors.append('recorder oracle used a different Lean executable')

    oracle_manifest=load('results/v0.41.0/oracle_run/manifest.json')
    if oracle_manifest:
        run=oracle_manifest.get('run',{})
        if oracle_manifest.get('schema_version')!=2 or run.get('status')!='completed' or run.get('exit_status')!=0 or run.get('missing_results')!=[] or run.get('invalid_results')!=[]:errors.append('bounded oracle execution did not complete cleanly')
        checks=oracle_manifest.get('checks',[])
        if not checks or not all(record.get('passed') for record in checks):errors.append('bounded oracle manifest checks failed')
        inputs=oracle_manifest.get('input_artifacts',[])
        check_hashes('bounded oracle inputs',{record['path']:record['sha256'] for record in inputs})
        if any(record.get('sha256_after')!=record.get('sha256') for record in inputs):errors.append('bounded oracle inputs changed while running')
        if oracle and {record['path']:record['sha256'] for record in inputs}!=oracle.get('source_sha256'):errors.append('bounded oracle input membership differs from result source membership')
        outputs=oracle_manifest.get('outputs',[])
        check_hashes('bounded oracle outputs',{record['path']:record['sha256'] for record in outputs})
        if set(oracle_manifest.get('declared_results',[]))!={'results/v0.41.0/oracle_run/oracle_results.json'}:errors.append('bounded oracle result membership mismatch')
        if {record['path'] for record in outputs if record.get('kind')=='result'}!={'results/v0.41.0/oracle_run/oracle_results.json'}:errors.append('bounded oracle output result membership mismatch')
    provenance=load('results/v0.41.0/oracle_provenance.json')
    if provenance:
        canonical=RD/'oracle_results.json';bounded=RD/'oracle_run/oracle_results.json'
        if provenance.get('status')!='passed' or not provenance.get('canonical_copy_equal') or not canonical.is_file() or not bounded.is_file() or sha(canonical)!=sha(bounded) or sha(canonical)!=provenance.get('sha256'):errors.append('canonical oracle differs from bounded-run evidence')
    inherited=load('results/v0.41.0/inherited_regression_summary.json')
    if inherited:
        expected_cases={'oracle','workflow','recovery','lazy','calibration'};cases=inherited.get('cases',[])
        if not inherited.get('all_passed') or {r.get('case') for r in cases}!=expected_cases or len(cases)!=len(expected_cases) or not all(r.get('passed') for r in cases):errors.append('inherited regressions incomplete/failed')
        check_hashes('inherited regressions',inherited.get('source_sha256'));check_hashes('inherited outputs',inherited.get('output_sha256'))
        for record in cases:
            if not (ROOT/record['source']).is_file() or sha(ROOT/record['source'])!=record.get('source_sha256'):errors.append('inherited check source changed: '+record['source'])
        run=inherited.get('run_directory','__missing__');regression=load(run+'/calibration_regression.json')
        if regression:
            if regression.get('status')!='passed' or regression.get('lean_crosscheck',{}).get('status')!='passed' or regression.get('lean_replanning',{}).get('status')!='passed' or not regression.get('interface') or not all(r.get('status')=='passed' for r in regression['interface']):errors.append('inherited calibration regression incomplete/failed')
            check_hashes('inherited calibration regression',regression.get('source_sha256'))
    review=load('results/v0.41.0/independent_review.json')
    if review:
        if review.get('status')!='passed' or review.get('open_blockers')!=[]:errors.append('independent review is not closed')
        check_hashes('independent review',review.get('source_sha256'))
        check_hashes('independently reviewed release tools',review.get('reviewed_tool_sha256'))
        if not RELEASE_TOOLS<=review.get('reviewed_tool_sha256',{}).keys():errors.append('independent review omits required release tool(s)')
        if review.get('artifacts_sha256'):check_hashes('independent review artifacts',review['artifacts_sha256'])
        new_modules={source for source in order if source.startswith('AVOC/') and source not in inherited_modules}
        if not new_modules<=review.get('source_sha256',{}).keys():errors.append('independent review omits new mathematical module(s)')
    review_text=RD/'INDEPENDENT_REVIEW.md'
    if not review_text.is_file() or not review_text.read_text().strip():errors.append('missing independent review explanation')
    else:evidence[review_text.relative_to(ROOT).as_posix()]=sha(review_text)
    result=dict(version='0.41.0',passed=not errors,errors=errors,targets=len(order),targets_passed=sum(t['passed'] for t in targets),
                named_theorem_reports=len(actual_inventory),axiom_union=audit.get('axiom_union',[]) if audit else [],
                negative_tests=len(expected_negative),substantive_negative_rejections=negatives.get('substantive_rejections',0) if negatives else 0,
                inherited_non_audit_modules=191,source_counts=counts,build_records=targets,evidence_sha256=evidence)
    write_json(RD/'release_verification.json',result)
    print(json.dumps({key:value for key,value in result.items() if key not in {'build_records','evidence_sha256','source_counts'}},indent=2))
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
