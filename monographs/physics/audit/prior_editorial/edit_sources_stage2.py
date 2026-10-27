from pathlib import Path
import re,json
P=Path('/mnt/data/physics_editorial_work/publication');S=P/'source';M=S/'monographs';log=[]
def upd(p,t,reason):
 o=p.read_text()
 if t!=o:log.append({'file':str(p.relative_to(S)),'reason':reason,'before':o,'after':t});p.write_text(t)
def para(p,needle,new):
 s=p.read_text();chunks=re.split(r'\n\s*\n',s); ix=[i for i,c in enumerate(chunks) if needle in c]
 if len(ix)!=1:raise ValueError((p,needle,ix))
 chunks[ix[0]]=new;upd(p,'\n\n'.join(chunks),'Timeless publication prose')
# Remaining orientation residue.
p=M/'chapters/orientation.tex';s=p.read_text().replace('The remaining theorem connecting the full-domain derivative or spectral exponential to the constructed unbounded Hamiltonian.','The theorem in the following chapter connecting the full-domain derivative and spectral exponential to the constructed Hamiltonian.');upd(p,s,'Remove obsolete open-target description')
para(M/'adic/orientation.tex',"The supplement's historical chapter ranges",'The technical source concordance identifies statements by exact source member, formula, and claim. Each result here carries its own hypotheses. A source title or a recorded test result is not a substitute for those hypotheses.')
# Remaining legacy/revision prose in mathematical bibliography is made bibliographic rather than a production diary.
for p in list(M.rglob('*references.tex'))+[M/'references.tex']:
 if not p.exists():continue
 s=p.read_text()
 s=re.sub(r'v0\.49\.0,?\s*(?:Checked\s*)?Block\s*49', 'formal source archive',s)
 s=s.replace('9 October 2026','2026')
 s=s.replace('Frozen formal source archive preserved in this collection.','Formal source archive with exact identity recorded in the verification appendix.')
 s=s.replace('Frozen source archive preserved in this collection.','Formal source archive with exact identity recorded in the verification appendix.')
 s=s.replace('the corrected unit-circle transport','the unit-circle transport')
 upd(p,s,'Remove release-specific descriptions from reading bibliographies')
# Generator: keep every theorem and proof, move implementation obligations out of the narrative.
g=S/'generator'/'Block50_Spectral_Generator_Bridge.tex';t=g.read_text();pre=t[:t.index('\\begin{document}')]
pre=pre.replace(r'\usepackage[paperwidth=6.8in,paperheight=9.6in,top=.76in,bottom=.69in,left=.81in,right=.81in]{geometry}',r'\usepackage[letterpaper,top=.86in,bottom=.82in,left=.87in,right=.87in]{geometry}')
pre=pre.replace(r'\usepackage{lmodern,microtype}',r'\usepackage{mathpazo,microtype}')
pre=pre.replace('Komorebi Physics, Block 50 analytical development','Komorebi Physics / spectral generator analysis').replace('ANALYTIC BLOCK 50','THE DIRAC GROUP AND ITS GENERATOR')
start=t.index('\\section{Setting and checked predecessor}')
body=t[start:]
body=body.replace('Setting and checked predecessor','The Hilbert space and the Hamiltonian')
body=body.replace('The earlier checked Block 48 and 49 modules establish self adjointness, closedness, and density, and identify', 'The preceding operator construction establishes self adjointness, closedness, and density, and identifies')
body=body.replace('Their separation is essential when moving this block into Lean.','Their separation is essential to the meaning of the estimates and to any formal implementation.')
body=body.replace('../figures/','figures/')
stop=body.index('\\section{Exact formal boundary and continuation}')
technical=body[stop:body.index('\\end{document}')]
(P/'audit'/'generator_original_technical_tail.tex').write_text(technical)
body=body[:stop]+r'''\section{Scope and connection to gauge transport}
The generator and resolvent arguments complete the analytic free-field construction on the fixed torus coefficient space. They are written proofs. Their translation into compiler-checked Lean statements remains separate from the recorded certificate for the self-adjoint Hamiltonian. The technical appendix specifies that boundary.

A centered Fourier symbol on the unchanged infinite mode set is not a changing finite spatial lattice. A lattice comparison must supply sampling and interpolation, control aliasing, and prove compatibility with the chosen geometry. A background gauge coupling must also specify its operator domain and evolution. Dynamical gauge and gravitational fields impose additional equations and constraints.

The following gauge treatment begins with those local transport structures. It does not turn the free spectral result into an interacting existence theorem. The production and backreaction obstruction in the matter model is likewise unaffected by this free-field analysis.

\end{document}
'''
intro=r'''\begin{document}
\thispagestyle{plain}
{\sffamily\small\color{cyan} KOMOREBI PHYSICS / FREE CONTINUUM DYNAMICS\par}
\vspace{14pt}
{\Huge\bfseries\color{abyss}The Dirac Group and Its Generator\par}
\vspace{12pt}
{\large\color{ash}Spectral identification, strong resolvents, and quantitative centered approximation\par}
\vspace{15pt}\noindent\textcolor{gold}{\rule{\linewidth}{.8pt}}\par\vspace{9pt}
The preceding chapter constructed a self-adjoint free Dirac Hamiltonian and a modewise unitary evolution. This chapter proves that they describe the same dynamics. The infinitesimal generator is exactly $-iH$, and its domain is precisely the maximal Hamiltonian domain.

The centered Fourier generators also converge on that domain and in the strong resolvent sense. A finite third-order spatial Fourier moment supplies a quadratic spacing bound for the propagator, uniform on each bounded time interval. The argument concerns a fixed flat torus and an unchanged infinite Fourier index set.

These results are supplied as written mathematical proofs. They are not newly compiler-certified Lean declarations, and they do not identify the model with a physical particle or with an interacting continuum theory.

'''
upd(g,pre+intro+body,'Recast the spectral bridge as a book chapter and remove release ledger')

# Legacy physical-model sources: preserve parameters, equations, labels, tests, and negative results.
for sub in ['backreaction','cosmology']:
 base=S/sub
 for p in base.rglob('*.tex'):
  s=p.read_text()
  for a,b in {
    'frozen benchmark':'specified benchmark','Frozen benchmark':'Specified benchmark',
    'frozen rapid-crossing':'specified rapid-crossing','Frozen rapid-crossing':'Specified rapid-crossing',
    'frozen distribution':'prescribed distribution','Frozen distribution':'Prescribed distribution',
    'frozen parameter set':'fixed parameter set','frozen ansatz':'prescribed ansatz',
    'frozen cosmological branch':'specified cosmological branch',
    'current scale-covariant':'scale-covariant',
    'This block adds results that were not merely carried forward from the parent volumes.':'The central results separate symmetry, conservation, approximation, and physical production.',
    'The most important new result is negative.':'The energy-budget result is a central obstruction.',
    'What this block changes':'What the analysis establishes',
    'what this block changes':'what the analysis establishes',
    'this block':'this analysis','This block':'This analysis',
    'The present block':'This analysis',
    'research edition':'account',
  }.items():s=s.replace(a,b)
  upd(p,s,'Remove development chronology from physical-model prose without changing equations')

broot=S/'backreaction'/'Projector_Refinement_Physics_Covariant_Backreaction_Bridge.tex'
t=broot.read_text();pre=t[:t.index('\\begin{document}')]
# Keep mathematical environments and macros. Alter only publication layout.
pre=re.sub(r'\\usepackage\[paperwidth=.*?\]\{geometry\}',r'\\usepackage[letterpaper,left=.87in,right=.87in,top=.84in,bottom=.84in,headheight=20pt,headsep=16pt,footskip=25pt]{geometry}',pre)
pre=pre.replace(r'\usepackage{lmodern}',r'\usepackage{mathpazo}')
pre=pre.replace('\\definecolor{BridgeBlue}{RGB}{31,57,84}','\\definecolor{BridgeBlue}{HTML}{10283F}')
pre=pre.replace('\\definecolor{BridgeGreen}{RGB}{45,111,79}','\\definecolor{BridgeGreen}{HTML}{078A98}')
pre=pre.replace('\\definecolor{BridgeGold}{RGB}{177,132,47}','\\definecolor{BridgeGold}{HTML}{C99853}')
pre+=r'''
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt plus .5pt minus .5pt}
\fancyhf{}\fancyhead[L]{\sffamily\scriptsize KOMOREBI PHYSICS}
\fancyhead[R]{\sffamily\scriptsize\color{BridgeBlue} COVARIANT FIBER DYNAMICS}
\fancyfoot[L]{\sffamily\scriptsize\color{BridgeGray} CONTINUUM, GEOMETRY AND REFINEMENT}
\fancyfoot[R]{\sffamily\small\color{BridgeBlue}\thepage}
\renewcommand{\headrulewidth}{0pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[L]{\sffamily\scriptsize KOMOREBI PHYSICS}\fancyfoot[R]{\sffamily\small\thepage}\renewcommand{\headrulewidth}{0pt}}
'''
opening=r'''\begin{document}
\mainmatter
\thispagestyle{plain}
{\sffamily\small\color{BridgeGreen} KOMOREBI PHYSICS / MATTER AND BACKREACTION\par}
\vspace{14pt}{\Huge\bfseries\color{BridgeBlue}Covariant Refinement-Fiber Dynamics\par}
\vspace{12pt}{\large Symmetry, constraint closure, energy availability, and radiative bounds\par}
\vspace{15pt}\textcolor{BridgeGold}{\rule{\linewidth}{.8pt}}\par\vspace{9pt}
Arithmetic refinement supplies a Hilbert-space structure and compatible operators. A physical fiber model additionally needs a covariant action, a state-selection rule, and a consistent energy budget. This account examines those requirements before a refinement distribution is propagated through cosmology.

At finite depth, explicit symmetry assumptions constrain the spectral channel without fixing every coupling. Covariant stress exchange and canonical closure then test compatibility with spacetime dynamics. The production calculation poses a different question: can the proposed crossing actually generate the distribution used by the observable model?

\begin{negativebox}[The controlling physical boundary]
For the specified benchmark, the unprojected production spectrum exceeds the available crossing energy by $\BridgeOverdraw$. A common normalization factor preserves a distribution's shape but does not solve the coupled background and mode equations. The cosmological calculations that follow are conditional on the prescribed normalized distribution, not evidence of a controlled microscopic production history.
\end{negativebox}
The mathematical identities remain meaningful after this physical benchmark fails its energy test. Written theorems, bounded computations, and model assumptions retain separate evidential roles.
'''
# No subsidiary book covers, duplicate navigation, or project-management assessment.
body=r'''
\input{source/01_audit}
\input{source/02_covariant_eft}
\input{source/03_canonical_closure}
\input{source/04_universality}
\input{source/05_backreaction}
\input{source/06_radiative}
\input{source/07_assessment}
\appendix
\input{source/appendix_reproducibility}
\backmatter
\chapter*{Bibliographic scope}\addcontentsline{toc}{chapter}{Bibliographic scope}
The internal derivations are not an exhaustive specialist priority audit. Comparisons with hierarchical field theory, multiscalar effective models, preheating, scalar-tensor theories, constrained Hamiltonian gravity, and adic quantum models require their own source-level review. No literature-priority or empirical-preference claim is inferred from the breadth of this construction.
\end{document}
'''
upd(broot,pre+opening+body,'Integrate the fiber model into the book with its energy obstruction stated before phenomenology')

# Keep exact provenance, but move it to the technical appendix rather than interrupting physics.
p=S/'backreaction/source/01_audit.tex';s=p.read_text()
s=s.replace('Audit of the Two-Volume Record','Mathematical Structure and Physical Assumptions').replace('Why this bridge is the next block','From refinement to a physical fiber')
s=s.replace('The first volume develops','The foundational treatment develops').replace('The second volume takes','The cosmological model takes').replace('The two books leave one especially important seam.','These constructions leave an important physical interface.')
s=s.replace('What the dark-sector volume actually assumes','Assumptions of the matter model').replace('Status before this bridge','Role in the model')
s=s.replace('The frozen Volume II benchmark','The specified cosmological benchmark')
a=s.index('\\section{Source integrity and executable provenance}');b=s.index('\\section{Claim migration caused by this audit}',a)
provenance=s[a:b];s=s[:a]+s[b:]
s=s.replace('Claim migration caused by this audit','Mathematical and physical status').replace('The audit changes the status of several statements without discarding the whole program.','The following table distinguishes what is proved, what is computationally tested, and what remains a physical hypothesis.').replace('Status after audit','Status').replace('new theorem','theorem')
s=s.replace('This is a stronger scientific position than simply adding another application.  It preserves what survives direct testing and localizes what must be rebuilt.','The distinction is decisive for the following cosmological analysis. A conditional distribution can be transported consistently without having been produced by a controlled microscopic solution.')
upd(p,s,'Move archive-history material into the technical appendix and retain the physical assumptions')
pa=S/'backreaction/source/appendix_reproducibility.tex';ap=pa.read_text();at=ap.index('\\section{Scope of the executable record}')
ap=ap[:at]+provenance+'\n'+ap[at:]
ap=ap.replace('Reproducibility Contract','Computational Evidence and Reproducibility').replace('newly introduced in this bridge','associated with this model').replace('Parent-release audit','Source-archive audit').replace('Release acceptance record','Integrity checks')
a=ap.index('\\section{Known erratum in the parent record}');b=ap.index('\\section{Numerical methods and tolerances}',a)
ap=ap[:a]+r'''\section{Source erratum}
The supporting technical supplement contains malformed status-label typography. The original file is retained unchanged in the provenance archive. The defect concerns presentation rather than a mathematical identity. Source identity and the corrected reading text are recorded separately.

'''+ap[b:]
ap=ap.replace('The bridge package is acceptable as an internal research release when all of the following hold:','The source integrity checks distinguish the following requirements:')
ap=ap.replace('This acceptance record concerns release integrity.  It is deliberately weaker than scientific validation.','These requirements concern artifact integrity, not scientific validation.')
upd(pa,ap,'Consolidate source failures and numerical provenance in the technical record')

p=S/'backreaction/source/07_assessment.tex';s=p.read_text()
s=s.replace('Scientific Assessment and the Decisive Next Gate','Physical Interpretation and Unresolved Comparisons').replace('The strongest conclusion supported now','Mathematical construction and physical validation')
a=s.index('The two-volume program is unusually broad.');b=s.index('\\section{What this bridge establishes}',a)
s=s[:a]+r'''A coherent mathematical construction, a controlled physical model, and an empirically supported theory are different kinds of result. The finite-depth covariant and canonical identities concern a stated model. The production spectrum additionally requires a controlled solution of the coupled dynamics. Empirical identification requires comparison with data and competing models.

The energy-budget obstruction locates a failure in the specified production history. It does not invalidate projector reconstruction, matrix-corner calculus, or the conditional transport of a prescribed distribution. It does prevent that distribution from being called a prediction of the microscopic crossing without a new dynamical argument.

'''+s[b:]
s=s.replace('What this bridge establishes','Established model statements').replace('What this bridge does not establish','Limits of the model').replace('The next decisive calculation','A controlled production comparison').replace('The immediate continuation is not another observable template.','An additional observable template does not resolve the upstream production problem.').replace('The appropriate description today is precise.','The claim boundary is precise.')
a=s.index('The claim boundary is precise.')
s=s[:a]+r'''The construction supplies exact internal identities, conditional gravitational statements, and an explicitly testable fiber model. Its specified cosmological production benchmark fails a quantified energy-budget test. A viable physical realization must control backreaction, ultraviolet sensitivity, and the transport of any resulting uncertainty through the observable calculations.

The cosmology chapter therefore begins from a prescribed normalized distribution. Its deductions retain their conditional meaning. They do not assume that the unresolved production comparison has succeeded.
'''
s=s.replace('after the present matter bridge, or in parallel with a separate team','alongside the matter comparison').replace('the present matter bridge','the matter construction')
upd(p,s,'Replace progress rhetoric with physical conclusions and the transition to cosmology')

# Cosmology keeps its mathematical appendices and tests, with a direct opening boundary.
croot=S/'cosmology/Projector_Refinement_Physics_Volume_II.tex';t=croot.read_text();pre=t[:t.index('\\begin{document}')]
pre=re.sub(r'\\usepackage\[paperwidth=.*?\]\{geometry\}',r'\\usepackage[letterpaper,left=.87in,right=.87in,top=.84in,bottom=.84in,headheight=20pt,headsep=16pt,footskip=25pt]{geometry}',pre)
pre=pre.replace(r'\usepackage{libertinus}',r'\usepackage{mathpazo}')
pre=pre.replace('Projector-Refinement Physics, Volume II:','Komorebi Physics:')
pre=pre.replace('\\definecolor{MonographBlue}{RGB}{31,57,84}','\\definecolor{MonographBlue}{HTML}{10283F}')
pre+=r'''
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt plus .5pt minus .5pt}
\fancyhf{}\fancyhead[L]{\sffamily\scriptsize KOMOREBI PHYSICS}
\fancyhead[R]{\sffamily\scriptsize\color{MonographBlue} COSMOLOGICAL TRANSPORT}
\fancyfoot[L]{\sffamily\scriptsize\color{MonographGray} CONTINUUM, GEOMETRY AND REFINEMENT}
\fancyfoot[R]{\sffamily\small\color{MonographBlue}\thepage}
\renewcommand{\headrulewidth}{0pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[L]{\sffamily\scriptsize KOMOREBI PHYSICS}\fancyfoot[R]{\sffamily\small\thepage}\renewcommand{\headrulewidth}{0pt}}
'''
opening=r'''\begin{document}\mainmatter
\thispagestyle{plain}
{\sffamily\small\color{MonographBlue} KOMOREBI PHYSICS / COSMOLOGICAL TRANSPORT\par}
\vspace{14pt}{\Huge\bfseries\color{MonographBlue}Cosmology, Dark Sectors, and Structure Formation\par}
\vspace{12pt}{\large Conditional transport from a prescribed refinement distribution\par}
\vspace{15pt}\textcolor{MonographBlue}{\rule{\linewidth}{.8pt}}\par\vspace{9pt}
The preceding fiber model separates a candidate covariant action from the production history used to populate it. This distinction controls the interpretation of the cosmological calculations. The specified rapid-crossing benchmark fails its available-energy test. A common post hoc normalization is not a solution of the coupled background and mode equations.

\begin{monographnote}[The distribution is an input]
The transport, CMB, structure, baryonic, and subhalo calculations below are conditional on a prescribed normalized distribution and on their stated approximations. They are not predictions of a demonstrated microscopic production process. The exact field identities and bounded calculations retain their mathematical meaning under that condition.
\end{monographnote}
The account first fixes relativistic background and perturbation conventions. It then defines the refinement sector, propagates its specified distribution through kinetic and observable models, and identifies linked rejection tests. Numerical controls apply to the declared implementations and parameter choices. They do not establish precision agreement with data or empirical preference over simpler models.
\input{frontmatter/notation}
'''
body=t[t.index('\\part{Relativistic Cosmological Backgrounds'):]
body=re.sub(r'\\part\{[^{}]*\}', '',body)
body=body[:body.index('\\backmatter')]+r'''\backmatter
\chapter*{Bibliographic scope}\addcontentsline{toc}{chapter}{Bibliographic scope}
These derivations and computations are not a complete specialist literature-priority audit. Hidden-sector towers, production mechanisms, scalar trapping, Boltzmann methods, CMB solvers, nonlinear structure, and galaxy-formation models each require their own comparative source review. The absence of an exhaustive priority audit limits historical novelty claims and is separate from the conditional mathematical results presented here.
\end{document}
'''
upd(croot,pre+opening+body,'Make the cosmology interpretation conditional before any observable calculation')
# Reconcile the cosmology open-problem section with the preceding negative result.
p=S/'cosmology/chapters/21_open_problems.tex';s=p.read_text();mark='\\section{Microscopic derivation}'
s=s.replace(mark,r'''\section{Production and backreaction}
The specified rapid-crossing spectrum must be replaced or recovered by a controlled coupled field-and-mode calculation. Its energy overdraw is already a concrete obstruction, not a small unquantified uncertainty. Cutoff stability, a conserved renormalized stress tensor, and consistent propagation of the produced spectrum are prerequisites for a microscopic prediction.
'''+mark)
upd(p,s,'Carry the energy-budget obstruction into the cosmology research boundary')
# Upstream condition placed directly beside the dark-sector mechanism, too.
p=S/'cosmology/chapters/09_scale_covariant_dark_sector.tex';s=p.read_text();ix=s.find('\\section{')
s=s[:ix]+r'''\begin{monographnote}[Production hypothesis]
The rapid-crossing formulas in this chapter describe a specified-background approximation. The covariant fiber analysis shows that the benchmark spectrum overdraws its available energy. Its normalized shape is therefore an input to downstream transport, not an established solution of the coupled production problem.
\end{monographnote}
'''+s[ix:];upd(p,s,'Place the physical condition at the mechanism, not only in front matter')

# Shared monograph typography: same design throughout, no dated standalone cover.
p=M/'komorebi-monograph.sty';sty=p.read_text()
sty=re.sub(r'\\setmainfont\{P052\}\[[^\n]*\]',r'\\setmainfont{P052}',sty)
sty=re.sub(r'\\setsansfont\{NimbusSans\}\[[^\n]*\]',r'\\setsansfont{Nimbus Sans}[Scale=.94]',sty)
sty=re.sub(r'\\setmonofont\{lmmono10\}\[[^\n]*\]',r'\\setmonofont{lmmono10-regular.otf}[Scale=.88]',sty)
sty=sty.replace(r'\setmathfont{latinmodern-math.otf}[Path=fonts/]',r'\setmathfont{latinmodern-math.otf}')
sty=sty.replace('{245D60}','{078A98}').replace('{212B34}','{1C3445}').replace('{EEF3F2}','{E5F3F4}')
sty=sty.replace('OPERATION KOMOREBI','KOMOREBI PHYSICS').replace('REALIZATION CALCULUS','CONTINUUM, GEOMETRY AND REFINEMENT')
a=sty.index('\\newcommand{\\KomorebiCover}');b=sty.index('\\newcommand{\\KomorebiOpeningNote}',a)
sty=sty[:a]+r'''\newcommand{\KomorebiCover}{%
  \thispagestyle{plain}\begingroup
  {\sffamily\fontsize{9}{12}\selectfont\color{accent}KOMOREBI PHYSICS\par}
  \vspace{14pt}
  {\fontsize{27}{32}\selectfont\bfseries\raggedright\KomorebiTitle\par}
  \vspace{12pt}
  {\fontsize{14}{19}\selectfont\color{muted}\KomorebiSubtitle\par}
  \vspace{16pt}\noindent\textcolor{accent}{\rule{\linewidth}{.8pt}}\par
  \vspace{8pt}\endgroup\color{ink}\normalfont
}
'''+sty[b:]
upd(p,sty,'Apply the physics palette and compact chapter openings without dates or release labels')
# Suppress build-specific metadata in titles.
for p in M.rglob('*.tex'):
 if 'Collection' in p.name or p.name=='collection_body.tex':continue
 s=p.read_text()
 s=re.sub(r'\\renewcommand\{\\KomorebiEdition\}\{[^\n]*\}',r'\\renewcommand{\\KomorebiEdition}{}',s)
 s=re.sub(r'(\\clearpage\s*){2,}',r'\\clearpage\n',s)
 upd(p,s,'Remove duplicate forced page breaks and unused edition fields')
(P/'audit'/'editorial_changes_stage2.json').write_text(json.dumps(log,indent=2))
print('stage2 operations',len(log))
