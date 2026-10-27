# Final companion validation

**Komorebi P. · October 7, 2026**

This record distinguishes scoped ordinary proofs, fresh Lean checks, finite computations, historical evidence, and publication review. It does not certify the original gamma/class-field equality.

## Mathematical verdict

The read-first proof audit covered 24 obligations. The complete ceiling divisor, unsigned cubic growth, the restricted fixed-affine finite-theta obstruction, absolute genus-three regularization, fourth-log reconstruction, reflection coefficient, period-one coefficient and special-cube formula pass within their stated hypotheses. The exact remaining arithmetic assertion is `Im(C_pol U_Gamma^3)=0`. Scalar-plane divisor cancellation does not supply torus descent or principal-norm compatibility.

The finite-theta theorem was restricted to finite polynomial expressions in fixed affine theta restrictions and derivatives, with one global nowhere-zero entire factor. Arbitrary unrelated exponential prefactors inside sums invalidate the quadratic divisor bound: `1+exp(z^3)` is a counterexample. The final manuscript makes the positive-definite imaginary-part hypothesis explicit. Original checkpoint wording is preserved as history.

Primary-source review authenticates nine external application leaves on the stated editions, including the proved modulus theorem on the Bergeron–Charollois–García authors' copy, full inertia-invariant Artin factors, class-number normalization, sigma–theta constants, and the theta/Jensen and sine partial-fraction inputs. The exact arXiv-v2 artifact could not be acquired and is not authenticated by implication. Inherited field, ray-field, algebraic-unit and branch certificates are not relabeled as fresh end-to-end arithmetic replay. The literature report records exact locators and failed acquisition attempts.

Evidence: `audits/FRESH_PROOF_AUDIT.{md,json}`, `../provenance/LITERATURE_CHECK.{md,json}`.

## Formal verification

The selected canonical formal source has 42 modules and 453 distinct theorem names; repeated same-name sources were byte-identical. Every module compiled freshly. The completed scope is 438 accepted module-scoped theorem audits, eight focused CM-norm audits, and seven PhaseRegulator audits appended to an authenticated exact source prefix. The audits have disjoint name sets whose union covers all 453 selected names. The current v0.14 core independently passes all 25 theorem audits, including 11 new family/coefficient theorems and 14 inherited statements.

The pinned runtime is Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Warnings are errors. Transitive axiom dependencies are limited to `propext`, `Classical.choice`, and `Quot.sound`; no `sorryAx` or custom axioms are accepted. Positive controls pass and deliberately false arithmetic controls are rejected.

Initial 1.5 GiB compilation hit actual heap limits in three inherited modules. At 3 GiB all 42 modules compiled, but the aggregate import and aggregate axiom auditor still hit the heap limit. The module-scoped replay additionally encountered a 120-second CM-norm timeout and a PhaseRegulator import-auditor heap limit. Focused retries resolved those two module-level gaps: the unchanged CM-norm module passed under a documented 300-second cap; PhaseRegulator passed through exact-source-prefix replay with only check/axiom-report commands appended. All failed attempts, resource records, diagnostics and prefix hashes are retained. The combined import remains incomplete under the tested cap.

This finite and conditional formal scope does not formalize the complex divisor interpretation, infinite analytic counting, canonical-product convergence, arithmetic gamma identification, or all ordinary proofs in the traditional manuscript. Exact theorem types and hypotheses are in the Lean guide and declaration inventory.

Evidence: `../lean/verification/`, the Lean replay ledger, and its guide.

## Finite exact and floating checks

| Fresh check | Tested scope | Outcome |
|---|---|---|
| Current integer checker | 20 named assertions; five negative controls; 2,197 lift triples; 92,480 family points for n=1…16 | PASS |
| Current numerical replay | Four identities, one quadratic-jet diagnostic, three negative controls at each requested precision 40/70; actual working precision 65/95 | PASS |
| Independent finite extension | Nine named checks; four negative controls; 4,913 triples; 15,125 family points; 135 complex positions; three exact polynomial samples | PASS |
| Independent floating extension | 15 identities at two new points; actual working precision 80, series design precision 50 | PASS |
| Independent plotted data | All 175 plotted n=2/3 coordinates, lifts and family counts recomputed independently | PASS |

Current floating maximum identity residuals are about `1.9204e-62` and `1.2792e-92`; the independent extension maximum is about `2.1231e-72`. These are observed regression residuals, not certified error intervals. The fixed-step quadratic-jet residual is about `3.9284e-11`; finite-difference truncation makes it a diagnostic. No numerical evaluation or enclosure of the entire infinite divisor product is claimed.

The independent extension first reached the inherited ±12 sigma-shift guard at `beta*(1.173+0.013i)`, then reached the 20,000-term cap at `F(0.307-0.009i)` when its initial representative predicted 41,634 terms. Both failures were reproduced and retained. A bounded independent wrapper follows the unchanged sigma-shift law and centers the representative. The successful run retains ±40 shifts and the 20,000-term cap; actual shifts were −4…20 and the largest cutoff was 3,719. Three overlap comparisons pass, including a point whose representative actually changes. The wrapper is not an unrestricted evaluator or an infinite-product certificate.

Evidence and complete commands, input hashes, precision and resource bounds: `numerical/` and `runs/independent_visual_final_freeze/`.

## Source integrity and provenance

All 738 protected intake files remain byte-identical to `../provenance/SOURCE_INTAKE_MANIFEST.json`. Seventeen archived manifests authenticate 709 recorded output hashes. Eleven historical receipts authenticate 68 explicit file hashes; four additional v0.2 receipt output hashes match no preserved payload and are explicitly **UNVERIFIED**. The present archive payloads match their own manifest. Missing old receipt payloads do not authenticate a run or invalidate fresh current runs.

The assembler compares 384 proper mathematical spans across its theta, Stark and polarization source-to-Markdown conversions, after declared notation namespacing. That is a scoped conversion check, not a byte-identity claim for the whole authored paper. Principal and reconstruction equations were manually typeset and independently compared against v0.13/v0.14; their final formula and proof-step audit passes. Publication notation, citations and relocated cross-references are reviewed separately.

The first citation conversion collided with the mathematical notation `E_t[2]`. The token guard rejected it before publication. Protecting mathematical spans before prose transformations corrected the converter. The reports retain this failure and its scope. Historical directed phase/branch evidence was integrity-checked; it was not freshly replayed numerically.

## Publication and packaging

All 72 final PDF pages pass individual native inspection at 150 dpi: 43 traditional, 19 visual, and 10 Lean. Publication page coverage and final artifact hashes are recorded in the final publication reports and `RELEASE_CHECK.json`. Eighteen native Python figures are reviewed individually; the genuine three-dimensional chamber is retained. Overflowing labels in figures 00 and 17 were corrected, and figure 17 received additional title/detail separation. The 3D and complex-plane maps were enlarged within the guide for legibility. Scientific finite control data did not change through those display edits. A traditional-paper figure that interrupted “For completeness” was moved after the complete paragraph; the repaired page was re-inspected, and the other 42 final pages are pixel-identical to the individually reviewed baseline. Archive CRC, member-set, manifest and exact-byte round-trip checks have separate receipts outside the archive, avoiding self-referential hashes.

| Final document | Pages | Independent native review |
|---|---:|---|
| Traditional manuscript | 43 | PASS |
| Python visual guide | 19 | PASS |
| Lean companion | 10 | PASS |

The source archive includes editable TeX/Markdown, Python generators and bounded replay runners, the selected Lean project, original source ZIPs, retained failure records and scoped audits. Dependency/runtime caches are excluded. Packaging writes a temporary ZIP, checks every CRC and manifest hash, then atomically installs the archive. The delivered saved ZIP is additionally checked after an exact-byte round trip. That round-trip receipt is kept outside the archive to avoid a self-referential hash.
