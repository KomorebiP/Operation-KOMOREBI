# Final-edition validation

**Komorebi P. · Quadratic-Form Engine / K-COS · October 7, 2026**

The publication set is complete for the scope stated below. This report distinguishes proofs, bounded numerical evidence, and machine-checked formal statements. None of these categories substitutes for the others.

## Publication set

| Companion | Pages | Included editable material | Final review |
|---|---:|---|---|
| Traditional manuscript | 85 | Full TeX and Markdown; 55 theorem, lemma, proposition or corollary statements; 31 figure displays; originals retained separately | All pages inspected; no unresolved finding |
| Visual guide | 18 | TeX, Markdown, Python generators; 17 reproducible illustrations and finite controls | All pages inspected; no unresolved finding |
| Lean guide | 7 | TeX, Markdown, pinned Lean project, declaration inventory and verification scripts | All pages inspected; no unresolved finding |

The original three-pass TeX builds and structural PDF checks were clean, but the original contact-sheet review missed collisions within figures. The subsequent full-resolution layout correction is documented in `VISUAL_LAYOUT_CORRECTIONS.md`, with revised page counts and independent checks. Historical publication-review evidence is retained with its limitation stated. The original 39 Markdown files from the v1.9 archive are retained byte-for-byte under `engine/`; those historical documents do not supersede the canonical companions.

## Mathematical audit and scope corrections

The traditional manuscript preserves the full engine proof development and integrates the centered spectral-packet theory. Audits made the domain and implementation hypotheses explicit: orthonormal QR complements; phase-aligned storage and a known exact phase graph; positive-support COS conditions; nonempty packets, integer expansion order and a specified analytic logarithm branch; and workspace accounting that includes the tile output. Composition of the layers does not assert pairwise commutativity of every operator.

The positive interval backend requires positive spectral coefficients, rank greater than two, a nonnegative threshold, an admissible positive tilt and a support endpoint above the threshold. The current automatic planner handles upper-tail queries above the mean. The dense spectral bridge regards each stored binary64 factor entry as an exact dyadic input. It does not enclose an unknown pre-rounding matrix.

Signed/noncentral and packetized floating implementations carry analytical error ledgers and bounded empirical validation; they are not end-to-end directed machine certificates. The large-scale streaming implementation is also not connected to a complete directed matrix-to-tail certificate. See `audits/CLAIM_AUDIT.md` for the original findings and `audits/STAGED_CORRECTION_AUDIT.md` for the corrected implementation review.

## Fresh numerical evidence

**58 selected unittest methods passed:** 48 production tests and 10 directed-contract regressions. A method can contain multiple assertions or subcases; 58 is the test-method count, not an assertion count. The groups cover streaming and structural identities, residual bounds, realistic finite models, signed/noncentral controls, interval COS, accuracy acceptance, verified spectra and directed serialization.

The fresh controls additionally include:

| Control | Requested relative accuracy | Directed ratio upper bound | Evidence |
|---|---:|---:|---|
| Exact-spectrum `0.02 χ²₈₀`, tail near `10^-5000` | `10^-18` | Less than `9.202 × 10^-20` | Independent finite Erlang log interval fully contained in the returned interval |
| Dense 64×64 exact-binary64 Hadamard factor, tail near `10^-16` | `10^-12` | Less than `2.783 × 10^-15` | All 64 known exact eigenvalues enclosed, followed by directed tail acceptance |

These displayed bounds round upward. Complete literal inputs and outputs are recorded in `numerical/recorded_runs/fresh_controls_final/controls.json`. The full report, environment, resource contracts, replay scripts and raw outputs are under `numerical/`.

The audit found and corrected four consequential implementation gaps:

1. Ambient point precision could collapse a narrow log interval to zero width. Endpoint parsing now preserves the input literals in directed arithmetic.
2. A point `expm1` and a rounded requested tolerance could authorize acceptance. Acceptance now compares the directed ratio upper endpoint to the exact-tolerance lower endpoint.
3. Nearest decimal formatting could serialize an endpoint inward. Exact binary interval tuples now produce outward decimal strings using integer rational conversion and directed Decimal rounding.
4. Negative thresholds could enter a positive-support cosine contract and produce an invalid positive log-probability enclosure. Domain validation now rejects unsupported inputs.

A final nonfinite-only serializer amendment handles both signed infinity tuple markers and rejects NaN. The 10 directed tests were rerun on the exact final source. Production groups and the two fresh finite controls ran immediately before that amendment, after all finite-path repairs; their finite code paths are identical. Their original execution hashes remain intact. `numerical/FINAL_SOURCE_PROVENANCE.json` documents this distinction rather than relabeling older executions.

The directed implementation claim is conditional on the recorded arithmetic trust base, including mpmath 1.3.0 interval operations and transcendental evaluations, its exact binary tuple representation, Python integers and directed Decimal serialization. The shared mpmath interval precision requires sequential calls. Floating summary fields are display values; outward literal interval endpoints carry the enclosure. This is bounded validation of the named implementation, not a proof of every possible input or every numerical library operation.

## Lean verification

**26 project theorems and 8 definitions passed**, with 34 declarations covered by the axiom audit. A fresh build and fresh direct source checks all exited successfully. The successful build's 1002 jobs include dependencies and are not a theorem count. The positive arithmetic control was accepted without axioms. False arithmetic and an error-budget proof missing its acceptance premise were both rejected.

The axiom union is exactly a subset of `propext`, `Classical.choice` and `Quot.sound`; there is no `sorryAx`, custom axiom or admitted project proof. Initial compiler failures are preserved alongside the successful logs. The project pins Lean `v4.34.0-rc2` and mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Runtime acquisition and the producing environment's narrow executable-location adapter are disclosed in `../lean/verification/runtime/`; official compiler and shared kernel-library hashes were checked.

Formal coverage consists of exact finite Gram identities, disjoint refinement and reindexing, streamed-action equivalence, quadratic energy and nonnegativity, coefficient order and its pointwise tail implication, and arithmetic consequences of supplied enclosures and error budgets. It does not establish Gaussian probability laws, eigenvalue enclosure algorithms, COS inversion or analytic remainders, or numerical interval-library correctness. Exact declarations and remaining obligations are in the Lean companion and its inventory. `../lean/verification/BUILD_AUDIT.json` is the authoritative build record.

## Reproduction and provenance

From the extracted release root, install `requirements-engine.txt` for numerical replay and follow `numerical/README.md`. For example:

```bash
python3 verification/numerical/replay.py --group directed_contract
```

The exact final directed-contract replay passed 10/10. Lean reproduction is documented in `../lean/README.md` and implemented by `../lean/verify.py`; dependency and compiler caches are deliberately excluded. Rebuild the three publication PDFs using:

```bash
python3 build_release.py
```

The original engine and packet source ZIPs are preserved under `../provenance/`. The bounded primary-source attribution check is recorded there in `LITERATURE_CHECK.md`; it is not an exhaustive novelty search. `../SOURCE_MANIFEST.json` lists SHA-256 hashes and byte counts for every packaged file. The packaging script verifies ZIP CRCs, unique member names and every manifest member hash.
