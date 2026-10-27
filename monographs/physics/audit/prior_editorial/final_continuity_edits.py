from pathlib import Path
import json
R=Path(__file__).resolve().parent;S=R/'source/monographs';changes=[]
def rep(path,old,new):
 p=S/path;s=p.read_text();n=s.count(old)
 if n!=1:raise ValueError((path,n,old[:80]))
 p.write_text(s.replace(old,new));changes.append({'source':str(p.relative_to(R)),'before':old,'after':new})
rep('chapters/orientation.tex','represented by named declarations in the Block 49 archive or its predecessors','represented by named declarations in the retained formal source')
rep('foundation_visual/visual_body.tex','This atlas neither enlarges the checked frontier beyond Block 49 nor reports a new Lean build.','The atlas illustrates the mathematics and does not supply an additional compiler certificate.')
rep('foundation_visual/visual_body.tex','The current Block 49 endpoint is precise because those passages are stated separately.','Keeping these passages separate makes the operator construction and its hypotheses precise.')
rep('gauge_visual/visual_body.tex','The formal endpoint remains the inherited Block 49 archive; the gauge results discussed here occupy earlier blocks and do not by themselves supply coupled dynamical gauge-field evolution.','The selected formal gauge results establish transport and refinement identities. They do not by themselves supply coupled dynamical gauge-field evolution.')
rep('gravity_visual/visual_body.tex','This atlas reports no new Lean compilation. The Block 49 frontier concerns the previously archived free Dirac development. Ordinary source derivations and finite verification scripts support the gravity chapters at their stated scope. The verification companion records that distinction explicitly.','The gravity chapters are supported by written derivations and finite computations at their stated scope. The retained formal free-Dirac construction does not certify the gravitational model. The verification companion records the distinction between these kinds of evidence.')
rep('gravity_visual/visual_body.tex','how the formal Block 49 development relates to this gravity set','which formal building blocks apply to the gravitational constructions')
rep('adic_visual/visual_body.tex',r'\paragraph{What is new in this account.}',r'\paragraph{Construction of the figures.}')
rep('adic_visual/visual_body.tex','from newly constructed small arrays or explicit scalar families','from small arrays or explicit scalar families')
rep('gauge/refinement.tex','The free-torus Hamiltonian completed at Block 49 provides a later operator endpoint for the ungauged branch','The self-adjoint free-torus Hamiltonian provides an operator endpoint for the ungauged branch')
p=S/'lean/lean_body.tex';s=p.read_text();start=s.index(r'\section{The exact continuation boundary}');end=s.index(r'\section{Historical block index}',start)
old=s[start:end]
new=r'''\section{Written extensions and formal coverage}

The retained formal source constructs both the full continuum unitary evolution and the self-adjoint physical Hamiltonian. The chapter \emph{The Dirac Group and Its Generator} gives a written proof connecting them. It proves strong continuity, identifies the complete generator domain with the maximal Hamiltonian domain, and establishes the spectral-exponential identity. That proof is not represented by compiler-certified declarations in the supplied archive.

The distinction is one of verification coverage, not an unresolved identification in the mathematical narrative. Bounded mode exponentials and the full coefficient and physical evolutions have formal source counterparts. The full-domain derivative argument, the reverse generator-domain inclusion, and the spectral-exponential identification still require a checked formal implementation.

The same chapter proves graph-domain and strong-resolvent convergence for the centered Fourier family on the fixed infinite coefficient space. It also gives quadratic approximation bounds under a third-order Fourier moment. These written extensions have not been added to the retained compiler evidence. A changing finite spatial lattice is a separate comparison problem requiring sampling, interpolation, aliasing control, and compatible domains.

The regular-connection link estimates also remain to be transported into a complete background-coupled Hamiltonian and evolution. Dynamical gauge fields require additional degrees of freedom and a Gauss constraint. Gravitational dynamics, cosmological production, and empirical predictions do not follow from the formally checked free-matter construction. Declaration totals do not measure completion of those physical problems.

'''
p.write_text(s[:start]+new+s[end:]);changes.append({'source':str(p.relative_to(R)),'before':old,'after':new})
rep('gauge_lean/lean_body.tex',"The Block49 continuation file accordingly lists background gauge coupling as a remaining target. It also retains the free theory's spectral-exponential identification, graph or resolvent convergence, and stronger weighted rates.","The Block49 continuation file accordingly lists background gauge coupling as a remaining target. The generator chapter in this volume supplies written proofs of the free theory's spectral-exponential identification, centered graph and resolvent convergence, and stronger weighted rates. Their formal implementation remains outside the retained compiler evidence.")
(R/'audit/editorial_changes_final_continuity.json').write_text(json.dumps(changes,indent=2))
print(len(changes),'edits')
