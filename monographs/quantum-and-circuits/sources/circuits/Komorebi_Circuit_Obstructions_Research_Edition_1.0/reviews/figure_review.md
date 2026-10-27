# Scientific figure review

Date: 2026-10-07. Scope: every one of the twelve PDF/PNG pairs in `figures/`, the exact fixture record `reviews/visual_examples.json`, and the corresponding plotting logic in `scripts/make_figures.py`. All twelve PNGs were visually inspected at their native generated resolutions. Every corresponding PDF exists and has one page. This is model-assisted figure QA, not independent human review or a new universal proof check.

**Final verdict: PASS for all twelve figure pairs.** Numerical fixtures and model calculations agree with the source. Three initial label defects were repaired by the author and reinspected. The final PNGs are legible; the corresponding corrected PDF pages were rasterized and checked. The final two table-PDF renders are pixel-identical to their visually reviewed repaired renders after the last suite regeneration. No unresolved stand-alone figure defect remains. No source files were edited by this reviewer.

## Resolved findings

1. **`small_oracle_counts` — fixed.** Initial tiny-segment counts collided with the baseline or each other. They were replaced with exact `n=1: 4 affine` and `n=2: 8 affine + 8 quadratic` annotations, while true bar heights remained unchanged. The first annotation placement collided with the legend; the final annotation at axes y=0.52 is clear of both legend and bars. The final PNG and PDF render pass. Large labels 112 and 128 remain inside their segments; the three-input total is explicitly 256.
2. **`orthogonal_gluing` — fixed.** Diagonal cell labels now match the witness-indexed axes: `delta_00, delta_10, delta_01, delta_11`. Each product is that idempotent, not scalar 1. The final PNG and PDF render pass. The identity matrix in the fixture record encodes the multiplication pattern.
3. **`unsafe_projection` — fixed.** The overlong “x at index 13” row label was shortened to “x (13)” without changing the assignment or bit values. The label now fits its cell. The final PNG and PDF render pass. Initial PDF text extraction had retained the full long label, illustrating why extraction alone did not establish PNG legibility.

## Complete twelve-pair register

| PDF | PNG | Final verdict | Mathematical and visual finding |
|---|---|---|---|
| `figures/cut_transport.pdf` | `figures/cut_transport.png` | PASS | Exact C01 schematic: the lower inverse-suffix path ends at `B=P(x,f(x))`; `H=A+B=fD` and the nonzero output-direction vector are correctly labelled. Fixed zero ancillas are suppressed only inside `P` boundary notation. No clipping. |
| `figures/dirty_and_trace.pdf` | `figures/dirty_and_trace.png` | PASS | All four register values at all four displayed stages agree for both initial target branches. Scratch restores to 0 and target toggles. This is the legal two-Toffoli dirty-workspace example, not the optimal one-Toffoli AND2 oracle; preserve that caption qualification. |
| `figures/packet_coverage.pdf` | `figures/packet_coverage.png` | PASS | All 32 F3 assignments are placed correctly. Eight teal positives with `a=b=1` plus three additional gold positives at `z=(1,1,1)` give 11. The overlap remains teal, consistent with “additional” gold coverage. Bit tuple order is coordinate 1 first. |
| `figures/evaluation_dual.pdf` | `figures/evaluation_dual.png` | PASS | The constant/`a`/`b` vectors at `00,10,01` XOR to the vector at `11`. The AND column shows exactly one positive point. Keep the field convention `F2` in the surrounding text/caption; the displayed plus signs are field sums. |
| `figures/sharing_degree.pdf` | `figures/sharing_degree.png` | PASS | Exact coordinate degrees are `1,2,2,4` after 0–3 Toffolis. The separate two-register product at `t=2` has degree 4 and fits `t+r=4`, while the coordinate bound is 3 there. Red product marker is visually distinct from the coordinate series. |
| `figures/small_oracle_counts.pdf` | `figures/small_oracle_counts.png` | PASS, repaired | Heights and counts are correct: per size `4`; `8+8`; `16+112+128`. Totals are `28,120,128` over 276 functions. Exact annotations for the two small columns are now legible and separate from the legend. |
| `figures/projection_costs.pdf` | `figures/projection_costs.png` | PASS | Both base-two log axes plot the proved exact restored-Toffoli formulas against actual `n=2^m−2`. Equality at `m=2,3` is preserved; strict separation starts at `m=4`. The x axis prevents confusing structural parameter growth with an exponential lower bound in input length. |
| `figures/projection_m10.pdf` | `figures/projection_m10.png` | PASS | Left panel correctly compares exact restored Toffoli costs `17` and `511`; right panel explicitly labels construction total gates `10,237` and `511`. The two panels use different vertical scales and identify their different resources. No claim that `10,237` is the optimum ordinary gate count. |
| `figures/unsafe_projection.pdf` | `figures/unsafe_projection.png` | PASS, repaired | Integer 13 has little-endian bits `(1,0,1,1,0,0)` in labels `1,…,6`. The column XOR is 6, giving `L=(0,1,1)` and `P3=0`; pair `(3,4)` gives `Q3=1`. The short `x (13)` row label and formula are legible. |
| `figures/orthogonal_gluing.pdf` | `figures/orthogonal_gluing.png` | PASS, repaired | Four basis indicators are pairwise orthogonal and each squares to itself. Off-diagonal zeros, diagonal witness indices, and the four-state pattern agree. |
| `figures/witness_fingerprint.pdf` | `figures/witness_fingerprint.png` | PASS | Rows use `(w1,w2,w3)` coordinate order, giving accepting integers `1,2,5,6` and monomials `z1,z2,z1*z3,z2*z3`. All four remain distinct in the formal polynomial despite even accepting parity. The eight-row table is readable and unclipped. |
| `figures/overlap_gf16.pdf` | `figures/overlap_gf16.png` | PASS | At field weight `z=theta`, the intersection comparison is `0` versus `theta`; Boolean-square comparison is `theta` versus `theta²`. Modulus is `theta^4+theta+1`; integer encodings 2 and 4 mean polynomial-basis field elements, not ordinary real/integer magnitudes. |

## Exact fixture reconciliation

The plotting script uses Matplotlib with exact fixture values and vector PDF output; no generated image or sampled curve substitutes for an exact mathematical object. Source checkers are imported without running their full main routines. Formula curves are identified as proved formulas, and the projection fixture explicitly marks that large full truth tables were not enumerated here.

The following bounded scalar reconstructions were performed during QA without invoking the expensive `--all` runner:

- Rebuilt all 32 values of F3 from `(a*b) OR (z1*z2*z3)` and confirmed stored truth table, affine shift, and 11 accepting points.
- Rebuilt all 64 m=3 projection values by scalar column XOR and matching-pair arithmetic. Confirmed 24 unsafe inputs, first index 13, little-endian bits, and `L=(0,1,1)`.
- Reconciled every projection row `m=2,…,10` with `n=2^m−2`, Toffoli formulas `2m−3` and `n/2`, parity-CNOT count `2m(2^{m−1}−1)`, and displayed construction totals.
- Reconciled small-oracle totals and 4,240 target/input cases with the earlier exact calibration audit and frozen source counts.
- Recovered fingerprint support from truth table 102 and verified ordinary formal monomial exponents for all four accepting witnesses.
- Independently multiplied polynomial-basis GF16 elements modulo binary polynomial 19 (`t^4+t+1`), confirming encodings `2*1=2` and `2*2=4`, and all four displayed overlap values.

A PDF text-span/page-bound scan found no span outside its page rectangle. That check does not prove cell-level legibility and did not replace the visual inspection: the unsafe row label and the tiny stacked labels were caught visually. No dense figure relies on color alone for its exact binary entries. The dirty-workspace grids, algebra table, and verifier table display their values in text.

## Caption and model conditions to preserve

The guide must preserve the source's coordinate-first bit ordering, Boolean/F2 arithmetic, and distinction between ordinary `z` variables and Boolean witness reduction. Dirty computation is allowed internally but restored at the boundary. Projection cost figures charge Toffolis separately from CNOTs and identify total costs as construction counts. The algebra figure represents four independent primitive witnesses and is not a general circuit-size lower bound. The GF16 figure distinguishes Boolean `w²=w` from field weight `theta²≠theta`.

This review addresses the stand-alone figure assets. Final placement, scaling, captions, and page-level clipping inside the visual and Lean guides require the guides' own final rendered-page QA.

## Final byte bindings

The following SHA-256 values bind the final reviewed assets. The same records are machine-readable in `reviews/figure_review_hashes.json`. All files were present and every PDF had exactly one page at final inspection. No page-spanning text overflow was detected. These hashes identify this delivered generation, not a promise that PDF metadata will be byte-identical after a later rebuild.

| Figure pair | PDF SHA-256 | PNG SHA-256 |
|---|---|---|
| `cut_transport` | `43b6b2b6d6d0bc071173dbb507cb2da6b7295704e13999026e530243873011ed` | `85fc266b44cf107759f0ec3781fe8a445e856e4ff0aa675a04371680351ec456` |
| `dirty_and_trace` | `426dcc7bddf5a2006503df44c437142f9b2e602a852cf4fbe0cde963fa872404` | `ccd5f90e6b416385953f06f5bfcef3ae20d03182b6ab744910020af72762cf3e` |
| `evaluation_dual` | `e8641e681696498ff7e486902912e3c1fb3df4aaacd4e5d6ddd201d4214e137a` | `97db50dcbf7a66685d3f9334697fb74f737538e9df1ef5cb094aa858e84704d8` |
| `orthogonal_gluing` | `9326cd3634cc843170e4200b52eb8944c37bafb89bddba8dd9ed6039eafa3520` | `f9c2d2d0373c2b75db4a85da83d8ce9bed6117677fb5dd8f709bf3b2ac9d93f1` |
| `overlap_gf16` | `4414ab174883e53c0282d79286e55de385340628c4a60e4464043a29398d852f` | `92fe6b1b3143a33c79861436afd41f9d98cc9f76ef77aca98f24fdd3f801c911` |
| `packet_coverage` | `a32dfe01be08661b932f632c3fcba5a15df0cb7177040a8d9716bc598f5a1ebc` | `eac4836397fb402e664f45fa09a6ee73ae35ed3aae105b6345a41624f076a6ed` |
| `projection_costs` | `7e7cb0a3f57d6a1563a67e0b49205ef1ea50f086786283431f9bef1206e69d39` | `24a12d05a0446e1d3c3962d0d8f3c7856c353e1448817684dd42a584323d6627` |
| `projection_m10` | `9da824a0d77c5e0036919ac6b2c427ba87c9ccaad783ed0bd33ad8079fdf0cb2` | `e56c1c7a05559084991659a1b2e6c0804e2d7925912ebcb6186da16e6504d5f4` |
| `sharing_degree` | `737b3956d90dcd686a149b497a462436e0ddc3b1516149a15e51179504d962c1` | `ff705490587b3991b50163dc36f29ca10bd7522151540b5ef17ff9ce3c5434bd` |
| `small_oracle_counts` | `ff521f109800eef50f8e02cdf16609abce568fd8d1c30fb9a1b286dd611e699a` | `c0bfc2e208c9f4011c457b6a2c0d4f3cb7f980d5b127a3b067b4e59a2afbc3bd` |
| `unsafe_projection` | `ce9542f7b01ff5dbf1045d4912755fb6560463716f5cae6054bc02daf43a7551` | `3a3329346f7304eb1094cc2b012bfe5a8e1d63b820c38ecb8b882c6e37a330da` |
| `witness_fingerprint` | `363b884048881099278b34bd8f0dea15a96d9558159c2dbbd2da9fb3b3bf920a` | `108c76eddda9b51e50b64bb523d10bb50be3e1e171dae30e8ce06c9f138aff2e` |

Final generator `scripts/make_figures.py`: `da13c8dc493bd288d15d7af5299bce0349c2f56cc7ec92a8e6cdae1b89c28e24`.

Final exact fixture record `reviews/visual_examples.json`: `00e1ebf777814efb115753477ed9c76baa2b2fa3c2a4b86f7e8fe2d8563ab613`.
