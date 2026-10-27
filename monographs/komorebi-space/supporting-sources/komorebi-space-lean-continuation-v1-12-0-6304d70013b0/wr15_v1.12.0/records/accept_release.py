"""Generate immutable acceptance records after the coordinator signs final reviews."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'integration/runs/clean_wr15_01'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())
def write(path, value): path.write_text(json.dumps(value, indent=2) + '\n')

rec, post = read(RUN/'receipt.json'), read(RUN/'postflight.json')
signoff = read(ROOT/'records/FINAL_AUDIT_SIGNOFF.json')
assert read(ROOT/'PROGRESS_LEDGER.json')['status'] != 'ACCEPTED', 'Do not rewrite accepted evidence'
assert rec['status'] == post['status'] == signoff['status'] == 'PASS'
assert signoff['formal_receipt_sha256'] == post['run_receipt_sha256'] == sha(RUN/'receipt.json')
assert signoff['postflight_sha256'] == sha(RUN/'postflight.json')
assert all(value is True for value in post['gates'].values())
assert all(c['passed'] and not c['timeout'] for c in rec['commands'])
for name, digest in signoff['review_sha256'].items(): assert sha(ROOT/name) == digest, name
overlay = read(ROOT/'records/FROZEN_OVERLAY.json')['source_sha256']
assert {str(p.relative_to(ROOT/'formal')):sha(p) for p in (ROOT/'formal').rglob('*') if p.is_file()} == overlay
sources = {name:digest for name,digest in overlay.items() if name.startswith('KomorebiSpace/')}
assert all(sha(RUN/'source'/name) == digest for name,digest in sources.items())
public = {}
for name in sources:
    text = (RUN/'source'/name).read_text()
    namespace = re.findall(r'^namespace\s+(\S+)', text, re.M)
    assert namespace == ['KomorebiSpace.CoordinateCovector']
    for kind, short in re.findall(r'^\s*(?:noncomputable\s+)?(theorem|lemma|def)\s+(\S+)', text, re.M):
        qualified = namespace[0]+'.'+short
        assert qualified not in public
        public[qualified] = {'kind':kind, 'module':name[:-5].replace('/','.')}
theorems = sum(v['kind'] in ('theorem','lemma') for v in public.values())
assert (theorems,len(public)) == (43,51)
rows = read(RUN/'new_declarations.json')
row_by_name = {r['name']:r for r in rows}
assert len(row_by_name) == len(rows) == rec['new_axiom_declarations']
for name, value in public.items():
    assert name in row_by_name and row_by_name[name]['module'] == value['module']
assert all(r['type_mode']=='full' and r['type'] and '⋯' not in r['type'] for r in rows)
assert rec['parent_declarations'] == 4982 and rec['inherited_declarations_preserved']
assert rec['axiom_declarations'] == 4982 + len(rows)
assert rec['compile_targets']==156 and rec['production_modules']==153
assert rec['explicit_theorem_lemma_count']==1693
assert len(rec['controls'])==44 and len(rec['commands'])==238
counts=dict(Counter(c['kind'] for c in rec['controls']))
assert counts=={'positive':14,'negative':28,'policy':2}
evidence_names=[
 'reviews/WR15_MATH_AUDIT.md','reviews/VERIFIER_REVIEW.md','reviews/reviewed_helpers.json',
 'reviews/PACKAGING_SCRIPT_REVIEW.md','formal/tests/control_manifest.json',
 'records/FINAL_AUDIT_SIGNOFF.json','integration/postflight/validate.py']
evidence_names += ['integration/scripts/'+name for name in read(ROOT/'reviews/reviewed_helpers.json')['files']]
evidence_names += ['integration/runs/clean_wr15_01/'+name for name in
 ['receipt.json','postflight.json','axioms.json','new_declarations.json','declarations_sorted.json','runtime_snapshot.json']]
evidence={name:sha(ROOT/name) for name in evidence_names}
complete=[f'WR{i:02}' for i in [1,2,3,4,5,6,7,8,9,13,14,15,16]]
remaining=['WR10','WR11','WR12']
now=datetime.now(timezone.utc).isoformat()
checkpoint='KS-v1.12.0-WR15-complete'
summary={
 'status':'PASS','checkpoint':checkpoint,'accepted_utc':now,
 'formal_receipt_sha256':sha(RUN/'receipt.json'),'postflight_sha256':sha(RUN/'postflight.json'),
 'axiom_report_sha256':sha(RUN/'axioms.json'),'new_declarations_sha256':sha(RUN/'new_declarations.json'),
 'inventory_sha256':rec['inventory_sha256'],'runtime_snapshot_sha256':rec['runtime_snapshot_sha256'],
 'compile_targets':156,'production_modules':153,'entrypoints':rec['entrypoints'],
 'explicit_theorem_lemma_count':1693,'new_explicit_theorems':theorems,'new_named_public_declarations':len(public),
 'axiom_declarations':rec['axiom_declarations'],'new_axiom_declarations':len(rows),
 'inherited_declarations':4982,'axiom_union':rec['axiom_union'],'controls':counts,
 'control_files':44,'recorded_commands':238,'runtime_file_count':rec['runtime_file_count'],
 'clean_project_build':True,'dependencies_rebuilt':False,'new_source_sha256':sources,
 'acceptance_evidence_sha256':evidence,'scope':'Every principal clause of WR15, with actual protected-kernel and matrix identifications.',
 'publication':'No updated PDF. The unchanged v1.10.0 monograph remains historical.',
 'trust_boundary':rec['trust_boundary']}
write(ROOT/'VERIFICATION_SUMMARY.json',summary)
write(ROOT/'FORMAL_COVERAGE.json',{
 'status':'PASS','complete':complete,'partial':[],'written_only':remaining,
 'new_groups':{'WR15':['CoordinateBasisChange','CoordinateCovector']},
 'new_statement_audit':'reviews/WR15_MATH_AUDIT.md',
 'new_full_types':'integration/runs/clean_wr15_01/new_declarations.json',
 'new_source_sha256':sources,'formal_receipt_sha256':summary['formal_receipt_sha256'],
 'scope':'Principal numbered theorem groups. Global manuscript and executable refinement audits remain separate.'})
write(ROOT/'PROGRESS_LEDGER.json',{
 'checkpoint':checkpoint,'parent':'KS-v1.11.0-WR08-WR09-WR16-complete','status':'ACCEPTED',
 'accepted_utc':now,'formal_receipt_sha256':summary['formal_receipt_sha256'],
 'postflight_sha256':summary['postflight_sha256'],'complete_formal_groups':complete,
 'partial_formal_groups':[],'open_formal_groups':remaining,
 'acceptance_evidence_sha256':evidence,
 'review_verdicts':{'mathematics':'PASS','verifier':'PASS','packaging_script':'PASS'},
 'completed':['Full WR15 Gram residual and actual Hilbert norm identity',
              'All invertible changes of full basis, including empty dimension',
              'Fresh cumulative compilation and full new-type/all-declaration audit',
              'Independent mathematical and terminal evidence reviews'],
 'next_restart':'WR10: construct actual ℓ² diagonal operator and vectors before infinite energy/tail bounds. See NEXT_RESEARCH_BLOCK.md.',
 'separate_remaining_work':['Whole-monograph independent audit','Executable certificate refinement',
   'Application-specific model identification','Publication and guide synchronization'],
 'events':'records/EVENTS.jsonl','failures_retained':True,'publication_unchanged':True})
progress=f'''# Komorebi Space — Lean progress v1.12.0

Accepted checkpoint: **{checkpoint}**. Parent: v1.11.0. Acceptance recorded {now}.

## WR15 completed

For every full basis B of the actual protected kernel, the formalization constructs its Gram matrix G = BᵀB and derives its invertibility. It computes the coordinate equation residual q and proves that the existing restricted Hilbert normal residual is g = B G⁻¹q, with **‖g‖² = qᵀG⁻¹q** in the original norm.

For every invertible C, it constructs an actual changed full basis B′ = BC, proves inverse coordinate transport c′ = C⁻¹c, derives S′ = SC, G′ = CᵀGC and q′ = Cᵀq from the computed equation, and proves the certificate unchanged. This includes zero-dimensional kernels and arbitrary nonorthonormal bases. The identities hold for every real α; optimizer bounds still have their separate positivity requirements.

The two modules add **43 explicit theorems and eight definitions**, or 51 named public declarations. The mathematical review checks all 16 clause and representation obligations. The full final export also includes generated compiler declarations, counted separately below.

## Verification

- Fresh project compilation: **156 targets**, comprising 153 production modules and three entrypoints. Cumulative explicit theorem/lemma count: **1,693**.
- Complete environment audit: **{rec['axiom_declarations']:,} declarations**, including **{len(rows)} new exports** and all **4,982 inherited identities**. Every new type is fully exported. Only `propext`, `Classical.choice`, and `Quot.sound` occur in the accepted axiom union.
- **44 controls**: 14 positive, 28 intended compiler rejections and two policy rejections. All **238 exact commands** passed their required outcomes.
- Independent mathematical/type audit and terminal evidence reconstruction passed. The runtime/cache endpoint inventory contains **{rec['runtime_file_count']:,} files**. Dependencies were not rebuilt from source.

The new positive controls exercise a full basis vector 2 in ℝ, a negative parameter for the algebraic identity, an empty Euclidean Hilbert space, and a nonorthogonal scale-and-shear change. In the latter, the raw covector square changes from 1 to 5 while the Gram certificate stays 1. The negatives reject the raw-norm substitution, a proper-subspace certificate missing a permitted direction, and a singular Gram matrix. These finite controls support interface checking; they are not the proofs of the universal theorem.

## Recovery and mistakes retained

Workspace maintenance removed the earlier scratch files. The saved predecessor was recovered and all 5,863 archive files verified against its accepted checksum manifest. The four previously delivered links were restored at their original local paths with matching hashes. The compiler runtime was recovered from its seven saved offline parts; archive digest, compiler/adapter identities and all nine dependency pins matched. Direct compiler startup without the bundled executable-location adapter failed, and startup with the unchanged adapter passed.

An initial file-recovery request used the wrong identifier field and was rejected; resolving the exact saved-file identifiers corrected it. Lean development exposed namespace/API adaptation, sum rewrites, source-root/import layout, strict linter errors and an unsupported optional printing setting. The controls exposed an obsolete matrix import, a missing real-number import and a deprecated import. Their failed sources, commands, logs and corrected attempts are retained. No failure was relabeled as a successful control.

Before source freeze, a leftover development object was detected inside the formal overlay and moved outside it. The accepted replay used a fresh empty project-object directory. A reviewer also strengthened its independently authored terminal-check script before use after a separate read found missing record comparisons. Frozen integration helpers were unchanged. An extra archive-review worker could not start because of the thread limit, so artifact checking was assigned to an available agent independent of the packaging implementation; mathematical review remained separately owned.

## Remaining work and restart

**Thirteen of sixteen principal groups are complete; no group is partially formalized.** WR10–WR12 remain written-only. The next block is the actual infinite ℓ² diagonal model, followed by its certified tails, sharp budget asymptotic and rounded noisy rate. The frozen statements and exact restart obligations are included.

The whole-monograph audit, executable-code refinement, model identification and synchronized publication/guide updates remain separate. No revised PDF is claimed. The historical v1.10.0 monograph is preserved unchanged through the predecessor archive.

## Evidence and limitations

Receipt SHA-256: `{summary['formal_receipt_sha256']}`. Postflight SHA-256: `{summary['postflight_sha256']}`. The JSON summary binds source, reports and reviews. The append-only journal is `records/EVENTS.jsonl`.

Lean's compiler/kernel, permitted axioms, pinned external caches and supporting runtime remain trusted. Endpoint hashes cannot detect a transient change restored between observations. Inherited declaration identity means name, originating module, kind, safety and axiom set, supported by unchanged inherited source and fresh compilation; it does not claim byte-identical proof expressions. The focused WR15 audit does not certify every sentence or executable example of the monograph.
'''
(ROOT/'PROGRESS_LEDGER.md').write_text(progress)
with (ROOT/'records/EVENTS.jsonl').open('a') as f:
    f.write(json.dumps({'event':'E006','kind':'WR15_formally_accepted','utc':now,'checkpoint':checkpoint,
      'formal_receipt_sha256':summary['formal_receipt_sha256'],'postflight_sha256':summary['postflight_sha256'],
      'acceptance_evidence_sha256':evidence,'complete_formal_groups':complete,'remaining':remaining})+'\n')
print(json.dumps({k:summary[k] for k in ['status','checkpoint','compile_targets','new_explicit_theorems',
      'new_named_public_declarations','new_axiom_declarations','axiom_declarations','recorded_commands']},indent=2))
