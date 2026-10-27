# Independent mathematical review of the Strong Artin reader set

## Normalized claim and primary verdict

The reader set develops exact finite cyclic attachment tests, conditional
finite-image realization criteria, and local coefficient-lifting theorems.
Its general arithmetic target is Strong Artin. Its recursive conditional
theorem concerns finite solvable-image representations and requires a
realization or lifting input at every invariant cyclic step.

**Primary verdict: conditional on a named input.** The general automorphy
conclusion requires the still-unproved realization or nonregular lifting
gate. The finite algebra and local root results do not discharge that gate.
The complete manuscript, its two included mathematical appendices, and all
24 visual-guide spreads have passed mathematical reconstruction at the exact
source revisions recorded in REVIEW_PINS.json. This is a pass for the
stated scope, not a proof of the full conjecture.

## Review scope and independence

The reviewer reconstructed the main arguments from the recovered original
manuscript, `PSC_Strong_Artin_Full_Force_Status.md`, and the precise research
boundaries of formal checkpoints v0.25, v0.26, v0.29, v0.34, v0.35, v0.37,
and v0.38. The independent control program imports no producer code. It uses
different object construction for permutation representations and a direct
entrywise inverse of the square derivative rather than the producer's
generic rational inversion routine.

This is an independent agent review, not an independent mathematical
specialist or second Lean kernel. Related model errors remain possible.
The bounded external theorem authentication belongs to `LITERATURE_CHECK.md`
and `LITERATURE_SOURCE_MANIFEST.json`: fifteen primary works were checked,
not every inherited bibliography entry. Historical source/compiler receipts are distinguished
from verification performed in this edition.

## Dependency graph

1. Invariant irreducible restriction and a cyclic quotient give an extension
   torsor. Established cuspidal cyclic descent gives the automorphic fibre.
2. Actual multiplicity spectra determine the possible quotient offsets.
   One offset must satisfy every required local condition.
3. Local compatible base change of an Artin parameter gives zero monodromy
   and finite local Weil image. Unramified Satake roots belong to one finite
   cyclotomic alphabet.
4. A supplied residual realization at a good separating prime determines
   the ordinary cyclic offset. Alternatively, a sufficiently large supplied
   residual realization has a bounded cross-characteristic image, or a
   supplied continuous semisimple l-adic realization has finite image.
5. The local coefficient modules classify actual defects and correction
   possibilities. Their criteria require their stated exactness, continuity,
   arithmetic-domain, gauge, and inverse-certificate hypotheses.
6. A global realization or a suitable nonregular automorphy lifting theorem
   is still required. Unramified agreement and finite coefficient lifting
   alone do not supply all ramified/archimedean attachment conditions.

## Obligation matrix

| Obligation | Result | Exact restriction |
|---|---|---|
| Cyclic Galois extension action is free | Passed for stated irreducible restriction | An intertwiner is scalar by Schur. General reducible restrictions can have self twists. |
| Cuspidal cyclic descent fibre | External source leaf | Cuspidal base change and the exact established descent hypotheses are retained. |
| Coefficient rotation | Passed | Unsigned elementary coefficient of degree k scales by the kth scalar power. |
| Multiplicity-spectrum classification | Passed | Semisimple finite-dimensional complex representations and one common shift on all stable types. |
| Exact prime cyclic alignment sets | Passed | Empty, singleton, or all of Cp. Arbitrary two-element C3 filters are not exact local alignment sets. |
| Determinant selector | Passed | Unique candidate when p does not divide n. Candidate selection does not prove attachment. |
| Algebraic determinant blindness | Passed | Algebraic characters of GLn are determinant powers. For p dividing n, their determinants are twist invariant. |
| Stable epsilon equality | External theorem checked | Equal dimension/determinant, finite inertia, and the Deligne–Henniart high-ramification threshold. No undefined inverse-normalization element is used. |
| Total induction blindness | Passed | Taking all quotient twists merely permutes the total fibre. |
| Finite residual trace bound | Passed | Semisimple defining module and residue characteristic greater than n. |
| Separating-prime attachment | Conditional | A continuous semisimple residual realization is supplied. Good reduction and finite-alphabet separation are separate hypotheses. |
| Large residual realization criterion | Conditional | Residual characteristic avoids an explicit finite bad set and exceeds the rank/image bound. |
| Quotient-prime collapse | Passed, with imported modular uniqueness | Semisimplified reductions/congruences lose the ordinary torsor label. The full characteristic-polynomial form of Brauer–Nesbitt applies over the residue algebraic closure; bare traces are insufficient. |
| Finite l-adic trace rigidity | Passed | Continuous semisimple representation, finite coefficient extension, finite ramification, density-one Frobenius trace set. |
| H1/H2 correction criteria | Passed by mathematical reconstruction | Vanishing criteria do not establish arithmetic vanishing. Absolute and locally constrained obstruction classes differ. No fresh Lean replay. |
| Mixed-characteristic layer coordinates | Passed by mathematical reconstruction and finite controls | Actual square-zero layer Z/p^(r+1) to Z/p^r, not a unital section from Fp. |
| Effective matrix power-ball image | Passed by mathematical reconstruction and finite controls | Exact two-sided inverse over Qp, integral scaled inverse, m greater than s. |
| Full Strong Artin | Incomplete | The global realization/automorphic carrier/nonregular lifting and required local checks remain. |

## Decisive corrections and counterexamples

1. **Prime cyclic alignment.** A coset of a subgroup of Cp is empty,
   singleton, or full. Consequently, pairwise nonempty exact local sets do
   have a common intersection. The three subsets `{0,1}`, `{1,2}`, `{0,2}`
   are a valid counterexample only for arbitrary coarse filters. They must
   not be drawn as exact local attachment sets. The producers were notified.
2. **Semisimplicity is essential to the trace bound.** The five upper
   unipotent matrices `[[1,a],[0,1]]` over F5 form a nonsemisimple order-five
   subgroup with one trace value, while 5 is greater than the rank 2.
3. **The large-characteristic condition is essential.** The two scalar
   matrices `I3` and `-I3` over F3 give a semisimple order-two subgroup with
   all traces zero. Multiplicity 3 vanishes in characteristic 3.
4. **A compatible residue branch need not lift.** The unit 4 modulo 9
   satisfies `4^3=1 mod 9`. Every lift 4, 13, or 22 modulo 27 has cube 10,
   so no one lifts to a cube root of 1. This is a genuine obstruction to
   that branch, not a counterexample to all p-adic roots or Strong Artin.
5. **Residual singularity differs from Qp singularity.** For the unipotent
   square centre the inverse derivative exists over Q2 but requires s=2,
   exceeding v2(2)=1. At `diag(1,-1)`, the square derivative annihilates E12
   and is singular even over Qp. The effective inverse criterion cannot
   apply there.
6. **Historical prose repairs.** The recovered l-adic realization corollary
   used the phrase “Frobenius semisimple” while invoking a theorem requiring
   global semisimplicity. The new writer was asked to impose global
   semisimplicity or supply the separate finite-exponent density argument.
   The status note's cohomology/eigenvariety “equivalent formulations” were
   identified as sufficient construction routes unless converses are
   supplied. Its broad monomial wording was restricted to the established
   induction chains.
7. **Complex pseudocharacter continuity.** Abstract characteristic-zero
   realization does not itself display continuity. Continuity can be
   obtained from a semisimple image-algebra trace pairing and the continuous
   coordinates `T(gg_i)`. A homomorphic image of a profinite group is
   profinite as a compact-group quotient. The assertion that every
   continuous image of a totally disconnected space is totally disconnected
   is false in general and must not be used as the proof.
8. **Fourier zero support.** A test involving only ratios where the first
   Fourier transform is nonzero is insufficient. For p=2, multiplicities
   `(1,1)` and `(2,0)` have the same total rank, but their nontrivial modes
   are respectively 0 and 2. No quotient rotation aligns them. All zero
   supports must match as part of the full Fourier identities.
9. **The trivial character.** The trivial GL1 automorphic character is
   cuspidal under the usual definition. Its familiar exception is to entire
   Artin L-function holomorphy because the Dedekind zeta function has a pole,
   not to the degree-one automorphic correspondence. The guide writer was
   asked to correct its introductory phrasing.
10. **Finite exceptions.** Almost-everywhere polynomial recovery leaves all
    excluded finite places and every archimedean place to check. Merely
    saying “ramified places” can omit an excluded unramified place.
11. **A uniform bad-prime set.** The large-residual theorem's separating
    alphabet must be fixed before choosing the residual representation.
    A normal field containing K and roots of unity of all orders up to B is
    enough. There is no need to enlarge it by arbitrary matrix coefficients
    of a subsequently chosen lift and risk apparent dependence on the prime.
12. **Ordinary splitting fields in residual collapse.** The old proof chose
    stable-type extensions over an arbitrary number field without proving
    it was a splitting field. The repaired argument uses the commuting
    p-part and prime-to-p part of each finite group element. The latter
    belongs to H, and in characteristic p the former is unipotent. Equality
    of restrictions then gives equality of all reduced characteristic
    polynomials and identifies the semisimplifications. The latter step is
    imported modular Brauer–Nesbitt, authenticated in Chenevier's exact
    arXiv:0809.0415v2: Theorem A, p. 4; Lemma 1.12(ii) and Amitsur's formula,
    pp. 12–14; Theorem 2.12/Corollary 2.13, pp. 28–29; explicit uniqueness
    sentence, p. 31. It holds over any algebraically closed field with no
    rank or group-order restriction. This is distinct from cross-characteristic
    lifting. The proof never equates chi(g^p) with chi(g) over a nonprime field.
13. **Normalization in illustrative realization theorems.** The checked
    Scholze and Goldring–Shin statements have their own occurrence,
    historical, coefficient, and Satake/Weil normalization assumptions.
    An application must compare those exact polynomials with the project's
    finite-Satake polynomials. Being in a named cohomological range alone
    does not discharge that comparison.
14. **A report transcription error.** `LEAN_COVERAGE.md` initially recorded
    the positive matrix control as `B delta=(0,-32,32,0)`. Direct arithmetic
    gives `(0,0,32,0)`. The report was corrected. Its second coordinate is
    `-8+16-8=0`. Both the formal source and the independent criterion/image
    controls use the correct inverse and pass. The corrected coverage
    report hash is
    `9a6fb0c3d7af377a9046f72cd42f7970e2a2e4441a68010bddb9d7c115cf6b23`.
15. **Figure-caption correspondence.** The final assembly initially described
    the scalar root-tree asset as a matrix inverse-certificate figure. Root's
    page review caught the mismatch. The repaired caption names the actual
    roots of one modulo successive powers of two, the dead prefix, and the
    separate matrix Hensel theorem. The entire repaired `paper/main.tex` was
    read, including this caption; its source is included in the final pins.
16. **Visible l-adic assumptions.** Guide spread 16 now explicitly requires
    a continuous semisimple Galois representation over a finite extension of
    Q_l and finite ramification. Its reductive-monodromy explanation is a
    valid characteristic-zero alternative to the paper's direct trace-coordinate
    proof. The unipotent Z_l control is continuous, has constant trace, and is
    injective, so has infinite image.

## Independent finite computations and provenance

`independent_controls.py` is the authoritative reviewer program.
`independent_contract.json` states its bounds and arithmetic domains.
`independent_run/manifest.json` is a version 2 provenance record with input
hashes, command, exit status, enforced resource limits, and result hashes.
`independent_run/results.json` records the scientific results.

All controls passed:

- 9,113 equal-total multiplicity pairs over Cp for p=2,3,5 with entries 0,1,2.
  The exact alignment sets comprised 7,820 empty, 1,284 singleton, and 9 full.
- 1,633 four-constraint families of nonempty exact prime cyclic alignment
  sets. Pairwise intersection was equivalent to common intersection.
- 326 root-multiset examples of ranks 1 through 5 over the integral prime
  cyclotomic quotient rings. All coefficient-rotation and separator tests
  passed. 322 cases separated and 4 were blind.
- S3 standard trace-pairing controls over F5, F7, and F11, plus C3 diagonal
  over F7. The generated-algebra pairing was nondegenerate and the trace
  encodings were injective.
- The unipotent/F5 and repeated-scalar/F3 negative controls above.
- For A=`[[1,1],[0,1]]`, p=2, d=2, s=2, m=3: all 256 horizon correction
  tuples modulo 32 and all 4,096 tuples one level deeper. The power images
  and the exact scaled-inverse acceptance set agreed on 16 targets.
- The noncommuting root `[[1,1],[8,1]]` squared to `[[9,2],[16,9]]`.
  The target `[[9,2],[0,1]]` was rejected.
- H1 for Ad(diag(1,-1)) on M2(F3) had dimension 0 for C2 and dimension 2
  for C6. The trivial F3 module for C3 had a nonzero degree-two obstruction.

The supplementary reviewer program `independent_layer_controls.py` and its
contract/validated version 2 manifest in `independent_layer_run/` checked
actual coefficient rings rather than only abstract coordinate spaces:

- All 270 centre/degree cases using every GL2(F2) and GL2(F3) centre, canonical
  integer lifts, and degrees 1 through 5. All 19,920 target tests in the
  square-zero layers Z/4 to F2 and Z/9 to F3 agreed with the normalized
  adjoint-norm image criterion.
- 3,528 root multisets of ranks 1 through 3 over F4, F9, and F25. Raising
  roots to the pth power agreed exactly with coefficientwise Frobenius.
  Frobenius was injective, including the nonprime-field cases.

The third reviewer program `independent_cochain_controls.py` and its
contract/validated manifest in `independent_cochain_run/` directly enumerate
the actual normalized C3/F3 cochain complex. There are 9 one-cochains, 81
two-cochains, 9 cocycles, and 3 coboundaries. The differential ranks are 1
and 2, giving H2 dimension 1. The scalar section `(1,4,16)` modulo 27 has
the carry representative `(0,1,1,1)`, which is a cocycle and not a boundary.
This is an explicit nonzero class, not just a numerical dimension claim.
The same program checks the original syzygy plane and the enlarged target
over F2, F3, and F5, preserving the rejected original error `(0,0,1)`.

The final independent guide program is independent_figure_controls_v3.py,
with independent_figure_contract_v3.json and the validated version 2 manifest
in independent_figure_run_v3/. It imports only reviewer-owned helpers and no
producer code. It reconstructs every field of all 24 figure-data records:
20 exact numeric models, three schematics, and one explicitly scoped
monodromy record. It checks all 78 Satake multisets, the cyclotomic coefficient
tables and reductions, all trace words, both norm/coboundary calculations,
actual square-zero correction, the moving-relation and augmented-system
controls, all five rational Newton iterates and errors, the two-sided matrix
inverse and target tests, and every finite root-tree node and edge. The
infinite-image unipotent claim follows from the displayed injective affine
formula, not from finite sampling.

Regeneration:

```text
python3 <mathbox-computation-audit>/scripts/run_experiment.py
  --root <strong_artin_set> --contract evidence/independent_contract.json
  --input evidence/independent_controls.py --output evidence/independent_run
  --result evidence/independent_run/results.json --timeout 60
  --max-output-bytes 1048576 --max-memory-bytes 536870912
  --max-cpu-seconds 30 --max-cores 1 --max-threads 1
  -- python3 evidence/independent_controls.py
```

The output directory must be new when regenerating. The manifest validator
returned “valid evidence record; mathematical interpretation requires review”.
The original three computations and the authoritative figure v3 run passed.
Earlier figure-control attempts are preserved in
independent_figure_attempts.json, with the failed scientific run in
independent_figure_run/ and the result-missing run in
independent_figure_run_v2/. Two preflight rejections required software and
complete input-artifact declarations. The first scientific program's reference
regex omitted digits in h1/h2 filenames and failed its inventory assertion.
The v2 control reached and passed every mathematical assertion, but printed
its result without writing the declared result artifact. The v3 program fixes
both reviewer implementation/protocol defects and writes the result under an
explicit --result path. These failures were not producer mathematical
counterexamples, and no failed output was silently promoted to a pass.

Some exploratory reads used paths while the root
was reorganizing historical directories, or looked for a nonexistent
`PROOF.md`, and returned “No such file or directory”. The canonical
`lean/history/v0.xx` paths and actual `PROOF_LEDGER.md` were then found and
read. Those were path lookup failures, not computation failures.

## Exact remaining gap and strongest safe statement

For every singular weight-zero finite-Satake cuspidal descent arising in
the solvable cyclic recursion, construct an actual continuous residual or
ordinary l-adic Galois realization with the prescribed polynomials, or prove
the applicable quotient-prime automorphy lifting theorem. Include the
required local attachment conditions. Local correction theorems require
arithmetic instantiation and do not construct a nonzero automorphic carrier.

The strongest safe conclusion is conditional solvable Strong Artin from
those supplied gates, together with the exact finite algebra and the
certified local root theorems in their stated domains. General Strong Artin
remains open.

## Final revision pins

REVIEW_PINS.json records the final SHA-256 hashes for the paper body,
both included appendices, assembly and caption source, all 24 guide spreads,
generator, and exact data. It separately names the four passing independent
manifest records and the preserved failed attempts. These hashes delimit
the review; a changed source must be compared before carrying this verdict
forward. Root's build and visual layout review is a separate release check.

The complete formal appendix has been reviewed at SHA-256
`fe5c7ef5adb27b4bbaa8f74b4444a401749f7e7583bae83f0af1776f21ea7f79`.
Its H1/H2, moving-syzygy, ordered-remainder, contraction, finite matrix test,
explicit controls, and joint finite-tower derivations passed mathematical
reconstruction. In particular its final additions preserve
faithful-leading-layer requirements, actual kernel coefficients, independent
local conjugators, a nonnegative inverse bound, and the strict precision
condition. This verdict does not claim a fresh Lean compilation. The attempted
toolchain recovery returned HTTP 403, as recorded in `LEAN_COVERAGE.md`, so
no fresh compiler ran.
