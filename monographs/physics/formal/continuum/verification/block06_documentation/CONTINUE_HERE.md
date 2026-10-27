# Continue Komorebi Physics Lean v0.6.0

Read AGENTS.md, README.md, STATUS.md, docs/BLOCK_06_PROOF_GUIDE.md, docs/SOURCE_MAP.md, docs/CLAIM_LEDGER.json, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and verification/final/report.json before editing. Read the complete relevant source pages, including page images where notation is ambiguous.

## Restore and verify

The checkpoint inventory is 483 theorem declarations, 579 named declarations, 29 mathematical modules and 41 deliberately invalid controls. Only a completed PASS audit confirms this checkpoint. Use the included runtime_restore_support/assemble.py with all seven checksum-matching portable runtime parts, or an already restored exact-pin kit. One actual production path was /mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2; a fresh container may differ.

Lean is 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Do not silently upgrade or replace the pinned dependencies. Restoration is local assembly/extraction, not remote dependency fetching.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker and bounded per-module runs. Imported caches are reused, not independently rebuilt wholesale. Recompile all local modules before claiming new verification. Timeouts, import errors and missing files are not proofs. Keep failed source snapshots and receipts separate from active proofs.

## Preserve the checkpoint

Copy the package into the next release version. Preserve all 29 mathematical source files byte-for-byte and make a new SHA-256 map. Snapshot current documentation and inventory before edits. Retain all earlier provenance, failures, successful logs, source manuscript and source map. Explicitly document any necessary repair to older mathematics.

All named declarations, including proof-bearing definitions, must be axiom-audited. No sorry/admit, custom axiom, unsafe/native proof escape or disabled kernel checking. Permitted axiom dependencies are propext, Classical.choice and Quot.sound. Update aggregate, declaration inventory, audit commands, cumulative verifier and negative controls together. Definitions and computations are not counted as new theorem declarations.

## Immediate source: Chapter 5.1–5.3

Physical PDF pages 27–28 (printed 14–15), positive-operator and overlapping atlases, equations (5.1)–(5.21). Page 28's rendered source was read. A previous Files page-image read could not supply page 27's image; parsed text is available, and the original PDF is included for rendering if needed.

The effects satisfy F_i=F_i*, F_i>=0, sum_i F_i=I. They need not be idempotent or pairwise orthogonal. The probability is Re<psi,F_i psi>, with reality proved. It is not generally ||F_i psi||^2. Construct the effect atlas with only its actual laws, then derive positivity, normalization and its continuity equation from the original vector derivative.

For the source current

J_ij = Re<F_i psi,A F_j psi> - Re<F_j psi,A F_i psi>,

prove antisymmetry and the row sum; derive the actual probability derivative for skew A. Do not assume the balance law in the atlas structure.

For differentiable moving effects, derive the complete derivative p_i'=s_i+sum_j J_ij, where s_i=Re<psi,F_i' psi>. Differentiate the partition law to obtain sum_i s_i=0. The transported case is F_i(t)=U(t)F_i(0)U(t)* with K=dot U U*: page 28's image confirms the dot on the first U. Derive F_i'=[K,F_i] using the actual unitary derivative, rather than assuming that formula.

Coarsening must use genuine address-map incidence (each fine effect assigned once); derive coarse positivity/completeness and actual probability, source and current aggregation. A weighted extension requires separately stated weight hypotheses. Do not confuse overlapping effects with overlapping aggregation weights that double-count the identity.

Chapter 5.4, equations (5.22)–(5.32), is the following target: Parseval-channel realization and dilation. Show actual synthesis/analysis identities and block reconstruction, not merely symbols for a dilation. Choose finite matrices or bounded Hilbert operators explicitly and preserve domain limits.

## Boundaries inherited from Block 06

The refinement theorem starts from an actual finite expansion of the original approximation, not convergence of a formal infinite series. The limits have fixed finite m and b>1. Positive-step and punctured-filter versions are separate. No arbitrary value assigned at zero is used. The next monomial survives, with a proved failure of an automatic extra order. The explicit noise term must not be dropped; extrapolation need not contract errors. No later physical discretization receives a remainder hypothesis for free.

## Earlier boundaries to preserve

Actual trajectories are supplied, not constructed. Trace conservation and Hermitian generators do not establish positivity preservation or a completely positive dynamical semigroup. Lindblad self-jumps are excluded as in the source and can affect coherences despite zero population contribution. Combined Hamiltonian-plus-jump currents retain both terms.

Detailed balance is with a fixed positive reference and positive populations; inactive-rate edges have explicit zero contributions. This is classical packet relative entropy, not quantum relative entropy. General graph convergence, zero-probability logarithm limits, q=1 limits and closed coarse rate models without lumpability remain separate. The old affine matrix witnesses are local derivatives at zero, not global positive solutions.

Retain finite-atlas/bounded-operator/finite-matrix scopes from earlier blocks. Countable sums, unbounded domains, trace-class and continuum/empirical claims need separate proofs. Chapter 3 still needs inventory. Preserve the corrected dark-sector candidate and do not revive superseded additive branches.

## Finish the next block

Run the full cumulative verifier, not just the new modules. Update the status, source map and claim ledger, including formerly pending entries that have now been discharged. Count only a completed PASS. Package the cumulative source, manuscript and evidence without duplicating the multi-gigabyte runtime. Freshly extract and reverify the ZIP with hashes before and after, and provide both the release and audit links.

## One-line continuation

Open this ZIP, read CONTINUE_HERE.md and the latest proof guide and report, restore the exact-pin runtime, freshly verify the baseline, then formalize Chapter 5 positive/overlapping operator atlases with actual probability derivatives, moving source terms and exact coarsening, preserving all prior source hashes and every stated proof boundary.
