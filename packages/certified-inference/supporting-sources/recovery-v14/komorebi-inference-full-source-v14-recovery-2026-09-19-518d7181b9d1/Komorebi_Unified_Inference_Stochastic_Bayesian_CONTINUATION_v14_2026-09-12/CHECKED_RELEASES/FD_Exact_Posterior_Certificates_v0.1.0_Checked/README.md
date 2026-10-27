# Exact rational posterior certificates

This release connects an executable rational checker to the existing
finite-dimensional Gaussian posterior Wasserstein bound. It also proves a
validity-preserving, non-increasing-score candidate acceptance policy.

See PROOF_NOTE.md for the full model, theorem hypotheses and non-claims.
Use FINAL_VERIFICATION_RECEIPT.json for the actual recorded verification status.

## Exact numerical evaluation

The producer uses Python 3.10+ standard libraries only. SymPy is needed only for
the independent diagnostic suite.

```bash
python checks/exact_certificate.py examples/GeneratedExactRotated.json \
  --output results/rotated.json \
  --emit-lean Komorebi/GeneratedExactRotated.lean \
  --namespace GeneratedExactRotated
python checks/test_exact_certificate.py
```

Integers and strings such as "3/8" or "0.125" are exact rationals. JSON floating-point
numbers are rejected. Upper bounds may be conservative, but the checker verifies
them against exact recomputation. The model is factor-coded: P=L L^T and
R=N N^T+sigma I. It is not silently identified with uncertain physical data.

A Python success is provisional arithmetic evidence, not formal verification.
The exported Lean module contains the concrete model and checked proof instance.
Its successful compilation is the formal certificate. Concrete decisions use
`decide +kernel` (kernel reduction), not native evaluation.

## Pinned Lean verification

Restore the portable runtime described by the full continuation archive. It pins
Lean 4.34.0-rc2 and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
The runtime is Linux x86_64, including compatible WSL2, not native Windows.

```bash
python verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --clean --modules --timeout 40
```

The empty --modules list above clears only project outputs. Then check modules in
MODULE_ORDER.json order. Each invocation below runs one bounded Lean process:

```bash
python verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --modules RationalMatrixCertificates --timeout 40
```

All dependencies of a selected module must already be checked. For a full
sequential build from a normal terminal, omit `--modules` entirely:

```bash
python verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --clean --timeout 40
```

In a tool with an outer execution limit, use separate calls for one or a few modules
in the recorded order instead of putting the entire build in one tool call.

 The source verifier
records exact commands, source snapshots and hashes, compiled-output hashes,
direct dependencies, exit status and timeouts. Each module uses one Lean thread
and treats warnings as errors. Permit the surrounding shell/tool enough time for
the verifier to preserve the receipt after a timeout.

The input-size guards are not proof-compilation performance guarantees. Large
exact inputs can exceed the resource cap. Such a run is not counted as checked.

## Main declarations

- checkCandidate_eq_true
- exactCandidate_valid
- checked_score_bounds_posterior
- checked_tolerance_bounds_posterior
- acceptCandidate_valid
- acceptCandidate_score_le
- selectCandidates_valid
- selectCandidates_score_le
- selected_batch_bounds_posterior
- selected_batch_preserves_posterior_tolerance

Every retained checked source is byte-identical to the v6 source. Final audit files
identify which dependencies were freshly recompiled. Historical continuous-time
and other unrelated programs are not claimed to have been rebuilt here.
