"""Author: Komorebi P. Synchronize the fifth release after compiler and PDF validation."""
from pathlib import Path
import json,hashlib,difflib,shutil,re
R=Path(__file__).resolve().parents[1]
O=R/'provenance/fourth_checked_block'
report=json.loads((R/'verification/verification_status.json').read_text())
pdf=json.loads((R/'verification/pdf_validation.json').read_text())
if report['status']!='LEAN_FIFTH_BLOCK_CHECKS_PASS' or pdf['visual_review']!='PASS':
    raise RuntimeError('Missing final validation')
N=report['gates']['source']['theorems'];M=report['gates']['source']['proof_modules']
D=report['gates']['lean']['namespace_declarations'];pages=pdf['pages']
for src,dst in [('Paper_VI_Reviewed.pdf','Projector_Resolved_Seed_Calculus_VI.pdf'),('Paper_VI_Reviewed.tex','Projector_Resolved_Seed_Calculus_VI.tex'),('lean_status.tex','lean_status.tex')]:
    shutil.copy2(R/'manuscript'/src,R/'companion'/dst)
p=R/'companion/README.md';s=p.read_text();i=s.index('## Current checked edition');j=s.index('## PowerShell',i)
s=s[:i]+f'''## Current checked edition — v0.5.0

The reviewed manuscript is {pages} pages. Paper VI has **33 complete scoped manuscript results, zero partial and zero pending**, with **{N} checked supporting Lean theorem declarations in {M} modules** and {D} namespace declarations audited. The full pinned build, axiom audit, 54 companion tests and six verifier controls pass.

This block closes the final two results: general nonnormal memory/Laplace self-energy (13.2) and canonical holomorphic naturality (15.1). Both manuscript proofs are expanded. See `../THEOREM_LEDGER.md` and `../REVIEW.md`. The three separately stated conjectures remain open and are excluded from the ledger count.

'''+s[j:]
i=s.index('## Verification and numerical provenance');s=s[:i]+'''## Verification and numerical provenance

The canonical reviewed PDF and TeX are in `../manuscript`. The 54 companion tests include the original 37 and 17 review boundary/validation cases; all pass again. Full Lean status and exact scoped coverage are recorded in `../verification/verification_status.json` and `../THEOREM_LEDGER.md`. Prose-to-Lean correspondence and ordinary specializations are manually reviewed.

The numerical implementation and all 19 figure pairs are unchanged. The retained 79-field numerical comparison was performed for the first checked block; this block reruns the 54 tests and the full Lean build and axiom audit.
''';p.write_text(s)
(R/'companion/RELEASE_AUDIT.md').write_text(f'''# Current release audit — fifth checked block

Author: Komorebi P.

- Reviewed PDF: {pages} pages; all 33 theorem-like results retained and three unchanged open conjectures.
- Lean: {N} explicit theorem declarations in {M} modules; {D} namespace declarations audited.
- Manuscript ledger: 33 complete scoped results, zero partial, zero pending.
- Tests: 54 companion tests and six verifier controls pass again.
- Dependencies: all nine locked revisions verified, without tracked source changes.
- Final LaTeX: no warnings, undefined references, overfull or underfull boxes.
- Visual inspection: all pages in contact sheets and changed pages at reading size.
- Numerical figures unchanged: 19 pairs; earlier 79-field comparison retained, not rerun.

Authoritative reports are `../verification/verification_status.json` and `../verification/pdf_validation.json`. Completion of the scoped ledger is distinct from formalization of every prose sentence or open conjecture. The supplied historical audit is preserved in `../provenance/original_release`.
''')
p=R/'companion/Verification_Notes.md';s=p.read_text();s=re.sub(r'current \d+-page checked edition \(54 tests; [^)]*Lean results\)',f'current {pages}-page checked edition (54 tests; 33 complete scoped Lean results)',s);p.write_text(s)
p=R/'companion/Source_and_Claim_Map.md';p.write_text(p.read_text().replace('31 complete and two partial results','33 complete scoped results, zero partial and zero pending'))
patch=[]
for p in sorted([*(R/'formalization/lean').glob('*.lean'),*(R/'formalization/lean/KomorebiPaperVI').glob('*.lean'),R/'formalization/lean/lakefile.toml']):
    rel=p.relative_to(R);old=O/rel
    a=old.read_text().splitlines(keepends=True) if old.exists() else []
    patch.extend(difflib.unified_diff(a,p.read_text().splitlines(keepends=True),fromfile='v0.4.0/'+str(rel) if old.exists() else '/dev/null',tofile='v0.5.0/'+str(rel)))
(R/'verification/lean_changes.patch').write_text(''.join(patch))
patch=[]
for name in ['Paper_VI_Reviewed.tex','lean_status.tex']:
    a=O/'manuscript'/name;b=R/'manuscript'/name
    patch.extend(difflib.unified_diff(a.read_text().splitlines(keepends=True),b.read_text().splitlines(keepends=True),fromfile='v0.4.0/manuscript/'+name,tofile='v0.5.0/manuscript/'+name))
(R/'verification/manuscript_changes.patch').write_text(''.join(patch))
C=R/'companion';files=[]
for p in C.rglob('*'):
    if not p.is_file() or p.name=='SHA256SUMS.txt' or any(x in ('__pycache__','.pytest_cache') for x in p.parts):continue
    files.append(p)
(C/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(C).as_posix()+'\n' for p in sorted(files)))
print(json.dumps({'documents_synchronized':True,'pages':pages,'theorems':N,'modules':M,'namespace_declarations':D}))
