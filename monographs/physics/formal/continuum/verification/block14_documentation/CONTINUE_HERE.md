# Continue from Komorebi Physics Lean v0.14.0 — Block 14

Read `AGENTS.md`, `STATUS.md`, `docs/BLOCK_14_PROOF_GUIDE.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and the completed `verification/final/report.json`. Only a completed PASS establishes the cumulative checkpoint. Any status sentence below is subordinate to that actual report.

## Checkpoint contract

Checked inventory: 1,260 theorem declarations, 1,502 inventoried names, 78 mathematical modules and 101 invalid controls. Block 14 adds 87 theorems and eighteen other inventoried declarations. Preserve all 78 mathematical files in a new block14 preservation layer before extending. All 71 previous mathematical sources are byte-identical. Counts include support lemmas and examples, not independent discoveries or a percentage of the 550-page edition.

The exact runtime is external. This block used `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`. Seven-part SHA-256 restoration support is included. Lean is 4.34.0-rc2 and Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine clean dependency pins must be checked.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker and warnings as errors. Retain the explicit `maxErrors=1000` limit on the deliberately invalid batch: with more than 100 controls, the default error cap cannot report every required diagnostic. Preserve failed snapshots. No admissions, custom axioms, unsafe/native evaluation or kernel bypass. Every proof-bearing definition belongs in the axiom audit. Imported caches are reused, not rebuilt wholesale.

## Immediate next literal target

Section 6.8, equations (6.57)–(6.67), physical PDF page 34: infinite reconstruction tower.

For actual orthogonal contractive finite-projector cutoffs S_N approaching I strongly, prove:

    S_N X S_N -> X strongly for bounded X,
    ||S_N X S_N-X|| -> 0 for compact X,
    ||S_N X S_N-X||_HS -> 0 for Hilbert–Schmidt X,
    S_N H S_N psi -> H psi for domain psi with graph-compatible cutoffs.

Keep the topology in every statement. The source's state-error estimate uses ||S_N||<=1. Arbitrary strong convergence of unspecified operators is not enough to invoke that bound. Compact right-compression also requires the relevant adjoint/co-range control; self-adjoint cutoffs supply it. Do not conflate strong convergence of a sequence with strong convergence of its adjoints. Inspect Mathlib's available compact/finite-rank/Hilbert–Schmidt interfaces before committing to a new representation.

Existing `StrongAtlas.partial_norm_le`, `CountableAtlas`, `GraphDomain`, `BoundedSpectral`, `SpectralTruncation` and `SpectralTimeApproximation` supply pieces. Preserve the prior strong-versus-norm counterexamples. Graph reconstruction must show S_N psi is in the generator domain before forming H S_N psi, and use the separately proved action convergence.

## New machinery

`ResolventDomain.Certificate T z`: bounded op, actual range in the partial domain and both shifted inverse identities. `lift` constructs the domain-valued map. Range equals domain, inverse is unique. `BoundedCommutator T P` has actual invariance, bounded extension and equality to [T,P] on D(T); no target identity installed as a field.

`ResolventCommutator`: proves [R_z,P]=-R_z B R_z and its norm/state bounds. Generic P need not be a projector or reduce T. A separate converse proves [R_z,P]=0 iff P preserves D(T) and TP=PT on it. Do not infer a generic norm-small reverse bound or uniqueness of extension from a nondense domain.

`ResolventBounds`: derives Im<x,(T-z)x>=-Im(z)||x||^2, then coercivity and ||R_z||<=1/|Im(z)| from symmetry and actual inverse. The eta^-2 commutator bound explicitly excludes eta=0. It is not an existence proof for abstract nonreal resolvents.

`ResolventParameters`: two genuine inverses obey R_z-R_w=(z-w)R_zR_w, commute, and satisfy quantitative comparison. No analyticity theorem is claimed.

`DiagonalResolvents`: actual bounded inverse symbol (lambda_n-z)^(-1) for arbitrary real eigenvalue sequences and every nonreal complex z. Range/domain proof uses lambda R x=x+zR x in l2; both inverse identities are proved. `harmonicCertificate` wraps the older gapped inverse, including eta=0. `harmonic_agrees` proves agreement where both apply.

`NonreducingPacket`: uses the prior first reflected coordinate, with block [[9,12],[12,16]]/25 and zero tail. Domain invariance holds for every maximal real diagonal operator. The actual [H,P] extension is (12/25)(lambda_0-lambda_1)(E_01-E_10). Its norm is proved using ||E_01-E_10||=1.

`ResolventExamples`: harmonic B=(12/25)(E_10-E_01), ||B||=12/25. Exact leakage for all real eta is (12/25)/(sqrt(1/4+eta^2)sqrt(9/4+eta^2)). At eta=0 norm is 16/25. At eta=1 squared norm is 2304/40625 and [R_1,P]e_1=(-48+384i)e_0/1625. The packet does not reduce H; no finite cutoff approximation is used. Six invalid controls detect missing minus, missing factor, eta=0 inverse-square misuse, false reduction, zero leakage and wrong squared norm.

## Boundaries and release protocol

General commutator identities assume actual inverse and bounded extension data. The constructive existence result discharges inverses for real diagonal operators, not arbitrary self-adjoint operators. Differential-oscillator equivalence, a general spectral theorem or Stone theorem, harmonic half-power hierarchy, unbounded ladder-product domains/canonical commutators, coherent-state factorial-lane weights, compact/Hilbert–Schmidt reconstruction, nonlinear/dissipative solution existence, density positivity preservation, entropy endpoints, countable dilation and later gravity/cosmology remain separate. Chapter 3 is still not fully inventoried. Formal model results are not empirical validation.

For the next block, update `dev_check.py` to a new failure-snapshot directory and extend inventory/aggregate/audit/preservation without changing old mathematical sources or weakening controls. Update source map, claim ledger, roadmap and status. Run full cumulative verification, package only after stable PASS, then rerun the full verifier from a fresh ZIP extraction. Deliver the separate archive receipt.

One-line continuation prompt: Open CONTINUE_HERE.md from Komorebi_Physics_Lean_v0.14.0_Checked_Block_14.zip, verify the 1,260-theorem/1,502-name checkpoint, preserve all 78 mathematical modules, and formalize Section 6.8's topology-specific bounded/compact/Hilbert–Schmidt and graph-domain reconstruction using actual orthogonal contractive cutoffs; retain every domain, convergence and empirical boundary.
