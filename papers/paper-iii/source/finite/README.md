# Projector-Resolved Seed Calculus III

**Typed Edge Operators, Connection Defects, and Obstruction Packets**  
**Komorebi P. — Version 1.0.1 (September 3, 2026)**

This release completes the finite algebraic scope of Paper III. It turns
packet-supported edge operators into typed graph walks, separates canonical
coordinate transport from independently chosen connection data, resolves
connection defects and holonomy into packet blocks, and records the exact
boundary between compiled results and future nonlinear extensions.

Within that stated scope, every theorem-like manuscript result is linked to
one or more compiled Lean declarations through the authoritative theorem map.
The release also includes the final PDF, LaTeX source, deterministic
Python-generated figures, a fail-closed kernel audit, and verification
metadata. “Complete” means complete relative to this release contract; it does
not assert novelty, priority, external peer review, or any theorem outside the
explicit hypotheses and finite interfaces in the manuscript.

## Main results

- Target-row/source-column edge operators have the documented execution
  orientation. Noncomposable words vanish, composable words collapse to their
  endpoint block, and finite transfer powers admit exact word and walk sums.
- Endpoint-action and reachability theorems expose the coefficient carried by
  a fixed walk and prove zero output when no compatible walk can reach a
  target packet.
- Exact coordinate transport, composition, and naturality are separated from
  reversible connection data. The latter has additive cocycle defect,
  triangle holonomy, flatness, path transport, and gauge covariance.
- Flat reversible connections are gauge-equivalent to canonical transport at
  the stated finite scope. Holonomy obstruction is exactly reconstructed from
  packet blocks, and a nonzero block supplies a packet witness.
- Arbitrary-length heterogeneous products are handled over one common finite
  packet index, with separately typed two- and three-step variants. The
  manuscript does not claim an arbitrary-length theorem over changing packet
  index types.
- Unary/binary operation trees satisfy input locality, while candidate-specific
  obstruction packets have exactly the logical force stated in the paper.

Colored dependent trees, multilinear packet-labeled tree expansions,
nonlinear Faà di Bruno defect propagation, infinite or analytic convergence,
and physical applications remain explicit roadmap items.

## Contents

- `paper/Projector_Resolved_Seed_Calculus_III.pdf` — final manuscript.
- `paper/Projector_Resolved_Seed_Calculus_III.tex` — complete LaTeX source.
- `paper/figures/` and `paper/scripts/generate_figures.py` — three generated
  figures and their deterministic generator; `paper/requirements.txt` records
  the verified Python rendering dependencies.
- `formalization/lean/` — pinned Lean 4/Mathlib project, authoritative theorem
  map, executable parity gate, and fail-closed kernel audit.
- `provenance/Lean_Completion_Contract.md` — the exact completion denominator,
  trust boundary, and nonclaims.
- `provenance/VERIFICATION_REPORT.md` and `kernel_audit_output.txt` — final
  verification record and captured kernel dependency evidence.
- `RELEASE.json`, `CITATION.cff`, `LICENSE_STATUS.md`, and
  `RELEASE_NOTES.md` — release and citation metadata.

## Verify

From the extracted release root, run:

```bash
./VERIFY.sh
```

That offline integrity pass verifies the complete file set against
`SHA256SUMS.txt`, rejects symbolic links and private build paths, checks the
release metadata against the theorem map and saved kernel audit, and confirms
the recorded PDF and source-artifact hashes.

For a clean proof, figure, and PDF rebuild, install the pinned Lean toolchain,
Mathlib dependencies, Python with Matplotlib, and a pdfTeX/Poppler/Ghostscript
toolchain, then run:

```bash
./VERIFY.sh --full
```

The full mode works in a temporary copy, so it does not modify the extracted
release. Exact commands and verified counts are recorded in
`provenance/VERIFICATION_REPORT.md`.

## Rights

No copyright license has been selected for this release. See
`LICENSE_STATUS.md`; absence of a license is not permission to reuse the work.
