"""Bounded reader-facing edits for the collected Realization Calculus book.

No theorem, proof formula, Lean source or formal identifier is rewritten.
The pre-edit texts and exact substitutions are retained for review.
"""
from pathlib import Path
import json, re, difflib, hashlib

G=Path(__file__).resolve().parent
ROOT=G.parent
LOG=[]

def edit(rel, old, new):
    p=G/rel;t=p.read_text()
    if old not in t:
        raise ValueError(f'Missing exact edit in {rel}: {old[:100]}')
    n=t.count(old);p.write_text(t.replace(old,new))
    LOG.append({'path':str(p.relative_to(ROOT)),'occurrences':n,'old':old,'new':new})

def whole(rel,new):
    p=G/rel;edit(rel,p.read_text(),new)

def main():
    # Timeless title furniture. Technical version numbers elsewhere are retained.
    inventory=json.loads((ROOT/'editorial/book_revision/ix_xii_prose_inventory_before.json').read_text())
    for row in inventory:
        p=ROOT/row['path'];rel=p.relative_to(G);t=p.read_text();new=t
        new=re.sub(r'\\renewcommand\{\\KomorebiEdition\}\{[^\n]*\}',r'\\renewcommand{\\KomorebiEdition}{}',new)
        new=re.sub(r'\\date\{[^\n]*\}',r'\\date{}',new)
        for k in ('IX','X','XI','XII'):
            new=new.replace('Core series '+k+'}', 'Chapter '+k+'}')
        new=new.replace(r'\KomorebiKind}{Traditional paper}',r'\KomorebiKind}{Mathematical text}')
        new=new.replace(r'\KomorebiKind}{Traditional monograph}',r'\KomorebiKind}{Mathematical text}')
        new=new.replace(r'\KomorebiKind}{Visual guide}',r'\KomorebiKind}{Visual studies}')
        new=new.replace(r'\KomorebiKind}{Lean and evidence guide}',r'\KomorebiKind}{Formal companion}')
        if new!=t:edit(rel,t,new)

    edit('IX/sources/edition_summary.tex','What this final edition establishes','Principal results')
    edit('IX/sources/edition_summary.tex','Evidence in this edition','Evidence')
    edit('IX/sources/edition_summary.tex',
         'The complete earlier Paper IX development follows alongside the strengthening. Dated appendices retain the original continuation arguments and recovered historical text. Statements about an earlier open target or an earlier build remain records of that checkpoint; the current theorem and scope statements govern this edition. The Lean companion supplies the exact formal source map and distinguishes source reconciliation from compiler execution. The visual guide supplies exact finite examples and theorem-derived diagrams.',
         'The arithmetic development leads to polynomial lifting, deformation and analytic regularity. The appendices give the detailed continuation arguments and the recovered foundational treatment. Where an earlier formulation is retained for comparison, its hypotheses and proof status remain explicit. The formal companion supplies the exact source map and distinguishes source review from compiler execution. The visual studies supply finite examples and diagrams derived from the theorems.')
    edit('IX/sources/edition_summary.tex',
         'This is a project publication under the name Komorebi P. The recorded parallel proof audits are internal computational-assistant reviews. They are not external peer review. The edition makes no claim of journal acceptance, external certification, or global historical priority.',
         'Recorded proof reviews are internal reviews. Formal proof coverage and the scope of each mathematical result are stated separately.')
    edit('IX/sources/main/Paper_IX_Traditional_Final.tex','with dated historical appendices','with detailed mathematical appendices')
    edit('IX/sources/main/parts/00_scope.tex','This edition integrates the original arithmetic framework with the completed\nextensions.','The arithmetic framework is developed together with its completed\nextensions.')
    edit('IX/sources/main/parts/00_scope.tex',
         'The verification record keeps the original dates and scope of each\nbuild. In particular, the latest 91-check polynomial build covers the\npolynomial development, while earlier builds support the arithmetic results.',
         'The formal companion identifies the scope of each recorded build. The\n91-check polynomial record covers the polynomial development; separate\nrecords support the arithmetic results.')
    edit('IX/sources/main/parts/70_continuation.tex',
         'The following mathematical release notes preserve the detailed arguments\nbehind the continuation. They are source-grounded exposition of the completed\nblocks, and retain their original hypotheses. Source-declaration and build\ninventories are supplied separately in the archive. References to earlier\nblocks and then-pending work are dated checkpoint statements; current scope\nis given in the main text.',
         'The following sections develop the detailed arguments behind polynomial\nlifting, correction torsors, compatible towers and local regularity. Each\nconstruction retains its stated hypotheses. The formal companion identifies\nthe corresponding declarations and verification records. The main text\ndistinguishes the completed results from the remaining questions.')
    for n in range(1,12):
        rel=f'IX/sources/main/parts/continuation_{n:02d}.tex';p=G/rel;t=p.read_text();new=t
        new=re.sub(r'(?m)^\\textbf\{(?:Author: )?Komorebi P\. --- 8 September 2026\.\}\n\n','',new)
        new=new.replace('Komorebi P. --- 8 September 2026\n\n','').replace('Author: Komorebi P.\n\n','')
        new=new.replace('This block supplies the actual nonlinear Taylor argument previously\nmissing from the Lean formalization.', 'The nonlinear Taylor argument supplies the correction formula used in\none-step polynomial lifting.')
        new=new.replace('This block formalizes the correction-digit torsor and prime-field counts\nfrom the previous checklist.', 'The correction-digit torsor gives exact prime-field lift counts.')
        new=new.replace('This block completes the nonsingular branch of the passage', 'The nonsingular construction passes')
        new=new.replace('This block formalizes square root uniqueness and nearby-root stability', 'The argument proves square root uniqueness and nearby-root stability')
        new=new.replace('This block constructs actual compatible polynomial towers', 'The construction gives actual compatible polynomial towers')
        new=new.replace('This block combines coefficient perturbation', 'The construction combines coefficient perturbation')
        new=new.replace('This block establishes both analyticity and differentiability', 'The argument establishes both analyticity and differentiability')
        new=new.replace('\\textbf{Fresh verification: PASS --- 40 checks, 244 explicit declaration\naudits.}\n\n','')
        new=new.replace('The six new mathematical modules compile; the\nrelease verification report records the authoritative fresh-build and\naxiom-audit results.', 'The formal companion identifies the six supporting modules and their\nrecorded compiler and axiom-audit results.')
        new=new.replace('The four new\nmathematical modules compile. The fresh verification report and\nindependent audit record the authoritative release status and exact\nsource revisions.', 'The formal companion identifies the four supporting modules and their\nrecorded verification scope.')
        if new!=t:edit(rel,t,new)

    edit('X/manuscript/Paper_X_Block27_Amended.tex',
         'This reading edition joins the preserved Block 27 manuscript, the subsequent residue-counting continuation, and the final checked conditional occupied-system completion. The live internal ledger is 20/20 at the explicitly amended conditional scope. Historical checkpoint totals remain dated evidence of their own source revisions. Universal companion existence, carrier existence, and nonzero occupancy are not inferred. The final assembly and its exact inputs are in Section~\\ref{sec:conditional-final}.',
         'Residual forests describe deformation above a fixed residual root. The later constructions compare compatible families and recover summands inside supplied carriers. Universal companion existence, carrier existence, and nonzero occupancy require additional inputs. Section~\\ref{sec:conditional-final} assembles the conditional result and states those inputs explicitly.')
    whole('X/manuscript/reading_contract.tex',r'''\section*{A route through the chapter}
\addcontentsline{toc}{section}{A route through the chapter}
The central distinction is between a residual root, a coherent branch and an
occupied packet in a carrier. Sections 2--7 develop the finite and formal
machinery. Sections 8--11 assemble its arithmetic uses under stated hypotheses.
The residue-counting arguments appear in Appendix C. Appendix D states the
conditional occupied-system completion theorem. The visual studies provide
worked examples of the same constructions.

\begin{tabularx}{\linewidth}{@{}p{.24\linewidth}X@{}}\toprule
Read for & Follow this route\\\midrule
The mathematical core & Residual partition, reconstruction, smooth and singular counts, cohomology packets and directed seed rank.\\
The arithmetic assembly & Common coefficient data, finite Frobenius separation, explicit carrier summands and inverse-limit-closed profiles.\\
The formal contract & The formal companion explains the terminal theorem and its three direct dependency modules, with a statement register and a hypothesis-by-hypothesis guide.\\
The finite examples & Plates X.1--X.30 show residue tables, projector tests, countermodels and norm-character examples.\\\bottomrule
\end{tabularx}

\paragraph{Two outputs require two sets of inputs.}
The terminal theorem proves that a transported target family exists and that the
declared summand can be recovered inside a supplied compatible carrier. It does
not identify those two objects. An application that needs such an identification
must supply its comparison. Likewise, zero multiplicities are permitted by the
formal assembly, so a nonzero conclusion retains a separate nonzero premise.

\paragraph{Mathematical and formal scope.}
The final source is over the rational absolute Galois group. Carrier data,
constituent comparisons and a completed source family are explicit inputs.
The formal companion distinguishes the amended conditional statements from
stronger existence questions and identifies their recorded verification.
Earlier source contracts remain available in the accompanying research records.
''')
    edit('X/manuscript/conditional_completion.tex',
         'The retained release records 20/20 internal claims checked at their amended and conditional source scopes. This is an assembly theorem with explicit inputs, not unrestricted companion existence or carrier existence.',
         'The twenty internal claims are checked at their amended and conditional source scopes. The assembly theorem uses explicit inputs. Unrestricted companion existence and carrier existence remain separate questions.')
    edit('X/manuscript/residue_continuation_body.tex',
         'The following continuation is retained at its original checkpoint scope. Its 17/20 status and the statement that Claims 9.1, 9.2 and 11.1 remain partial are historical descriptions of that checkpoint. Section~\\ref{sec:conditional-final} supplies the later amended conditional completion. The counting formulas, hypotheses and remaining norm-image obligations below are preserved.',
         'The following arguments develop residue counting and the associated norm-image conditions. Their formulas and hypotheses remain distinct from the amended conditional completion in Section~\\ref{sec:conditional-final}. The formal companion distinguishes the source contracts and their verification status.')

    # Replace a publication-history preface with the mathematical reading route.
    for role in ('traditional','visual_guide','lean_guide'):
        rel=f'XI/publication/source/{role}/reader_route.tex';p=G/rel
        t=p.read_text();new=t
        new=new.replace('Reading this edition','A route through Chapter XI').replace('Five readers with different jobs','The mathematical text and its companions')
        new=new.replace('77 pages, v0.4.0. ', '').replace('36 pages, v0.5.0. ', '')
        new=new.replace('Current scope and research routes','Scope and research routes')
        new=new.replace('Keep all five PDFs together with their delivered filenames. The colored reading links resolve to actual pages of the companion files. Section numbers remain the primary mathematical locators. The included JSON concordance records the resolved page destinations for this edition.',
                        'The reading links connect the mathematical text, visual studies, research companions and formal companion. Section and result numbers remain local to the named treatment. Plate references include the chapter number, so a reference such as Plate XI.32 identifies a visual plate rather than a source version.')
        # Exact historical lineage remains in the source records, not the reading route.
        new=new.replace('Historical obligation 66, historical Theorem 16.2, and all-records row 95 refer to this endpoint\'s lineage. Historical register row 66 is a different statement.',
                        'The formal companion distinguishes this conjecture from the differently numbered statements in the source registers.')
        marker=r'\subsection*{What this revision checks}'
        if marker in new:
            a=new.index(marker);b=new.index(r'\endgroup',a)
            new=new[:a]+r'''\subsection*{The construction and its limits}
The breakwise phase product uses its moving symplectic spaces. The type-side
pairing fixes a prime-field character, and the tame comparison retains the
rank-one conductor and trivial-character Gauss-sum boundaries. Interaction
carriers are distinguished from minimal character orbits.

The detailed construction appendices give ordinary proofs under their stated
type-theory hypotheses. The selected Henniart--Lemaire induction inputs
\cite{HenniartLemaire2011} retain their characteristic, rank and normalization
conditions. They do not establish H5 or corrected-character occurrence.
The formal companion identifies the actual compiler and axiom coverage.

'''+new[b:]
        if new!=t:edit(rel,t,new)

    rel='XI/publication/source/traditional/Paper_XI_Traditional_Final.tex'
    edit(rel,
         "This reading edition separates the missing arithmetic realization from the\nconditional identification of one actual candidate. The endpoint formerly\nlisted as proof obligation 66 (historical Theorem 16.2, row 95 of the\nall-records register) is now \\cref{conj:arithmetic_realization}.\nThe finite theorem statements and proofs include the geometric-Frobenius\nconvention correction and the additional local corrections recorded in this\nedition's reading guide. The later\nrestricted constructions are developed in \\cref{sec:arithmetic_progress} and\nthe detailed construction appendices. Their evidence is ordinary proof with\nretained internal reviews, rather than new Lean certificates. These reviews\nare not external peer review.",
         'Arithmetic realization and identification of an actual candidate are\nseparate problems. The realization endpoint is\n\\cref{conj:arithmetic_realization}. The restricted constructions are developed\nin \\cref{sec:arithmetic_progress} and the detailed construction appendices.\nThey have ordinary mathematical proofs with retained internal reviews.\nTheir formal coverage is stated separately in the formal companion.')
    edit(rel,'The accompanying release includes Markdown (\\texttt{.md}) files containing\ndetailed proofs, construction notes, proof audits, and research records.',
         'The accompanying sources include detailed proofs, construction notes,\nproof reviews and research records.')

    rel='XII/publication/source/traditional/Paper_XII_Traditional_Final.tex'
    edit(rel, r'\section*{Publication and supporting files}',r'\section*{The realization boundary}')
    edit(rel,
         'This reading edition, dated 10 October 2026, retains the complete revised mathematical proofs. Fourteen inherited vector figures are unchanged. Four diagrams have been redrawn to separate their arrows, expose the supplied inputs, and synchronize the final architecture with the five gates of Theorem~\\ref{thm:five_gate_completion}. Supporting Markdown (\\texttt{.md}) files are included with the source: the publication note, formal-evidence boundary, original-to-revised claim crosswalk, current status, source-preservation ledger, and build instructions. They record the statement hypotheses, evidence scope, and editorial changes alongside the preserved original and revised source snapshots.',
         'Theorem~\\ref{thm:five_gate_completion} brings the five realization requirements into one statement. The diagrams throughout the chapter distinguish supplied arithmetic data from algebraic deductions. The formal companion gives the claim-by-claim source map and the scope of the recorded verification.')
    edit(rel,'The saved release reports complete mapped formal evidence for all forty-nine revised internal claims, while the original-wording census is forty-one complete, seven partial, and one unchecked. These are different contracts.',
         'Formal evidence is mapped to all forty-nine revised internal claims. The original formulations have a separate record: forty-one complete, seven partial and one unchecked. The stronger original formulations and the revised statements are different contracts.')
    for role in ('traditional','lean_guide'):
        rel=f'XII/publication/source/{role}/reading_route.tex'
        p=G/rel;t=p.read_text();new=t.replace('This release preserves those historical statuses rather than promoting amended statements into proofs of their stronger predecessors.',
            'Amended statements are distinguished from their stronger predecessors.')
        new=new.replace('No fresh Lean compilation is claimed here. Current checks concern source preservation, inherited evidence authenticity, bounded computations, references, and publication quality.',
            'The formal companion identifies the recorded Lean compilation and the separate source, computation and correspondence checks.')
        if new!=t:edit(rel,t,new)

    # Resolve visible plate identifiers without changing hyperlink destinations.
    platefiles=[
      ('X','X/manuscript/Paper_X_Block27_Amended.tex'),
      ('X','X/visual_appendix/appendix.tex'),
      ('X','X/visual_appendix/source/pages.tex'),
      ('XI','XI/publication/source/traditional/reader_route.tex'),
      ('XI','XI/publication/source/visual_guide/reader_route.tex'),
      ('XI','XI/publication/source/lean_guide/reader_route.tex'),
      ('XII','XII/publication/source/traditional/reading_route.tex'),
      ('XII','XII/publication/source/lean_guide/reading_route.tex'),
    ]
    for k,rel in platefiles:
        p=G/rel;t=p.read_text();new=t
        new=re.sub(r'(?<![A-Za-z0-9_])V0*(\d+)--V0*(\d+)(?![A-Za-z0-9_])',lambda m:f'Plates {k}.{int(m[1])}--{k}.{int(m[2])}',new)
        new=re.sub(r'(?<![A-Za-z0-9_])V0*(\d+)(?![A-Za-z0-9_])',lambda m:f'Plate {k}.{int(m[1])}',new)
        new=new.replace('Atlas pages Plates','Plates').replace('atlas plate Plate','atlas Plate').replace('atlas Plates','Plates').replace('atlas Plate','Plate')
        if new!=t:edit(rel,t,new)

    for k,rel in [('X','X/visual_appendix/appendix.tex'),('XII','XII/publication/source/visual_guide/Paper_XII_Visual_Guide_Final.tex')]:
        p=G/rel;t=p.read_text();new=t
        new=new.replace('{V#1. #2}',f'{{Plate {k}.#1. #2}}')
        new=new.replace(r'\bfseries V#1\quad',f'\\bfseries Plate {k}.#1\\quad')
        new=new.replace(r'{V#1}}',f'{{Plate~{k}.#1}}')
        new=new.replace(r'{V\,--\,#1}}',f'{{Plate~{k}.#1}}')
        new=new.replace(r'V\,--\,\thepage',f'Plate~{k}.\\thepage')
        if k=='X':
            new=new.replace("Reader's edition\\quad\\textbullet\\quad Block 27 + scalar/Mellin continuation",'Residual seeds and finite occupancy')
        else:
            new=new.replace('6 October 2026\\quad\\textbullet\\quad Formal source: v0.17.0 / evidence v0.17.1','Support, packets and conditional realization')
        if new!=t:edit(rel,t,new)

    edit('XII/publication/source/visual_guide/source/pages.tex',
         '{\\sffamily\\small Komorebi P.\\quad\\textbullet\\quad 10 October 2026}\\par',
         '{\\sffamily\\small Komorebi P.}\\par')
    edit('XII/publication/source/visual_guide/source/pages.tex',
         'These are explanations of the formal release, not additional assumptions or new Lean certificates.',
         'These examples explain the mathematical constructions. They add no assumptions or Lean certificates.')
    # Store the precise source-edit record, including complete changed hunks.
    (ROOT/'editorial/book_revision/ix_xii_substitutions.json').write_text(json.dumps(LOG,indent=2)+'\n')
    diffs=[]
    for row in inventory:
        p=ROOT/row['path'];old=(G/'book_edit_before'/p.relative_to(G)).read_text();new=p.read_text()
        if old!=new:
            diffs.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+row['path'],tofile=row['path']))
    (ROOT/'editorial/book_revision/ix_xii_prose.patch').write_text(''.join(diffs))
    print(json.dumps({'substitutions':len(LOG),'changed_paths':len({r['path'] for r in LOG})}))

if __name__=='__main__':main()
