# Paper IX: cumulative archive with compatible p-adic polynomial towers

**Author: Komorebi P. — 8 September 2026.**

The nonsingular infinite-lifting block is complete. Starting from an actual lower polynomial root and a surjective reduced Jacobian, Lean constructs a compatible integer tower, proves that it converges to a p-adic point, and proves that the original polynomials vanish exactly at that point. Every stage has the checked number of next-level residue lifts.

This archive preserves all earlier Paper IX work: the full stated Nishibuchi conjecture, sharp dyadic towers, exact packet periods and isometries, affine/shared correction theory, polynomial obstructions, and exact lift counts. It also includes the available historical manuscripts, research checkpoints, proof sources, verification records and updated checklist.

## New theorem

Let \(p\) be prime, \(L\ge1\), and let
\[
F\in\mathbb Z[X_1,\ldots,X_d]^e,\qquad
x\in\mathbb Z^d,\qquad F(x)\equiv0\pmod{p^L}.
\]
If
\[
A_x=DF(x)\bmod p:\mathbb F_p^d\longrightarrow\mathbb F_p^e
\]
is surjective, then
\[
\boxed{\exists a\in\mathbb Z_p^d:\quad F(a)=0,
\qquad a\equiv x\pmod{p^L}.}
\]
The stronger theorem constructs one sequence \(z_n\in\mathbb Z^d\) satisfying
\[
z_0=x,\quad F(z_n)\equiv0\pmod{p^{L+n}},\quad
z_{n+1}\equiv z_n\pmod{p^{L+n}},
\]
\[
z_n\longrightarrow a,\qquad
 a-z_n\in p^{L+n}\mathbb Z_p^d,\qquad
DF(z_n)\bmod p=A_x.
\]
Only the initial Jacobian is assumed surjective. Its persistence, existence of later lifts, convergence, retained precision and exact polynomial vanishing are all proved.

Surjectivity gives \(e\le d\) and exactly
\[
\boxed{p^{d-e}}
\]
distinct next-level residue lifts at every stage of the selected tower. The obstruction group has one element. This is a per-stage count; a parametrization of all p-adic roots and multi-level descendant counts are not claimed here.

The integer tower theorem also works over every positive composite modulus, including one. The p-adic limit theorem and rank-based branching count use prime \(p\). The retained precision is a divisibility lower bound; the approximation error can vanish or have higher valuation.

## How the proof fits together

1. Actual Taylor transport identifies the next correction equation.
2. Surjectivity solves it for every residual digit. Integer polynomial congruence keeps the actual reduced Jacobian fixed.
3. Dependent recursion constructs a single compatible tower.
4. Increasing divisibility makes that tower Cauchy in the p-adic metric. Completeness supplies its limit, preserving every earlier precision.
5. Continuity of the original polynomial evaluation and residuals tending to zero prove exact vanishing at the limit.
6. The preceding finite-field count specializes to \(p^{d-e}\) choices at each stage.

The exact statement contracts expose the original polynomial evaluations, formal partial derivatives, initial hypotheses, sequence, limit and congruences.

## Where to read

| Location | Contents |
|---|---|
| `REMAINING_CHECKLIST.md` | Current notation, all proved results and remaining tasks |
| `polynomial_towers/PADIC_TOWERS.md` | New theorem and proof explanation |
| `polynomial_towers/formalization/` | New proof sources and their preserved dependencies |
| `polynomial_towers/INDEPENDENT_PROOF_AUDIT.md` | Independent statement and evidence review |
| `polynomial_towers/verification/` | Fresh compile, contract, axiom and negative-control results |
| `polynomial_counts/` | Correction torsors and exact one-step residue counts |
| `polynomial_lifting/` | Actual Taylor, finite obstruction, representative independence and shared polynomial lifting |
| `strengthening/` | Sharp towers, exact dyadic periods and continuous isometries |
| `shared_correction/`, `native/` | Earlier shared/affine and native-conjecture work |
| `manuscript/` | All 25 baseline PDF/TeX files exposed, including the main Paper IX PDF |
| `baseline/` | Original complete source archive preserved unchanged |
| `research/`, `historical/` | Recovered research, source windows and earlier release evidence |
| `MANIFEST.json`, `PACKAGE_COMPLETENESS.json` | Distributed-file hashes and prior-archive coverage |

Historical manuscripts have not been rewritten into one current paper incorporating every continuation. Their old status statements are superseded by the root checklist. Two older edge manuscripts remain partial recovered source windows, and the Annals TeX remains identified as a reconstructed text copy.

## Verification and reproduction

The fresh replay passed **22 gates in 78.188 seconds**: 14 modules, three contract files containing five expanded contract declarations, three rejected invalid proofs and **127 explicit declaration audits**. Six new modules contribute 35 declarations (31 theorems and four definitions); the other audited declarations belong to preserved dependencies and contracts.

The authoritative new report is `polynomial_towers/verification/polynomial_towers_verification.json`. All required project modules are freshly compiled. Only `propext`, `Classical.choice` and `Quot.sound` are permitted; warnings are errors. The pinned Mathlib cache is reused.

The toolchain is Lean `4.34.0-rc2` with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Run this new block:

```sh
python3 replay_paper9_towers.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run
```

Replay all preserved active proof blocks first:

```sh
python3 replay_paper9_towers.py --all --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_full_run
```

The separately supplied portable kit is required; the wrappers do not download dependencies. The new observed run covers this block and its dependencies. Earlier blocks retain their passing evidence and were not all rerun during this block. Their overlapping declaration counts should not be added as if they were unique discoveries.

## Boundaries and next work

The controls prove that \(X^2-5\) lifts modulo two to four but has no root modulo eight, that the rectangular projection \(F(X,Y)=X\) has distinct dyadic roots in the same lower residue despite its surjective Jacobian, and that \(X-2\) cannot preserve an unjustified extra digit of the initial approximation.

The next clear formalization is **uniqueness in the square nonsingular case** \(d=e\). A chosen tower has a unique limit, but uniqueness among all roots in the initial residue has not yet been formalized here. Rectangular local parametrizations and general singular towers need further arguments.

Unrestricted native Conjectures 13.2/13.3 still require precise objects, presentation-equivalence hypotheses and descent arguments. Surjectivity must apply to a combined polynomial system when shared lifting is claimed; individual block surjectivity alone is insufficient. Exact higher differences, other least-period families, general Mahler-kernel valuations and arbitrary-row classical-tail valuations remain separate research questions. Nishibuchi's full stated Conjecture 3.9 remains completed.

The ZIP covers the known local Paper IX collection and all earlier cumulative releases by uncompressed-file hashes. It excludes the separate portable runtime, reproducible compiled caches, unrelated raw search results, repeated cumulative ZIP containers and the full external Nishibuchi paper. The external source's URL, version and checksum remain recorded.
