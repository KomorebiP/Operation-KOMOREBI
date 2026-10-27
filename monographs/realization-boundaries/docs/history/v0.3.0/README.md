# Realization Boundaries — checked Lean companion v0.3.0

**Current checkpoint:** `verification/accepted_v0.3.0/run.json`. Read its status field before relying on the report. This is an incremental continuation of v0.2.0, not a claim of full-book formalization.

## What this checkpoint adds

Five new production modules prove the tail-divisibility signature, exact unmarked and marked classification, finite-change coordinate transport, torsion-image obstruction for arbitrary homomorphisms, embedding and surjection criteria, and concrete canonical-completion reconstruction obstructions. All fifteen inherited production modules are unchanged.

For the actual paired-prime subgroups of the infinite product:

- `pairedGroup_isomorphic_iff`: G_a is isomorphic to G_b exactly when the selector functions disagree at finitely many indices.
- `pairedGroup_marked_isomorphic_iff`: preserving the prescribed indicator upgrades the criterion to literal equality of selectors.
- `pairedGroup_eq_of_finite_disagreement`: finitely different selectors define the same subgroup of the fixed ambient product.
- `finite_disagreement_of_nontorsion_image`: any homomorphism with one nontorsion image element already forces finite disagreement.
- `hom_image_torsion`: infinitely different selectors force every image element to be torsion. This does not force the homomorphism to be zero.
- `normalFormTransportEquiv`: the exact correction `(r,d) -> (r,d+s_a(r)-s_b(r))` respects the twisted group law and fixes the realized ambient vector.
- `no_completion_invariant_reconstruction`: no assignment invariant under the canonical completion isomorphism can recover every original group. No computability assumption is needed.

The full all-homomorphism diagonal formula, endomorphism ring, automorphisms, seed rank, oracle semantics and grammar diagonalization remain explicitly unclaimed.

## Reproduce the verification

Use the pinned Linux portable kit with Lean 4.34.0-rc2 and the recorded Mathlib revision. The package does not repeat the multi-gigabyte runtime.

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-fresh-verification
```

Choose a new evidence directory. The runner verifies pinned dependencies, rebuilds all project output from scratch, audits declarations and axiom dependencies, compiles the positive contracts, checks the exact diagnostic failures, replays each production module through Lean's kernel checker, and compares source/compiler/dependency endpoint hashes. No network update is made.

The expected-failure sources under `tests/negative` are deliberately invalid and never imported by production. To develop one source, use `scripts/check.py SOURCE --kit PATH`.

## Navigate the handoff

`PROGRESS_LEDGER_v0.3.0.md` is the authoritative restart ledger. `LEAN_VERIFICATION_REPORT.md` records the accepted gates and limits. `docs/MONOGRAPH_COVERAGE.json` retains all 45 numbered book entries with exact coverage. `docs/EXACT_STATEMENT_REVIEW.md` includes actual exported type signatures. `docs/NAMED_THEOREMS.json` distinguishes explicitly written theorems from generated declarations. `docs/DEVELOPMENT_INCIDENTS_v0.3.0.md` records failed development attempts and their resolutions.

Previous evidence and ledgers are preserved, not silently replaced. Prior documentation is under `docs/history`; the earlier accepted verification directories retain their original names and receipts. `provenance/PARENT_v0.2.0_SOURCE_IDENTITY.json` checks all inherited production modules against the actual parent archive. The finalized monograph and its original source package are retained unchanged as publication provenance.

## Trust boundary

Kernel replay uses Lean's own implementation, not an independent second kernel. Standard logical axioms, the restored compiler, imported compiled caches, runtime and hardware remain trusted. The imported caches and compiler were not rebuilt from source or independently authenticated against upstream. Equal endpoint hashes do not rule out a transient modification restored between endpoints. Noncomputable definitions are not evidence for the still-pending oracle presentation theorem. No Python extraction equivalence, external peer review, or historical priority is claimed.

New Lean source and verification tooling retain the open license in `LICENSE`. The archived publication retains its own licensing files.
