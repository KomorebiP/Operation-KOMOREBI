#!/usr/bin/env python3
"""Resolve local book references and relocate retained proof-development records."""
from pathlib import Path
import json,re,shutil,hashlib
ROOT=Path(__file__).resolve().parent; BOOK=ROOT.parent; BACKUP=ROOT/'book_edit_baseline'
J=[]; MOVED=[]
def sh(s):return hashlib.sha256(s.encode()).hexdigest()
def write(p,s,why):
 old=p.read_text() if p.exists() else ''
 if old==s:return
 b=BACKUP/p.relative_to(ROOT)
 if p.exists() and not b.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
 J.append({'path':str(p.relative_to(ROOT)),'reason':why,'before_sha256':sh(old),'after_sha256':sh(s)})
active=json.loads((BOOK/'editorial/book_revision/v_viii_active_sources.json').read_text())
for key,names in active.items():
 n=key.split('_')[0]
 for name in names:
  p=Path(name)
  if any(x in p.parts for x in ['graphics','visual_graphics','generated']):continue
  s=p.read_text();t=s
  t=t.replace('Part III, Sections III.16--III.18 (range-bundle construction).','Chapter VII, Part III, Sections III.24--III.26 (range-bundle construction).')
  if n=='V':
   t=t.replace('Locator 5 (p. 34)','Section 20 (notation crosswalk)').replace('Locator D (p. 35)','Section 21 (formal correspondence)')
  lines=t.splitlines(keepends=True)
  for i,line in enumerate(lines):
   if '\\vpage{' not in line:continue
   line=re.sub(r'\s*\(pp?\.\s*[0-9, \-]+\)', '',line)
   line=re.sub(r'Traditional pp?\.\s*[0-9, \-]+\s*/\s*','Mathematical text: ',line)
   line=line.replace('Traditional monograph:','Mathematical text:').replace('Traditional edition:','Mathematical text:').replace('Traditional Part','Mathematical text, Part')
   if n=='VI':line=line.replace('Source release: Paper VI v0.5.0, Checked Fifth Block. Inherited evidence: September 2026.','Chapter VI formal companion: thirty-three-result correspondence and reproduction record.')
   lines[i]=line
  t=''.join(lines)
  write(p,t,'Resolve obsolete standalone page locators and name actual mathematical sections')

# The mathematical appendices give a continuous argument; historical audit narratives
# remain available in a separately identified formal-companion appendix.
titles={1:'Exact semantics, support and low-rank identities',2:'Finite compilers and continuous allocation',3:'Product chains, Krylov spaces and integer budgets',4:'Structured transforms and clipped precision',5:'Graph support, schedules and preconditioning',6:'Global small-core recompression'}
intros={1:'This appendix develops exact packet semantics, support propagation, low-rank algebra and error models. Positive-budget conditions are isolated before the allocation theorem in Appendix B.',2:'This appendix gives finite compiler constructions, continuous allocation and explicit storage and operation models. All optimization statements retain their independent admissibility conditions.',3:'This appendix develops product-chain bounds, packet Krylov identities and exact integer-budget programs. Cost, error and candidate-set assumptions remain explicit.',4:'This appendix proves the structured-transform identities and the global clipped-allocation theorem, including the maximal-budget endpoint.',5:'This appendix develops support bounds, graph schedules, block discovery and preconditioning certificates. Classical algorithmic inputs remain separate from the finite certificates proved here.',6:'This appendix derives global small-core recompression from actual compact ranges and supplied ordered thin-SVD equations. Optimality is proved against arbitrary ambient competitors.'}
history=['\\clearpage\\section{Historical proof-development records}\\label{sec:proof-history}\n', 'The following records retain the successive verification narratives that accompanied the six mathematical appendices. Their build counts, failures and remaining-work lists describe the indicated stage. They are not current open-problem lists. The final finite correspondence covers all 56 manuscript-proved items under its stated hypotheses. The four classical inputs and the three broader research targets retain their separately stated boundaries. No new compiler or numerical execution is asserted by reproducing these records.\n']
for n in range(1,7):
 p=ROOT/f'VIII/editable/traditional/parts/02_supplement_{n:02}.tex';s=p.read_text()
 original=s
 oldline=next(x for x in s.splitlines() if x.startswith('This chapter retains the substantive mathematical pages'))
 s=s.replace(oldline,intros[n]+'\\par')
 if n==1:
  anchor=r'\textbf{Fresh Lean run.}'
 elif n==6:
  anchor=r'\subsection{Source map and verification}'
 else:
  anchor=next(x for x in s.splitlines() if x.startswith('\\subsection{Verification'))
 start=s.index(anchor);tail=s[start:]
 # Keep the old evidence bytes exactly in a sidecar and use the same prose in the guide.
 rel=f'VIII/editable/lean_guide/history/appendix_{n:02}_record.tex'
 side=ROOT/rel;write(side,tail,'Move complete retained development record to formal companion; no evidence removed')
 history.append('\\subsection{'+titles[n]+'}\\label{sec:history-'+str(n)+'}\n')
 # Old subdivision headings become unnumbered within this historical subsection.
 rendered=re.sub(r'\\subsection\{([^}]*)\}',r'\\subsubsection*{\1}',tail)
 rendered=re.sub(r'\\label\{([^}]*)\}',lambda m:'\\label{history:'+m[1]+'}',rendered)
 rendered=rendered.replace(r'\FloatBarrier','')
 history.append(rendered)
 MOVED.append({'from':str(p.relative_to(ROOT)),'anchor':anchor,'original_start_line':original[:original.index(anchor)].count('\n')+1,'original_end_line':len(original.splitlines()),'raw_record':rel,'raw_record_sha256':sh(tail),'scope':'Complete verification/provenance tail; mathematical proof bodies precede the move boundary.'})
 s=s[:start]
 if n==1:
  old=r'The amended nonempty-index statement should require $\tau>0$. Nonemptiness also makes the sum of positive costs in the displayed optimizer’s denominator positive.'
  # Replace the complete one-line obsolete status paragraph, retaining its mathematical hypothesis.
  for line in s.splitlines():
   if line.startswith('The amended nonempty-index statement should require'):
    s=s.replace(line,r'The nonempty-index statement requires $\tau>0$. Nonemptiness also makes the sum of positive costs in the displayed optimizer’s denominator positive. The empty edge set is treated separately. Existence, global optimality and uniqueness for the positive-budget problem are proved in Section~\ref{supp2:subsection:004}.')
  s=s.replace('with positive sensitivities and costs, but it does not explicitly impose $\\tau>0$.','with positive sensitivities and costs. The positive-budget condition is essential.')
  s=s.replace('Boundary audit for item 8.4; evidence for this release','Positive-budget condition for item 8.4')
 else:
  label=f'supp{n}:subsection:'+('006' if n==6 else '007')
  body={2:r'The integer-budget compiler and discrete precision program follow in Appendix C. Structured transforms and clipped allocation are developed in Appendix D, graph support and schedules in Appendix E, and optimal small-core recompression in Appendix F.',3:r'The structured primitives and clipped-allocation theorem follow in Appendix D. Graph schedules and preconditioning certificates are developed in Appendix E. Appendix F gives the small-core optimality argument.',4:r'Appendix E develops the remaining graph, schedule, counting and preconditioning constructions. Appendix F proves the global small-core recompression theorem from its stated factorization data.',5:r'The global small-core recompression theorem is proved in Appendix F. The classical conjugate-gradient algorithm theorem, floating-point product model and simultaneous spectral decomposition remain separately supplied inputs.',6:r'The 56-item manuscript-proved register is covered under its stated hypotheses. General SVD existence, a numerical SVD algorithm, floating-point CG convergence and hardware speedups do not follow merely from this formal scope. The formal companion identifies the exact declaration map and recorded verification evidence.'}[n]
  s+='\\subsection{Place in the finite development}\\label{'+label+'}\n'+body+'\n\nThe historical compiler, regression and development records appear in the formal companion under ``Historical proof-development records.''\n'
 write(p,s,'Keep mathematical development in main text and move historical verification records to formal appendix')

p=ROOT/'VIII/editable/lean_guide/chapters/proof_history.tex';write(p,'\n\n'.join(history),'Add complete labeled historical evidence appendix after formal reading material')
p=ROOT/'VIII/editable/lean_guide/Paper_VIII_Lean_Guide_Final.tex';s=p.read_text();s=s.replace('\\end{document}','\\clearpage\\input{chapters/proof_history.tex}\n\\end{document}')
write(p,s,'Include relocated historical proof-development records in formal companion')
# Required macros used only in the moved historical numerical evidence.
p=ROOT/'VIII/editable/lean_guide/preamble.tex';s=p.read_text();s+='\n% Numerical notation in retained historical verification records.\n\\providecommand{\\norm}[1]{\\left\\lVert#1\\right\\rVert}\n'
write(p,s,'Provide existing norm notation for relocated historical evidence')

# Remove stale forward-looking status in mathematical discussion, replacing it with exact local routes.
p=ROOT/'VIII/editable/traditional/parts/02_supplement_02.tex';s=p.read_text()
s=s.replace('The quantized-budget compiler, which can recover unsupported points, remains a separate unformalized item in this release.',r'The quantized-budget compiler can recover unsupported points. Its construction is given in Section~\ref{supp3:subsection:005}.')
s=s.replace('The continuous allocation theorem is complete','The continuous allocation theorem')
s=s.replace(r'\textbf{Why the amendment matters.} In the previous block, Lean proved that positive sensitivities and positive tolerances on a nonempty edge set force the budget to be positive. Nonpositive budgets are infeasible. This block completes the optimization theorem with that missing condition explicit. The source PDF is unchanged, and the amendment is recorded separately.',r'\textbf{Why the hypothesis matters.} Section~\ref{supp1:subsection:005} shows that positive sensitivities and positive tolerances on a nonempty edge set force a positive budget. The theorem above states that condition explicitly and proves the unique global optimum.')
s=s.replace('Clipped allocation and the discrete precision program remain outside this completed item.',r'Clipped allocation is treated in Sections~\ref{supp4:subsection:005}--\ref{supp4:subsection:006}. The discrete precision program is treated in Section~\ref{supp3:subsection:004}.')
write(p,s,'Replace obsolete pending-status prose with exact later mathematical cross-references')
(BOOK/'editorial/book_revision/v_viii_reference_journal.json').write_text(json.dumps(J,indent=2)+'\n')
(BOOK/'editorial/book_revision/viii_moved_history.json').write_text(json.dumps(MOVED,indent=2)+'\n')
print({'changed_files':len(J),'records_moved':len(MOVED)})
