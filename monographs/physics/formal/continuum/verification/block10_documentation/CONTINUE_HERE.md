# Continue Komorebi Physics Lean v0.10.0

Read AGENTS.md, README.md, STATUS.md, docs/BLOCK_10_PROOF_GUIDE.md, docs/BLOCK_10_DECLARATION_INDEX.md, docs/SOURCE_MAP.md, docs/CLAIM_LEDGER.json, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and the completed verification/final/report.json. Inspect actual source pages/images when needed.

## Verified checkpoint contract

896 theorem declarations, 1,084 inventoried names, 52 mathematical modules and 73 invalid controls. Check the current completed report before calling it checked. The previous 47 mathematical files are byte-identical. Preserve all 52 mathematical files in a new block10 preservation layer before extension.

The exact runtime used here was `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`. It is not bundled. Seven-part checksum restoration support remains included.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker, warnings as errors and bounded command windows. Preserve every failed attempt separately. No admissions, custom axioms, native evaluation or disabled kernel checks. Reuse pinned imported caches explicitly rather than claiming a full dependency rebuild.

## Immediate next target

Section 6.4 (6.26): the actual diagonal phase evolution. `HarmonicSurrogates.phaseSymbol eig t` already constructs exp(-i t eig_n), and its operators have group law, inverse and norm preservation. Prove strong continuity in TIME, invariance of the maximal weighted-l2 domain, and the actual ambient derivative for domain initial states. Do not confuse already proved strong convergence in CUTOFF with strong continuity in TIME. Then specialize the prior countable energy/current theorems to this constructed flow rather than supplying their derivative hypothesis.

A likely route is approximation by finite-support vectors for strong time continuity, bounded unit-modulus multiplication on the weighted domain for domain invariance, and a square-summable domination argument for difference quotients on D(H). Distinguish graph continuity from ambient differentiability and retain the maximal domain. Do not label a pointwise coordinate derivative as a proved l2 derivative.

## Block 10 machinery to reuse

BoundedSpectral: actual bounded sequence multiplication on l2, exact sup/operator norm, adjoints, products and differences.
SpectralTruncation: cutoff and fixed anchor operators, literal sandwich formula, strong convergence on each state, exact tail supremum, and norm convergence iff the scalar sequence tends to the anchor.
HarmonicSurrogates: actual harmonic resolvent for every real eta (spectral gap makes eta=0 valid here), domain range and both inverse identities; t>=0 heat construction, t>0 decay; arbitrary real-spectrum phase family and algebraic laws; old coordinate-cutoff bridge.
AnchoredSurrogates: bounded/Cayley symbols tend to one, true regularizer-domain compositions, correct anchored errors, zero-padded errors equal to one.
SpectralErrorBounds: exact harmonic endpoints and rates, heat-at-zero/backward-time boundaries, wrong-anchor rejection, nonzero 2/21 error witness and exact phase action on every tail basis vector.

## Open boundaries remain

The constructed harmonic realization is not yet identified with the differential oscillator on L2(R). A general Borel functional calculus and Stone theorem are not proved here. D(H^(1/2)) hierarchy (6.12), Section 6.5 infinite coarse domains and controlled current regrouping, residue/ladder routing, countable dilation, measurement instruments, entropy endpoints and later continuum/gravity/cosmology remain separate. Per-row absolute current summability is not whole-double-array summability.

## Release protocol

Use scripts/dev_check.py with its output directory updated to the new block. Extend the inventory including proof-bearing definitions and abbreviations. Update the aggregate, Audit.lean, verifier controls/preservation, source map, ledger, guide and failure records. Final production audit must complete PASS; package only with stable proof-input hashes; rerun the entire verifier from a fresh archive extraction and deliver its external receipt.

One-line restoration prompt: Open CONTINUE_HERE.md from Komorebi_Physics_Lean_v0.10.0_Checked_Block_10.zip, verify the 896-theorem/1,084-name checkpoint, preserve all 52 mathematical modules, and prove the constructed spectral phase family's strong time continuity, maximal-domain invariance and actual l2 Schrödinger derivative without substituting coordinatewise differentiation or cutoff convergence for those obligations.
