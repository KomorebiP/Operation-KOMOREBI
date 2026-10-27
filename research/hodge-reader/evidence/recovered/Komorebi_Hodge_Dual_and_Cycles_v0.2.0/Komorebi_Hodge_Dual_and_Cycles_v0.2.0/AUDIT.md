# Computation and proof audit

## Contract

The mathematical objective was to extend the degree-70 carrier method toward uniform Hodge-packet coverage. The implemented surrogates are invariant-column optimization certificates and polynomial certificates for explicit complete-intersection cycles. The coefficient domains are integers, rational numbers, and exact polynomial rings with symbolic kappa. The relation kappa^q=-1/5 enters the containment proof; the determinant identities hold symbolically without substituting a numerical root.

Pass means the stated finite checks and certificate inequalities were replayed exactly. It does not mean the Hodge conjecture or the algebraic-geometric proof was formally verified.

## Predecessor preservation and reproduction

The authoritative predecessor is `predecessor/Komorebi_Hodge_Carrier70_v0.1.0.zip`.

SHA256: `72807b5827d21a85bfc1aa8b62ab11a3371de5e6529be751c0943e07bf5e9a77`.

It was extracted into a clean work directory. The original `verify_certificate.py` was read and run with an explicit output path. All 24 original checks passed. Its output is copied to `results/predecessor_replay/verification.json`. This reproduction does not independently prove the external geometric inputs.

## Discovery versus verification

The original broader matrix search and this session's exploratory scan use a bounded enumeration of columns and a floating-point linear program. Those computations discover candidate primal and dual data only. All published capacities here have exact feasible primal solutions and a global dual certificate independent of the discovery bound or floating-point tolerances.

The final authoritative command is:

```sh
python checks/verify_all.py
```

It uses no optimizer, network, random numbers, or floating-point arithmetic. Inputs are `checks/capacity_inputs.json` and the preserved predecessor bytes. It produces `results/verification.json`, `results/capacity_certificates.json`, and `results/cycle_examples.json`. All independent determinant and balance checks are generated from the equations stated in the proof.

## Actual finite range

- Seven individually specified balanced characters at moduli 25,33,35,39,40,55,70; not a complete census of those levels.
- Exact global dual potentials for every residue and every coordinate step of each of those seven inputs.
- Exact intermediate determinant identities for q=2,3,4,5,7,11,17.
- Independent Jacobian-socle pairing for all b at q=2,7,11.
- All b, all units modulo 5q, and all 120 first-five permutations at 2<=q<=64.
- 137 grouped assertions passed in the recorded final run, with 241,920 distinct support monomials and 218,836 balance/conjugacy instances.

There is no universal inference from those sample ranges. Uniformity is proved separately by the congruence argument and wedge-product identity in `PROOF.md`.

## Failures and retractions within this continuation

### F1. Universal positive-anticanonical matrix coverage is false

The proposed extension fails on the infinite family a_(q,b) for q>5 and gcd(b,q)=1. Every allowed matrix has normalized weight sum at most 1. The obstruction survives Galois conjugation, coordinate permutations, and coordinate-power lifts. This is a theorem about the specific matrix constructor, not a numerical search failure and not a counterexample to Hodge.

### F2. Replacing one exponent by a parameter did not establish coverage

An early probe replaced the 7 in the old matrix by a parameter q. The formal normalized weights remain positive and sum to 1+7/(10q). This alone does not exhibit the desired full-support packets on the projective quotient. No uniform new primitive-packet family was established from this observation. It is not counted as a result and should not be promoted to a theorem merely because the positivity calculation works.

### F3. One exploratory input was not a Hodge character

The raw exploratory scan included modulus 45 with tuple (1,10,19,28,36,37). Its entries sum to 131, not 135, so it fails even the initial balance condition. Its reported candidate capacity 34/45 is not a Hodge result. That record is preserved only in `experiments/scan.json` as failed discovery evidence and is excluded from `checks/capacity_inputs.json`. The authoritative verifier checks all unit-conjugate sums for every input before any capacity claim.

The invalid input does not contaminate the seven retained exact certificates. The one-column lower bound C(a)>=1 for balanced a would independently flag the invalid capacity result.

### F4. Positive standard-family algebraicity was already known

The explicit cycles reconstructed here realize Aoki's five-phase standard characters. Finding equations and a determinant certificate is useful for this project, but this is not newly proving an open Hodge family. The original Aoki full text was not successfully retrieved, so the exact historical overlap of the equations is not classified.

### F5. Source access was incomplete

The J-STAGE/Project Euclid routes to the original 1987 paper failed to return readable text, including a security interstitial. The later primary paper establishes the attribution; the positive proof here instead uses our full direct construction and the verified Villaflor complete-intersection theorem. No unread source is claimed to have been audited.

## Representation and geometry boundaries

- Columns of A are invariant exponent vectors; rows of A are target monomials. Transposing these conventions would invalidate the certificate.
- The capacity relaxation allows arbitrary finite support, not necessarily six linearly independent columns. Capacity>1 does not prove existence of a normal well-formed carrier.
- A nonzero complex character component is not alone a rational cycle. The proof uses the rational class of Z, rational group actions, and the multiplicity-one eigenspace decomposition to generate the rational packet.
- The complete-intersection surface is integral but need not be smooth. The source theorem is used with its actual complete-intersection hypotheses, not a fabricated smoothness claim.
- Neither an abstract matching Hodge type nor a guessed cycle class is used to claim nonzero projection: the socle coefficient and exact period provide that check.
- No Lean code was produced or run in this continuation.
- No numerical optimizer timeout is treated as infeasibility. No bounded negative search is treated as a universal obstruction.

## Reproducibility and provenance

The final run's Python, SymPy, platform, timestamps, command, and runtime are in `results/verification.json`. File hashes, preserved predecessor identity, and build metadata are in `MANIFEST.json`. There is no Git commit for this standalone bundle; none is invented. A repeated run changes timestamps and report hashes, but not the exact mathematical inputs or expected values.

The universal arguments remain manuscript-level. An independent review should check the saturated complete-intersection ideal argument, row/sign conventions of the residue normalization, the rational group-module reconstruction, and the exact correspondence assumptions in the preserved predecessor.
