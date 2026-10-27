"""Integrate the September proof texts and checked October source contracts."""
from pathlib import Path
import re
import subprocess
HERE=Path(__file__).resolve().parent
REC=HERE.parent/'evidence/recovered'
sources={
 'carrier70':REC/'Komorebi_Hodge_Carrier70_v0.1.0/Komorebi_Hodge_Carrier70_v0.1.0/PROOF.md',
 'transfer210':REC/'Komorebi_Hodge_Carrier_Transfer_v0.2.0/Komorebi_Hodge_Carrier_Transfer_v0.2.0/PROOF.md',
 'capacity_cycles':REC/'Komorebi_Hodge_Dual_and_Cycles_v0.2.0/Komorebi_Hodge_Dual_and_Cycles_v0.2.0/PROOF.md',
}
figures={
 'carrier70':[('## 4.','19_carrier70_matrix','The exact exponent matrix. Rows are monomials and columns are target coordinates.'),('## 5.','22_carrier70_torus_matrix','The exact Laurent exponent matrix, with negative entries permitted on the torus.'),('## 6.','21_carrier70_singular_locus','The certified coordinate singular planes. Normality uses their codimension in the cone.')],
 'transfer210':[('## 5.','23_transfer210_orbits','Source and target ordered unit orbits have dimensions 24 and 48, with conductors 70 and 210.'),('## 6.','24_transfer210_incidence','An exact signed multiplicity equality. Its algebraic implication also uses the stated classical correspondence operations.'),('## 7.','27_global_dual210','The exact global dual combines a complete finite premise with a uniform large-degree inequality.')],
 'capacity_cycles':[('## 3.','26_capacity_values','Seven named capacity certificates and the degree-210 target. These eight specified characters are not a census of their degrees.'),('## 5.','30_explicit_fivephase_surface','A direct reconstruction of the known Aoki standard surface. Containment follows from exact Newton identities.'),('## 8.','31_socle_pairing35','At degree 35 the exact socle coefficient gives a nonzero period and a genuine packet component.')],
}
for name,path in sources.items():
 s=path.read_text()
 s=re.split(r'\n## References(?: and external inputs| and source provenance)?\n',s)[0]
 if name=='carrier70':
  s=s.replace('# A normal weighted-Fano carrier for a Fermat degree-70 Hodge packet','# A normal weighted carrier at degree 70')
  s=s.replace('Research note, 21 September 2026, America/Chicago.','The September 21 construction, reconciled with the October exact replay and source audit.')
  s=s.replace('The geometric proof is not Lean-verified or independently reviewed.','The geometric proof remains at manuscript level. The October review separately replayed the exact algebra and checked the stated classical leaves. This is not a formal verification of the geometry.')
 if name=='transfer210':
  s=s.replace('Not Lean-verified or independently peer reviewed.','The geometric argument is not formally verified or peer reviewed. Exact certificates were independently replayed for this edition.')
  start=s.index('The original Aoki publisher landing page was accessible')
  end=s.index('## 4. The inherited geometric seed',start)
  s=s[:start]+'''The October audit obtained the original Aoki article. Theorem 1-4 states concatenation and removal of complementary-pair auxiliary blocks. Theorem 2-1 supplies the standard blocks below under its actual nonzero-entry and coprimality conditions. The September source-access limitation is preserved in the evidence archive and resolved for these specific leaves in this edition. Neither theorem allows cancellation of an arbitrary motive. The Shioda–Ran original proofs were not independently re-audited.

'''+s[end:]
  s=s.replace('Some original publisher PDF and ancillary-log fetches failed.','Some historical publisher PDF and ancillary-log fetches failed. The October audit subsequently obtained the original Aoki statements used here.')
  for n,key in {1:'DaSilvaFermat',2:'Aoki',3:'Jumagulov2026',4:'ArapuraUniruled',5:'DeligneHodgeII',6:'BDPP'}.items():
   s=s.replace('['+str(n)+']',r'\cite{'+key+'}')
 if name=='capacity_cycles':
  start=s.index('The positive algebraicity family reconstructed here')
  end=s.index('The concrete advances within this research attempt are:',start)
  s=s[:start]+'''The positive algebraicity family reconstructed here is the **known five-phase standard family of Aoki**. The October original-source audit checked Theorem 2-1 of the 1987 paper. Its equations give the same family after the Newton identities below. The construction is a direct recomputation of those known surfaces. The determinant and period are derived explicitly using the checked complete-intersection theorem of Villaflor Loyola. No priority for the surfaces, equations, algebraicity or determinant is claimed.

'''+s[end:]
  s=s.replace('It is not Lean-verified or independently reviewed.','The exact certificates were independently replayed in October. The geometric arguments are not formally verified or peer reviewed.')
  s=s.replace('The original Aoki full text was not successfully retrieved, so the exact historical overlap of the equations is not classified.','The October original-source audit identifies these equations with the known Aoki standard construction.')
  # The source-access paragraph is a historical failure, now followed by the correction.
  old='No unread source is claimed to have been audited.'
  s=s.replace(old,old+' The October audit later obtained the original Aoki theorem statements and confirmed the standard-family equations. The historical retrieval failure is not a current missing premise for these leaves.')
 for anchor,stem,caption in figures[name]:
  full=next((line for line in s.splitlines() if line.startswith(anchor+' ')),None)
  if full:
   fig=r'\begin{figure}[tbp]\centering\includegraphics[width=0.98\linewidth]{'+stem+r'.pdf}\caption{'+caption+r'}\end{figure}'
   s=s.replace(full,fig+'\n\n'+full)
 s=re.sub(r'^(#{2,6})\s+\d+(?:\.\d+)*\.?\s+(.+)$',r'\1 \2',s,flags=re.M)
 for old,new in {
  'Sections 6–9':'the uniruledness, descent, lifting and return arguments above',
  'Sections 3–6':'the balance, cycle and period arguments above',
  'Sections 6–7':'the two dual obstruction arguments above',
  'Section 8.1':'the preceding boundary isomorphism',
  'Section 6 above':'the uniruledness argument above',
  'Section 6':('the uniruledness argument above' if name=='carrier70' else 'the preceding dual argument'),
  'Section 8 examples':'holomorphic-power examples',
  'Theorem 3.2':'the uniform matrix-obstruction theorem above',
  'Proposition 5.2':'the algebraicity-transfer proposition above',
  'Corollary 6.4':'the direct-matrix obstruction corollary above',
 }.items():s=s.replace(old,new)
 s=s.replace('### the algebraicity-transfer proposition above. Algebraicity of the degree-210 packet','### Algebraicity of the degree-210 packet')
 s=s.replace('### the direct-matrix obstruction corollary above. No direct positive-weight matrix carrier for b','### No direct positive-weight matrix carrier')
 s=s.replace('### the uniform matrix-obstruction theorem above: no positive-anticanonical invariant-column matrix','### No positive-anticanonical invariant-column matrix')
 if name=='transfer210':
  s=s.replace('### Exact witnesses',r'\Needspace{10\baselineskip}'+'\n\n### Exact witnesses')
 s=s.replace(';',',')
 md=HERE/(name+'.md')
 md.write_text(s)
 subprocess.run(['pandoc',str(md),'-f','markdown+tex_math_single_backslash+raw_tex','-t','latex','--top-level-division=chapter','-o',str(HERE/(name+'.tex'))],check=True)
 t=(HERE/(name+'.tex')).read_text()
 t=re.sub(r'\\(label|hypertarget)\{([^}]+)\}',lambda m:'\\'+m.group(1)+'{'+name+'-'+m.group(2)+'}',t)
 if name=='carrier70':
  t=re.sub(r'(\\chapter\{[^}]+\})',r'\1\\label{ch:carrier70}',t,count=1)
 t=t.replace('∎',r'\hfill\ensuremath{\square}')
 t=t.replace('. the preceding','. The preceding')
 t=t.replace('the algebraicity-transfer proposition above. Algebraicity of the degree-210 packet','Algebraicity of the degree-210 packet')
 t=t.replace('the direct-matrix obstruction corollary above. No direct positive-weight matrix carrier for b','No direct positive-weight matrix carrier for the target')
 t=t.replace('stated in Section 3','resolved in the source-access discussion above')
 if name=='transfer210':
  t=t.replace('\\begin{longtable}','{\\small\\begin{longtable}').replace('\\end{longtable}','\\end{longtable}}')
 def numbered(match):
  content=match.group(1)
  tag=re.search(r'\\tag\{([^}]+)\}',content)
  if not tag:return match.group(0)
  key=name+'-'+tag.group(1)
  content=content.replace(tag.group(0),'').strip()
  return '\\begin{equation}\\label{eq:'+key+'}\n'+content+'\\end{equation}'
 t=re.sub(r'\\\[(.*?)\\\]',numbered,t,flags=re.S)
 for tag in ('1.1','1.2','2.1','2.2','2.3','2.4','2.5','3.1','3.2','4.1','4.2','5.1','5.2','5.3','5.4','5.5','6.1','6.2','6.3','6.4','6.5','7.1'):
  if '\\label{eq:'+name+'-'+tag+'}' in t:
   t=t.replace('('+tag+')','\\eqref{eq:'+name+'-'+tag+'}')
 (HERE/(name+'.tex')).write_text(t)

original=(REC/'Projector_Resolved_Hodge_Calculus_Dyadic_Completion_Source/Projector_Resolved_Hodge_Calculus_Dyadic_Completion_Source/Projector_Resolved_Hodge_Calculus_Complete.tex').read_text()
bib=original[original.index('\\begin{thebibliography}'):original.index('\\end{thebibliography}')+len('\\end{thebibliography}')]
addition=(HERE.parent/'evidence/literature/bibliography_additions.tex').read_text()
for block in re.split(r'(?=\\bibitem\{)',addition)[1:]:
 key=re.match(r'\\bibitem\{([^}]+)\}',block).group(1)
 if '\\bibitem{'+key+'}' not in bib:
  bib=bib.replace('\\end{thebibliography}',block+'\n\\end{thebibliography}')
extra=r'''
\bibitem{Jumagulov2026}
R. Jumagulov.
\newblock The Hodge conjecture for Fermat fourfolds of odd degree at most 199.
\newblock arXiv:2608.18134v1, Appendix A and the standard-family discussion.
\newblock Used for context and target selection. No global census from this source is certified by this edition.
'''
bib=bib.replace('\\end{thebibliography}',extra+'\\end{thebibliography}')
(HERE/'bibliography.tex').write_text('{\\small\n'+bib.replace(';',',')+'\n}')
print('Full September proofs and checked bibliography assembled')
