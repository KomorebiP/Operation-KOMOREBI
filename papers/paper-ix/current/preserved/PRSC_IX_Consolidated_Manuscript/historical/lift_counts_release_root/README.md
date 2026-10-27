# Paper IX: cumulative archive with exact polynomial lift counts

**Author: Komorebi P. — 8 September 2026.**

The correction-torsor and exact-count block is complete. For every finite integer-polynomial system at a lower root, Lean now connects the actual next-level residue classes to the finite Jacobian correction fiber, constructs its kernel torsor, and proves both the lift count and the cardinality of the original obstruction group.

This cumulative ZIP preserves the completed Nishibuchi conjecture, sharp dyadic towers, exact packet periods, continuous isometries, affine/shared lifting and the preceding polynomial obstruction block. It includes available historical manuscripts, recovered research notes, source code, expanded theorem contracts, audit logs and reproduction scripts. The checklist is the current proved/open status reference.

## The new result

Let \(p\) be prime, \(L\ge1\),
\[
F\in\mathbb Z[X_1,\ldots,X_d]^e,\qquad
F(x)\equiv0\pmod{p^L}.
\]
Set
\[
A_x=DF(x)\bmod p:\mathbb F_p^d\to\mathbb F_p^e,
\quad \rho_x=\operatorname{rank}_{\mathbb F_p}A_x,
\quad \mathcal O_x=\mathbb F_p^e/\operatorname{im}A_x,
\quad o_x=[F(x)/p^L\bmod p].
\]
For the actual residue lift set
\[
\mathcal L_{x,L}=
\{y\in(\mathbb Z/p^{L+1}\mathbb Z)^d:
 y\equiv x\pmod{p^L},\ F(y)=0\},
\]
Lean proves
\[
\boxed{
\#\mathcal L_{x,L}=
\begin{cases}
p^{d-\rho_x},&o_x=0,\\
0,&o_x\ne0,
\end{cases}
\qquad \#\mathcal O_x=p^{e-\rho_x}.
}
\]
The nonempty correction-digit fiber is an explicit torsor for \(\ker A_x\): every valid digit is obtained uniquely from a fixed valid digit by adding a kernel vector. A checked bijection identifies these digits with distinct residue classes modulo \(p^{L+1}\). A separate class-preserving equivalence connects the original integer-domain obstruction to this finite-field cokernel.

The proof permits singular Jacobians and zero dimensions. The torsor and residue-class bridges work for arbitrary positive moduli; the vector-space rank formulas require prime moduli. Polynomial depth remains positive.

The checked examples at \(p=2,L=1,x=0\) show why the obstruction cannot be omitted:

| Polynomial | Jacobian rank modulo two | Number of lifts modulo four above zero modulo two |
|---|---:|---:|
| \(X\) | 1 | 1 |
| \(0\) | 0 | 2 |
| \(X^2\) | 0 | 2 |
| \(X^2-2\) | 0 | 0 |

These examples check boundaries. The general formulas are universally quantified Lean theorems, not conclusions from bounded enumeration.

## Where to read

| Location | Contents |
|---|---|
| `REMAINING_CHECKLIST.md` | Full notation, all completed results and remaining work |
| `polynomial_counts/POLYNOMIAL_LIFT_COUNTS.md` | New theorem, proof explanation, hypotheses and scope |
| `polynomial_counts/formalization/` | New sources and the three unchanged polynomial/affine dependencies |
| `polynomial_counts/INDEPENDENT_PROOF_AUDIT.md` | Independent mathematical and machine-evidence review |
| `polynomial_lifting/` | Actual Taylor, finite obstruction, representative independence and shared polynomial lifting |
| `strengthening/` | Sharp towers, exact displacements and periods, and continuous dyadic isometries |
| `shared_correction/` | Common quotient, universal property and actual affine pair lifting |
| `native/` | Earlier native-conjecture work and experiments |
| `manuscript/` | All 25 PDF/TeX files exposed from the original baseline, including the main Paper IX PDF |
| `baseline/` | Preserved original complete source ZIP |
| `research/`, `historical/` | Recovered research, source windows and earlier release/development evidence |
| `MANIFEST.json`, `PACKAGE_COMPLETENESS.json` | File hashes and coverage of previous archives |

The historical main manuscript has not been rewritten into a single current paper containing every continuation. Earlier status claims in historical documents do not override the current checklist. Recovered partial source windows remain labeled as partial.

## Verification and reproduction

The fresh replay passed **17 gates in 52.489 seconds**: nine modules, three contract modules containing six expanded contract declarations, three rejected invalid proofs and **106 explicit declaration audits**. Six new modules contribute 66 declarations; the rest are three preserved dependencies and statement contracts.

The final run details and allowed axiom closures are recorded in `polynomial_counts/verification/polynomial_counts_verification.json` and summarized in `RELEASE_AUDIT.json`. The verifier freshly compiles all modules needed by the new block, checks expanded contracts, audits every explicit declaration, and rejects invalid proofs about singular lift uniqueness, unconditional lifting and dropping the prescribed lower residue.

The runtime is Lean `4.34.0-rc2`, with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Only `propext`, `Classical.choice` and `Quot.sound` are allowed. Warnings are errors. The Mathlib cache is reused, but no project compiled outputs are reused by this block's fresh gate. Corrected development failures are preserved separately from its final result.

Run just the new block with the separately supplied portable kit:

```sh
python3 replay_paper9_counts.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run
```

Replay all preserved active proof blocks first, then the new count block:

```sh
python3 replay_paper9_counts.py --all --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_full_run
```

The full wrapper is supplied for reproduction. This block's observed fresh run covers the new count formalization and its dependencies. Earlier completed blocks retain their previously passing evidence and are not re-audited by the new run. Their declaration counts overlap and should not be added to obtain a count of unique theorems.

## What remains

The next clear formalization is lifting through all levels under a surjective reduced Jacobian, followed by constructing the compatible p-adic limit. General native 13.2/13.3 still need precise object definitions, presentation-equivalence hypotheses, transition maps and descent arguments. One successful step alone does not imply infinite lifting.

Exact higher differences, least periods beyond the checked dyadic family, general Mahler-kernel valuations and arbitrary-row classical-tail valuations remain research questions. Nishibuchi's full stated Conjecture 3.9 remains completed; these are further strengthenings and separate native goals.

This archive covers the known local Paper IX collection and all previous cumulative releases by uncompressed-file hashes. The portable runtime, reproducible build caches, unrelated search results, repeated cumulative ZIP containers and the full third-party Nishibuchi paper are excluded. Source URLs, versions and checksums are retained where applicable.
