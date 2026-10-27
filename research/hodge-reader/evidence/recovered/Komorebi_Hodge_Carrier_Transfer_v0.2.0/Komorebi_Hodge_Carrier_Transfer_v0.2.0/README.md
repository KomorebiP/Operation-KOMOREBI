# Komorebi Hodge Carrier and Transfer v0.2.0

## Result

This block transfers the inherited degree-70 carrier result to the full-conductor degree-210 character `(2,9,129,142,168,180)`. Its rational Hodge packet has dimension 48. A 14-term exact identity and classical Fermat cycle operations prove algebraicity relative to the predecessor proposition.

It also proves global obstructions to the previous direct matrix criterion, including one for this very target and an infinite family, and a holomorphic-power obstruction for six further direct diagonal quotient targets.

**Status:** manuscript-level proof with exact finite verification; no Lean verification, no independent peer review, no general Hodge-conjecture proof, no historical novelty claim.

## Read first

- `PROOF.md`: complete mathematical argument, dependencies and boundaries.
- `AUDIT.md`: computation and discovery provenance, failures, nonclaims.
- `CONTINUE_HERE.md`: the precise next proof boundary.
- `MANIFEST.json`: hashes and execution metadata.

## Reproduce the new exact certificate

From this directory:

```sh
python checks/verify.py
```

Python 3.10 or later. Standard library only. No internet or optimizer. The output is `results/verification.json`. The recorded run passes 46 checks. To preserve that record while replaying, use:

```sh
python checks/verify.py --out results/replay.json
```

The last optional replay file is not part of the frozen manifest.

## Predecessor

`predecessor/Komorebi_Hodge_Carrier70_v0.1.0.zip` is an unchanged copy of the authoritative previous archive. Its verifier was extracted to a separate working directory and rerun successfully: 24 checks. `results/predecessor_verification.json` preserves that replay. See the archived README for its dependencies, including SymPy.

The new 46-check verifier does not silently treat these arithmetic tests as a formal proof of the predecessor's geometry.

## Discovery versus final verification

`discovery/search_transfer.py` is an optional bounded rediscovery tool. It requires NumPy and SciPy. Its floating-point solver output is only a proposed certificate and is checked exactly before acceptance. It writes `discovery/rediscovered_transfer.json` by default, never overwriting the frozen certificate.

The degree-18 exploratory scan JSON files are historical bounded observations, not proofs of global matrix nonexistence. The proofs are the exact dual certificates and uniform arguments in `PROOF.md`.

No external mathematical source or classical theorem is authenticated by an exit code. Original Aoki PDF access failed; the exact statements were checked in the accessible research-paper reproduction identified in the proof note.
