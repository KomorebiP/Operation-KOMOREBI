from pathlib import Path
import json,re,hashlib
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');E=R/'editorial/prose_review';B=E/'authorized_local_calibrations_before'
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
changes=[
 {'file':'source_ix_xii/XI/publication/source/traditional/Paper_XI_Traditional_Final.tex','old':'interaction packets of depth twelve','new':'interaction packets of length twelve','category':'root-authorized uniquely forced local mathematical-term typo','rationale':'The example heading names lengths four and six, their least common multiple is twelve, and the adjacent dimension calculation is 2*12=24. Length matches the declared Frobenius coset-cycle length. No formula, hypothesis, conclusion, or argument changes.','source_journal':'xi_traditional_exact_journal.json'},
 {'file':'source_i_iv/IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/atlas-pages.tex','old':'At a zero of $D_N$, these meromorphic expressions have poles rather than finite values.','new':'Behavior at zeros of $D_N$ depends on the reciprocal order and the branch conventions stated on Plate~IV.13.','category':'root-authorized bounded exposition calibration','rationale':'Defer behavior at zeros to the adjacent Plate IV.13 reciprocal-order and branch conventions instead of retaining a blanket meromorphic-pole assertion. No theorem, hypothesis, formula, or new proof introduced. The exact $D_N$ fragment is preserved.','source_journal':'iv_exact_journal.json'}]
for c in changes:
 a=(B/c['file']).read_text();b=(R/c['file']).read_text();assert a.count(c['old'])==1;assert b==a.replace(c['old'],c['new'],1)
 c.update({'line_before':a[:a.index(c['old'])].count('\n')+1,'occurrences':1,'expected_occurrences':1,'authorization':'Root explicitly authorized both exact replacements after local semantic calibration. I–IV build completed before the IV edit; editor did not rebuild.','backup':str((B/c['file']).relative_to(R)),'before_sha256':sha(a),'after_sha256':sha(b),'exact_only_replacement_verified':True})
 pats={'math':r'(?s)(?<!\\)\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$(?!\$).*?(?<!\\)\$', 'literal':r'(?s)\\begin\{(?:Verbatim|verbatim|lstlisting|minted)\}.*?\\end\{(?:Verbatim|verbatim|lstlisting|minted)\}|\\(?:code|leanname|path|url|nolinkurl|texttt)\{[^}]*\}', 'refs_and_figures':r'\\(?:label|ref|pageref|cref|Cref|eqref|cite|input|include|includegraphics|vfig)\*?(?:\[[^\]]*\])?\{[^}]*\}'}
 c['preservation']={}
 for k,pat in pats.items():
  av=re.findall(pat,a);bv=re.findall(pat,b);assert av==bv,(c['file'],k);c['preservation'][k]={'count':len(av),'identical':True,'sha256':sha(json.dumps(av))}
 c['numeric_digit_check']='All formula digits unchanged. XI all source digits unchanged; IV adds only the authorized prose locator 13 in Plate~IV.13.'
 if '/XI/' in c['file']:assert re.findall(r'\d+',a)==re.findall(r'\d+',b)
 else:assert re.findall(r'\d+',c['new'])==['13'] and re.findall(r'\d+',c['old'])==[]
 jp=E/c['source_journal'];j=json.loads(jp.read_text())
 if not any(x['old']==c['old'] and x['new']==c['new'] for x in j):j.append(c)
 jp.write_text(json.dumps(j,indent=2)+'\n')
 # Confirm journal replay from the original prose-pass backup reconstructs the final calibrated source.
 baseline=E/('xi_xii_before' if '/XI/' in c['file'] else 'iii_iv_before')/c['file'];s=baseline.read_text()
 for e in j:
  if e['file']==c['file']:
   assert s.count(e['old'])==e['occurrences'];s=s.replace(e['old'],e['new'])
 assert s==b,c['file'];c['full_prose_plus_calibration_journal_replay']=True
(E/'authorized_local_calibrations.json').write_text(json.dumps({'status':'SEALED','changes':changes,'no_builds':True,'classification':'One authorized local mathematical-term typo and one authorized exposition calibration; these are recorded separately from routine grammar proofreading.','symbolic_mathematical_token_changes':[]},indent=2)+'\n')
for report,entry in [('xi_traditional_subreport.json',changes[0]),('iv_subreport.json',changes[1])]:
 p=E/report;d=json.loads(p.read_text());d['authorized_local_calibrations']=[entry];d['authorized_calibration_record']='editorial/prose_review/authorized_local_calibrations.json';d['resolved_after_root_calibration']=d.pop('unresolved_issues',[]);d['unresolved_issues']=[];d['mathematical_term_typo_corrections']=[changes[0]] if report.startswith('xi_') else [];d['symbolic_mathematical_token_changes']=[]
 if report.startswith('xi_'):d['mathematical_token_changes']='No symbolic token change. Root-authorized local mathematical-term typo: depth twelve -> length twelve, separately logged.'
 else:d['mathematical_token_changes']='No symbolic token change. Root-authorized bounded exposition clarification defers zero behavior to Plate IV.13; separately logged.'
 d['validation']['authorized_calibration']='PASS: exact requested replacement only; immediate backup, math/code/reference comparison, and full exact-journal replay verified.' if isinstance(d.get('validation'),dict) else d.get('validation')
 p.write_text(json.dumps(d,indent=2)+'\n')
# Recheck the original changed-file protections with the extended journals, without reasserting old baseline asset manifests after root styling.
for script,record in [('xi_traditional_verify.py','xi_traditional_preservation_check.json'),('iv_verify_prose.py','iv_preservation_check.json')]:
 scope={};exec((E/script).read_text().split('manifest=')[0],scope);p=E/record;d=json.loads(p.read_text());d['changed_files']=scope['checks'];d['authorized_calibration_recheck']='PASS: symbolic math, literals, existing labels/refs/citations/input/figure commands, environment sequences and complete journal replay rechecked after root-authorized calibration.';d['math_token_changes']='No symbolic-token changes; authorized mathematical-term/exposition calibrations are recorded in authorized_local_calibrations.json.';p.write_text(json.dumps(d,indent=2)+'\n')
print('PASS: two exact authorized clarifications verified, both complete journals reconstruct final sources.')
