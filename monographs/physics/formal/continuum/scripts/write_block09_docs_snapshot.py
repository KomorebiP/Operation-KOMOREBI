from pathlib import Path
import json, collections, shutil, hashlib
r=Path(__file__).resolve().parents[1]
inv=json.loads((r/'declaration_inventory.json').read_text())
new=[e for e in inv['declarations'] if e['origin']=='new_full_edition_block_09']
names={e['name'] for e in inv['declarations']}
counts=collections.defaultdict(collections.Counter)
for e in new:counts[e['module']][e['kind']]+=1
report=json.loads((r/'verification/final/report.json').read_text())
status=report['status']
release='Komorebi Physics Lean v0.9.0 — Block 09'
new_table='\n'.join(f"| {m.split('.')[-1]} | {c['theorem']} | {c['def']} | {c['structure']} |" for m,c in counts.items())
guide=r'''# Block 09 — Explicit domains, countable continuity and a genuine unbounded model

Source: *Projector-Refinement Physics: Complete Unified Theory*, 550 physical PDF pages, Chapter 6.1–6.4, physical pages 30–33 (printed 17–20). This block targets (6.1)–(6.9), the spectral realization of (6.10)–(6.11) and (6.13)–(6.14), and the continuity/Parseval consequences (6.27)–(6.41). Equation (6.26)'s unitary group is **not constructed**. The source page images were inspected. Files did not supply three previews; the unchanged included PDF was rendered locally for them. The overbar in (6.34) is retained.

The authoritative current result is `verification/final/report.json`. This guide describes conditional mathematics and constructed spectral examples, not observational confirmation of the later physics.

## 1. Scope and inventory

| Module | Theorems | Definitions | Structures |
|---|---:|---:|---:|
TABLE
| **Block 09** | **113** | **29** | **2** |

The cumulative inventory is **783 theorem declarations, 952 named declarations and 47 mathematical modules**. All 40 Block 08 mathematical files are byte-identical. Of the cumulative theorems, 39 are recovered Paper VII declarations and 744 are authored across nine full-edition blocks. These are declaration counts, including support lemmas and examples, not independent discoveries or a percentage of 550-page completion.

The generic spaces are complex inner-product spaces. The index type can be arbitrary; countable labels are a specialization. Sums are unconditional nets over finite subsets, not just one chosen enumeration. The constructed diagonal model uses the complete infinite-dimensional Hilbert space `ℓ²(ℕ, ℂ)`. The unbounded operator is never assigned a bounded-map type. Its individual projector maps are bounded.

## 2. An actual operator domain and graph norm

The generator has the type

```lean
T : H →ₗ.[ℂ] H
```

This is Mathlib's partially defined linear-map interface. It contains a complex-linear subspace `T.domain` and a linear map from that domain into H. Evaluation `T x` requires an actual domain element. No continuity or norm bound is assumed for this map.

`GraphDomain.graphMap` constructs the linear embedding

\[
x\longmapsto (x,Tx)\in H\oplus_2 H.
\]

Its actual `WithLp 2` product norm defines `graphNorm`. It is not the max/sup product norm. The formalization proves injectivity, definiteness, homogeneity and triangle inequality, and the literal identity

\[
\|x\|_T^2=\|x\|^2+\|Tx\|^2.
\]

For any filter and any domain-valued family x_a, it proves

\[
\|x_a-x\|_T\to0
\iff
x_a\to x\text{ in }H\quad\text{and}\quad Tx_a\to Tx\text{ in }H.
\]

It separately proves equivalence with the source's squared-error formulation. The ambient subtype norm is not silently relabeled as the graph norm.

`StrongAtlas` has only bounded projectors, idempotence, pairwise orthogonality, Hermiticity and strong reconstruction. It has no current, derivative or graph-convergence field. `DomainAtlas` adds only invariance of `T.domain` under each projector. Restricted projectors and their finite sums are then actually constructed on that domain.

`GraphCompatible` explicitly requires convergence of the graph-norm error of the finite sums. The two component limits and the vector `HasSum` of generator images are derived. Graph compatibility is not assumed by every domain atlas. A bounded operator is included as a consistency specialization, not used to represent all operators.

## 3. Actual derivatives and literal graph-compatible current limits

Define

\[
E_i(\psi)=\|P_i\psi\|^2,
\qquad J_{ij}(\psi)=2\operatorname{Im}\langle P_i\psi,TP_j\psi\rangle.
\]

Every application of T to a packet is justified by the domain-invariance field. Finite linearity is proved on that domain.

The analytic input is the original ambient state derivative, with the curve taking values in the true domain:

```lean
HasDerivAt (fun s => (psi s : H)) ((-Complex.I) • T (psi t)) t
```

No derivative of T, graph differentiability of psi, packet-energy derivative or continuity law is supplied as an input. Differentiating the bounded projection of the actual state gives

\[
E_i'(t)=2\operatorname{Im}\langle P_i\psi(t),T\psi(t)\rangle.
\]

The literal source route uses graph convergence to prove

\[
\sum_{j\in F}J_{ij}\longrightarrow
2\operatorname{Im}\langle P_i\psi,T\psi\rangle=E_i'(t).
\]

A quantified estimate is also checked:

\[
\left|\sum_{j\in F}J_{ij}-E_i'(t)\right|
\le2\|P_i\psi\|\,\|T S_F\psi-T\psi\|.
\]

The derivative and the limiting value are independently derived before they are identified.

## 4. Added strengthening: fixed rows need less than full graph convergence

For the current and conservation identities, formal symmetry on the domain is sufficient:

\[
\langle Tx,y\rangle=\langle x,Ty\rangle\quad(x,y\in D(T)).
\]

This is weaker than self-adjointness and is named `IsSymmetric`, not misleadingly called a complete self-adjoint operator. The constructed spectral model below satisfies actual equality with its adjoint.

For one fixed packet i, symmetry gives

\[
\langle P_i\psi,TP_j\psi\rangle
=\langle TP_i\psi,P_j\psi\rangle.
\]

The right side pairs the strongly convergent packet sum against the fixed vector TP_i psi. Therefore the scalar current row has an unconditional sum **without adding graph compatibility**:

\[
\sum_jJ_{ij}=2\operatorname{Im}\langle P_i\psi,T\psi\rangle.
\]

The stronger error bound is

\[
\boxed{\left|\sum_{j\in F}J_{ij}-E_i'(t)\right|
\le2\|TP_i\psi\|\,\|S_F\psi-\psi\|.}
\]

This is a strengthening relative to the source's stated graph-limit route, not a literature novelty claim. It does **not** prove convergence of TS_F psi in Hilbert norm or provide a bound uniform in i. Symmetry and packet-domain invariance remain essential inputs to this route.

`current_row_abs_summable` proves absolute summability of each real scalar row. This is derived from the unconditional real `HasSum`; it is not inferred from convergence of an arbitrary ordered series. No absolute summability of the entire double current array is asserted.

## 5. Boundary flux and global energy without illegal infinite interchanges

Symmetry and conjugate symmetry establish

\[
\langle P_j\psi,TP_i\psi\rangle
=\overline{\langle P_i\psi,TP_j\psi\rangle},
\qquad J_{ij}=-J_{ji}.
\]

For every finite receiving region B, the actual derivative is proved to equal

\[
\boxed{\frac{d}{dt}\sum_{i\in B}E_i(t)
=\lim_{F\uparrow I}\sum_{i\in B}\sum_{j\in F\setminus B}J_{ij}(t).}
\]

The proof first cancels the finite internal double sum. The identity is used eventually when F contains B. Only the finite receiving sum passes through the limit.

Strong completeness and finite Pythagoras yield the actual infinite Parseval statement

\[
\sum_i\|P_i\psi\|^2=\|\psi\|^2.
\]

For a supplied all-real-time domain-valued solution, differentiating the original state norm and using symmetry gives global norm constancy. Combined with Parseval this proves global packet-energy constancy. No infinite sum of derivatives or unrestricted double-current rearrangement is used.

This does not construct e^{-itT}, prove Stone's theorem locally, or establish existence/domain invariance/differentiability of a general unitary group. The source's (6.41) is covered as a conservation consequence along a supplied actual trajectory, not as proof of the construction in (6.26).

## 6. Constructed maximal spectral domain, including self-adjointness

For any real coefficient family lambda_i, define

\[
D(T_\lambda)=\{x\in\ell^2:\ (\lambda_i x_i)_i\in\ell^2\},
\qquad (T_\lambda x)_i=\lambda_i x_i.
\]

This is the maximal weighted domain, not only finitely supported vectors. The module constructs its subspace laws and partial linear operator. Coordinate projectors are actual bounded operators and are proved to preserve the domain. Finite coordinate approximations prove domain density.

The formalization proves formal symmetry, then tests the adjoint on the actual coordinate singletons to show

\[
(T_\lambda^*y)_i=\lambda_i y_i.
\]

Since T_lambda* y is an actual l2 vector, this coordinate formula forces y into the declared maximal domain. Together with the symmetric inclusion it gives

\[
\boxed{T_\lambda^*=T_\lambda.}
\]

Closedness follows from the imported adjoint theory. Self-adjointness, density, and graph compatibility are **proved properties of this construction**, not assumed fields.

The exact domain and graph norm formulas are

\[
x\in D(T_\lambda)\iff\sum_i\lambda_i^2|x_i|^2<\infty,
\qquad
\|x\|_{T_\lambda}^2=\sum_i(1+\lambda_i^2)|x_i|^2.
\]

Here `< infinity` is formalized by summability of the nonnegative real series. For natural-number labels, the literal tail is checked:

\[
\boxed{\|x-S_Mx\|_{T_\lambda}^2
=\sum_{n\ge M}(1+\lambda_n^2)|x_n|^2\longrightarrow0.}
\]

The code represents this tail as a tsum over n+M. The convergence is genuine, for every vector in the maximal domain, not eventual equality on a finite-support test set.

## 7. Genuine unboundedness and topology-sensitive exact tests

Set lambda_n=n+1/2. The resulting spectral harmonic model is self-adjoint and graph-compatible on l2(N,C). Norm-one coordinate vectors satisfy

\[
\|e_n\|=1,\qquad\|T e_n\|=n+\tfrac12.
\]

Lean proves that no finite real constant bounds \|Tx\| by C\|x\| over the domain, and that no bounded everywhere-defined operator agrees with T there.

For the actual domain sequence

\[
u_n=\frac{e_n}{n+1/2},
\]

it proves

\[
u_n\to0\text{ in Hilbert norm},\qquad
Tu_n=e_n,\qquad\|Tu_n\|=1,
\]

and rejects generator-image convergence to zero and graph convergence. The exact squared graph norm is

\[
\|u_n\|_T^2=(n+1/2)^{-2}+1.
\]

These are sequence-limit and universal unboundedness proofs, not numerical checks at finitely many n. The sequence u_n is **not** presented as the truncations of one fixed state or as a counterexample to the separately proved coordinate graph compatibility.

This is a spectral multiplier realization. Its unitary equivalence to the differential harmonic oscillator on L2(R), the form-domain D(T^{1/2}), and the full physical oscillator realization remain separate. The spectral coordinate currents are proved zero and are not advertised as nonzero transport.

## 8. Separate nonzero derivative consistency test

`DomainExamples` embeds the earlier two-sector rotation into the partial-map interface using the genuine bounded Hamiltonian H=iA. Its graph compatibility and symmetry are proved. The actual current values are -2 and +2. The original affine state curve satisfies the required ambient evolution derivative at zero, and the generic domain theorem yields packet derivative -2 and a current row with that nonzero sum.

The reverse amplitude without conjugation is proved false. This is a finite-dimensional local derivative witness, not the unboundedness example, not a global solution, and not a claim that all spectral currents are nonzero.

## 9. Verification and remaining boundaries

The cumulative verifier removes local compiled outputs, recompiles 47 mathematical modules and the aggregate with one worker and warnings as errors, and audits all 952 inventoried names, including structures and proof-bearing definitions. Six new invalid controls bring the cumulative control count to 65. Each must produce its own intended diagnostic in its mapped source range. An import failure, timeout or nonzero batch exit alone is insufficient.

All 40 prior mathematical modules are checked against `reference/block08_preservation.json`; all earlier preservation layers remain active. The v0.8.0 baseline was freshly reverified before extension. Lean is 4.34.0-rc2; Mathlib is pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine clean pinned dependency repositories are checked. Only propext, Classical.choice and Quot.sound are allowed axiom dependencies. Imported Lean/Mathlib caches are reused, not rebuilt wholesale. No admissions, custom axioms, native evaluation or disabled kernel checks occur in active mathematics.

The completed final report controls release status. The external fresh-extraction receipt reports the second complete run and hashes the unchanged ZIP. Development failures remain separate and are documented in `BLOCK_09_FAILURES.md`.

Not covered: construction of a general unitary group or solution, physical differential-oscillator identification, full form-domain hierarchy, Section 6.3's bounded functional surrogates and operator-norm limits, Section 6.5's infinite coarse-cell domain/rearrangement obligations, spectral residue/ladder routing, countable dilation, measurement instruments, zero-probability entropy extensions, continuum gravity, cosmology, or empirical adequacy. No finite-stage floating-point residual is relabeled as a universal theorem.

**Next target:** Chapter 6.3's actual bounded diagonal multipliers and topology-specific truncation, including resolvent, heat, unitary, bounded and Cayley tails. Keep heat-time and denominator assumptions explicit. Also retain the unclosed D(T^{1/2}) hierarchy of 6.2 and coarse-cell obligations of 6.5 in the ledger.
'''.replace('TABLE',new_table)
(r/'docs/BLOCK_09_PROOF_GUIDE.md').write_text(guide)
index=['# Block 09 declaration index','',f'{len(new)} new inventoried names: 113 theorem declarations, 29 definitions and two structures.','']
for module in counts:
 index += ['## '+module,'','| Name | Kind | Source line |','|---|---|---:|']
 index += [f"| `{e['name']}` | {e['kind']} | {e['line']} |" for e in new if e['module']==module]
 index.append('')
(r/'docs/BLOCK_09_DECLARATION_INDEX.md').write_text('\n'.join(index))
receipts=[(q,json.loads(q.read_text())) for q in sorted((r/'verification/development/block09').glob('*/receipt.json')) if q.parent.name != 'supplementary_signature_timeout']
failed=[(q,d) for q,d in receipts if d.get('returncode')!=0]
fm=['# Block 09 failures and repairs','',f'{len(receipts)} snapshotted development compilations: {len(receipts)-len(failed)} passed and {len(failed)} failed. These are development invocations, not theorem counts. Each receipt preserves actual command, source SHA-256, duration, return code and compiler log. A pass is not a cumulative audit.','',
'The failures included reserved-identifier parsing (`partial` and `λ`), dependent-domain/`lp` coercions, finite-sum and derivative API normalization, deprecated API and warnings-as-errors failures, and one import attempted before its dependency compiled. Four diagonal-domain attempts contained Lean’s deterministic 200000-heartbeat-limit diagnostics. Explicitly fixing the `ℓ²(I, ℂ)` type of the singleton avoided that elaboration bottleneck; no heartbeat or kernel-check bypass was added. Cascading errors from failed declarations are retained as failures, not mathematical counterexamples.','',
'The final API probe under `verification/development/block09/api_probe_final.lean` is discovery scratch with unknown-name probes, not active mathematics and not a passed module. Additional ad hoc #check probes were not counted as mathematical development snapshots.','',
'A supplementary 15-signature #check inspection exceeded its 30-second limit; its input and a TIMEOUT receipt are preserved under development/block09/supplementary_signature_timeout. Its stdout was not written before the subprocess exception, and no completed signature-inspection result is claimed. This was not an active mathematical-module compilation. A status-poll tool call also timed out while the separately launched cumulative verifier continued; the completed report was later read directly.','',
'Files could not provide source page images 30, 31 and 33. The included original PDF was rendered and inspected locally. Its bytes were not changed. The portable runtime restoration succeeded with the exact seven-part checksums; the restoration log is retained.','',
'The first cumulative mathematical audit passed, but a subsequent packaging review found that lakefile.toml still advertised version 0.8.0. It was corrected to 0.9.0. Because that file is a hashed proof input, the prior audit was retained as superseded and the in-progress first extraction recheck was deliberately stopped, not counted as PASS. The corrected cumulative audit and a new fresh-extraction audit are the production pair. See verification/block09_metadata_correction.json. No mathematical source changed for this repair.','',
'| Attempt | Module | First compiler diagnostic |','|---|---|---|']
for q,d in failed:
 text=(q.parent/'compile.log').read_text(); errors=[l.strip() for l in text.splitlines() if ': error' in l or 'TIMEOUT' in l]
 first=errors[0] if errors else 'See raw compiler log.'
 fm.append(f"| `{q.parent.name}` | {d['module'].split('.')[-1]} | {first.replace('|','/')} |")
fm += ['',f'Current cumulative report status when this file was generated: **{status}**. Its completed `verification/final/report.json` is authoritative. Intentionally invalid controls are a separate expected-failure contract and are not included in the {len(failed)} development failures.','']
(r/'docs/BLOCK_09_FAILURES.md').write_text('\n'.join(fm))
# Update the latest ledger, retaining every earlier mathematical boundary.
p=r/'docs/CLAIM_LEDGER.json';ledger=json.loads(p.read_text());ledger['release']=release
ledger['claims']=[c for c in ledger['claims'] if c['id']!='C6-GRAPH-COUNTABLE-NEXT' and not c['id'].startswith('C6-B09-')]
def claim(id,eq,ds,scope,status='CHECKED_BLOCK_09'):
 for d in ds:
  assert d in names,d
 return dict(id='C6-B09-'+id,master_equations=eq,status=status,declarations=ds,scope=scope)
D='KomorebiPhysics.'
ledger['claims'] += [
claim('DOMAIN-GRAPH','6.1–6.9',[D+'GraphDomain.graphMap',D+'GraphDomain.graphNorm_sq',D+'GraphDomain.graph_convergence_iff',D+'GraphDomain.squared_graph_convergence_iff',D+'DomainAtlas.graph_components'], 'Actual LinearPMap domain, L2 graph embedding and both component limits. Graph compatibility is an explicit atlas hypothesis, not a claim derived from strong reconstruction alone.'),
claim('STRONG-ATLAS','6.3–6.6',[D+'StrongAtlas',D+'DomainAtlas',D+'DomainAtlas.project',D+'DomainAtlas.partialSum',D+'DomainAtlas.GraphCompatible'], 'Generic projector/strong-resolution/domain-invariance inputs. Actual diagonal realization is separately constructed. No desired current or derivative law is a structure field.','ASSUMPTION_INTERFACE_WITH_CONSTRUCTIONS'),
claim('LITERAL-CURRENT','6.27–6.35',[D+'DomainAtlas.hasDerivAt_energy',D+'DomainAtlas.energy_derivative_graph_limit',D+'DomainAtlas.amplitude_reverse',D+'DomainAtlas.current_antisymm'], 'Actual ambient Schrödinger derivative on domain-valued trajectory; scalar finite-subset current limit follows via graph compatibility. Conjugation retained; no group existence.'),
claim('STRONG-ROW','Added stronger fixed-row theorem',[D+'DomainAtlas.amplitude_hasSum_strong',D+'DomainAtlas.current_hasSum',D+'DomainAtlas.current_row_abs_summable',D+'DomainAtlas.current_tail_strong_bound'], 'Symmetry moves T onto the fixed domain packet; strong completeness then yields scalar row limits and absolute summability per row without graph compatibility. No generator-image limit, whole double absolute sum, or uniform-in-label estimate is inferred.'),
claim('BOUNDARY-GLOBAL','6.36–6.41',[D+'DomainAtlas.region_derivative_boundary_limit',D+'StrongAtlas.energy_hasSum',D+'GraphDomain.packet_energy_constant'], 'Actual finite-region boundary derivative and infinite Parseval. Global packet constancy conditional on supplied all-time differentiable domain-valued solution; no derivative/tsum interchange.'),
claim('DIAGONAL','6.10–6.11, 6.13–6.14 and added self-adjointness',[D+'DiagonalDomain.operator',D+'DiagonalDomain.dense_domain',D+'DiagonalDomain.selfAdjoint',D+'DiagonalDomain.graph_compatible',D+'SpectralGraph.domain_iff',D+'SpectralGraph.graph_tail_series',D+'SpectralGraph.graph_range_tail_tendsto'], 'Real diagonal multiplier on its maximal weighted-l2 domain. Density, actual adjoint equality, closedness and graph compatibility proved. Spectral model only; physical differential-operator equivalence and square-root form domain remain open.'),
claim('UNBOUNDED-TEST','Added exact domain/topology tests',[D+'UnboundedExamples.harmonic_unbounded',D+'UnboundedExamples.no_bounded_extension',D+'UnboundedExamples.shrinking_strong',D+'UnboundedExamples.shrinking_action_not_zero',D+'UnboundedExamples.shrinking_not_graph'], 'Harmonic spectral multiplier lambda_n=n+1/2. Genuine universal unboundedness and limit counterexample. The shrinking sequence is not a fixed-state packet truncation.'),
claim('NONZERO-TEST','Added nonzero consistency test',[D+'DomainExamples.exact_current',D+'DomainExamples.actual_packet_derivative',D+'DomainExamples.current_hasSum_nonzero',D+'DomainExamples.reverse_without_conjugation_false'], 'Finite-dimensional partial-map witness with currents -2,+2 and actual local derivative -2. It is not claimed unbounded or a global solution.'),
claim('GROUP','6.26',[], 'The actual group exp(-itT), its domain invariance, existence and differentiability are not constructed. Conservation results consume the original derivative.','NOT_FORMALIZED_IN_THIS_RELEASE'),
claim('FORM-DOMAIN','6.12 and stated strict hierarchy',[], 'Square-root/form-domain construction and strict hierarchy, plus differential harmonic-oscillator identification, remain separate.','NOT_FORMALIZED_IN_THIS_RELEASE'),
claim('BOUNDED-SURROGATES','6.15–6.25',[], 'Next target: actual bounded multipliers, topology-specific strong versus norm truncations, heat-time restrictions and tail anchors.','NOT_FORMALIZED_IN_THIS_RELEASE'),
claim('COARSE-RESIDUE','6.42 onward',[], 'Infinite coarse-cell construction/domain preservation, controlled current rearrangement, residue packets and ladder operators remain separate.','NOT_FORMALIZED_IN_THIS_RELEASE')]
p.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
# Append a clearly authoritative new section to the historical source map.
p=r/'docs/SOURCE_MAP.md';s=p.read_text();heading='\n## Block 09 — Explicit domains and countable continuity\n';s=s.split(heading)[0]
s=s.replace('A finite index type represents the atlas.', 'For Chapters 2–5 below, a finite index type represents the atlas. Block 09 has the separate infinite-index interface documented at the end.')
s+=heading+'''
Physical PDF pages 30–33 (printed 17–20) were read and the source images inspected. The master file hash is unchanged. Generic `LinearPMap` means a linear map on an explicit domain, not a bounded everywhere-defined map. `StrongAtlas` uses an unconditional finite-subset net. The old finite/bounded modules are unchanged.

| Source | Formal representatives | Scope |
|---|---|---|
| (6.1)–(6.2) | `DomainAtlas.partialSum`, `GraphDomain.graphMap`, `graphNorm_sq` | Actual domain sum and actual L2 graph norm. |
| (6.3)–(6.6) | `StrongAtlas`, `DomainAtlas`, `GraphCompatible` | Explicit independent assumptions for generic atlases. |
| (6.7)–(6.9) | `squared_graph_convergence_iff`, `graph_convergence_iff`, `graph_components` | Both state and generator-image convergence proved. |
| (6.10)–(6.11) | `DiagonalDomain.operator`, `SpectralGraph.domain_iff`, `UnboundedExamples.basis_action` | Constructed spectral multiplier, maximal weighted-l2 domain. Not differential-oscillator identification. |
| (6.12), hierarchy | Not covered | Form-domain and strict inclusions still separate. |
| (6.13)–(6.14) | `SpectralGraph.graph_tail_series`, `graph_range_tail_tendsto` | Exact infinite weighted tail and actual limit. |
| (6.15)–(6.25) | Not covered | Bounded surrogates and topology-specific operator norm estimates next. |
| (6.26) | Original ambient `HasDerivAt` assumption | No construction of the unitary group. |
| (6.27)–(6.33) | `DomainAtlas.hasDerivAt_energy`, `energy_derivative_graph_limit` | Actual energy derivative and literal graph-compatible current limit. |
| Added fixed-row strengthening | `current_hasSum`, `current_row_abs_summable`, `current_tail_strong_bound` | Symmetry/domain invariance give scalar row convergence from strong reconstruction; no full action limit or double summability. |
| (6.34)–(6.35) | `amplitude_reverse`, `current_antisymm` | Correct conjugation and sign; formal symmetry is sufficient. |
| (6.36)–(6.37) | `boundary_identity`, `region_derivative_boundary_limit` | Finite receiving region, eventual containing finite subset and actual derivative. |
| (6.38)–(6.40) | `StrongAtlas.partial_norm_sq`, `energy_hasSum`, `energy_tsum` | Finite Pythagoras and true infinite Parseval. |
| (6.41) | `GraphDomain.packet_energy_constant` | Conservation along supplied all-time solution, not proof of (6.26). |
| Added realization | `DiagonalDomain.selfAdjoint`, `closed`, `graph_compatible` | Actual adjoint equality and graph compatibility of maximal weighted multiplier. |
| Added tests | `UnboundedExamples`, `DomainExamples` | Genuine unbounded and topology-limit tests; separate finite nonzero derivative witness. |
| (6.42) onward | Not covered | Infinite coarse domains and rearrangement still need proofs. |

See `BLOCK_09_PROOF_GUIDE.md` and the complete declaration index. Block 09 does not supersede the remaining continuum, gravitational, cosmological or empirical boundaries.
'''
p.write_text(s)
(r/'STATUS.md').write_text(f'''# {release}

**Current cumulative audit: {status}**, `verification/final/report.json`. A report marked INCOMPLETE or FAIL is not a checked release.

| Inventory | Count |
|---|---:|
| Block 09 new theorems | 113 |
| Previous cumulative theorems | 670 |
| **Cumulative theorem declarations** | **783** |
| Named declarations, including constructors | 952 |
| Mathematical modules | 47 |
| Aggregate | 1 |
| Intentionally invalid controls | 65 |
| Previous mathematical modules preserved unchanged | 40 |

Block 09 adds 29 definitions and two structures as well as 113 theorem declarations. Theorem counts by module: GraphDomain 16, CountableAtlas 17, CountableContinuity 23, DiagonalDomain 14, SpectralGraph 13, UnboundedExamples 19, DomainExamples 11. Counts include support and example theorems, not independent discoveries or full-edition completion percentages.

## Newly covered

Explicit partial linear domains, actual L2 graph norm and its two convergence components; strong orthogonal atlases and invariant domain sums; actual unbounded-domain energy derivatives; literal graph-compatible current limits; stronger symmetric fixed-row limits and absolute row summability; finite-region flux; infinite Parseval and global conservation along supplied trajectories.

The actual diagonal multiplier on its maximal weighted-l2 domain is proved densely defined, self-adjoint, closed and graph-compatible. Weighted domain/norm/tail identities include the harmonic spectral choice n+1/2. Its unboundedness and failure of a universal strong-to-graph implication are exact theorems, not finite numerical tests. A separate bounded two-sector example tests nonzero current and derivative signs.

## Not closed

General unitary-group or ODE construction, differential harmonic-oscillator identification, D(T^{{1/2}}) hierarchy, Section 6.3 bounded surrogates/operator-norm truncation, Section 6.5 infinite coarse domain/current obligations, residue/ladder routing, countable dilation, entropy-boundary extensions, continuum gravity/cosmology or empirical validity. Per-row absolute summability is not entire-double-array absolute summability. Strong scalar pairing convergence is not generator-image convergence.

## Evidence and reproduction

`verification/block08_baseline/report.json` is the freshly completed starting audit. `verification/final/report.json` is the authoritative current cumulative run. An external archive receipt records the complete fresh-extraction recheck. All 40 prior mathematical files are checked byte-for-byte, and all earlier preservation layers remain active.

Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 are pinned. Nine clean dependency revisions are checked; the imported cache is reused, not rebuilt wholesale. Only propext, Classical.choice and Quot.sound are allowed. Active mathematical sources contain no admissions or custom axioms.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

Next: Chapter 6.3's bounded spectral multipliers and topology-specific truncation. See `CONTINUE_HERE.md` for the exact continuation boundary.
''')
(r/'README.md').write_text(f'''# {release}

Cumulative formalization of the 550-page *Projector-Refinement Physics: Complete Unified Theory* by Komorebi P.

**Current cumulative audit: {status}.** The authoritative result is `verification/final/report.json`. Inventory: 783 theorem declarations, 952 names, 47 mathematical modules and 65 invalid controls. Block 09 adds 113 theorems; all 40 Block 08 mathematical files are preserved. These are declaration counts, not independent discoveries or a completion percentage.

## This block

The generator now has an explicit partial linear domain. A genuine graph norm and strong/countable atlas interface support actual Schrödinger packet derivatives, finite-region current limits, infinite Parseval and conservation. A stronger fixed-row argument uses symmetry and strong reconstruction without assuming full generator-image convergence. Every scalar row is proved absolutely summable; the whole double array is not.

An actual real diagonal multiplier on its maximal weighted-l2 domain is constructed and proved self-adjoint and graph-compatible. For lambda_n=n+1/2 it is genuinely unbounded, with no bounded extension. An exact sequence tends to zero in Hilbert norm but not graph norm. Separate finite nonzero tests reject wrong current, derivative and conjugation claims.

Read `docs/BLOCK_09_PROOF_GUIDE.md`, `docs/BLOCK_09_DECLARATION_INDEX.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and `STATUS.md`.

## Reproduce

Restore the exact Linux/WSL portable kit using `runtime_restore_support/` or use an existing matching kit. The multi-gigabyte runtime is not bundled. Lean is 4.34.0-rc2; Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

The verifier removes local outputs, rebuilds every active mathematical module and the aggregate, audits all inventoried declarations and constructors, requires the intended diagnostic for every invalid control, and verifies all preservation layers and nine clean dependency pins. It uses one worker and warnings as errors. The imported dependency cache is reused, not rebuilt wholesale. Allowed axioms are only propext, Classical.choice and Quot.sound.

The fresh baseline is `verification/block08_baseline/report.json`. Failed source snapshots and receipts are retained under `verification/development/block09/` and explained by `docs/BLOCK_09_FAILURES.md`. Intentionally false controls are not active mathematical modules.

## Package and fresh-extraction audit

```bash
python3 scripts/package_release.py --out ../Komorebi_Physics_Lean_v0.9.0_Checked_Block_09.zip
python3 scripts/recheck_archive.py --archive ../Komorebi_Physics_Lean_v0.9.0_Checked_Block_09.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /new/extraction/directory --out /external/evidence/directory
```

Packaging refuses a non-PASS final report or changed proof inputs. The second command requires a new directory and reruns the entire verifier, not just checksums. Its external report hashes the unchanged delivered ZIP.

## Boundary

No claim that all 550 pages are proved. General unitary-group construction, physical differential-oscillator identification, form-domain hierarchy, bounded-surrogate/operator-norm results, infinite coarse-cell domain/rearrangement theorems, later continuum/gravity/cosmology and empirical validation remain separate. The source's historical floating residuals are not rerun. Next: Chapter 6.3, actual bounded spectral multipliers and topology-specific truncation.
''')
(r/'CONTINUE_HERE.md').write_text('''# Continue Komorebi Physics Lean v0.9.0

Read AGENTS.md, README.md, STATUS.md, docs/BLOCK_09_PROOF_GUIDE.md, docs/BLOCK_09_DECLARATION_INDEX.md, docs/SOURCE_MAP.md, docs/CLAIM_LEDGER.json, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and the completed verification/final/report.json. Inspect the actual full manuscript pages and images for ambiguous formulas.

## Checkpoint and reproducibility

783 theorem declarations, 952 inventoried names, 47 mathematical modules and 65 invalid controls. Verify the completed current report before calling the checkpoint checked. The exact kit used here is `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`, but a new runtime may differ. Seven-part checksum restoration support is included; the runtime itself is not duplicated.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Recompile the baseline. Preserve all 47 mathematical modules byte-for-byte under a new `block09_preservation.json`, retaining earlier layers. Use one worker, bounded batches and warnings as errors. No admissions, custom axioms, native evaluation or kernel-bypass options. Imported pinned Mathlib/Lean caches are reused, not rebuilt wholesale.

## Immediate Block 10 target

Chapter 6.3, physical page 31, printed 18, equations (6.15)–(6.25): construct actual bounded spectral multipliers on l2, prove norm/strong convergence with the correct tail convention, then instantiate the harmonic resolvent, heat, unitary, bounded and Cayley expressions. Read whole pages, not just this instruction. For heat-tail convergence require t>0. For generic resolvents retain nonzero denominator/spectral assumptions; the harmonic spectrum is bounded below by 1/2. Do not identify zero-padded unitary truncation with norm convergence. Anchor bounded/Cayley tails at their actual limit value.

Source 6.2's D(T^{1/2}) hierarchy (6.12) remains open. The current maximal diagonal domain, adjoint equality and weighted graph tail are already done; do not re-count those declarations. A diagonal functional model is not a proved unitary equivalence to the differential harmonic oscillator on L2(R).

## What is already established

`GraphDomain`: actual LinearPMap domain, L2 graph map/norm and component-limit equivalence. `CountableAtlas`: arbitrary-index strong projectors, domain invariance, actual domain sums, finite Pythagoras, infinite Parseval and graph/action equivalence. `CountableContinuity`: actual domain-valued Schrödinger derivative, literal graph current limit, current antisymmetry, finite-region boundary limits and global conservation conditional on supplied trajectory.

The added strengthening moves T onto one fixed packet using symmetry. It proves scalar-row convergence and absolute scalar-row summability from strong completeness without graph compatibility. It DOES NOT prove TS_F psi→Tpsi in norm, a uniform bound over labels, absolute summability of the full double array, or arbitrary interchange of infinite sums.

`DiagonalDomain`: real diagonal multiplier on maximal weighted-l2 domain, constructed coordinate resolution, domain density, symmetry, actual self-adjointness, closedness, graph compatibility. `SpectralGraph`: weighted domain iff, graph norm sum and exact graph tail series tending to zero. `UnboundedExamples`: harmonic lambda_n=n+1/2, unboundedness/no bounded extension and shrinking eigenvector counterexample. The latter is a sequence of domain vectors, not fixed-state packet truncations. Spectral currents vanish.

`DomainExamples`: separate finite bounded nonzero current/actual local derivative witness -2,+2. It is not a global solution or the unboundedness witness.

## Remaining domains and sums

The source (6.26) group exp(-itT) has not been constructed. Actual domain-valued trajectories and their ambient derivatives are supplied to the generic theorem. No graph derivative is assumed. Source (6.41) is a conservation consequence along such a solution.

Source 6.5 requires construction of infinite coarse cells, proof that they preserve the operator domain, and justified current regrouping. Closedness plus appropriate graph convergence may help. Do not replace a missing double-sum argument with per-row absolute summability. Source residue packets and unbounded ladders are also not yet formalized.

## Release protocol

Record each attempted compilation with scripts/dev_check.py. Preserve failures. Add new proof-bearing names to the full inventory and Audit.lean. Update verifier preservation/control entries, source map, ledger, guide and failure record. The final cumulative report must complete PASS. Package only after proof-input hashes are stable. Rerun the entire verifier from a fresh ZIP extraction and provide the external receipt.

One-line restoration prompt: Open CONTINUE_HERE.md from Komorebi_Physics_Lean_v0.9.0_Checked_Block_09.zip, verify the 783-theorem/952-name checkpoint, preserve all 47 mathematical sources, and continue Chapter 6.3's bounded spectral multipliers and topology-specific truncation without conflating strong convergence, graph convergence and operator-norm convergence.
''')
p=r/'docs/FULL_EDITION_ROADMAP.md';s=p.read_text();s=s.replace('| 6 | Countable/unbounded extensions and later finite differential obstruction | Not completed | Inventory source and prove domain, convergence and noncommutative identities separately. |','| 6 | Countable/unbounded extensions | Block 09: domains, graph norm, current limits, Parseval and a self-adjoint unbounded spectral model | Form-domain hierarchy, bounded surrogates, topology-specific norm limits and infinite coarse cells remain. |')
a=s.index('## Immediate next block');b=s.index('## Limits not closed by Block 08',a)
s=s[:a]+'''## Immediate next block

Chapter 6.3, physical PDF page 31, printed 18: actual bounded diagonal multiplier operators, resolvent/heat/unitary/ bounded/Cayley tails, and the precise distinction between strong and operator-norm convergence. Require the needed heat-time and denominator hypotheses. Keep the tail anchors. Section 6.2's form domain (6.12) remains separate.

## Block 09 advance and boundary

The unbounded domain, actual L2 graph norm, both component limits, invariant-domain sums, literal graph-compatible current limit, actual packet derivatives, finite-region boundary flux and infinite Parseval are now checked. Symmetry gives a stronger fixed-row scalar limit from strong state convergence without full graph convergence. Per-row absolute summability is proved; global double-array absolute summability is not.

A real diagonal multiplier on its maximal weighted-l2 domain is proved dense, self-adjoint, closed and graph-compatible. Harmonic eigenvalues n+1/2 give a genuinely unbounded realization, exact weighted graph-tail series, and a strong-not-graph sequence. It is not identified with a physical differential oscillator or used to assume a general unitary group. Global conservation still consumes a supplied actual trajectory.

Chapter 6.5's infinite coarse-domain and rearrangement obligations, and residue/ladder routing, remain. No percentage of full-edition completion is asserted.

'''+s[b:]
p.write_text(s)
# Include the regeneration script itself, after successful execution, for provenance.
# Do not overwrite this portable script.
print('Wrote Block 09 documentation with cumulative status',status)
