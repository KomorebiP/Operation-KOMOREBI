#!/usr/bin/env python3
"""Prepare companion verification prose from the accepted release receipt."""
from pathlib import Path
import argparse, hashlib, json

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--receipt', type=Path, default=ROOT/'formal/evidence/RELEASE_VERIFICATION.json')
p.add_argument('--output', type=Path, default=ROOT/'verification/COMPANION_EVIDENCE.json')
a = p.parse_args()
x = json.loads(a.receipt.read_text())
assert x['status'] == 'PASS', 'Release receipt is not accepted'
c, lean, py = x['coverage'], x['lean'], x['python']
assert c == {**c, 'record_count':108, 'proof_records':69, 'covered':69, 'partial':0, 'not_mapped':0}
assert py['status'] == 'PASS'
def number(v): return len(v) if isinstance(v, list) else v
nc = number(lean['negative_controls'])
axioms = ', '.join(r'\code{'+s+'}' for s in lean['axioms'])
logical_checked = lean.get('logical_checked_count', lean['logical_replay_count'])
duplicate_rechecks = lean.get('upstream_duplicate_body_rechecks', 0)
assert logical_checked == lean['logical_replay_count'] + duplicate_rechecks
assert lean['source_owned_count'] == logical_checked + lean['runtime_helpers']
logical_detail = f"Of these, {lean['logical_replay_count']} are checked by logical replay"
duplicate_phrase = ('one declaration sharing an upstream name receives a fresh-name kernel body check' if duplicate_rechecks == 1 else f'{duplicate_rechecks} declarations sharing upstream names receive fresh-name kernel body checks')
logical_detail += (' and '+duplicate_phrase+' after exact type/value comparison. ' if duplicate_rechecks else '. ')
lead = (f"The accepted release receipt reports complete correspondences for all {c['proof_records']} proof-level records in the current {c['record_count']}-record inventory. "
        "Each conclusion retains the hypotheses and presentation conventions recorded in the correspondence map. Definitions, boundaries, and classical inputs are classified separately.")
sem = x['semantics']
if 'new_review_proof_records' in sem:
    lead += (f" The release includes targeted new semantic reviews for {sem['new_review_proof_records']} proof-level records and retains accepted predecessor correspondences for {sem['retained_proof_records']} others. "
             "The total of 69 accepted correspondences is not a claim that every record received a new independent audit during this release.")
formal = (f"The release audit checks {lean['module_count']} formal source modules plus the retained boundary suite. Including that suite, it inventories {lean['source_owned_count']} source-owned entries and checks {logical_checked} logical declarations. "
          + logical_detail +
          f"It inventories {lean['runtime_helpers']} runtime helpers separately and records {nc} rejected negative controls. "
          "The allowed transitive axiom set is "+axioms+". "
          r"The receipt is \code{formal/evidence/RELEASE_VERIFICATION.json}; its detailed compiler and logical-replay evidence is under \code{formal/evidence/whole_closure/}.")
python = (f"Fresh computational checks pass for {py['exact_visual_checks']} exact finite or symbolic visual assertions, {py['tests']} companion tests, and {py['regenerated_figure_pairs']} regenerated PDF/PNG figure pairs. "
          "These bounded computations have their own scope and do not replace the formal declarations.")
limits = ("The pinned upstream dependency cache is reused. Logical replay uses Lean's official kernel; it is not an independently implemented checker. "
          "The current source-to-manuscript correspondence is a separate reviewed mathematical artifact.")
guide = '\n\\subsection{Accepted release verification}\n\n'+'\n\n'.join([lead,formal,python,limits])+'\n'
machine = '\n\n'.join([formal.replace(r'\code{',r'\nolinkurl{'),python,limits])
out = {'schema':'komorebi.companion-evidence/1','receipt':str(a.receipt.relative_to(ROOT)),
       'receipt_sha256':hashlib.sha256(a.receipt.read_bytes()).hexdigest(),
       'guide_verification_tex':guide,'machine_verification_tex':machine}
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(out,indent=2)+'\n')
print(a.output)
