from pathlib import Path
import re
M=Path('/mnt/data/physics_editorial_work/publication/source/monographs')
items={
'foundations/references.tex':[
r'\item Komorebi P. \emph{Projector Refinement Physics, Volume I}. The foundational source studies cover transfer calculus, mixed and open dynamics, countable resolutions, unbounded domains, positive effects, and matrix-corner derivations. The technical source concordance identifies the relevant statements.',
r'\item Komorebi P. \emph{Projector Refinement Physics, Volume I: Technical Supplement}. Claim statements, formula registries, computational checks, and the hypotheses delimiting their conclusions.',
r'\item Komorebi P. \emph{Komorebi Physics formal source}. The foundations verification appendix gives declaration identities, retained compiler evidence, and the limits of its coverage.',
r'\item Komorebi P. \emph{Fourier Packets and the Continuum Dirac Operator}. The free-field construction in this book.'],
'gauge/references.tex':[
r'\item Komorebi P. \emph{Projector Refinement Physics, Volume I}. The Abelian gauge and ordered non-Abelian holonomy studies supply the finite field equations and matrix identities. These are written mathematical arguments. Exact formal coverage is identified separately.',
r'\item Komorebi P. \emph{Komorebi Physics formal source}. The gauge verification appendix records the transport and refinement declarations, their hypotheses, and the limitations of the retained compiler evidence.',
r'\item Komorebi P. \emph{Projectors, Packets, and Transfer} and \emph{Fourier Packets and the Continuum Dirac Operator}. The packet framework and free-field operator construction in this book. Extending the latter to a background connection requires the domain and evolution comparisons stated here.'],
'gravity/references.tex':[
r'\item Komorebi P. \emph{Projector Refinement Physics, Volume I}. The source studies cover weak fields, holonomy, Gowdy reduction, linearized ADM constraints, nonlinear transfer, resolved connections, the Lorentzian parent, regular reduction, electrovac geometry, and scalar collapse.',
r'\item Komorebi P. \emph{Projector Refinement Physics, Volume I: Technical Supplement}. The nonlinear and strong-field claim dossiers specify boundary, spectral, and numerical hypotheses. The verification appendix maps these hypotheses to the constructions used here.',
r'\item Komorebi P. \emph{Komorebi Physics formal source}. Its projector, gauge, and free Dirac results provide related mathematical infrastructure. They do not constitute a compiler certificate for the nonlinear gravity and collapse statements.'],
'adic/references.tex':[
r'\item Komorebi P. \emph{Projector-Refinement Physics, Volume I}. The arithmetic source studies cover unit registers, Haar refinement, finite-adelic dynamics, product walks, radial self-energy, polyphase structure, infinite Haar limits, spectral renormalization, and hypergeometric companion functions.',
r'\item Komorebi P. \emph{Volume I Technical Supplement and Independent Review Dossier}. The arithmetic claim dossiers and formula registries specify the scope of the corresponding derivations and computational checks.',
r'\item Komorebi P. \emph{Volume I Second Implementation Reproduction}. Finite Haar tests provide internal reproduction evidence for their stated inputs, not for the entire infinite theory.',
r'\item Komorebi P. \emph{Komorebi Physics formal source}. The verification appendix identifies related tower and concrete reconstruction results. Shared interfaces are not a certificate for every arithmetic theorem.']}
for rel,rows in items.items():
 p=M/rel;s=p.read_text();a=s.index('\\begin{enumerate}');b=s.index('\\end{enumerate}',a)
 first=s[a:s.index('\n',a)+1]
 s=s[:a]+first+'\n'.join(rows)+'\n'+s[b:]
 s=s.replace('Preserved project sources','Project sources')
 p.write_text(s)
