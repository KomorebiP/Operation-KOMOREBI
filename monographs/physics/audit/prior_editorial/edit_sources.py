from pathlib import Path
import re, json, shutil
W=Path('/mnt/data/physics_editorial_work'); P=W/'publication'; S=P/'source'; M=S/'monographs'; LOG=[]; CONCORD=[]

def write(p,t,why):
 old=p.read_text()
 if old!=t:
  LOG.append({'file':str(p.relative_to(S)),'reason':why,'before':old,'after':t})
  p.write_text(t)

def replace(p,old,new,why='Continuity and publication language'):
 s=p.read_text()
 if old not in s: raise ValueError(f'Missing replacement in {p}: {old[:100]}')
 write(p,s.replace(old,new),why)

def replace_para(p,needle,new):
 s=p.read_text(); ps=re.split(r'\n\s*\n',s); found=0
 for i,q in enumerate(ps):
  if needle in q:ps[i]=new; found+=1
 if found!=1:raise ValueError((str(p),needle,found))
 write(p,'\n\n'.join(ps),'Rewrite a development-history paragraph without altering mathematics')

def balanced_command(s,command):
 pos=0
 while True:
  m=re.search(re.escape(command)+r'\s*\{',s[pos:])
  if not m:return
  a=pos+m.start(); start=pos+m.end(); depth=1; j=start
  while j<len(s) and depth:
   if s[j]=='{' and (j==0 or s[j-1]!='\\'):depth+=1
   elif s[j]=='}' and (j==0 or s[j-1]!='\\'):depth-=1
   j+=1
  yield a,j,s[start:j-1]
  pos=j

# Implementation locators belong to the technical record, not the argument.
for p in list(M.rglob('*.tex')):
 if p.name=='preamble.tex':continue
 t=p.read_text(); spans=list(balanced_command(t,r'\sourcepointer'))
 for a,b,body in spans:CONCORD.append({'file':str(p.relative_to(M)),'source_note':body})
 for a,b,_ in reversed(spans):t=t[:a]+t[b:]
 t=re.sub(r'\\begin\{samepage\}\s*\\end\{samepage\}','',t)
 if spans:write(p,t,'Move implementation locators into the technical source concordance')

# Timeless thematic openings. Conventions and all mathematical text following
# the opening are kept, except local tables of contents removed below.
openings={
'foundations/orientation.tex':r'''\section*{Resolution, dynamics, and reconstruction}
A physical description often begins by separating a state into spatial cells, frequency bands, spin channels, tensor factors, or spectral sectors. Such a separation is useful only when the components can be reconstructed, their interactions can be described, and different resolutions can be compared. Those requirements lead to the calculus developed here.

An orthogonal projector selects a packet. Placing an operator between two projectors gives a transfer block. A skew-adjoint generator determines an antisymmetric current between packet weights. Grouping the labels produces a coarser description in which internal currents cancel. These statements can be understood in a small matrix example before any infinite-dimensional analysis is needed.

The same questions become more demanding when frames move, states become mixed, or the system exchanges information with an environment. Countable resolutions introduce convergence. Unbounded operators introduce domains. Each extension retains part of the finite algebra and adds a hypothesis that must remain visible where it is used.

The free Dirac construction that follows gives these ideas a concrete analytic realization. Fourier modes resolve a spinor field, finite matrices govern its components, and completion leads to a self-adjoint Hamiltonian. Gauge transport, constrained gravity, and arithmetic refinement then test which parts of the same language survive in different settings.

\begin{readerroadmap}[title={The organizing question}]
Which quantities can be reconstructed exactly, which balances survive a change of resolution, and which additional hypotheses are required for an infinite or unbounded system?
\end{readerroadmap}

The mathematical arguments use ordinary complex linear algebra, operator theory, and Hilbert-space analysis. Formal source correspondences and verification records are collected in the technical appendices. Numerical illustrations explain specified examples rather than replacing universal proofs.
''',
'chapters/orientation.tex':r'''\section*{From finite spinors to a continuum Hamiltonian}
The preceding calculus becomes a concrete field construction when Fourier modes are used as packets. Each mode carries a four-component spinor and an explicit Hermitian matrix. The field is reconstructed through an isometric Fourier map. Exact norm preservation, completion, approximation, and control of the adjoint domain justify the passage from finite calculations to continuum analysis.

The setting is a free spinor on a fixed flat three-torus. For every real mass parameter, the resulting Hamiltonian is densely defined, self-adjoint, and closed. Its domain is exactly the first-order weighted Fourier square-summability domain. These assertions include the operator domain, not merely a formal differential expression.

The Hamiltonian and the modewise unitary evolution are first constructed separately. The following chapter, \emph{The Dirac Group and Its Generator}, connects them by proving strong continuity, equality of the full generator domain with the Hamiltonian domain, and the spectral-exponential identity. It also develops graph-domain and strong-resolvent convergence for the centered Fourier family and a quadratic spacing estimate under third-order Fourier regularity.

\begin{readerroadmap}[title={The role of this construction}]
Finite Clifford identities determine each mode. Hilbert-space completion reconstructs the field. Adjoint-domain equality determines the self-adjoint operator. The generator argument then identifies its evolution. These are distinct steps in one continuous mathematical construction.
\end{readerroadmap}

The operator construction has recorded Lean verification. The generator identification and quantitative extensions are supplied as written mathematical proofs, without a compiler certificate for those extensions. The technical appendices identify the exact formal statements and evidence. None of these mathematical results by itself identifies an observed particle or supplies a dynamical spacetime geometry.
''',
'gauge/orientation.tex':r'''\section*{Transport beyond the free field}
The free Dirac construction resolves a translation-invariant field into independent Fourier modes. Gauge coupling changes that organization. Transport between neighboring fibers carries additional information, and a comparison between resolutions must preserve the order and orientation of the links.

A link has a named source and target. Its transformation law is fixed by that direction. Composition cancels the gauge factors at internal endpoints, while a closed path retains conjugation at its basepoint. This elementary mechanism supports the treatment of holonomy, curvature, covariant differences, and refinement.

The finite Maxwell--Dirac example combines matter continuity, electric work, and propagation of the Gauss constraint. Geometric interpolation then separates edge compatibility, curvature defects, and Hilbert normalization. Regularity assumptions turn these structural conditions into quantitative estimates.

The constructions concern specified finite systems and prescribed background connections. A coupled continuum gauge theory additionally requires an operator domain, existence of the field evolution, propagation of constraints, and a convergence theorem in an explicitly chosen topology. Local covariance does not discharge those obligations.

The visual atlas develops the finite examples. The technical appendix records formal source coverage and the limits of its verification evidence. The argument here remains readable without following implementation identifiers.
''',
'gravity/orientation.tex':r'''\section*{Geometry, constraints, and strong fields}
Gauge covariance identifies compatible transport. Gravity asks for more: the geometry, constraints, and evolution must be specified together. A propagation rule, a canonical constraint algebra, and an evolved matter system are different mathematical objects, with different hypotheses.

This account proceeds from weighted transport geometry and reduced Gowdy evolution to finite linearized ADM constraints. The nonlinear obstruction explains why a nonzero derivative cannot satisfy the ordinary Leibniz rule on a complete finite pointwise algebra. Matrix moment maps, homological transfer, and spectral representations provide alternatives in their stated settings.

A real Lorentzian action supplies a classical gauge-theoretic parent. Boundary constructions and local second-class reduction retain their regularity and nondegeneracy conditions. The spherical sector makes mass, flux, and horizon diagnostics explicit, allowing exact identities to be compared with bounded numerical experiments.

The results do not amount to a complete continuum or quantum theory of gravity. A manufactured electrovac trajectory is not an existence theorem for nonlinear collapse. A scalar trapped-sphere diagnostic is not a continuum formation theorem without stability, convergence, and event control. These distinctions are part of the mathematics rather than qualifications added after it.

The shared resolution language continues in the arithmetic and polyphase constructions that follow. It makes the state spaces, comparison maps, and residual obstructions explicit without equating their physical interpretations.
''',
'adic/orientation.tex':r'''\section*{Arithmetic resolution and quantum refinement}
The preceding constructions compare geometric and spectral resolutions. Arithmetic refinement provides another concrete family: finite unit registers, Haar packets, hierarchical Hamiltonians, and polyphase channels. The question remains the same. Which maps preserve the state, which preserve the dynamics, and what additional structure appears when hidden components are eliminated?

Normalized Haar averages identify coarse states inside a fine Hilbert space. Compatibility of the Hamiltonian, rather than normalization alone, determines whether that subspace carries the same evolution. Schur reduction and its time-domain memory equation describe the effect of components that cannot simply be discarded.

Infinite depth introduces a separate analytic problem. The hierarchical model specifies a common Hilbert space, a maximal operator domain, and the topology of approximation. Spectral decimation and hypergeometric companion functions provide exact coordinates within their declared domains. None of these identities alone identifies arithmetic depth with a physical observable.

The following account of covariant fiber dynamics supplies a candidate physical coupling and examines its energy and production constraints. That transition separates a mathematical refinement structure from a proposed model of matter.

The visual and verification appendices distinguish exact identities, finite computations, and formal coverage. The infinite arithmetic hierarchy is presented with its written proofs and is not assigned a Lean certificate beyond the statements specifically identified there.
'''
}
for rel,new in openings.items():
 p=M/rel;s=p.read_text(); idx=s.find('\\clearpage')
 if idx<0:raise ValueError(rel)
 tail=s[idx:]
 write(p,new+'\n'+tail,'Replace standalone editorial preface with a thematic book introduction')

# Preserve full source orientation and boundary text in the historical input archive;
# the public argument has an updated conclusion that matches the following chapter.
p=M/'foundations/conclusion.tex';s=p.read_text()
s=s.replace('From the foundations to the next physical constructions','From packet calculus to field dynamics')
s=s.replace('The formal identification of the already constructed unitary evolution with that Hamiltonian\'s spectral evolution remains an explicit next target.','The following generator chapter proves its spectral-evolution identification at the level of mathematical analysis. Formal certification of that identification is recorded separately from the operator construction.')
s=s.replace('Block49 provides the self-adjoint physical Hamiltonian.','The Fourier construction provides the self-adjoint physical Hamiltonian.')
s=s.replace('The next thematic paper is gauge covariance and geometric refinement.','Gauge covariance and geometric refinement then extend the transport setting.')
s=s.replace('The remaining volumes develop','The remaining parts of this book develop')
s=s.replace("The source archives remain part of the edition. They preserve earlier formulations, computational records, and the route by which hypotheses were sharpened. The new volume supplies a continuous reading path through that material, with the exact source map and reproducible figures alongside it.","The same reading discipline applies across the book: exact algebra, analytic reconstruction, and physical interpretation must each carry their own hypotheses.")
write(p,s,'Connect foundations to the completed written generator argument and the book sequence')

p=M/'gauge/conclusion.tex';s=p.read_text().replace('What the construction supplies, and what comes next','Gauge transport and its continuum comparison')
s=s.replace('Block49 constructs the self-adjoint physical torus Hamiltonian on its weighted Fourier domain. The formal identification of the previously constructed unitary group with its spectral evolution remains a separate target.','The free construction gives a self-adjoint physical torus Hamiltonian on its weighted Fourier domain. The generator chapter supplies its spectral-evolution identification as a written proof. Its formal certification remains distinct from the recorded operator certificate.')
a=s.index('The constrained-gravity volume is the next editorial step');b=s.index('\\begin{readerroadmap}',a)
s=s[:a]+'''The constrained-gravity chapter examines the additional obligations imposed by a dynamical geometry: regular-chart reduction, constraint closure, boundary terms, and strong-field evolution. Arithmetic refinement and cosmological transport retain the same requirement to identify their state spaces and comparison maps, without sharing all of the gauge model's assumptions.\n\n'''+s[b:]
write(p,s,'Replace editorial roadmap with the actual transition to constrained gravity')

p=M/'gravity/conclusion.tex';s=p.read_text().replace('The completed constructions and the next obligations','Constraint structure and the limits of reconstruction')
a=s.index('\\subsection{The next volume in the series}');b=s.index('\\begin{readerroadmap}',a)
s=s[:a]+r'''\subsection{From geometric to arithmetic refinement}
The next chapter develops register factorization, Haar packets, spectral reduction, and infinite-depth quantum hierarchies. It changes the model while preserving the discipline used here: finite identities, refinement compatibility, and analytic limits require separate arguments. The covariant fiber and cosmology chapters then examine whether a chosen refinement sector admits a physically controlled production history and consistent observable transport.

'''+s[b:]
write(p,s,'Replace future editorial plans with a mathematical transition')

p=M/'adic/conclusion.tex';s=p.read_text();a=s.index('Five thematic sets are now assembled')
s=s[:a]+'''A candidate fiber interpretation must specify how refinement degrees of freedom couple to spacetime and how they are populated. The covariant fiber chapter addresses that question before the cosmological calculations are used. Its energy-budget obstruction remains controlling: downstream transport from a prescribed distribution is meaningful, but it is not evidence that the proposed production history generated that distribution.\n'''
write(p,s,'Carry the production obstruction forward into the cosmology sequence')

# Dirac transition: the correspondence table is retained in the source concordance.
p=M/'chapters/boundary.tex'; original=p.read_text()
(P/'audit'/'dirac_historical_boundary.tex').write_text(original)
new=r'''\clearpage
\part{The operator and its evolution}
\section{The completed operator construction}
The free field now has two precise mathematical descriptions. Modewise exponentials define a unitary evolution on the complete coefficient space and, by Fourier conjugation, on physical torus fields. The maximal coefficient multiplier defines a self-adjoint unbounded Hamiltonian whose domain is the first-order weighted Fourier space.

These constructions answer different questions. Norm preservation determines the behavior of the bounded evolution maps. Self-adjointness determines the operator and its adjoint domain. Finite-packet graph approximation controls the state and its Hamiltonian image at the same time. No one of these statements can replace the others.

\begin{longtable}{@{}L{.36\linewidth}L{.55\linewidth}@{}}
\toprule
Construction & Mathematical role\\\midrule\endhead
Clifford mode matrices & Exact mass shell and finite-dimensional self-adjointness.\\
Mode exponentials & Group identities and unitary spinor dynamics.\\
Completed coefficient evolution & Removal of finite support by norm stability.\\
Fourier equivalence & Lossless transport between coefficients and physical fields.\\
Maximal Hamiltonian & Density, adjoint-domain equality, and closedness.\\
Weighted domain & A mass-independent characterization of first-order regularity.\\
\bottomrule
\end{longtable}

The explicit spectral-projector formula, sharp finite Duhamel coefficient, and worked examples are deductions with proofs in the text. The technical appendix distinguishes these deductions from their exact formal correspondences. Recorded compiler evidence applies to the named statements and hypotheses, not to every sentence of interpretation.

\section{Connecting the group to its generator}
The next chapter proves that the constructed group is the spectral evolution of this Hamiltonian:
\[
\mathcal U(t)=e^{-itH_m^{\mathrm{phys}}}.
\]
The proof establishes strong continuity and differentiates on the full Hamiltonian domain with control of the Fourier tail. The reverse domain inclusion then shows that the infinitesimal generator has exactly that domain. The equality is therefore a conclusion about the complete Hilbert-space group, not an inference from agreement on finitely many modes.

This is a written mathematical result. Its Lean formalization remains outside the recorded certificate for the Hamiltonian construction. The separation concerns verification coverage, not an additional unstated hypothesis in the analytic theorem.

\section{Operator limits and regularity}
The centered family acts on the same infinite Fourier index set as the continuum family. The generator chapter proves convergence on the Hamiltonian domain and strong-resolvent convergence. It also gives a quadratic spacing estimate for the propagator, uniformly on bounded time intervals, under an explicit third-order spatial Fourier moment condition.

The regularity condition is essential to that estimate. Arbitrary square-integrable data retain the strong compact-time convergence statement, but are not assigned a universal quadratic rate. The first-order Hamiltonian domain alone is not substituted for the third-order moment used by the quantitative bound.

A changing finite spatial grid is a different comparison problem. It needs sampling, aliasing control, embeddings into the physical Hilbert space, and compatibility with geometric refinement. The centered multiplier family does not supply those ingredients merely by using a spacing parameter.

\section{Beyond the free field}
A prescribed background connection changes the operator and its domain. Dynamical gauge fields additionally require field energy, a Gauss constraint, matter backreaction, and an existence theory. The gauge chapter develops the finite transport and refinement ingredients for these questions without treating them as a coupled continuum evolution theorem.

The gravity, arithmetic refinement, and cosmology chapters retain their own mathematical and physical assumptions. The free model provides a controlled analytic sector to which such constructions may be compared. It neither derives a dynamical metric nor predicts an observational parameter.
'''
write(p,new,'Reconcile the operator chapter with the generator and resolvent proofs that follow')

# Remove duplicate local navigation; the assembled book supplies global navigation.
for p in M.rglob('*.tex'):
 if p.name=='preamble.tex':continue
 s=p.read_text()
 s=re.sub(r'\\tableofcontents\b','',s)
 s=re.sub(r'\\pagenumbering\{(?:roman|arabic)\}','',s)
 s=re.sub(r'\\addcontentsline\{toc\}\{section\}\{Preface\}','',s)
 # Local parts become thematic section leaves, not another book-level part system.
 s=re.sub(r'\\part\{([^{}]*)\}',r'\\section*{\1}',s)
 write(p,s,'Use one book-level contents and pagination system')

# Short exact rewrites outside the front matter.
replace_para(M/'chapters/finite_core.tex','The following proof retains the explicit Duhamel bound',r'''The following proof gives an explicit Duhamel bound, including its sharp coefficient. This is an ordinary mathematical deduction with a complete proof. The formal compact-time convergence argument uses exponential continuity and is identified separately in the verification appendix.''')
replace_para(M/'gravity/constraints.tex','The proposition isolates the spectral transfer argument.',r'''The proposition isolates the spectral transfer argument. The continuum connection calculation is its stated input. Neither a floating-point test nor a source reference can replace that input. The construction is an ordinary mathematical result rather than a certified Lean theorem.''')
replace_para(M/'gravity/constraints.tex','The technical supplement already labels this boundary claim conditional.',r'''This proposition states the exact missing implication. Off-shell closure of the bulk BRST transformations is insufficient to prove its boundary moment-map hypotheses. The action-split computations establish the split and tangential Cartan identities. They do not construct every normal embedding variable or verify a complete boundary symplectic reduction. The boundary result remains conditional on the hypotheses printed in its statement.''')
replace_para(M/'gravity/strong_fields.tex','The original verification JSON records nineteen passed checks.',r'''The electrovac verification record contains nineteen passed checks. The symbolic identity and archived data structure have supporting audit records, but these are distinct from a replay of the electrovac evolution. The numerical table is retained as recorded evidence. Its environment and command provenance are specified in the verification appendix.''')
replace_para(M/'gravity/strong_fields.tex','The original scalar verifier records twelve passed checks.',r'''The scalar verification record contains twelve passed checks. Two concern symbolic identities. The remaining checks are bounded numerical tests with declared thresholds. The symbolic audit, null-channel algebra, and seven-row data structure have separate supporting records. Those checks do not constitute a replay of the full collapse or an authentication of its original execution environment. The verification appendix states that evidence boundary.''')

# Root templates keep bibliographic titles but no release stamp or extra mini-cover.
for p in M.glob('Physics_*.tex'):
 if 'Collection_Guide' in p.name:continue
 s=p.read_text()
 s=re.sub(r'\\renewcommand\{\\KomorebiEdition\}\{[^\n]*\}',r'\\renewcommand{\\KomorebiEdition}{}',s)
 s=s.replace('An explicit construction through Block 49 with proofs, domain control, worked examples, and a precise continuation boundary.','Finite spinor dynamics, Fourier completion, and the exact domain of the physical Hamiltonian.')
 s=s.replace('The Physics Formalization\\Through Block 49','Formal Verification of the\\Free Dirac Operator')
 s=s.replace('The Physics Formalization Through Block 49','Formal Verification of the Free Dirac Operator')
 write(p,s,'Use publication titles without internal release identifiers')

# Technical prose: preserve exact filenames, toolchain pins, failure records, and
# numerical provenance while removing the editorial voice of an ongoing release.
for p in M.rglob('*.tex'):
 if p.name in ['preamble.tex','collection_body.tex','Physics_Collection_Guide.tex']:continue
 s=p.read_text()
 replacements={
  'This edition adds':'This account includes',
  'this edition adds':'this account includes',
  'The present edition':'This account',
  'the present edition':'this account',
  'This edition does not':'This account does not',
  'This edition did not':'The accompanying preparation record did not',
  'this edition does not':'this account does not',
  'this edition did not':'the accompanying preparation record did not',
  'in this edition':'in this account',
  'for this edition':'for the documented audit',
  'of this edition':'of this account',
  'This edition':'The accompanying record',
  'this edition':'the accompanying record',
  'The recovered ':'The ',
  'the recovered ':'the ',
  'recovered sources':'supporting sources',
  'recovered archive':'source archive',
  'recovered volume':'source volume',
  'recovered chapter':'source chapter',
  'the new monograph':'the monograph',
  'the new volume':'this chapter',
  'the new exposition':'the exposition',
  'The new exposition':'The exposition',
  'The new monograph':'The monograph',
 }
 for a,b in replacements.items():s=s.replace(a,b)
 write(p,s,'Remove development-session phrasing while retaining evidence scope')

# Bibliographic provenance remains exact where necessary, but no release date in main narrative.
p=M/'adic/primary_context.tex';s=p.read_text()
s=s.replace('version 1.2.8 (15 September 2026),\n','')
s=s.replace('revision 24 August 2017, ', '')
s=s.replace('The NIST pages retrieved on 9 October 2026 identify version 1.2.8, released 15 September 2026. ','')
s=s.replace('were inspected in the versions stated above','are used only for the contextual comparisons stated above')
write(p,s,'Keep mathematical literature context without a web-retrieval diary')

# Store edits before subsequent source-specific passes.
(P/'audit'/'editorial_changes_stage1.json').write_text(json.dumps(LOG,indent=2))
(P/'audit'/'source_concordance.json').write_text(json.dumps(CONCORD,indent=2))
print('Changed file operations',len(LOG),'source correspondence records',len(CONCORD))
