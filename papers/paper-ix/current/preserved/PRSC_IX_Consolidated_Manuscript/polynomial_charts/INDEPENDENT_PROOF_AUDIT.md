# Independent proof audit: recovered parameter charts

Author of the mathematical project: Komorebi P.

Review date: 8 September 2026. This review was performed by a separate agent
reading the reconstructed raw sources. It did not write or modify their proofs.
The evidence reconciliation script imports none of the verification runner's
parser code. This is not an independent implementation of Lean's kernel.

## Claim card and verdict

Let \(p\) be prime, \(L\ge1\), \(e,q\ge0\), and let
\(F\in\mathbb Z[X_1,\ldots,X_{e+q}]^e\). Let
\(x\in\mathbb Z^{e+q}\), with \(F(x)\equiv0\pmod{p^L}\), and assume
that the actual derivative \(DF(x)\bmod p\) maps
\(\mathbb F_p^{e+q}\) onto \(\mathbb F_p^e\).

There exists a coordinate permutation \(\sigma\). With
\((\sigma z)_i=z_{\sigma(i)}\), write \(t_0\) for the last \(q\)
coordinates of \(\sigma x\). The exact conclusion is a homeomorphism
\[
h:t_0+p^L\mathbb Z_p^q\;\xrightarrow{\sim}\;
\{z\in x+p^L\mathbb Z_p^{e+q}:F(z)=0\},
\]
whose inverse is the last-coordinate projection after \(\sigma\).
For all parameters \(t,u\) and all \(N\ge0\),
\[
t\equiv u\pmod{p^N}\quad\Longleftrightarrow\quad
h(t)\equiv h(u)\pmod{p^N}.
\]
Coefficients and the base point are integral; roots and parameters range over
the full p-adic residue balls. Congruences are coordinatewise.

**Primary verdict: proved as written.** The raw proof audit, fresh Lean gate
and independent evidence reconciliation all passed for this exact claim.

Authoritative declarations:
`PolynomialGeneralChart.exists_parameter_homeomorph` and the expanded
`PolynomialGeneralChartContract.full_rectangular_chart`, both in the
`Komorebi` namespace. The exact reviewed source hashes are pinned by `inventory.json` and
`audit/reconciliation.json`.

## Dependency graph

1. The preserved integer Taylor theorem and actual derivative reduction give
   `integer_inverse_congruence_step`. Multiplication by \(q^n\) is cancelled
   only after proving the positive integer modulus is nonzero. A surjective
   endomorphism of the finite square digit space is injective. Induction gives
   all integer congruence depths in one residue class.
2. Canonical truncations at precision \(N+1\) remain in the original residue
   class, even when \(N=0\). The previously checked derivative base-point
   identity transfers surjectivity to the integer truncation. Evaluation
   commutes with the actual quotient ring maps. This transfers the integer
   inverse-congruence theorem to arbitrary p-adic inputs. Equality at all
   quotients gives injectivity.
3. Subtracting an integer target changes only constant coefficients, so the
   actual reduced Jacobian is unchanged. The preserved exact-root theorem
   gives a preimage of every admissible integer target. The image of the
   compact input residue ball is closed. It contains every canonical
   truncation of a target and hence its limit. No compatible choice of those
   preimages is asserted or required.
4. The square restriction is the actual polynomial evaluation map. It is
   continuous, surjective by step 3, and injective by step 2. The exact
   compact-to-Hausdorff equivalence theorem gives its continuous inverse.
   Evaluation of that inverse recovers the target, and step 2 proves all
   inverse congruence bounds.
5. For a surjective solved-coordinate block, the actual augmented polynomial
   system is \(\Psi(y,t)=(F(y,t),t)\). Its proved derivative formula has the
   identity free-coordinate block. The lower-root congruence places \((0,t)\)
   in the appropriate output ball. The inverse from step 4 produces the
   root, exact free coordinates, continuity and uniqueness in the entire
   input ball. Projection proves the reverse congruence implication.
6. Surjectivity of the full reduced derivative makes its actual coordinate
   columns span the output space. An injectively selected basis has exactly
   \(e\) columns, and its injection extends to a permutation of all \(e+q\)
   coordinates. Polynomial renaming by \(\sigma^{-1}\) transports evaluation
   and partial derivatives to these actual selected columns.
7. `reorderRootHomeomorph` identifies the entire original and reordered root
   subtypes. Composing it with step 5 constructs the claimed homeomorphism
   on the original root locus. Its inverse is definitionally the prescribed
   projection. Congruences are transported by the permutation in both
   directions.

All mathematical leaves are either proofs within the checked project modules
or identified primary Mathlib results. The user does not supply a suitable
minor, a root function, a chart, or a surrogate derivative. No circular
dependency was found.

## Obligation matrix

| Obligation | Status | Evidence |
|---|---|---|
| Actual integer polynomial evaluation | Passed | `evalSystem` is `MvPolynomial.eval`; `padicEval` is `eval₂` under the integer cast homomorphism. |
| Actual full derivative | Passed | `digitJacobian` sums the evaluated partial derivatives against the input vector. The expanded contract repeats this expression. |
| Automatic solved coordinates | Passed | Basis selection, dimension equality, injection extension, and `solvedJacobian_reorder_apply`. |
| Correct inverse renaming | Passed | `reorderPoint σ z = z ∘ σ`, polynomial rename uses `σ.symm`, and both evaluation and derivative identities are proved. |
| Whole original root locus | Passed | Target subtype retains the original `F`, original base ball and exact zero equation; `reorderRootHomeomorph` handles both directions. |
| Existence for arbitrary p-adic parameters | Passed | Full inverse of the augmented polynomial map, with the target's ball membership proved from the lower-root congruence. |
| Uniqueness for each parameter | Passed | Square augmented-map injectivity and exact root/free-coordinate specifications. No uniqueness of all rectangular roots is claimed. |
| Continuity both ways | Passed | Continuous inverse of the compact-ball map, continuous target inclusion, and explicit coordinate projection. |
| Every precision, not only the base precision | Passed | `∀ N` in the final theorem and expanded contract; coordinatewise divisibility is both preserved and reflected. |
| \(p=2\), \(L=1\) | Passed | The proof uses only primality and \(1\le L\); no odd-prime or deeper-ball restriction is introduced. |
| \(e=0\), \(q=0\), both zero | Passed | Empty finite types are permitted. Basis cardinality and finite sums cover the empty case; zero parameters yield a singleton parameter ball and local square uniqueness. |
| \(N=0\) | Passed | Divisibility by \(p^0=1\) is included; truncation at \(N+1\) retains the first residue digit. |
| Approximate versus exact base root | Passed | No conclusion asserts that the chart fixes `x`; the note explicitly requires exact \(F(x)=0\) for that stronger normalization. |
| Positive composite integer modulus support | Passed | The integer inverse lemma requires \(q>0\) and a surjective square digit map, not a field. The p-adic/chart theorems separately require prime \(p\). |
| Fresh compiler and complete axiom evidence | Passed | All 40 gates, 37 source/control files, 165 compiled outputs and 244 explicit declaration closures independently reconciled. |
| Source continuity across workspace pruning | Passed with explicit boundary | Prior 17 modules are recovered from the saved archive. New chart modules are reconstructed; lost hashes and failed logs are not represented as recovered. |
| Analyticity and differentiability | Out of scope | The result proves continuity and exact congruence equivalence. |
| Nonunit Jacobians and weighted lifting | Out of scope | Full mod-\(p\) surjectivity is an explicit hypothesis. |
| Arbitrary p-adic coefficients | Out of scope | Polynomial coefficients are in \(\mathbb Z\); arbitrary p-adic outputs and parameters are covered. |

## Decisive checks

The expanded main contract exhibits the actual derivative matrix, actual
p-adic polynomial evaluation, actual original-ball inequalities, actual
coordinate projection and all-depth equivalence. Its only geometric
assumptions are the lower-root congruence and full derivative surjectivity.
Thus success cannot be obtained by assuming a good minor or a preexisting
homeomorphism in an alias.

The new mathematical control uses \(F(X,T)=X^2-T\) at the dyadic origin.
Its full derivative is surjective, while the specified \(X\)-block is zero.
The parameter \(T=2\) belongs to the base parameter ball, but the equation
has no root, already modulo 4. This limits the conclusion to a *suitable*
coordinate choice and rejects a false arbitrary-prescribed-coordinate
extension. The finite `ZMod 4` check is a proof of this finite obstruction,
not evidence extrapolated to a universal theorem.

The inherited controls reject global square uniqueness, rectangular
uniqueness and one unsupported extra perturbation digit. The successful
positive controls and intended negative compiler diagnostics were
independently reconciled with the final gate.

The first recovery gate, `replay_recovered_01`, was interrupted by
`OSError [Errno 28] No space left on device`. Its output report was left
empty, so the independent JSON reader also failed when that path appeared.
Neither event is a theorem failure or a completed verification result. The
available logs and `DISK_EXHAUSTION_FAILURE.json` are retained, with hashes of
the discarded reproducible build. After disk space was recovered, `replay_recovered_02` also exhausted the
overlay while writing later contract evidence. That run likewise left an
empty report and is not accepted as a completed gate. Its failure record and
available logs are retained. The third run, `/dev/shm/paper9_charts_recovered_03`, failed at the compiler
version check because the kit launcher could not copy its compatibility
adapter into the exhausted `/tmp` filesystem. Its complete FAILED report
is retained; no project compilation ran in that attempt.

The fourth fresh run uses `/dev/shm/paper9_charts_recovered_04`, with
`TMPDIR=/dev/shm` and the existing shipped `compat/app_path.so` supplied as
`LD_PRELOAD`. The adapter source, binary, and kit launcher hashes match the
kit's shipped file manifest. The adapter only redirects the current process
executable-location `readlink` to `/proc/self/exe`; it does not edit Lean or
its proof checking. The existing runner preserves the inherited preload
setting. The supplementary `execution_environment.json` records these
overrides. No compiled project outputs from previous interrupted attempts
were reused for the fourth gate, and all mathematical sources stayed frozen.

## Primary-source checks

Seven exact local Mathlib dependencies are recorded in
`audit/mathlib_source_records.json`, including full file hashes, theorem
locators, extracted hypotheses and explicit applications. The pinned revision
is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, with Lean `4.34.0-rc2`.
The checks cover basis selection, extension of injections to permutations,
compactness of p-adic integers, norm/divisibility equivalence, small negative
powers, compact-to-Hausdorff homeomorphisms and differentiation after injective
variable renaming. Exact source code was available locally, so no web search
was needed. This is dependency verification and makes no novelty claim.

## Observed verification and reconciliation

The successful fresh gate is `/dev/shm/paper9_charts_recovered_04`, recorded in
the release under `polynomial_charts/verification/`. It passed **40 of 40
gates** in **141.775 seconds**, rebuilding **25 mathematical modules**, two
positive control modules and six expanded contract files. The latter contain
11 theorem contracts. Four negative controls were rejected with their
intended mathematical type mismatches.

The new eight mathematical modules contribute **60 theorems and 15
definitions**. Across the entire active mathematical, control and contract
sources, **244 explicit declarations** were audited: 195 theorems, 45
definitions and four abbreviations. All their axiom dependencies are subsets
of `propext`, `Classical.choice` and `Quot.sound`. No `sorryAx`, custom axiom,
unsafe proof mechanism or native decision shortcut was found.

The independent script reconciled all **37 source and control hashes**, all
**40 compiler/parser log hashes**, all **165 compiled-file hashes**, and all
**244 declaration/axiom reports**. It also confirmed that all **17 previous
mathematical sources** are byte-identical to the recovered perturbation
release. The parser retains the distinct primed name
`Komorebi.PolynomialCoordinateReorder.reorderPoint_inverse'`.

Pinned report SHA-256:
`cf1cbf35ad3b727bf91eb0f7701028a0a560e9147ae3e4146fcf2faa0d3dbcc0`.

Pinned inventory SHA-256:
`c3d51834f2b42bca9b48457c7587feb7c6746b4a8f1cc88598ae4462eb2e32a5`.

The successful independent command was:

```text
python3 /dev/shm/paper9_release_196a43c5b4f3/polynomial_charts/audit/reconciliation.py --gate /dev/shm/paper9_charts_recovered_04 --previous /workspace/scratch/196a43c5b4f3/recovered/PRSC_IX_Complete_Perturbation/polynomial_deformation/formalization --output /dev/shm/paper9_release_196a43c5b4f3/polynomial_charts/audit/reconciliation.json
```

After extracting the release and replaying the gate into a new directory,
`audit/reconciliation.py --gate NEW_RUN --previous PRIOR_FORMALIZATION`
performs the same checks while the compiled replay outputs still exist.
The release intentionally excludes those reproducible compiled files, while
retaining their hashes and the observed reconciliation result.

The evidence script was minimally extended after its first successful pass
to verify that `execution_environment.json` binds exactly this final report
hash and PASS status; that strengthened reconciliation also passed. This did
not modify any mathematical source or rerun the Lean gate.

Self-review of this audit and the new theorem note, README and chart checklist
found no notation or scope mismatch. No mathematical-token correction was
needed. Historical theorem claims in the older checklist remain identified
as preserved prior evidence, rather than a new independent re-audit of every
archived arithmetic proof.

## Remaining gap and safe scope

There is no identified remaining mathematical or verification gap for the
claim card. The fourth fresh run passed, and its frozen source inventory,
complete compiler evidence and axiom lists were independently reconciled.

The theorem does not resolve weighted singular lifting, first-order root
motion, arbitrary singular towers, native presentation invariance, global or
completed descent, or the other open arithmetic blocks in Paper IX. It proves
the continuous local rectangular parameter chart block under the exact
surjectivity hypothesis above.
