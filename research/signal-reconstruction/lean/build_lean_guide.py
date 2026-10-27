#!/usr/bin/env python3
"""Build guide prose, exact source anchors, and a conservative live SG map.

Uses Pandoc for typesetting conversion; never invokes Lean or Lake.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / 'related_formal/paper_v/formalization/lean/KomorebiPaperV'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Ranges are literal source slices; context and interpretation are separate fields.
ANCHORS = [
 ('packet','Packets',17,23,['KomorebiPaperV.packet','KomorebiPaperV.packet_idempotent'],
  'I, R and V are arbitrary types; decidable equality on R and zero in V.',
  'Coordinate restriction and its exact pointwise idempotence.'),
 ('packet_complete','Packets',36,45,['KomorebiPaperV.packet_complete'],
  'R is finite with decidable equality; V is an additive commutative monoid.',
  'A finite partition sum restores each supplied coordinate.'),
 ('address_roundtrip','Packets',74,83,['KomorebiPaperV.address_synthesize_analyze','KomorebiPaperV.address_analyze_synthesize'],
  'I, R, Q and V are arbitrary types; e is a supplied equivalence I ≃ R × Q.',
  'Inverse address maps give exact round trips on arbitrary functions.'),
 ('integer_equiv','IntegerPolyphase',57,64,['KomorebiPaperV.IntegerPolyphase.addressEquiv'],
  'N is natural and strictly positive; addresses and quotient coordinates are signed integers.',
  'Euclidean division supplies a literal integer address equivalence.'),
 ('sample_delay','IntegerPolyphase',94,104,['KomorebiPaperV.IntegerPolyphase.sample_delay'],
  'N > 0; d is any signed integer; x is any coefficient function.',
  'A general original-sample delay changes phase and adds a signed quotient carry.'),
 ('hilbert_signal','HilbertPackets',16,24,['KomorebiPaperV.HilbertPackets.Signal','KomorebiPaperV.HilbertPackets.projection'],
  'Complex square-summable sequences; arbitrary address type; decidable phase labels.',
  'The packet restriction remains in the actual ℓ2 sequence space.'),
 ('hilbert_polyphase','HilbertPackets',116,133,['KomorebiPaperV.HilbertPackets.polyphase','KomorebiPaperV.HilbertPackets.polyphase_energy'],
  'N > 0 and the input is complex ℓ2; the output uses joint ℓ2 on Fin N × ℤ.',
  'Polyphase reindexing is a linear isometric equivalence and preserves total energy.'),
 ('impulse_expansion','HilbertPackets',135,137,['KomorebiPaperV.HilbertPackets.impulse_expansion'],
  'x is a complex square-summable sequence on ℤ.',
  'The vector series of coordinate impulses converges to x in ℓ2 norm.'),
 ('fir_definitions','FIRTransfer',53,57,['KomorebiPaperV.FIRTransfer.fir','KomorebiPaperV.FIRTransfer.kernel'],
  'K is a semiring; h is finitely supported; x is any bilateral sequence.',
  'Finite convolution and the exact signed channel kernel are defined.'),
 ('fir_transfer','FIRTransfer',96,101,['KomorebiPaperV.FIRTransfer.fir_polyphase_transfer'],
  'K is a semiring; N > 0; h is finitely supported; x is an arbitrary ℤ-indexed function.',
  'Finite-support convolution is represented by exact finite channel sums.'),
 ('filter_pr','FilterBank',133,136,['KomorebiPaperV.FilterBank.perfect_reconstruction_iff'],
  'I is finite with decidable equality; E and R have finite complex Laurent entries; c and d are arbitrary.',
  'Reconstruction of every channel sequence is equivalent to the gain-delay Laurent matrix identity.'),
 ('filter_sample_delay','FilterBank',155,161,['KomorebiPaperV.FilterBank.original_sample_delay'],
  'N > 0; the supplied Laurent matrix identity R*E = gainDelay c d holds.',
  'A delay d in channel samples becomes the original-sample delay N*d.'),
 ('known_edge','KnownEdge',17,19,['KomorebiPaperV.known_edge_error'],
  'E is an additive commutative group; Q : E → E is arbitrary; the same supplied j is retained.',
  'Exact supplied-edge cancellation is purely additive and does not estimate j.'),
 ('estimated_edge','KnownEdge',43,46,['KomorebiPaperV.estimated_edge_norm_bound'],
  'E is a seminormed additive commutative group; all four elements are supplied.',
  'The total supplied reconstruction error is bounded by background and edge errors.'),
 ('mask_finite','MaskPerturbation',43,47,['KomorebiPaperV.MaskPerturbation.finite_p_perturbation'],
  'Ω is measurable; S,T measurable; μ arbitrary; p : ENNReal with 1 ≤ p and p ≠ ∞; a,b complex.',
  'Extended finite-exponent mask error separates amplitude error from changed support.'),
 ('mask_infinity','MaskPerturbation',73,77,['KomorebiPaperV.MaskPerturbation.infinity_perturbation'],
  'Ω is measurable; μ arbitrary; S,T arbitrary sets; a,b complex; actual S∆T=∅ condition.',
  'A pointwise support bound yields an essential-supremum bound; the condition is actual set equality.'),
 ('pruning_synthesis','PruningSums',88,97,['KomorebiPaperV.PruningSums.packet_projector_synthesis'],
  'H is a complex normed space; a finite tree, conservation law, identity root and complete pruning are supplied.',
  'A complete covering antichain of conserving operator labels synthesizes identity.'),
 ('pruning_solver','PruningAlgorithm',13,30,['KomorebiPaperV.PruningAlgorithm.Result','KomorebiPaperV.PruningAlgorithm.solve'],
  'A finite adaptive tree; arbitrary real node costs; noncomputable real comparison and cached child model.',
  'Bottom-up additive-cost selection records a cut, cost and explicit abstract operation counts.'),
 ('pruning_work','PruningAlgorithm',89,95,['KomorebiPaperV.PruningAlgorithm.solve_linear_work'],
  'Finite tree and supplied node costs; unit-cost visits/comparisons/additions as defined in solve.',
  'The recorded abstract operation count is at most three times the number of tree nodes.'),
]


P = 'KomorebiPaperV.'
RELATIONS = {
 1: ([P+'packet_complete',P+'HilbertPackets.projector_complete'],
     'The archived source proves coordinate and ℓ2 projector specializations; the SG result is for arbitrary complete algebraic projectors.'),
 2: ([P+'FilterBank.bank_mul'],
     'Composition is proved for finite Laurent filter-bank operators; arbitrary packet transfer paths remain a prose theorem.'),
 3: ([P+'packet_refinement',P+'HilbertPackets.projector_refinement'],
     'The source proves supplied coordinate refinement and its bounded ℓ2 specialization, not every abstract packet operator refinement.'),
 4: ([P+'HilbertPackets.reindexIsometry'],
     'A bijective coordinate reindexing is a particular isometric transform; the arbitrary invertible-transform conjugation theorem is not a recovered target.'),
 5: ([P+'IntegerPolyphase.synthesis_analysis',P+'IntegerPolyphase.analysis_synthesis',P+'FIRTransfer.fir_polyphase_transfer'],
     'Exact integer round trips and finite-support convolution are formalized. The SG claim allows ℓ1 infinite-support kernels and needs its absolute-convergence argument.'),
 9: ([P+'known_edge_error'],
     'The formal supplied-edge cancellation is related; Fourier out-of-band identification of an unknown scalar coefficient is additional.'),
 10: ([P+'known_edge_error',P+'known_edge_norm'],
      'Supplied-edge error cancellation is formal. The Fourier-defined block, its projector identities and exactness on the model class are separate prose obligations.'),
 11: ([P+'known_edge_error',P+'known_edge_norm'],
      'The cancellation part is formal; analytic Fourier decay, tail summation and the concrete signal-norm instantiation are not targets here.'),
 16: ([P+'positive_gap',P+'gap_stability'],
      'Finite objective gap and stability are formal under a strict optimum and uniform objective errors; profiled dictionary identification and its particular score are additional.'),
 17: ([P+'MaskPerturbation.symmetric_difference_norm',P+'MaskPerturbation.finite_p_perturbation'],
      'The source provides extended measurable-mask identities and bounds; the SG mixed-amplitude finite-vector identity is a distinct specialization/derivation.'),
 32: ([P+'gap_stability'],
      'The finite strict-margin selection principle is formal; circular Nth-root geometry, associated-root error and the particular metric gate remain additional.'),
 36: ([P+'estimated_edge_error',P+'estimated_edge_norm_bound'],
      'The additive error split is formal; the A_M linearity rewrite and its operator-norm amplification are not this source type.'),
 37: ([P+'MaskPerturbation.finite_p_perturbation'],
      'Measurable-mask error infrastructure is related, but the corrected mean-zero periodic sawtooth calculation and sharp factor two are not formalized here.'),
 38: ([P+'estimated_edge_norm_bound',P+'MaskPerturbation.full_signal_perturbation'],
      'Supplied-error combination is related; calibrated parameter rates, canonical jump L1 control and Fourier operator-norm growth remain prose obligations.'),
 42: ([P+'HilbertPackets.impulse_dense_span',P+'HilbertPackets.projector_orthogonal'],
      'The source proves density and orthogonality for particular ℓ2 coordinate packets; arbitrary nested finite-span projector convergence is not a recovered target.'),
 46: ([P+'HilbertPackets.shift_generated_dense_span',P+'HilbertPackets.projector_complete'],
      'An explicit dense core and bounded finite projector identity are formal examples; the general bounded-operator extension theorem is not a recovered target.'),
}


OBLIGATIONS = {
 6: 'Unit-circle power observations, finite alias group, and Bézout/gcd identification.',
 7: 'Measurement-fiber identifiability and direct-sum uniqueness in the declared model.',
 8: 'Matched circular location metric and the fixed-order narrow-pulse counterexample.',
 12:'Dirichlet-kernel scaled limit, sine-integral profile, and the local Gibbs overshoot.',
 13:'Fejér-kernel positivity, integral normalization, and range preservation almost everywhere.',
 14:'Projected sparse null-secant injectivity and the capped spark convention.',
 15:'Restricted column separation, nuisance projection contraction, and sparse support bounds.',
 18:'Continuous distributional derivative and Fourier normalization to exponential moments.',
 19:'Hankel/Vandermonde factorization, rank, and zero-order interpretation.',
 20:'Prony annihilator uniqueness, polynomial roots, and matched location recovery.',
 21:'Canonical mean-zero periodic primitive and its representative.',
 22:'Finite exact data budget, unknown/zero order branch, and synthesis modulo representative.',
 23:'Fourier-noise scaling and the rectangular Hankel Frobenius/spectral bound.',
 24:'Perturbed inverse/Neumann gate and annihilator coefficient error.',
 25:'Strict Rouché disk gate, one root per disk, and conditional true-root matching.',
 26:'Perturbed full-column-rank least squares and amplitude stability.',
 27:'Defective moment model and shared aliased exponential nodes across offsets.',
 28:'Complex singular-value perturbation and a supplied threshold, including full rank.',
 29:'Adjacent offset products with R≥1 and nonzero amplitude.',
 30:'Offset phase denominator and explicit defect-to-phase bound.',
 31:'Normalized residual zero exactly characterizes a finite progression.',
 33:'Associated root branch and divided angular perturbation.',
 34:'Explicit exact calibration data budget and distinct active alias nodes.',
 35:'Uniform inverse bounds, coefficient lower bounds, strict branch margin, and conditional rates.',
 39:'Stacked full-column-rank recurrence, common annihilator, and channelwise Vandermonde recovery.',
 40:'Confluent shift annihilation, polynomial degree, and nonvanishing leading offset coefficients.',
 41:'Restricted sparse injectivity with projected model mismatch and edge approximation error.',
 43:'Positive ridge normal equations, uniqueness, and modified residual stationarity.',
 44:'Scalar clipping nonexpansiveness, box truth assumption, and Euclidean assembly.',
 45:'Exact full residual identity and ideal finite pixel spanning; no compression inference.',
}


def write_csv(name, rows, keys):
    with (HERE/name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in keys})


def build_concordance(declarations):
    path = ROOT/'traditional/Claim_Concordance.json'
    if not path.is_file():
        return 'The current traditional claim catalogue is still being assembled; no per-SG certification is inferred.', None
    data = json.loads(path.read_text())
    claims = data if isinstance(data,list) else data['claims']
    by_name = {row['name']:row for row in declarations}
    records = []
    table = ['| Claim | Archived relation | Remaining obligation |','|---|---|---|']
    for claim in claims:
        cid = claim['claim_id']
        number = int(cid.split('-')[1])
        names, explanation = RELATIONS.get(number, ([],OBLIGATIONS.get(number,'No matching dedicated target was identified in this preserved corpus.')))
        related = []
        for name in names:
            item = by_name[name]
            path2 = ROOT/item['file']
            lines = path2.read_text().splitlines()
            # Literal source header through the first proof delimiter, preserving Lean syntax.
            start = item['line']-1
            end = start
            while end < len(lines)-1 and ':=' not in lines[end]: end += 1
            quoted = '\n'.join(lines[start:end+1])
            related.append(dict(declaration=name,file=item['file'],line=item['line'],
                                source_sha256=item['source_sha256'],source_quoted=quoted,
                                coverage_relation='related_infrastructure_only'))
        classification = 'related_infrastructure' if related else 'no_recovered_target'
        row = dict(claim_id=cid,title=claim['title'],statement_tex=claim['statement_tex'],
                   hypotheses=claim['hypotheses'],hypotheses_tex=claim['hypotheses_tex'],domain=claim['domain'],
                   coverage_classification=classification,related_declarations=related,
                   interpretation=explanation,full_current_claim_covered=False,
                   fresh_signal_lean_certificate=False,traditional_claim_input_sha256=sha(path))
        records.append(row)
        label = 'Related infrastructure' if related else 'No recovered target'
        table.append(f"| {cid}: {claim['title']} | {label} | {explanation} |")
    summary = dict(schema='komorebi.signal.claim-lean-concordance.v1',author='Komorebi P.',edition='2026-10-06',
                   traditional_claim_input='traditional/Claim_Concordance.json',traditional_claim_input_sha256=sha(path),
                   evidence_scope='Inspected Paper V v1.1.0 source; inherited checks plus current static correspondence only',
                   claims=records)
    (HERE/'Claim_Lean_Concordance.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    csvrows = [dict(row,related_declarations='; '.join(a['declaration'] for a in row['related_declarations'])) for row in records]
    write_csv('Claim_Lean_Concordance.csv',csvrows,['claim_id','title','domain','hypotheses','statement_tex',
              'coverage_classification','related_declarations','interpretation','full_current_claim_covered',
              'fresh_signal_lean_certificate','traditional_claim_input_sha256'])
    audit = dict(status='PASS_STATIC_LIVE_CLAIM_MAPPING',claim_count=len(records),
                 input_file='traditional/Claim_Concordance.json',input_sha256=sha(path),
                 field_parity_checked=['claim_id','title','statement_tex','hypotheses','hypotheses_tex','domain'],
                 every_claim_present=True,all_source_hashes_match=True,
                 full_signal_claims_formally_covered=0,classification_counts=dict(Counter(r['coverage_classification'] for r in records)),
                 fresh_lean_execution=False,scope='Exact live-field copies and saved source anchors; human relation assessment, not a new kernel check')
    assert [r['claim_id'] for r in records] == [r['claim_id'] for r in claims]
    for old,new in zip(claims,records):
        assert all(old[k]==new[k] for k in audit['field_parity_checked'])
        for anchor in new['related_declarations']:
            assert sha(ROOT/anchor['file']) == anchor['source_sha256']
    (HERE/'CLAIM_MAPPING_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    return '\n'.join(table), audit


HEADER = r'''\documentclass[11pt]{article}
\usepackage[letterpaper,margin=.85in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype,amsmath,amssymb,amsthm}
\usepackage{booktabs,longtable,array,enumitem,xcolor,seqsplit,calc}
\usepackage{listings,tcolorbox,fancyhdr,titlesec,hyperref,needspace}
\definecolor{Navy}{HTML}{17324D}
\definecolor{Teal}{HTML}{2F7A78}
\definecolor{Pale}{HTML}{E7F0F6}
\hypersetup{colorlinks=true,linkcolor=Navy,urlcolor=Teal,pdfauthor={Komorebi P.},pdftitle={Signal Reconstruction: Lean Guide and Formalization Concordance}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small Signal Reconstruction: Lean Guide}\fancyhead[R]{\small Komorebi P.}\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{Navy}}{\thesection}{.7em}{}
\titleformat{\subsection}{\large\bfseries\color{Navy}}{\thesubsection}{.6em}{}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlist{itemsep=3pt,topsep=4pt}
\lstset{basicstyle=\footnotesize\ttfamily,breaklines=true,columns=fullflexible,backgroundcolor=\color{Pale},frame=single,framerule=0pt,xleftmargin=6pt,xrightmargin=6pt,language={},keepspaces=true,showstringspaces=false,
literate={ℤ}{{$\mathbb Z$}}1 {ℕ}{{$\mathbb N$}}1 {ℂ}{{$\mathbb C$}}1 {ℝ}{{$\mathbb R$}}1 {Ω}{{$\Omega$}}1 {μ}{{$\mu$}}1 {γ}{{$\gamma$}}1 {ε}{{$\epsilon$}}1 {η}{{$\eta$}}1 {τ}{{$\tau$}}1 {δ}{{$\delta$}}1 {α}{{$\alpha$}}1 {β}{{$\beta$}}1 {ρ}{{$\rho$}}1 {φ}{{$\phi$}}1 {ω}{{$\omega$}}1
{→}{{$\to$}}1 {←}{{$\leftarrow$}}1 {↔}{{$\leftrightarrow$}}1 {≃}{{$\simeq$}}1 {∀}{{$\forall$}}1 {∃}{{$\exists$}}1 {∈}{{$\in$}}1 {∉}{{$\notin$}}1 {≤}{{$\le$}}1 {≥}{{$\ge$}}1 {≠}{{$\ne$}}1 {∑}{{$\sum$}}1 {∞}{{$\infty$}}1 {∅}{{$\varnothing$}}1 {∆}{{$\triangle$}}1 {∧}{{$\land$}}1 {∨}{{$\lor$}}1 {⟨}{{$\langle$}}1 {⟩}{{$\rangle$}}1 {‖}{{$\Vert$}}1 {₀}{{$_0$}}1 {ₑ}{{$_e$}}1 {ₗ}{{$_l$}}1 {ᵢ}{{$_i$}}1 {×}{{$\times$}}1 {∘}{{$\circ$}}1 {ℓ}{{$\ell$}}1 {⊤}{{$\top$}}1 {·}{{$\cdot$}}1 {⊢}{{$\vdash$}}1 {⇑}{{$\Uparrow$}}1}
\newtcolorbox{scopebox}{colback=Pale,colframe=Navy,boxrule=.5pt,arc=0pt}
\newcommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\newcommand{\passthrough}[1]{#1}
\allowdisplaybreaks
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}
\vspace*{1.0in}
{\large\color{Teal}\textsc{Operation Komorebi}}\par\vspace{.35in}
{\Huge\bfseries\color{Navy}Signal Reconstruction}\par\vspace{.2in}
{\LARGE Lean Guide and\par Formalization Concordance}\par\vspace{.45in}
{\large Komorebi P.}\par\vspace{.18in}
{\large Final Edition\quad October 6, 2026}\par\vspace{.6in}
\begin{scopebox}
Exact source contracts for packets, transfer blocks, supplied edges,
measurable masks, and finite pruning.\par
Unknown-edge estimation and self-calibration obligations are explicitly mapped.
\end{scopebox}
\vfill
Related Paper V v1.1.0 checkpoint: 23 production modules, 225 theorem targets.\par
Inherited formal evidence; no fresh Signal Lean build.\par
Full Markdown, preserved source, concordance, and review records included.
\end{titlepage}
\hypersetup{pageanchor=true}
\setcounter{tocdepth}{1}
\begingroup\small\setlength{\parskip}{0pt}\tableofcontents\endgroup\clearpage
'''


def main():
    declarations = json.loads((HERE/'Related_Declaration_Inventory.json').read_text())
    known_names = {row['name'] for row in declarations}
    content = (HERE/'guide_content.md').read_text()
    anchor_rows = []
    for key,module,start,end,names,context,interpretation in ANCHORS:
        path = SOURCE/(module+'.lean')
        lines = path.read_text().splitlines()
        quoted = '\n'.join(lines[start-1:end])
        assert set(names) <= known_names, names
        for name in names:
            assert name.split('.')[-1] in quoted, (key,name)
        anchor = dict(anchor_id=key,file=path.relative_to(ROOT).as_posix(),start_line=start,end_line=end,
                      source_sha256=sha(path),qualified_declarations=names,source_quoted=quoted,
                      context_hypotheses=context,interpretation=interpretation,
                      evidence='Literal preserved source excerpt; inherited related proof evidence; no current elaboration')
        anchor_rows.append(anchor)
        display = f"**Source excerpt:** `{module}.lean`, lines {start}–{end}. Context: {context}\n\n```text\n{quoted}\n```"
        content = content.replace('{{anchor:'+key+'}}',display)
    concordance,audit = build_concordance(declarations)
    content = content.replace('{{concordance}}',concordance)
    modules = json.loads((HERE/'Related_Module_Inventory.json').read_text())
    table = ['| Module | Theorems | Other explicit declarations | Principal role |','|---|---:|---:|---|']
    roles = {
      'BinaryAdaptive':'Binary cuts and additive cost recurrence','CRT':'Coprime residue arithmetic',
      'CompletePrunings':'Complete covering antichains and cut equivalence','CyclicSeries':'Convergent cyclic coefficient series',
      'FIRTransfer':'Finite-support signed polyphase kernels','FilterBank':'Finite Laurent bank action and reconstruction',
      'FiniteAdaptive':'Finite arbitrary-arity packet trees and cuts','FiniteSelection':'Finite objective minimum and gap stability',
      'FiniteTransforms':'Finite signal coordinates, Haar/lifting and matrix action','HaarChannels':'Literal normalized ℓ2 low/detail channels',
      'HaarHilbert':'Haar isometry and energy','HilbertPackets':'Bounded ℓ2 projectors, impulses and polyphase isometry',
      'IntegerPolyphase':'Signed Euclidean addresses, inverse laws and delays','KnownEdge':'Supplied-edge cancellation and error splitting',
      'Lifting':'Predict/update inverse and determinant identities','MaskPerturbation':'Extended measurable-mask error bounds',
      'Packets':'Pointwise coordinate packets and address round trips','PruningAlgorithm':'Cached bottom-up evaluator and work model',
      'PruningSums':'Literal antichain sums, synthesis and objectives','SmithAction':'Finite matrix basis change for Smith form',
      'SmithCyclic':'Smith-compatible cyclic coefficient action','WaveletPackets':'Finite-depth Haar packet operators and reconstruction',
      'ZTransform':'Convergent bilateral transforms and FIR channel formulae'}
    for row in modules:
        table.append(f"| `{row['module']}` | {row['theorem_lemma_count']} | {row['explicit_declaration_count']-row['theorem_lemma_count']} | {roles[row['module']]} |")
    content = content.replace('{{modules}}','\n'.join(table))
    assert '{{' not in content, 'Unfilled guide placeholder'
    md = HERE/'Signal_Reconstruction_Lean_Guide.md'
    md.write_text('# Signal Reconstruction: Lean Guide and Formalization Concordance\n\nKomorebi P. · Final Edition · October 6, 2026\n\n'+content)
    (HERE/'SOURCE_ANCHORS.json').write_text(json.dumps(dict(schema='komorebi.signal.source-anchors.v1',
          author='Komorebi P.',source_version='Paper V v1.1.0 checkpoint',anchors=anchor_rows),indent=2,ensure_ascii=False)+'\n')
    body = subprocess.run(['pandoc','--from=markdown+tex_math_dollars','--to=latex','--listings','--wrap=none'],
                          input=content,text=True,capture_output=True,check=True).stdout
    # Keep Unicode Lean tokens in listings; allow long ASCII paths to wrap in prose.
    def inline_text(match):
        # Pandoc escapes underscores/braces inside its lstinline output.
        # Restore the literal inline content before converting it to texttt.
        value = re.sub(r'\\([_{}#$%&])',r'\1',match[2])
        glyphs = {'ℤ':r'\mathbb Z','ℕ':r'\mathbb N','ℂ':r'\mathbb C','ℝ':r'\mathbb R',
                  'Ω':r'\Omega','μ':r'\mu','→':r'\to','≃':r'\simeq','₀':r'_0','ₗ':r'_l',
                  'ᵢ':r'_i','∀':r'\forall','∧':r'\land','×':r'\times','∆':r'\triangle',
                  '∅':r'\varnothing','≥':r'\ge','≤':r'\le','ℓ':r'\ell'}
        escaped = ''.join((r'\ensuremath{'+glyphs[char]+'}') if char in glyphs else
                         {'_':r'\_','#':r'\#','%':r'\%','&':r'\&','{':r'\{','}':r'\}',
                           '$':r'\$','~':r'\textasciitilde{}','^':r'\textasciicircum{}',
                           '\\':r'\textbackslash{}'}.get(char,char) for char in value)
        return r'\texttt{\seqsplit{'+escaped+'}}' if len(value)>=24 and value.isascii() else r'\texttt{'+escaped+'}'
    body = re.sub(r'\\passthrough\{\\lstinline(.)(.*?)\1\}',inline_text,body)
    body = body.replace('ℓ2',r'$\ell^2$').replace('R≥1',r'$R\ge1$')
    prose_glyphs = {'ℤ':r'\mathbb Z','ℕ':r'\mathbb N','ℂ':r'\mathbb C','ℝ':r'\mathbb R',
                    'Ω':r'\Omega','μ':r'\mu','→':r'\to','≃':r'\simeq','×':r'\times',
                    '∅':r'\varnothing','∆':r'\triangle','∞':r'\infty','≠':r'\ne',
                    '≤':r'\le','≥':r'\ge','ℓ':r'\ell'}
    segments = re.split(r'(\\begin\{lstlisting\}.*?\\end\{lstlisting\})',body,flags=re.S)
    for i in range(0,len(segments),2):
        segments[i] = ''.join(r'\ensuremath{'+prose_glyphs[c]+'}' if c in prose_glyphs else c for c in segments[i])
    body = ''.join(segments)
    body = body.replace(r'\textbf{Source excerpt:}',r'\Needspace{8\baselineskip}\textbf{Source excerpt:}')
    body = body.replace(r'\begin{lstlisting}',r'\begin{minipage}{\linewidth}'+'\n'+r'\begin{lstlisting}')
    body = body.replace(r'\end{lstlisting}',r'\end{lstlisting}'+'\n'+r'\end{minipage}\par')
    (HERE/'Signal_Reconstruction_Lean_Guide.tex').write_text(HEADER+body+'\n\\end{document}\n')
    result = dict(status='GUIDE_SOURCES_GENERATED',source_anchor_count=len(anchor_rows),
                  source_anchor_hashes_match=True,claim_mapping_audit=audit,
                  fresh_lean_execution=False,markdown_sha256=sha(md),
                  tex_sha256=sha(HERE/'Signal_Reconstruction_Lean_Guide.tex'))
    (HERE/'GUIDE_GENERATION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','source_anchor_count','fresh_lean_execution')}))


if __name__=='__main__':
    main()
