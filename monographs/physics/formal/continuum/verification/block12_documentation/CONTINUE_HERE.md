# Continue from Komorebi Physics Lean v0.12.0 — Block 12

Read `AGENTS.md`, `STATUS.md`, `docs/BLOCK_12_PROOF_GUIDE.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and the completed verification report. Treat only an actual PASS as a checked checkpoint.

## Checkpoint contract

1,083 theorem declarations, 1,296 inventoried names, 65 mathematical modules and 87 invalid controls. Preserve all 65 mathematical files in a new block12 preservation layer before extending. The 58 Block 11 mathematical files remain byte-identical. Counts are not independent discoveries or a full-edition completion percentage.

Runtime used: `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`. Runtime bytes remain external; seven-part checksum restoration support is included. Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 are pinned.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker and warnings as errors. Preserve failed snapshots. No admissions, custom axioms, native evaluation or kernel bypass. All proof-bearing definitions and aliases belong in the axiom audit. Imported caches are reused, not rebuilt wholesale.

## Immediate next target

Section 6.6, equations (6.48)–(6.52), physical PDF page 33. For a positive modulus M, construct the finite character projector for the number spectrum n, prove its exact equality to the infinite mask {n | n mod M=r}, and prove lowering/raising routing on actual weighted domains. The harmonic generator spectrum n+1/2 differs from the number spectrum n; do not silently interchange their phase factors. Keep the sign of the character phase and the ladder orientation explicit. Lowering at n=0 and all unbounded domain/range obligations need real proofs. Preserve source square-root amplitudes.

The current `SpectralCells.mask`, `mask_apply`, domain mask and graph facts provide the infinite cell. `BoundedSpectral` supplies actual bounded complex multipliers. The finite character sum can be proved coordinatewise, but the ladder maps require domain constructions, not formal matrix names or arbitrary everywhere-defined bounded operators.

## New machinery

`InfiniteCells`: arbitrary strong subcells, bounded projector constructor, intersection/disjoint/complement laws, actual energy HasSum and a strong coarse atlas.
`ClosedCellDomains`: finite domain-valued subcell sums, actual closed-graph limit pair, derived domain preservation/action HasSum, graph convergence and graph-compatible coarse atlas. `coarsenOfPreserves` permits independent domain proofs.
`InfiniteCellCurrents`: source-cell row HasSum via symmetry, receiving-cell outer HasSum, separately justified reverse iteration, actual derivative of infinite-cell energy. Joint-product current/amplitude HasSum explicitly requires joint summability.
`SpectralCells`: indicator coordinate formula, maximal-domain preservation, graph contraction/weighted sums, commutation with evolution, spectral zero currents and constructed-solution coarse derivatives for graph-compatible general atlases.
`InfiniteCellAlgebra`: support/fixed-point criteria, coarsening composition and self-adjoint-involution transport.
`InfiniteCoarseExamples`: rational first-two-mode reflection, unchanged tail, arbitrary spectral-domain preservation, infinite even/odd cells, true normalized harmonic orbit. Even probability337/625; receiving-even current and actual derivative288/625 at zero. Both fine-cell iterated sums and actual coarse quantities agree.
`CurrentSummationExamples`: disjoint triangle cycles on N×Fin3. Rows/columns finite, both iterated sums exist and equal zero, joint array is not summable. Abstract counterexample, not a Hamiltonian realization.

## Boundaries and release protocol

Do not treat current-row absolute summability as absolute summability of a whole double array. Coarse-domain preservation is an explicit theorem or hypothesis, not a consequence of strong state convergence alone. Closedness plus graph compatibility are sufficient, not a claimed necessary characterization. The infinite coarse constructions use complete complex Hilbert spaces and unconditional finite-subset sums.

General Stone/spectral representation, differential oscillator equivalence, form domains, residue/ladder routing, compact/Hilbert–Schmidt reconstruction, higher graph derivatives, heat time derivatives, countable dilation, instrument updates, entropy endpoints, nonlinear/dissipative existence and later gravity/cosmology remain separate. Chapter 3 still lacks a complete independent inventory. No physical empirical validation is claimed.

Update `dev_check.py` to the next block. Extend the inventory, aggregate and Audit.lean; add preservation and controls without weakening existing tests. Update source map, claim ledger, roadmap, guide, failure records and status. Run the complete cumulative verifier, package only after a stable PASS, then repeat the full audit from a fresh ZIP extraction and deliver its external receipt.

One-line continuation prompt: Open CONTINUE_HERE.md from Komorebi_Physics_Lean_v0.12.0_Checked_Block_12.zip, verify the 1,083-theorem/1,296-name checkpoint, preserve all 65 mathematical modules, and formalize Section 6.6 finite-character residue projections and actual domain-correct ladder routing; retain every convergence, domain and empirical boundary.
