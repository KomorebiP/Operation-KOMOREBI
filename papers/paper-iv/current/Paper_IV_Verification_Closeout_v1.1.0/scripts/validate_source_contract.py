#!/usr/bin/env python3
"""Use the preserved verifier's actual typed API to check the manuscript map.

This is a source/contract audit. It does not label historical compiler output
as fresh kernel execution. Real compiler receipts live in lean_primary/.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, inspect, json, sys
ROOT=Path(__file__).resolve().parents[1]
FORMAL=ROOT/'publication_baseline/source/complete/original_snapshot/lean_release/PRSC_IV'
def load_gate():
 path=FORMAL/'verification/check_release.py';spec=importlib.util.spec_from_file_location('paper_iv_preserved_release_gate',path)
 if spec is None or spec.loader is None:raise RuntimeError('Cannot load preserved verifier')
 module=importlib.util.module_from_spec(spec)
 # dataclasses consult sys.modules while processing postponed annotations.
 sys.modules[spec.name]=module;spec.loader.exec_module(module);return module

def collect():
 gate=load_gate();reporter=gate.Reporter('release');files=gate.release_files(FORMAL)
 gate.check_manifest(FORMAL,files,reporter)
 names=gate.check_evidence_claims(FORMAL,files,reporter)
 records=gate.check_generated_register(FORMAL,files,reporter)
 targets,nd,nt=gate.load_lean_contract(FORMAL,reporter)
 rows=gate.parse_theorem_map(FORMAL/gate.AUTHORITATIVE_THEOREM_MAP)
 mapped,numbers=gate.crosscheck_map_contract(rows,records,targets)
 full={key:r for key,r in records.items() if r.kind in gate.RESULT_KINDS and r.evidence=='P + L(full)'}
 return gate,rows,records,targets,{'status':'PASS','scope':'Source associations and preserved-contract consistency, not fresh proof checking.','register_records':len(records),'full_scoped_results':len(full),'map_rows':len(rows),'mapped_targets':len(mapped),'mapped_theorems':sum(t.kind=='theorem' for t in targets),'mapped_definitions':sum(t.kind=='definition' for t in targets),'record_associations':len(set(numbers)),'inherited_namespace_counts_not_recomputed_here':{'declarations':nd,'theorems':nt},'verifier_sha256':hashlib.sha256((FORMAL/'verification/check_release.py').read_bytes()).hexdigest(),'api_signatures':{n:str(inspect.signature(getattr(gate,n))) for n in ['load_lean_contract','crosscheck_map_contract','check_evidence_claims','check_generated_register']}}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 *_,report=collect();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0
if __name__=='__main__':sys.exit(main())
