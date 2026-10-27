# Computation audit of Paper III exact suites

## Outcome

**Outcome: audited, not executed as a fresh suite replay by this reviewer.** All three implementations were read in full and their finite assertions, ranges, counts, arithmetic domains, and adverse examples were checked against the available output receipts. No mathematical implementation defect was found. The parent reports fresh execution of the documented commands; this report does not claim that the reviewer independently reran those three full suites.

The recorded suite results are **15,331 + 2,622 + 677 = 18,630 passing counted assertions**. That is an assertion count, including repeated and dependent checks, rather than 18,630 independent examples or any exhaustive coverage of the manuscript's universal hypotheses. The implementations and receipts already describe themselves as bounded examples and explicitly disclaim a Lean replay or proof of universal Banach-space statements. Those limitations are accurate.

I separately executed 17 narrow audit checks: input/receipt hash and count reconciliation, a derivation of the iterator counts, exact hand-case evaluation of the tensor negative controls, the order-four decorated term count, interpreter optimization status for this audit process, and input stability. These checks passed. No original script or receipt was modified.

## Contract and reproduction commands

The documented commands are in `README_FIRST.md`, under “Reproduce the new exact tests.” Run them from the release root with ordinary Python assertion evaluation enabled and SymPy available:

```sh
python checkpoint_v0.3.0/tools/exact_packet_checks.py --output /tmp/p3_section16_replay.json
python checkpoint_v0.3.0/tests/section17/exact_section17.py --output /tmp/p3_section17_replay.json
python tests/test_higher_packet_calculus.py
```

The parent supplied `PYTHONPATH=/workspace/scratch/9014da510e4f/paper3_python_deps` for SymPy 1.14.0. The first two scripts accept an output path; the higher-order script writes its fixed release-relative receipt `evidence/section17_higher_order_tests.json`. That side effect is declared by its source, so rerunning it updates the receipt. I did not rerun it or change that output.

| Suite | Finite assertion actually tested | Arithmetic and deterministic data | Recorded result |
|---|---|---|---:|
| Section 16 | Coordinate reconstruction, composition, coordinate changes, one nonlinear inverse transport, a finite orbit/return-time comparison, and adverse controls for selected packet systems and rational vectors | `fractions.Fraction`; exact arithmetic modulo 2 in one control; dimensions 1–4; basis seeds 0–5 and fixed offsets | 15,331 |
| Section 17 tensor/second-order suite | Selected arbitrary multilinear tensors and complete resolutions; their finite packet expansion; ambient infinity-norm bounds for selected tensors; one polynomial second-order chain law at selected points/directions; partition counts | `Fraction` plus exact SymPy rational polynomial differentiation; seed 20261019 | 2,622 |
| Higher-order supplement suite | Selected cubic polynomial compositions with packet Faà di Bruno terms through order 4; exact polynomial segment Taylor remainders; finite packet coefficient reconstructions; sampled range-vector norm inequalities | SymPy exact rationals, polynomial differentiation/integration and equality; seed 20261020; receipt reports SymPy 1.14.0 | 677 |

No finite-field result is transported to characteristic zero by inference: the modulo-2 control is deliberately a separate counterexample to dropping annihilation. No floating tolerance, numerical integration, or probabilistic failure probability is used.

## Section 16 implementation and range

The script constructs an invertible basis matrix by elementary row shears over the rationals, inverts it by exact Gaussian elimination, and conjugates diagonal coordinate projectors by that matrix. This gives the actual finite complete idempotents, including oblique ones. The projector assertions verify completeness, idempotence, and pairwise annihilation of the primary family. Auxiliary families use the same structurally invertible construction. The coordinate evaluator actually analyzes the nonlinear function applied to the synthesized full tuple; it retains mixed terms.

There are 24 labelled family instances: six seeds in each dimension 1, 2, 3, and 4. In dimension one all seeds yield the same identity family; these are not 24 distinct geometric decompositions. The script exhausts the Cartesian grid `{-1,0,1}^n` for each family, giving

`6(3 + 9 + 27 + 81) = 720` point/family iterations.

Each iteration performs seven coordinate/inverse assertions and fourteen orbit assertions. The orbit map is the coordinate swap in dimensions at least two and identity in dimension one; it is an involution. Steps 0–6 are checked. Consequently, these are tests of the coordinate identity for this orbit map, not sampled general nonlinear dynamics.

The independently chosen legal tuple is formed by projecting a separate rational vector in each slot. This is a valid domain fixture because every component belongs to the corresponding projector range. The group name `all_legal_tuple_reconstruction` means full reconstruction of each chosen tuple; it does not enumerate all legal tuples over the infinite rational field. The changed-coordinate family also contains a zero projector, providing a useful algebraic edge case beyond the manuscript's nonzero-packet convention.

The count is exactly

`6 sum_{n=1}^4 (1+n^2) + 21·720 + 7 = 204 + 15,120 + 7 = 15,331`.

| Count group | Assertions |
|---|---:|
| Primary projector axioms | 204 |
| Two analysis/synthesis identities | 1,440 |
| Nonlinear reconstruction, composition, coordinate change, selected legal-tuple inverse, and nonlinear shear inverse | 5 × 720 |
| Iterate conjugacy, steps 0–6 | 5,040 |
| Return-time equivalence, steps 0–6 | 5,040 |
| Empty/zero module and three adverse mechanisms | 7 |

The missing-completeness example projects `(3,5)` to `(3,0)`. The modulo-2 family consists of three identity maps, whose sum is identity but whose pairwise products are nonzero; synthesis followed by analysis sends the legal tuple `(1,0,0)` to `(1,1,1)`. The nonlinear control evaluates `(x_1 x_2, x_1^2+x_2)` at `(2,3)`, giving `(6,7)`, while diagonal-only output restrictions give `(0,3)`. These fixtures belong to the respective stated adverse domains and falsify the shortcuts they target.

## Section 17 tensor and second-order implementation

The tensor evaluator explicitly stores coefficients indexed by an output and an ordered input multi-index. It does not assume symmetry. The projectors are conjugated coordinate projectors from upper triangular matrices with diagonal one. Those matrices are exactly invertible, and all primary projector identities are tested. The `vsum` helper materializes its iterator before summing separate output coordinates, so it does not suffer generator exhaustion after the first component.

### Reconstruction and resolutions

The multilinear loop contains 75 cases. Input dimension is 2 except every fifth case, where it is 3; output dimension is 2 except every seventh case, where it is 3. Arity is `case mod 4`, thus 0–3. Coefficients lie in the integer set `{-3,…,3}` and input coordinates in `{-5,…,5}`. This is a fixed seeded sample, not an exhaustive population. For each selected tensor it exhausts all input packet label tuples and output labels at the chosen directions.

There are 19 nullary cases. The tensor evaluator handles them with the unique empty multi-index and empty product one. The 75-count projected-input group includes 19 deliberately vacuous checks in these nullary cases. The 161 per-output expansion checks and 120 positive-arity output-range checks agree with the varying dimensions.

A separate loop uses 45 complete resolutions with 2 or 3 pieces, dimensions 2 or 3, and arities 0–3. It constructs the last matrix as identity minus the preceding sum. All 45 sampled input resolutions contain a non-idempotent member; that is explicitly checked. This verifies the finite expansion on examples outside projector systems and tests the correct algebraic fact that completeness suffices for multilinear reconstruction. It does not claim that these general resolutions yield direct-sum coordinates.

### Exact ambient norm certificates

There are 16 sampled tensors for norm checks:

- six cases have dimension 3 and arity 1;
- five have dimension 2 and arity 2;
- five have dimension 2 and arity 3.

For each tensor, every input packet tuple and output packet are visited, giving

`6·3^2 + 5·2^3 + 5·2^4 = 174` ambient block inequalities.

The multilinear infinity norm is computed by enumerating **all sign vectors in every input slot**. This is exact for these finite real tensors: on a product of cubes each coordinate function is separately affine in each scalar variable, so its absolute maximum is attained at a sign vertex. Taking the maximum over output coordinates gives the vector infinity norm. Matrix infinity norms use exact row sums. The coefficient tensor of each projected ambient block is rebuilt by evaluating it on all standard-basis input tuples, which is valid by multilinearity.

Thus the 174 values are complete finite certificates for the sampled **ambient extended** maps `Q B(P_1 ·,…,P_r ·)`. They are not exact norms of the literal maps between projector ranges. The code's nearby “restricted map” comment refers to its ambient extension; the receipt accurately calls the tests ambient norm certificates. An additional 162 checks assert positivity of the bound whenever the sampled projected tensor is nonzero. These are conditional dependent checks, not additional independent tensor cases.

### Chain rule and partition counts

The second-order law uses fixed maps `G(x,y)=(x+xy,y+x^2)` and `F(u,v)=(u^2+uv,v^3+u)`, 24 sampled triples of two-packet families, sampled integer base points and directions, and all eight input/output label triples. This gives 192 decorated second-order equalities. The left side differentiates the expanded composite directly in SymPy. The right side differentiates `F` and `G` separately and sums all four two-block and both one-block intermediate packet choices. These are genuinely different constructions of the derivative identity, although both use SymPy's exact symbolic backend.

The partition generator inserts each next integer into an existing block or starts one new final block. Canonical creation order prevents duplicate encodings of an unordered partition. Counts for orders 1–7 are compared with the Stirling recurrence, giving 28 checks. The decorated counts use intermediate-label counts 0–4, giving 35 Touchard checks. The zero-label cases at positive order correctly yield zero. This is exhaustive enumeration of partitions within that stated range, not an exhaustive theorem in arbitrary order.

### Adverse controls

Keeping only one intermediate packet label is false in 154 of the 192 sampled second-order cases. The suite records that count and has one assertion requiring at least one counterexample; 154 is not added again to the assertion total.

The explicit nonsymmetric tensor control was independently evaluated by the reviewer. Its full value is `(14,18)`, its diagonal-packet sum is `(72,76)`, and its incomplete sum is `(0,28)`. Therefore the reported differences are exactly `(-58,-58)` and `(14,-10)`. The same modulo-2 nonorthogonal-coordinate mechanism is checked separately. These controls test actual invalid shortcuts, not assertions obtained by restating a filter selecting only successful examples.

## Higher-order and Taylor supplement implementation

The two packet families are fixed complementary rank-one systems obtained by conjugating diagonal coordinate projectors by fixed shear matrices. The coefficients, points, and directions are seeded rational numbers. The randomly generated maps are specified cubic polynomials in two variables, with some mixed/quadratic coefficients forced nonzero and no constant term. The nominal `deg` parameter is unused, but every call uses its fixed default, so no claimed degree range is affected.

Ten trials use derivative orders 1–4. The selected input label patterns alternate, giving prefixes of `0101` or `1010`; the script does not enumerate every possible input-label pattern. It does enumerate every intermediate label assignment for every partition of each selected derivative. It separately differentiates the expanded composite, evaluates an unlabelled partition formula, and evaluates the decorated formula with intermediate projectors. All directions passed to the outer derivative are evaluated rational vectors, so the directional-derivative helper correctly treats them as fixed arguments.

At order four the formal decorated-term count is

`S(4,1)·2 + S(4,2)·4 + S(4,3)·8 + S(4,4)·16 = 2+28+48+16 = 94`.

This counts formal decorated terms, including terms that vanish because the inner and outer maps are cubic. It is not a count of nonzero contributions.

The Taylor loop uses 22 cubic maps, points, and directions, and truncation orders 0–3. It computes the polynomial on the exact segment and integrates the exact weighted `(m+1)`st derivative with denominator `m!`. This independently checks the normalization of the integral remainder, including the order-zero case. The order-three remainder is identically zero for cubic maps, so the suite does not test a nonzero fourth-order remainder. It checks both unprojected and projected equalities.

The 132 packet coefficient checks equal `22(1+2+3)`. Lower-order coefficients are rechecked for several truncation orders; there are 66 distinct trial/derivative-order coefficient evaluations. The count should remain “132 assertions,” not “132 independent Taylor coefficients.”

The explicitly wrong chain rule omits `DF D^2G` with a linear outer map. The true mixed second derivative is `(1,3)`, whereas the false outer-second-derivative-only formula gives zero. Thus this control detects the missing one-block partition.

The final 80 norm inequalities use one fixed matrix `A=[[2,-1],[1,3]]`, the four input/output projector pairs, and 20 sampled rational vectors for each pair. They verify `||QAz||_infinity <= ||Q|| ||A|| ||z||_infinity` for `z=P v`. They do **not** optimize over the whole range unit ball, calculate the exact restricted operator norm, or prove the stronger range-jet theorem. The source comments explicitly describe the checks as sampled vector inequalities. The universal restriction bound requires the ordinary proof supplied separately.

| Higher-order group | Assertions |
|---|---:|
| Unprojected partition chain rule | 40 |
| All intermediate labels for selected input patterns | 40 |
| Two literal output components | 80 |
| Decorated formal term counts | 40 |
| Exact polynomial Taylor remainder | 88 |
| Two projected remainder identities | 176 |
| Packet Taylor coefficient reconstructions, including repetitions | 132 |
| Missing-branch negative control | 1 |
| Sampled range-vector norm inequalities | 80 |
| **Total** | **677** |

## Execution and provenance limits

The original Section 16 receipt records a self-reported elapsed time of approximately 2.193 seconds and contains the matching script SHA-256. That is the suite's recorded time, not a runtime measured by this reviewer. The Section 17 receipt has no software version, source hash, or elapsed-time field. The higher-order receipt includes SymPy 1.14.0, but no script hash or elapsed time. The fresh observed hashes below bind the inputs and outputs available during this audit; they do not retrospectively create missing launch metadata.

The three script hashes and the higher-order receipt hash also match the release's existing SHA-256 manifest. The reviewer confirmed that all six audited input/output files were unchanged during the narrow audit checks. The extracted release is not a Git repository, so no Git commit or clean-working-tree assertion is made.

The narrow audit process observed CPython 3.12.14, SymPy 1.14.0, Linux x86_64, and Python optimization flag zero. Its source-receipt check record is `computation_audit_observations.json`, with `run.status = completed` and `research_suites_reexecuted = false`. Those hardware/software/runtime observations apply only to the audit process. It is a custom source-audit record, not a fabricated version-2 replay manifest for the three suites. No broad test was rerun, no tested bound was expanded, and no external theorem or approximate numerical calculation was introduced.

All three suites are single-process deterministic programs with fixed seeds and finite loops. There is no sampling early-exit, symmetry filter claiming exhaustive polynomial coverage, parallel reduction, cache-dependent acceptance, or timeout interpreted as a pass. The higher-order suite relies on Python `assert`; future reproductions must use the documented ordinary interpreter mode, not `python -O` or `PYTHONOPTIMIZE`.

## Release interpretation

The counts and negative controls are suitable as bounded exact computational evidence supporting the written proofs. They show that the implementations retain cross-packet and partition terms on the specified examples, that several false simplifications are rejected, and that the scalar/tensor arithmetic agrees exactly. They do not certify arbitrary dimensions, arbitrary Banach spaces, all polynomials, all input label patterns, all derivative orders, exact restricted operator norms, analytic convergence, or Lean kernel replay.

No new bug, false receipt count, or invalid adverse example requires an implementation repair. The only necessary care in the release description is to preserve the precise distinction between counted assertions, selected examples, exhaustive sign-vertex certificates for fixed tensors, and the separate ordinary universal proofs.

## File identities

| Role | File | SHA-256 |
|---|---|---|
| Section 16 source | `paper3_release/checkpoint_v0.3.0/tools/exact_packet_checks.py` | `30191b01ea38552dee9dfa27716fc4b54cf9940eefb9ce5148b15788118c1e6b` |
| Section 17 source | `paper3_release/checkpoint_v0.3.0/tests/section17/exact_section17.py` | `fe0dbed92ee60278b5e12f7f575f949c17fbabc2147b7da97c8830b640a3c308` |
| Higher-order source | `paper3_release/tests/test_higher_packet_calculus.py` | `adea0f0389c06c88f368faeccd0b5c6a4eb45a4b010e68dbd38ff346d4ff7c03` |
| Section 16 receipt | `paper3_audit/section16_exact_replay.json` | `9d3ca07b2ac34b0c9bd7ee7a2fe21dc9140dd6644f9b6930ec88b81e48107f67` |
| Section 17 receipt | `paper3_audit/section17_exact_replay.json` | `6b8e5bf246bf2d1d68db2f2148dd007c5d37329831cbb53e8744ab807c6eef32` |
| Higher-order receipt | `paper3_release/evidence/section17_higher_order_tests.json` | `626dafe0d0fbae785368c88c845aefece87e23b45410bc717fa542e64f51c376` |

The audit observation record itself has SHA-256 `ff93de98805045753031fd7f668d9ce7e2303f17b4bbc89b9b8d90df9a20d34c`.
