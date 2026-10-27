# v0.8 verification

## Cumulative regression suite
- `test_streaming_skat.py`: 6/6 PASS
- `test_formal_v02.py`: PASS
- `test_approximate_lightcone.py`: 5/5 PASS
- `test_budget_scheduler.py`: 4/4 PASS
- `test_spectral_tail_bridge.py`: 5/5 PASS
- `test_residual_trace_cap.py`: 5/5 PASS
- `test_residual_completion.py`: 3/3 PASS

## Trace/moment MGF audit
- random factor/range cases: 120
- admissible tilts per case: 4
- total comparisons: 480
- trace/cap envelope dominates exact log MGF: True
- trace-Frobenius-cap envelope dominates exact log MGF: True
- trace-Frobenius-cap no looser than trace/cap in 83.54% of comparisons
- median trace/cap slack: 0.00449915
- median trace-Frobenius-cap slack: 0.00352631

## Deep-tail stress test at p=1e-8
- depth 4: v0.7 Weyl 90097.490 decades -> v0.8 moments 11.855 decades (7599.7x narrower)
- depth 5: v0.7 Weyl 16511.194 decades -> v0.8 moments 9.757 decades (1692.3x narrower)
- depth 6: v0.7 Weyl 3747.457 decades -> v0.8 moments 7.668 decades (488.7x narrower)
- depth 7: v0.7 Weyl 2274.835 decades -> v0.8 moments 5.697 decades (399.3x narrower)
- depth 8: v0.7 Weyl 1165.288 decades -> v0.8 moments 3.391 decades (343.6x narrower)

All v0.8 trace/moment intervals contained the full-spectrum K-COS reference: True.

## Residual completion
- moment rank bracket valid at every tested depth: True
- rank exactly certified by moment lower bound plus orthogonal-complement upper bound in 6/7 tested depths
- maximum completed-spectrum relative error: 5.936e-16
- maximum completed-tail error at p=1e-8: 9.770e-15 decades
- depth 8: basis dimension 48, residual rank certified as 2, completion returns full dimension 50

## PDF verification
- pages: 40
- compiled twice with pdfLaTeX
- no undefined references or overfull boxes in the final pass
- rendered at 160 dpi and the new v0.8 pages visually inspected
- PyMuPDF preflight: openable, unencrypted, text-native

## Claim boundary
The exact algebraic identities and inequalities are proved. Performance comparisons are finite numerical evidence only. The moment certificate is intentionally conservative; exact streamed residual completion is the preferred terminal path once the missing rank is affordable.
