# Komorebi Information Realization · v0.3.0

**Access-aware packet repair, exact transfer leakage, and predictive closure.**

This release connects the preceding finite information theory to the actual Haar packet implementation in Komorebi Math. It includes constructive optimal repairs, impossibility witnesses, an explicit reduced dynamical system, and counterexamples that delineate the claims.

## Read first

- `THEORY.md`: general definitions and proofs.
- `WORKED_EXAMPLES.md`: worked Haar shift, predictive closure, horizon cancellation, encoder-access penalty, and energy/information examples.
- `AUDIT_REPORT.md`: coverage, failures, assumptions, and verification limits.
- `PROGRESS_LEDGER.md`: completed obligations and next restart point.
- `VERIFICATION_SUMMARY.json`: machine-readable test completion and environment.
- `PROVENANCE.json`: exact source lineage and hashes.

The unchanged preceding package lives in `prior_v0_2/`, including all original examples, proofs, figures, code, and logs. The actual upstream wheel is retained under `vendor/`. It is read through Python zipimport, not installed or modified. No network access is required to run the delivered code.

## Run

Use Python 3.10 or later. The new exact core needs only the standard library. The pinned Haar integration requires NumPy. Plot regeneration additionally requires matplotlib. This release was executed with Python 3.13.5 and NumPy 2.3.5 on Linux.

From the extracted directory:

```text
python verify_manifest.py
python examples/worked_examples_v03.py
python tests/run_v03.py --suite all
python -O tests/run_v03.py --suite all
python tests/replay_v02.py --suite all
```

Individual new suite names are `graph`, `linear_access`, `transfer_closure`, `library`, and `boundaries`. Running reports again overwrites their generated report files. Consequently a manifest made at delivery will no longer match changed execution timestamps; verify the pristine package first.

To regenerate the two charts:

```text
python examples/make_figures.py
```

The CLI files resolve paths relative to their own location and can also be invoked from another working directory. On Windows PowerShell, `python` may be replaced by the desired interpreter such as `py -3.13`. No Windows run is claimed in the evidence.

## Main result

For a full finite-field state space and linear observation R, task F, and helper access U, an exact helper-only repair is possible precisely when

`ker(R) intersect ker(U) is contained in ker(F)`.

When possible, exactly `d = rank([R;F]) - rank(R)` coded field coordinates suffice. The construction achieves the minimum alphabet `q**d`, even among nonlinear encoders. Otherwise it returns two indistinguishable states requiring different answers.

In the Haar shift example, two hidden detail coordinates influence the next coarse output through one combination. One coded coordinate is sufficient for every future coarse output, while a full source reconstruction would need two. The distinction is between source information and task-relevant predictive information.

## Boundaries

This is a finite, single-encoder, single-decoder result. Implemented fields are prime fields. The native floating Haar code is not claimed to implement exact finite-field arithmetic. Its relevant source file matches the GitHub file read in this continuation, but the entire repository has not been audited. The energy objective in the native library is not equated with task entropy.

The new suites and examples pass in normal and optimized Python. All seven v0.2 suites were newly replayed in normal mode. Theorems have written proofs, not compiled Lean proofs. No universal-information, quantum-information, physical-noise-robustness, or novelty claim is made.

## Contents and attribution

New modules: `src/packet_information.py`, `src/access_graph.py`, `src/komorebi_adapter.py`. The upstream wheel is preserved with its existing package metadata. No new license terms are assigned to upstream material. Sources and related coding literature are identified in the theory and provenance files. No remote repository was changed.
