# Continue Komorebi Physics Lean v0.5.0

Read AGENTS.md, README.md, STATUS.md, docs/BLOCK_05_PROOF_GUIDE.md, docs/SOURCE_MAP.md, docs/CLAIM_LEDGER.json, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and verification/final/report.json before editing. Read complete relevant source pages and their images when notation is ambiguous.

## Restore and verify

The expected checked inventory is 402 theorem declarations, 490 named declarations, 25 mathematical modules and 34 deliberately invalid controls. Trust the actual machine report, not those numbers alone. Use the included `runtime_restore_support/assemble.py` with all seven checksum-matching portable runtime parts, or an already restored exact-pin kit. A successful prior production path was `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`; that path is not guaranteed in a fresh container.

Lean is 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Do not silently upgrade them or substitute unchecked axioms. Runtime restoration is local assembly/extraction, not remote dependency fetching.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker and bounded per-module runs. Imported dependency caches are reused, not independently rebuilt wholesale. Recompile all local proof modules before reporting a checked result. Timeouts, import failures and missing files are not proofs. Keep failed sources/logs separate from the active mathematical source tree.

## Preserve the checkpoint

All 25 current mathematical files are the upstream baseline for a next block. Copy the package into the new version; preserve a SHA-256 map for those files and a snapshot of current docs/inventory. Prior files should remain byte-identical unless an explicit repair is necessary and documented. Preserve all earlier provenance and successful/failed receipts.

Declarations are inventoried and axiom-audited, including proof-bearing definitions. No sorry/admit, custom axiom, unsafe/native proof escape or disabled kernel checking. Allowed reported dependencies are propext, Classical.choice and Quot.sound. Update the aggregate, inventory, audit commands, verifier and negative-control inventory together. Do not count tests, numerical output or definitions as new theorem declarations.

## Immediate source target: Chapter 4.9

Physical PDF page 26, printed page 13, equations (4.59)–(4.67): the general refinement-cancellation tower.

F(h)=F+sum_(r>=1) c_r h^r,
R_j^(0)=F(h/2^j),
R_j^(m)=(2^m R_(j+1)^(m-1)-R_j^(m-1))/(2^m-1).

The stated target is R_0^(m)=F+O(h^(m+1)), with explicit first three formulas. Separate two layers:

1. Exact finite polynomial/monomial coefficient cancellation, denominators nonzero, and recursive closed-form coefficients. Prove these algebraically; do not make an asymptotic hypothesis contain the desired cancellation.
2. Analytic asymptotic remainder control. State actual regularity/asymptotic assumptions, finite truncation order, domain and limiting filter. Prove scaling/linear-combination Big-O propagation, rather than treating a formal infinite series as a convergence theorem.

Exact low-degree counterexamples should reject wrong powers, wrong signs and an off-by-one order. Evaluate source images and subsequent pages before choosing whether to move to Chapter 5; do not skip remaining Chapter 4 material simply because 4.7 is done.

## Boundaries to retain

Lindblad populations derive from the original matrix HasDerivAt. The generator sums distinct jumps; self-jumps can alter coherences even with zero population contribution. Coherent inputs are allowed. Rate nonnegativity, square-root normalization and source/target orientation are explicit. Trace zero and Hermitian rates do not prove existence or positivity preservation from initial data.

Detailed balance concerns a fixed positive reference and classical packet relative entropy. Populations are strictly positive for logarithm differentiation. Zero rates use an explicit inactive-edge convention; active flux arguments are proved positive. The sign result is not automatically a theorem about the combined Hamiltonian-plus-jump generator. Zero dissipation implies equal ratios on active edges; current equilibrium uniqueness assumes all distinct rates positive, not general irreducibility. No convergence rate or initial-value solution is constructed.

The two affine matrix examples satisfy the original flow at zero only. PSD input and trace one are proved at that base state, not globally along the affine curve. Coarse flux is exact, but no closed coarse rate matrix is assumed without lumpability. The information entropy is not von Neumann entropy.

The prior full-edition scopes still apply: finite atlases, bounded operator derivatives or finite matrices as appropriate; no countable/unbounded/continuum claim without separate proof. No empirical theory validation. Chapter 3 remains partly uninventoried. Preserve the source's corrected dark-sector branch and do not revive its superseded additive branches.

## Finish a block

Run the cumulative verifier. Report exact counts only from a completed PASS report. Update all status, source-map and claim-ledger entries, including formerly pending entries that the new proofs discharge. Retain remaining gaps explicitly. Package source/manuscript/evidence but not the multi-gigabyte runtime, then extract into a different directory and rerun the full verifier. Verify hashes before and after. Include the full cumulative ZIP and its audit links.

## One-line continuation

Open this ZIP, read CONTINUE_HERE.md and the latest proof guide and report, restore the exact-pin runtime, freshly verify the baseline, then formalize Chapter 4.9 refinement-cancellation towers with exact coefficient cancellation separated from analytic remainder bounds, preserving every stated proof boundary and all prior source hashes.
