# Komorebi Quadratic-Form Engine manuscript v1.8 final verification

Date: 2026-09-24

## Final editorial state

The main manuscript is method-centered and contains:

- a front results-at-a-glance statement;
- exact central positive, central indefinite, and positive noncentral reductions;
- memory-bounded streamed factor calculus;
- exact and approximate polyphase light cones;
- residual spectral certification and exact completion;
- deep-tail validation through 1e-5000;
- independent characteristic-function inversion near 1e-16;
- directed-rounding positive-tail enclosure;
- a fail-closed accuracy-driven certification theorem;
- explicit input-semantics handling around float64 quantization;
- a compact guarantee/scope table and final conclusion.

## Fresh executable regression pass

The following test files were re-executed from the final source tree:

- test_accuracy_driven.py: 2/2 PASS
- test_interval_kcos.py: 3/3 PASS
- test_noncentral_engine.py: 4/4 PASS
- test_signed_engine.py: 4/4 PASS
- test_residual_completion.py: 3/3 PASS
- test_spectral_tail_bridge.py: 5/5 PASS
- test_approximate_lightcone.py: 5/5 PASS
- test_budget_scheduler.py: 4/4 PASS
- test_residual_trace_cap.py: 5/5 PASS
- test_streaming_skat.py: 6/6 PASS

Total: **41/41 PASS**.

## Deep-tail precision layers retained in the final paper

1. Closed-form / finite exact controls.
2. Independent high-precision characteristic-function inversion on heterogeneous spectra near 1e-16.
3. Directed-rounding interval enclosure with proved support/alias and infinite-mode remainder bounds.
4. Accuracy-driven fail-closed controller that accepts only after the requested multiplicative probability accuracy is proved.

## Important scope boundary

The strongest rigorous probability guarantee begins from an exact supplied positive spectrum of rank greater than two. Arbitrary floating-point matrix-to-spectrum conversion is not yet itself enclosed by verified interval linear algebra. Low-rank mixed-sign forms also remain outside the strongest accuracy-driven guarantee.

## PDF verification

The final PDF compiles without LaTeX warnings, undefined references, or overfull boxes. It is openable, unencrypted, text-based rather than scanned, and consists of 64 pages. All pages were rendered for visual inspection.
