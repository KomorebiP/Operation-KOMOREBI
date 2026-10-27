# Continue Komorebi Physics Lean v0.8.0

Read AGENTS.md, README.md, STATUS.md, docs/BLOCK_08_PROOF_GUIDE.md, docs/BLOCK_08_DECLARATION_INDEX.md, docs/SOURCE_MAP.md, docs/CLAIM_LEDGER.json, docs/FULL_EDITION_ROADMAP.md, declaration_inventory.json and the completed verification/final/report.json before editing. Inspect whole relevant manuscript pages and original images whenever notation is ambiguous.

## Checkpoint

670 theorem declarations, 808 inventoried names, 40 mathematical modules, 59 invalid controls. Current production audit completed PASS. Restore the exact checksum-matching portable kit; do not silently upgrade dependencies. An actual kit used here was /mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2. A new container may differ. The seven parts and runtime are not duplicated in this source ZIP.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Recompile the baseline before extending. Preserve all 40 mathematical files byte-for-byte under a new block08_preservation.json, retaining prior layers. Use one worker and bounded module runs, warnings as errors, no admissions or custom axioms. Imported Mathlib/Lean caches are reused, not rebuilt wholesale.

## Immediate Block 09 target

Chapter 6: Countable Atlases and Unbounded Generators. Physical pages 30–32, printed 17–19, were read. Original page 30/31 images were rendered locally after Files previews were unavailable; images are retained under verification/source_previews/block08/. Start with 6.1, (6.1)–(6.9), then 6.4, (6.26)–(6.36).

Represent the unbounded Hamiltonian's actual linear domain D(H), domain preservation P_i D(H)⊆D(H), the graph norm, and graph-compatible partial sums. Separate strong resolution from graph convergence. Prove that graph convergence yields both S_F psi→psi and H S_F psi→H psi; then derive the finite-partial-current limit for a supplied differentiable state trajectory. Do not give H the type of an everywhere bounded operator and claim it is unbounded. Do not assume the desired current limit as a field. For the current's sign/conjugation, inspect the original page image: equation (6.34) has conjugation.

The source writes sums over the directed set of finite subsets. Do not infer absolute summability or exchange two infinite sums without a separate theorem. Finite subsystem cancellation can be proved before any infinite double-sum interchange. Self-adjointness/symmetry and domain hypotheses must be explicit. Deriving an actual unitary group e^{-itH}, its invariance and differentiability is separate from a theorem conditional on a supplied trajectory derivative.

Chapter 6.2 gives a spectral weighted-l2 model with lambda_n=n+1/2. It can supply a genuine unbounded test case. Chapter 6.3 distinguishes resolvent/heat zero-tail norm convergence from unitary strong convergence; a zero-padded unitary truncation has operator-norm error 1. Bounded and Cayley transforms need their asymptotic identity tail. Keep these topology statements separate; do not claim them until proved.

## Reusable interfaces

PositiveEffects and MovingEffects: finite positive Hermitian bounded effect atlases, actual Born derivatives and moving sources. Current finite label assumptions cannot simply be erased for countable sums.

ParsevalChannels and ChannelDilation: actual dependent finite Hilbert sums, bounded channel analysis/synthesis, V*V=I, compression and image projector Q=VV*. Q need not be ambient I.

SquareRootDilation: arbitrary finite positive effect atlases already have actual square-root channels and universal finite dilation on complete complex H. Do not list this finite result as still unproved. No countable-outcome version is present.

DilationDynamics: exact compression defect, unsharpness residual norm and actual fixed-channel lifted skew flow/current. No time-dependent-channel derivative or ODE existence.

CycleGauge: finite zero-divergence antisymmetric freedom, converse, subsystem flux and coarse invariance. Does not say every modified current arises from the same original generator.

## Audit and deliver

Update aggregate, inventory, Audit.lean, verifier control and preservation lists, source map, claim ledger, guide, status and continuation together. Audit proof-bearing definitions too. Only propext, Classical.choice and Quot.sound are accepted axiom dependencies. Save failed snapshots outside active modules. A timeout or import error never counts as a proof or control rejection.

Package only after a completed cumulative PASS. Then safely extract into a new directory and run the full verifier again with scripts/recheck_archive.py. Keep the external archive-check report. Never relabel a checksum-only test as a Lean proof recheck. Keep the master PDF and exact pins. Do not bundle the runtime or font files.

## Continuing boundaries

No dynamical existence/uniqueness, initial-state positivity-preserving or completely positive evolution semigroup, zero-population/q=1 entropy extension, general-graph rate theorem, automatic coarse Markov closure, quantum-relative-entropy result, infinite tower/formal-series convergence, countable/unbounded/trace-class completion, full Chapter 3 inventory, gravity/cosmology completion or empirical validation. Preserve corrected scale-covariant dark-sector bookkeeping, not rejected additive branches.

## One-line continuation prompt

Open `Komorebi_Physics_Lean_v0.8.0_Checked_Block_08.zip`, read `CONTINUE_HERE.md` completely, restore and freshly verify the 670-theorem checkpoint with the pinned portable Lean kit, preserve all active sources and proof boundaries, then prove the next Chapter 6 graph-compatible countable-atlas and unbounded-generator continuity block and deliver a cumulative audited ZIP.
