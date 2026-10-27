from pathlib import Path
import json,hashlib,shutil,re
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');E=R/'editorial/prose_review';B=E/'authorized_local_calibrations_before'
changes=[
 {'file':'source_ix_xii/XI/publication/source/traditional/Paper_XI_Traditional_Final.tex','old':'interaction packets of depth twelve','new':'interaction packets of length twelve','category':'root-authorized uniquely forced local mathematical-term typo','rationale':'The local heading explicitly gives lengths four and six, the least common multiple is twelve, and the next sentence gives total dimension 2*12=24. Length matches the declared Frobenius coset-cycle length. No formula, hypothesis, conclusion, or argument changes.','source_journal':'xi_traditional_exact_journal.json'},
 {'file':'source_i_iv/IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/atlas-pages.tex','old':'At a zero of $D_N$, these meromorphic expressions have poles rather than finite values.','new':'Behavior at zeros of $D_N$ depends on the reciprocal order and the branch conventions stated on Plate~IV.13.','category':'root-authorized bounded exposition calibration','rationale':'Defer behavior at zeros to the adjacent Plate IV.13 reciprocal-order and branch conventions instead of retaining a blanket meromorphic-pole assertion. No theorem, hypothesis, formula, or new proof is introduced. The exact $D_N$ math fragment is preserved.','source_journal':'iv_exact_journal.json'}]
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
for c in changes:
 p=R/c['file'];a=p.read_text();assert a.count(c['old'])==1,c['file'];b=a.replace(c['old'],c['new']);bp=B/c['file'];bp.parent.mkdir(parents=True,exist_ok=True);assert not bp.exists(),bp;shutil.copy2(p,bp);p.write_text(b)
 c.update({'line_before':a[:a.index(c['old'])].count('\n')+1,'occurrences':1,'expected_occurrences':1,'authorization':'Root explicitly authorized both exact replacements after local semantic calibration; I–IV build completed before the IV edit; no rebuild requested of this editor.','backup':str(bp.relative_to(R)),'before_sha256':sha(a),'after_sha256':sha(b),'exact_only_replacement_verified':b==a.replace(c['old'],c['new'],1)})
 # Check formulas, literal blocks, labels and numeric tokens against the immediate pre-calibration backup.
 pats={'math':r'(?s)(?<!\\)\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$(?!\$).*?(?<!\\)\$', 'literal':r'(?s)\\begin\{(?:Verbatim|verbatim|lstlisting|minted)\}.*?\\end\{(?:Verbatim|verbatim|lstlisting|minted)\}|\\(?:code|leanname|path|url|nolinkurl|texttt)\{[^}]*\}', 'refs_and_figures':r'\\(?:label|ref|pageref|cref|Cref|eqref|cite|input|include|includegraphics|vfig)\*?(?:\[[^\]]*\])?\{[^}]*\}', 'numeric_digits':r'\d+'}
 c['preservation']={}
 for k,pat in pats.items():
  av=re.findall(pat,a);bv=re.findall(pat,b);assert av==bv,(c['file'],k);c['preservation'][k]={'count':len(av),'identical':True,'sha256':sha(json.dumps(av))}
 jpath=E/c['source_journal'];j=json.loads(jpath.read_text());j.append(c);jpath.write_text(json.dumps(j,indent=2)+'\n')
(E/'authorized_local_calibrations.json').write_text(json.dumps({'status':'SEALED','changes':changes,'no_builds':True},indent=2)+'\n')
# Keep the combined XI/XII exact journal reconstructible after the authorized term correction.
p=E/'xi_xii_journal.json';j=json.loads(p.read_text());j.append(changes[0]);p.write_text(json.dumps(j,indent=2)+'\n')
print('SEALED: both exact authorized replacements applied; formulas/code/references/numeric digits preserved.')
