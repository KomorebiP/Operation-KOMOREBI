# Continue from Komorebi Physics Lean v0.13.0 — Block 13

Read `AGENTS.md`, `STATUS.md`, `docs/BLOCK_13_PROOF_GUIDE.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and the completed verification report. Treat only a completed PASS as a checked checkpoint.

## Checkpoint contract

1,173 theorem declarations, 1,397 inventoried names, 71 mathematical modules and 95 invalid controls. Preserve all 71 mathematical files in a new block13 preservation layer before extending. All 65 Block 12 mathematical files remain byte-identical. Counts are not independent discoveries or a full-edition completion percentage.

Runtime used: `/mnt/data/lean_parts/Komorebi_Portable_Lean_4.34.0-rc2`. Runtime bytes remain external. Seven-part checksum restoration support is included. Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 are pinned.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/baseline
```

Use one worker and warnings as errors. Preserve failed snapshots. No admissions, custom axioms, native evaluation or kernel bypass. All proof-bearing definitions and aliases belong in the axiom audit. Imported caches are reused, not rebuilt wholesale.

## Immediate next literal target

Section 6.7, equations (6.53)–(6.56), physical PDF page 34: nonreducing packets and a resolvent certificate.

For a partially defined H and a bounded packet operator P preserving D(H), construct or use a genuine resolvent R_z with range in D(H) and both inverse identities. Suppose [H,P] agrees on D(H) with an actual bounded operator B. Prove

    [R_z,P] = -R_z B R_z
    ||[R_z,P]|| <= ||R_z||^2 ||B||.

Do not manipulate H on a vector without its domain proof. The notation (H-z)^(-1) alone does not prove that a resolvent exists. A general algebraic interface can take the true inverse identities explicitly, with the harmonic resolvent from Block 10 giving an actual realization. The self-adjoint eta^(-2) estimate must retain eta nonzero and its actual resolvent norm bound. P need not reduce H. A nonzero commutator example would be preferable to purely diagonal masks, which commute with H.

Existing `HarmonicSurrogates` supplies domain-valued actual resolvents and two-sided inverse identities. `InfiniteCoarseExamples` provides a bounded first-two-coordinate reflection, non-spectral packets and domain preservation. `GraphDomain` and `DiagonalDomain` retain real domain interfaces. Inspect their exact types before reuse.

## New machinery

`ResidueCharacters`: exact primitive-character selection, explicit exponential phase signs, arbitrary positive modulus and a checked wrong-sign example at M=3.

`ResidueProjectors`: actual bounded phase operators and actual finite character sum; equality to `SpectralCells.mask` for every l2 vector; genuine infinite HasSum, complete orthogonal residue atlas, probability/energy HasSum and maximal real-diagonal domain preservation. Phases use the number spectrum n, not n+1/2.

`LadderDomains`: domain D = {x in l2 | sum n|x_n|^2 finite}, the maximal domain for the sqrt(n) diagonal symbol. Raw lowering/raising sequence maps become Hilbert outputs only after both maximal-domain iff proofs. Dense actual partial maps, vacuum and basis amplitudes.

`LadderAdjoints`: both actual maximal Hilbert-adjoint equalities, closedness, exact action norm sums and ||raise x||^2=||lower x||^2+||x||^2. No product-domain commutator assertion.

`LadderRouting`: input residue projection preserves D; `packet` packages that proof. Actual lowering/raising intertwining Q_(s-1), Q_(s+1), zero wrong corners, retained allowed corners and output resolution. Residue subtraction is in ZMod, not natural numbers.

`LadderExamples`: normalized basis norms, universal unboundedness and absence of bounded extensions; M=3 exact wraparound Q2 a Q0 e9=3e8 and Q0 raise Q2 e8=3e9, wrong lanes zero, vacuum lowering zero and raising e1, wrong amplitude nine rejected, missing character normalization gives three.

## Boundaries and release protocol

Ladder outputs belong to l2, not automatically back to D. Unbounded products and canonical commutators require separate product domains. The full harmonic half-power hierarchy and equivalence with the differential oscillator on L2(R) are not established. The companion coherent-state factorial-lane weights were not formalized here. General Stone/spectral representation, non-diagonal solution existence, compact/Hilbert–Schmidt reconstruction, general nonlinear/dissipative existence and density positivity preservation, countable dilation, entropy endpoints and later gravity/cosmology remain separate. Chapter 3 is still not completely inventoried.

Preserve all prior convergence distinctions. In particular, current rows/iterated sums do not imply joint summability, and strong state convergence does not by itself preserve unbounded domains. Formal model theorems are not empirical validation.

Update `dev_check.py` for Block 14. Extend inventory, aggregate and Audit.lean; add source preservation and controls without weakening existing tests. Update source map, claim ledger, roadmap, proof/failure records and status. Run the full cumulative verifier, package only after stable PASS, then rerun the full audit from a fresh ZIP extraction and deliver its external receipt.

One-line continuation prompt: Open CONTINUE_HERE.md from Komorebi_Physics_Lean_v0.13.0_Checked_Block_13.zip, verify the 1,173-theorem/1,397-name checkpoint, preserve all 71 mathematical modules, and formalize Section 6.7's actual domain-correct resolvent-commutator identity and norm certificate; retain every domain, convergence and empirical boundary.
