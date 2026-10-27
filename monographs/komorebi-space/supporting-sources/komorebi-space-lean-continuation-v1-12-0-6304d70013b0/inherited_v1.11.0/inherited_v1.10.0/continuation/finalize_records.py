#!/usr/bin/env python3
"""Bind continuation status only to terminal accepted evidence and actual sources."""
from pathlib import Path
import hashlib
import json
import re

CONT = Path(__file__).resolve().parent
ROOT_DIR = CONT.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def main():
    base_dir=CONT/'integration/runs/cumulative_base_01'
    base=json.loads((base_dir/'receipt.json').read_text())
    seal=json.loads((base_dir/'postflight.json').read_text())
    assert base['status']=='PASS' and seal['status']=='PASS'
    assert seal['base_receipt_sha256']==sha(base_dir/'receipt.json')
    candidates=[]
    for p in (CONT/'integration/runs').glob('*/receipt.json'):
        r=json.loads(p.read_text())
        if r.get('schema')=='komorebi-space-incremental-overlay-v1' and r.get('status')=='PASS':
            candidates.append((p.parent,r))
    assert len(candidates)==1, 'Require one unambiguous accepted final integration'
    final_dir,final=candidates[0]
    assert final['base_receipt_sha256']==sha(base_dir/'receipt.json')
    assert final['base_postflight_sha256']==sha(base_dir/'postflight.json')
    assert final['axiom_report_sha256']==sha(final_dir/'axioms.json')
    audit=json.loads((final_dir/'axioms.json').read_text())
    assert not audit['unexpected']
    byname={r['name']:r for r in audit['declarations']}
    fields={
      'WR01': {'budget_preserving_existence':'BoundedApproximateRealization.exists_solution_of_bounded_residual_tendsto_zero','equivalence':'BoundedApproximateRealization.mem_range_iff_bounded_approximation','escape':'BoundedApproximateRealization.norm_tendsto_atTop_of_not_mem_range'},
      'WR02': {'construction':'NestedMinimumCorrections.affineCorrections_spec','monotone':'NestedMinimumCorrections.nested_affine_norm_monotone','finite_energy':'NestedMinimumCorrections.nested_affine_energy','equivalence':'NestedMinimumCorrections.nested_affine_intersection_iff_bounded','strong_limit_unique_minimum_and_limit_energy':'NestedMinimumCorrections.nested_affine_strong_realization','escape':'NestedMinimumCorrections.nested_affine_escape'},
      'protected_bridge': {'same_budget_exact_protected_candidate':'ProtectedBoundedRealization.exists_exact_repair_of_bounded_approximation'}
    }
    for group,clauses in fields.items():
        for clause,name in list(clauses.items()):
            full='KomorebiSpace.'+name
            assert full in byname and byname[full]['type'], full
            clauses[clause]={'declaration':full,'type':byname[full]['type'],'axioms':byname[full]['axioms']}
    write_json(CONT/'FORMAL_COVERAGE.json',{'status':'PASS','source_type_comparison':'Editorial independent audit, not automatic translation of prose','claims':fields,'axiom_report_sha256':sha(final_dir/'axioms.json')})
    checkpoint=json.loads((CONT/'BASE_CHECKPOINT.json').read_text())
    predecessor=ROOT_DIR/'work/Komorebi_Space_Monograph_v1.7.0'
    for rel,h in checkpoint['source_hashes'].items():
        assert sha(predecessor/rel)==h,rel
    source_hashes={str(p.relative_to(CONT)):sha(p) for p in sorted((CONT/'formal/KomorebiSpace').glob('*.lean'))}
    for rel,h in source_hashes.items():
        assert sha(final_dir/'source'/Path(rel).relative_to('formal'))==h
    counts=final['control_counts']
    summary={'status':'PASS','version':'1.8.0','release_kind':'formal continuation of unchanged v1.7.0 reader set',
      'predecessor_sha256':checkpoint['predecessor_sha256'],'inherited_formal_files_unchanged':len(checkpoint['source_hashes']),
      'base_label':base_dir.name,'base_compile_targets':base['compile_targets'],'base_production_modules':base['production_modules'],
      'base_clean_build':base['clean_project_build'],'base_receipt_sha256':sha(base_dir/'receipt.json'),'base_postflight_sha256':sha(base_dir/'postflight.json'),
      'overlay_label':final_dir.name,'overlay_clean_build':final['clean_project_build'],'overlay_receipt_sha256':sha(final_dir/'receipt.json'),
      'new_production_modules':len(source_hashes),'new_explicit_theorems_and_lemmas':sum(len(re.findall(r'^theorem\s+',p.read_text(),re.M)) for p in (CONT/'formal/KomorebiSpace').glob('*.lean')),
      'new_source_sha256':source_hashes,'final_production_modules':final['production_modules'],'final_source_targets':len(final['complete_module_order']),
      'audited_declarations':final['axiom_declarations'],'new_audited_declarations':final['new_axiom_declarations'],'axiom_union':final['axiom_union'],
      'positive_files':sum(v.get('positive',0) for v in counts.values()),'compiler_negative_files':sum(v.get('negative',0) for v in counts.values()),'policy_negative_files':sum(v.get('policy',0) for v in counts.values()),
      'wr_complete':['WR01','WR02','WR06','WR07','WR13','WR14'],'wr_partial':['WR09','WR16'],'wr_written_only':['WR03','WR04','WR05','WR08','WR10','WR11','WR12','WR15'],
      'next_block':['WR03','WR04','WR05'],'new_full_cumulative_clean_final_replay_claimed':False,'inherited_reader_pdfs_changed':False,
      'trust_boundary':['Official Lean kernel/compiler and three standard axioms.','Pinned imported dependency caches reused, not rebuilt.','New sources compiled over a fresh clean and sealed cumulative baseline.','No universal Python refinement or automatic prose proof checking.'],
      'accepted_finished_utc':final['finished_utc']}
    write_json(CONT/'VERIFICATION_SUMMARY.json',summary)
    ledger={'checkpoint':'KS-v1.8.0-WR01-WR02-complete','parent':checkpoint['checkpoint'],'parent_archive_sha256':checkpoint['predecessor_sha256'],
      'completed':['WR01 full principal group','WR02 full principal group','protected-kernel existence bridge','clean merged core and regularization replay','incremental final-scope compilation and axiom audit','independent mathematical/type review','independent verifier review and base terminal postflight'],
      'verification_summary_sha256':sha(CONT/'VERIFICATION_SUMMARY.json'),'open_formal_groups':summary['wr_written_only'],'partial_formal_groups':summary['wr_partial'],
      'next_restart':'Formalize WR03 budget attainment/profile, then WR04 dual certificate and WR05 robustness. Use the new convex projection bridge and full accepted source snapshot. Do not modify inherited evidence.',
      'publication_state':'Inherited v1.7.0 reader PDFs remain unchanged; continuation guide provides revised evidence status. Synchronize monograph/visual/Lean guides after remaining formal groups.',
      'failure_record':'Preserved development compiler and fixture failures, runtime self-path startup failure, and verifier integrity gaps corrected before final acceptance.'}
    write_json(CONT/'PROGRESS_LEDGER.json',ledger)
    text=f'''# Komorebi Space progress ledger · v1.8.0

Checkpoint: `KS-v1.8.0-WR01-WR02-complete`. Parent: v1.7.0 archive SHA256 `{checkpoint['predecessor_sha256']}`.

## Completed in this block

WR01 and WR02 now have complete formal counterparts under the published real Hilbert-space hypotheses. A third module applies bounded approximation to the actual protected correction kernel and preserves the same budget. The new sources contain {summary['new_explicit_theorems_and_lemmas']} explicit named theorems and lemmas, including auxiliaries.

The core and regularization extension were compiled together from an empty project object directory: {summary['base_compile_targets']} targets. A separate terminal postflight checked every copied input, every expected command, all logs, and final object hashes. The additions were then compiled over those validated objects, with a fresh full-scope axiom audit of {summary['audited_declarations']:,} declarations. Only `propext`, `Classical.choice`, and `Quot.sound` occur. This final stage is explicitly incremental. It is not a second clean rebuild of every final source.

All {summary['positive_files']} positive files, {summary['compiler_negative_files']} compiler rejection files, and {summary['policy_negative_files']} policy rejection files passed their intended outcome checks. The 169 inherited formal-tree files remain unchanged. Exact finite Python suites were not rerun in this block.

## Current coverage

| Status | Groups |
|---|---|
| Complete | WR01, WR02, WR06, WR07, WR13, WR14 |
| Partial, limiting conclusion open | WR09, WR16 |
| Written-only | WR03–WR05, WR08, WR10–WR12, WR15 |

The alternative projection proof in `proofs/STRONG_PROJECTION_ROUTE.md` covers written WR01–WR03 and passed independent mathematical review. It does not promote WR03 to formal coverage. The printed weak-subsequence lemma is also not newly formalized.

## Publication and limits

The v1.7.0 monograph (161 pages), visual guide (43 pages), and evidence guide (36 pages) are retained unchanged inside `inherited_v1.7.0`. Use the continuation guide and this ledger for the updated formal status. Full book-wide proof-to-source auditing and a synchronized reader release remain open.

The official compiler/kernel and pinned compiled dependency caches remain trusted. No independent kernel, full mathlib rebuild, native Windows replay, or universal Python-refinement proof was performed.

## Failures and corrections

Direct compiler startup could not locate its executable; the existing portable-runtime path adapter corrected that environmental issue. Early Lean attempts failed on dotted syntax, missing typeclass/elaboration information, norm coercion, and strict linting. A first bridge build omitted an inherited dependency from its local build order. These were repaired without adding axioms or weakening the theorem statements. Failed logs and later terminal results are retained.

Independent verifier review found missing terminal ancillary-input/object checks and incomplete command-inventory acceptance. A separate postflight and the hardened incremental verifier closed these checks. The preserved review distinguishes those assurance gaps from mathematical failures. No changed input or invalid compiled theorem was found.

The first guide build failed on an unavailable LuaLaTeX font loader. Switching to XeLaTeX resolved that environment problem. The second build failed on an equation tag placed inside an aligned block. Moving the tag to the outer display fixed the typesetting without changing the mathematics. Font substitutions were then resolved before final visual review. The failed and superseded build logs are retained.

## Exact restart

1. Read `VERIFICATION_SUMMARY.json`, `FORMAL_COVERAGE.json`, and the independent reviews.
2. Use `formal/` at the package root for the complete accepted source snapshot. The standalone additions are in `continuation/formal/`.
3. Continue with WR03's complete budget-profile theorem, using `exists_mem_iInter_of_closed_convex_bounded` for attainment if useful. Then formalize WR04 and WR05.
4. Keep the real correction-space norm, same protected kernel, M=0 cases, and every WR03 shape/limit clause. A proof of attainment alone is only partial WR03 coverage.
5. Use new immutable replay labels. Follow `README.md` for clean-baseline and incremental reproduction. Preserve all accepted and failed evidence.

Accepted base label: `{base_dir.name}`. Accepted final label: `{final_dir.name}`.
'''
    (CONT/'PROGRESS_LEDGER.md').write_text(text)
    readme=f'''# Komorebi Space · Formal continuation v1.8.0

WR01–WR02 and the protected-kernel bridge are now formalized and verified. The complete inherited reader set is included, along with the updated continuation guide, sources, raw evidence, and progress ledger.

- `formal/`: complete final source snapshot, with one combined entrypoint `KomorebiSpaceCombined.lean`.
- `inherited_v1.7.0/`: unchanged 161-page monograph, 43-page visual guide, 36-page Lean guide, historical source and evidence.
- `continuation/publication/Continuation_Guide.pdf`: new reader guide and detailed alternate projection proofs.
- `continuation/FORMAL_COVERAGE.json`: exact public theorem types for each newly covered clause.
- `continuation/integration/runs/`: accepted compiler, axiom, control, and terminal integrity evidence. Compiled object caches are omitted from the delivery.
- `PROGRESS_LEDGER.md`: current completion boundary and exact next block.

The remaining WR formalization is eight written-only groups and the two partial limit conclusions. The full final library contains {summary['final_production_modules']} production modules and {summary['audited_declarations']:,} audited declarations. Generated and auxiliary declarations are included in that count.

## Reproduce with the pinned portable runtime

The runtime is supplied separately. It contains Lean 4.34.0-rc2 and the nine pinned dependencies. On the tested Linux runtime, its documented self-path compatibility adapter is required. Set `KS_RUNTIME` to the runtime folder, then from this package root run:

```sh
python3 continuation/integration/scripts/verify.py --runtime "$KS_RUNTIME" --path-adapter "$KS_RUNTIME/compat/app_path.so" --label local_base
python3 continuation/integration/postflight/validate.py --base continuation/integration/runs/local_base
python3 continuation/integration/overlay/verify_overlay.py --base continuation/integration/runs/local_base --base-postflight continuation/integration/runs/local_base/postflight.json --overlay continuation/formal --runtime "$KS_RUNTIME" --path-adapter "$KS_RUNTIME/compat/app_path.so" --label local_wr
```

Each replay refuses to overwrite an existing label. Run the commands in order and stop if any exits nonzero. The second check is terminal evidence validation, not another Lean compilation. The final replay reuses only the newly validated base objects and conducts a fresh full-scope audit.

No independent kernel, full-source dependency rebuild, native Windows validation, or universal proof of the Python implementation is claimed. The older publication PDFs retain their historical evidence wording, so the new guide and ledger are authoritative for this continuation's formal status.
'''
    (CONT/'README.md').write_text(readme)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
