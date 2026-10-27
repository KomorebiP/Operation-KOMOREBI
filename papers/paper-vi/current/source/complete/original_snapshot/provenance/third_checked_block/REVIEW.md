# Paper VI — third checked formalization block

Author: Komorebi P. · 6 September 2026 · v0.3.0

**Three of the last eight results are now complete: 10.2, 11.1 and 14.1.** The five remaining results all have checked supporting proofs, but still have explicit unproved clauses or connections. This is not a fully formalized paper.

| Count | Previous checked block | This release |
|---|---:|---:|
| Explicit Lean theorem declarations | 152 | 227 |
| Proof modules | 19 | 30 |
| Complete manuscript results | 25 | 28 |
| Partial manuscript results | 1 | 5 |
| Pending manuscript results | 7 | 0 |

The 75 new supporting theorem declarations are not 75 new manuscript theorems. The namespace audit covers 512 declarations, including definitions and generated auxiliaries; this is a third counting unit. These counts concern Paper VI only. No cumulative total for Papers I–VI is inferred from them. The original three conjectures remain open and are excluded from the 33-result ledger.

## Fresh checks

- The complete root module builds with Lean 4.34.0-rc2, strict elaboration options and warnings treated as errors.
- Every explicit theorem is printed in the axiom audit; every declaration in the project namespace is inspected. Only `propext`, `Classical.choice`, and `Quot.sound` are allowed. No active placeholder, custom axiom or unregistered unsafe code is accepted.
- All nine dependency revisions match the lockfile, with no tracked source modifications. Mathlib is pinned at `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- All 54 companion tests and six verifier controls pass again, including the optimized-Python negative control.
- Source hashes, exact theorem inventory, root-import coverage, audit coverage and the 33-result ledger pass.

The authoritative results are `verification/verification_status.json`, `lean_build.log`, and `lean_axiom_audit.log`. Development logs preserve failures and intermediate checks separately. The real verification report records `full_paper_formalized: false`. A successful build proves the Lean declarations, not the manually reviewed prose-to-Lean correspondence.

## Newly completed results

| Result | Statement | Checked scope |
|---|---|---|
| 10.2 | Poisson subordination | The actual normalized improper Poisson integral for every nonnegative eigenvalue, including zero; Bochner integrability and equality with the actual exponential of the finite spectral square root. |
| 11.1 | Exact discrete Green reconstruction at grid nodes | The literal finite Dirichlet tridiagonal matrix, its actual inverse, the scaled discrete Laplacian inverse, and the exact grid-node continuum Green identity for h=1/(n+1). |
| 14.1 | Semigroup survival identities | Actual finite Metzler-subgenerator exponential: survival derivative and strict positivity at finite nonnegative time, monotonicity, integrated hazard, existence of the survival limit, total defective density mass 1 minus that limit, and the eventual-absorption specialization. |

## Analytic proof details

For Poisson subordination, convergence is proved first by domination by the nonnegative mass-one kernel. The zero mode is included. The positive-mode identity is not assumed: the proof changes variables with `phi_a(x)=x-a/x` and with the reciprocal map `x -> a/x`. Their Jacobians give

    integral_0^infinity exp(-x^2-a^2/x^2) dx = exp(-2a)*sqrt(pi)/2,  a >= 0.

Scaling and the substitution `u=s^(-1/2)` give the actual scalar Laplace identity. Finite Bochner sums then recover the actual exponential of the spectral square root. The finite spectral resolution is the paper's starting data, as in 10.1.

The Green proof constructs the literal tridiagonal Dirichlet matrix and verifies its product with the kernel `min(i,j)-i*j/(n+1)` equals identity, including endpoint terms. It then identifies the actual inverse, scales by `(n+1)^2`, and derives the exact continuum Green value at grid nodes. Lean uses zero-based `Fin n` indices; manuscript node `i` is Lean index `i-1`.

For survival, the state is the actual matrix exponential acting on the initial probability vector. Metzler positivity and invertibility of the finite-time exponential prove positive survival at every finite nonnegative time. The derivative gives nonnegative exit density and monotonicity. The logarithmic derivative and interval integration give the hazard formula. Monotonicity and a lower bound give a limit; improper integration proves density mass `1-limit`. Eventual absorption gives mass one. Eventual absorption is an explicit additional hypothesis, not inferred from the subgenerator sign conditions.

## Checked progress on the five remaining results

### 10.3 — Fractional intertwining theorem

An integrable common-measure defect identity for actual nonnegative CFC fractional powers in a C-star algebra; a positive scalar normalizer and its normalized scalar integral representation.

**Still missing:** Identify the measure with sin(pi*alpha)/pi times Lebesgue measure, rewrite the literal resolvent-defect integrand, prove both printed norm constants and the exact-intertwining consequence, and connect the rectangular Hilbert-space formulation.

### 10.4 — Fractional semigroup refinement

Actual positive CFC powers and exponential semigroups in a unital C-star algebra; Duhamel identity, t*norm(D_alpha) contraction bound, and t*exp(-t*m^alpha)*norm(D_alpha) bound under an operator-order gap.

**Still missing:** Substitute the unproved alpha*m^(alpha-1)*norm(D) estimate from 10.3 to obtain the final printed common-gap bound; package the rectangular Hilbert-space specialization.

### 10.5 — Fractional refinement towers

For an actual CFC tower in a fixed C-star algebra, summable norms of fractional defects imply absolute summability of time defects and uniform convergence of their series on every bounded nonnegative time interval.

**Still missing:** Derive fractional-defect summability from the printed generator-defect hypotheses using both missing estimates in 10.3; package towers of varying Hilbert spaces.

### 13.2 — Memory/self-energy correspondence

Actual improper exponential integral, convergence, a real shifted right-inverse identity, and left/right multiplication through the memory integral, under an explicit exponential-decay bound in a real Banach algebra.

**Still missing:** Derive the required decay from the stated spectral-abscissa condition for arbitrary finite complex matrices, identify the complex damped Laplace integrand, and finish the literal inverse/self-energy statement.

### 15.1 — Naturality under exact intertwining

Actual finite complex rectangular resolvent intertwining and naturality of finite sums of common contour integrals, including integral/matrix multiplication interchange.

**Still missing:** Connect a holomorphic function on an arbitrary neighborhood of both spectra to an admissible common contour representation of the canonical functional calculus, including contour existence and independence.

The fractional-semigroup and tower modules use actual CFC powers and exponentials. They prove the Duhamel formula, the contraction bound, the common-gap bound in terms of the fractional defect, absolute summability from summable fractional-defect norms, and uniform convergence on bounded nonnegative time intervals. They do not derive the paper's generator-defect hypotheses without 10.3. In particular, the hypothesis that fractional-defect norms are summable is explicitly stronger than the generator criterion still to be connected.

The memory proof uses a real Banach-algebra exponential with a supplied exponential-decay bound. It is not yet the full complex spectral-abscissa theorem. The contour proof integrates actual resolvents, but does not yet construct or prove independence of admissible contours for the canonical holomorphic functional calculus. These are substantive remaining obligations; none is hidden by the partial label.

## Manuscript and numerical provenance

The latest Fractional Naturality Resolved manuscript remains the mathematical baseline. All ten earlier corrections are retained. This block updates the title-page count, abstract and formalization appendix, adds the subordination/Green/survival proof connections, and explicitly lists the five remaining boundaries. It also removes the misleading phrase “finite-dimensional statement below” before the bounded-operator fractional theorem. All 33 original theorem-like results remain in the same order. Authorship remains Komorebi P.

The companion implementation and figures are unchanged. Its 54 tests were rerun. The first-block numerical comparison retains agreement of all 79 numeric fields at absolute tolerance 1e-10 and relative tolerance 1e-8, after regenerating 19 figure pairs. That numerical experiment was not repeated in this source formalization block; its retained evidence is not a new universal proof.

The untouched supplied edition is under `provenance/original_release`; the two earlier checked scope records and audits are retained under `provenance`. Current source hashes, audit logs, manuscript and Lean patches, and the complete release manifest are included. The manifest excludes dependency/build caches and the producing toolchain binaries.

## Reproduction

Install the pinned Lean toolchain using elan. In `formalization/lean`, preserve the lockfile, obtain dependencies and the mathlib cache with `lake exe cache get`, then run `lake build KomorebiPaperVI` and `lake env lean -DwarningAsError=true KernelAudit.lean`.

For the complete gate, install the companion requirements and run `python3 verification/verify.py` with `lake` on PATH. Missing `lake` returns exit code 2; a failed mandatory gate returns 1. `--static-only` does not claim kernel verification. The producing environment's executable-self-location adapter is disclosed in `verification/runtime/RUNTIME.md`; the compiler, kernel and dependency sources are unmodified.

Compile `manuscript/Paper_VI_Reviewed.tex` with pdflatex until references stabilize. The final PDF is visually checked; `verification/pdf_validation.json` records its hash, page count and inspection scope. Run `companion/run_all.py` to regenerate the independent numerical study.
