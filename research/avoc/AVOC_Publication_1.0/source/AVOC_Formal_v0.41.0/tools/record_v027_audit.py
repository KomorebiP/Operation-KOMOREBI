#!/usr/bin/env python3
"""Record a timed fresh evidence collection, not fictional timing of earlier builds/tests."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.27.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True);a=ap.parse_args()
    inputs=sorted([*ROOT.glob('AVOC/*.lean'),ROOT/'AVOC.lean',ROOT/'checks/test_global_library.py',
        ROOT/'tools/global_library.py',ROOT/'tools/SemanticLibraryMain.lean',ROOT/'library_source_pins.json',
        ROOT/'examples/library/global.json'])
    before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    started=datetime.now(timezone.utc).isoformat();t=time.perf_counter()
    cmd=[sys.executable,str(ROOT/'tools/summarize_v027.py'),'--baseline',str(a.baseline.resolve())]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=60)
    elapsed=time.perf_counter()-t
    (RD/'collector_stdout.json').write_text(p.stdout);(RD/'collector_stderr.txt').write_text(p.stderr)
    after={str(f.relative_to(ROOT)):sha(f) for f in inputs}
    if p.returncode or before!=after:
        raise RuntimeError('collector failed or inputs changed: '+p.stderr)
    (RD/'collector_inputs.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
    outputs=[RD/'verification_summary.json',RD/'final_build_records.json',RD/'negative_final.json',
        RD/'collector_inputs.json',RD/'collector_stdout.json',RD/'library_tests/wire_summary.json',
        RD/'library_tests/store_summary.json',RD/'kernel_table_probe.json']
    manifest={'schema_version':1,'claim_id':'AVOC-v0.27-cost-closure-and-checked-persistent-library',
      'repository':{'commit':None,'dirty':True,'baseline_archive_sha256':sha(a.baseline)},'command':cmd,
      'environment':{'software':['Python '+platform.python_version(),'Lean 4.34.0-rc2 commit 6a10ac8c22beadecabdbb0919c2b50214762f91d',
          'mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 (pinned cache)'],
          'hardware':platform.platform()+'; '+str(os.cpu_count())+' logical CPUs exposed; no hardware speed guarantee'},
      'mathematics':{'assertion_tested':'Current source/axiom/build/negative provenance, finite closure-check acceptance, independent all-behavior cost oracle and saved-library validation behavior.',
          'coefficient_domain':'Exact Nat tree-node costs and Bool truth tables, no floating mathematical comparisons.',
          'conventions':'Three inputs, lexicographic false-first order, signature bit i equals output at input i; eager additive unit tree-node cost; all finite heights in the theorem.',
          'inputs':[{'path':str(f.relative_to(ROOT)),'sha256':before[str(f.relative_to(ROOT))]} for f in inputs],
          'bounds':{'local_targets':150,'theorem_reports':1447,'negative_files':71,'semantic_classes':256,
            'constructor_inequalities':196869,'wire_cases':25,'funded_query_comparisons':644,'store_cases':13,
            'parser_fuel':64,'max_nodes_per_expression':4096,'optional_static_kernel_timeout_seconds':30},
          'non_claims':['No successful standalone kernel reduction of the concrete complete table: optional attempt timed out.',
             'No full mathlib-source rebuild, independent kernel or Python/filesystem refinement.',
             'No physical speedup, net-cost-optimal metareasoning, production LLM evidence or general programming-language optimality.']},
      'randomness':{'used':True,'generator':'Python random.Random used only for 128 seeded query ASTs in regression; certificate and cost oracle deterministic','seed':20260913},
      'run':{'started_at':started,'runtime_seconds':elapsed,'exit_status':p.returncode,
             'scope':'This runtime times the fresh evidence collector only. Original proof/test timings are in their individual records.'},
      'outputs':[{'path':str(f.relative_to(ROOT)),'sha256':sha(f)} for f in outputs],
      'checks':['Fresh collector verifies current input/output/log/import hashes for every local target and all negative files.',
          'Exact expected theorem name set and allowed foundational axioms checked.',
          'Independent node-size oracle agrees with every funded query and concrete certificate.',
          'Before/after collection source hashes agree. Legacy metadata record supplemented by per-target logs.'],
      'result':'PASS for stated local source and executed-checker assertions; optional concrete-table kernel reduction remains timed out.',
      'residual_risks':['Generic theorem/checker soundness plus executed concrete acceptance trusts Lean compiler/runtime.',
          'Protected host, source pins, Python/JSON/IO remain trusted; controlled exception is not power-loss testing.',
          'The included validator is the inherited v1-only local adaptation of mathbox, not full v2.']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'collector_passed':True,'source_inputs_unchanged':True,'collector_seconds':elapsed,'manifest':'results/v0.27.0/computation_manifest.json'},indent=2))
if __name__=='__main__':main()
