# Continue from Komorebi Physics Lean v0.15.0 — Block 15

Read `AGENTS.md`, `STATUS.md`, `docs/BLOCK_15_PROOF_GUIDE.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and the completed `verification/final/report.json`. Only a completed PASS establishes the cumulative checkpoint. A status sentence or source inventory is not a substitute for that report.

## Checkpoint contract

Inventory: **1,371 theorem declarations, 1,626 inventoried names, 86 mathematical modules and 108 invalid controls**. Block 15 adds 111 theorems and 13 definitions. Preserve all 86 mathematical files in a new Block 15 preservation layer before extending. All 78 Block 14 mathematical sources are byte-identical. Counts include support lemmas and examples, not independent discoveries or a percentage of the 550-page edition.

The exact runtime is external. This block used `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`. Seven-part checksum restoration support is included. Lean is 4.34.0-rc2; Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine clean dependency revisions must be checked.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker and warnings as errors. Keep `maxErrors=1000` in the deliberately invalid batch, and require each control's designated diagnostic in its mapped source range. A nonzero process exit, timeout or import failure is not a successful negative test. No admissions, custom axioms, native/unsafe evaluation or kernel bypass. Every proof-bearing definition belongs in the transitive axiom audit. Imported compiled dependencies are reused, not rebuilt wholesale.

## Immediate next literal source

Chapter 7, (7.1)–(7.23), physical PDF pages 36–37: finite pointwise differential no-go, then noncommutative corner-algebra resolution.

For a finite label type and the complex algebra of functions with pointwise multiplication, prove that an actual complex-linear map satisfying exact Leibniz is zero. Derive the idempotent-coordinate argument; do not put D=0 in the interface. Do not generalize the no-go without proof to arbitrary finite-dimensional commutative algebras, which can have nilpotents and nonzero derivations. The finite product of complex fields and the specified scalar linearity matter.

Then construct the actual finite-matrix derivation delta_K(X)=i(KX-XK). Prove ordinary Leibniz, star compatibility under Hermitian K, and the trace integration-by-parts identity. Preserve the sign and multiplication order. Subsequent source targets are curvature (7.24)–(7.30) and projector-corner path/refinement identities (7.31)–(7.37). Inspect existing QuantumPacketCore, MixedTransfer and Deformation algebra first instead of counting recovered results as newly authored.

Advancing to Chapter 7 does not declare Chapter 6 fully complete. The harmonic half-power hierarchy (6.12), differential-oscillator identification, broader interacting-domain and continuous-spectral questions, ladder-product domains and companion coherent-state weights remain explicit obligations. Section 6.9 numerical residuals are historical and were not rerun.

## Newly available machinery

`StrongReconstruction.compression` is actual S*X*S. The exact error identity, state estimate, comparison estimate with 2||X-Y||, varying-vector lemma and strong reconstruction are proved from explicit contraction and strong convergence. No operator-norm convergence is inferred for arbitrary bounded X.

`CompactReconstruction` derives uniform convergence on compact sets with an epsilon-net. Actual compact X gives left norm convergence. For self-adjoint contractions, the Gram inequality ||X(S-I)||^2 <= 2||(S-I)(X*X)|| supplies the right limit without assuming strong convergence of arbitrary adjoints. Full compact reconstruction follows. Self-adjoint contractions are a sufficient contract, not characterized as necessary.

`HilbertSchmidtCore.IsHS b X` is actual square summability of ||X b_i||^2. `columns` constructs a genuine lp-2 vector. Membership and norm are basis independent; adjoint invariance, ideal multiplication bounds, triangle bounds and opNorm<=hsNorm are proved. The total scalar definitions `energy` and `hsNorm` are not a norm on nonmembers. Do not drop IsHS from definiteness/norm statements; the infinite identity is proved not HS. No complete bundled Schatten hierarchy is claimed.

`HilbertSchmidtReconstruction` proves left error convergence by dominated convergence with summable bound 4||X b_i||^2, right convergence by adjoint invariance, and the full sandwich limit plus its operator-norm consequence. Error membership is proved. No unsupported sum interchange.

`AtlasReconstruction.cutoff` constructs the actual finite operator sum. Its norm<=1, idempotence, self-adjointness and strong limit are proved. The bounded/compact/HS limits are instantiated. A finite set of sectors need not have a finite-dimensional range.

`GraphReconstruction.reconstructed` applies T only to the actual domain-valued partial sum. Its error is bounded by the generator-action error plus the ordinary cutoff tail of T x. `GraphCompatible` supplies the former; strong completeness supplies the latter. This is ambient norm convergence, not graph-norm convergence of generator images. The diagonal model's existing graph theorem supplies an actual realization.

`HilbertSchmidtExamples` uses X with multiplier 2^(-n), a genuine HS input of squared norm 4/3. For E_M=X-S_MXS_M, exact HasSum and norm theorems give ||E_M||_HS^2=(4/3)4^(-M), ||E_M||=2^(-M), and E_M!=0 at every finite M. At M=2 they are 1/12 and 1/4 respectively.

`ReconstructionExamples` constructs compact rank-one P=|e0><e0| and S_n=I+|e0><e_(n+1)|. The latter have norm<=2 and converge strongly on every l2 vector, but ||S_n P S_n-P||=1. Their adjoints do not converge strongly and each S_n is non-self-adjoint. Do not call these contractions or orthogonal cutoffs. Separately, genuine orthogonal spectral cutoffs have strong convergence but identity operator-norm error one.

## Boundaries and release protocol

Only the stated cutoff, summability and graph hypotheses are discharged. No operator-norm convergence of every bounded operator, generic strong-to-adjoint inference, automatic graph compatibility, HS result for non-HS inputs or general Schatten-p theory is proved. Earlier general spectral/Stone, differential-oscillator, nonlinear/dissipative existence, density positivity, entropy boundary, countable dilation, continuum gravity and cosmology obligations remain. Chapter 3 is not fully inventoried. Formal model proofs do not establish empirical adequacy.

For the next block, preserve the mathematical sources; update the dev snapshot directory and extend inventory, aggregate, all-name axiom audit, preservation and controls. Update the ledger, source map, guide, roadmap and failures together. Recompile the entire active library, package only after stable PASS, then run the full verifier from a fresh ZIP extraction and deliver its separate receipt.

One-line continuation prompt: Open CONTINUE_HERE.md from Komorebi_Physics_Lean_v0.15.0_Checked_Block_15.zip, verify the 1,371-theorem/1,626-name checkpoint, preserve all 86 mathematical modules, and formalize Chapter 7's finite pointwise derivation no-go and actual matrix corner derivations with Leibniz, star and trace identities; retain every domain, topology and empirical boundary.
