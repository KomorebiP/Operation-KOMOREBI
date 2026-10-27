# Independent written mathematical audit of Paper VII

Primary verdict: **correct only after a stated restriction**.

The normalized target is the finite packet/quantum theorem package actually stated in the raw companion, its six successive mathematical supplements, and the strengthened manuscript: finite complex Hilbert spaces, complete orthogonal packet resolutions, the declared observable algebra, bounded finite Hamiltonians, and the explicitly stated maps and limits. This verdict concerns mathematical statements and written derivations. It is neither a verification of declaration counts nor an independent Lean/compiler audit. For the cumulative corrected 19-item scope, I found no new counterexample to its explicitly amended statements. The original companion alone does contain a false-as-total statement, and the strengthened QEC section needs a nonzero-code restriction; its self-energy stability statement should explicitly type both hidden blocks as self-adjoint on common spaces.

Reviewed sources are pinned by SHA-256 in `reviewed_sources.json`. No raw source was modified. All core proofs, every mathematical argument in the six raw supplements, and all strengthened mathematical sections (lines 245–2688) were read. The stronger continuum tail was reviewed here at first pass; the root agent is separately reviewing that tail. No subagent was created: the attempted spawn was rejected by the thread limit.

## Claim card and conventions

- States are vectors in finite complex Hilbert spaces. Operators act on the left; matrix coefficient action on a bipartite state is `C -> AC`.
- Packet projectors are orthogonal idempotents with pairwise zero products and sum the identity. A transfer block has target/output index first: `U_ba=P_b U P_a`.
- Operator packets are maps `X -> P_a X P_b` on the complex Hilbert–Schmidt operator space.
- Adjoint is conjugate transpose, inner products are conjugate linear in the first argument, and real time evolution is `exp(-itH)`.
- Effective inverses live on the retained subspace, not the full ambient space. For a retained/hidden splitting, `H=[[A,B],[B*,D]]` and `F_P(z)=z-A-B(z-D)^(-1)B*`.
- Projected curvature is the curvature of the exterior extension of `nabla=P d`, or equivalently the covariant commutator with the actual vector-field bracket. The curvature coefficient is `P(dP wedge dP)P`.
- Exact correction must name a channel normalization or an explicit nonnegative output scale. The fifth supplement does this and treats the zero code separately.
- Infinite limits are limited to the actual norm, direct-limit, trace-norm, and fixed-positive-time hypotheses. Finite examples do not prove the five physical continuum conjectures.

## Decisive restrictions and counterexamples

### 1. Original Feshbach hypothesis is insufficient; supplements and strengthened text repair it

Raw companion lines 928–946 assumes only invertibility of `z-H_QQ`, yet displays both full and Schur inverses. Take the two-dimensional Hermitian matrix `H=diag(0,1)`, retain the first coordinate, and take `z=0`. The hidden denominator is `-1`, hence invertible, but `z-H=diag(0,-1)` is singular and the Schur complement is `0`. This is a valid counterexample under the stated raw hypotheses, not numerical instability.

The smallest correction is to require both `z-H_QQ` and `z-H` invertible, or equivalently require `z-H_QQ` and its Schur complement invertible. The first supplement lines 181–205 explicitly states and proves this correction. The final completion supplement lines 205–206 expressly retains earlier amendments. Strengthened lines 1668–1694 uses the equivalent corrected hypothesis. Its block elimination signs are correct: both triangular factors contain positive `B(z-D)^(-1)` or `(z-D)^(-1)B*` because the off-diagonal blocks of `z-H` are negative.

### 2. Raw physical anomaly compression vanishes automatically

Raw companion lines 1220–1242 defines the physical projector by the common kernel. Thus `C_a Pi=0` for every constraint and, for prescribed scalar coefficients, `[C_a,C_b]Pi=0` and `(sum_c f_ab^c C_c)Pi=0`. Hence `Pi A_ab Pi=0` irrespective of full operator closure. No self-adjointness or left annihilation is needed for this implication.

A nonzero compression in the exact setup would contradict the setup; a zero compression cannot certify closure. A valid nontrivial physical-kernel counterexample is the three-dimensional pair

`X=0 direct-sum [[0,1],[1,0]]`, `Z=0 direct-sum [[1,0],[0,-1]]`, `Pi=diag(1,0,0)`.

Both constraints annihilate the one-dimensional physical range, while `[X,Z]=0 direct-sum [[0,-2],[2,0]]` is nonzero and lies outside their complex linear span. The first supplement lines 259–300 explicitly diagnoses this issue. Strengthened lines 2337–2387 correctly distinguishes quotient closure in `End(H)/span{C_a}` from full realization of prescribed structure constants and automatic common-kernel compression.

### 3. The strengthened QEC section needs a nonzero-code hypothesis

Strengthened setup lines 1426–1431 allows any orthogonal projector, including `P=0`. The claimed traceless representative at lines 1443–1448 divides by `k=dim(PH)`. At `P=0` it is undefined. Further, syndrome theorem lines 1472–1499 says the coefficient matrix in the scalar Gram identities is positive semidefinite. If `P=0`, `E_1=I`, and `c_11=-1`, the identities `P E_1* E_1 P=c_11 P` both equal zero, although `c` is not positive semidefinite. The recovery proof at line 1542 also asks for a code density matrix, which does not exist on a zero code.

The cheap consistent fix is to assume `k>=1` throughout that section. The quotient definition itself remains meaningful for the zero code; if zero-code support is desired, it needs separate branches rather than cancellation by `P` or division by `k`. The fifth raw supplement lines 93–100, 121–143, 157–181, and 241–256 explicitly treats those branches and avoids the division. This is a local restriction, not a defect in its completed criterion.

The strengthened syndrome-measurement corollary lines 1570–1575 should expressly inherit the trace-preserving code-channel hypothesis from lines 1524–1528 and include the complement outcome when `sum Q_j != I`. Otherwise the stated probabilities `lambda_j` need not sum to one: e.g. `E_1=2I` gives `lambda_1=4`. On a normalized code-error channel, with complement probability zero on its output support, the assertion is correct.

### 4. Spacing, moduli, nonempty spectra, and empty maxima

The raw dispersion expression divides by `h^2`; the first supplement lines 213–249 correctly adds `h!=0` and proves a stronger all-real bound. For a physical grid, `h>0` is natural. The third supplement lines 56–57 and 70–100 explicitly requires positive algebra block dimensions, a nonempty addressed factor for the cyclicity equivalence, and positive cyclic modulus. It uses the empty finite supremum `0` for the zero module, rather than an undefined maximum. Its Euclidean transfer proof explicitly requires a nonempty finite spectrum before choosing `E_0=min Spec H` (lines 194–216). These restrictions are mathematically necessary for the exact formulas, and must survive any consolidation.

### 5. Self-energy stability needs both hidden blocks self-adjoint

Raw strengthened lines1942–1965 introduces the second hidden matrix `tilde D` but does not expressly state its self-adjointness. The intended comparison between self-adjoint hidden Hamiltonians is correct. If the theorem is read as imposing only its printed spectral-distance and coupling-norm inequalities on the second block, it fails: take `D=0_3`, `tilde D=5J` with `J` the three-dimensional upper shift, `B=tilde B=(1,0,1)`, `z=1`, `delta=1`, and `g=2`. Both hidden spectra are `{0}` and `norm(B)=sqrt(2)<=2`. Here `(I-5J)^(-1)=I+5J+25J^2`, so the self energies are2 and27, giving difference25; the printed right side is `4*5=20`. The needed restriction is that both hidden blocks are self-adjoint on the same hidden Hilbert space and both couplings act between the same identified hidden and retained spaces. This is exactly the stated proof's resolvent-norm input, and should be explicit in the final theorem.

## Dependency graph

1. Actual matrix action `AC` -> row-space characterization -> one-seed orbit dimension -> stacked row spaces and construction -> simultaneous direct-sum seed rank.
2. Product-vector minimum -> coefficient-matrix rank; actual partial trace -> `rho_B=C^T(C^T)*` -> reduced support criterion. The transpose/conjugation convention is checked, not replaced by `C*C`.
3. Positive modulus + unitary finite-order symmetry -> finite character orthogonality + adjoint reindexing -> orthogonal charge projectors -> tensor address partition and charge selection.
4. Complete resolutions -> corner reconstruction/composition -> finite path expansion -> adjoint/unitary conservation -> coherent path interference. No intermediate measurement is inserted into the unmeasured path sum.
5. Finite self-adjoint Hamiltonian -> unitary exponential -> Duhamel/conjugation derivative -> commutator leakage. Projector derivative identities -> skew canonical connection -> Kato ODE -> moving-frame Hamiltonian -> moving-packet Duhamel bound.
6. Smooth idempotent map -> locally invertible intertwiner -> actual range fibers and local products -> smooth overlap cocycles and intrinsic-section criterion -> projected derivative and local gauge compatibility -> bracket cancellation -> actual global curvature. The completion theorem uses real bounded endomorphisms and boundaryless smooth Banach manifolds; complex quantum examples are understood in real differential calculus.
7. Kraus sums + genuine identity-tensor amplification -> complete positivity; normalization -> trace preservation. Hilbert–Schmidt packet resolution -> dephasing and linear superblock composition. Conjugation covariance -> coherence preservation; output/input Choi convention -> Choi symmetry.
8. Scalar code Gram data -> Hermitian diagonalization -> discard null eigendirections -> orthogonal isometry syndromes -> total Kraus recovery -> trace/scaled correction and one decoder for span. Conversely, density-state linearity/polarization -> all code operators -> composite Kraus rank-one rigidity -> original Gram matrix using recovery completeness.
9. Invertible hidden denominator + invertible Schur complement -> projected resolvent. The same block equations -> Volterra memory. Hidden self-adjoint spectral theorem -> resolvent sign, memory Gram positivity, oscillatory positive coefficients, and norm stability.
10. Finite spectral theorem -> transfer positivity, logarithm reconstruction, and finite reflected Gram matrices. Centered periodic dispersion + Gaussian lattice domination -> fixed-positive-time heat and moment convergence. Gaussian Poisson summation -> continuum small-time dimension. The dimension corollary chooses one time for each epsilon; its formal conclusion is not a uniform diffusion interval or a simultaneous `t(N)->0` limit.
11. Quotient by constraint span -> universal closure criterion. Actual intertwiners -> commutator/anomaly transport. Common-space norm convergence -> bounded Hamiltonian, leakage, and constraint limits; trace-norm convergence -> heat traces. Each continuum theorem remains conditional on its own convergence hypotheses.

No circular implication was found in the written arguments. Classical external leaves are listed separately below.

## Obligation matrix: cumulative 19-item written scope

Statuses concern written mathematical arguments under recorded amended hypotheses, not compiler reports.

| Item | Actual obligation and decisive source | Status |
|---|---|---|
| 2.1 | `AC` row-space orbit; positive row dimension for full cyclicity equivalence. Companion 210–223; third supplement 64–76. | Passed with stated dimension restriction |
| 2.2 | Necessary stacked rank and attained seed count simultaneously in each independent direct-sum block. Companion 225–250; third 78–100. | Passed; empty supremum convention required |
| 2.3 | Kronecker action matches coefficients, Schmidt minimum matches rank, and actual reduced support. Third 105–148. | Passed for nonempty addressed factor |
| 2.4 | Actual binary translations/gate word, including `n=0`, gives coordinate basis. Second 56–90. | Passed |
| 3.1 | Positive-modulus character sum, completeness, self-adjointness, and eigenaction; `N=1` retained. Third 151–188. | Passed |
| 3.2 | Actual finite-coordinate tensor product multiplication and grouping; empty tensor factor family included by product convention. Second 100–134. | Passed |
| 4.1 | Arbitrary finite gate list, correct order, empty circuit boundary. First 65–93. | Passed |
| 4.2 | Two distinct adjoint conservation identities with correct index order. First 95–112. | Passed |
| 5.1 | Algebraic commuting packets reduce actual power-series exponential. First 119–133. | Passed |
| 5.2 | Actual exponential derivative/unitary norm estimate; both real-time signs, `P=0` and zero time. Fourth 60–102. | Passed in stated finite/C-star norm scope |
| 6.1 | Differentiability of constructed `U*psi`, real conjugate derivative, Hermitian negative connection term. Second 143–182. | Passed |
| 6.3 | Differentiate all packet laws; skew canonical connection and exact commutator derivative. Second 192–233. | Passed |
| 6.4 | Actual range local products, intrinsic local connection and gluing, actual manifold bracket, curvature tensor. Completion 45–55, 62–203. | Passed written derivation in stated boundaryless real bounded-operator scope |
| 7.1 | Trace cyclicity/dephasing duality for actual matrices. First 142–160. | Passed |
| 7.2 | Complete positivity at all finite auxiliary dimensions, actual block amplification, normalization. Second 242–282. | Passed |
| 8.1 | Both directions, total normalized recovery, null Gram values, zero code, complex polarization, all finite references, one span decoder. Fifth 62–256. | Passed written derivation; finite Hermitian diagonalization is a classical input |
| 9.1 | Actual retained-coordinate inverse under both invertibility hypotheses. First 169–210; S 1668–1694. | Failed raw assumption; passed explicit amended statement |
| 10.1 | Defined exponential agrees with finite spectral calculus, actual ground minimum and interval. Third 194–229. | Passed on nonempty finite state space |
| 11.1 | Actual quotient requires `h!=0`; all-real sine remainder and exact coefficient `1/12`. First 213–249. | Passed amended bound |

## Obligation matrix: strengthened additions

| Strengthened loci | Obligation | Status |
|---|---|---|
| 365–425 | Finite-group isotypic projectors and representation matrix units. Coefficients and inverse/index order are correct. | Passed by independent finite-unitary averaging reconstruction; exact Serre attribution not authenticated |
| 453–658 | Charge selection/addition, tensor selection, path interference, allowed path pruning. | Passed |
| 680–912 | Invariant packet equivalences, norm equality, Duhamel leakage, Kato transport, moving Hamiltonian and moving leakage. | Passed under existence of the stated differentiable propagator |
| 918–998 | Polar intertwiner and uniform `O(h^2)` local error -> `O(mesh)` telescoping global error. | Passed on the stated `C^2` compact interval |
| 1009–1092 | Local isometry, gauge connection law, nonabelian curvature, Bloch convention and Chern integral. | Passed; real scalar curvature explicitly uses `-i` |
| 1095–1224 | Hilbert–Schmidt projections, dephasing properties, measurements, superblock composition. | Passed |
| 1226–1247 | Converse Kraus/Choi representation theorem. | Conditional, exact cited-source form unverified in this pass |
| 1251–1336 | Coherence and Choi covariance with output tensor input convention. | Passed assuming the unitary symmetry convention carried from the cyclic setup |
| 1371–1387 | Generator representation for finite CPTP quantum semigroups. | Conditional, exact GKSL/Lindblad source and Schrödinger/Heisenberg convention unverified |
| 1390–1419 | Charged jump terms preserve every coherence order. | Passed algebraically |
| 1426–1575 | QEC quotient/traceless representative, positivity of c, total recovery and syndrome probabilities. | Failed at `P=0`; correct after `k>=1` and inherited channel/support hypotheses |
| 1578–1612 | Approximate overlap norm inequality. | Passed; no recovery fidelity theorem follows and none is claimed |
| 1641–1642 | Correctable observable-algebra commutant criterion. | Conditional, exact external source form unverified |
| 1668–1983 | Corrected Feshbach, spectral equivalence, sign, bounds, expansion, memory, local closure, stability. | Passed when both hidden blocks are self-adjoint and all differences use common spaces; print these prerequisites explicitly |
| 1999–2104 | Positive transfer/logarithm, finite reflection Gram positivity, ground gap convergence and packet transfer. | Passed with nonempty spectrum and the stated existence of an excited eigenvalue |
| 2112–2259 | Finite spectral limits, packet heat moments, centered lattice dispersion and dominated fixed-time convergence. | Passed; omit empty packets from moment quotients |
| 2262–2305 | Gaussian theta identity -> small-time dimension asymptotic. | Conditional on exact Gaussian Poisson identity; elementary tail/differentiated-tail estimates are valid |
| 2308–2317 | Epsilon-dependent selected time followed by sufficiently large lattice. | Passed at the stated pointwise conclusion; no uniform interval asserted by formula |
| 2337–2493 | Quotient closure, trivial common-kernel compression, physical invariance and exact/approximate refinement. | Passed |
| 2523–2685 | Bounded direct limits, fixed finite packet resolutions, norm summable Hamiltonians, kernel positivity/constraint closure limits, trace-norm heat limits. | Passed in the stated common-space/trace-class hypotheses; unbounded physical existence is out of scope |

## Source and computation checks

Read-only source commands used `nl -ba ... | sed -n ...`, `rg -n` for mathematical loci, and Python `hashlib.sha256` on exact raw byte strings. No status table was used as a premise for proof validity. There is no `.mathbox` ledger or applicable `AGENTS.md` in the inspected workspace hierarchy/source tree.

The file `exact_boundary_cases.json` records only exact integer witnesses for the three decisive boundary findings above. It is not a proof of universal packet, continuum, or recovery statements. No original numerical experiments were rerun by this auditor, and no Lean modules or imported theorem bodies were compiled or independently checked in this pass.

Classical inputs not independently authenticated here include the finite Hermitian spectral theorem, converse Kraus/Choi characterization, GKSL/Lindblad representation, operator-algebra correction theorem, and Gaussian Poisson summation. The finite-group dependency was subsequently discharged by the explicit independent unitary-averaging derivation in `FINITE_GROUP_RECONSTRUCTION.md`; no exact Serre source authentication is asserted. The raw supplements provide an internal written necessity proof for scalar finite Knill–Laflamme, so that implication need not rest on the strengthened citation alone. Parent-level source checks or formal evidence may discharge these exact-source leaves; this report itself does not claim to have done so.

## Remaining gap, safe conclusion, and cheapest next check

The smallest written fixes are to carry the raw amendments into the consolidated statements, add `k>=1` to the strengthened QEC section with explicit inherited normalization/support for the syndrome probability corollary, and print the self-adjoint/common-space hypotheses for both hidden blocks in self-energy stability. Do not turn the common-kernel anomaly compression into a closure test. A direct review of the final consolidated QEC definition and the Feshbach statement is the cheapest next check.

The strongest safe conclusion of this pass is: the cumulative amended finite 19-item mathematical arguments are coherent under their recorded admissible domains and normalizations; the strengthened manuscript has sound finite extensions once its QEC zero-code typing is restricted or separately treated, with exact external-source leaves remaining conditional. These results establish finite algebra, transport, recovery, and conditional bounded/heat limit criteria. They do not establish existence of a physical continuum model, full Lorentzian reconstruction, the Einstein infrared criterion, or a physical massless spin-two sector.

## Subsequent evidence reconciliation

The root agent separately authenticated Gaussian theta transformation from NIST DLMF and finite Kraus/Choi and trace preservation from the author-hosted Watrous text. Those source reports are in `audit/continuum_root/THETA_SOURCE_CHECK.json` and `audit/continuum_root/QUANTUM_SOURCE_CHECK.json`; they discharge the corresponding conditional leaves at the parent audit level. This auditor independently reconstructed the finite-group dependency in `FINITE_GROUP_RECONSTRUCTION.md`. The scoped Lindblad access attempt in `LINDBLAD_SOURCE_CHECK.json` authenticated publisher metadata only and leaves the exact generator representation theorem conditional.

The computation agent’s exact rational witness script was independently reviewed for the norm, Choi, and Feshbach conventions and replayed successfully:269/269 finite assertions, with byte-decoded JSON content matching the supplied output. `EXACT_WITNESS_REVIEW.json` pins the script SHA-256 and scope; `exact_rational_recheck.json` records the replay. These finite examples do not supply universal theorem or Lean verification.
